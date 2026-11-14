"""本地后台管理站点（Flask）

登录页 + 相机配置页。页面元素结构与 page_objects 里的定位器一一对应。

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

STATE = {"camera": {}}

CSS = """
body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f6f8; margin: 0; }
.header { background: #1f2d3d; color: #fff; padding: 14px 28px; font-size: 18px; }
.nav a { color: #cfd8e3; margin-right: 18px; text-decoration: none; font-size: 14px; }
.nav a:hover { color: #fff; }
.container { max-width: 960px; margin: 24px auto; background: #fff; padding: 24px 28px; border-radius: 6px;
             box-shadow: 0 2px 10px rgba(0,0,0,.06); }
h2 { font-size: 20px; margin: 0 0 18px; }
input[type=text], input[type=number], input[type=password] {
    height: 32px; padding: 0 10px; border: 1px solid #dcdfe6; border-radius: 4px; width: 180px; }
select { height: 32px; padding: 0 8px; border: 1px solid #dcdfe6; border-radius: 4px; }
button { height: 32px; padding: 0 14px; border: none; border-radius: 4px; background: #409eff; color: #fff;
         cursor: pointer; font-size: 14px; }
button:hover { background: #66b1ff; }
.tip { margin-top: 16px; padding: 8px 12px; background: #f0f9eb; color: #67c23a; border-radius: 4px; }
.field { margin-bottom: 14px; display: flex; align-items: center; gap: 10px; }
.field label { width: 100px; color: #606266; font-size: 14px; }
"""


def page(title, body, nav=True):
    menu = '<div class="nav"><a href="/camera">相机配置</a></div>'
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
            resp = redirect("/camera")
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
  <input type="checkbox" name="watermark" onchange="togglePosition()">
</div>
<div class="field"><label>水印位置</label>
  <select name="watermark_position" disabled>
    <option value="top">顶部</option>
    <option value="bottom" selected>底部</option>
  </select>
</div>
<button onclick="saveCamera()">保存配置</button>
<div id="tip" class="tip" hidden>配置保存成功</div>
<div class="field" style="margin-top:16px"><label>当前配置</label>
  <span id="previewText">1080P / 30fps / 水印关闭</span></div>
<script>
function togglePosition() {
  const on = document.querySelector('[name=watermark]').checked;
  document.querySelector('[name=watermark_position]').disabled = !on;
}
function showTip(text, isError) {
  const tip = document.getElementById('tip');
  tip.textContent = text;
  tip.hidden = false;
  tip.style.background = isError ? '#fef0f0' : '#f0f9eb';
  tip.style.color = isError ? '#f56c6c' : '#67c23a';
}
function saveCamera() {
  const res = document.querySelector('[name=resolution]').value;
  const fpsRaw = document.querySelector('[name=fps]').value.trim();
  const on = document.querySelector('[name=watermark]').checked;
  if (fpsRaw === '') {
    showTip('帧率不能为空', true);
    return;
  }
  const fps = Number(fpsRaw);
  if (isNaN(fps) || fps < 15 || fps > 60) {
    showTip('帧率必须在 15-60 之间', true);
    return;
  }
  const pos = document.querySelector('[name=watermark_position]').value;
  const posText = pos === 'top' ? '顶部' : '底部';
  document.getElementById('previewText').textContent =
    res + ' / ' + fps + 'fps / 水印' + (on ? '开启(' + posText + ')' : '关闭');
  showTip('配置保存成功', false);
}
</script>
"""
    return page("相机配置", body)


# ---------------- 运维 ----------------
@app.get("/health")
def health():
    return {"status": "ok", "service": "mock-camera-admin"}


@app.post("/__admin/reset")
def reset():
    STATE["camera"] = {}
    return {"code": 200, "msg": "reset ok"}


if __name__ == "__main__":
    print(f"本地后台管理站点启动：http://127.0.0.1:{PORT}  账号={ADMIN_USER}/{ADMIN_PWD}")
    app.run(host="0.0.0.0", port=PORT, debug=False, threaded=True)
