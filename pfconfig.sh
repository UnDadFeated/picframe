#!/bin/bash
# Wrapper to launch the TUI editor for the Picframe configuration file.
# On the Raspberry Pi:
#   - Config is at ~/picframe_data/config/configuration.yaml
#   - TUI code is at ~/picframe_src/src/picframe/pfconfig.py
# Locally:
#   - Config is at ./src/picframe/config/configuration.yaml
#   - TUI code is at ./src/picframe/config/pfconfig.py

# Determine if running on the Pi (check for picframe_data directory)
if [ -d "$HOME/picframe_data/config" ]; then
    CONFIG_DIR="$HOME/picframe_data/config"
    SCRIPT_DIR="$HOME/picframe_src/src/picframe"
else
    # Running locally - use relative paths
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    CONFIG_DIR="$SCRIPT_DIR"
fi

CONFIG_FILE="$CONFIG_DIR/configuration.yaml"

# Check if config file exists
if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: Configuration file not found at $CONFIG_FILE"
    exit 1
fi

# Launch the TUI editor
python3 "$SCRIPT_DIR/pfconfig.py" "$CONFIG_FILE"
