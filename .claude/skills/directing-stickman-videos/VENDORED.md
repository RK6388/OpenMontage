# Vendored skill: directing-stickman-videos

- Upstream: https://github.com/kaomei/stickman-video-director (path `skills/directing-stickman-videos`)
- Pinned commit: `103c96cf401f42eefb1753eb1a6ed82931af7f0c` (2026-11, "Add a concise chat style picker to the Skill (#180)")
- License: MIT (copied to `LICENSE` in this folder)
- Vendored: 2026-11-27, unmodified apart from adding this file and `LICENSE`.

## Security review done before vendoring

- Only outbound network call in the code: `scripts/gemini-media.mjs` → `generativelanguage.googleapis.com`, refused unless `--allow-network` is passed; API key read only from `GEMINI_API_KEY`, never logged.
- Spawned processes are limited to `node`, `python3`, `ffmpeg`, `ffprobe`. The two `exec(compile(...))` uses run local helpers only after a SHA-256 match; production scenes are sandboxed against subprocess launches via an audit hook.
- No install/postinstall hooks (`package.json` has only `test`, `doctor`, `test:b8`); deps are `sharp` and `@napi-rs/canvas`.
- No access to SSH keys, cloud credentials, shell rc files or Claude settings; no telemetry. The skill explicitly forbids starring/forking the repo for the user.
- No prompt-injection phrases or hidden Unicode in instruction files (the only hidden characters are in archived third-party license web pages under the upstream `docs/`, which are not vendored).
- All media files match their extensions (no disguised executables).
- `npm test`: 603/603 passing; `node scripts/autopilot.mjs doctor`: all local checks pass.

## Setup in a fresh checkout

```bash
cd .claude/skills/directing-stickman-videos
npm ci --ignore-scripts && npm rebuild sharp @napi-rs/canvas
node scripts/autopilot.mjs doctor
```

## Updating

Re-clone upstream, re-run the review above on the diff since the pinned commit, then replace this folder and update the pinned commit.
