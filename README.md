# Picframe v1.2.0 — Digital picture frame for Raspberry Pi

A feature-rich digital picture frame application for Raspberry Pi using pi3d, with video support, smart caching, MQTT integration, auto-update, and a modern web interface.

## Highlights

### Terminal Configuration TUI (`pfconfig`)
- Reorganized with dedicated **Photos**, **Videos**, and **Database Management** submenus
- 18 intuitive workflow groups for fast scanning
- Intuitive choice selectors - see actual option names instead of numbers
- Choice selectors with `< Left/Right >`, plus per-setting `[R]` revert
- Run locally using: `./pfconfig.sh`

### Auto-Update
- Configure automatic updates on startup from your GitHub fork
- Works with pip-installed versions (no local git repo needed)
- Enable via `pfconfig` menu: `Updates` → `Auto Update On Start`
- Point to your fork's branch and URL for seamless updates

### Playback & Caching
- Photo + video support with AV1 playback
- **Video ratio control** (`video_ratio_videos`/`video_ratio_total`) - randomized X/Y ratio, e.g., 1/10 = 1 video per 10 media items
- **Photo cooldown** (`photo_quarantine_days`) - fixed days before a photo can be shown again (default 330 days)
- **Video cooldown** (`video_quarantine_days`) - fixed days before a video can be shown again (default 330 days)
- Year-agnostic smart cache window (`YYYY-MM-DD_` naming)
- Automatic timezone-aware midnight refresh without restart

### Display, Web, and Reliability
- Multi-mode display power control with readable names: `vcgencmd (Raspberry Pi)`, `xset (X11)`, `wlr-randr (Wayland)`
- Secondary HDMI output selection support
- Web UI controls with live cache progress and preview
- Idempotent DB schema updates and bad-file tracking database
- Reusable HTTP server binding to reduce restart port conflicts
- MQTT integration with Home Assistant

---

## Release v1.2.0

- Updated install_picframe.sh with 5-second mount delay and RequiresMountsFor support
- Created deploy_picframe.sh and update_picframe.sh for streamlined deployment
- Improved .gitignore to exclude sensitive files and local config
- Version bumped to 1.2.0

Refer to the `CHANGELOG.md` or Git history for the full set of changes.


## Important: Smart Cache Filename Requirement

> **Smart cache requires media files to be named with `YYYY-MM-DD_` prefix!**
> 
> When `enable_smart_cache: True` is enabled in your configuration, only files matching the pattern `YYYY-MM-DD_*.jpg`, `YYYY-MM-DD_*.mp4`, etc. will be added to the database. Files without this prefix are skipped during the cache build.
> 
> This is intentional for seasonal/curated media management - files from past years (e.g., `2009-04-15_vacation.jpg`) will match the current date window (±15 days by default) across any year, allowing you to display content from previous years without storing all files in the database.
> 
> Example valid filenames:
> - `2024-12-25_christmas.jpg`
> - `2009-04-15_easter_egg_hunt.mp4`
> - `2025-01-01_new_year.jpg`

---

## Features

- **Photo & Video Support** - JPEG, PNG, HEIC, and videos (MP4, MKV, MOV, AV1, WebM)
- **Smart Caching** - Year-agnostic date filtering with automatic midnight refresh
- **Modern Web UI** - Dark-themed control panel at `http://<pi-ip>:9000`
- **Automatic Refresh** - Midnight timezone-aware cache refresh without restart
- **EXIF Orientation** - Automatic rotation handling for photos and videos
- **Display Power Control** - Supports HDMI off/on via wlr-randr, xset, or vcgencmd
- **MQTT Support** - Remote control integration for Home Assistant

---

## Installation

### Option 1: One-Click Install (Recommended for Raspberry Pi OS Bookworm Lite)

```bash
# SSH into your Pi as 'pi'
sudo apt-get update && sudo apt-get install -y git

# Clone and run installer (uses main branch from your fork)
cd /home/pi
git clone -b main https://github.com/UnDadFeated/picframe.git
cd picframe
chmod +x install_picframe.sh
./install_picframe.sh
```

The installer will:
1. Install system dependencies (Python, ffmpeg, VLC, labwc)
2. Set up Python virtual environment
3. Install Picframe from this fork
4. Configure mosquitto (optional MQTT)
5. Set up labwc compositor autostart
6. Create startup service

**After install:**
- Start manually: `/home/pi/start_picframe.sh`
- Auto-start on reboot is configured via labwc autostart

### Option 2: Manual Install

```bash
# Install dependencies
sudo apt-get update
sudo apt-get install -y python3-venv python3-pip ffmpeg vlc libatlas-base-dev libopenjp2-7 libpng16-16 libjpeg-dev libavcodec-extra

# Clone repository (main branch from your fork)
git clone -b main https://github.com/UnDadFeated/picframe.git
cd picframe

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install package
pip install .

# Copy and edit configuration
cp src/picframe/config/configuration_example.yaml ~/picframe_data/config/configuration.yaml
nano ~/picframe_data/config/configuration.yaml
```

### Google Photos via rclone (with `pfconfig`)

Use this flow to mount Google Photos and point Picframe at it using the TUI menu.

1. Install and configure rclone on the Pi:

```bash
sudo apt-get update
sudo apt-get install -y rclone
rclone config
```

In `rclone config`, create a remote (example name: `gphotos`) using the Google Photos backend and complete browser auth.

2. Create a local mount point and test access:

```bash
sudo mkdir -p /mnt/gphotos
sudo chown pi:pi /mnt/gphotos
rclone ls "gphotos:media/by-day" | head
```

3. Mount Google Photos (foreground test):

```bash
rclone mount "gphotos:media/by-day" /mnt/gphotos --vfs-cache-mode full --dir-cache-time 72h --poll-interval 15m
```

4. Open `pfconfig` and set paths from the menu:

```bash
cd /home/pi/picframe
./pfconfig.sh
```

In `pfconfig`:
- Go to `Directories & Filters`
- Set `Media Root Folder` (`model.pic_dir`) to `/mnt/gphotos`
- Optionally set `Subdirectory Filter` (`model.subdirectory`) if you want a subset
- Save with `S`

5. Start Picframe:

```bash
/home/pi/start_picframe.sh
```

Notes:
- Keep smart-cache naming in mind (`YYYY-MM-DD_...`) if `enable_smart_cache` is enabled.
- For always-on mounts after reboot, create an rclone systemd mount service for `/mnt/gphotos`.

---

## Configuration


Edit `~/picframe_data/config/configuration.yaml`:

### Key Settings

```yaml
viewer:
  # Smart cache (requires YYYY-MM-DD_ filename prefix!)
  date_range_days: 15                      # +/- days from today
  enable_date_filter: True                  # enable date filtering
  enable_smart_cache: True                  # only cache files in date window
  cache_refresh_timezone: "America/Los_Angeles"  # your timezone

  # Display
  fit: False                                # False = crop to fill, True = show all
  display_power: 2                         # 0=vcgencmd, 1=xset, 2=wlr-randr
  use_sdl2: True                            # use SDL2 (recommended for Pi)
  
  # Video ratio (X/Y randomized)
  video_ratio_enabled: True              # enable randomized video/photo ratio
  video_ratio_videos: 1                  # X videos per Y total (e.g., 1 = 1 video per total)
  video_ratio_total: 10                  # Y total media denominator
  video_quarantine_days: 330          # fixed cooldown days before video eligible again
  video_volume: 0                    # 0 = muted, 100 = full volume
  video_fit_display: True              # True = stretch to fit
  video_progress_show: True          # show video duration countdown
  video_play_immediately: True        # start video when fade-in completes

  # Photo cooldown
  photo_quarantine_days: 330            # fixed cooldown days before photo eligible again
  
  # Web interface
  show_cache_indicator: True               # show cache building progress
  cache_progress_x_offset: 80              # adjust position as needed
  
model:
  pic_dir: "/mnt/nas"                      # your photo/video folder (NAS mount)
  subdirectory: ""                          # subfolder if needed
  
  # Auto-update / Auto-run
  autorun_enabled: True                  # enable auto-start on login

http:
  use_http: True
  port: 9000                               # web UI port
  path: "~/picframe_data/html"
```

### Date Range / Smart Cache

- **date_range_days**: How many days back/forward from today to include
- **Year-agnostic**: A file dated `2009-04-15` will show in the frame during April 2026 if within the ±15 day window
- **Midnight refresh**: At local midnight (based on `cache_refresh_timezone`), the cache automatically purges files outside the new date window and picks up any newly eligible files - no restart needed

---

## Usage

### Start Picframe
```bash
/home/pi/start_picframe.sh
```

### Web Control Panel
Open `http://<raspberry-pi-ip>:9000` in your browser.

Features:
- Play/Pause, Next/Back, Shuffle toggle
- Time delay, fade time, brightness sliders
- Date filter controls
- Current image preview
- Cache progress indicator

### Keyboard Controls (if configured)
- Space: Pause/Resume
- O: Toggle display off/on

---

## Troubleshooting

**No images showing:**
- Check database was built: look for `/home/pi/picframe_data/data/pictureframe.db3`
- Ensure filenames have `YYYY-MM-DD_` prefix when smart cache is enabled
- Check logs: `~/picframe_data/logs/`

**Display stays blank:**
- Try `display_power: 2` for wlr-randr mode
- Check `use_sdl2: True` is set

**Cache not building:**
- Delete `.db3` files and restart to rebuild:
  ```bash
  rm -f ~/picframe_data/data/*.db3
  ~/pi/start_picframe.sh
  ```

**HTTP UI not loading:**
- Verify `use_http: True` in config
- Check port 9000 isn't in use: `sudo lsof -i :9000`

---

## License

MIT License - same as upstream [helgeerbe/picframe](https://github.com/helgeerbe/picframe)

---

## Links

The canonical GitHub repository name is **`picframe`** (for example `UnDadFeated/picframe`).

- Original project: https://github.com/helgeerbe/picframe
- This fork: https://github.com/UnDadFeated/picframe
- Installation reference: https://www.thedigitalpictureframe.com/install-the-pi3d-pictureframe-software-with-one-click-2025-edition-raspberry-pi-2-3-4-5/
