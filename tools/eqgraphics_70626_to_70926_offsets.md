# eqgame Offset Comparison

Old: `E:\EQ Legends\EQGraphics.dll`
New: `E:\SteamLibrary\steamapps\common\Everquest F2P\EQGraphics.dll`

Old version: `Jul  6 2026 10:47:41`
New version: `Jul  9 2026 11:15:49`

Defines compared: `13`
Changed addresses: `3`
High-confidence relocations: `2`
Review-needed section-delta relocations: `11`
Unresolved relocations: `0`

## Method Counts

- `section_delta`: 11
- `code59`: 1
- `exact96`: 1

## Review Needed

| Name | Old | New | Section | Method |
| --- | ---: | ---: | --- | --- |
| `CEQGBitmap__GetFirstBitmap_x` | `0x180003250` | `0x180003250` | `.text` | `section_delta` |
| `CParticleSystem__Render_x` | `0x1800B2E10` | `0x1800B2E10` | `.text` | `section_delta` |
| `CParticleSystem__CreateSpellEmitter_x` | `0x1800A2A20` | `0x1800A2A20` | `.text` | `section_delta` |
| `CRender__RenderScene_x` | `0x1800DAE50` | `0x1800DAE50` | `.text` | `section_delta` |
| `CRender__RenderBlind_x` | `0x1800DAD10` | `0x1800DAD10` | `.text` | `section_delta` |
| `CRender__ResetDevice_x` | `0x1800DB9C0` | `0x1800DB9C0` | `.text` | `section_delta` |
| `CRender__UpdateDisplay_x` | `0x1800DCBC0` | `0x1800DCBC0` | `.text` | `section_delta` |
| `C2DPrimitiveManager__AddCachedText_x` | `0x1800F5820` | `0x1800F5820` | `.text` | `section_delta` |
| `C2DPrimitiveManager__Render_x` | `0x1800F69C0` | `0x1800F69C0` | `.text` | `section_delta` |
| `ObjectPreviewView__Render_x` | `0x1800277E0` | `0x1800277E0` | `.text` | `section_delta` |
| `EQGraphics_DebugAPI_Ptr_x` | `0x1803D6FA8` | `0x180338FA8` | `.rdata` | `section_delta` |

## All Results

| Name | Old | New | Confidence | Method |
| --- | ---: | ---: | --- | --- |
| `__eqgraphics_fopen_x` | `0x180281408` | `0x1801E9BE8` | `high` | `code59` |
| `CEQGBitmap__GetFirstBitmap_x` | `0x180003250` | `0x180003250` | `review` | `section_delta` |
| `CParticleSystem__Render_x` | `0x1800B2E10` | `0x1800B2E10` | `review` | `section_delta` |
| `CParticleSystem__CreateSpellEmitter_x` | `0x1800A2A20` | `0x1800A2A20` | `review` | `section_delta` |
| `CRender__RenderScene_x` | `0x1800DAE50` | `0x1800DAE50` | `review` | `section_delta` |
| `CRender__RenderBlind_x` | `0x1800DAD10` | `0x1800DAD10` | `review` | `section_delta` |
| `CRender__ResetDevice_x` | `0x1800DB9C0` | `0x1800DB9C0` | `review` | `section_delta` |
| `CRender__UpdateDisplay_x` | `0x1800DCBC0` | `0x1800DCBC0` | `review` | `section_delta` |
| `__bRenderSceneCalled_x` | `0x180370610` | `0x1802CCC28` | `high` | `exact96` |
| `C2DPrimitiveManager__AddCachedText_x` | `0x1800F5820` | `0x1800F5820` | `review` | `section_delta` |
| `C2DPrimitiveManager__Render_x` | `0x1800F69C0` | `0x1800F69C0` | `review` | `section_delta` |
| `ObjectPreviewView__Render_x` | `0x1800277E0` | `0x1800277E0` | `review` | `section_delta` |
| `EQGraphics_DebugAPI_Ptr_x` | `0x1803D6FA8` | `0x180338FA8` | `review` | `section_delta` |
