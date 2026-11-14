"""本地后台管理站点（Flask）

替代公司内网脱敏域名，让 Playwright + PO 用例可以在本地真实跑通。
包含登录页 + 四个功能页：相册管理、相机配置、浏览器配置、DJ 音乐播放器。
页面的元素结构与 page_objects 里的定位器一一对应。

启动：
    python mock_site/app.py                # 默认 9100 端口
    $env:PORT=9101; python mock_site/app.py

账号：testuser / 123456（可用 ADMIN_USER / ADMIN_PWD 覆盖）
"""
import os
from functools import wraps

from flask import Flask, Response, redirect, request

app = Flask(__name__)

PORT = int(os.getenv("PORT", "9100"))
ADMIN_USER = os.getenv("ADMIN_USER", "testuser")
ADMIN_PWD = os.getenv("ADMIN_PWD", "123456")

INIT_ALBUMS = [
    {"name": "日常照片", "count": 36},
    {"name": "旅行记录", "count": 120},
    {"name": "截图备份", "count": 58},
]

SONGS = [
    {"id": 1, "name": "夜航", "artist": "Mock Band", "duration": "03:34"},
    {"id": 2, "name": "霓虹", "artist": "Mock Band", "duration": "03:08"},
    {"id": 3, "name": "晚风", "artist": "Mock Band", "duration": "04:00"},
]

STATE = {"albums": [dict(a) for a in INIT_ALBUMS], "camera": {}, "browser": {}, "dj": {}}

CSS = """
body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f6f8; margin: 0; }
.header { background: #1f2d3d; color: #fff; padding: 14px 28px; font-size: 18px; }
.nav a { color: #cfd8e3; margin-right: 18px; text-decoration: none; font-size: 14px; }
.nav a:hover { color: #fff; }
.container { max-width: 960px; margin: 24px auto; background: #fff; padding: 24px 28px; border-radius: 6px;
             box-shadow: 0 2px 10px rgba(0,0,0,.06); }
h2 { font-size: 20px; margin: 0 0 18px; }
.toolbar { display: flex; gap: 10px; align-items: center; margin-bottom: 16px; }
input[type=text], input[type=number], input[name=fps], input[name=collect_max] {
    height: 32px; padding: 0 10px; border: 1px solid #dcdfe6; border-radius: 4px; width: 180px; }
select { height: 32px; padding: 0 8px; border: 1px solid #dcdfe6; border-radius: 4px; }
button { height: 32px; padding: 0 14px; border: none; border-radius: 4px; background: #409eff; color: #fff;
         cursor: pointer; font-size: 14px; }
button:hover { background: #66b1ff; }
button.danger { background: #f56c6c; }
table { width: 100%; border-collapse: collapse; }
th, td { border-bottom: 1px solid #ebeef5; padding: 10px 8px; text-align: left; font-size: 14px; }
th { color: #909399; font-weight: normal; }
.modal { position: fixed; inset: 0; background: rgba(0,0,0,.4); display: flex; align-items: center;
         justify-content: center; }
.modal[hidden] { display: none; }
.dialog { background: #fff; padding: 20px 24px; border-radius: 6px; min-width: 300px; }
.dialog .actions { display: flex; gap: 10px; justify-content: flex-end; margin-top: 16px; }
.dialog .btn { padding: 6px 16px; border-radius: 4px; cursor: pointer; font-size: 14px; }
.dialog .btn.confirm { background: #409eff; color: #fff; }
.dialog .btn.cancel { background: #f2f3f5; color: #333; }
.tip { margin-top: 16px; padding: 8px 12px; background: #f0f9eb; color: #67c23a; border-radius: 4px; }
.field { margin-bottom: 14px; display: flex; align-items: center; gap: 10px; }
.field label { width: 100px; color: #606266; font-size: 14px; }
"""


def page(title, body, nav=True):
    menu = (
        '<div class="nav">'
        '<a href="/album">相册管理</a>'
        '<a href="/camera">相机配置</a>'
        '<a href="/browser">浏览器配置</a>'
        '<a href="/dj">DJ音乐播放器</a>'
        "</div>"
    )
    header = f'<div class="header">{title}{menu if nav else ""}</div>' if nav else ""
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{title}</title><style>{CSS}</style></head>
<body>
{header}
<div class="container">
{body}
</div>
</body>
</html>"""
    return Response(html, mimetype="text/html")


def require_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.cookies.get("session_user") != ADMIN_USER:
            return redirect("/login")
        return func(*args, **kwargs)

    return wrapper


# ---------------- 登录 ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == ADMIN_USER and password == ADMIN_PWD:
            resp = redirect("/album")
            resp.set_cookie("session_user", username, max_age=3600)
            return resp
        body = (
            '<h2>后台管理登录</h2>'
            '<form method="post" action="/login">'
            '<div class="field"><label>用户名</label>'
            '<input type="text" name="username" placeholder="请输入用户名"></div>'
            '<div class="field"><label>密码</label>'
            '<input type="password" name="password" placeholder="请输入密码"></div>'
            '<button type="submit">登录</button>'
            "</form>"
            '<div class="tip" style="background:#fef0f0;color:#f56c6c">用户名或密码错误</div>'
        )
        return page("后台管理登录", body, nav=False)

    body = (
        '<h2>后台管理登录</h2>'
        '<form method="post" action="/login">'
        '<div class="field"><label>用户名</label>'
        '<input type="text" name="username" placeholder="请输入用户名"></div>'
        '<div class="field"><label>密码</label>'
        '<input type="password" name="password" placeholder="请输入密码"></div>'
        '<button type="submit">登录</button>'
        "</form>"
    )
    return page("后台管理登录", body, nav=False)


# ---------------- 相册管理 ----------------
@app.get("/album")
@require_login
def album():
    rows = "".join(
        f'<tr><td><input type="checkbox" class="row-check"></td>'
        f'<td class="album-name">{a["name"]}</td><td>{a["count"]}</td></tr>'
        for a in STATE["albums"]
    )
    body = f"""
<h2>相册管理</h2>
<div class="toolbar">
  <input type="text" placeholder="搜索相册名称" id="keyword">
  <button onclick="doSearch()">搜索</button>
  <button onclick="doUpload()">上传图片</button>
  <button class="danger" onclick="openModal()">批量删除</button>
</div>
<table>
  <thead><tr>
    <th><input type="checkbox" class="all-check" onclick="toggleAll(this)"></th>
    <th>相册名称</th><th>图片数量</th>
  </tr></thead>
  <tbody id="albumBody">{rows}</tbody>
</table>
<div id="tip" class="tip" hidden>删除成功</div>
<div id="confirmModal" class="modal" hidden>
  <div class="dialog">
    <p>确认删除选中的相册吗？</p>
    <div class="actions">
      <div class="btn confirm" onclick="doDelete()">确认</div>
      <div class="btn cancel" onclick="closeModal()">取消</div>
    </div>
  </div>
</div>
<script>
function currentRows() {{ return Array.from(document.querySelectorAll('#albumBody tr')); }}
function doSearch() {{
  const kw = document.getElementById('keyword').value.trim();
  currentRows().forEach(function (tr) {{
    const name = tr.querySelector('.album-name').textContent;
    tr.hidden = kw !== '' && name.indexOf(kw) === -1;
  }});
  showTip('搜索完成：' + currentRows().filter(function (r) {{ return !r.hidden; }}).length + ' 个相册');
}}
function toggleAll(cb) {{
  document.querySelectorAll('.row-check').forEach(function (c) {{ c.checked = cb.checked; }});
}}
function openModal() {{ document.getElementById('confirmModal').hidden = false; }}
function closeModal() {{ document.getElementById('confirmModal').hidden = true; }}
function doDelete() {{
  const checked = Array.from(document.querySelectorAll('.row-check')).filter(function (c) {{ return c.checked; }});
  checked.forEach(function (c) {{ c.closest('tr').remove(); }});
  closeModal();
  showTip('删除成功，共删除 ' + checked.length + ' 个相册');
}}
function doUpload() {{ showTip('上传成功'); }}
function showTip(text) {{
  const tip = document.getElementById('tip');
  tip.textContent = text;
  tip.hidden = false;
}}
</script>
"""
    return page("相册管理", body)


# ---------------- 相机配置 ----------------
@app.get("/camera")
@require_login
def camera():
    body = """
<h2>相机配置</h2>
<div class="field"><label>分辨率</label>
  <select name="resolution">
    <option value="720P">720P</option>
    <option value="1080P" selected>1080P</option>
    <option value="4K">4K</option>
  </select>
</div>
<div class="field"><label>帧率</label>
  <input type="number" name="fps" value="30">
</div>
<div class="field"><label>水印开关</label>
  <input type="checkbox" name="watermark">
</div>
<button onclick="saveCamera()">保存配置</button>
<div id="tip" class="tip" hidden>配置保存成功</div>
<div id="preview" class="field" style="margin-top:16px"><label>当前配置</label><span id="previewText">1080P / 30fps / 水印关闭</span></div>
<script>
function saveCamera() {
  const res = document.querySelector('[name=resolution]').value;
  const fps = document.querySelector('[name=fps]').value;
  const wm = document.querySelector('[name=watermark]').checked;
  document.getElementById('previewText').textContent =
    res + ' / ' + fps + 'fps / 水印' + (wm ? '开启' : '关闭');
  document.getElementById('tip').hidden = false;
}
</script>
"""
    return page("相机配置", body)


# ---------------- 浏览器配置 ----------------
@app.get("/browser")
@require_login
def browser():
    body = """
<h2>浏览器配置</h2>
<div class="toolbar">
  <button onclick="clearCache()">一键清理缓存</button>
</div>
<div class="field"><label>收藏上限</label>
  <input type="number" name="collect_max" value="100">
  <button onclick="saveCollectLimit()">保存</button>
</div>
<div id="tip" class="tip" hidden>操作成功</div>
<div class="field" style="margin-top:16px"><label>当前收藏上限</label><span id="maxText">100</span></div>
<script>
function clearCache() { showTip('操作成功：缓存已清空'); }
function saveCollectLimit() {
  const v = document.querySelector('[name=collect_max]').value;
  document.getElementById('maxText').textContent = v;
  showTip('操作成功：收藏上限已更新为 ' + v);
}
function showTip(text) {
  const tip = document.getElementById('tip');
  tip.textContent = text;
  tip.hidden = false;
}
</script>
"""
    return page("浏览器配置", body)


# ---------------- DJ 音乐播放器 ----------------
@app.get("/dj")
@require_login
def dj():
    rows = "".join(
        f'<tr><td>{s["id"]}</td><td>{s["name"]}</td><td>{s["artist"]}</td>'
        f'<td>{s["duration"]}</td>'
        f'<td><button class="play-btn" onclick="playSong({s["id"]})">播放</button></td></tr>'
        for s in SONGS
    )
    body = f"""
<h2>DJ 音乐播放器</h2>
<table>
  <thead><tr><th>ID</th><th>歌曲</th><th>歌手</th><th>时长</th><th>操作</th></tr></thead>
  <tbody id="playlist">{rows}</tbody>
</table>
<div class="field" style="margin-top:18px"><label>音量</label>
  <input type="number" name="volume" value="50" min="0" max="100">
</div>
<div class="field"><label>均衡器</label>
  <select name="eq">
    <option value="normal">标准</option>
    <option value="rock">摇滚</option>
    <option value="jazz">爵士</option>
    <option value="vocal">人声</option>
  </select>
</div>
<div class="field"><label>播放模式</label>
  <select name="play_mode">
    <option value="sequence">顺序播放</option>
    <option value="loop">列表循环</option>
    <option value="single">单曲循环</option>
    <option value="random">随机播放</option>
  </select>
</div>
<button onclick="saveDj()">保存设置</button>
<div id="tip" class="tip" hidden>设置成功</div>
<div class="field" style="margin-top:16px"><label>当前状态</label>
  <span id="statusText">音量 50 / 标准 / 顺序播放</span></div>
<script>
function playSong(id) {{
  const btn = event.target;
  const name = btn.closest('tr').children[1].textContent;
  document.getElementById('tip').textContent = '正在播放：' + name;
  document.getElementById('tip').hidden = false;
}}
function saveDj() {{
  const volume = document.querySelector('[name=volume]').value;
  const eq = document.querySelector('[name=eq]').selectedOptions[0].textContent;
  const mode = document.querySelector('[name=play_mode]').selectedOptions[0].textContent;
  document.getElementById('statusText').textContent = '音量 ' + volume + ' / ' + eq + ' / ' + mode;
  document.getElementById('tip').textContent = '设置成功';
  document.getElementById('tip').hidden = false;
}}
</script>
"""
    return page("DJ 音乐播放器", body)


# ---------------- 运维 ----------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "mock-admin-web"}


@app.post("/__admin/reset")
def reset():
    STATE["albums"] = [dict(a) for a in INIT_ALBUMS]
    STATE["camera"] = {}
    STATE["browser"] = {}
    STATE["dj"] = {}
    return {"code": 200, "msg": "reset ok"}


if __name__ == "__main__":
    print(f"本地后台管理站点启动：http://127.0.0.1:{PORT}  账号={ADMIN_USER}/{ADMIN_PWD}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
