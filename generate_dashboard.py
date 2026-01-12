import json
import html
import os

# ---------------- CONFIG ----------------
DATA_FILE = "data.json"
OUTPUT_FILE = "index.html"

SUBJECT_META = {
    "পদার্থবিজ্ঞান": {"color": "#ef4444", "icon": "⚛️", "size": "large"},
    "উচ্চতর গণিত": {"color": "#ec4899", "icon": "📐", "size": "large"},
    "রসায়ন": {"color": "#8b5cf6", "icon": "🧪", "size": "medium"},
    "জীববিজ্ঞান": {"color": "#10b981", "icon": "🧬", "size": "medium"},
    "বাংলা": {"color": "#f59e0b", "icon": "✍️", "size": "small"},
    "English": {"color": "#3b82f6", "icon": "🔤", "size": "small"},
    "ICT": {"color": "#06b6d4", "icon": "💻", "size": "small"},
    "Digital": {"color": "#f97316", "icon": "🌐", "size": "medium"},
}

SUBJECT_ORDER = ["বাংলা", "English", "ICT", "পদার্থবিজ্ঞান", "রসায়ন", "উচ্চতর গণিত", "জীববিজ্ঞান", "Digital"]
BANGLA_PAPER_ORDER = {"প্রথম": 1, "দ্বিতীয়": 2, "তৃতীয়": 3, "চতুর্থ": 4}

# ---------------- HELPERS ----------------
def get_subject_meta(name: str) -> dict:
    for subject, meta in SUBJECT_META.items():
        if name.startswith(subject):
            return meta
    return {"color": "#94a3b8", "icon": "📚", "size": "small"}

def subject_sort_key(name: str) -> int:
    for i, subject in enumerate(SUBJECT_ORDER):
        if name.startswith(subject):
            return i
    return len(SUBJECT_ORDER)

def build_file_tree(node_dict: dict) -> str:
    if not node_dict:
        return ""
    html_out = '<ul class="tree-list">'
    
    def tree_sort_key(item):
        title, data = item
        is_file = not bool(data.get("children"))
        paper_order = 999
        for word, order in BANGLA_PAPER_ORDER.items():
            if word in title:
                paper_order = order
                break
        return (is_file, paper_order, title)

    items = sorted(node_dict.items(), key=tree_sort_key)
    for title, item in items:
        safe_title = html.escape(title)
        children = item.get("children", {})
        if children:
            html_out += f"""
            <li class="tree-folder">
                <details>
                    <summary>📂 {safe_title}</summary>
                    <div class="nested-content">{build_file_tree(children)}</div>
                </details>
            </li>"""
        else:
            link = html.escape(item.get("link", "#"))
            html_out += f'<li><a href="{link}" target="_blank" class="tree-file">📄 {safe_title}</a></li>'
    return html_out + "</ul>"

def create_card(name, data, is_exam=False):
    meta = get_subject_meta(name)
    children = data.get("children", {})
    tree_content = build_file_tree(children)
    js_content = json.dumps(tree_content)
    safe_name = html.escape(name)
    
    css_class = f"bento-item {meta['size']}" if not is_exam else "bento-item medium exam-card"
    badge = '<div class="card-badge">PYQ Hub</div>' if is_exam else ""
    
    return f"""
    <div class="{css_class}" style="--accent: {meta['color']}" onclick='openPanel("{safe_name}", {js_content})'>
        {badge}
        <div class="card-icon">{meta['icon']}</div>
        <div class="card-body">
            <h3>{safe_name}</h3>
            <p>{len(children)} Sections Available</p>
        </div>
        <div class="hover-glow"></div>
    </div>"""

# ---------------- LOAD DATA ----------------
if not os.path.exists(DATA_FILE):
    initial = {
        "Notes": {"children": {}},
        "PYQ": {"children": {}},
        "Digital": {"children": {}}
    }
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(initial, f, indent=4, ensure_ascii=False)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    raw_data = json.load(f)

notes_data = raw_data.get("Notes", {}).get("children", {})
pyq_data = raw_data.get("PYQ", {}).get("children", {})
digital_data = raw_data.get("Digital", {}).get("children", {})

# ---------------- GENERATE CARDS ----------------
lib_html = "".join([create_card(n, d) for n, d in sorted(notes_data.items(), key=lambda x: subject_sort_key(x[0]))])
exam_html = "".join([create_card(n, d, True) for n, d in pyq_data.items()])
digital_html = "".join([create_card(n, d) for n, d in digital_data.items()])

# ---------------- FINAL TEMPLATE ----------------
full_html = fr"""
<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>HSC Digital Resource Library</title>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap">

<style>
:root {{
    --bg: #0b0f1a; --sidebar: #111827; --card: #1f2937;
    --border: rgba(255,255,255,0.08); --accent: #38bdf8;
    --text-main: #f3f4f6; --text-dim: #9ca3af;
}}
* {{ box-sizing:border-box; -webkit-tap-highlight-color:transparent; transition:all 0.2s ease; }}
body {{ margin:0; font-family:'Plus Jakarta Sans',sans-serif; background:var(--bg); color:var(--text-main); display:flex; height:100vh; overflow:hidden; }}
nav {{ width:80px; background:var(--sidebar); border-right:1px solid var(--border); display:flex; flex-direction:column; align-items:center; padding:20px 0; justify-content:space-between; flex-shrink:0; }}
.nav-group {{ display:flex; flex-direction:column; gap:16px; align-items:center; width:100%; }}
.nav-logo {{ font-weight:800; color:var(--accent); font-size:24px; margin-bottom:16px; }}
.nav-item {{ width:48px; height:48px; border-radius:12px; display:flex; align-items:center; justify-content:center; cursor:pointer; color:var(--text-dim); border:1px solid transparent; font-size:1.2rem; }}
.nav-item:hover {{ background: rgba(255,255,255,0.05); color:var(--text-main); }}
.nav-item.active {{ background: var(--accent); color: var(--bg); box-shadow:0 0 20px rgba(56,189,248,0.4); }}

main {{ flex:1; overflow-y:auto; padding:40px 60px; scroll-behavior:smooth; position:relative; }}
.container {{ max-width:1200px; margin:0 auto; min-height:100%; display:flex; flex-direction:column; }}
h1 {{ font-size:clamp(1.8rem,5vw,2.5rem); font-weight:800; margin:0 0 8px; letter-spacing:-1px; }}
.subtitle {{ color:var(--text-dim); margin-bottom:32px; font-size:1rem; }}

.view {{ display:none; flex:1; }}
.view.active {{ display:block; animation:slideUp 0.4s ease; }}
@keyframes slideUp {{ from {{ opacity:0; transform:translateY(10px); }} to {{ opacity:1; transform:translateY(0); }} }}

.bento-grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(280px,1fr)); grid-auto-rows:160px; gap:20px; }}
.bento-item {{ background:var(--card); border:1px solid var(--border); border-radius:24px; padding:24px; display:flex; flex-direction:column; justify-content:space-between; cursor:pointer; overflow:hidden; }}
.bento-item:hover {{ border-color:var(--accent); transform:translateY(-5px); box-shadow:0 10px 30px rgba(0,0,0,0.3); }}
.large {{ grid-column:span 2; grid-row:span 2; }}
.medium {{ grid-column:span 2; }}

.card-icon {{ font-size:32px; }}
.card-body h3 {{ margin:0; font-size:1.2rem; }}
.card-body p {{ margin:4px 0 0; color:var(--text-dim); font-size:0.85rem; }}
.card-badge {{ position:absolute; top:16px; right:16px; background:rgba(56,189,248,0.1); color:var(--accent); padding:4px 10px; border-radius:20px; font-size:11px; font-weight:700; }}

#panel {{ position:fixed; right:-100%; top:0; width:500px; height:100vh; background:#111827; border-left:1px solid var(--border); z-index:2000; padding:40px; overflow-y:auto; transition:0.4s cubic-bezier(0.4,0,0.2,1); }}
#panel.active {{ right:0; box-shadow:-20px 0 50px rgba(0,0,0,0.5); }}
.close-btn {{ float:right; cursor:pointer; font-size:32px; color:var(--text-dim); }}

.tree-list {{ list-style:none; padding:0; margin:0; }}
summary {{ padding:12px 15px; background:rgba(255,255,255,0.03); border-radius:10px; margin:6px 0; cursor:pointer; font-weight:600; font-size:0.95rem; display:flex; align-items:center; }}
summary:hover {{ background:rgba(255,255,255,0.07); }}
.nested-content {{ margin-left:18px; border-left:1px solid rgba(255,255,255,0.1); padding-left:12px; }}
.tree-file {{ display:block; padding:10px; color:var(--text-dim); text-decoration:none; font-size:0.9rem; border-radius:8px; }}
.tree-file:hover {{ color:var(--accent); background:rgba(56,189,248,0.05); }}

footer {{ margin-top:auto; padding:40px 0 20px; border-top:1px solid var(--border); text-align:center; color:var(--text-dim); font-size:0.85rem; }}
.footer-links {{ margin-top:12px; display:flex; justify-content:center; gap:20px; }}
.footer-links span, .footer-links a {{ color:var(--accent); text-decoration:none; cursor:pointer; font-weight:600; }}

#disclaimer-modal {{ display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.85); z-index:3000; align-items:center; justify-content:center; padding:20px; }}
.modal-content {{ background:var(--sidebar); padding:35px; border-radius:24px; max-width:550px; border:1px solid var(--border); line-height:1.6; }}
.modal-content h3 {{ margin-top:0; color:#fff; }}
.modal-btn {{ background:var(--accent); color:var(--bg); border:none; padding:12px 24px; border-radius:10px; cursor:pointer; margin-top:20px; font-weight:700; width:100%; }}

@media (max-width:850px) {{
    body {{ flex-direction:column; }}
    nav {{ width:100%; height:70px; flex-direction:row; padding:0 20px; order:2; border-right:none; border-top:1px solid var(--border); }}
    .nav-group {{ flex-direction:row; justify-content:center; }}
    .nav-logo {{ display:none; }}
    main {{ padding:25px 20px 100px; order:1; }}
    .bento-grid {{ grid-template-columns:1fr; grid-auto-rows:auto; }}
    .large, .medium {{ grid-column:span 1; grid-row:span 1; }}
    #panel {{ width:100%; }}
    footer {{ padding-bottom:40px; }}
}}
</style>
"""

# ---------------- BODY ----------------
full_html += fr"""
<body>
<nav>

    <div class="nav-group">
        <div class="nav-item" onclick="collapseAll()" title="Collapse All Folders">🧹</div>
    </div>


    <div class="nav-group" style="flex-grow:1; justify-content:center;">
        <div class="nav-item" onclick="switchView('exams', this)" title="Question Bank">📝</div>
        <div class="nav-item active" onclick="switchView('library', this)" title="Study Library">📚</div>
        <div class="nav-item" onclick="switchView('digital', this)" title="Digital Resources">🌐</div>
    </div>


    <div class="nav-group">
        <div class="nav-item" onclick="location.reload()" title="Refresh Page">🔄</div>
        <div class="nav-logo">H</div>
    </div>

</nav>

<main>
<div class="container">
    <div id="library" class="view active">
        <h1>Subject Library</h1>
        <p class="subtitle">Select a subject for HSC 2026 notes.</p>
        <div class="bento-grid">{lib_html}</div>
    </div>
    <div id="exams" class="view">
        <h1>Exam Hub</h1>
        <p class="subtitle">Access Board & Admission question banks.</p>
        <div class="bento-grid">{exam_html}</div>
    </div>
    <div id="digital" class="view">
        <h1>Digital Resources</h1>
        <p class="subtitle">Curated links, tools, and extra resources for HSC students.</p>
        <div class="bento-grid">{digital_html}</div>
    </div>
    <footer>
        <p>© <span id="year"></span> HSC Resource Hub | Curated by <strong>Somrat_10369</strong></p>
        <div class="footer-links">
            <span onclick="toggleModal(true)">Legal Disclaimer</span>
            <a href="mailto: somrat10369@gmail.com?subject=Report%20About%20Your%20Websites%20Fair%20Use%20Policy&body=Hi%2C%0AI%20noticed%20an%20issue%20on%20this%20page%3A%20%5BURL%5D.%0AIssue%20(short)%3A%20%5Bdescribe%20the%20problem%20or%20suggested%20correction%5D.%0ASuggested%20correction%3A%20%5Bwhat%20you'd%20like%20changed%5D.%0AOptional%3A%20My%20contact%20info%3A%20%5Bemail%2Fphone%5D%0A%0AThanks%20for%20maintaining%20this%20resource%2C%0A%5BYour%20Name%5D">Contact Support</a>
        </div>
    </footer>
</div>

<div id="panel">
    <span class="close-btn" onclick="closePanel()">×</span>
    <h2 id="panel-title" style="margin-top:0; font-size:1.8rem;">Subject</h2>
    <div id="panel-body" style="margin-top:30px;"></div>
</div>

    <div id="disclaimer-modal">
        <div class="modal-content">
            <h3>⚖️ Legal Disclaimer</h3>
            <p>This website is an <strong>educational project</strong> created to help students access resources easily. All materials (PDFs, images, and links) are sourced from publicly available files on the internet.</p>
            <p><strong>Copyright Notice:</strong> We do not claim ownership of any copyrighted books or lecture notes. All rights belong to the original authors and publishers. No harm is intended toward any commercial interests.</p>
            <p>If you are a copyright owner and would like content removed, please contact us and we will take immediate action.</p>
            <button class="modal-btn" onclick="toggleModal(false)">I AGREE</button>
        </div>
    </div>
</main>


<script>
document.getElementById('year').textContent = new Date().getFullYear();

function switchView(viewId, el) {{
    document.querySelectorAll('.view').forEach(v=>v.classList.remove('active'));
    document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
    document.getElementById(viewId).classList.add('active');
    el.classList.add('active');
}}

function openPanel(title, content) {{
    document.getElementById('panel-title').innerText = title;
    document.getElementById('panel-body').innerHTML = content;
    document.getElementById('panel').classList.add('active');
    if(window.innerWidth<850) document.body.style.overflow='hidden';
}}

function closePanel() {{
    document.getElementById('panel').classList.remove('active');
    document.body.style.overflow='auto';
}}

function toggleModal(show) {{
    document.getElementById('disclaimer-modal').style.display = show ? 'flex' : 'none';
}}

function collapseAll() {{
    document.querySelectorAll('details[open]').forEach(d=>d.removeAttribute('open'));
}}
</script>
</body>
</html>
"""

# ---------------- WRITE ----------------
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(full_html)
print(f"Dashboard successfully generated: {OUTPUT_FILE}")
