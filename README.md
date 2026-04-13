## Picframe Fork (based on helgeerbe/picframe)

This repository is a practical fork of the original Picframe project, tuned for a real-world home frame setup.

- Upstream project: https://github.com/helgeerbe/picframe
- Fork maintainer: https://github.com/UnDadFeated/picframe
- License: MIT (same as upstream)

## What this fork changes

Compared to the original upstream `main` branch, this fork adds reliability improvements, display/power handling updates, better control behavior, deployment-focused configuration defaults, and modernized web control UI.

### 1) Display and power control improvements

- Added support for selecting and handling a second HDMI output.
- Improved display on/off control logic.
- Added support for checking display connection state via DRM sysfs (`/sys/class/drm/card0-HDMI-A-1/status`) when using display power mode 3.

### 2) Input and control interface updates

- Improved touch and mouse handling behavior.
- Added configurable menu fade timing in the HTML control interface.
- Added a boolean control variable in the web UI logic for cleaner control state handling.

### 3) Video playback and media flow fixes

- Multiple fixes for video playback edge cases and badly behaved video files.
- Additional fixes around video player/streamer behavior for smoother playback.
- Cache loading flow improvements to better support seasonal/curated media sets.

### 4) Metadata and geo lookup reliability

- Geo reverse lookup fixes and robustness updates.
- Added required `User-Agent` for Nominatim requests.
- Added minimum retry time handling for Nominatim requests to reduce request failures.

### 5) Viewer and runtime stability

- Fixes in controller/model/viewer flow to improve runtime consistency.
- Thread naming cleanup and related reliability fixes.
- General maintenance improvements across startup and peripheral handling code.

### 6) Configuration defaults aligned to deployed setup

- Updated `configuration_example.yaml` to reflect this fork's actively deployed/default setup.

### 7) Cache database and bad file handling

- Added idempotent schema migration handling in `image_cache.py` to avoid startup failures on existing or partially migrated SQLite databases.
- Added dedicated bad-file tracking database support (`bad_files_db`) for persistently recording unreadable/corrupt files.
- Added skip logic so files already known to be bad can be ignored during future scans, improving cache refresh performance.
- Added `bad_files_db` configuration entry to model defaults and deployment config.

### 8) HTTP and startup resilience

- Added reusable HTTP server binding (`allow_reuse_address = True`) to reduce restart-time port binding issues.
- Added startup script hardening for user-session launch behavior under Wayland/labwc.
- Preserved stable operation on port `9000` after prior conflict troubleshooting.

### 9) Web control interface redesign

- Rebuilt the control page (`src/picframe/html/index.html`) with a modern wireframe-inspired layout.
- Reworked UI styles and interaction behavior in `src/picframe/html/pf_functions.js`.
- Added theme toggling with dark mode as default and persisted theme preference.
- Improved responsive layout and control readability for desktop and mobile browsers.

## Files with fork-vs-upstream differences

Compared to upstream `origin/main`, this fork currently differs in these core files:

- `pyproject.toml`
- `src/picframe/config/configuration_example.yaml`
- `src/picframe/controller.py`
- `src/picframe/geo_reverse.py`
- `src/picframe/html/index.html`
- `src/picframe/html/pf_functions.js`
- `src/picframe/image_cache.py`
- `src/picframe/interface_http.py`
- `src/picframe/interface_peripherals.py`
- `src/picframe/model.py`
- `src/picframe/start.py`
- `src/picframe/video_player.py`
- `src/picframe/video_streamer.py`
- `src/picframe/viewer_display.py`

## Quick start

Use upstream installation/documentation as your base reference, then apply this fork for the behavior improvements listed above:

- Upstream wiki: https://github.com/helgeerbe/picframe/wiki

If you are running this fork directly, start with:

- `src/picframe/config/configuration_example.yaml`
- your existing `configuration.yaml` deployment values

## Bookworm Lite install (Wolfgang-based script)

This fork includes an end-to-end installer script for Raspberry Pi OS Bookworm Lite.

Original source reference (base script/workflow inspiration):

- https://www.thedigitalpictureframe.com/install-the-pi3d-pictureframe-software-with-one-click-2025-edition-raspberry-pi-2-3-4-5/

Install script fixes and changes in this fork (relative to the original workflow):

- Converted to a strict, resumable Bash flow with `set -euo pipefail` and explicit step progress tracking.
- Added robust internet checks before package and pip operations.
- Added systemd resume service logic (`install_script_service`) to continue after reboots and remove itself on completion.
- Switched package install to include Bookworm/labwc runtime dependencies (`xwayland`, `labwc`, `wlr-randr`, `vlc`, `ffmpeg`, `python3-venv`).
- Updated pip install target to this fork directly (`git+https://github.com/UnDadFeated/picframe.git@dev`).
- Added idempotent creation of Picframe runtime folders and safer first-run initialization behavior.
- Added explicit mosquitto config drop-in (`/etc/mosquitto/conf.d/picframe.conf`) and service enable/restart.
- Replaced simple launch command with hardened `/home/pi/start_picframe.sh` (Wayland env, lock file, timestamped logging, duplicate-process guard).
- Added labwc autostart and minimal `rc.xml` creation for fullscreen frame operation.
- Added user-level `picframe.service` + `loginctl enable-linger pi` to keep startup behavior consistent across reboots.

Fork adaptation details:

- Script path: `scripts/install_picframe.sh`
- Target branch: `dev`
- It installs dependencies, sets up a venv, installs this fork, configures mosquitto, and configures labwc autostart.

### Recommended base image

- Raspberry Pi OS Lite (64-bit), Bookworm
- Username: `pi`
- Network online before running installer

### Run installer

On the Pi:

```bash
sudo apt-get update && sudo apt-get install -y git
cd /home/pi
git clone -b dev https://github.com/UnDadFeated/picframe.git
cd picframe
chmod +x scripts/install_picframe.sh
./scripts/install_picframe.sh
```

The installer is reboot-resumable and logs progress to:

- `/home/pi/install_progress.txt`
- `/home/pi/install_log.txt`

After completion, Picframe is started via:

- `/home/pi/start_picframe.sh`
- labwc autostart: `/home/pi/.config/labwc/autostart`

## Notes

- Smart cache/date-window mode in this fork requires media filenames to begin with a `YYYY-MM-DD_` prefix for files to be loaded into the Picframe database. This applies to both images and videos when that filtering mode is enabled.

This fork is focused on practical day-to-day operation on a Raspberry Pi picture frame (display control, input handling, and playback reliability), while staying close to upstream structure.