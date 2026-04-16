#!/usr/bin/env python3
import curses
import yaml
import os
import re
import sys
import copy

CONFIG_PATHS = [
    "configuration.yaml",
    os.path.expanduser("~/picframe_data/config/configuration.yaml")
]

SLIDERS = {
    'blur_amount': (0, 50),
    'fps': (1, 60),
    'video_volume': (0, 100),
    'date_range_days': (1, 365),
    'clock_text_sz': (10, 200),
    'menu_text_sz': (10, 100),
    'show_text_sz': (10, 100),
    'text_x_margin': (0, 500),
    'text_y_margin': (0, 500),
    'outer_mat_border': (0, 200),
    'inner_mat_border': (0, 200),
    'recent_n': (0, 90),
    'reshuffle_num': (1, 10),
    'time_delay': (1, 600),
    'fade_time': (1.0, 30.0),
    'update_interval': (1.0, 30.0),
    'blur_zoom': (1.0, 5.0),
    'edge_alpha': (0.0, 1.0),
    'show_text_tm': (1.0, 300.0),
    'text_opacity': (0.0, 1.0),
    'slide_progress_font_size': (5, 50),
    'cache_progress_font_size': (5, 50),
    'clock_opacity': (0.0, 1.0),
    'menu_autohide_tm': (0.0, 60.0),
    'rclone_sync_interval': (1, 72),
}

CHOICES = {
    'blend_type': ['blend', 'burn', 'bump'],
    'text_justify': ['L', 'C', 'R'],
    'clock_justify': ['L', 'C', 'R'],
    'clock_top_bottom': ['T', 'B'],
    'slide_progress_position': ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center'],
    'cache_progress_position': ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center'],
    'input_type': ['keyboard', 'touch', 'mouse', None],
    'display_power': [0, 1, 2],
    'sort_cols': ['fname ASC', 'fname DESC', 'last_modified ASC', 'last_modified DESC', 'exif_datetime ASC', 'exif_datetime DESC', 'rating DESC', 'rating ASC'],
    'true_tone_adjust': ["none", "warm", "cool", "auto"],
    'sound_profile': ["none", "acoustic", "lofi", "nature", "ambient"]
}

FRIENDLY_NAMES = {
    "viewer.fit": "Fit Image to Screen (No Crop)",
    "viewer.video_fit_display": "Stretch Video to Fit Screen",
    "viewer.blur_amount": "Background Blur Intensity",
    "viewer.blur_zoom": "Background Blur Zoom",
    "viewer.blur_edges": "Blur Edges",
    "viewer.edge_alpha": "Background Edge Alpha",
    "viewer.fps": "Display Framerate (FPS)",
    "viewer.kenburns": "Enable Ken Burns Panning",
    "viewer.display_power": "Display Power Mode (0/1/2)",
    "viewer.use_glx": "Use GLX Engine (X11)",
    "viewer.use_sdl2": "Use SDL2 Visual Engine",
    "viewer.blend_type": "Image Transition Type",
    "viewer.background": "Background Color RGBA Array",

    "viewer.show_text": "Metadata Tags to Show",
    "viewer.show_text_fm": "Caption Date Format",
    "viewer.show_text_tm": "Metadata Fade Time (sec)",
    "viewer.show_text_sz": "Metadata Text Size",
    "viewer.text_justify": "Metadata Alignment (L/C/R)",
    "viewer.text_x_margin": "Text X-Margin Horizontal",
    "viewer.text_y_margin": "Text Y-Margin Vertical",
    "viewer.text_opacity": "Text Visual Opacity",
    "viewer.text_bkg_hgt": "Text Background Darkbox Height",
    "viewer.text_line_spacing": "Text Line Spacing",
    "viewer.video_volume": "Video Player Volume Limit",

    "viewer.show_clock": "Show Floating Clock Display",
    "viewer.clock_justify": "Clock Alignment (L/C/R)",
    "viewer.clock_text_sz": "Clock Text Size",
    "viewer.clock_format": "Clock Date Format",
    "viewer.clock_opacity": "Clock Visual Opacity",
    "viewer.clock_top_bottom": "Clock Position (Top/Bottom)",
    "viewer.clock_wdt_offset_pct": "Clock X-Offset Width %",
    "viewer.clock_hgt_offset_pct": "Clock Y-Offset Height %",

    "viewer.mat_images": "Auto-Mat Images Mode",
    "viewer.mat_type": "Allowed Mat Texture Styles",
    "viewer.outer_mat_color": "Outer Mat Color Array",
    "viewer.inner_mat_color": "Inner Mat Color Array",
    "viewer.outer_mat_border": "Outer Mat Border Width",
    "viewer.inner_mat_border": "Inner Mat Border Width",
    "viewer.outer_mat_use_texture": "Use Outer Mat Texture Pattern",
    "viewer.inner_mat_use_texture": "Use Inner Mat Texture Pattern",
    "viewer.mat_resource_folder": "Mat Textures Source Folder",

    "viewer.menu_text_sz": "Main Menu View Text Size",
    "viewer.menu_autohide_tm": "Menu Autohide Duration",
    "viewer.slide_progress_show": "Show Slide Progress Text",
    "viewer.slide_progress_font_size": "Slide Progress Text Size",
    "viewer.slide_progress_position": "Slide Progress Screen Pos",
    "viewer.slide_progress_x_offset": "Slide Progress X-Offset",
    "viewer.slide_progress_y_offset": "Slide Progress Y-Offset",
    "viewer.show_cache_indicator": "Show Bootup Cache Status",
    "viewer.cache_progress_position": "Cache Indicator Screen Pos",
    "viewer.cache_progress_x_offset": "Cache Indicator X-Offset",
    "viewer.cache_progress_y_offset": "Cache Indicator Y-Offset",
    "viewer.cache_progress_font_size": "Cache Indicator Text Size",
    "viewer.cache_progress_text_width": "Cache Indicator Limit Width",

    "model.pic_dir": "Media Source Folder Path",
    "model.deleted_pictures": "Safe Trash Folder Repository",
    "model.subdirectory": "Subdirectory Targeted Filter",
    "model.follow_links": "Follow Deep Folder Symlinks",
    "model.no_files_img": "No Photos Available Display IMG",
    "model.location_filter": "Include Location Keywords",
    "model.tags_filter": "Include Metadata Photo Tags",
    "model.load_geoloc": "Enable Deep Reverse Location",
    "model.geo_key": "Map API Key (Needs Email)",
    "model.locale": "Raspberry Pi Locale Standard",
    "viewer.geo_suppress_list": "Location Ignored Keyword Array",

    "model.time_delay": "Photo Slide Duration Time",
    "model.fade_time": "Transition Bleed Fade Time",
    "model.shuffle": "Shuffle Default Playing Order",
    "model.recent_n": "Prioritize Newer Photos (< Days)",
    "model.reshuffle_num": "Cycles Allowed Before Shuffle",
    "model.update_interval": "Folder Activity Polish Interval",
    "model.sort_cols": "SQLite Internal Sorting Order",
    "model.portrait_pairs": "Pair Portrait Photos Together",

    "viewer.enable_date_filter": "Filter by Exact Anniversary",
    "viewer.date_range_days": "Anniversary Days Limit Window",
    "viewer.enable_smart_cache": "Strict Smart Cache File Rule",
    "viewer.cache_start_min_files": "Min Base Files To Open Render",
    "viewer.cache_refresh_timezone": "Midnight Auto Refresh Timezone",

    "peripherals.input_type": "Primary Hardware IO Controller",
    "peripherals.buttons.pause.enable": "Enable External Fast Pause",
    "peripherals.buttons.pause.shortcut": "Fast Pause Keystroke Shortcut",
    "peripherals.buttons.display_off.enable": "Enable Display Kill UI Toggle",
    "peripherals.buttons.display_off.shortcut": "Display Kill Shortcut Bind",
    "peripherals.buttons.location.enable": "Enable Location UI Toggle",
    "peripherals.buttons.location.shortcut": "Location Shortcut Bind",
    "peripherals.buttons.exit.enable": "Enable Application Quit Core",
    "peripherals.buttons.power_down.enable": "Enable Hardware Shutdown Bind",

    "mqtt.use_mqtt": "Enable External Home Assistant",
    "mqtt.server": "MQTT Broker Server Address IP",
    "mqtt.port": "MQTT Active Server Port",
    "mqtt.login": "MQTT Secured Username",
    "mqtt.password": "MQTT Secured Password",
    "mqtt.device_id": "Device Display Broadcaster Name",
    "mqtt.tls": "MQTT TSL Encryption Rule",
    "mqtt.device_url": "Device URL HTTP Override",

    "http.use_http": "Enable Phone Remote UI Access",
    "http.path": "Static Web View Folder Path",
    "http.port": "Web App Listening Port (9000)",
    "http.auth": "Require Web Login Password",
    "http.username": "Web Server Admin Login Core",
    "http.use_ssl": "Enforce SSL Browser Security",
    "http.password": "Web Server Encrypted Password",
    "http.keyfile": "SSL Encryption Keyfile Dir",
    "http.certfile": "SSL External Cert Validation",

    "ai.semantic_tagging_enable": "Run Semantic Target Auto-Tagging",
    "ai.face_aware_kenburns": "Detect Faces for Ken-Burns Panning",
    "ambient.pir_sensor_pin": "PIR Hardware Motion GPIO Pin",
    "ambient.true_tone_adjust": "Ambient True-Tone Adjustment",
    "dashboard.weather_overlay_enable": "Overlay Dynamic System Weather",
    "dashboard.weather_location": "City, State / Zip Code for Weather",
    "dashboard.daily_recap_mode": "Daily Nostalgia Anniversary Routine",
    "cloud.rclone_sync_enable": "Sync Files via Rclone Network",
    "cloud.rclone_remote_name": "Rclone Cloud Provider API Name",
    "cloud.rclone_sync_interval": "Cloud Downloader Background Hours",
    "sound.soundscapes_enable": "Enable Live Background Audio Sets",
    "sound.sound_profile": "Background DJ Sound Profile"
}

MENU_STRUCTURE = {
    "Display & Visuals": [
        "viewer.fit", "viewer.video_fit_display", "viewer.blur_amount",
        "viewer.blur_zoom", "viewer.blur_edges", "viewer.edge_alpha",
        "viewer.fps", "viewer.kenburns", "viewer.display_power",
        "viewer.use_glx", "viewer.use_sdl2", "viewer.blend_type", "viewer.background"
    ],
    "Overlays: Text & Files": [
        "viewer.show_text", "viewer.show_text_fm", "viewer.show_text_tm",
        "viewer.show_text_sz", "viewer.text_justify", "viewer.text_x_margin",
        "viewer.text_y_margin", "viewer.text_opacity", "viewer.text_bkg_hgt",
        "viewer.text_line_spacing", "viewer.video_volume"
    ],
    "Overlays: Clock": [
        "viewer.show_clock", "viewer.clock_justify", "viewer.clock_text_sz",
        "viewer.clock_format", "viewer.clock_opacity", "viewer.clock_top_bottom",
        "viewer.clock_wdt_offset_pct", "viewer.clock_hgt_offset_pct"
    ],
    "Matting & Borders": [
        "viewer.mat_images", "viewer.mat_type", "viewer.outer_mat_color",
        "viewer.inner_mat_color", "viewer.outer_mat_border", "viewer.inner_mat_border",
        "viewer.outer_mat_use_texture", "viewer.inner_mat_use_texture",
        "viewer.mat_resource_folder"
    ],
    "UI Elements & Menus": [
        "viewer.menu_text_sz", "viewer.menu_autohide_tm", "viewer.slide_progress_show",
        "viewer.slide_progress_font_size", "viewer.slide_progress_position",
        "viewer.slide_progress_x_offset", "viewer.slide_progress_y_offset",
        "viewer.show_cache_indicator", "viewer.cache_progress_position",
        "viewer.cache_progress_x_offset", "viewer.cache_progress_y_offset",
        "viewer.cache_progress_font_size", "viewer.cache_progress_text_width"
    ],
    "Directory, GPS & Filter": [
        "model.pic_dir", "model.deleted_pictures", "model.subdirectory",
        "model.follow_links", "model.no_files_img", "model.location_filter",
        "model.tags_filter", "model.load_geoloc", "model.geo_key", "model.locale",
        "viewer.geo_suppress_list"
    ],
    "Timings & Shuffle Algorithm": [
        "model.time_delay", "model.fade_time", "model.shuffle", "model.recent_n",
        "model.reshuffle_num", "model.update_interval", "model.sort_cols",
        "model.portrait_pairs"
    ],
    "Date & Cache Window": [
        "viewer.enable_date_filter", "viewer.date_range_days",
        "viewer.enable_smart_cache", "viewer.cache_start_min_files",
        "viewer.cache_refresh_timezone"
    ],
    "Peripherals & Controls": [
        "peripherals.input_type", "peripherals.buttons.pause.enable",
        "peripherals.buttons.pause.shortcut", "peripherals.buttons.display_off.enable",
        "peripherals.buttons.display_off.shortcut", "peripherals.buttons.location.enable",
        "peripherals.buttons.location.shortcut", "peripherals.buttons.exit.enable",
        "peripherals.buttons.power_down.enable"
    ],
    "MQTT Configuration": [
        "mqtt.use_mqtt", "mqtt.server", "mqtt.port", "mqtt.login",
        "mqtt.password", "mqtt.device_id", "mqtt.tls", "mqtt.device_url"
    ],
    "HTTP Configuration": [
        "http.use_http", "http.path", "http.port", "http.auth",
        "http.username", "http.use_ssl", "http.password", "http.keyfile", "http.certfile"
    ],
    "AI & Ambient Intelligence": [
        "ai.semantic_tagging_enable", "ai.face_aware_kenburns",
        "ambient.pir_sensor_pin", "ambient.true_tone_adjust"
    ],
    "Cloud Sync & Dashboards": [
        "dashboard.weather_overlay_enable", "dashboard.weather_location", "dashboard.daily_recap_mode",
        "cloud.rclone_sync_enable", "cloud.rclone_remote_name", "cloud.rclone_sync_interval"
    ],
    "Audio Soundscapes": [
        "sound.soundscapes_enable", "sound.sound_profile"
    ]
}

def get_config_path():
    for p in CONFIG_PATHS:
        if os.path.exists(p):
            return p
    return None

def update_yaml_field(yaml_text, keys_path, new_val):
    lines = yaml_text.split('\n')
    current_path = []
    current_indent_levels = []
    
    for i, line in enumerate(lines):
        if line.strip().startswith('#'): continue # skip full comment lines
        
        match = re.match(r'^(\s*)([a-zA-Z0-9_]+)\s*:(.*)', line)
        if match:
            indent_str = match.group(1)
            key = match.group(2)
            rest = match.group(3)
            indent_len = len(indent_str)
            
            while current_indent_levels and current_indent_levels[-1] >= indent_len:
                current_indent_levels.pop()
                current_path.pop()
                
            current_indent_levels.append(indent_len)
            current_path.append(key)
            
            if current_path == keys_path:
                parts = rest.split('#', 1)
                comment = ' #' + parts[1] if len(parts) > 1 else ''
                
                if isinstance(new_val, bool):
                    v_str = 'True' if new_val else 'False'
                elif new_val is None:
                    v_str = 'null'
                elif isinstance(new_val, (int, float)):
                    v_str = str(new_val)
                elif isinstance(new_val, str):
                    if new_val == "" or new_val.lower() in ("null", "none"):
                        v_str = '""' if new_val == "" else new_val
                    else:
                        v_str = f'"{new_val}"' if not new_val.startswith('[') else str(new_val)
                else:
                    v_str = str(new_val)
                    
                lines[i] = f"{indent_str}{key}: {v_str}{comment}"
                return '\n'.join(lines)
    return yaml_text

def flatten_keys(d, parent_key=[]):
    items = []
    for k, v in d.items():
        new_key = parent_key + [k]
        if isinstance(v, dict):
            items.extend(flatten_keys(v, new_key))
        else:
            items.append((new_key, v))
    return items

def get_nested_val(d, keys):
    val = d
    for k in keys:
        if isinstance(val, dict) and k in val:
            val = val[k]
        else:
            return None
    return val

def set_nested_val(d, keys, val):
    for key in keys[:-1]:
        d = d[key]
    d[keys[-1]] = val

class App:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        # Keypad intercepts Raw UART Escape Sequences preventing OB/crash
        self.stdscr.keypad(True)
        curses.curs_set(0)
        
        # Premium Aesthetic Colors Overhaul
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)    # Selected Highlight
        curses.init_pair(2, curses.COLOR_GREEN, -1)                   # UI Widget Colors
        curses.init_pair(3, curses.COLOR_CYAN, -1)                    # Header Titles
        curses.init_pair(4, curses.COLOR_RED, -1)                     # Warnings / Errors
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_WHITE)   # Footer / Status Bars
        
        self.stdscr.timeout(100)
        
        self.path = get_config_path()
        if not self.path:
            self.draw_message("Could not find configuration.yaml.", wait=True)
            sys.exit(1)
            
        with open(self.path, 'r') as f:
            self.yaml_text = f.read()
            
        self.data = yaml.safe_load(self.yaml_text)
        self.original_data = copy.deepcopy(self.data)
        
        self.build_categories()
        
        self.current_section = None
        self.current_idx = 0
        self.scroll_top = 0
        self.unsaved_changes = False

    def build_categories(self):
        self.categories = copy.deepcopy(MENU_STRUCTURE)
        mapped_keys = set()
        for cats in self.categories.values():
            mapped_keys.update(cats)
            
        flat_all = flatten_keys(self.data, [])
        unmapped = []
        for keys_path, v in flat_all:
            k_str = ".".join(keys_path)
            if k_str not in mapped_keys and not isinstance(v, list):
                unmapped.append(k_str)
                
        if unmapped:
            self.categories["All Unmapped Options"] = sorted(unmapped)
            
        self.sections = list(self.categories.keys())
        
    def draw_message(self, msg, wait=False):
        self.stdscr.clear()
        h, w = self.stdscr.getmaxyx()
        self.stdscr.addstr(h//2, max(0, w//2 - len(msg)//2), msg[:w-1])
        self.stdscr.refresh()
        if wait:
            self.stdscr.timeout(-1)
            self.stdscr.getch()
            self.stdscr.timeout(100)
            
    def get_string_input(self, prompt, initial=""):
        curses.curs_set(1)
        h, w = self.stdscr.getmaxyx()
        self.stdscr.move(h-2, 0)
        self.stdscr.clrtoeol()
        self.stdscr.addstr(h-2, 0, f" {prompt}: ")
        
        input_win = curses.newwin(1, w - len(prompt) - 4, h-2, len(prompt) + 4)
        input_win.keypad(True)
        
        text = str(initial)
        pos = len(text)
        
        while True:
            input_win.clear()
            input_win.addstr(0, 0, text)
            input_win.move(0, pos)
            input_win.refresh()
            
            c = input_win.getch()
            if c in (10, 13):
                break
            elif c == 27: # ESC
                text = initial
                break
            elif c in (curses.KEY_BACKSPACE, 127, 8):
                if pos > 0:
                    text = text[:pos-1] + text[pos:]
                    pos -= 1
            elif c == curses.KEY_DC:
                if pos < len(text):
                    text = text[:pos] + text[pos+1:]
            elif c == curses.KEY_LEFT:
                pos = max(0, pos - 1)
            elif c == curses.KEY_RIGHT:
                pos = min(len(text), pos + 1)
            elif 32 <= c <= 126:
                text = text[:pos] + chr(c) + text[pos:]
                pos += 1
                
        curses.curs_set(0)
        return text

    def get_number_input(self, prompt, initial=""):
        val = self.get_string_input(prompt, str(initial))
        try:
            return float(val) if '.' in str(initial) else int(val)
        except ValueError:
            return initial

    def prompt_save(self):
        curses.curs_set(0)
        h, w = self.stdscr.getmaxyx()
        win = curses.newwin(5, 50, max(0, h//2 - 2), max(0, w//2 - 25))
        win.box()
        win.addstr(1, 2, "You have unsaved changes.", curses.color_pair(4) | curses.A_BOLD)
        win.addstr(3, 2, "(S)ave  (D)iscard  (C)ancel")
        win.refresh()
        while True:
            c = win.getch()
            if c in (ord('s'), ord('S')):
                self.save_changes()
                return True
            elif c in (ord('d'), ord('D')):
                self.data = copy.deepcopy(self.original_data)
                self.unsaved_changes = False
                return True
            elif c in (ord('c'), ord('C'), 27):
                return False

    def check_unsaved(self):
        return self.data != self.original_data

    def save_changes(self):
        flat_items = flatten_keys(self.data, [])
        orig_items = dict(flatten_keys(self.original_data, []))
        
        for keys_path, v in flat_items:
            orig_v = orig_items.get(tuple(keys_path))
            if orig_v != v:
                self.yaml_text = update_yaml_field(self.yaml_text, keys_path, v)
        
        with open(self.path, 'w') as f:
            f.write(self.yaml_text)
        self.original_data = copy.deepcopy(self.data)
        self.unsaved_changes = False
        self.draw_message("Changes saved successfully!", wait=True)

    def draw_footer_bar(self, h, w, status_text):
        # Draw status info
        self.stdscr.addstr(h-2, 0, (" " * w)[:w-1], curses.color_pair(5))
        self.stdscr.addstr(h-2, 2, status_text[:w-4], curses.color_pair(5))
        
        # Draw standard keybinds
        if self.current_section is None:
            self.stdscr.addstr(h-1, 0, " [UP/DOWN] Move Menu   [ENTER] Select Category   [S] Save All   [Q/ESC] Quit ".ljust(w)[:w-1])
        else:
            self.stdscr.addstr(h-1, 0, " [UP/DOWN] Move List   [LEFT/RIGHT] Adjust Widget   [ENTER] Force Edit   [R] Revert Option   [B/ESC] Back ".ljust(w)[:w-1])

    def run(self):
        while True:
            try:
                self.unsaved_changes = self.check_unsaved()
                h, w = self.stdscr.getmaxyx()
                self.stdscr.erase()
                
                title = f" Picframe Configuration Extender "
                self.stdscr.addstr(0, max(0, w//2 - len(title)//2), title[:w-1], curses.color_pair(3) | curses.A_BOLD)
                
                if self.unsaved_changes:
                    self.stdscr.addstr(0, 2, "[ * UNSAVED * ]", curses.color_pair(4) | curses.A_BOLD)
                
                if self.current_section is None:
                    self.stdscr.addstr(2, 2, "MAIN MENU GROUPS", curses.color_pair(3) | curses.A_BOLD)
                    
                    max_display = h - 6
                    self.scroll_top = max(0, min(self.scroll_top, self.current_idx))
                    if self.current_idx >= self.scroll_top + max_display:
                        self.scroll_top = self.current_idx - max_display + 1
                        
                    for i in range(self.scroll_top, min(len(self.sections), self.scroll_top + max_display)):
                        sec = self.sections[i]
                        attr = curses.color_pair(1) if i == self.current_idx else curses.A_NORMAL
                        self.stdscr.addstr(4 + (i - self.scroll_top), 4, f"{'> ' if i == self.current_idx else '  '}{sec.upper()}", attr)
                        
                    self.draw_footer_bar(h, w, f" Editing Root: {self.path} ")
                    
                    c = self.stdscr.getch()
                    if c == curses.KEY_UP:
                        self.current_idx = max(0, self.current_idx - 1)
                    elif c == curses.KEY_DOWN:
                        self.current_idx = min(len(self.sections) - 1, self.current_idx + 1)
                    elif c in (10, 13):
                        self.current_section = self.sections[self.current_idx]
                        self.current_idx = 0
                        self.scroll_top = 0
                    elif c in (ord('s'), ord('S')):
                        if self.unsaved_changes:
                            self.save_changes()
                    elif c in (ord('q'), ord('Q'), 27): # Q or ESC
                        if self.unsaved_changes:
                            if self.prompt_save():
                                break
                        else:
                            break
                    elif c == curses.KEY_RESIZE:
                        pass
                else:
                    keys_list = self.categories[self.current_section]
                    items = []
                    for k_str in keys_list:
                        keys_path = k_str.split('.')
                        v = get_nested_val(self.data, keys_path)
                        if v is not None and not isinstance(v, list):
                            items.append((keys_path, v))
                    
                    self.stdscr.addstr(2, 2, f"SECTION: {self.current_section.upper()}", curses.color_pair(3) | curses.A_BOLD)
                    
                    max_display = h - 7
                    self.scroll_top = max(0, min(self.scroll_top, self.current_idx))
                    if self.current_idx >= self.scroll_top + max_display:
                        self.scroll_top = self.current_idx - max_display + 1
                        
                    if self.scroll_top > 0:
                        self.stdscr.addstr(3, max(0, w//2 - 9), " ▲ MORE OPTIONS ABOVE ▲ ", curses.color_pair(3))
                        
                    active_status = "No option selected."
                        
                    for i in range(self.scroll_top, min(len(items), self.scroll_top + max_display)):
                        keys_path, v = items[i]
                        k = ".".join(keys_path)
                        is_sel = (i == self.current_idx)
                        attr = curses.color_pair(1) if is_sel else curses.A_NORMAL
                        
                        leaf_k = keys_path[-1]
                        friendly = FRIENDLY_NAMES.get(k, k.split('.')[-1].replace('_',' ').title())
                        
                        # Process Status Bar extraction for highlighted item
                        if is_sel:
                            if leaf_k in CHOICES:
                                bounds = f"Choices: {len(CHOICES[leaf_k])} variations (Switch with LEFT/RIGHT)"
                            elif leaf_k in SLIDERS:
                                bounds = f"Slider Min {SLIDERS[leaf_k][0]} to Max {SLIDERS[leaf_k][1]}"
                            elif isinstance(v, bool):
                                bounds = "Boolean Option (Toggle with SPACE or LEFT/RIGHT)"
                            else:
                                bounds = "Raw Text / Numerical Field (Force edit with ENTER key)"
                                
                            has_changed = v != get_nested_val(self.original_data, keys_path)
                            mod_mark = "[MODIFIED] " if has_changed else ""
                            active_status = f"{mod_mark}YAML Node: [{k}]  |  {bounds}"
                        
                        disp_color = curses.color_pair(2) if not is_sel else curses.color_pair(1)
                        self.stdscr.addstr(4 + (i - self.scroll_top), 2, f"{'> ' if is_sel else '  '}{friendly:<36} | ", attr)
                        
                        if leaf_k in CHOICES:
                            opts = CHOICES[leaf_k]
                            try:
                                valstr = str(v) if v is not None else "None"
                                if len(valstr) > 17:
                                    valstr = valstr[:14] + "..."
                                self.stdscr.addstr(f"< {valstr:^17} >"[:w-42], disp_color)
                            except:
                                self.stdscr.addstr(f"{v}"[:w-42], attr)
                        elif leaf_k in SLIDERS and isinstance(v, (int, float)):
                            smin, smax = SLIDERS[leaf_k]
                            smin, smax = float(smin), float(smax)
                            try:
                                v_num = float(v)
                                valstr = f"{v:>5.1f}" if isinstance(v, float) else f"{v:>5d}"
                                pct = max(0.0, min(1.0, (v_num - smin) / float(abs(smax - smin))))
                                bar_len = 15
                                filled = int(pct * bar_len)
                                bar = "=" * filled + "-" * (bar_len - filled)
                                self.stdscr.addstr(f"[{bar}] ", disp_color)
                                self.stdscr.addstr(f"{valstr}", attr)
                            except:
                                self.stdscr.addstr(f"{v}"[:w-42], attr)
                        elif isinstance(v, bool):
                            self.stdscr.addstr(f"[", disp_color)
                            self.stdscr.addstr(f"{'X' if v else ' '}", curses.A_BOLD if is_sel else attr)
                            self.stdscr.addstr(f"]", disp_color)
                        else:
                            valstr = str(v)
                            if len(valstr) > w - 46:
                                valstr = valstr[:w-49] + "..."
                            self.stdscr.addstr(f"{valstr}", attr)
                            
                    if self.scroll_top + max_display < len(items):
                        self.stdscr.addstr(4 + max_display, max(0, w//2 - 9), " ▼ MORE OPTIONS BELOW ▼ ", curses.color_pair(3))
                        
                    self.draw_footer_bar(h, w, active_status)
                    
                    c = self.stdscr.getch()
                    if c == curses.KEY_UP:
                        self.current_idx = max(0, self.current_idx - 1)
                    elif c == curses.KEY_DOWN:
                        self.current_idx = min(len(items) - 1, self.current_idx + 1)
                    elif c in (27, ord('b'), ord('B')): # ESC
                        self.current_section = None
                        self.current_idx = 0
                    elif c in (ord('r'), ord('R')) and len(items) > 0:
                        keys_path, v = items[self.current_idx]
                        orig_v = get_nested_val(self.original_data, keys_path)
                        if orig_v is not None:
                            set_nested_val(self.data, keys_path, orig_v)
                    elif c in (curses.KEY_LEFT, curses.KEY_RIGHT, 10, 13, ord(' ')) and len(items) > 0:
                        keys_path, v = items[self.current_idx]
                        leaf_k = keys_path[-1]
                        
                        if leaf_k in CHOICES and c in (curses.KEY_LEFT, curses.KEY_RIGHT):
                            opts = CHOICES[leaf_k]
                            try:
                                c_idx = opts.index(v)
                            except ValueError:
                                c_idx = 0
                                
                            if c == curses.KEY_LEFT:
                                next_idx = (c_idx - 1) % len(opts)
                            else:
                                next_idx = (c_idx + 1) % len(opts)
                                
                            set_nested_val(self.data, keys_path, opts[next_idx])
                            
                        elif isinstance(v, bool) and c in (10, 13, 32, curses.KEY_LEFT, curses.KEY_RIGHT):
                            set_nested_val(self.data, keys_path, not v)
                            
                        elif leaf_k in SLIDERS and isinstance(v, (int, float)) and c in (curses.KEY_LEFT, curses.KEY_RIGHT):
                            smin, smax = SLIDERS[leaf_k]
                            step = (smax - smin) / 50.0
                            if isinstance(v, int): step = max(1, int(step))
                            if c == curses.KEY_LEFT:
                                new_val = max(smin, v - step)
                            else:
                                new_val = min(smax, v + step)
                            if isinstance(v, int): new_val = int(new_val)
                            set_nested_val(self.data, keys_path, new_val)
                                
                        elif c in (10, 13): # ENTER forcing manual intervention
                            active_friendly = FRIENDLY_NAMES.get(".".join(keys_path), leaf_k)
                            if isinstance(v, (int, float)):
                                new_v = self.get_number_input(f"Enter exact value for {active_friendly}", v)
                                if leaf_k in SLIDERS:
                                    smin, smax = SLIDERS[leaf_k]
                                    new_v = max(smin, min(smax, new_v))
                                set_nested_val(self.data, keys_path, new_v)
                            else:
                                new_v = self.get_string_input(f"Enter new text for {active_friendly}", v)
                                set_nested_val(self.data, keys_path, new_v)

            except curses.error:
                # Bypass KEY_RESIZE or other native screen shifting faults natively smoothly
                pass

def main():
    try:
        curses.wrapper(lambda stdscr: App(stdscr).run())
    except KeyboardInterrupt:
        pass

if __name__ == '__main__':
    main()
