# Picframe v1.2.2 — Digital picture frame for Raspberry Pi

A feature-rich digital picture frame application for Raspberry Pi using pi3d, with video support, smart caching, MQTT integration, auto-update, and a modern web interface.

## Highlights

### Terminal Configuration TUI (`pfconfig`)
- Reorganized with dedicated **Photos**, **Videos**, and **Database Management** submenus
- 18 intuitive workflow groups for fast scanning
- Intuitive choice selectors - see actual option names instead of numbers
- Choice selectors with `< Left/Right >`, plus per-setting `[R]` revert
- Run locally using: `./pfconfig.sh` or remotely via `ssh pi@192.168.4.110 "python3 /home/pi/picframe/src/picframe/pfconfig.py"`

### Auto-Update & Deployment
- Configure automatic updates on startup from your GitHub fork
- Works with pip-installed versions (no local git repo needed)
- Enable via `pfconfig` menu: `Updates` → `Auto Update On Start`
- Point to your fork's branch and URL for seamless updates
- Use `tmp/deploy_picframe.sh` for one-click local-to-Pi deployment
- Use `tmp/update_picframe.sh` for remote-only updates (runs on Pi)

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

## Release v1.2.2

- **Configuration Reorganization**: Moved `configuration.yaml` from `~/picframe_data/config/` to `~/picframe_src/picframe/config/` directory
- **Version bumped to 1.2.2**

Refer to the Git history for the full set of changes.

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

## Installation

### Prerequisites

- **Hardware**: Raspberry Pi 3, 4, or 5
- **OS**: Raspberry Pi OS Bookworm Lite (64-bit recommended)
- **Network**: Internet access for initial setup
- **Access**: SSH access as the `pi` user

### One-Step Install (Recommended)

Run this entire block as a single command via SSH into your Pi:

```bash
curl -sSL https://raw.githubusercontent.com/UnDadFeated/picframe/main/install_picframe.sh | bash -s -- --yes
```

**What the installer does:**
1. Installs system dependencies (Python, ffmpeg, VLC, labwc, rclone)
2. Sets up a Python virtual environment at `/home/pi/picframe/venv`
3. Installs Picframe from your fork's main branch
4. Creates configuration directory structure (`~/picframe_data/`)
5. Sets up labwc compositor autostart
6. Creates the startup script (`/home/pi/start_picframe.sh`)

> ⚠️ **Reboot Required**: After installation completes, reboot your Pi:
> ```bash
> sudo reboot
> ```

### Post-Install Configuration

After reboot, configure Picframe:

1. **Edit the configuration file**:
   ```bash
   nano ~/picframe_data/config/configuration.yaml
   ```
   Or use the TUI:
   ```bash
   cd /home/pi/picframe
   ./pfconfig.sh
   ```

2. **Set your media directory** in `model.pic_dir` (e.g., `/mnt/nas` for NAS-mounted photos/videos)

3. **Start Picframe**:
   ```bash
   /home/pi/start_picframe.sh
   ```

4. **Access the Web UI** at `http://<pi-ip>:9000`

### Google Photos via rclone (Optional)

For mounting Google Photos as a local directory:

```bash
# Install and configure rclone
sudo apt-get install -y rclone
rclone config  # Create a Google Photos remote

# Create mount point and mount
sudo mkdir -p /mnt/gphotos
sudo chown pi:pi /mnt/gphotos
rclone mount "gphotos:media/by-day" /mnt/gphotos --vfs-cache-mode full --dir-cache-time 72h &

# In pfconfig, set Media Root Folder to /mnt/gphotos
```

---

## Configuration

### Key Settings (in `~/picframe_data/config/configuration.yaml`)

```yaml
viewer:
  # Smart cache (requires YYYY-MM-DD_ filename prefix!)
  date_range_days: 15                      # +/- days from today
  enable_date_filter: True                  # enable date filtering
  enable_smart_cache: True                  # only cache files in date window
  cache_refresh_timezone: "America/Los_Angeles"  # your timezone

  # Display
  fit: False                                # False = crop to fill, True = show all
  display_power: 2                          # 0=vcgencmd, 1=xset, 2=wlr-randr
  use_sdl2: True                            # use SDL2 (recommended for Pi)

  # Video ratio (X/Y randomized)
  video_ratio_enabled: True
  video_ratio_videos: 1
  video_ratio_total: 10
  video_quarantine_days: 330
  video_volume: 0
  video_fit_display: True
  video_progress_show: True
  video_play_immediately: True

  # Photo cooldown
  photo_quarantine_days: 330

  # Web interface
  show_cache_indicator: True
  cache_progress_x_offset: 80

model:
  pic_dir: "/mnt/nas"                      # your photo/video folder (NAS mount)
  subdirectory: ""
  autorun_enabled: True

http:
  use_http: True
  port: 9000
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
- Delete `.db3` files and restart:
  ```bash
  rm -f ~/picframe_data/data/*.db3
  /home/pi/start_picframe.sh
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