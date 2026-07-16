# Offset Comparison

Old: `E:\MQBuilds\Old EQ Exe's\eqmain-62426.dll`
New: `E:\SteamLibrary\steamapps\common\Everquest F2P\eqmain.dll`

Old version: `not embedded`
New version: `not embedded`

Defines compared: `12`
Changed addresses: `8`
High-confidence relocations: `5`
Review-needed section-delta relocations: `7`
Unresolved relocations: `0`

## Method Counts

- `section_delta`: 7
- `code51`: 1
- `code52`: 1
- `code57`: 1
- `code56`: 1
- `code58`: 1

## Review Needed

| Name | Old | New | Section | Method |
| --- | ---: | ---: | --- | --- |
| `EQMain__CLoginViewManager__HandleLButtonUp_x` | `0x18001B0E0` | `0x18001B0F0` | `.text` | `paired_disassembly` |
| `EQMain__pinstCEQSuiteTextureLoader_x` | `0x180177DF0` | `0x180178DF0` | `.data` | `section_delta` |
| `EQMain__pinstCLoginViewManager_x` | `0x18017F4F8` | `0x1801804F8` | `.data` | `section_delta` |
| `EQMain__pinstCXWndManager_x` | `0x1803824C8` | `0x1803834C8` | `.data` | `section_delta` |
| `EQMain__pinstCSidlManager_x` | `0x1803824D0` | `0x1803834D0` | `.data` | `section_delta` |
| `EQMain__pinstLoginController_x` | `0x18017F500` | `0x180180500` | `.data` | `section_delta` |
| `EQMain__pinstLoginServerAPI_x` | `0x18017F4E0` | `0x1801804E0` | `.data` | `section_delta` |

## All Results

| Name | Old | New | Confidence | Method |
| --- | ---: | ---: | --- | --- |
| `EQMain__CEQSuiteTextureLoader__GetTexture_x` | `0x18008EA80` | `0x18008EED0` | `high` | `code51` |
| `EQMain__CLoginViewManager__HandleLButtonUp_x` | `0x18001B0E0` | `0x18001B0F0` | `high` | `paired_disassembly` |
| `EQMain__LoginController__GiveTime_x` | `0x180016640` | `0x180016640` | `high` | `code52` |
| `EQMain__LoginController__Shutdown_x` | `0x180016E40` | `0x180016E40` | `high` | `code57` |
| `EQMain__LoginServerAPI__JoinServer_x` | `0x180018050` | `0x180018060` | `high` | `code56` |
| `EQMain__WndProc_x` | `0x18000C220` | `0x18000C220` | `high` | `code58` |
| `EQMain__pinstCEQSuiteTextureLoader_x` | `0x180177DF0` | `0x180178DF0` | `review` | `section_delta` |
| `EQMain__pinstCLoginViewManager_x` | `0x18017F4F8` | `0x1801804F8` | `review` | `section_delta` |
| `EQMain__pinstCXWndManager_x` | `0x1803824C8` | `0x1803834C8` | `review` | `section_delta` |
| `EQMain__pinstCSidlManager_x` | `0x1803824D0` | `0x1803834D0` | `review` | `section_delta` |
| `EQMain__pinstLoginController_x` | `0x18017F500` | `0x180180500` | `review` | `section_delta` |
| `EQMain__pinstLoginServerAPI_x` | `0x18017F4E0` | `0x1801804E0` | `review` | `section_delta` |
