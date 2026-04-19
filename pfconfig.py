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
    'blur_zoom': (1.0, 5.0),
    'cache_progress_font_size': (5, 50),
    'cache_progress_text_width': (50, 1200),
    'cache_progress_x_offset': (0, 500),
    'cache_progress_y_offset': (0, 500),
    'clock_hgt_offset_pct': (1.0, 10.0),
    'clock_opacity': (0.0, 1.0),
    'clock_text_sz': (10, 200),
    'clock_wdt_offset_pct': (1.0, 10.0),
    'date_range_days': (1, 365),
    'edge_alpha': (0.0, 1.0),
    'fade_time': (1.0, 30.0),
    'fps': (1, 60),
    'inner_mat_border': (0, 200),
    'menu_autohide_tm': (0.0, 60.0),
    'menu_text_sz': (10, 100),
    'outer_mat_border': (0, 200),
    'recent_n': (0, 90),
    'reshuffle_num': (1, 10),
    'show_text_sz': (10, 100),
    'show_text_tm': (1.0, 300.0),
    'slide_progress_font_size': (5, 50),
    'slide_progress_x_offset': (0, 500),
    'slide_progress_y_offset': (0, 500),
    'text_line_spacing': (0.8, 3.0),
    'text_opacity': (0.0, 1.0),
    'text_x_margin': (0, 500),
    'text_x_position': (0, 4000),
    'text_y_margin': (0, 500),
    'text_y_position': (0, 4000),
    'time_delay': (1, 600),
    'update_interval': (1.0, 30.0),
    'video_every_n_photos': (1, 200),
    'video_volume': (0, 100),
}

CHOICES = {
    'blend_type': ['blend', 'burn', 'bump'],
    'cache_progress_position': ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center'],
    'clock_justify': ['L', 'C', 'R'],
    'clock_top_bottom': ['T', 'B'],
    'display_power': [0, 1, 2],
    'input_type': ['keyboard', 'touch', 'mouse', None],
    'slide_progress_position': ['top-left', 'top-right', 'bottom-left', 'bottom-right', 'top-center', 'bottom-center'],
    'sort_cols': ['fname ASC', 'fname DESC', 'last_modified ASC', 'last_modified DESC', 'exif_datetime ASC', 'exif_datetime DESC', 'rating DESC', 'rating ASC'],
    'text_justify': ['L', 'C', 'R'],
    'text_position_mode': ['margin', 'absolute'],
}

FRIENDLY_NAMES = {
    "http.auth": "Enable HTTP Basic Auth",
    "http.certfile": "SSL Certificate Path",
    "http.keyfile": "SSL Private Key Path",
    "http.password": "HTTP Basic Auth Password",
    "http.path": "HTTP Static Content Path",
    "http.port": "HTTP Server Port",
    "http.use_http": "Enable HTTP Server",
    "http.use_ssl": "Enable HTTPS",
    "http.username": "HTTP Basic Auth Username",

    "model.deleted_pictures": "Deleted Media Folder",
    "model.fade_time": "Fade Time (sec)",
    "model.follow_links": "Follow Symlinked Folders",
    "model.geo_key": "Geo Lookup Key",
    "model.load_geoloc": "Enable Geo Reverse Lookup",
    "model.locale": "Locale",
    "model.location_filter": "Location Filter",
    "model.no_files_img": "No Files Placeholder Image",
    "model.pic_dir": "Media Root Folder",
    "model.portrait_pairs": "Enable Portrait Pairing",
    "model.recent_n": "Recent-First Window (days)",
    "model.reshuffle_num": "Reshuffle Every N Runs",
    "model.shuffle": "Shuffle Playlist",
    "model.sort_cols": "Sort Order",
    "model.subdirectory": "Subdirectory Filter",
    "model.tags_filter": "Tags Filter",
    "model.time_delay": "Slide Time Delay (sec)",
    "model.update_interval": "Cache Update Interval (sec)",

    "mqtt.device_id": "MQTT Device ID",
    "mqtt.device_url": "MQTT Device URL",
    "mqtt.login": "MQTT Username",
    "mqtt.password": "MQTT Password",
    "mqtt.port": "MQTT Port",
    "mqtt.server": "MQTT Server",
    "mqtt.tls": "MQTT TLS CA Path",
    "mqtt.use_mqtt": "Enable MQTT",

    "updater.auto_update_on_start": "Auto Update On Start",
    "updater.git_branch": "Update Git Branch",
    "updater.git_remote": "Update Git Remote",
    "updater.repo_dir": "Update Repository Path",
    "updater.restart_after_update": "Restart After Update",

    "peripherals.buttons.display_off.enable": "Enable Display Off Button",
    "peripherals.buttons.display_off.shortcut": "Display Off Shortcut",
    "peripherals.buttons.exit.enable": "Enable Exit Button",
    "peripherals.buttons.location.enable": "Enable Location Button",
    "peripherals.buttons.location.shortcut": "Location Shortcut",
    "peripherals.buttons.pause.enable": "Enable Pause Button",
    "peripherals.buttons.pause.shortcut": "Pause Shortcut",
    "peripherals.buttons.power_down.enable": "Enable Power Down Button",
    "peripherals.input_type": "Input Device Type",

    "viewer.background": "Background RGBA",
    "viewer.blend_type": "Transition Blend Type",
    "viewer.blur_amount": "Background Blur Amount",
    "viewer.blur_edges": "Blur Edges",
    "viewer.blur_zoom": "Blur Zoom",
    "viewer.cache_progress_font_size": "Cache Progress Font Size",
    "viewer.cache_progress_position": "Cache Progress Position",
    "viewer.cache_progress_text_width": "Cache Progress Text Width",
    "viewer.cache_progress_x_offset": "Cache Progress X Offset",
    "viewer.cache_progress_y_offset": "Cache Progress Y Offset",
    "viewer.cache_refresh_timezone": "Cache Refresh Timezone",
    "viewer.cache_start_min_files": "Cache Start Min Files",
    "viewer.clock_format": "Clock Format",
    "viewer.clock_hgt_offset_pct": "Clock Vertical Offset %",
    "viewer.clock_justify": "Clock Justify",
    "viewer.clock_opacity": "Clock Opacity",
    "viewer.clock_text_sz": "Clock Text Size",
    "viewer.clock_top_bottom": "Clock Top/Bottom",
    "viewer.clock_wdt_offset_pct": "Clock Horizontal Offset %",
    "viewer.date_range_days": "Date Filter Window (days)",
    "viewer.display_hdmi": "Display Output Name",
    "viewer.display_power": "Display Power Mode",
    "viewer.edge_alpha": "Edge Alpha",
    "viewer.enable_date_filter": "Enable Date Filter",
    "viewer.enable_smart_cache": "Enable Smart Cache",
    "viewer.fit": "Fit Image to Display",
    "viewer.fps": "Framerate (FPS)",
    "viewer.geo_suppress_list": "Geo Suppress List",
    "viewer.inner_mat_border": "Inner Mat Border",
    "viewer.inner_mat_color": "Inner Mat Color",
    "viewer.inner_mat_use_texture": "Use Inner Mat Texture",
    "viewer.kenburns": "Enable Ken Burns",
    "viewer.mat_images": "Auto Mat Images",
    "viewer.mat_resource_folder": "Mat Resource Folder",
    "viewer.mat_type": "Mat Type Filter",
    "viewer.menu_autohide_tm": "Menu Auto-Hide (sec)",
    "viewer.menu_text_sz": "Menu Text Size",
    "viewer.outer_mat_border": "Outer Mat Border",
    "viewer.outer_mat_color": "Outer Mat Color",
    "viewer.outer_mat_use_texture": "Use Outer Mat Texture",
    "viewer.show_cache_indicator": "Show Cache Indicator",
    "viewer.show_clock": "Show Clock",
    "viewer.show_text": "Text Fields To Show",
    "viewer.show_text_fm": "Text Date Format",
    "viewer.show_text_sz": "Text Size",
    "viewer.show_text_tm": "Text Show Time (sec)",
    "viewer.slide_progress_font_size": "Slide Progress Font Size",
    "viewer.slide_progress_position": "Slide Progress Position",
    "viewer.slide_progress_show": "Show Slide Progress",
    "viewer.slide_progress_x_offset": "Slide Progress X Offset",
    "viewer.slide_progress_y_offset": "Slide Progress Y Offset",
    "viewer.text_bkg_hgt": "Text Background Height",
    "viewer.text_justify": "Text Justify",
    "viewer.text_line_spacing": "Text Line Spacing",
    "viewer.text_opacity": "Text Opacity",
    "viewer.text_position_mode": "Text Position Mode",
    "viewer.text_width": "Text Wrap Width",
    "viewer.text_x_margin": "Text X Margin",
    "viewer.text_x_position": "Text X Position",
    "viewer.text_y_margin": "Text Y Margin",
    "viewer.text_y_position": "Text Y Position",
    "viewer.use_glx": "Use GLX",
    "viewer.use_sdl2": "Use SDL2",
    "viewer.video_every_n_photos": "Video Every N Photos",
    "viewer.video_fit_display": "Stretch Video To Display",
    "viewer.video_volume": "Video Volume",
}

MENU_STRUCTURE = {
    "Caching & Date Filtering": [
        "viewer.cache_refresh_timezone",
        "viewer.cache_start_min_files",
        "viewer.date_range_days",
        "viewer.enable_date_filter",
        "viewer.enable_smart_cache",
    ],
    "Display & Rendering": [
        "viewer.background",
        "viewer.blend_type",
        "viewer.blur_amount",
        "viewer.blur_edges",
        "viewer.blur_zoom",
        "viewer.display_hdmi",
        "viewer.display_power",
        "viewer.edge_alpha",
        "viewer.fit",
        "viewer.fps",
        "viewer.kenburns",
        "viewer.use_glx",
        "viewer.use_sdl2",
        "viewer.video_fit_display",
    ],
    "Directories & Filters": [
        "model.deleted_pictures",
        "model.follow_links",
        "model.geo_key",
        "model.load_geoloc",
        "model.locale",
        "model.location_filter",
        "model.no_files_img",
        "model.pic_dir",
        "model.subdirectory",
        "model.tags_filter",
        "viewer.geo_suppress_list",
    ],
    "HTTP": [
        "http.auth",
        "http.certfile",
        "http.keyfile",
        "http.password",
        "http.path",
        "http.port",
        "http.use_http",
        "http.use_ssl",
        "http.username",
    ],
    "Matting": [
        "viewer.inner_mat_border",
        "viewer.inner_mat_color",
        "viewer.inner_mat_use_texture",
        "viewer.mat_images",
        "viewer.mat_resource_folder",
        "viewer.mat_type",
        "viewer.outer_mat_border",
        "viewer.outer_mat_color",
        "viewer.outer_mat_use_texture",
    ],
    "MQTT": [
        "mqtt.device_id",
        "mqtt.device_url",
        "mqtt.login",
        "mqtt.password",
        "mqtt.port",
        "mqtt.server",
        "mqtt.tls",
        "mqtt.use_mqtt",
    ],
    "Peripherals": [
        "peripherals.buttons.display_off.enable",
        "peripherals.buttons.display_off.shortcut",
        "peripherals.buttons.exit.enable",
        "peripherals.buttons.location.enable",
        "peripherals.buttons.location.shortcut",
        "peripherals.buttons.pause.enable",
        "peripherals.buttons.pause.shortcut",
        "peripherals.buttons.power_down.enable",
        "peripherals.input_type",
    ],
    "Updates": [
        "updater.auto_update_on_start",
        "updater.git_branch",
        "updater.git_remote",
        "updater.repo_dir",
        "updater.restart_after_update",
    ],
    "Slideshow Timing": [
        "model.fade_time",
        "model.portrait_pairs",
        "model.recent_n",
        "model.reshuffle_num",
        "model.shuffle",
        "model.sort_cols",
        "model.time_delay",
        "model.update_interval",
        "viewer.video_every_n_photos",
    ],
    "UI Overlays": [
        "viewer.cache_progress_font_size",
        "viewer.cache_progress_position",
        "viewer.cache_progress_text_width",
        "viewer.cache_progress_x_offset",
        "viewer.cache_progress_y_offset",
        "viewer.clock_format",
        "viewer.clock_hgt_offset_pct",
        "viewer.clock_justify",
        "viewer.clock_opacity",
        "viewer.clock_text_sz",
        "viewer.clock_top_bottom",
        "viewer.clock_wdt_offset_pct",
        "viewer.menu_autohide_tm",
        "viewer.menu_text_sz",
        "viewer.show_cache_indicator",
        "viewer.show_clock",
        "viewer.slide_progress_font_size",
        "viewer.slide_progress_position",
        "viewer.slide_progress_show",
        "viewer.slide_progress_x_offset",
        "viewer.slide_progress_y_offset",
        "viewer.show_text",
        "viewer.show_text_fm",
        "viewer.show_text_sz",
        "viewer.show_text_tm",
        "viewer.text_bkg_hgt",
        "viewer.text_justify",
        "viewer.text_line_spacing",
        "viewer.text_opacity",
        "viewer.text_position_mode",
        "viewer.text_width",
        "viewer.text_x_margin",
        "viewer.text_x_position",
        "viewer.text_y_margin",
        "viewer.text_y_position",
        "viewer.video_volume",
    ],
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


def get_option_comment(keys_path, value):
    key_path = ".".join(keys_path)
    leaf_k = keys_path[-1]
    if leaf_k in CHOICES:
        return f"choices: {len(CHOICES[leaf_k])}"
    if leaf_k in SLIDERS:
        smin, smax = SLIDERS[leaf_k]
        return f"range: {smin}..{smax}"
    if isinstance(value, bool):
        return "toggle on/off"
    return f"set {key_path}"

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
        orig_items = {tuple(k): v for k, v in flatten_keys(self.original_data, [])}
        
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

                        option_comment = get_option_comment(keys_path, v)
                        if option_comment:
                            row_y = 4 + (i - self.scroll_top)
                            start_x = max(46, w - 34)
                            comment_width = max(0, w - start_x - 1)
                            if comment_width > 8:
                                comment_text = f" # {option_comment}"
                                if len(comment_text) > comment_width:
                                    comment_text = comment_text[:comment_width - 3] + "..."
                                self.stdscr.addstr(row_y, start_x, comment_text, curses.color_pair(3))
                            
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
