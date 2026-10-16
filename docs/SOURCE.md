# Source and native-port explanation

## Why does this use DXVK?

There are two separate parts:

| Part | Role in this build |
|---|---|
| Game CPU code | Native ARM64 Android ELF libraries, including `libgtav.so`, loaded through the Android/SDL launcher |
| Graphics | Direct3D 11/DXGI calls handled by the bundled native DXVK libraries, which use Vulkan |

DXVK is a graphics API implementation. Its upstream documentation explicitly supports [native game ports without Wine](https://github.com/doitsujin/dxvk#dxvk-native). Its presence is not evidence of CPU or console emulation. Similarly, whether source is publicly available does not determine whether a program executes native machine code.

For this supplied APK, the inspected payloads are ARM64 ELF shared libraries. The launcher enters the native engine through SDL's `nativeRunMain`. The packaged-library inspection did not identify a bundled Wine, FEX, Box64 or QEMU runtime. This is evidence about the inspected package, not a claim that the complete original build process or every upstream dependency has been independently reproduced.

The deferred experimental **native Vulkan renderer** is a different graphics backend. This Chinese Android port already has native ARM64 CPU execution; switching the graphics backend is separate work.

## What source is included?

The [modifications directory](../modifications) contains the Java helpers, JNI language bridge, exact-build patch/hook scripts, translation mapping, compile-only stubs and verification scripts used for our changes. They cover language selection, configuration, cache identity, display requests, session handling and diagnostics.

The [verification directory](../verification) contains package checks, native patch bytes/addresses, the language emulation matrix, regression checks and host-test output. These can help review our changes. They do not establish that gameplay works on a phone.

## What is unavailable?

- The complete original game engine and Android-base source, with verified provenance and redistribution permission.
- The exact custom DXVK patch set used for the supplied renderer binaries.
- A complete public rebuild from source of the entire APK.

Older source code was supplied during development, but it does not fully match the engine and custom DXVK build used here. This public repository contains our modification layer. Proprietary engine code, decompiled original launcher code, game data, private signing material and private development checkpoints are excluded.

Upstream open-source component links are listed in [CREDITS.md](CREDITS.md). An upstream repository is not a substitute for the missing exact custom changes. This repository must not be described as the complete open-source GTA V port.

## Exact binary identity

| Artifact | SHA-256 |
|---|---|
| Supplied base APK | `40b08f37e632eb50cba8ee11370eb595a1450659c09d1268ba65d1b57205be24` |
| Original `libgtav.so` | `b0464aa55843ebab78cb9993ec89146c08c29145c58a62f9197f2348248149f5` |
| Language-patched `libgtav.so` | `1ba6de9319498877b831620d1972d2edbed87d58573dde3ce3265cffebf0281c` |
| Signed XHYN V 0.1 APK | `34c1183d6b74336a0b5825ce896ccb9b46c00ab654bb39ae486226a3edb0ce4d` |

All other original native libraries are preserved byte for byte. `libxhyn_locale.so` is the new JNI helper. Binary/header evidence is in [native-runtime.json](../verification/native-runtime.json).

The original engine's ELF build ID is `6772f303e9542e621ae915435dbdf7ef2a69403d`. The APK packaging metadata records DXVK checkout `6a0ea561f9add008899680e6c313aa21c151e03e`, while warning that packaging metadata may not identify the actual engine build. The binary hashes are the guards used for patching.

## Source licensing

Publication here permits inspection; it does not relicense GTA V, the supplied engine or third-party components. No blanket open-source license is claimed for the full APK. Existing third-party notices remain applicable. A native port still has copyright and dependency-license obligations; the word "native" does not remove them.
