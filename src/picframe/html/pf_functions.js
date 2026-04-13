
async function getData() {
    const response = await fetch("/?all");
    return response.json();
}


function createSpans() {
    let span_div_html = "";
    Object.entries(ids).forEach(([element_id, element]) => {
        let description = element_id.replace("_", " ");
        if (element.desc !== undefined) {
            description = element.desc;
        }
        if (element.type === "bool" || element.type === "action") {
            span_div_html += `<button class="pf_span off" id="${element_id}" onclick="toggle('${element_id}')">${description}</button>`;
        } else {
            const width = TYPES[element.type][0];
            span_div_html += `<label class="pf_span field"><span>${description}</span><input id="${element_id}" style="width:${width}ch;"></label>`;
        }
    });
    const span_div = document.getElementById("spans");
    span_div.innerHTML = span_div_html;

    // make enter press upload button
    span_div.addEventListener("keyup", event => {
        if (event.keyCode === 13) { // enter key
            event.preventDefault();
            uploadValues();
        }
    });
}


function isNumeric(num) {
    return (typeof(num) === 'number' || typeof(num) === "string" && num.trim() !== '') && !isNaN(num);
}


function refreshPage() {
    Object.entries(ids).forEach(([element_id, element]) => { //ids declared previous to this script in each page
        let docElement = document.getElementById(element_id);
        let value = element.val;
        if (isNumeric(value)) {
            value = parseFloat(value);
            if (element.type === "number") { // integer or float
                if (Math.floor(value) !== value) { //float
                    value = value.toFixed(2);
                }
            } else if (element.type === "date") {
                date = new Date(value * 1000); // js uses ms
                value = `${date.getFullYear()}/${date.getMonth() + 1}/${date.getDate()}`;
            }
        } else if (element.type === "bool") {
            if (value == true || value === "true" || value === "True" || value === "ON") {
                value = true;
            } else {
                value = false;
            }
        }
        docElement.value = value; //TODO have some fields not changed by ids.val?
        element.val = value; // reset to refreshed version TODO check this is necessary?
        if (element.type === "bool") {
            docElement.className = (element.val ? "pf_span on" : "pf_span off");
        }
    });
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
    Object.entries(ids).forEach(([element_id, element]) => { //ids declared previous to this script in each page
        if (element.fn === "setter" && element.type !== "bool") { // done by toggle function.
            let docElement = document.getElementById(element_id);
            if (docElement.value != element.val) {
                console.log("updating:" + element_id + "->" + docElement.value + ":was:" + element.val + ":");
                element.val = docElement.value;
                fetch(`/?${element_id}=${docElement.value}`).then(() => data_changed = true); //TODO do we need to refresh?
            }
        }
    });
    if (data_changed) { //TODO - is this necessary in ids.val changed here?
        refreshData();
    }
}


function toggle(id) {
    let element = ids[id];
    if (element.type === "bool") { //toggle val and class
        element.val = !(element.val);
    }
    let cmd = `/?${id}=${element.val}`
    if (element.fn !== "setter") { // i.e. use fn
        cmd = `/?${element.fn}`;
        cmd = cmd.replace('$val', element.val);
    }
    let docElement = document.getElementById(id);
    let css = (element.val ? "pf_span on" : "pf_span off"); // return to this
    docElement.className = "pf_span flash";
    console.log(cmd);
    fetch(cmd).then(() => afterFlash(docElement, css));
}


function afterFlash(element, css) {
    element.className = css; //TODO slight time delay?
}


// the super slimmed down python server doesn't load style sheets from file so this is
// done using javascript!
function setStyle() {
    const x = document.createElement("STYLE");
    const t = document.createTextNode(`
    :root {
        --bg: #1f2329;
        --panel: #2b3038;
        --panel-2: #343a44;
        --text: #e8edf2;
        --muted: #98a2b3;
        --accent: #4ea1ff;
        --good: #2b9464;
        --bad: #8f3a3a;
        --flash: #c97b32;
        --border: #3f4652;
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        background: radial-gradient(circle at top right, #2e3440 0%, var(--bg) 45%, #181b20 100%);
        color: var(--text);
        font-family: "Segoe UI", "Helvetica Neue", Arial, sans-serif;
    }
    .app-shell {
        max-width: 1200px;
        margin: 0 auto;
        padding: 16px;
        display: grid;
        gap: 16px;
    }
    .topbar {
        background: linear-gradient(135deg, var(--panel) 0%, var(--panel-2) 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 16px;
    }
    h1 { margin: 0; font-size: 1.4rem; letter-spacing: 0.02em; }
    .subline { margin-top: 6px; color: var(--muted); font-size: 0.92rem; }
    .preview-card, .controls-card {
        background: linear-gradient(160deg, var(--panel) 0%, #242930 100%);
        border: 1px solid var(--border);
        border-radius: 14px;
        padding: 14px;
    }
    .preview-title, .controls-title { font-weight: 600; margin-bottom: 10px; color: #cfd8e3; }
    .preview-frame {
        border: 1px solid var(--border);
        border-radius: 12px;
        overflow: hidden;
        background: #121417;
        aspect-ratio: 16/9;
    }
    #preview_img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        display: block;
    }
    .preview-links { margin-top: 10px; display: flex; gap: 12px; flex-wrap: wrap; }
    .preview-links a { color: var(--accent); text-decoration: none; }
    .preview-links a:hover { text-decoration: underline; }
    .controls-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
        gap: 8px;
        margin-bottom: 12px;
    }
    button#upload_button {
        background: var(--accent);
        color: #0e1a28;
        border: 0;
        border-radius: 10px;
        font-weight: 700;
        padding: 10px 14px;
        cursor: pointer;
    }
    .pf_span {
        border: 1px solid var(--border);
        border-radius: 10px;
        padding: 8px 10px;
        color: var(--text);
        background: #2a2f37;
    }
    .pf_span.field { display: flex; flex-direction: column; gap: 6px; }
    .pf_span.field input {
        border: 1px solid var(--border);
        border-radius: 8px;
        background: #161a20;
        color: var(--text);
        padding: 6px 8px;
    }
    .off { background-color: var(--bad); color: #f4dde0; }
    .on { background-color: var(--good); color: #ddf8ea; }
    .flash { background-color: var(--flash); color: #fdf2e5; }
    @media (min-width: 900px) {
        .app-shell { grid-template-columns: 1fr 1fr; }
        .topbar { grid-column: 1 / -1; }
    }
    `);
    x.appendChild(t);
    document.head.appendChild(x);
}
