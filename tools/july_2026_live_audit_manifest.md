# July 2026 Live Binary Audit Manifest

## Scope

This report compares only the two requested EverQuest Live builds:

- Old: `E:\MQBuilds\Old EQ Exe's\eqgame62426.exe`
- New: `E:\MQBuilds\Old EQ Exe's\eqgame70926.exe`
- Old EQGraphics: `E:\MQBuilds\Old EQ Exe's\EQGraphics-62426.dll`
- New EQGraphics: `E:\SteamLibrary\steamapps\common\Everquest F2P\EQGraphics.dll`
- Old eqmain: `E:\MQBuilds\Old EQ Exe's\eqmain-62426.dll`
- New eqmain: `E:\SteamLibrary\steamapps\common\Everquest F2P\eqmain.dll`

Test and Legends artifacts were not used.

- Old eqgame SHA-256: `45d86cb6d415453f694873180d5df8d56f254018d2835c6b423cfb676f68a499`
- New eqgame SHA-256: `6f3c4ff56abf0decf3c5d6cea2926ec98ad97af0f4fd170aae367ee9c6a56db8`
- Old eqmain SHA-256: `1595acf15d9a895bc4f87cf161b1c4f1c994319f88fb439a90407034f04148ed`
- New eqmain SHA-256: `799a84c95f8a9c31c5d3d0fb61087e85acf9370fb23a87e97ca1a81b42612d05`

Conclusions require paired disassembly, callers/xrefs, allocations, strides, constructor stores, or vtable neighborhoods. Section-delta guesses are not accepted.

## Status

- Current `eqgame.h`: 658 candidates audited.
- Confirmed current definitions: 579.
- Wrong current definitions: 79.
- Unresolved changed definitions: 0.
- Additional semantic lifecycle correction: the old `PreZoneMainUI` and `ZoneMainUI` names did not identify the real pre-zone/zone pair.
- EQGraphics offset set: fully confirmed.
- Requested structure families: audited. Five low-use `PlayerZoneClient` names remain in two physically resolved ambiguity sets.

## Implementation Order

1. Correct structure layouts and virtual interfaces.
2. Replace the wrong function, vtable, and global definitions.
3. Correct the pre-zone/zone lifecycle pair by semantics, not old symbol lineage.
4. Build with all temporary runtime bypasses still active.
5. Restore verified detours in small groups: core/input, UI/windows, chat, graphics.
6. Remove July bring-up logging and bypasses only after smoke tests pass.

## July Layout Changes

### CXWnd

- Size remains `0x268`.
- The internal member storage is heavily permuted.
- `CSidlScreenWnd` remains `0x2d0`; its direct tail is unchanged.
- The July Live layout is not the July Test permutation. Live `WindowText` moves `0x1d8 -> 0x158`; retaining the Test/June `0x1d8` location crashes in `CXStr::FreeRep` as character select appears.
- Critical Live moves include `ClientRect 0x254 -> 0x034`, `RuntimeTypes 0x1a0 -> 0x050`, `pController 0x158 -> 0x0a8`, `Tooltip 0x050 -> 0x110`, `Location 0x124 -> 0x16c`, `ParentWindow 0x190 -> 0x240`, and `WindowStyle 0x204 -> 0x25c`.
- Client, client-clip, and screen-clip dirty flags move to `0x161`, `0x070`, and `0x0f8` respectively.
- Both eqgame and eqmain use the same July physical map. The game and login declarations are updated atomically and guarded by compile-time offset checks.
- `BackgroundDrawType` remains semantically unresolved and is represented as unknown storage; no runtime consumer outside the window inspector was found.
- `CSidlScreenWnd::ContextMenuID` remains `+0x2b8`; `ContextMenuTipID` remains `+0x2c8`. The staged swap is wrong.

### Login Frontend

- `CLoginViewManager::HandleLButtonUp` moves `0x18001B0E0 -> 0x18001B0F0`.
- The old July address begins in the preceding function's epilogue and raises `EXCEPTION_ILLEGAL_INSTRUCTION` before the login screen when AutoLogin calls it.

### CButtonWnd And Derived Controls

- `CButtonWnd`: `0x348 -> 0x350`.
- New shared-control member: `pGroupRefCtrl +0x278`.
- `Checked 0x278 -> 0x280`; `bMouseOver 0x279 -> 0x281`.
- Every field from `DecalOffset` onward moves `+0x8`.
- `CInvSlotWnd`: `0x460 -> 0x468`.
- `CSpellGemWnd`: `0x400 -> 0x408`.
- True new `CButtonWnd` vtable: `0x140AF0728`.

### ItemBase And ItemClient

- `ItemBase`: `0x108 -> 0x110`.
- `ItemClient`: `0x120 -> 0x128`.
- `ItemHash +0x54` was removed; new `+0x10c` is padding.

```text
RealEstateID 008->0EC      StackCount 00C->064       OrnamentationIcon 010->0C8
AugFlag 014->08C           GlobalIndex 018->0AC      ID 024->0C0
ScriptIndex 028->0C4       bCollected 02C->0A0       DontKnow 030->100
bRankDisabled 038->068     Power 03C->0F8           bItemNeedsUpdate 040->088
RespawnTime 044->0F4       Luck 048->0E4            NewArmorID 04C->030
NoteStatus 050->09C        ArmorType 058->060        bConvertable 05C->0BC
Charges 060->07C           pEvolutionData 068->050   SaveString 078->038
MerchantSlot 090->070      LastCastTime 098->0E8     ActorTag1 09C->108
Tint 0A0->0CC              bDisableAugTexture 0A4->098
Contents 0A8->008          ItemDef 0D0->090          bCopied 0D8->078
ItemGUID 0D9->0D0          Price 0F0->080            NoDropFlag 0F8->0B8
MerchantQuantity 0FC->0F0  ActorTag2 100->0A8        Open 104->0A4
SharedItemDef 108->110     ClientString 118->120
```

`ItemDefinition` remains `0x688`; `ItemContainer` remains `0x28`; generic containers and shared pointers are unchanged.

### PlayerZoneClient And PlayerClient

- `PlayerBase` remains `0x1c8`.
- No field was removed.
- The direct `PlayerZoneClient` payload was reordered, reducing padding by `0x30`.
- Direct span: `[0x1c8,0x65c) -> [0x1c8,0x62c)`.
- `MovementStats` remains `0x91c` and moves `0x65c -> 0x62c`.
- Embedded `ActorClient` remains `0x210` and moves `0xfe0 -> 0xfb0`.
- `PlayerClient` own boundary moves `0x1278 -> 0x1248`.
- `PlayerClient`: `0x20d8 -> 0x20a8`.
- Every member from `MovementStats` onward moves uniformly by `-0x30`.
- Every `PlayerClient`-owned field moves uniformly by `-0x30`.

Direct member map:

```text
1C8 LastIntimidateUse->1C8 | 1CC GM->284 | 1D0 Unknown3->530 | 1D4 LoginSerial->53C
1D8 AnimationSpeedRelated->224 | 1E0 HPCurrent->3F0 | 1E8 SitStartTime->260 | 1EC LastTimeStoodStill->3E8
1F0 Handle->609 | 210 bBetaBuffed->221 | 214 EnduranceMax->4E0 | 218 FishingEvent->482
21C MerchantGreed->2A8 | 220 Original->480 | 224 ViewHeight->544 | 228 pTouchingSwitch->2F8
230 IsPassenger->4D4 | 231 Blind->4D5 | 238 HPMax->330 | 240 bAnimationOnPop->220
244 Buyer->348 | 248 StandState->1D5 | 249 bTempPet->3D0 | 24C CastingData->1DC
290 NpcTintIndex->4E8 | 294 bOfflineMode->5FD | 298 MasterID->554 | 2A0 GuildID->250
2A8 bSummoned->2B5 | 2AC Unknown1->4BC | 2B0 FallingStartZ->3CC | 2B4 MissileRangeToTarget->4C8
2B8 Anon->244 | 2BC DoSpecialMelee->4CC | 2C0 PrimaryTintIndex->258 | 2C4 TitleVisible->2F7
2C8 EnduranceCurrent->55C | 2CC DragNames->56D | 34C Deity->27C | 350 LastPrimaryUseTime->4A8
354 MyWalkSpeed->2A0 | 358 IsAttacking->{484,4C0} | 35C realEstateItemGuid->268 | 36E Title->34C
3F0 AltAttack->4EC | 3F4 bAttackRelated->338 | 3F8 BearingToTarget->25C | 3FC LFG->4C4
3FD Level->564 | 400 PetID->5F8 | 404 CorpseDragCount->{484,4C0} | 408 RealEstateID->4D8
40C bBuffTimersOnHold->23C | 40D DraggingPlayer->2B6 | 450 AFK->604 | 454 RespawnTimer->1D0
458 CameraOffset->288 | 45C CharClass->{2B4,538,565} | 460 ManaCurrent->234 | 464 bSwitchMoved->4C5
465 HoldingAnimation->558 | 468 LastRefresh->560 | 46C MinuteTimer->1CC | 470 PvPFlag->2F6
471 Suffix->400 | 4F8 pCharacter->248 | 500 GMRank->4AD | 501 FindBits->{2B4,538,565}
504 SpellGemETA->4F4 | 540 Birthdate->568 | 544 LastResendAddPlayerPacket->3E4 | 548 LastSecondaryUseTime->3E0
54C Linkdead->608 | 550 Trader->1D8 | 554 bStationary->3DC | 558 LastTick->600
55C Light->3F8 | 560 ppUDP->548 | 568 GetMeleeRangeVar1->28C | 56C CombatSkillUsed->22C
574 Meditating->2A4 | 578 Mercenary->4AC | 57C Unknown4->33C | 580 bAlwaysShowAura->56C
584 LastCollision->300 | 5B4 berserker->5FC | 5B8 SecondaryTintIndex->228 | 5BC bShowHelm->{2B4,538,565}
5C0 WarCry->280 | 5C4 SomeData->5F0 | 5CC LoginRelated->488 | 5F0 pRaceGenderInfo->298
5F8 NextIntimidateTime->2B0 | 5FC ManaMax->294 | 600 HideMode->4D0 | 604 LastAttack->550
608 RunSpeed->290 | 60C InPvPArea->540 | 610 SpellCooldownETA->3D4 | 614 StunTimer->2AC
618 NextSwim->3D8 | 61C FD->1D4 | 620 pViewPlayer->340 | 628 Sneak->4E4
62C LastRangedUsedTime->4B0 | 630 LastTrapDamageTime->4F0 | 634 HibernatingCount->238 | 638 CurrIOState->3EC
63C FishingETA->534 | 640 TimeStamp->4DC | 644 CombatSkillTicks->4B4 | 64C RealEstateItemId->240
650 IntimidateCount->481 | 654 Zone->264 | 658 LastMealTime->3FC
```

Ambiguities are physical bijections, not missing bytes:

- `IsAttacking` and `CorpseDragCount`: `{0x484, 0x4c0}`.
- direct `CharClass`, `FindBits`, and `bShowHelm`: `{0x2b4, 0x538, 0x565}`.
- MQ class reads should use embedded `ActorClient::Class`, absolute `0xffc -> 0xfcc`.

Important uniform moves:

```text
WhoFollowing F78->F48       TargetOfTarget FA8->F78      mActorClient FE0->FB0
pActor 1198->1168           pAnimation 11F0->11C0        StaticCollision 1220->11F0
mPhysicsEffects 1240->1210  PhysicsEffectsUpdated 1258->1228
MercID 1378->1348           AssistName 13A1->1371        Fellowship 1578->1548
Campfire block 1DD8->1DA8  Equipment 1E0C->1DDC         SpawnStatus 20A8->2078
```

### Advanced Loot

- `AdvancedLootItem`: `0xb8 -> 0xb0`; old padding at `+0x8` was removed.
- Fields from `Name` onward move `-0x8`.
- `CAdvancedLootWnd`: `0x428 -> 0x438`.
- Existing controls through `pPLootList +0x3f0` do not move.
- New qwords occupy `+0x418` and `+0x420`.
- Old action tail `0x418/0x41c/0x420/0x424` moves to `0x428/0x42c/0x430/0x434`.

### Unchanged UI Structures

The following are unchanged and should not receive Test-derived shifts:

- `CItemDisplayWnd 0xab0` (current dirty `0x330` is wrong)
- `CChatWindow 0x4d8`
- `CContextMenuManager 0x22f0`
- `CBuffWindow 0x350`
- `CCursorAttachment 0x648`
- `CFindItemWnd 0x400`
- `CGroupWnd 0x4728`
- `CKeyRingWnd 0x4a8`
- `CLootWnd 0xcc0`
- `CMapViewWnd 0x858`
- `CPetInfoWnd 0x3d0`
- `CPlayerWnd 0x408`
- `CSpellDisplayWnd 0x3b8`
- `CTargetWnd 0x3c8`
- `CTradeWnd 0x1748`

`CChatWindow +0x490` is a pointer, not `int NamesContextMenu`. Menu IDs occupy `+0x49c..+0x4cc`.

## Graphics ABI

- `SGraphicsEngine` remains `0x60`; `pRender` remains `+0x18`.
- `CRender` remains `0xf9f0`; `pD3DDevice` remains `+0xf08`.
- New `CRender` inserts a deleting destructor at virtual slot `+0x000`.
- Every old `CRenderInterface` virtual moves by `+0x8`.
- New slots: `ResetDevice +0xe8`, `RenderScene +0x160`, `RenderBlind +0x168`, `UpdateDisplay +0x170`.
- `ReleaseGraphicsEngine`: old `EQGraphics+0x1a240`, new `+0x1a2a0`.
- Native release ordering is unchanged. MQ graphics hooks must be removed before EQ calls release at new `eqgame+0x5b8444`.

The current `eqgraphics.h` mappings are confirmed correct.

## UI Lifecycle Correction

The old names were semantically wrong:

- Real pre-zone broadcaster: old `0x1406055d0`, new `0x140609730` (`CXWnd::OnPreZone`, virtual `+0x358`).
- Real zone broadcaster: old `0x140605ad0`, new `0x140609c30` (`CXWnd::OnZone`, virtual `+0x350`).
- Old `CDisplay__PreZoneMainUI = 0x140124630` and new lineage successor `0x140126d00` are quest-container erase routines, not UI lifecycle functions.

Use:

```text
CDisplay__PreZoneMainUI_x = 0x140609730
CDisplay__ZoneMainUI_x    = 0x140609C30
```

Other lifecycle mappings are confirmed:

```text
CleanGameUI       1974F0->199C80   CleanCharSelectUI 1976C0->199E50
InitCharSelectUI  19C630->19EE00   InitNewUI         1A0D00->1A34D0
InitGameUI        19D410->19FBE0   ReloadUI          1A77A0->1A9F60
RestartUI         20A8B0->20D560
```

## Chat ABI Confirmation

The Live `ChatManagerClient::DisplayChatText` lineage is structurally unchanged
from `eqgame62426.exe+0x10eae0` to `eqgame70926.exe+0x1111d0`, but the historical
five-parameter declaration was incomplete. Both binaries read three stack
booleans after the register arguments (`rbp+0x50`, `+0x58`, and `+0x60`), so the
verified declaration is:

```cpp
void dsp_chat(const char* line, int color, bool logIsOk,
    bool convertPercent, bool makeStmlSafe, bool checkChatFilter);
```

The July chat routing helpers are also ABI-confirmed from their prologues and
call sites:

```cpp
int CChatWindowManager::GetChannelFromColor(int color);
void CChatWindowManager::AddText(CXStr* text, int color);
void CChatWindow::AddOutputText(CXStr* text, int color);
```

`CChatWindowManager::AddText` maps the color to a channel, selects the window
pointer from the manager's channel table, and forwards the same `CXStr*` and
color to `CChatWindow::AddOutputText`.

## Wrong Current eqgame Definitions

All values below are RVAs; prepend image base `0x140000000`.

### Wrong Changed Functions And Vtables

```text
CListWnd__SetItemIcon             5DA140->5DD990
CharacterZoneClient__GetBaseSkill 08AFB0->108470
ItemBase__IsLoreEquipped          570F80->678940
CButtonWnd__vftable               AEFD10->AF0728
CContainerWnd__vftable            A050B0->A05A10
MapViewMap__vftable               A52A40->A53430
```

### Wrong Globals

```text
CDisplay__cameraType DFEBCC->DFEC1C  __Guilds EB6190->EB6180
__MemCheckActive EB923D->EB921D      __MemCheckBitmask EB7B23->EB7B03
__ScreenMode DFEE64->DFEE7C           __ServerHost EB01F8->EB21E8
__gWorld EAFF10->EB1CA0               __gpbCommandEvent EB0008->EB1FF8
__CurrentMapLabel F47510->F474F0      __HWnd F33248->F33228
__HelpPath F2CA78->F2CA60             __LabelCache F480E0->F480C0
__LoginName F339DC->F339BC            __MouseEventTime F2CBB0->F2CB98
__Mouse F33250->F33230                __heqmain F33228->F33208
__m_layoutCopy F589D8->F589B8         __gCXStrAccess F58538->F58518
__RestrictionInfo B020C0->B02C50      Teleport_Table_Size EB0094->EB2084
Teleport_Table EB0520->EAFA40         __ChatFilterDefs A6A1D0->A6ABC0
instCRaid EB2520->EB2510              instDynamicZone EB6050->EB6040
instExpeditionLeader EB609E->EB608E   instExpeditionName EB60DE->EB60CE
pinstAltAdvManager DFFD08->DFFCF8     pinstCContainerMgr DFF018->DFF090
pinstCDBStr DFEAC0->DFEAB0            pinstCInvSlotMgr DFF000->DFF070
pinstDZMember EB6168->EB6158          pinstDZTimerInfo EB6170->EB6160
pinstEQSoundManager E00090->E00080    pinstEQSpellStrings DE3640->DE3630
pinstLootFiltersManager DFE508->DFE4F8
pinstSwitchManager EAF9C0->EAF9B0
```

### All 37 Stale Old Function Addresses

```text
__do_loot 22EFD0->231E50
AggroMeterManagerClient__Instance 0B4830->0B5F20
AltAdvManager__CanSeeAbility 1B2B60->1B53D0
CAAWnd__UpdateSelected 366C20->36A6C0
CAdvancedLootWnd__DoSharedAdvLootAction 0AA7B0->0ABDD0
CBroadcast__Get 0C28A0->0C4000
CChatService__GetNumberOfFriends 6BB900->675A20
CFindItemWnd__Update 157610->159BE0
CharacterZoneClient__GetAdjustedSkill 0F7810->0F91D0
CListWnd__GetItemWnd 5D73E0->5DB230
CListWnd__SetColumnWidth 5D9720->5DD570
CListWnd__SetItemText 5D9D40->5DDB90
CSidlScreenWnd__CalculateHSBRange 5BF6B0->5C35B0
CSidlScreenWnd__CalculateVSBRange 5BF580->5C3490
CSpellDisplayWnd__SetSpell 51A660->51E4D0
CStmlWnd__MakeWndNotificationTag 5E3B10->5E7900
CTextureAnimation__Draw 5CD600->5D1480
CTextureFont__GetHeight 5F2C00->5F69E0
CTextureFont__GetTextExtent 5F2C40->5F6A20
CXWnd__DoAllDrawing 5C5B40->5C99F0
CXWnd__GetClientRect 5C86D0->5CC590
CXWnd__IsReallyVisible 5CAB30->5CE9B0
CXWnd__IsType 5CAB80->5CEA00
CXWnd__Minimize 5CAC80->5CEAF0
CXWnd__ProcessTransition 5CBB90->5CF9E0
CXWnd__StartFade 5CC860->5D06C0
CXWndManager__DrawWindows 5ECF50->5F0D20
ItemBase__GetImageNum 670D20->6747B0
ItemBase__IsEmpty 6745D0->678060
ItemBase__IsLore 674E40->6788B0
ItemClient__dItemClient 2C3560->2C6350
PcBase__GetAlternateAbilityId 684FE0->688A80
PcBase__GetCombatAbility 6856D0->689310
PcClient__AlertInventoryChanged 2E6C60->2E9AB0
PcZoneClient__GetPcSkillLimit 2F85B0->2FB490
PlayerClient__GetPcClient 30B280->30E350
CDisplay lifecycle symbols: use the semantic pair documented above
```

## Confirmed Stable Systems

No July layout change was found in:

- spells, spell affects, spell managers, and spell caches
- `ItemDefinition`, item/profile containers, and generic container templates
- `BaseProfile`, `PcProfile`, `PcBase`, `PcClient`, and `CharacterZoneClient` tails
- doors, ground items, groups, raids, aggro data, tasks, world/zone data
- target indicator and target-manager tail
- guild, fellowship, mercenary, achievements, tribute, aura, social, and real-estate records
- common list, tab, page, combo, edit, STML, and texture-animation derived layouts

## Pre-existing Source Model Corrections

These were wrong in both Live binaries and are not July regressions. Keep them in a separate cleanup patch if possible.

### Player Points

- `CPlayerPointManager` is `0x30`: `ArrayClass<Point> +0`, `SoeUtil::String +0x18`.
- Placement remains `PcClient +0x2208`.
- `PointSystemBase` begins `+0x2238`; real-estate arrays remain `+0x2268/+0x2280/+0x2298`.
- Existing loyalty fields at `+0x2258/+0x225c/+0x2260` overlap the proven string and are invalid.

### Tradeskills

- `CTradeskillWnd` is `0x10d8`, not `0x10e0`.
- Manager pointer `+0x3b8`; `SearchResults[100] +0x3c0`; count `+0x6e0`; flag `+0x6e8`; container item pointer `+0x6f0/+0x6f8`.
- `TradeskillRecipe` is `0x100`, not `0xa8`.
- Recipe fields: integers `+0..+0x10`, name `+0x14`, detail value/flag `+0x54/+0x58`, ingredients `+0x5c`, icons `+0x84`, ingredient names `+0xb0`.

### Social Windows

- `EQSocial` remains `0x51c`.
- `CActionsWnd` is `0x450`; controls occupy `+0x2d8..+0x448`.
- `CSocialEditWnd` is `0x3c0`; controls occupy `+0x2d4..+0x3b8`.
- `__CurrentSocial`: old `0x140C210E4`, new `0x140C230E4`.

## Runtime Validation

July Live smoke test passed on 2026-07-16 after correcting the `CXWnd` permutation and login frontend target:

- reached the login screen with the MQ window visible
- entered the game and remained stable while idle
- `/plugin` completed normally
- zoning completed normally
- camping/logging out completed normally

This establishes a known-good startup, UI initialization, command, zone-transition, and logout baseline. It does not by itself validate every datatype, structure field, or plugin workflow.

## Temporary Bring-up Changes

The current worktree contains July crash-isolation guards across graphics, input, window hooks, chat, pulse, plugin handling, frame limiting, auto inventory, login frontend, display hooks, and `MQ2ChatWnd`. These guards are not binary fixes. Restore them incrementally only after the corresponding structures and targets are corrected.

Do not use `tools/compare_eqgame_offsets.py` section-delta output as a patch source. Its fallback targets are proven wrong for multiple core globals and embedded objects.
