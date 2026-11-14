"""一键执行：拉起本地后台站点 → 跑 Playwright 用例 → 生成 Allure 报告

用法：
    python run.py                     # 全部用例
    python run.py testcases/test_dj.py # 只跑 DJ 模块
"""
import os
import shutil
import subprocess
import sys
import time

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE_PORT = os.getenv("PORT", "9100")
SITE_URL = f"http://127.0.0.1:{SITE_PORT}"


def start_site():
    try:
        requests.get(f"{SITE_URL}/health", timeout=1)
        print(f"[站点] 已在运行：{SITE_URL}")
        return None
    except Exception:
        pass

    print(f"[站点] 启动本地后台站点：{SITE_URL}")
    proc = subprocess.Popen(
        [sys.executable, os.path.join(ROOT, "mock_site", "app.py")],
        cwd=ROOT,
        env={**os.environ, "PORT": SITE_PORT},
    )
    for _ in range(30):
        try:
            requests.get(f"{SITE_URL}/health", timeout=1)
            print("[站点] 启动成功")
            return proc
        except Exception:
            time.sleep(1)
    proc.terminate()
    raise RuntimeError("后台站点启动失败，请手动执行：python mock_site/app.py")


def gen_report():
    allure = shutil.which("allure")
    if not allure:
        print("[报告] 未检测到 allure 命令，跳过 HTML 生成（原始数据在 report/allure_raw）")
        return
    rc = subprocess.call(
        [allure, "generate", "report/allure_raw", "-o", "report/allure_html", "--clean"], cwd=ROOT
    )
    print("[报告] 已生成：report/allure_html/index.html" if rc == 0 else "[报告] 生成失败")


def main():
    os.chdir(ROOT)
    site = start_site()
    try:
        args = sys.argv[1:]
        rc = subprocess.call([sys.executable, "-m", "pytest", *args], cwd=ROOT)
        gen_report()
        print(f"[结果] pytest 退出码 = {rc}")
        sys.exit(rc)
    finally:
        if site:
            site.terminate()
            print("[站点] 已关闭")


if __name__ == "__main__":
    main()
