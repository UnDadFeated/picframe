#!/usr/bin/env python3
"""Professional TUI Configuration Editor for Picframe"""

import curses
import sys
import time
import yaml
from pathlib import Path
from typing import Any, Dict

# ─────────────────────────────────────────────────────────────────────
# Configuration Menu Structure with Human-Friendly Names
# ─────────────────────────────────────────────────────────────────────

MENU_STRUCTURE: Dict[str, Dict[str, Any]] = {
    "🖼️  Display": {
        "viewer.fit": {"name": "Fit Image to Display", "type": "bool", "help": "Scale to fit or crop to fill"},
        "viewer.display_power": {"name": "Display Power Control", "type": "choice", "choices": ["vcgencmd (Raspberry Pi)", "xset (X11)", "wlr-randr (Wayland)"]},
        "viewer.display_x": {"name": "Display X Offset", "type": "int", "min": 0, "max": 1920},
        "viewer.display_y": {"name": "Display Y Offset", "type": "int", "min": 0, "max": 1080},
        "viewer.display_w": {"name": "Display Width", "type": "int", "min": 320, "max": 3840},
        "viewer.display_h": {"name": "Display Height", "type": "int", "min": 240, "max": 2160},
        "viewer.fps": {"name": "Framerate (FPS)", "type": "int", "min": 1, "max": 60},
        "viewer.background": {"name": "Background Color (RGBA)", "type": "str"},
        "viewer.use_glx": {"name": "Use GLX (X Server)", "type": "bool"},
        "viewer.use_sdl2": {"name": "Use SDL2 (Wayland/Pi)", "type": "bool"},
        "viewer.mat_images": {"name": "Auto-Mat Threshold", "type": "float", "min": 0.0, "max": 1.0},
    },
    
    "🎬 Video": {
        "viewer.video_volume": {"name": "Video Volume", "type": "int", "min": 0, "max": 100},
        "viewer.video_fit_display": {"name": "Stretch Video to Display", "type": "bool"},
        "viewer.video_play_immediately": {"name": "Play Video Immediately", "type": "bool"},
        "viewer.video_progress_show": {"name": "Show Video Progress", "type": "bool"},
        "viewer.video_ratio_enabled": {"name": "Enable Video Ratio", "type": "bool"},
        "viewer.video_ratio_videos": {"name": "Video Ratio Numerator", "type": "int", "min": 1, "max": 200},
        "viewer.video_ratio_total": {"name": "Video Ratio Denominator", "type": "int", "min": 1, "max": 100},
        "viewer.video_quarantine_days": {"name": "Video Cooldown (days)", "type": "int", "min": 0, "max": 365},
    },
    
    "📸 Photos": {
        "model.pic_dir": {"name": "Media Root Folder", "type": "str"},
        "model.deleted_pictures": {"name": "Deleted Pictures Folder", "type": "str"},
        "model.no_files_img": {"name": "No Files Image", "type": "str"},
        "model.subdirectory": {"name": "Subdirectory of pic_dir", "type": "str"},
        "model.shuffle": {"name": "Shuffle Playlist", "type": "bool"},
        "model.follow_links": {"name": "Follow Symlinked Folders", "type": "bool"},
        "model.recent_n": {"name": "Recent-First Window (days)", "type": "int", "min": 0, "max": 90},
        "model.reshuffle_num": {"name": "Reshuffle Play Count", "type": "int", "min": 1, "max": 100},
        "model.time_delay": {"name": "Slide Time Delay (sec)", "type": "float", "min": 1, "max": 600},
        "model.fade_time": {"name": "Fade Time (sec)", "type": "float", "min": 1.0, "max": 30.0},
        "model.update_interval": {"name": "Cache Update Interval (sec)", "type": "float", "min": 1.0, "max": 30.0},
        "model.portrait_pairs": {"name": "Portrait Pairs Display", "type": "bool"},
        "model.location_filter": {"name": "Location SQL Filter", "type": "str"},
        "model.tags_filter": {"name": "Tags SQL Filter", "type": "str"},
        "model.key_list": {"name": "Key List (comma-separated)", "type": "str"},
        "viewer.photo_quarantine_days": {"name": "Photo Cooldown (days)", "type": "int", "min": 0, "max": 365},
    },
    
    "🎨 Visual Effects": {
        "viewer.blend_type": {"name": "Transition Blend Type", "type": "choice", "choices": ["blend", "burn", "bump"]},
        "viewer.kenburns": {"name": "Enable Ken Burns", "type": "bool"},
        "viewer.blur_edges": {"name": "Blur Edges", "type": "bool"},
        "viewer.blur_amount": {"name": "Background Blur Amount", "type": "int", "min": 0, "max": 50},
        "viewer.blur_zoom": {"name": "Blur Zoom", "type": "float", "min": 1.0, "max": 5.0},
        "viewer.edge_alpha": {"name": "Edge Alpha", "type": "float", "min": 0.0, "max": 1.0},
        "viewer.text_opacity": {"name": "Text Opacity", "type": "float", "min": 0.0, "max": 1.0},
        "viewer.text_bkg_hgt": {"name": "Text Background Height (0-1)", "type": "float", "min": 0.0, "max": 1.0},
    },
    
    "⏰ Clock": {
        "viewer.show_clock": {"name": "Show Clock Overlay", "type": "bool"},
        "viewer.clock_format": {"name": "Clock Format", "type": "str"},
        "viewer.clock_text_sz": {"name": "Clock Text Size", "type": "int", "min": 10, "max": 200},
        "viewer.clock_opacity": {"name": "Clock Opacity", "type": "float", "min": 0.0, "max": 1.0},
        "viewer.clock_justify": {"name": "Clock Justify", "type": "choice", "choices": ["L", "C", "R"]},
        "viewer.clock_top_bottom": {"name": "Clock Position", "type": "choice", "choices": ["Top", "Bottom"]},
        "viewer.clock_wdt_offset_pct": {"name": "Clock Width Offset (%)", "type": "float", "min": 0.0, "max": 50.0},
        "viewer.clock_hgt_offset_pct": {"name": "Clock Height Offset (%)", "type": "float", "min": 0.0, "max": 50.0},
    },
    
    "📝 Text Overlay": {
        "viewer.show_text": {"name": "Text Fields to Show", "type": "str"},
        "viewer.show_text_fm": {"name": "Date Format String", "type": "str"},
        "viewer.show_text_tm": {"name": "Text Show Time (sec)", "type": "float", "min": 1.0, "max": 300.0},
        "viewer.show_text_sz": {"name": "Text Size", "type": "int", "min": 10, "max": 100},
        "viewer.text_justify": {"name": "Text Justification", "type": "choice", "choices": ["L", "C", "R"]},
        "viewer.text_position_mode": {"name": "Text Position Mode", "type": "choice", "choices": ["margin", "absolute"]},
        "viewer.text_x_margin": {"name": "Text X Margin (px)", "type": "int", "min": 0},
        "viewer.text_y_margin": {"name": "Text Y Margin (px)", "type": "int", "min": 0},
        "viewer.text_x_position": {"name": "Text X Position (px)", "type": "int"},
        "viewer.text_y_position": {"name": "Text Y Position (px)", "type": "int"},
        "viewer.text_width": {"name": "Text Max Width (px)", "type": "int"},
        "viewer.text_line_spacing": {"name": "Text Line Spacing", "type": "float", "min": 0.5, "max": 3.0},
        "viewer.font_file": {"name": "Font File Path", "type": "str"},
        "viewer.shader": {"name": "Shader Path", "type": "str"},
    },
    
    "🖌️  Mat/Frame": {
        "viewer.mat_type": {"name": "Mat Style", "type": "str"},
        "viewer.outer_mat_color": {"name": "Outer Mat Color (RGBA)", "type": "str"},
        "viewer.inner_mat_color": {"name": "Inner Mat Color (RGBA)", "type": "str"},
        "viewer.outer_mat_border": {"name": "Outer Mat Border (px)", "type": "int", "min": 0},
        "viewer.inner_mat_border": {"name": "Inner Mat Border (px)", "type": "int", "min": 0},
        "viewer.outer_mat_use_texture": {"name": "Use Outer Mat Texture", "type": "bool"},
        "viewer.inner_mat_use_texture": {"name": "Use Inner Mat Texture", "type": "bool"},
        "viewer.mat_resource_folder": {"name": "Mat Resource Folder", "type": "str"},
    },
    
    "⏱️  Slide Progress": {
        "viewer.slide_progress_show": {"name": "Show Slide Countdown", "type": "bool"},
        "viewer.slide_progress_font_size": {"name": "Slide Countdown Font Size", "type": "int", "min": 8, "max": 72},
        "viewer.slide_progress_position": {"name": "Slide Countdown Position", "type": "choice", "choices": ["top-right", "bottom-right"]},
        "viewer.slide_progress_x_offset": {"name": "Slide X Offset (px)", "type": "int", "min": 0},
        "viewer.slide_progress_y_offset": {"name": "Slide Y Offset (px)", "type": "int", "min": 0},
    },
    
    "💾 Cache Progress": {
        "viewer.show_cache_indicator": {"name": "Show Cache Indicator", "type": "bool"},
        "viewer.cache_progress_position": {"name": "Cache Progress Position", "type": "choice", "choices": ["top-right", "bottom-right"]},
        "viewer.cache_progress_x_offset": {"name": "Cache X Offset (px)", "type": "int", "min": 0},
        "viewer.cache_progress_y_offset": {"name": "Cache Y Offset (px)", "type": "int", "min": 0},
        "viewer.cache_progress_font_size": {"name": "Cache Font Size", "type": "int", "min": 8, "max": 72},
        "viewer.cache_progress_text_width": {"name": "Cache Text Max Width (px)", "type": "int", "min": 100},
    },
    
    "📊 Menu": {
        "viewer.menu_text_sz": {"name": "Menu Text Size", "type": "int", "min": 10, "max": 100},
        "viewer.menu_autohide_tm": {"name": "Menu Auto-hide Time (sec)", "type": "float", "min": 0.0, "max": 60.0},
        "viewer.geo_suppress_list": {"name": "Location Suppress List", "type": "str"},
    },
    
    "💾 Database": {
        "model.db_file": {"name": "Database File Path", "type": "str"},
        "model.bad_files_db": {"name": "Bad Files Database", "type": "str"},
        "model.load_geoloc": {"name": "Load GPS from OSM", "type": "bool"},
        "model.geo_key": {"name": "Geocoder Key (email)", "type": "str"},
        "model.locale": {"name": "System Locale", "type": "str"},
        "model.image_attr": {"name": "Image Metadata Fields", "type": "str"},
        "viewer.enable_smart_cache": {"name": "Enable Smart Cache", "type": "bool"},
        "viewer.enable_date_filter": {"name": "Enable Date Filter", "type": "bool"},
        "viewer.date_range_days": {"name": "Date Filter Window (days)", "type": "int", "min": 1, "max": 365},
        "viewer.cache_start_min_files": {"name": "Cache Start Min Files", "type": "int", "min": 0, "max": 1000},
        "viewer.cache_refresh_timezone": {"name": "Cache Refresh Timezone", "type": "str"},
    },
    
    "🔄 Updates": {
        "updater.auto_update_on_start": {"name": "Auto Update on Start", "type": "bool"},
        "updater.restart_after_update": {"name": "Restart After Update", "type": "bool"},
        "updater.git_branch": {"name": "Git Branch", "type": "str"},
        "updater.git_remote": {"name": "Git Remote URL", "type": "str"},
        "updater.git_repo": {"name": "Git Repo URL", "type": "str"},
        "updater.repo_dir": {"name": "Repository Path", "type": "str"},
    },
    
    "🌐 MQTT": {
        "mqtt.use_mqtt": {"name": "Enable MQTT", "type": "bool"},
        "mqtt.server": {"name": "MQTT Server", "type": "str"},
        "mqtt.port": {"name": "MQTT Port", "type": "int", "min": 1, "max": 65535},
        "mqtt.login": {"name": "MQTT Username", "type": "str"},
        "mqtt.password": {"name": "MQTT Password", "type": "str"},
        "mqtt.tls": {"name": "TLS CA Certificate Path", "type": "str"},
        "mqtt.device_id": {"name": "Device ID", "type": "str"},
        "mqtt.device_url": {"name": "Device URL (Home Assistant)", "type": "str"},
    },
    
    "🌐 HTTP": {
        "http.use_http": {"name": "Enable HTTP Server", "type": "bool"},
        "http.path": {"name": "HTML Files Folder", "type": "str"},
        "http.port": {"name": "HTTP Port", "type": "int", "min": 1025, "max": 65535},
        "http.use_ssl": {"name": "Enable HTTPS", "type": "bool"},
        "http.auth": {"name": "Enable Basic Auth", "type": "bool"},
        "http.username": {"name": "HTTP Username", "type": "str"},
        "http.password": {"name": "HTTP Password", "type": "str"},
        "http.keyfile": {"name": "SSL Private Key Path", "type": "str"},
        "http.certfile": {"name": "SSL Certificate Path", "type": "str"},
    },
    
    "🔌 Peripherals": {
        "peripherals.input_type": {"name": "Input Device Type", "type": "choice", "choices": ["null", "keyboard", "touch", "mouse"]},
        "peripherals.buttons.pause.enable": {"name": "Pause Button Enabled", "type": "bool"},
        "peripherals.buttons.pause.label": {"name": "Pause Button Label", "type": "str"},
        "peripherals.buttons.pause.shortcut": {"name": "Pause Shortcut", "type": "str"},
        "peripherals.buttons.display_off.enable": {"name": "Display Off Button Enabled", "type": "bool"},
        "peripherals.buttons.display_off.label": {"name": "Display Off Label", "type": "str"},
        "peripherals.buttons.display_off.shortcut": {"name": "Display Off Shortcut", "type": "str"},
        "peripherals.buttons.location.enable": {"name": "Location Button Enabled", "type": "bool"},
        "peripherals.buttons.location.label": {"name": "Location Label", "type": "str"},
        "peripherals.buttons.location.shortcut": {"name": "Location Shortcut", "type": "str"},
        "peripherals.buttons.exit.enable": {"name": "Exit Button Enabled", "type": "bool"},
        "peripherals.buttons.exit.label": {"name": "Exit Label", "type": "str"},
        "peripherals.buttons.exit.shortcut": {"name": "Exit Shortcut", "type": "str"},
        "peripherals.buttons.power_down.enable": {"name": "Power Down Button Enabled", "type": "bool"},
        "peripherals.buttons.power_down.label": {"name": "Power Down Label", "type": "str"},
        "peripherals.buttons.power_down.shortcut": {"name": "Power Down Shortcut", "type": "str"},
    },
    
    "🤖 AI": {
        "ai.semantic_tagging_enable": {"name": "Enable Semantic Tagging", "type": "bool"},
        "ai.semantic_tagging_model": {"name": "Semantic Tagging Model", "type": "str"},
        "ai.semantic_tagging_threshold": {"name": "Semantic Tagging Threshold", "type": "float", "min": 0.0, "max": 1.0},
    },
    
    "🌡️  Ambient": {
        "ambient.pir_sensor_pin": {"name": "PIR Sensor Pin", "type": "str"},
        "ambient.true_tone_adjust": {"name": "True Tone Adjust", "type": "float", "min": 0.0, "max": 1.0},
    },
    
    "📊 Dashboard": {
        "dashboard.daily_recap_mode": {"name": "Daily Recap Mode", "type": "str"},
    },
    
    "☁️  Cloud": {
        "cloud.rclone_sync_enable": {"name": "Enable Rclone Sync", "type": "bool"},
        "cloud.rclone_remote_name": {"name": "Rclone Remote Name", "type": "str"},
        "cloud.rclone_sync_interval": {"name": "Rclone Sync Interval (sec)", "type": "int", "min": 60},
    },
    
    "🔊 Sound": {
        "sound.soundscapes_enable": {"name": "Enable Soundscapes", "type": "bool"},
        "sound.sound_profile": {"name": "Sound Profile", "type": "str"},
    },
}

# ─────────────────────────────────────────────────────────────────────
# Color Definitions
# ─────────────────────────────────────────────────────────────────────

class Colors:
    """Color pair definitions"""
    TITLE = 1
    MENU_ITEM = 2
    SELECTED = 3
    VALUE = 4
    HELP = 5
    STATUS = 6
    ERROR = 7
    SUCCESS = 8

def init_colors() -> None:
    """Initialize curses color pairs"""
    try:
        curses.init_pair(Colors.TITLE, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(Colors.MENU_ITEM, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(Colors.SELECTED, curses.COLOR_BLACK, curses.COLOR_CYAN)
        curses.init_pair(Colors.VALUE, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(Colors.HELP, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(Colors.STATUS, curses.COLOR_BLACK, curses.COLOR_WHITE)
        curses.init_pair(Colors.ERROR, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(Colors.SUCCESS, curses.COLOR_GREEN, curses.COLOR_BLACK)
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────────────
# YAML Utilities
# ─────────────────────────────────────────────────────────────────────

def load_yaml(filepath: str) -> Dict[str, Any]:
    """Load YAML configuration file"""
    try:
        with open(filepath, 'r') as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}

def save_yaml(filepath: str, data: Dict[str, Any]) -> bool:
    """Save configuration to YAML file, preserving comments"""
    try:
        with open(filepath, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        return True
    except Exception:
        return False

def get_nested_value(data: Dict[str, Any], path: str) -> Any:
    """Get nested dictionary value using dot notation (e.g., 'viewer.fps')"""
    keys = path.split('.')
    value = data
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return None
    return value

def set_nested_value(data: Dict[str, Any], path: str, value: Any) -> None:
    """Set nested dictionary value using dot notation"""
    keys = path.split('.')
    current = data
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

# ─────────────────────────────────────────────────────────────────────
# Main TUI Application
# ─────────────────────────────────────────────────────────────────────

class PicframeConfigEditor:
    """Professional TUI configuration editor for Picframe"""
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.config: Dict[str, Any] = load_yaml(config_path)
        self.menu_sections = list(MENU_STRUCTURE.keys())
        self.current_section_idx = 0
        self.current_item_idx = 0
        self.scroll_offset = 0
        self.item_scroll_offset = 0
        self.status_msg = ""
        self.status_time = 0.0
        self.editing = False
        self.edit_buffer = ""
        self.edit_cursor_pos = 0
        self.editing_key_path: str | None = None
    
    def run(self, stdscr: Any) -> None:
        """Main event loop"""
        curses.curs_set(0)
        stdscr.keypad(True)
        stdscr.nodelay(False)
        init_colors()
        
        while True:
            self.draw(stdscr)
            key = stdscr.getch()
            
            if not self.handle_input(key):
                break
    
    def handle_input(self, key: int) -> bool:
        """Handle keyboard input. Returns False to quit."""
        if self.editing:
            return self.handle_edit_input(key)
        
        # Navigation
        if key == curses.KEY_UP:
            self.current_item_idx = max(0, self.current_item_idx - 1)
        elif key == curses.KEY_DOWN:
            items = list(MENU_STRUCTURE[self.menu_sections[self.current_section_idx]].keys())
            self.current_item_idx = min(len(items) - 1, self.current_item_idx + 1)
        elif key == curses.KEY_LEFT:
            self.current_section_idx = max(0, self.current_section_idx - 1)
            self.current_item_idx = 0
        elif key == curses.KEY_RIGHT:
            self.current_section_idx = min(len(self.menu_sections) - 1, self.current_section_idx + 1)
            self.current_item_idx = 0
        
        # Actions
        elif key in (ord('\n'), ord('\r'), ord(' ')):
            self.start_edit()
        elif key == ord('s') or key == ord('S'):
            self.save_config()
        elif key == ord('q') or key == ord('Q') or key == 27:  # ESC
            return False
        elif key == ord('?') or key == ord('h') or key == ord('H'):
            self.show_help()
        
        return True
    
    def handle_edit_input(self, key: int) -> bool:
        """Handle input while editing a value"""
        if key == 27:  # ESC - cancel
            self.editing = False
            self.editing_key_path = None
            self.edit_buffer = ""
            self.edit_cursor_pos = 0
        elif key in (ord('\n'), ord('\r')):  # ENTER - confirm
            self.apply_edit()
        elif key == curses.KEY_BACKSPACE or key == 127:
            self.edit_buffer = self.edit_buffer[:-1]
            if self.edit_cursor_pos > 0:
                self.edit_cursor_pos -= 1
        elif key == curses.KEY_LEFT:
            self._handle_edit_left()
        elif key == curses.KEY_RIGHT:
            self._handle_edit_right()
        elif key == curses.KEY_UP:
            self._handle_edit_up()
        elif key == curses.KEY_DOWN:
            self._handle_edit_down()
        elif 32 <= key <= 126:  # Printable characters
            self.edit_buffer += chr(key)
            self.edit_cursor_pos = len(self.edit_buffer)
        return True
    
    def _handle_edit_left(self) -> None:
        """Handle left arrow key during editing"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        if config_item["type"] in ("int", "float"):
            self._adjust_slider(-1)
        elif self.edit_cursor_pos > 0:
            self.edit_cursor_pos -= 1
            # Rebuild edit_buffer with cursor position
            self.edit_buffer = self.edit_buffer  # cursor position tracked separately
    
    def _handle_edit_right(self) -> None:
        """Handle right arrow key during editing"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        if config_item["type"] in ("int", "float"):
            self._adjust_slider(1)
        elif self.edit_cursor_pos < len(self.edit_buffer):
            self.edit_cursor_pos += 1
    
    def _handle_edit_up(self) -> None:
        """Handle up arrow key during editing"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        if config_item["type"] in ("int", "float"):
            self._adjust_slider(-1)
        elif config_item["type"] == "choice":
            self._adjust_choice(-1)
    
    def _handle_edit_down(self) -> None:
        """Handle down arrow key during editing"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        if config_item["type"] in ("int", "float"):
            self._adjust_slider(1)
        elif config_item["type"] == "choice":
            self._adjust_choice(1)
    
    def _adjust_choice(self, direction: int) -> None:
        """Adjust choice selection"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        if config_item["type"] != "choice" or "choices" not in config_item:
            return
        
        choices = config_item["choices"]
        # Use edit buffer value if available, otherwise config value
        if self.editing and self.editing_key_path == key_path and self.edit_buffer:
            current_value = self.edit_buffer
        else:
            current_value = get_nested_value(self.config, key_path)
        current_idx = choices.index(str(current_value)) if str(current_value) in choices else 0
        
        new_idx = current_idx + direction
        new_idx = max(0, min(len(choices) - 1, new_idx))
        
        self.edit_buffer = choices[new_idx]
    
    def _adjust_slider(self, direction: int) -> None:
        """Adjust slider value by direction (-1 or 1)"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        if config_item["type"] not in ("int", "float"):
            return
        
        # Use edit buffer value if currently editing and buffer has content
        if self.editing and self.editing_key_path == key_path and self.edit_buffer:
            try:
                current_value = float(self.edit_buffer)
            except (ValueError, TypeError):
                current_value = get_nested_value(self.config, key_path)
        else:
            current_value = get_nested_value(self.config, key_path)
        if current_value is None:
            current_value = config_item.get("min", 0)
        
        try:
            current_val = float(current_value)
            min_val = config_item.get("min", 0)
            max_val = config_item.get("max", 100)
            
            # Calculate step size based on range
            range_size = max_val - min_val
            if range_size <= 10:
                step = 1
            elif range_size <= 50:
                step = 1
            elif range_size <= 100:
                step = 2
            elif range_size <= 1000:
                step = 10
            else:
                step = range_size / 50  # 50 steps across the range
            
            new_val = current_val + (direction * step)
            new_val = max(min_val, min(max_val, new_val))
            
            # Format the value
            if config_item["type"] == "int":
                self.edit_buffer = str(int(new_val))
            else:
                self.edit_buffer = f"{new_val:.2f}"
        except (ValueError, TypeError):
            pass
    
    def start_edit(self) -> None:
        """Start editing the current item"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        if self.current_item_idx < len(items):
            key_path = items[self.current_item_idx]
            config_item = MENU_STRUCTURE[section][key_path]
            
            # Initialize edit buffer - for text fields, pre-fill with current value
            # for int/float fields, start empty so typing begins fresh (slider uses current_value as base)
            current_value = get_nested_value(self.config, key_path)
            if config_item["type"] in ("int", "float"):
                self.edit_buffer = ""
            else:
                self.edit_buffer = str(current_value) if current_value is not None else ""
                
            self.editing_key_path = key_path
            self.edit_cursor_pos = len(self.edit_buffer)
            self.editing = True
    
    def apply_edit(self) -> None:
        """Apply the edited value"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        # Parse value based on type
        try:
            parsed_value: Any
            if config_item["type"] == "bool":
                parsed_value = self.edit_buffer.lower() in ("true", "yes", "1", "on")
            elif config_item["type"] == "int":
                parsed_value = int(self.edit_buffer)
                # Clamp to range if specified
                if "min" in config_item:
                    parsed_value = max(config_item["min"], parsed_value)
                if "max" in config_item:
                    parsed_value = min(config_item["max"], parsed_value)
            elif config_item["type"] == "float":
                stripped = self.edit_buffer.strip().lower()
                if stripped in ("none", "null", ""):
                    parsed_value = None
                else:
                    parsed_value = float(self.edit_buffer)
                    if "min" in config_item:
                        parsed_value = max(config_item["min"], parsed_value)
                    if "max" in config_item:
                        parsed_value = min(config_item["max"], parsed_value)
            else:
                parsed_value = self.edit_buffer
            
            set_nested_value(self.config, key_path, parsed_value)
            self.status_msg = f"✓ Updated {config_item['name']}"
            self.status_time = time.time()
        except ValueError as e:
            self.status_msg = f"✗ Invalid value: {str(e)}"
            self.status_time = time.time()
        
        self.editing = False
        self.editing_key_path = None
        self.edit_buffer = ""
    
    def save_config(self) -> None:
        """Save configuration to YAML file"""
        if save_yaml(self.config_path, self.config):
            self.status_msg = f"✓ Configuration saved to {self.config_path}"
        else:
            self.status_msg = "✗ Failed to save configuration"
        self.status_time = time.time()
    
    def show_help(self) -> None:
        """Display help message"""
        self.status_msg = "↑↓ Navigate  ← → Section  Enter Edit  S Save  Q Quit  ? Help"
        self.status_time = time.time()
    
    def draw(self, stdscr: Any) -> None:
        """Draw the TUI with vertical sidebar"""
        stdscr.clear()
        height, width = stdscr.getmaxyx()
        
        # Title
        def get_picframe_version():
            """Get picframe version by reading __init__.py or falling back to git describe."""
            import os
            import subprocess
            
            # Default path on Raspberry Pi
            init_path = os.path.expanduser("~/picframe_src/src/picframe/__init__.py")
            if os.path.isfile(init_path):
                try:
                    with open(init_path, "r") as f:
                        for line in f:
                            if line.startswith("__version__"):
                                v = line.split('"')[1]
                                return v
                except Exception:
                    pass
            
            # Fallback: git describe from ~/picframe_src
            try:
                result = subprocess.run(
                    ["git", "describe", "--tags", "--always"],
                    cwd=os.path.expanduser("~/picframe_src"),
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    tag = result.stdout.strip().lstrip("v")
                    return tag
            except Exception:
                pass
            
            return "unknown"
        
        v = get_picframe_version()
        title = f" Picframe Configuration Editor - v{v} "
        title_x = (width - len(title)) // 2
        stdscr.addstr(0, title_x, title, curses.color_pair(Colors.TITLE) | curses.A_BOLD)
        
        # Sidebar (left)
        sidebar_w = 30
        sidebar_x = 0
        sidebar_y = 2
        for i, section in enumerate(self.menu_sections):
            attr = curses.color_pair(Colors.SELECTED) if i == self.current_section_idx else curses.color_pair(Colors.MENU_ITEM)
            line = f" {section}"
            stdscr.addstr(sidebar_y + i, sidebar_x, line[:sidebar_w-1], attr)
        
        # Items (right)
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        right_margin = 2
        item_w = width - sidebar_w - right_margin
        item_x = sidebar_w
        item_y = 2
        
        # Calculate scroll offset to keep selected item visible
        visible_items = height - 4
        if self.current_item_idx < self.item_scroll_offset:
            self.item_scroll_offset = self.current_item_idx
        elif self.current_item_idx >= self.item_scroll_offset + visible_items:
            self.item_scroll_offset = self.current_item_idx - visible_items + 1
        
        for i, key_path in enumerate(items):
            if i < self.item_scroll_offset:
                continue
            if item_y >= height - 3:
                break
            
            config_item = MENU_STRUCTURE[section][key_path]
            current_value = get_nested_value(self.config, key_path)
            
            # Format value (use edit_buffer if currently editing)
            # Removed unused display_value assignment
            
            if config_item["type"] == "int":
                if self.editing and self.editing_key_path == key_path and self.edit_buffer:
                    # Only show edit buffer for the currently editing item
                    try:
                        val = int(self.edit_buffer)
                        if "min" in config_item:
                            val = max(config_item["min"], val)
                        if "max" in config_item:
                            val = min(config_item["max"], val)
                        value_str = f"{val} [{val}]"
                    except ValueError:
                        value_str = f"{self.edit_buffer} [?]"
                else:
                    value_str = str(current_value)
            elif config_item["type"] == "float":
                if self.editing and self.editing_key_path == key_path and self.edit_buffer:
                    # Only show edit buffer for the currently editing item
                    try:
                        fval = float(self.edit_buffer)
                        if "min" in config_item:
                            fval = max(config_item["min"], fval)
                        if "max" in config_item:
                            fval = min(config_item["max"], fval)
                        value_str = f"{fval:.2f} [{fval:.2f}]"
                    except (ValueError, TypeError):
                        value_str = f"{self.edit_buffer} [?]"
                else:
                    value_str = f"{current_value}" if current_value is not None else "None"
            elif config_item["type"] == "bool":
                if self.editing and self.edit_buffer:
                    value_str = "✓ ON" if self.edit_buffer.lower() in ("true", "yes", "1", "on") else "○ OFF"
                else:
                    value_str = "✓ ON" if current_value else "○ OFF"
            elif config_item["type"] == "choice":
                if self.editing and self.edit_buffer:
                    value_str = f"{self.edit_buffer} [editing]"
                else:
                    value_str = str(current_value)
            else:
                value_str = str(current_value)[:30] if not self.editing else self.edit_buffer
            
            # Draw item
            attr = curses.color_pair(Colors.SELECTED) if i == self.current_item_idx else curses.color_pair(Colors.MENU_ITEM)
            name_w = 28  # Fixed width for name column to keep values close to submenu
            name = config_item["name"][:name_w]
            line = f"  {name:<{name_w}} {value_str}"
            stdscr.addstr(item_y, item_x, line[:item_w-1], attr)
            item_y += 1
        
        # Status bar
        status_bar_y = height - 2
        status_text = self.status_msg if time.time() - self.status_time < 3.0 else ""
        stdscr.addstr(status_bar_y, 0, " " * width, curses.color_pair(Colors.STATUS))
        if status_text:
            stdscr.addstr(status_bar_y, 2, status_text[:width-4], curses.color_pair(Colors.STATUS))
        
        # Edit overlay
        if self.editing:
            self._draw_edit_overlay(stdscr, width, height)
        
        # Help line
        help_text = "↑↓ Navigate  ← → Section  ENTER Edit  S Save  Q Quit  ? Help"
        help_y = height - 1
        stdscr.addstr(help_y, 0, help_text[:width-1], curses.color_pair(Colors.HELP))
        
        stdscr.refresh()
    
    def _draw_edit_overlay(self, stdscr, width: int, height: int) -> None:
        """Draw the edit overlay with slider/choice support"""
        section = self.menu_sections[self.current_section_idx]
        items = list(MENU_STRUCTURE[section].keys())
        key_path = items[self.current_item_idx]
        config_item = MENU_STRUCTURE[section][key_path]
        
        # Calculate overlay position
        overlay_w = min(60, width - 4)
        overlay_h = 8
        overlay_x = (width - overlay_w) // 2
        overlay_y = (height - overlay_h) // 2
        
        # Draw overlay background
        for y in range(overlay_h):
            stdscr.addstr(overlay_y + y, overlay_x, " " * overlay_w, curses.color_pair(Colors.VALUE))
        
        # Draw border
        border_attr = curses.color_pair(Colors.SELECTED) | curses.A_BOLD
        stdscr.addstr(overlay_y, overlay_x, "+" + "-" * (overlay_w - 2) + "+", border_attr)
        stdscr.addstr(overlay_y + overlay_h - 1, overlay_x, "+" + "-" * (overlay_w - 2) + "+", border_attr)
        for y in range(1, overlay_h - 1):
            stdscr.addstr(overlay_y + y, overlay_x, "|", border_attr)
            stdscr.addstr(overlay_y + y, overlay_x + overlay_w - 1, "|", border_attr)
        
        # Draw title
        title = f" {config_item['name']}"
        stdscr.addstr(overlay_y + 1, overlay_x + 2, title[:overlay_w - 4], curses.A_BOLD)
        
        # Draw current value with slider/choice
        current_value = get_nested_value(self.config, key_path)
        value_y = overlay_y + 3
        
        if config_item["type"] == "choice" and "choices" in config_item:
            # Draw choice list
            choices = config_item["choices"]
            current_str = str(current_value) if current_value is not None else ""
            selected_idx = next((i for i, c in enumerate(choices) if c == current_str), 0)
            for i, choice in enumerate(choices):
                y_pos = value_y + i
                if i == selected_idx:
                    marker = "► "
                    attr = curses.color_pair(Colors.SELECTED) | curses.A_BOLD
                else:
                    marker = "  "
                    attr = curses.color_pair(Colors.VALUE)
                stdscr.addstr(overlay_y + y_pos, overlay_x + 2, f"{marker}{choice}", attr)
            hint = "↑↓ Select  ENTER Confirm"
        elif config_item["type"] in ("int", "float"):
            # Draw slider
            min_val = config_item.get("min", 0)
            max_val = config_item.get("max", 100)
            slider_w = overlay_w - 8
            if self.edit_buffer:
                # Use edit buffer value when actively editing
                try:
                    display_val = int(float(self.edit_buffer)) if config_item["type"] == "int" else float(self.edit_buffer)
                except (ValueError, TypeError):
                    # Fall back to current config value if edit buffer is invalid
                    display_val = current_value if current_value is not None else min_val
            else:
                # No edit buffer - use current config value (not min_val)
                display_val = current_value if current_value is not None else min_val
            
            normalized = (display_val - min_val) / (max_val - min_val) if max_val != min_val else 0
            normalized = max(0.0, min(1.0, normalized))
            filled = int(normalized * slider_w)
            
            slider_line = f" [{('=' * filled) + ('-' * (slider_w - filled))}] {display_val}"
            stdscr.addstr(value_y, overlay_x + 2, slider_line[:overlay_w - 4], curses.color_pair(Colors.VALUE))
            
            # Show range
            range_line = f" Min: {min_val}    Max: {max_val}"
            stdscr.addstr(value_y + 1, overlay_x + 2, range_line[:overlay_w - 4], curses.color_pair(Colors.HELP))
            
            # Show edit buffer
            buffer_y = value_y + 5
            input_label = " Value: "
            stdscr.addstr(buffer_y, overlay_x + 2, input_label, curses.A_BOLD)
            stdscr.addstr(buffer_y, overlay_x + 10, self.edit_buffer.ljust(overlay_w - 14), curses.color_pair(Colors.SELECTED) | curses.A_BOLD)
            
            hint = "← → Adjust  ENTER Confirm  ESC Cancel"
        else:
            # Text input - show cursor position
            buffer_y = value_y
            input_label = " Value: "
            stdscr.addstr(buffer_y, overlay_x + 2, input_label, curses.A_BOLD)
            # Display text with cursor marker
            if self.edit_buffer:
                cursor_char = "█"
                text_display = self.edit_buffer[:self.edit_cursor_pos] + cursor_char + self.edit_buffer[self.edit_cursor_pos:]
            else:
                text_display = "█"
            stdscr.addstr(buffer_y, overlay_x + 10, text_display.ljust(overlay_w - 14), curses.color_pair(Colors.SELECTED) | curses.A_BOLD)
            hint = "← → Move Cursor  ENTER Confirm  ESC Cancel"
        
        # Draw hint
        hint_y = overlay_y + overlay_h - 2
        stdscr.addstr(hint_y, overlay_x + 2, hint[:overlay_w - 4], curses.color_pair(Colors.HELP))
    
    @staticmethod
    def _draw_slider(value: float, min_val: float, max_val: float, width: int) -> str:
        """Draw a simple slider representation"""
        if value is None:
            return "[" + "-" * width + "]"
        
        normalized = (float(value) - min_val) / (max_val - min_val)
        normalized = max(0.0, min(1.0, normalized))
        filled = int(normalized * width)
        slider = "[" + "=" * filled + "-" * (width - filled) + "]"
        return f"{slider} {value}"

# ─────────────────────────────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────────────────────────────

def main() -> None:
    """Main entry point"""
    # Get config path from command line argument or use default
    if len(sys.argv) > 1:
        config_path = Path(sys.argv[1])
    else:
        # Default: look in same directory as this script
        script_dir = Path(__file__).parent
        config_path = script_dir / "configuration.yaml"
    
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        sys.exit(1)
    
    try:
        editor = PicframeConfigEditor(str(config_path))
        curses.wrapper(editor.run)
    except KeyboardInterrupt:
        print("\nConfiguration editor closed.")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
