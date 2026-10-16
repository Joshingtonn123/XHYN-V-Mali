<p align="center"><img src="assets/xhyn-v.png" width="160" alt="XHYN V icon"></p>

# XHYN V Reborn

An unofficial native GTA V port for Android, based on the **Chinese GTA V Android port** and maintained by **XHYN-PH**.

**[Download 0.1](https://github.com/XHYN-PH/XHYN-V-reborn/releases/tag/v0.1)** · **[Source information](docs/SOURCE.md)**

> **You must provide your own legally obtained GTA V game files.** No game-data files, RPF archives or game-download links are included here.

## Why Reborn?

My previous XHYN V repository was removed, so I had to start over. Reborn is the new home for the project, starting again at **version 0.1**.

## How it works

The game runs as native **ARM64 Android code**. **DXVK** translates its Direct3D 11 graphics calls to Vulkan. DXVK handles graphics translation; using it does not make a port a CPU or console emulator.

DXVK also supports [native ports without Wine](https://github.com/doitsujin/dxvk#dxvk-native). More detail is available in the [source notes](docs/SOURCE.md).

## Getting started

1. Install the APK from the release page.
2. Provide your own **GTA V Legacy 1.61 / build 2699** files.
3. Select English and start with the default settings.
4. Close and reopen the app after changing language or graphics settings.

Requires **Android 11 or newer**, an ARM64 device and a compatible Vulkan driver.

The menu language also selects the in-game language when supported. English is used by default and for unsupported selections. Other game languages require their matching text and font files; missing language files are not automatically replaced. Some menu translations are incomplete.

## Source and credits

The [modifications folder](modifications) contains the source for our changes. The complete game-engine source and the exact custom DXVK changes are not available here. [Source information](docs/SOURCE.md) explains what is included and how the older source code relates to this build.

Credit for the original Chinese port and third-party libraries belongs to their authors. XHYN-PH maintains this version and its modifications. See [credits](docs/CREDITS.md).

This is an unofficial project, with no affiliation to Rockstar Games or Take-Two. GTA V belongs to its respective rights holders.

## Reporting a problem

Include your phone model, GPU, Android version, graphics driver, game version and the steps that cause the problem. You can attach a report from **XHYN V → Export diagnostics** after removing any personal information.
