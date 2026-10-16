# Bink decoding and playback

This upstream build note describes the Linux/Android decoder, ABI, background work and dependency licenses. The Android packaging script includes it in the APK as the FFmpeg build notes. Source paths below refer to the upstream source tree; they do not mean that source is included in this APK.

## Implementation and formats

The game retains the original Bink ABI, bwMovie, RAGE file callbacks, audio provider and texture uploads. FFmpeg 8.0.1 decodes Bink 1 and the older Bink DCT/RDFT audio. A separate CPU adapter decodes KB2g/Bink 2.2 mission videos.

The newer SDK headers are not used with the old ABI: their plane member order and frame buffer count differ. The supplied 2026 SDK also lacks expand.h, required by Bink 1, and uses NO_BINK10_SUPPORT.

FFmpeg enables only the required Bink video/audio decoding and PCM conversion. Networking, tools, other decoders, GPL and nonfree components are disabled. Download sources and SHA-256 hashes are pinned in BinkFfmpeg.cmake. Downloads are cached in target/downloads; the complete dependency source is in the build directory under bink-ffmpeg/source.

The KB2g core comes from the supplied Bink2Source-2026.03.31.7z. Its origin, checksums and original notices are preserved under src/dev_ng/rage/suite/src/bink/native2/. It is managed separately from the FFmpeg/Bink 1 code.

bink1_decoder validates the container, frame index and audio track sizes, and outputs Y/Cr/Cb/A planes and interleaved S16 PCM. Up to four audio tracks can be selected. Queues are bounded; if audio consumption stalls, dropped audio is reported rather than blocking rendering. FFmpeg buffers are released by their own allocator and are not counted as RAGE allocations. Plane pointers and strides are obtained again whenever textures are locked, avoiding writes to stale addresses after a discard map.

The color matrix follows each file's BINKYCRCBNEW flag. Switching back to older programs restores the original parameters. The adapter rejects unsupported BIKk full-range color and retains the old SDK's keyframe and return-value semantics. Pixel, PCM and format boundaries are documented in NUMERICAL_COMPATIBILITY.md, NUM-014 through NUM-016.

## Background decoding contract

Each open movie has one worker thread for reads, audio track indexing, keyframe seeking and decoding. Rendering only polls completed results and uploads separate planes. RAGE audio callbacks remain on their original thread.

Only the latest request and one pending frame are kept. A new seek cancels old work at the next I/O boundary; old results cannot overwrite a new channel. Closing waits for an entered file callback to return before closing the file. A single read already blocked inside the provider cannot be interrupted.

Multi-track audio indexes are committed for complete frames. Cancellation does not corrupt later timestamps. A completed seek resets the playback clock. Non-looping playback uploads the final frame before stopping. Linux pending seeks are coalesced to the latest target. Pause, looping and storage lifetime retain their original contracts.

The two channels of ordinary television are original game behavior. TV_HLP_LEST1B_1 uses the original script's left/right channel switching and up/down volume controls. INPUTGROUP_MOVE and INPUT_PHONE prompts are routed accordingly. Input is withdrawn when the mission withdraws its prompt; no exit action absent from the original mission is added.

## Upstream validation scope

The standalone tests/bink1 project covers full real Bink 1/KB2g movies, random seeking, image/audio output, short reads, invalid containers and deliberately blocked I/O. FFmpeg build parallelism is controlled by GTAV_BINK_BUILD_JOBS, defaulting to 1; the outer --parallel option does not replace it.

Historical development sanitizer, ARM64 decoding and background regression runs passed according to the upstream note. The mission movies are lester1b_1.bik and lester1b_2.bik; passing ordinary programs is not a substitute for testing these movies. Final story mission playback still requires acceptance testing, with scope described in records/platform-validation.md. Affected inputs are retested when decoding or related behavior changes; this does not automatically require launching the whole game.

These are upstream records, not runtime test results for this English test APK.

## Licenses and distribution materials

FFmpeg is used under LGPL 2.1 or later. Its original license is packaged with the APK. Distributing a statically linked build also requires the corresponding library source, build modifications, and materials needed to replace or relink the library. A source URL alone does not replace those materials.

Bink 1/audio decoding does not use the SDK source. The separate Bink 2 video core comes from the supplied 2026 SDK, retains its original notices, and is not part of FFmpeg or the LGPL code.
