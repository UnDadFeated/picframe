#!/bin/bash

# Path to store progress and log file
PROGRESS_FILE="$HOME/install_progress.txt"
LOG_FILE="$HOME/install_log.txt"
SERVICE_NAME="install_script_service"

# Set user and home directory
USER="pi"
HOME="/home/$USER"

# Function to log messages
log_message() {
    echo "$1" | tee -a "$LOG_FILE"
}

# Function to update progress
update_progress() {
    echo "$1" > "$PROGRESS_FILE"
}

# Function to get the last completed step
get_last_completed_step() {
    if [ -f "$PROGRESS_FILE" ]; then
        cat "$PROGRESS_FILE"
    else
        echo "0"
    fi
}

# Function to add a systemd service to resume the script after reboot
add_systemd_service() {
    local script_path=$(realpath "$0")
    SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
    sudo tee "$SERVICE_FILE" > /dev/null <<EOL
[Unit]
Description=Resume install script after reboot

[Service]
ExecStart=$script_path
Type=oneshot
RemainAfterExit=true

[Install]
WantedBy=multi-user.target
EOL
    sudo systemctl enable $SERVICE_NAME
    log_message "Added systemd service for reboot resume."
}

# Function to remove the systemd service after completion
remove_systemd_service() {
    sudo systemctl disable $SERVICE_NAME
    sudo rm /etc/systemd/system/$SERVICE_NAME.service
    log_message "Removed systemd service after completion."
}

# Function to reboot and resume
reboot_and_resume() {
    add_systemd_service
    update_progress "$1"
    log_message "Rebooting to complete the installation. The script will continue after reboot."
    sudo reboot
    exit 0
}

# Function to check for a working internet connection
check_internet_connection() {
  log_message "Checking for an active internet connection..."
  while ! ping -c 1 -W 1 google.com &> /dev/null; do
    log_message "No internet connection. Retrying in 5 seconds..."
    sleep 5
  done
  log_message "Internet connection confirmed."
}

# Ensure the "pi" user has passwordless sudo for specific commands in Step 5
sudoers_entry="$USER ALL=(ALL) NOPASSWD: $HOME/venv_picframe/bin/picframe, $HOME/venv_picframe/bin/pip, /usr/bin/python3, /bin/mkdir"

# Check if the entry already exists in the sudoers file to avoid duplication
if ! sudo grep -qF "$sudoers_entry" /etc/sudoers; then
    echo "$sudoers_entry" | sudo tee -a /etc/sudoers > /dev/null
    echo "Configured passwordless sudo for the 'pi' user."
else
    echo "Passwordless sudo for 'pi' user is already configured."
fi

# Main install script

# Get the last completed step
LAST_COMPLETED_STEP=$(get_last_completed_step)

# Step 1: Update the operating system...
if [ "$LAST_COMPLETED_STEP" -lt 1 ]; then
    check_internet_connection
    log_message "Step 1: Updating operating system..."
    sudo apt-get update && sudo apt upgrade -y
    reboot_and_resume 1
fi

# Step 2: Update raspi-config to boot in console as Pi...
if [ "$LAST_COMPLETED_STEP" -lt 2 ]; then
    log_message "Step 2: Updating raspi-config..."
    sudo raspi-config nonint do_boot_behaviour B2
    reboot_and_resume 2
fi

# Step 3: Install Samba and set up user with error handling
if [ "$LAST_COMPLETED_STEP" -lt 3 ]; then
    check_internet_connection
    log_message "Step 3: Installing Samba and configuring user..."
    
    # Attempt to install Samba
    sudo apt-get install samba -y

    # Ensure expect is installed for automating smbpasswd
    if ! command -v expect > /dev/null; then
        sudo apt-get install -y expect
    fi

    # Check if the Samba user '$USER' already exists, if not, add it using expect for reliable password setting
    if ! sudo pdbedit -L | grep -q "^$USER:"; then
        sudo expect <<EOL
spawn sudo smbpasswd -a $USER
expect "New SMB password:"
send "$USER\r"
expect "Retype SMB password:"
send "$USER\r"
expect eof
EOL
    fi

    # Modify Samba config file
    SAMBA_CONFIG="/etc/samba/smb.conf"
    sudo tee "$SAMBA_CONFIG" > /dev/null <<EOL
[global]
security = user
workgroup = WORKGROUP
server role = standalone server
map to guest = never
encrypt passwords = yes
obey pam restrictions = no
client min protocol = SMB2
client max protocol = SMB3

# Additional macOS fine-tuning for users; optional for Windows

vfs objects = catia fruit streams_xattr
fruit:metadata = stream
fruit:model = RackMac
fruit:posix_rename = yes
fruit:veto_appledouble = no
fruit:wipe_intentionally_left_blank_rfork = yes
fruit:delete_empty_adfiles = yes

[$USER]
comment = $USER Directories
browseable = yes
path = $HOME
read only = no
create mask = 0775
directory mask = 0775
EOL

    # Restart Samba service
    sudo systemctl restart smbd
    update_progress 3
    log_message "Samba installation and configuration completed."
fi

# Step 4: Install additional packages
if [ "$LAST_COMPLETED_STEP" -lt 4 ]; then
    check_internet_connection
    log_message "Step 4: Installing additional packages..."
    sudo apt-get install git libsdl2-dev xwayland labwc wlr-randr vlc ffmpeg -y
    # Create Pictures and DeletedPictures directories
    su - $USER -c "mkdir -p $HOME/Pictures $HOME/DeletedPictures"
    log_message "Directories 'Pictures' and 'DeletedPictures' created."
    # Install Mosquitto for MQTT
    sudo apt-get install -y mosquitto mosquitto-clients
    log_message "Mosquitto Server installed."
    reboot_and_resume 4
fi

# Step 5: Installing picframe
if [ "$LAST_COMPLETED_STEP" -lt 5 ]; then
    check_internet_connection
    log_message "Step 5: Installing picframe..."
    log_message "Creating virtual environment for picframe..."
    su - $USER -c "mkdir -p $HOME/venv_picframe" 2>&1 | tee -a "$LOG_FILE"

    log_message "Setting up Python virtual environment..."
    su - $USER -c "python3 -m venv $HOME/venv_picframe" 2>&1 | tee -a "$LOG_FILE"

    log_message "Activating virtual environment..."
    su - $USER -c "source $HOME/venv_picframe/bin/activate" 2>&1 | tee -a "$LOG_FILE"

    log_message "Installing paho-mqtt..."
    su - $USER -c "$HOME/venv_picframe/bin/pip install paho-mqtt" 2>&1 | tee -a "$LOG_FILE"

    log_message "Installing picframe..."
    su - $USER -c "git clone https://github.com/UnDadFeated/picframe.git $HOME/picframe_src" 2>&1 | tee -a "$LOG_FILE"
    su - $USER -c "$HOME/venv_picframe/bin/pip install $HOME/picframe_src" 2>&1 | tee -a "$LOG_FILE"

    # Initialize Picframe and confirm default directories
    log_message "Initializing Picframe with default directories..."
    if (echo -e "\n\n\n" | su - $USER -c "$HOME/venv_picframe/bin/picframe -i $HOME/" 2>&1 | tee -a "$LOG_FILE"); then
        log_message "Picframe initialized with default directories."
        # Copy generated configuration.yaml from old location to new config/ directory
        su - $USER -c "cp $HOME/picframe_data/config/configuration.yaml $HOME/picframe_src/picframe/config/" 2>&1 | tee -a "$LOG_FILE"
        log_message "Configuration copied to picframe/config/ directory."
        update_progress 5
    else
        log_message "Error: Failed to initialize Picframe."
        exit 1
    fi
fi

# Step 6: Configure Mosquitto for anonymous access and open listener
if [ "$LAST_COMPLETED_STEP" -lt 6 ]; then
    log_message "Step 6: Configuring Mosquitto for anonymous access and listener..."

    # Edit the Mosquitto configuration file
    log_message "Editing /etc/mosquitto/mosquitto.conf to allow anonymous access and open listener..."
    echo "allow_anonymous true" | sudo tee -a /etc/mosquitto/mosquitto.conf > /dev/null
    echo "listener 1883 0.0.0.0" | sudo tee -a /etc/mosquitto/mosquitto.conf > /dev/null

    # Restart the Mosquitto service to apply changes
    sudo systemctl restart mosquitto
    log_message "Mosquitto configuration updated and service restarted."

    # Mark step as completed
    update_progress 6
    log_message "Mosquitto configuration completed."
fi

# Step 7: Create autostart script for Picframe as user "pi"
if [ "$LAST_COMPLETED_STEP" -lt 7 ]; then
    log_message "Step 6: Creating autostart script for Picframe as user 'pi'..."

    # Create autostart script for Picframe
    AUTOSTART_SCRIPT="$HOME/start_picframe.sh"
    su - $USER -c "cat > $AUTOSTART_SCRIPT" <<'EOL'
#!/bin/bash
# Kill any existing picframe processes
pkill -9 -f picframe 2>/dev/null
sleep 3

# Wait for clean shutdown
for i in 1 2 3 4 5; do
    pgrep -f picframe >/dev/null 2>&1 || break
    sleep 1
done

# Start picframe
source $HOME/venv_picframe/bin/activate
nohup picframe > /dev/null 2>&1 &
disown
EOL

    # Make the autostart script executable
    su - $USER -c "chmod +x $AUTOSTART_SCRIPT"
    log_message "Autostart script created and made executable: $AUTOSTART_SCRIPT."

    # Create pfconfig.sh script
    PFCONFIG_SCRIPT="$HOME/pfconfig.sh"
    su - $USER -c "cat > $PFCONFIG_SCRIPT" <<'EOF'
#!/bin/bash
# Wrapper to launch the TUI editor for the Picframe configuration file.
CONFIG_DIR="$HOME/picframe_data/config"
SCRIPT_DIR="$HOME/picframe_src/src/picframe"
CONFIG_FILE="$CONFIG_DIR/configuration.yaml"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Launch the TUI editor
python3 "$SCRIPT_DIR/pfconfig.py" "$CONFIG_FILE"
EOF

    # Make the pfconfig script executable
    su - $USER -c "chmod +x $PFCONFIG_SCRIPT"
    log_message "pfconfig.sh script created and made executable: $PFCONFIG_SCRIPT."

    # Mark step as completed
    update_progress 7
    log_message "Directory setup and autostart script creation completed."
fi

# Step 8: Configure autostart for Picframe using labwc and set up systemd service as user "pi"
if [ "$LAST_COMPLETED_STEP" -lt 8 ]; then
    log_message "Step 7: Configuring autostart for Picframe with labwc and setting up systemd service as user 'pi'..."

    # Create systemd user service to start Picframe on boot
    su - $USER -c "mkdir -p $HOME/.config/systemd/user"
    SYSTEMD_SERVICE_FILE="$HOME/.config/systemd/user/picframe.service"
    su - $USER -c "cat > $SYSTEMD_SERVICE_FILE" <<'EOL'
[Unit]
Description=Picframe slideshow
After=graphical-session.target

[Service]
Type=simple
ExecStartPre=/bin/bash -c 'pkill -9 -f "picframe" 2>/dev/null; sleep 2'
ExecStart=/home/pi/venv_picframe/bin/picframe
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOL
    log_message "Created systemd user service for Picframe: $SYSTEMD_SERVICE_FILE"

    # Enable the user systemd service for autostart
    su - $USER -c "systemctl --user enable picframe.service"
    log_message "Enabled systemd user service for Picframe autostart."

    # Mark step as completed and reboot to apply changes
    log_message "Autostart configuration for Picframe completed. Rebooting to apply changes."
    reboot_and_resume 8
fi

# Final step: Remove the systemd service only if all steps are completed
if [ "$LAST_COMPLETED_STEP" -ge 8 ]; then
    remove_systemd_service
    log_message "Installation script completed, and systemd service removed. Rebooting now..."
    sudo reboot
fi