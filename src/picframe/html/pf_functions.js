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


function createSpans() {
    let span_div_html = "";
    Object.entries(ids).forEach(([element_id, element]) => {
        let description = element_id.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
        if (element.desc !== undefined) {
            description = element.desc;
        }
        if (element.type === "bool" || element.type === "action") {
            span_div_html += `<button class="control-btn" id="${element_id}" onclick="toggle('${element_id}')">${description}</button>`;
        } else {
            const width = TYPES[element.type][0];
            span_div_html += `<label class="control-field"><span>${description}</span><input id="${element_id}" style="width:${width}ch;"></label>`;
        }
    });
    const span_div = document.getElementById("spans");
    span_div.innerHTML = span_div_html;

    span_div.addEventListener("keyup", event => {
        if (event.keyCode === 13) {
            event.preventDefault();
            uploadValues();
        }
    });
}


function isNumeric(num) {
    return (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);
}


function refreshPage() {
    Object.entries(ids).forEach(([element_id, element]) => {
        let docElement = document.getElementById(element_id);
        let value = element.val;
        if (isNumeric(value)) {
            value = parseFloat(value);
            if (element.type === "number") {
                if (Math.floor(value) !== value) {
                    value = value.toFixed(2);
                }
            } else if (element.type === "date") {
                date = new Date(value * 1000);
                value = `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
            }
        } else if (element.type === "bool") {
            if (value == true || value === "true" || value === "True" || value === "ON") {
                value = true;
            } else {
                value = false;
            }
        }
        docElement.value = value;
        element.val = value;
        if (element.type === "bool") {
            docElement.className = (element.val ? "control-btn active" : "control-btn");
        }
    });
}


function refreshStatus(data) {
    if (data) {
        document.getElementById("status-files").textContent = data.file_count || "--";
        document.getElementById("status-loading").textContent = data.loading ? "Yes" : "No";
        let scanText = "--";
        if (data.scan_total > 0) {
            scanText = `${data.scan_processed || 0}/${data.scan_total} (${Math.round(data.scan_percent || 0)}%)`;
        }
        document.getElementById("status-scan").textContent = scanText;
    }
}


function refreshData() {
    getData().then(ret_val => {
        let data_changed = false;
        Object.entries(ret_val).forEach(([key, val]) => {
            if (key in ids && ids[key].val != val) {
                data_changed = true;
                ids[key].val = val;
            }
        });
        if (data_changed) {
            refreshPage();
        }
    });
    getStatus().then(refreshStatus);
}


function repeatRefresh() {
    refreshData();
    const img = document.getElementById("preview_img");
    if (img) {
        img.src = `/current_image?t=${Date.now()}`;
    }
    setTimeout(repeatRefresh, 15000);
}


function uploadValues() {
    let data_changed = false;
    Object.entries(ids).forEach(([element_id, element]) => {
        if (element.fn === "setter" && element.type !== "bool") {
            let docElement = document.getElementById(element_id);
            if (docElement.value != element.val) {
                console.log("updating:" + element_id + "->" + docElement.value + ":was:" + element.val + ":");
                element.val = docElement.value;
                fetch(`/?${element_id}=${docElement.value}`).then(() => data_changed = true);
            }
        }
    });
    if (data_changed) {
        refreshData();
    }
}


function toggle(id) {
    let element = ids[id];
    if (element.type === "bool") {
        element.val = !(element.val);
    }
    let cmd = `/?${id}=${element.val}`
    if (element.fn !== "setter") {
        cmd = `/?${element.fn}`;
        cmd = cmd.replace('$val', element.val);
    }
    let docElement = document.getElementById(id);
    let css = (element.val ? "control-btn active" : "control-btn");
    docElement.className = "control-btn flash";
    console.log(cmd);
    fetch(cmd).then(() => afterFlash(docElement, css));
}


function afterFlash(element, css) {
    element.className = css;
}


function getTheme() {
    return localStorage.getItem("picframe-theme") || "dark";
}


function setTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("picframe-theme", theme);
}


function toggleTheme() {
    const current = getTheme();
    setTheme(current === "dark" ? "light" : "dark");
}


function setStyle() {
    const theme = getTheme();
    setTheme(theme);
    
    const x = document.createElement("STYLE");
    const t = document.createTextNode(`
    :root {
        --bg-primary: #1a1d21;
        --bg-secondary: #25292e;
        --bg-tertiary: #2d3238;
        --text-primary: #e8eaed;
        --text-secondary: #9aa0a6;
        --border: #3c4043;
        --accent: #8ab4f8;
        --accent-hover: #aecbfa;
        --active: #81c995;
        --active-dim: #2e3b2f;
        --inactive: #5f6368;
        --inactive-dim: #3c3f44;
        --flash: #fdd663;
    }
    [data-theme="light"] {
        --bg-primary: #f8f9fa;
        --bg-secondary: #ffffff;
        --bg-tertiary: #e8eaed;
        --text-primary: #202124;
        --text-secondary: #5f6368;
        --border: #dadce0;
        --accent: #1a73e8;
        --accent-hover: #1557b0;
        --active: #34a853;
        --active-dim: #e6f4ea;
        --inactive: #9aa0a6;
        --inactive-dim: #f1f3f4;
        --flash: #fbbc04;
    }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body {
        background: var(--bg-primary);
        color: var(--text-primary);
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        min-height: 100vh;
        line-height: 1.5;
        transition: background 0.3s, color 0.3s;
    }
    .container {
        max-width: 1100px;
        margin: 0 auto;
        padding: 24px;
        display: flex;
        flex-direction: column;
        gap: 20px;
    }
    .header {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px 24px;
    }
    .header-content {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .logo {
        display: flex;
        align-items: center;
        gap: 12px;
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .logo svg {
        color: var(--accent);
    }
    .tagline {
        color: var(--text-secondary);
        font-size: 0.875rem;
        margin-top: 8px;
    }
    .theme-toggle {
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 8px;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        color: var(--text-secondary);
        transition: all 0.2s;
    }
    .theme-toggle:hover {
        border-color: var(--accent);
        color: var(--accent);
    }
    .sun-icon { display: none; }
    .moon-icon { display: block; }
    [data-theme="light"] .sun-icon { display: block; }
    [data-theme="light"] .moon-icon { display: none; }
    .section-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 14px;
    }
    .section-header h2 {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .preview {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
    }
    .preview-links {
        display: flex;
        gap: 14px;
    }
    .preview-links a {
        color: var(--accent);
        text-decoration: none;
        font-size: 0.875rem;
        transition: color 0.2s;
    }
    .preview-links a:hover {
        color: var(--accent-hover);
    }
    .preview-frame {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        background: var(--bg-primary);
        aspect-ratio: 16/9;
    }
    #preview_img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }
    .controls {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
    }
    #upload_button {
        background: var(--accent);
        color: var(--bg-primary);
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
        cursor: pointer;
        font-size: 0.9rem;
        transition: all 0.2s;
    }
    #upload_button:hover {
        background: var(--accent-hover);
    }
    .controls-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
        gap: 10px;
    }
    .control-btn {
        border: 1px solid var(--border);
        border-radius: 8px;
        padding: 10px 12px;
        color: var(--text-secondary);
        background: var(--bg-tertiary);
        cursor: pointer;
        font-size: 0.875rem;
        font-weight: 500;
        transition: all 0.15s ease;
    }
    .control-btn:hover {
        border-color: var(--accent);
        color: var(--text-primary);
    }
    .control-btn.active {
        background: var(--active-dim);
        border-color: var(--active);
        color: var(--active);
    }
    .control-btn.flash {
        background: var(--flash);
        border-color: var(--flash);
        color: var(--bg-primary);
    }
    .control-field {
        display: flex;
        flex-direction: column;
        gap: 6px;
        padding: 10px 12px;
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    .control-field span {
        font-size: 0.8rem;
        color: var(--text-secondary);
        font-weight: 500;
    }
    .control-field input {
        border: 1px solid var(--border);
        border-radius: 6px;
        background: var(--bg-primary);
        color: var(--text-primary);
        padding: 8px 10px;
        font-size: 0.9rem;
    }
    .control-field input:focus {
        outline: none;
        border-color: var(--accent);
    }
    .info {
        background: var(--bg-secondary);
        border: 1px solid var(--border);
        border-radius: 16px;
        padding: 20px;
    }
    .status-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 16px;
    }
    .status-item {
        display: flex;
        flex-direction: column;
        gap: 4px;
        padding: 12px;
        background: var(--bg-tertiary);
        border-radius: 8px;
    }
    .status-label {
        font-size: 0.75rem;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .status-value {
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    @media (max-width: 600px) {
        .container { padding: 16px; }
        .controls-grid { grid-template-columns: 1fr 1fr; }
        .status-grid { grid-template-columns: 1fr; }
    }
    @media (min-width: 800px) {
        .container { 
            display: grid; 
            grid-template-columns: 1fr 320px; 
            align-items: start;
        }
        .header { grid-column: 1 / -1; }
        .preview { grid-column: 1 / 2; }
        .controls { grid-column: 2 / 3; grid-row: 2 / 4; }
        .info { grid-column: 1 / 2; }
    }
    `);
    x.appendChild(t);
    document.head.appendChild(x);
}