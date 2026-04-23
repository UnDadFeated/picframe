#!/bin/bash
set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "== Updating picframe from fork ==="

cd /home/pi/picframe_data

# Fetch and pull from fork (fork remote, dev branch)
git fetch fork
git pull fork dev

log "== Update complete, calling deploy ==="
bash /tmp/deploy_picframe.sh