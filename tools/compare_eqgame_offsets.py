#!/usr/bin/env python3
"""Compare two eqgame.exe builds and update MacroQuest eqgame offsets.

The scanner anchors on the current eqgame.h values in the old executable, then
relocates them in the new executable with a few strategies:

* changed version strings are found directly
* code addresses are matched with normalized instruction bytes
* data/rdata addresses are matched with exact byte windows
* remaining addresses fall back to the matching PE section's VA delta

The output is intentionally conservative: every rewritten define is listed with
the method that found it, so low-confidence section-delta results can be checked.
"""

from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
from collections import Counter
from dataclasses import dataclass

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64


DATE_RE = re.compile(rb"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) [ 0-3][0-9] 20[0-9][0-9]\x00")
TIME_RE = re.compile(rb"[0-2][0-9]:[0-5][0-9]:[0-5][0-9]\x00")
DEFINE_RE = re.compile(r"^(#define\s+)([A-Za-z0-9_]+_x)(\s+)0x([0-9A-Fa-f]+)(.*)$")


@dataclass(frozen=True)
class Section:
    name: str
    va: int
    virtual_size: int
    raw_size: int
    raw_offset: int


@dataclass
class Result:
    name: str
    old_va: int
    new_va: int | None
    section: str | None
    method: str

    @property
    def confidence(self) -> str:
        if self.method.startswith(("version_string", "code", "exact")):
            return "high"
        if self.method == "section_delta":
            return "review"
        return "unresolved"


class EqGameImage:
    def __init__(self, path: pathlib.Path):
        self.path = path
        self.data = path.read_bytes()
        self.pe = pefile.PE(str(path))
        self.base = self.pe.OPTIONAL_HEADER.ImageBase
        self.sections = [
            Section(
                section.Name.rstrip(b"\0").decode(errors="replace"),
                self.base + section.VirtualAddress,
                section.Misc_VirtualSize,
                section.SizeOfRawData,
                section.PointerToRawData,
            )
            for section in self.pe.sections
        ]

    def section_for_va(self, va: int) -> Section | None:
        for section in self.sections:
            if section.va <= va < section.va + section.virtual_size:
                return section
        return None

    def section_by_name(self, name: str) -> Section | None:
        for section in self.sections:
            if section.name == name:
                return section
        return None

    def file_offset_for_va(self, va: int) -> int | None:
        section = self.section_for_va(va)
        if section is None:
            return None

        rel = va - section.va
        if rel >= section.raw_size:
            return None

        return section.raw_offset + rel

    def va_for_file_offset(self, offset: int) -> int:
        rva = self.pe.get_rva_from_offset(offset)
        return self.base + rva

    def section_blob(self, name: str) -> tuple[Section, bytes]:
        section = self.section_by_name(name)
        if section is None:
            raise ValueError(f"{self.path} does not contain section {name}")
        return section, self.data[section.raw_offset : section.raw_offset + section.raw_size]

    def version_date(self) -> str:
        matches = [m.group(0)[:-1].decode("ascii") for m in DATE_RE.finditer(self.data)]
        if not matches:
            raise ValueError(f"Could not find client date in {self.path}")
        return sorted(set(matches))[0]

    def version_times(self) -> list[str]:
        return sorted(set(m.group(0)[:-1].decode("ascii") for m in TIME_RE.finditer(self.data)))


def parse_defines(header_text: str) -> list[tuple[str, int]]:
    values: list[tuple[str, int]] = []
    for line in header_text.splitlines():
        match = DEFINE_RE.match(line)
        if match:
            values.append((match.group(2), int(match.group(4), 16)))
    return values


def client_date_literal(version_date: str) -> str:
    parsed = dt.datetime.strptime(version_date.replace("  ", " 0"), "%b %d %Y")
    return f"{parsed:%Y%m%d}u"


def find_version_string(old: EqGameImage, new: EqGameImage, old_value: bytes, new_value: bytes) -> tuple[int, int] | None:
    old_offset = old.data.find(old_value + b"\0")
    new_offset = new.data.find(new_value + b"\0")
    if old_offset < 0 or new_offset < 0:
        return None
    return old.va_for_file_offset(old_offset), new.va_for_file_offset(new_offset)


def build_code_regex(old: EqGameImage, md: Cs, va: int, min_len: int = 56, max_ins: int = 18) -> tuple[re.Pattern[bytes], int] | None:
    offset = old.file_offset_for_va(va)
    if offset is None:
        return None

    buffer = bytearray(old.data[offset : offset + 180])
    mask = bytearray(b"x" * len(buffer))
    total = 0
    count = 0

    for ins in md.disasm(bytes(buffer), va):
        rel = ins.address - va
        if ins.disp_size:
            start = rel + ins.disp_offset
            mask[start : start + ins.disp_size] = b"?" * ins.disp_size
        if ins.imm_size:
            start = rel + ins.imm_offset
            mask[start : start + ins.imm_size] = b"?" * ins.imm_size

        total = rel + ins.size
        count += 1
        if total >= min_len or count >= max_ins:
            break

    if total < 8:
        return None

    parts = [
        b"." if mask_byte == ord("?") else re.escape(bytes([byte]))
        for byte, mask_byte in zip(buffer[:total], mask[:total])
    ]
    return re.compile(b"".join(parts), re.DOTALL), total


def relocate_code(old: EqGameImage, new: EqGameImage, md: Cs, old_va: int) -> tuple[int, str] | None:
    regex = build_code_regex(old, md, old_va)
    if regex is None:
        return None

    pattern, length = regex
    new_text_section, new_text = new.section_blob(".text")
    hits = []
    for match in pattern.finditer(new_text):
        hits.append(match.start())
        if len(hits) > 1:
            break

    if len(hits) != 1:
        return None

    return new_text_section.va + hits[0], f"code{length}"


def relocate_exact(old: EqGameImage, new: EqGameImage, old_va: int) -> tuple[int, str] | None:
    old_section = old.section_for_va(old_va)
    if old_section is None:
        return None

    new_section = new.section_by_name(old_section.name)
    if new_section is None:
        return None

    rel = old_va - old_section.va
    if rel >= old_section.raw_size:
        return None

    old_blob = old.data[old_section.raw_offset : old_section.raw_offset + old_section.raw_size]
    new_blob = new.data[new_section.raw_offset : new_section.raw_offset + new_section.raw_size]

    for length in (96, 64, 48, 32, 24, 16):
        start_rel = max(0, rel - 16)
        if start_rel + length > old_section.raw_size:
            continue

        needle = old_blob[start_rel : start_rel + length]
        hits = []
        position = new_blob.find(needle)
        while position != -1 and len(hits) < 2:
            hits.append(position)
            position = new_blob.find(needle, position + 1)

        if len(hits) == 1:
            return new_section.va + hits[0] + (rel - start_rel), f"exact{length}"

    return None


def compare_offsets(old: EqGameImage, new: EqGameImage, defines: list[tuple[str, int]]) -> list[Result]:
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    version_pairs: dict[int, int] = {}
    try:
        date_pair = find_version_string(old, new, old.version_date().encode("ascii"), new.version_date().encode("ascii"))
        if date_pair:
            version_pairs[date_pair[0]] = date_pair[1]
    except ValueError:
        pass

    old_times = old.version_times()
    new_times = new.version_times()
    if old_times and new_times:
        time_pair = find_version_string(old, new, old_times[0].encode("ascii"), new_times[0].encode("ascii"))
        if time_pair:
            version_pairs[time_pair[0]] = time_pair[1]

    results: list[Result] = []
    for name, old_va in defines:
        old_section = old.section_for_va(old_va)
        new_va: int | None = None
        method = "unresolved"

        if old_va in version_pairs:
            new_va = version_pairs[old_va]
            method = "version_string"
        elif old_section and old_section.name == ".text":
            found = relocate_code(old, new, md, old_va)
            if found:
                new_va, method = found

        if new_va is None:
            found = relocate_exact(old, new, old_va)
            if found:
                new_va, method = found

        if new_va is None and old_section is not None:
            new_section = new.section_by_name(old_section.name)
            if new_section is not None:
                new_va = old_va + (new_section.va - old_section.va)
                method = "section_delta"

        results.append(Result(name, old_va, new_va, old_section.name if old_section else None, method))

    return results


def rewrite_header(header_text: str, results: list[Result], new_date: str, new_time: str) -> str:
    by_name = {result.name: result for result in results if result.new_va is not None}
    lines = []
    for line in header_text.splitlines():
        if line.startswith("#define __ClientDate"):
            line = re.sub(r"\d{8}u", client_date_literal(new_date), line)
        elif line.startswith("#define __ExpectedVersionDate"):
            line = re.sub(r'"[^"]+"', f'"{new_date}"', line)
        elif line.startswith("#define __ExpectedVersionTime"):
            line = re.sub(r'"[^"]+"', f'"{new_time}"', line)
        else:
            match = DEFINE_RE.match(line)
            if match and match.group(2) in by_name:
                result = by_name[match.group(2)]
                line = f"{match.group(1)}{match.group(2)}{match.group(3)}0x{result.new_va:08X}{match.group(5)}"
        lines.append(line)

    return "\n".join(lines) + "\n"


def image_version_label(image: EqGameImage) -> str:
    parts = []
    try:
        parts.append(image.version_date())
    except ValueError:
        pass

    times = image.version_times()
    if times:
        parts.append(times[0])

    return " ".join(parts) if parts else "not embedded"


def write_report(report_path: pathlib.Path, old: EqGameImage, new: EqGameImage, results: list[Result]) -> None:
    counts = Counter(result.confidence for result in results)
    methods = Counter(result.method for result in results)
    changed = sum(1 for result in results if result.new_va is not None and result.new_va != result.old_va)
    old_version = image_version_label(old)
    new_version = image_version_label(new)

    lines = [
        "# Offset Comparison",
        "",
        f"Old: `{old.path}`",
        f"New: `{new.path}`",
        "",
        f"Old version: `{old_version}`",
        f"New version: `{new_version}`",
        "",
        f"Defines compared: `{len(results)}`",
        f"Changed addresses: `{changed}`",
        f"High-confidence relocations: `{counts['high']}`",
        f"Review-needed section-delta relocations: `{counts['review']}`",
        f"Unresolved relocations: `{counts['unresolved']}`",
        "",
        "## Method Counts",
        "",
    ]

    for method, count in methods.most_common():
        lines.append(f"- `{method}`: {count}")

    review = [result for result in results if result.confidence != "high"]
    lines.extend(["", "## Review Needed", ""])
    if review:
        lines.append("| Name | Old | New | Section | Method |")
        lines.append("| --- | ---: | ---: | --- | --- |")
        for result in review:
            new_va = f"0x{result.new_va:08X}" if result.new_va is not None else "unresolved"
            lines.append(f"| `{result.name}` | `0x{result.old_va:08X}` | `{new_va}` | `{result.section}` | `{result.method}` |")
    else:
        lines.append("No review-needed entries.")

    lines.extend(["", "## All Results", ""])
    lines.append("| Name | Old | New | Confidence | Method |")
    lines.append("| --- | ---: | ---: | --- | --- |")
    for result in results:
        new_va = f"0x{result.new_va:08X}" if result.new_va is not None else "unresolved"
        lines.append(f"| `{result.name}` | `0x{result.old_va:08X}` | `{new_va}` | `{result.confidence}` | `{result.method}` |")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", required=True, type=pathlib.Path)
    parser.add_argument("--new", required=True, type=pathlib.Path)
    parser.add_argument("--header", required=True, type=pathlib.Path)
    parser.add_argument("--report", type=pathlib.Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()

    old = EqGameImage(args.old)
    new = EqGameImage(args.new)
    header_text = args.header.read_text(encoding="utf-8")
    defines = parse_defines(header_text)
    results = compare_offsets(old, new, defines)

    if args.report:
        write_report(args.report, old, new, results)

    if args.write:
        new_time = new.version_times()[0]
        args.header.write_text(rewrite_header(header_text, results, new.version_date(), new_time), encoding="utf-8")

    counts = Counter(result.confidence for result in results)
    print(f"Compared {len(results)} offsets")
    print(f"High confidence: {counts['high']}")
    print(f"Review needed: {counts['review']}")
    print(f"Unresolved: {counts['unresolved']}")
    if args.report:
        print(f"Wrote report: {args.report}")
    if args.write:
        print(f"Updated header: {args.header}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
