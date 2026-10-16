# Changes

## 0.1 — 16 October 2026

New DXVK base and a fresh version series.

- Translated the inventoried launcher text, trainer display strings and 89 touch layouts into English.
- Added menu/game-language selection with English defaults and fallback for unsupported selections.
- Patched this exact engine's Chinese-only language gate and separated its font and text-archive selection.
- Restored the original violet XHYN V theme and V icon.
- Added a custom DXVK configuration editor/switch with a preserved disabled snapshot.
- Added compiler-worker and current-resolution refresh controls. Workers retain the base default of 2.
- Added persistent cache identities using library, OS and actual driver information.
- Improved exit classification, native-main return reporting, fresh-process restart handling and bounded SDL shutdown.
- Added bounded local diagnostics, a ten-minute comparison marker and access to the existing benchmark.

### Validation and limits

58 helper checks passed on the host. Native language instructions passed all 14 engine language IDs under ARM64 emulation with 4 KiB and 16 KiB page models. Signature, ZIP/native alignment, DEX references, retained payload hashes, icons and touch-layout checks passed.

Some menu-language bundles are partial. Official localized game resources are required. Other GTA versions remain unsupported. Remaining native renderer, streaming and PGO work needs matching source and device measurements.
