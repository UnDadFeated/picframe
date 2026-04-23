#!/bin/bash
set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "== Updating picframe from fork (origin) ==="

cd /home/pi/picframe

# Fetch and pull from my fork, main branch
git fetch origin
git pull origin main

log "== Reinstalling picframe in venv ==="

# Activate the venv that was created at install time
if [ -f "/home/pi/picframe/venv/bin/activate" ]; then
    source /home/pi/picframe/venv/bin/activate
elif [ -f "/home/pi/picframe_data/venv/bin/activate" ]; then
    source /home/pi/picframe_data/venv/bin/activate
else
    log "WARNING: venv not found, using system python"
fi

cd /home/pi/picframe
pip install -e . --quiet 2>&1 | tail -1 || true

log "== Stopping running picframe instance ==="
# Stop any running picframe process
pkill -f "picframe" || true
sleep 2

# Restart picframe using the same method as installation
if pgrep -f picframe > /dev/null; then
    log "WARNING: picframe is still running"
fi

# Write a restart command for the user to run manually (since we can't background from here)
log ""
log "=== Update complete! ==="
log "To restart picframe, run:"
log "  ssh pi@192.168.4.110 'bash /home/pi/picframe/start_picframe.sh'"
log ""

log "=== Done ==="