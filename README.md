<p align="center"><img src="assets/xhyn-v.png" width="160" alt="XHYN V icon"></p>

# XHYN V Reborn

An unofficial GTA V Android project maintained by **XHYN-PH**. Version **0.1** starts again from the DXVK base, with English translations, language selection and the violet XHYN V theme.

**[Download 0.1](https://github.com/XHYN-PH/XHYN-V-reborn/releases/tag/v0.1)** · **[Changes](CHANGELOG.md)** · **[Source information](docs/SOURCE.md)**

> **Test release.** Build checks passed, but phone gameplay and performance have not been verified. Users must provide their own legally obtained GTA V game files. No GTA V game-data files, RPF archives or game-download links are supplied here.

## What is it?

The supplied game engine runs as native **ARM64 Android code**. **DXVK** converts its Direct3D 11 graphics calls to Vulkan. A graphics translation layer can be used by a native port; it does not by itself make the project a CPU or console emulator.

DXVK's own documentation describes [native use without Wine](https://github.com/doitsujin/dxvk#dxvk-native). See [the source and evidence notes](docs/SOURCE.md) for what has been inspected and what remains unavailable.

## Getting started

1. Install the APK from the 0.1 release.
2. Provide your own legally obtained **GTA V Legacy 1.61 / build 2699** files.
3. Choose **English** first and launch with the default settings.
4. After changing language or renderer settings, close XHYN V and reopen it before starting another game session.

Requires **Android 11 or newer**, an ARM64 device and a compatible Vulkan driver. Other game versions and broad GPU compatibility are unverified.

## New in 0.1

- English launcher, trainer labels and touch layouts.
- A supported menu language also selects the game language on the next full launch. No explicit selection or an unsupported game language uses English in game.
- Violet theme, XHYN V name and original V icon.
- DXVK configuration switch with a recovery copy, compiler-worker and refresh controls.
- Clearer exit reports, persistent renderer-cache identities and diagnostic export.

Some menu translations are incomplete. Other game languages require their corresponding text/font resources. Missing game packs are not automatically detected and replaced with English.

## Source and credits

Our modification source is in [modifications](modifications). This is **not the complete GTA V engine source**, and the exact custom DXVK patch set used by the supplied base is unavailable. The [source notes](docs/SOURCE.md) explain these limits.

GTA V belongs to its respective rights holders. XHYN-PH maintains these modifications; credit for the original engine, Android base and third-party libraries remains with their authors. This project is unofficial and is not affiliated with Rockstar Games or Take-Two. See [credits and notices](docs/CREDITS.md).

## Reporting a problem

Include your phone/GPU, Android version, selected driver, game build and steps to reproduce. Use **XHYN V → Export diagnostics**, review the report, and remove personal information before attaching it to an issue. No FPS gain or fix for the earlier ten-minute crash is claimed yet.
