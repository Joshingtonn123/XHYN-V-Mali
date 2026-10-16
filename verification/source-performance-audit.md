# Native source and performance audit — XHYN V 0.1

The uploaded archive is useful for understanding language IDs, text/font archives and Android integration. It is not the exact complete native source tree used by the original Chinese-port APK.

## Revision evidence

- The APK packaging metadata records custom DXVK checkout `6a0ea561f9add008899680e6c313aa21c151e03e`.
- The archive's `src/dev_ng/CMakeLists.txt` defaults to revision `70d7508c01201ed3d4bfb33da42ba834eafe3857` and `patches/dxvk_android-global-sdl.patch`.
- The APK warns that its packaging source commit/dirty state may describe packaging time rather than the actual engine build. Actual binary SHA-256 values and ELF build IDs are the reliable patch guards.
- This engine's ELF build ID is `6772f303e9542e621ae915435dbdf7ef2a69403d`.

## Custom patch files recorded by the APK

A full filename inventory of the extracted archive found none of these exact custom patch files. These are metadata fingerprints, not proof of which individual optimization is active at runtime.

| Patch | Recorded SHA-256 | Archive result |
|---|---|---|
| dxvk-gplall-descriptor-batch.patch | be85caf334631b23eb3527d99a9eb16a75ecb4f9bdfe967b80c541210f7732a2 | Missing |
| dxvk-gplall-null-view.patch | 974426c76502b121b57d7614692f59a48134d48af09c939d3fa3b283ae5a20b1 | Missing |
| dxvk-gplall-android.patch | 253793b2c012c795c0973796f7f08934f9d25091abb748667625b9ec2b45057c | Missing |
| dxvk-gplall-pipeline-layout-dirty.patch | not recorded | Missing |
| dxvk-gplall-async-interop.patch | aea80190884a20377b20b6ce6b2209cd0f1aa1133906e2ab5f8a1ad985910e54 | Missing |
| dxvk-gplall-uniform-dirty.patch | 6a0e1df25144b9ca4b7504dc0580202f800f70d7a3afbbf017cb28326b45ad55 | Missing |

## Useful archive patch ideas and limits

The available `dxvk_android-global-sdl.patch` describes allocator locking, Android SDL loading/lifetime behavior, transient null surface handling, SUBOPTIMAL presentation behavior and load/store-op compatibility. It provides review leads, not a compatible replacement for the APK's custom renderer.

The allocator hunks have no surrounding function context. The presenter patch broadly accepts every nonnegative Vulkan result; a compatible implementation must explicitly distinguish successful acquisition/SUBOPTIMAL from TIMEOUT or NOT_READY. Copying those hunks without the matching fork and lifetime rules could cause correctness failures.

The shipped DXVK and integration libraries are stripped and do not expose the internal presenter/allocator implementations needed for a safe binary rewrite. No allocation, queue, descriptor or upload patch was applied to those binaries. Their original hashes remain unchanged in `regressions.json` and `apk-verification.json`.

## Work included and remaining

Included: compiler-worker controls with verified startup override path; persistent cache identities; existing async/descriptor controls; display/lifecycle/restart safeguards; bounded progress updates and session diagnostics; repeatable benchmark/capture workflow.

Still open: native shader warmup budgets/cancellation, additional surface/presenter policy, exact allocator locking changes, new queue batching/wait removal, new descriptor/uniform/upload reuse, streaming/decompression changes, and PGO. PGO requires matching buildable source and representative ARM64 profiles. Packaging metadata already mentions ThinLTO; 0.1 does not add a new LTO or PGO build.

There is no device benchmark, measured FPS gain or established fix for the reported ten-minute crash. Session interval averages cannot be used as frame-time percentiles. Native captures may contain only short windows.

The source archive itself is excluded from the deliverables. GitHub was not accessed or changed.
