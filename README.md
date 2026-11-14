# mobile_admin_web_auto

基于 **Playwright + 标准 PO 分层**的后台管理 UI 自动化项目，覆盖 **相册管理 / 相机配置 / 浏览器配置 / DJ 音乐播放器** 四个页面。

仓库自带一个本地后台站点（`mock_site/`），替代原来的脱敏域名，克隆下来即可真实跑通全部 8 条用例，
每条用例都有明确断言（不只是"点完就算过"）。

---

## 一、技术栈

| 类别 | 选型 |
| --- | --- |
| 语言 | Python 3.10+ |
| UI 引擎 | Playwright（Chromium，支持无头） |
| 用例框架 | pytest |
| 分层设计 | PO（Page Object） |
| 报告 | Allure + JUnit XML |
| 稳定性 | pytest-rerunfailures（UI 抖动重跑） |
| 日志 | loguru |
| 被测站点 | Flask（自建 4 页面 + 登录） |

## 二、目录结构

```
mobile_admin_web_auto/
├── common/
│   ├── browser_handler.py   # 浏览器引擎（懒启动、无头可配、每用例独立 context）
│   ├── conf_handler.py      # 多环境配置（env.yaml + env_local.yaml 覆盖）
│   ├── data_handler.py      # YAML 测试数据读取
│   └── logger_handler.py    # 日志（loguru）
├── config/
│   ├── env.yaml             # local / ci 双环境（入库）
│   └── env_local.yaml       # 本地私有账号地址（.gitignore 排除）
├── data/
│   └── test_data.yaml       # 测试数据：相册关键字、分辨率帧率、收藏上限、DJ 参数
├── page_objects/            # PO 层：元素定位 + 页面操作，页面改版只改这里
│   ├── base_page.py         #   公共父类：显式等待、点击、输入、下拉、计数
│   ├── login_page.py        #   登录页
│   ├── album_page.py        #   相册管理页
│   ├── camera_page.py       #   相机配置页
│   ├── browser_page.py      #   浏览器配置页
│   └── dj_page.py           #   DJ 音乐播放器页
├── testcases/               # 用例层：只写业务流程 + 断言，不写元素定位
│   ├── conftest.py          #   engine / page / 登录 / 站点复位 fixture
│   ├── test_album.py
│   ├── test_camera.py
│   ├── test_browser.py
│   └── test_dj.py
├── mock_site/
│   └── app.py               # 本地后台站点（登录 + 4 页面 + /__admin/reset）
├── report/                  # 运行产物（.gitignore 排除）
├── run.py                   # 一键执行：起站点 → 跑用例 → 生成报告
├── pytest.ini
└── requirements.txt
```

## 三、覆盖场景

| 页面 | 用例 | 断言内容 |
| --- | --- | --- |
| 相册管理 | 检索 + 全选 + 批量删除 | 初始相册数、检索后命中数、检索结果名称、「删除成功」提示、删除后列表为空 |
| 相册管理 | 上传图片入口 | 「上传成功」提示文案 |
| 相机配置 | 设置 1080P/30fps + 开水印 + 保存 | 「配置保存成功」提示、分辨率/帧率/水印三项回显 |
| 相机配置 | 切换 4K/60fps + 保存 | 4K、60fps 回显、水印默认关闭 |
| 浏览器配置 | 一键清理缓存 | 「操作成功」提示、提示含缓存关键字 |
| 浏览器配置 | 收藏上限配置 | 「操作成功」提示、上限数值回显 |
| DJ 播放器 | 歌单展示 + 播放 | 歌曲条数为 3、提示含「正在播放」与歌曲名 |
| DJ 播放器 | 音量 + 均衡器 + 播放模式 | 「设置成功」提示、三项配置回显 |

## 四、本地运行

```powershell
# 1. 安装依赖
pip install -r requirements.txt
playwright install chromium        # 首次必须，下载浏览器内核

# 2. 一键执行（自动拉起本地站点）
python run.py

# 或分开执行
python mock_site/app.py            # 另开终端，默认 9100 端口
pytest
```

只想看页面效果：浏览器打开 <http://127.0.0.1:9100/login>，账号 `testuser / 123456`。

想看着浏览器一步步跑（调试用）：

```powershell
$env:HEADLESS="false"; pytest testcases/test_album.py
```

## 五、配置与环境

`config/env.yaml` 只管地址与运行参数，真实账号写 `config/env_local.yaml`（不入库）。

```yaml
current_env: "local"
local:
  base_url: "http://127.0.0.1:9100"
  timeout: 10000        # 元素等待超时（毫秒）
  headless: true        # CI 必须 true
  slow_mo: 0            # 调试时设 500 便于观察
ci:
  base_url: "http://host.docker.internal:9100"
```

优先级：**环境变量 `BASE_URL` / `ENV` / `HEADLESS` > `env_local.yaml` > `env.yaml`**。

## 六、设计要点

1. **PO 分层彻底**：元素定位与页面操作全部收在 `page_objects/`，用例里只出现业务动作和断言，页面改版只改一处。
2. **浏览器不再"一 import 就启动"**：旧写法把 `BrowserEngine()` 放在模块顶层，收集用例阶段就弹窗；
   现在由 `engine` fixture 在 session 开始时创建，`headless` 由配置驱动，CI 里不会弹窗。
3. **用例隔离**：每个用例一个独立 context + page，并在测试前自动登录，用例之间不串 cookie 和页面状态。
4. **数据驱动**：相册关键字、分辨率、帧率、收藏上限、DJ 参数全部放在 `data/test_data.yaml`，改参数不改代码。
5. **环境自愈**：`site_ready` fixture 在 session 开始前调用 `/__admin/reset` 复位站点数据；
   破坏性用例（批量删除）另外用 `fresh_site` 再复位一次，重复执行结果稳定。
6. **断言到位**：每条用例都校验提示文案 + 页面回显值，避免"只有点击、没有验证"的假用例。

## 七、CI 说明

容器化执行建议使用 Playwright 官方镜像（自带浏览器内核）：

```yaml
image: mcr.microsoft.com/playwright/python:v1.40.0-jammy
```

流水线里需要先起被测站点（`python mock_site/app.py` 或容器化的同镜像服务），
再用 `BASE_URL` 指向它，`HEADLESS=true` 保证无头执行，最后发布 JUnit + Allure 报告。

## 八、说明

仓库内地址、账号均为本地 Mock 站点固定值，不含公司真实环境信息；
真实配置通过 `config/env_local.yaml` 或环境变量注入。
