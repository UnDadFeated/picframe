#!/bin/bash
set -e

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

log "== Restarting picframe service ==="
sudo systemctl restart picframe

log "== Deploy complete ==="