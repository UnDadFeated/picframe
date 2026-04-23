#!/bin/bash
# Wrapper to launch the TUI editor for the Picframe configuration file.
# It finds the configuration file and opens it in the editor.
# If no configuration file exists, it copies the example file first.

# Find the configuration file
CONFIG_FILE=""
if [ -f "configuration.yaml" ]; then
    CONFIG_FILE="configuration.yaml"
elif [ -f "~/picframe_data/config/configuration.yaml" ]; then
    CONFIG_FILE="$HOME/picframe_data/config/configuration.yaml"
else
    # Look for the example file
    EXAMPLE_FILE="$(dirname "$0")/configuration_example.yaml"
    if [ -f "$EXAMPLE_FILE" ]; then
        mkdir -p "$HOME/picframe_data/config"
        cp "$EXAMPLE_FILE" "$HOME/picframe_data/config/configuration.yaml"
        CONFIG_FILE="$HOME/picframe_data/config/configuration.yaml"
    else
        echo "Error: No configuration file found."
        echo "Please create one from the example file: pfconfig.sh --init"
        exit 1
    fi
fi

# Launch the TUI editor
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/pfconfig.py" "$CONFIG_FILE"