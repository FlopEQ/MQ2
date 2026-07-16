#!/usr/bin/env python3
"""Derive CXWnd member moves by comparing matching Live-client methods."""

from __future__ import annotations

import argparse
import collections
import difflib
import pathlib
import re

import pefile
from capstone import Cs, CS_ARCH_X86, CS_MODE_64
from capstone.x86 import X86_OP_IMM, X86_OP_MEM, X86_OP_REG


PAIR_RE = re.compile(
    r"\| `(?P<name>[^`]+)` \| `0x(?P<old>[0-9A-Fa-f]+)` \| `0x(?P<new>[0-9A-Fa-f]+)`"
)


class Image:
    def __init__(self, path: pathlib.Path):
        self.pe = pefile.PE(str(path))
        self.base = self.pe.OPTIONAL_HEADER.ImageBase
        self.image = self.pe.get_memory_mapped_image()
        self.ranges: dict[int, int] = {}
        for entry in getattr(self.pe, "DIRECTORY_ENTRY_EXCEPTION", []):
            begin = self.base + entry.struct.BeginAddress
            self.ranges[begin] = self.base + entry.struct.EndAddress

    def is_executable(self, va: int) -> bool:
        rva = va - self.base
        for section in self.pe.sections:
            if section.VirtualAddress <= rva < section.VirtualAddress + section.Misc_VirtualSize:
                return bool(section.Characteristics & 0x20000000)
        return False

    def qword(self, va: int) -> int:
        rva = va - self.base
        return int.from_bytes(self.image[rva : rva + 8], "little")

    def function_bytes(self, va: int) -> bytes:
        end = self.ranges.get(va)
        if end is None:
            candidates = [begin for begin in self.ranges if begin <= va < self.ranges[begin]]
            if candidates:
                end = self.ranges[max(candidates)]
            else:
                end = va + 0x100
        end = min(end, va + 0x1000)
        rva = va - self.base
        return self.image[rva : rva + (end - va)]


def normalize(ins) -> tuple:
    operands = []
    for op in ins.operands:
        if op.type == X86_OP_REG:
            operands.append(("reg", ins.reg_name(op.reg)))
        elif op.type == X86_OP_MEM:
            operands.append(
                (
                    "mem",
                    ins.reg_name(op.mem.base),
                    ins.reg_name(op.mem.index),
                    op.mem.scale,
                    op.size,
                )
            )
        elif op.type == X86_OP_IMM:
            # Small constants help align field initialization. Addresses do not.
            value = op.imm if -0x1000 <= op.imm < 0x30 else "address"
            operands.append(("imm", value, op.size))
        else:
            operands.append(("other", op.type, op.size))
    return (ins.mnemonic, tuple(operands))


def this_aliases(instructions) -> set[str]:
    aliases = {"rcx"}
    for ins in instructions[:24]:
        if ins.mnemonic in ("mov", "lea") and len(ins.operands) == 2:
            dst, src = ins.operands
            if dst.type != X86_OP_REG:
                continue
            dst_name = ins.reg_name(dst.reg)
            if src.type == X86_OP_REG and ins.reg_name(src.reg) in aliases:
                aliases.add(dst_name)
            elif (
                src.type == X86_OP_MEM
                and ins.reg_name(src.mem.base) in aliases
                and not src.mem.index
                and src.mem.disp == 0
            ):
                aliases.add(dst_name)
    return aliases


def member_refs(ins, aliases: set[str]) -> list[int]:
    refs = []
    for op in ins.operands:
        if op.type != X86_OP_MEM:
            continue
        if ins.reg_name(op.mem.base) not in aliases or op.mem.index:
            continue
        if 0x30 <= op.mem.disp < 0x268:
            refs.append(op.mem.disp)
    if ins.mnemonic == "add" and len(ins.operands) == 2:
        dst, value = ins.operands
        if (
            dst.type == X86_OP_REG
            and ins.reg_name(dst.reg) in aliases
            and value.type == X86_OP_IMM
            and 0x30 <= value.imm < 0x268
        ):
            refs.append(value.imm)
    return refs


def compare_pair(md: Cs, old: Image, new: Image, old_va: int, new_va: int):
    old_ins = list(md.disasm(old.function_bytes(old_va), old_va))
    new_ins = list(md.disasm(new.function_bytes(new_va), new_va))
    old_aliases = this_aliases(old_ins)
    new_aliases = this_aliases(new_ins)
    matcher = difflib.SequenceMatcher(
        a=[normalize(ins) for ins in old_ins],
        b=[normalize(ins) for ins in new_ins],
        autojunk=False,
    )
    for block in matcher.get_matching_blocks():
        for index in range(block.size):
            left = old_ins[block.a + index]
            right = new_ins[block.b + index]
            old_refs = member_refs(left, old_aliases)
            new_refs = member_refs(right, new_aliases)
            if len(old_refs) == len(new_refs) == 1:
                yield old_refs[0], new_refs[0]


def report_pairs(path: pathlib.Path, all_functions: bool = False):
    for line in path.read_text(encoding="utf-8").splitlines():
        match = PAIR_RE.match(line)
        if not match:
            continue
        name = match.group("name")
        if (not all_functions and not name.startswith("CXWnd__")) or name.endswith("vftable_x"):
            continue
        yield name, int(match.group("old"), 16), int(match.group("new"), 16)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old", type=pathlib.Path)
    parser.add_argument("new", type=pathlib.Path)
    parser.add_argument("report", type=pathlib.Path)
    parser.add_argument("--old-vtable", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--new-vtable", type=lambda value: int(value, 0), required=True)
    parser.add_argument("--vtable-size", type=lambda value: int(value, 0), default=0x348)
    parser.add_argument("--all-functions", action="store_true")
    args = parser.parse_args()

    old = Image(args.old)
    new = Image(args.new)
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True

    pairs = list(report_pairs(args.report, args.all_functions))
    for slot in range(0, args.vtable_size, 8):
        old_va = old.qword(args.old_vtable + slot)
        new_va = new.qword(args.new_vtable + slot)
        pairs.append((f"vtable+0x{slot:03x}", old_va, new_va))

    votes: dict[int, collections.Counter[int]] = collections.defaultdict(collections.Counter)
    sources: dict[tuple[int, int], set[str]] = collections.defaultdict(set)
    seen_pairs = set()
    for name, old_va, new_va in pairs:
        if not old.is_executable(old_va) or not new.is_executable(new_va):
            continue
        key = (old_va, new_va)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        try:
            mappings = compare_pair(md, old, new, old_va, new_va)
            for old_offset, new_offset in mappings:
                votes[old_offset][new_offset] += 1
                sources[(old_offset, new_offset)].add(name)
        except Exception as exc:
            print(f"warning: {name}: {exc}")

    print("old,new,votes,alternatives,sources")
    for old_offset in sorted(votes):
        ranked = votes[old_offset].most_common()
        new_offset, count = ranked[0]
        alternatives = ";".join(f"0x{value:x}:{score}" for value, score in ranked[1:4])
        evidence = ";".join(sorted(sources[(old_offset, new_offset)]))
        print(f"0x{old_offset:x},0x{new_offset:x},{count},{alternatives},{evidence}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
