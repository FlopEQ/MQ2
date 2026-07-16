# Offset Comparison

Old: `E:\MQBuilds\Old EQ Exe's\EQGraphics-62426.dll`
New: `E:\SteamLibrary\steamapps\common\Everquest F2P\EQGraphics.dll`

Old version: `Jun 24 2026 10:04:15`
New version: `Jul  9 2026 11:15:49`

Defines compared: `13`
Changed addresses: `10`
High-confidence relocations: `11`
Review-needed section-delta relocations: `2`
Unresolved relocations: `0`

## Method Counts

- `code56`: 5
- `code61`: 2
- `code57`: 2
- `section_delta`: 2
- `code26`: 1
- `code58`: 1

## Review Needed

| Name | Old | New | Section | Method |
| --- | ---: | ---: | --- | --- |
| `__bRenderSceneCalled_x` | `0x180370610` | `0x180370610` | `.data` | `section_delta` |
| `EQGraphics_DebugAPI_Ptr_x` | `0x1803D6FA8` | `0x1803D6FA8` | `.data` | `section_delta` |

## All Results

| Name | Old | New | Confidence | Method |
| --- | ---: | ---: | --- | --- |
| `__eqgraphics_fopen_x` | `0x180281408` | `0x180282058` | `high` | `code61` |
| `CEQGBitmap__GetFirstBitmap_x` | `0x180003250` | `0x180003250` | `high` | `code26` |
| `CParticleSystem__Render_x` | `0x1800B2E10` | `0x1800B34C0` | `high` | `code56` |
| `CParticleSystem__CreateSpellEmitter_x` | `0x1800A2A20` | `0x1800A3090` | `high` | `code56` |
| `CRender__RenderScene_x` | `0x1800DAE50` | `0x1800DB6A0` | `high` | `code56` |
| `CRender__RenderBlind_x` | `0x1800DAD10` | `0x1800DB560` | `high` | `code56` |
| `CRender__ResetDevice_x` | `0x1800DB9C0` | `0x1800DC210` | `high` | `code56` |
| `CRender__UpdateDisplay_x` | `0x1800DCBC0` | `0x1800DD410` | `high` | `code57` |
| `__bRenderSceneCalled_x` | `0x180370610` | `0x180370610` | `review` | `section_delta` |
| `C2DPrimitiveManager__AddCachedText_x` | `0x1800F5820` | `0x1800F6090` | `high` | `code58` |
| `C2DPrimitiveManager__Render_x` | `0x1800F69C0` | `0x1800F7230` | `high` | `code61` |
| `ObjectPreviewView__Render_x` | `0x1800277E0` | `0x180027840` | `high` | `code57` |
| `EQGraphics_DebugAPI_Ptr_x` | `0x1803D6FA8` | `0x1803D6FA8` | `review` | `section_delta` |
