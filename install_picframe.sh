#!/usr/bin/env bash
set -euo pipefail

# Wolfgang installer for Raspberry Pi OS Bookworm Lite
# Fork: https://github.com/UnDadFeated/picframe (dev branch)

SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
SCRIPT_NAME="install_picframe.sh"

PROGRESS_FILE="/home/pi/install_progress.txt"
LOG_FILE="/home/pi/install_log.txt"
SERVICE_NAME="install_script_service"

log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

progress_set() {
  echo "$1" > "$PROGRESS_FILE"
}

progress_get() {
  if [ -f "$PROGRESS_FILE" ]; then
    cat "$PROGRESS_FILE"
  else
    echo "0"
  fi
}

wait_for_internet() {
  log "Checking internet connectivity..."
  until ping -c 1 -W 2 1.1.1.1 >/dev/null 2>&1; do
    log "No internet yet. Retrying in 5 seconds..."
    sleep 5
  done
  log "Internet connectivity confirmed"
}

install_resume_service() {
  local svc="/etc/systemd/system/${SERVICE_NAME}.service"

  sudo tee "$svc" >/dev/null <<EOF
[Unit]
Description=Resume Wolfgang Picframe install after reboot
After=network-online.target
Wants=network-online.target

[Service]
Type=oneshot
ExecStart=${SCRIPT_PATH}
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable "${SERVICE_NAME}"
  log "Enabled installer resume service"
}

remove_resume_service() {
  local svc="/etc/systemd/system/${SERVICE_NAME}.service"
  sudo systemctl disable "${SERVICE_NAME}" >/dev/null 2>&1 || true
  sudo rm -f "$svc"
  sudo systemctl daemon-reload
  log "Removed installer resume service"
}

reboot_and_resume() {
  local step="$1"
  install_resume_service
  progress_set "$step"
  log "Rebooting now. Installer will resume at next boot."
  sudo reboot
  exit 0
}

if [ "$(basename "$SCRIPT_PATH")" != "$SCRIPT_NAME" ]; then
  log "WARNING: Expected script name ${SCRIPT_NAME}, got $(basename "$SCRIPT_PATH")"
fi
if [ "$SCRIPT_DIR" != "/home/pi/picframe" ]; then
  log "INFO: Installer running from ${SCRIPT_DIR} (expected repo root is /home/pi/picframe)"
fi

LAST_STEP=$(progress_get)
log "Starting installer from ${SCRIPT_PATH}. Last completed step: ${LAST_STEP}"

# 1) Update OS and reboot
if [ "$LAST_STEP" -lt 1 ]; then
  wait_for_internet
  log "Step 1: apt update/upgrade"
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get -y upgrade
  reboot_and_resume 1
fi

# 2) Boot to console + auto-login pi
if [ "$LAST_STEP" -lt 2 ]; then
  log "Step 2: Configure console boot"
  sudo raspi-config nonint do_boot_behaviour B2
  reboot_and_resume 2
fi

# 3) Core packages
if [ "$LAST_STEP" -lt 3 ]; then
  wait_for_internet
  log "Step 3: Install required packages"
  sudo apt-get install -y \
    git python3-venv python3-pip \
    libsdl2-dev xwayland labwc wlr-randr \
    vlc ffmpeg mosquitto mosquitto-clients

  sudo -u pi mkdir -p /home/pi/Pictures /home/pi/DeletedPictures
  progress_set 3
  log "Step 3 complete"
fi

# 4) Install picframe fork in venv
if [ "$LAST_STEP" -lt 4 ]; then
  wait_for_internet
  log "Step 4: Install Picframe fork in venv"

  sudo -u pi python3 -m venv /home/pi/venv_picframe
  sudo -u pi /home/pi/venv_picframe/bin/pip install --upgrade pip wheel
  sudo -u pi /home/pi/venv_picframe/bin/pip install paho-mqtt
  sudo -u pi /home/pi/venv_picframe/bin/pip install "git+https://github.com/UnDadFeated/picframe.git@dev"

  if [ ! -f /home/pi/picframe_data/config/configuration.yaml ]; then
    log "Initializing Picframe data/config under /home/pi"
    printf '\n\n\n' | sudo -u pi /home/pi/venv_picframe/bin/picframe -i /home/pi/ || true
  fi

  progress_set 4
  log "Step 4 complete"
fi

# 5) Configure mosquitto listener
if [ "$LAST_STEP" -lt 5 ]; then
  log "Step 5: Configure mosquitto"
  sudo mkdir -p /etc/mosquitto/conf.d
  sudo tee /etc/mosquitto/conf.d/picframe.conf >/dev/null <<EOF
allow_anonymous true
listener 1883 0.0.0.0
EOF
  sudo systemctl restart mosquitto
  sudo systemctl enable mosquitto
  progress_set 5
  log "Step 5 complete"
fi

# 6) Create start script + labwc autostart
if [ "$LAST_STEP" -lt 6 ]; then
  log "Step 6: Configure labwc autostart"

  sudo -u pi tee /home/pi/start_picframe.sh >/dev/null <<'EOF'
#!/bin/bash
exec >> /home/pi/picframe_data/logs/picframe_user_start.log 2>&1
echo "=== $(date '+%Y-%m-%d %H:%M:%S') start_picframe ==="
export XDG_RUNTIME_DIR=/run/user/1000
export WAYLAND_DISPLAY=wayland-0
mkdir -p /run/user/1000
sleep 2
if pgrep -f '/home/pi/venv_picframe/bin/picframe' >/dev/null 2>&1; then
  echo "picframe already running"
  exit 0
fi
exec /usr/bin/flock -n /tmp/picframe.lock /home/pi/venv_picframe/bin/picframe
EOF
  sudo chmod +x /home/pi/start_picframe.sh

  sudo -u pi mkdir -p /home/pi/.config/labwc
  sudo -u pi tee /home/pi/.config/labwc/autostart >/dev/null <<'EOF'
/home/pi/start_picframe.sh
EOF

  sudo -u pi tee /home/pi/.config/labwc/rc.xml >/dev/null <<'EOF'
<windowRules>
  <windowRule identifier="*" serverDecoration="no" />
</windowRules>
EOF

  progress_set 6
  log "Step 6 complete"
fi

# 7) Create user service to start labwc on boot
if [ "$LAST_STEP" -lt 7 ]; then
  log "Step 7: Configure user systemd service"
  sudo -u pi mkdir -p /home/pi/.config/systemd/user
  sudo -u pi tee /home/pi/.config/systemd/user/picframe.service >/dev/null <<'EOF'
[Unit]
Description=Picframe labwc session
After=graphical-session-pre.target

[Service]
ExecStart=/usr/bin/labwc
Restart=always

[Install]
WantedBy=default.target
EOF

  sudo -u pi systemctl --user daemon-reload || true
  sudo -u pi systemctl --user enable picframe.service || true

  # Ensure user service starts at boot even when user isn't logged in
  sudo loginctl enable-linger pi || true

  reboot_and_resume 7
fi

remove_resume_service
progress_set 99
log "Installation completed successfully"
exit 0
