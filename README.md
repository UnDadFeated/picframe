# Picframe - Digital Picture Frame for Raspberry Pi

A feature-rich digital picture frame application for Raspberry Pi using pi3d, with video support, smart caching, and a modern web interface.

## Fork Changes / What's New

This fork includes the following improvements over the original [helgeerbe/picframe](https://github.com/helgeerbe/picframe):

### Terminal Configuration TUI (`pfconfig`)
- **Alphabetized Navigation**: Main categories and each submenu are organized alphabetically for faster scanning.
- **Intuitive Grouping**: Settings are grouped by workflow (`Display & Rendering`, `UI Overlays`, `Slideshow Timing`, `Caching & Date Filtering`, etc.).
- **Supported Settings Only**: Removed unsupported AI/cloud/sound entries from TUI menus and aligned visible options to active runtime config keys.
- **Updated Controls**: Added newer keys such as `viewer.video_every_n_photos`, text absolute positioning (`text_position_mode`, `text_x_position`, `text_y_position`), and `viewer.display_hdmi`.
- **Choice Selectors**: Uses `< Left/Right >` arrow keys for enum-style options instead of manual typing.
- **Safety Features**: Includes `[R] Revert` per option and preserves inline YAML comments when saving.
- **Run locally using**: `./pfconfig.sh`

### Display & Power Control
- Support for secondary HDMI output selection
- Improved display on/off control logic (DRM sysfs checking for mode 3)
- Display power modes: 0=vcgencmd, 1=xset, 2=wlr-randr

### Video Playback
- AV1 codec support (libdav1d + libaom-av1)
- Multiple fixes for video edge cases and badly behaved files
- Better player/streamer behavior for smoother playback
- Cache loading flow improvements for seasonal media sets

### Smart Caching & Playback
- Year-agnostic date filtering with `YYYY-MM-DD_` filename prefix
- Automatic midnight refresh (timezone-aware) without restart
- Purges out-of-window files and picks up new files at local midnight
- Configurable date window (±15 days default)
- **Anniversary Playback Cooldown**: Prevents photos from repeating endlessly within a calendar year. Once a photo plays, it faces an ~11-month cooldown so it only returns next year during its specific anniversary window.

### Metadata & Geo
- Geo reverse lookup fixes with User-Agent for Nominatim
- Retry handling to reduce request failures
- EXIF orientation handling for both photos and videos

### Database & Cache
- Idempotent schema migration (avoids startup failures)
- Dedicated bad-file tracking database (`bad_files_db`)
- Skip logic for known-bad files during cache refresh

### HTTP / Web UI
- Modern dark-themed web interface at port 9000
- Toggle controls for pause/display/shuffle
- Live cache progress bar
- Current image thumbnail preview
- Auto-refresh every 5 seconds

### Installation
- One-click install script for Raspberry Pi OS Bookworm Lite
- Hardened startup script with duplicate-process guard
- labwc compositor autostart configuration
- Reboot-resumable installer with progress logging

### HTTP Server
- Reusable HTTP server binding (`allow_reuse_address = True`)
- Reduced port binding issues on restart

---

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

# Clone and run installer
cd /home/pi
git clone -b dev https://github.com/UnDadFeated/picframe.git
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

# Clone repository
git clone -b dev https://github.com/UnDadFeated/picframe.git
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
  
  # Video
  video_every_n_photos: 10                # if videos exist, force at least 1 video every N photos
  video_volume: 0                          # 0 = muted, 100 = full volume
  video_fit_display: True                  # True = stretch to fit
  
  # Web interface
  show_cache_indicator: True               # show cache building progress
  cache_progress_x_offset: 80              # adjust position as needed
  
model:
  pic_dir: "/mnt/nas"                      # your photo/video folder (NAS mount)
  subdirectory: ""                          # subfolder if needed
  
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

- Original project: https://github.com/helgeerbe/picframe
- This fork: https://github.com/UnDadFeated/picframe
- Installation reference: https://www.thedigitalpictureframe.com/install-the-pi3d-pictureframe-software-with-one-click-2025-edition-raspberry-pi-2-3-4-5/
