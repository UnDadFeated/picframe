async function getData() {
    const response = await fetch("/?all");
    return response.json();
}

async function getStatus() {
    try {
        const response = await fetch("/?get_cache_status");
        return response.json();
    } catch {
        return {};
    }
}


function getTheme() {
    return localStorage.getItem("picframe-theme") || "dark";
}

function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("picframe-theme", theme);
}

function toggleTheme() {
    setTheme(getTheme() === "dark" ? "light" : "dark");
}


function createSpans() {
    const GROUP_LABELS = {
        playback: "Playback",
        overlays: "Text Overlays",
        filter:   "Filters",
        timing:   "Timing & Display",
        system:   "System"
    };
    const GROUP_ORDER = ["playback", "overlays", "filter", "timing", "system"];

    // Build a map of group → entries
    const groups = {};
    GROUP_ORDER.forEach(g => { groups[g] = []; });
    Object.entries(ids).forEach(([id, el]) => {
        const g = el.group || "system";
        if (!groups[g]) groups[g] = [];
        groups[g].push([id, el]);
    });

    let html = "";
    GROUP_ORDER.forEach(g => {
        if (!groups[g] || groups[g].length === 0) return;
        html += `<div class="ctrl-section">${GROUP_LABELS[g] || g}</div>`;
        html += `<div class="controls-grid">`;
        groups[g].forEach(([id, el]) => {
            const label = el.desc !== undefined ? el.desc : id.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
            const dangerClass = DANGER_IDS.has(id) ? " danger" : "";
            if (el.type === "bool" || el.type === "action") {
                html += `<button class="control-btn${dangerClass}" id="${id}" onclick="toggle('${id}')">${label}</button>`;
            } else {
                html += `<label class="control-field"><span>${label}</span><input id="${id}" placeholder="—"></label>`;
            }
        });
        html += `</div>`;
    });

    const container = document.getElementById("spans");
    container.innerHTML = html;
    container.addEventListener("keyup", e => {
        if (e.keyCode === 13) { e.preventDefault(); uploadValues(); }
    });
}


function isNumeric(num) {
    return (typeof num === "number" || (typeof num === "string" && num.trim() !== "")) && !isNaN(num);
}


function refreshPage() {
    Object.entries(ids).forEach(([id, el]) => {
        const dom = document.getElementById(id);
        if (!dom) return;
        let value = el.val;
        if (isNumeric(value)) {
            value = parseFloat(value);
            if (el.type === "number") {
                if (Math.floor(value) !== value) value = value.toFixed(2);
            } else if (el.type === "date") {
                const d = new Date(value * 1000);
                value = `${d.getFullYear()}/${d.getMonth() + 1}/${d.getDate()}`;
            }
        } else if (el.type === "bool") {
            value = (value === true || value === "true" || value === "True" || value === "ON");
        }
        dom.value = value;
        el.val = value;
        if (el.type === "bool") {
            dom.className = value ? "control-btn active" : "control-btn";
        }
    });
}


function refreshStatus(data) {
    if (!data) return;

    document.getElementById("status-files").textContent = data.file_count ?? "--";

    const loadEl = document.getElementById("status-loading");
    loadEl.textContent = data.loading ? "Yes" : "No";
    loadEl.className = "status-tile-value" + (data.loading ? " active" : "");

    let scanText = "--";
    if (data.scan_total > 0) {
        scanText = `${data.scan_processed || 0}/${data.scan_total}`;
    }
    document.getElementById("status-scan").textContent = scanText;
}


function refreshData() {
    getData().then(ret => {
        let changed = false;
        Object.entries(ret).forEach(([key, val]) => {
            if (key in ids && ids[key].val != val) {
                changed = true;
                ids[key].val = val;
            }
        });
        if (changed) refreshPage();
    });
    getStatus().then(refreshStatus);
}


function flashDot() {
    const dot = document.getElementById("refresh_dot");
    if (!dot) return;
    dot.classList.add("on");
    setTimeout(() => dot.classList.remove("on"), 600);
}


function repeatRefresh() {
    refreshData();
    const img = document.getElementById("preview_img");
    if (img) {
        img.src = `/current_image?t=${Date.now()}`;
        flashDot();
    }
    setTimeout(repeatRefresh, 15000);
}


function uploadValues() {
    let changed = false;
    Object.entries(ids).forEach(([id, el]) => {
        if (el.fn === "setter" && el.type !== "bool") {
            const dom = document.getElementById(id);
            if (dom && dom.value != el.val) {
                el.val = dom.value;
                fetch(`/?${id}=${dom.value}`).then(() => { changed = true; });
            }
        }
    });
    if (changed) setTimeout(refreshData, 300);
}


function toggle(id) {
    const el = ids[id];
    if (el.type === "bool") el.val = !el.val;
    let cmd = `/?${id}=${el.val}`;
    if (el.fn !== "setter") {
        cmd = `/?${el.fn}`.replace("$val", el.val);
    }
    const dom = document.getElementById(id);
    const finalCss = el.type === "bool"
        ? (el.val ? "control-btn active" : "control-btn")
        : "control-btn" + (DANGER_IDS.has(id) ? " danger" : "");
    dom.className = "control-btn flash";
    fetch(cmd).then(() => { dom.className = finalCss; });
}


document.addEventListener("DOMContentLoaded", () => {
    createSpans();
    refreshData();
    repeatRefresh();
});
