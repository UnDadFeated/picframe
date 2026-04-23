#!/bin/bash
# Idempotent deploy script - safe to run multiple times
set -e

echo "=== Deploying picframe code ==="
# Clone fork to /home/pi/picframe_data/picframe
cd /tmp
if [ -d "/tmp/picframe_clone" ]; then
    rm -rf /tmp/picframe_clone
fi
git clone https://github.com/UnDadFeated/picframe.git /tmp/picframe_clone
# Copy to destination
cp -r /tmp/picframe_clone/* /home/pi/picframe_data/picframe/
cp -r /tmp/picframe_clone/.* /home/pi/picframe_data/picframe/ 2>/dev/null || true
rm -rf /tmp/picframe_clone

echo "=== Rebuilding venv and installing picframe ==="
cd /home/pi
rm -rf venv_picframe
python3 -m venv venv_picframe
/home/pi/venv_picframe/bin/pip install --upgrade pip
/home/pi/venv_picframe/bin/pip install -e /home/pi/picframe_data/picframe/

echo "=== Creating start script ==="
cat > /home/pi/picframe_data/start_picframe.sh << 'STARTEOF'
#!/bin/bash
export XDG_RUNTIME_DIR=/tmp/runtime-pi
mkdir -p $XDG_RUNTIME_DIR
chown pi:pi $XDG_RUNTIME_DIR
exec /home/pi/venv_picframe/bin/python -m picframe
STARTEOF
chmod +x /home/pi/picframe_data/start_picframe.sh

echo "=== Deploy script complete ==="