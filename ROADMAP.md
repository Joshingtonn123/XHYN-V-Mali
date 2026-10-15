# XHYN V Reborn — combined roadmap

The uploaded DXVK-GPLALL 2.6.8 APK is the main development base. The 845 native Vulkan variant remains experimental, with its modifications deferred until the DXVK base is refined.

This combines the language, reliability, launcher, and performance suggestions into 34 tasks. All checkboxes describe planned work. Adding this document does not mean the APK features have been implemented or their performance verified.

## Phase 1 — English and language compatibility first

- [ ] **1. Complete English translation.** Cover the launcher, settings, trainer, touch editor, driver importer, diagnostics, dialogs, help text, and bundled control labels. Use a consistent translation catalog so future changes remain maintainable.
- [ ] **2. Support normal phone locales.** Trace and correct Chinese-only startup and resume restrictions in this DXVK engine. Verify its own code locations rather than reusing binary offsets from the native Vulkan build.
- [ ] **3. Separate launcher and game languages.** Default the launcher to English, provide English fallback for untranslated launcher text, and let game language be selected independently from the phone locale.
- [ ] **4. Coordinate game text, resources, and fonts.** Offer game languages only when supported by the engine and installed assets. Handle missing language/font resources with a useful fallback or error. A launcher translation does not supply missing game language files.
- [ ] **5. Translate touch layouts safely.** Preserve action bindings, IDs, inheritance, geometry, and numeric values. Check label-length limits and compatibility with previously saved English layouts.
- [ ] **6. Improve startup and import errors.** Keep preparation and native-loading failures inside a readable error flow. Explain where extracted game files belong and label ZIP/RAR importing as mod importing where that is its actual function.

The first test APK should focus on these six tasks. Check first launch, returning from the background, English and other phone locales, installed game-language resources, and both fresh and existing touch layouts before performance changes.

## Phase 2 — Reliability and settings carryovers

- [ ] **7. Preserve the DXVK configuration switch and recovery copy.** Keep custom text across disabling, repeated settings edits, and re-enabling. Use safe writes and persistent recovery instead of relying only on a rolling backup. This switch controls overrides; DXVK remains the renderer.
- [ ] **8. Fully remove BCn decoding.** Remove the option, automatic/forced decoding paths, importer/loader integration, and decoder libraries. Check texture-compression capabilities and explain incompatibility on devices that require decoding.
- [ ] **9. Correct exit classification.** Preserve native exit codes, low-memory records, SIGKILL records, and crash traces. Distinguish an intentional Quit from an unexpected exit; retain ambiguous SIGKILL records without automatically calling them low-memory kills.
- [ ] **10. Add bounded session diagnostics and export.** Record available memory, swap, thermal state, frame history, actual driver/renderer identity, and effective settings. Preserve useful log tails and associate files with the correct session. Export locally through a user-requested report, without forced uploads.
- [ ] **11. Correct display-mode selection.** Preserve the current screen dimensions when choosing refresh rates. Offer Auto, 60 Hz, and supported higher-refresh choices, keeping display refresh separate from the game FPS cap.
- [ ] **12. Bound shutdown and add apply-and-restart.** Handle an engine thread that fails to stop, and reload driver/renderer changes through a fresh process with clear save handling.
- [ ] **13. Recover a working configuration.** After repeated failed starts, offer reversible restoration of the last working graphics/driver/configuration selection while preserving saves, mods, and personal touch layouts.
- [ ] **14. Check installations and bundled layouts.** Detect missing or mixed game files, incorrect names, malformed JSON, invalid references, and incompatible labels before launch or release. Preserve the newer base's valid mobile controls and diagnostic features.
- [ ] **15. Import and export complete settings profiles.** Include graphics overrides, renderer choice, driver identity, supported DXVK options, environment variables, and touch layouts. Validate imported settings against the selected renderer and device.

## Phase 3 — Performance tuning and launcher improvements

- [ ] **16. Establish a repeatable gameplay baseline.** Record frame times, CPU/GPU work, memory trends, temperatures where exposed, and exit reasons. Include sessions long enough to investigate the reported crashes after roughly ten minutes.
- [ ] **17. Reduce diagnostic and file-handling overhead.** Keep detailed capture opt-in and bounded. Remove redundant renderer/configuration lookups, repeated directory scans, and avoidable synchronous file work during gameplay or launch preparation.
- [ ] **18. Strengthen persistent cache identity.** Fingerprint the actual renderer and driver binaries, including replacements with unchanged filenames. Preserve compatible caches and separate incompatible ones; do not require clearing every cache on every change.
- [ ] **19. Tune existing compiler-worker controls.** Compare Auto with supported limited worker counts under the same route and thermal conditions. Map controls to the actual DXVK fork. A compiler-thread count does not select particular CPU cores.
- [ ] **20. Tune FPS limits, frame queues, and sustained-play presets.** Compare supported latency/queue controls and 30/60 FPS targets. Develop measured performance, balanced, and sustained-play profiles, changing one variable at a time rather than enabling every experimental option.
- [ ] **21. Add reversible workload controls.** Expose shadow distance, rendering resolution, and supported expensive effects. Preserve original values. Coordinate feature-level choices across launcher arguments, DXVK configuration, and settings.xml.
- [ ] **22. Compare System and imported drivers.** Test the same game route and settings using compatible drivers. Report the actual loaded driver, Vulkan capabilities, and tested status; avoid claiming one driver is fastest on every device.
- [ ] **23. Validate renderer-specific controls.** Expose compiler, memory, HUD, and environment settings only where their implementation is verified. Explain unsupported options, retain the DXVK configuration switch, and keep irrelevant D3D9 controls out of this D3D11 launcher.
- [ ] **24. Improve bounded shader/pipeline preparation.** Reuse valid caches, investigate controlled warm-up where the renderer permits it, limit competing background work, and show meaningful progress when measurable. A cache does not guarantee that first-use pipeline compilation disappears.

The first performance batch should cover logging/file overhead, cache handling, compiler/FPS tuning, reversible graphics controls, and driver comparisons. The base already contains caching, async interop, and descriptor/uniform-related work; compare and refine those implementations before adding overlapping systems.

## Phase 4 — Native engine and DXVK work

These tasks depend on identifying compatible engine and renderer sources, or narrowly verified binary changes. The supplied archive is a useful reference, but it is not established as the exact source of this APK or its custom GTA/DXVK 2.6.8 implementation. Its origin and redistribution permissions also remain unresolved.

- [ ] **25. Review Android surface and SDL integration patches.** Check native-window loss and recreation, pause/resume behavior, and shared SDL runtime handling against the current base. Adapt only relevant missing changes.
- [ ] **26. Review swapchain recreation behavior.** Check for repeated recreation on persistent SUBOPTIMAL results. Handle successful acquisition, suboptimal acquisition, timeout/not-ready, and actual errors explicitly; do not copy broad nonnegative-result checks without reviewing the call path.
- [ ] **27. Audit allocation locking and resource lifetime.** Review the supplied mutex additions against surrounding locking. Investigate retained textures/buffers, fragmentation, failed allocations, and GPU-completion-aware cleanup. Do not assume these changes explain the ten-minute crash.
- [ ] **28. Reduce measured waits and submission overhead.** Profile engine/render/DXVK handoffs, flushing, queue locking, and submission frequency. Test batching and the existing async interop path while preserving resource dependencies and synchronization correctness.
- [ ] **29. Refine descriptor, uniform, and upload reuse.** Investigate repeated updates, allocations, and copies. Compare against the descriptor batching and uniform/layout tracking already present, and reclaim reused resources only after their GPU work completes.
- [ ] **30. Optimize measured asset-streaming bottlenecks.** Investigate blocking reads, repeated decompression/preparation, page faults, loading contention, and memory pressure while preserving asset compatibility and data validation.
- [ ] **31. Optimize measured ARM64 CPU hotspots and builds.** Evaluate suitable NEON/vectorization opportunities and representative profile-guided optimization. Check existing optimization/LTO settings first; adding flags already in use is not a new improvement. Measure correctness and sustained performance for each change.

## Phase 5 — Experimental graphics features

- [ ] **32. Evaluate other pinned DXVK revisions.** First preserve or reconstruct the engine/renderer interface and obtain any required matching custom patches. Build and test the engine and renderer as a compatible pair, then compare with the current 2.6.8 baseline. Config keys alone cannot recreate missing interop code.
- [ ] **33. Evaluate spatial upscaling.** Investigate a native presentation/upscale pass using a compatible implementation. Compare lower rendering resolution plus upscaling against native resolution for image quality, GPU cost, memory use, and real frame times.
- [ ] **34. Research optional frame generation.** Verify access to completed frames and presentation before choosing an implementation. Start with an optional 2x experiment on a stable baseline, recording real versus presented FPS, latency, artifacts, GPU work, and memory. Respect the implementation's licensing and asset requirements.

The 845 native Vulkan track remains deferred. Revisit its black-screen problem and engine-source compatibility after the DXVK language and reliability baseline is working.

## How changes will be judged

Use the same device, game files, driver version, resolution, graphics settings, FPS limit, save/route, and comparable starting temperatures. Record cache state so first-run compilation and warmed runs are not mixed. Compare typical frame times, slow-frame percentiles, stutter events, memory growth, thermal behavior, image correctness, controls, and session completion.

Keep the current engine/renderer pair together while establishing the language baseline. A feature is complete only after implementation and relevant checks; a performance gain requires comparable device measurements. None of the proposed library changes is a verified fix for the existing long-session crash.
