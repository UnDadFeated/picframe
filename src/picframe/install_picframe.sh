nd i#!/bin/bash
# =============================================================================
# Picframe One-Click Installer for Raspberry Pi OS Bookworm Lite
# =============================================================================
# This script automates the installation of Picframe on a Raspberry Pi.
# It is resilient to reboots: if interrupted, it resumes from the last step.
#
# Usage (on the Pi, as user 'pi'):
#   git clone -b main https://github.com/UnDadFeated/picframe.git
#   cd picframe
#   chmod +x install_picframe.sh
#   ./install_picframe.sh
# =============================================================================

# Path to store progress and log file
PROGRESS_FILE="/home/pi/.picframe_install_progress"
LOG_FILE="/home/pi/.picframe_install_log.txt"
SERVICE_NAME="picframe_install_resume"

# Picframe source URL (change to your fork)
PICFRAME_REPO_URL="https://github.com/UnDadFeated/picframe.git"
PICFRAME_REPO_BRANCH="main"

# ============================================================
# Helper functions
# ============================================================

log_message() {
    local msg="[$(date '+%Y-%m-%d %H:%M:%S')] $1"
    echo "$msg" | tee -a "$LOG_FILE"
}

update_progress() {
    echo "$1" > "$PROGRESS_FILE"
}

get_last_completed_step() {
    if [ -f "$PROGRESS_FILE" ]; then
        cat "$PROGRESS_FILE"
    else
        echo "0"
    fi
}

# ============================================================
# Reboot / systemd helpers
# ============================================================

add_systemd_service() {
    local script_path
    script_path="$(cd "$(dirname "$0")" && pwd)/$(basename "$0")"
    local service_file="/etc/systemd/system/${SERVICE_NAME}.service"

    cat > "$service_file" <<EOF
[Unit]
Description=Resume Picframe install script after reboot
After=network-online.target

[Service]
Type=oneshot
ExecStart=${script_path}
StandardOutput=append:${LOG_FILE}
StandardError=append:${LOG_FILE}

[Install]
WantedBy=multi-user.target
EOF
    sudo systemctl daemon-reload
    sudo systemctl enable "${SERVICE_NAME}"
    log_message "Added systemd service to resume install after reboot."
}

remove_systemd_service() {
    sudo systemctl disable "${SERVICE_NAME}" 2>/dev/null
    sudo systemctl stop "${SERVICE_NAME}" 2>/dev/null
    sudo rm -f "/etc/systemd/system/${SERVICE_NAME}.service"
    sudo systemctl daemon-reload 2>/dev/null
    log_message "Removed install resume systemd service."
}

needs_reboot() {
    update_progress "$1"
    log_message "Rebooting to complete step ${1}. The script will resume after reboot."
    add_systemd_service
    sudo reboot
}

# ============================================================
# Internet check
# ============================================================

check_internet_connection() {
    log_message "Checking for an active internet connection..."
    local attempts=0
    while ! ping -c 1 -W 2 google.com &>/dev/null; do
        attempts=$((attempts + 1))
        if [ "$attempts" -ge 60 ]; then
            log_message "ERROR: No internet connection after ~5 minutes. Aborting."
            exit 1
        fi
        sleep 5
    done
    log_message "Internet connection confirmed."
}

# ============================================================
# Ensure passwordless sudo for picframe-specific commands
# ============================================================

configure_sudoers() {
    local sudoers_entry="pi ALL=(ALL) NOPASSWD: /home/pi/venv_picframe/bin/picframe, /home/pi/venv_picframe/bin/pip, /usr/bin/python3, /bin/mkdir"
    if ! sudo grep -qF "$sudoers_entry" /etc/sudoers 2>/dev/null; then
        echo "$sudoers_entry" | sudo tee -a /etc/sudoers >/dev/null
        log_message "Configured passwordless sudo for the 'pi' user."
    fi
}

# ============================================================
# MAIN INSTALL LOGIC
# ============================================================

# Get the last completed step
LAST_COMPLETED_STEP=$(get_last_completed_step)

# ---------- Step 1: Update the operating system ----------
if [ "$LAST_COMPLETED_STEP" -lt 1 ]; then
    check_internet_connection
    log_message "=== Step 1: Updating operating system ==="
    sudo apt-get update
    sudo apt-get upgrade -y
    needs_reboot 1
fi

# ---------- Step 2: Boot behavior (console boot) ----------
if [ "$LAST_COMPLETED_STEP" -lt 2 ]; then
    log_message "=== Step 2: Setting console boot mode ==="
    sudo raspi-config nonint do_boot_behaviour B2
    needs_reboot 2
fi

# ---------- Step 3: Samba sharing ----------
if [ "$LAST_COMPLETED_STEP" -lt 3 ]; then
    check_internet_connection
    log_message "=== Step 3: Installing Samba and configuring ==="
    sudo apt-get install samba -y

    if ! command -v expect &>/dev/null; then
        sudo apt-get install -y expect
    fi

    # Set Samba password for 'pi' (only if not already set)
    if ! sudo pdbedit -L 2>/dev/null | grep -q "^pi:"; then
        expect <<'EXPEOF'
spawn sudo smbpasswd -a pi
expect "New SMB password:"
send "pi\r"
expect "Retype SMB password:"
send "pi\r"
expect eof
EXPEOF
    fi

    # Write Samba config
    cat > /etc/samba/smb.conf <<'EOF'
[global]
   security = user
   workgroup = WORKGROUP
   server role = standalone server
   map to guest = never
   encrypt passwords = yes
   obey pam restrictions = no
   client min protocol = SMB2
   client max protocol = SMB3

   vfs objects = catia fruit streams_xattr
   fruit:metadata = stream
   fruit:model = RackMac
   fruit:posix_rename = yes
   fruit:veto_appledouble = no
   fruit:wipe_intentionally_left_blank_rfork = yes
   fruit:delete_empty_adfiles = yes

[picframe-pi]
   comment = Picframe Pi Directories
   browseable = yes
   path = /home/pi
   read only = no
   create mask = 0775
   directory mask = 0775
   force user = pi
EOF

    sudo systemctl restart smbd
    update_progress 3
    log_message "Samba installation and configuration completed."
fi

# ---------- Step 4: Install system packages ----------
if [ "$LAST_COMPLETED_STEP" -lt 4 ]; then
    check_internet_connection
    log_message "=== Step 4: Installing system packages ==="
    sudo apt-get install -y \
        git libsdl2-dev xwayland labwc wlr-randr vlc ffmpeg \
        mosquitto mosquitto-clients

    # Create media directories
    mkdir -p /home/pi/Pictures /home/pi/DeletedPictures
    log_message "Directories 'Pictures' and 'DeletedPictures' created."
    needs_reboot 4
fi

# ---------- Step 5: Install picframe (from this fork) ----------
if [ "$LAST_COMPLETED_STEP" -lt 5 ]; then
    check_internet_connection
    log_message "=== Step 5: Installing picframe ==="

    # Clone the repo if not already done
    if [ ! -d "/home/pi/picframe/.git" ]; then
        log_message "Cloning picframe repository..."
        git clone -b "${PICFRAME_REPO_BRANCH}" "${PICFRAME_REPO_URL}" /home/pi/picframe
    fi

    # Create / reuse virtual environment
    if [ ! -d "/home/pi/venv_picframe" ]; then
        python3 -m venv /home/pi/venv_picframe
    fi

    # Activate and install dependencies
    log_message "Installing picframe in virtual environment..."
    /home/pi/venv_picframe/bin/pip install --upgrade pip
    /home/pi/venv_picframe/bin/pip install paho-mqtt

    # Install picframe from local source (editable install)
    log_message "Installing picframe from local source..."
    cd /home/pi/picframe
    /home/pi/venv_picframe/bin/pip install -e .

    log_message "Picframe installed successfully."
    update_progress 5
fi

# ---------- Step 6: Configure Mosquitto ----------
if [ "$LAST_COMPLETED_STEP" -lt 6 ]; then
    log_message "=== Step 6: Configuring Mosquitto MQTT ==="
    mosquitto_conf="/etc/mosquitto/mosquitto.conf"

    # Add anonymous config if not already present
    if ! grep -q "allow_anonymous" "$mosquitto_conf" 2>/dev/null; then
        echo "allow_anonymous true" | sudo tee -a "$mosquitto_conf" >/dev/null
    fi
    if ! grep -q "listener" "$mosquitto_conf" 2>/dev/null; then
        echo "listener 1883 0.0.0.0" | sudo tee -a "$mosquitto_conf" >/dev/null
    fi

    sudo systemctl restart mosquitto
    log_message "Mosquitto configured and restarted."
    update_progress 6
fi

# ---------- Step 7: Create autostart script ----------
if [ "$LAST_COMPLETED_STEP" -lt 7 ]; then
    log_message "=== Step 7: Creating autostart script ==="

    cat > /home/pi/start_picframe.sh <<'EOF'
#!/bin/bash
# Wait for NAS/network to be ready (5 second delay)
sleep 5
# Activate Picframe virtual environment and start the frame
source /home/pi/venv_picframe/bin/activate
cd /home/pi/picframe
picframe
EOF
    chmod +x /home/pi/start_picframe.sh
    log_message "Autostart script created with 5-second mount delay: /home/pi/start_picframe.sh"
    update_progress 7
fi

# ---------- Step 8: Configure labwc autostart & systemd ----------
if [ "$LAST_COMPLETED_STEP" -lt 8 ]; then
    log_message "=== Step 8: Configuring labwc autostart ==="

    # labwc autostart (with 5-second delay for NAS mount)
    mkdir -p /home/pi/.config/labwc
    cat > /home/pi/.config/labwc/autostart <<'EOF'
# Wait for NAS to be mounted before starting picframe
exec bash -c 'sleep 5 && /home/pi/start_picframe.sh'
EOF

    # labwc rc.xml — remove window decorations for picframe
    cat > /home/pi/.config/labwc/rc.xml <<'EOF'
<windowRules>
    <windowRule identifier="*" serverDecoration="no" />
</windowRules>
EOF

    # systemd user service for labwc
    mkdir -p /home/pi/.config/systemd/user
    cat > /home/pi/.config/systemd/user/picframe.service <<'EOF'
[Unit]
Description=PictureFrame on Pi
After=graphical.target

[Service]
ExecStart=/usr/bin/labwc
Restart=always
RestartSec=5

[Install]
WantedBy=default.target
EOF

    # Enable the user service
    systemctl --user daemon-reload
    systemctl --user enable picframe.service

    log_message "Labwc autostart and systemd service configured."
    needs_reboot 8
fi

# ---------- Step 9: Create system-level picframe.service with boot delay ----------
if [ "$LAST_COMPLETED_STEP" -lt 9 ]; then
    log_message "== Step 9: Creating system-level picframe.service with 5-second boot delay ==="

    SYSTEM_SERVICE_FILE="/etc/systemd/system/picframe.service"

    cat > "$SYSTEM_SERVICE_FILE" <<'EOF'
[Unit]
Description=Picframe slideshow
After=network-online.target local-fs.target
Wants=network-online.target
# Wait for NAS mount point
RequiresMountsFor=/mnt/nas

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/home/pi
Restart=on-failure
RestartSec=5
# 5-second delay before starting to ensure NAS is mounted
ExecStart=/bin/bash -c 'sleep 5 && /home/pi/venv_picframe/bin/picframe'

[Install]
WantedBy=multi-user.target
EOF

    # Enable and start the system-level service
    sudo systemctl daemon-reload
    sudo systemctl enable picframe.service
    sudo systemctl restart picframe

    # Disable the old user-level labwc service
    systemctl --user disable picframe.service 2>/dev/null

    log_message "System-level picframe.service created with 5-second boot delay and NAS mount dependency."
    update_progress 9
fi

# ---------- Final: Cleanup ----------
if [ "$LAST_COMPLETED_STEP" -ge 9 ]; then
    remove_systemd_service
    log_message "== Installation completed successfully! ==="
    log_message "Rebooting to finalize..."
    sudo reboot
    exit 0
fi

log_message "Installation script finished. Last completed step: ${LAST_COMPLETED_STEP}"
