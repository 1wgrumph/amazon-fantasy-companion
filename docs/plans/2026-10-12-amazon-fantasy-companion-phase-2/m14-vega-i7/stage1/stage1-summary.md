# M14 Stage 1 — Vega Virtual Device rendered display

Verdict: GO.

The Vega Virtual Device reached a rendered, interactive guest display inside the sandbox on the supported host (Ubuntu 24.04.4). SDK 0.24.12112. Vega CLI 1.4.5 remained NOT_ADMITTED and ran only inside the sandbox under amendment DEC-AFC-M14-I7-SANDBOX-20261020.

## Flags that worked

```
LIBGL_ALWAYS_SOFTWARE=1
GALLIUM_DRIVER=llvmpipe
MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
vega virtual-device start --timeout 600
```

GUI and gl-accel stayed at their defaults, both on. The display was a local Xvfb on :91 started with `-nolisten tcp`.

The guest settled on the ready screen. `inputd-cli button_press KEY_RIGHT` exited 0 and changed the settings-gear pixels (1040 pixels, guest box x=891..926 y=21..56). `inputd-cli button_press KEY_ENTER` exited 0 and replaced that screen with Settings / Account Settings (18798 guest pixels, x=43..926 y=21..415). The emulator skin did not change. Stop exited 0 and the next status was `{"running":false,"process_ids":{"qemu":-1}}`. During shutdown the emulator process group still died with SIGSEGV. That stop result is recorded in the run strace.

## Hypotheses

(a) Supported host, default `vega virtual-device start --timeout 600`, two attempts. The first died on a stale AVD lock that names a pid. Inside a fresh pid namespace that pid can belong to a live unrelated process, and the emulator exits. The second attempt, after both lock files were removed, SIGSEGV'd because the sandbox GL loader had no GLES 2 config. A third attempt with the same flags would have repeated that crash.

(b) Software rendering, three attempts. `--no-gl-accel` reached `running:true` with `library_mode swiftshader_indirect` and a black guest; both screenshots matched and showed only the emulator skin. Default flags plus the llvmpipe environment, after the host Mesa driver closure was mounted read-only, painted the guest. The input in that attempt ran during the splash, exited 253 (`Cannot read properties of undefined (reading 'trim')`), and the device was gone for the next command. The third attempt used the same flags and waited 12 seconds. It met all four success criteria. Run id `run-20261020T231237-9b8e52ee`.

(c) DRM node, shared-memory, and pulse passthrough was not run. llvmpipe painted the guest with no DRM device node. The sandbox account is not in the video or render groups, so those nodes stay inaccessible. That is recorded and was not requested as a group change.

## Criteria

1. Status before input: `{"running":true,"process_ids":{"qemu":74}}`.
2. `guest-before.png` shows the guest ready UI (planet icon, "Vega Virtual Device is ready"), separate from the remote skin.
3. KEY_ENTER exited 0. `guest-after-key-enter.png` shows Settings / Account Settings. KEY_RIGHT also exited 0 and moved pixels on the gear.
4. Stop exit 0, status `running:false`, shutdown SIGSEGV recorded. The stop was not free of SIGSEGV.

## Containment

On the successful run the proxy allowed 8 connections to k-artifactory-external.labcollab.net and 1 to kepler-static-artifacts.kepler.labcollab.net. The canary host was denied. One CONNECT was rejected as incomplete, with 0 bytes, before a host was parsed. No non-loopback connect succeeded. The telemetry helper was spawned 28 times and every exec returned EACCES because the home mount is noexec. `optIn` stayed false. `crashpad_handler` was exec'd with an off-allowlist crash-report URL and made no connect. The containment proof's own external connect returned network-unreachable. All six containment proofs exited 0.

## Sandbox changes

Edited on the supported host, under the staged runtime. The design was kept: outer `unshare --user --map-root-user --net --mount`, one inner bwrap, noexec writable mounts with exec submounts, allowlisting CONNECT proxy, strace, containment proofs.

- `config.json`: host tree and in-sandbox home are separate paths; the staged tree is bound at the original path inside the namespace. Quarantine is `/tmp/<account>-afc-quarantine`. Work root is under `<vegabox-home>`. Display socket for :91. `runtime_mounts` rebuilt for 24.04 and extended with the host Mesa llvmpipe closure (libGLX_mesa, libgallium, libLLVM, dri, libdrm, libgbm, and the libraries they load). Mount count 315.
- `run.py`: `allowed_worktree` retargeted to the work directory under `<vegabox-home>`. Launch prefix `aa-exec -p lxc-usernsexec`.
- `outer.py`: bind of the staged home onto the original in-sandbox path, display bind, long-run ceiling for the stage-1 script.
- Node v22.23.3, sha256 fde6a4bf8d0562f7751d1a2d6cb9b417c4cfe107bbcb0aa3e9a24e125e348f48, copied from the existing workstation binary and mounted at `/usr/bin/node`. No other software was installed.

## Frictions

- `vega virtual-device start` exits 0 when the device stays unresponsive after the deadline.
- `vvman` is absent, so the CLI falls through to `kepler --v`, which prints 0.200.0 while `vega --version` prints SDK 0.24.12112.
- A copied `hardware-qemu.ini.lock` holds a pid. In a new pid namespace the emulator treats that pid as another live instance and exits.
- Default host GPU mode SIGSEGV's when GLVND is present and the Mesa driver closure is not. It does not fall back to software.
- `--no-gl-accel` selects swiftshader_indirect. The guest surface stays black (`sPrepareTexImage2D` validation) while the skin draws. There is no CLI flag that names llvmpipe.
- "Virtual device ready" is printed while the splash is still on screen. `inputd-cli` during that window throws `Cannot read properties of undefined (reading 'trim')` and exits 253, and the device then disappears.
- `gwsi-tool-screenshooter` returns Incomplete, and copy-from writes a 0-byte file, on a frame that `xwd` shows as a full guest UI.
- Stop can exit 0 while the emulator process group dies with SIGSEGV and crashpad logs `ptrace: Operation not permitted`.
- The telemetry helper is spawned with `optIn` false. The noexec home mount makes the exec fail. The CLI still connects to the artifactory allowlist host.
- `crashpad_handler` is launched with `--url=https://clients2.google.com/cr/report`, which is outside the allowlist. This run recorded no connect from that process.
- Fontconfig, iconv/gconv, and pulse fail closed and are non-fatal. Vulkan instance creation fails; GLES through llvmpipe still paints.
- The sandbox account is not in the video or render groups. Host DRM nodes were not usable. No group change was requested.

## Time and BRAN

Agent clock start 2026-10-20T22:18:24Z. The successful run finished 2026-10-20T23:13:10Z. BRAN was not available: this worktree has no native policy file, so no BRAN check was run.

Hashes of the screenshots, status file, console excerpt, and this summary are in stage1-receipt.json.
