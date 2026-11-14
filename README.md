# mobile_admin_web_auto

后台管理站点的 UI 自动化测试工程，用 Playwright 驱动 Chromium，按 PO（Page Object）分层，
覆盖相册管理、相机配置、浏览器配置、DJ 音乐播放器四个页面。

被测站点是仓库内的一个 Flask 应用（`mock_site/app.py`），带登录页和四个功能页，
元素结构和 `page_objects/` 里的定位器一一对应。克隆仓库、装好浏览器内核就能跑，当前 8 条用例。

## 环境要求

| 项 | 说明 |
| --- | --- |
| Python | 3.10 及以上（验证用的是 3.13） |
| 浏览器 | Playwright 自带的 Chromium，首次需 `playwright install chromium` |
| 被测站点 | 仓库内 `mock_site/app.py`，默认监听 9100 端口 |
| Allure 命令行 | 可选，仅生成 HTML 报告时需要 |

## 依赖与用途

| 包 | 用途 | 备注 |
| --- | --- | --- |
| `playwright` | 浏览器驱动 | 同步 API，用 `sync_playwright()` |
| `pytest` | 用例组织与 fixture | `pytest.ini` 固定扫描路径 |
| `allure-pytest` | 报告 | 按 feature/story 分组，失败带截图能力 |
| `pytest-rerunfailures` | 失败重跑 | UI 抖动兜底，最多 1 次，间隔 2 秒 |
| `PyYAML` | 环境配置与测试数据 | 两处用途：`config/env.yaml`、`data/test_data.yaml` |
| `loguru` | 日志 | `report/logs/admin_web_日期.log` |
| `requests` | 调运维接口复位站点数据 | 只用于 `/__admin/reset`，不参与 UI 操作 |
| `flask` | 起被测站点 | 仅 `mock_site` 使用 |

安装：

```powershell
pip install -r requirements.txt
playwright install chromium
```

`playwright install chromium` 会下载约 200MB 的浏览器内核，只需执行一次。

## 目录与职责

| 路径 | 职责 |
| --- | --- |
| `common/browser_handler.py` | 浏览器引擎。构造时才启动 Chromium，`new_page()` 每次返回独立的 context + page |
| `common/conf_handler.py` | 读 `env.yaml` 与 `env_local.yaml`，产出 `config` 单例（base_url / timeout / headless / slow_mo） |
| `common/data_handler.py` | 读取 `data/test_data.yaml`，用例从这里取参数 |
| `common/logger_handler.py` | loguru 初始化 |
| `page_objects/base_page.py` | PO 父类：打开页面、显式等待后点击、填值、下拉选择、取文本、计数、等提示、截图 |
| `page_objects/login_page.py` | 登录页，`login()` 完成表单提交 |
| `page_objects/album_page.py` | 相册管理页：搜索、全选、批量删除、上传入口、统计剩余行数 |
| `page_objects/camera_page.py` | 相机配置页：分辨率/帧率、水印开关、保存、读回显 |
| `page_objects/browser_page.py` | 浏览器配置页：清缓存、收藏上限、读回显 |
| `page_objects/dj_page.py` | DJ 页：播放、音量、均衡器、播放模式、读状态 |
| `testcases/conftest.py` | 四层 fixture：站点就绪检查、浏览器引擎、已登录页面、数据复位 |
| `testcases/test_*.py` | 按页面拆分的用例，每条都带断言 |
| `mock_site/app.py` | 被测站点：登录 + 四页面 + `/health` + `/__admin/reset` |
| `data/test_data.yaml` | 用例参数：相册关键字、分辨率、帧率、收藏上限、DJ 音量与模式 |
| `run.py` | 起站点、跑用例、生成报告的入口 |

分层原则：元素定位只出现在 `page_objects/`，`testcases/` 里不出现 XPath。
页面改版时只改对应的 page 文件，用例不动。

## 跑起来

```powershell
# 方式一：一条命令（自动起站点、跑完自动关）
python run.py

# 方式二：分开执行
python mock_site/app.py    # 终端 1
pytest                      # 终端 2

# 只跑某个页面
pytest testcases/test_dj.py
```

正常输出结尾：

```
============================= 8 passed in 15.40s ==============================
```

本站点也可以直接在浏览器里点，用来对照用例行为：<http://127.0.0.1:9100/login>，账号 `testuser / 123456`。

调试时想看到浏览器一步步操作：

```powershell
$env:HEADLESS = "false"
$env:SLOW_MO = "500"     # 每个操作后停顿 500ms，便于观察
pytest testcases/test_album.py
```

`HEADLESS` 和 `SLOW_MO` 也可以写进 `config/env_local.yaml`，不必每次设环境变量。

## 一次用例的执行过程

以「批量删除相册」为例：

```
testcases/test_album.py::test_album_batch_delete(page, fresh_site)
  → conftest.py::fresh_site            先调 /__admin/reset，把三个相册复位
  → conftest.py::page                  新建 context + page，LoginPage 登录，拿到已登录页面
  → AlbumManagePage.enter_album_page() goto + wait_for_load_state("networkidle")
  → search_album_name("日常照片")       填关键字、点搜索，页面内 JS 过滤行
  → remaining_albums()                 统计未 hidden 的行数，断言为 1
  → batch_delete_album()               全选 → 批量删除 → 确认 → 等「删除成功」提示
  → 断言提示可见、剩余行数为 0
```

## 配置

`config/env.yaml`：

```yaml
current_env: "local"

local:
  base_url: "http://127.0.0.1:9100"
  timeout: 10000
  headless: true
  slow_mo: 0

ci:
  base_url: "http://host.docker.internal:9100"
  timeout: 15000
  headless: true
  slow_mo: 0

account:
  username: "testuser"
  password: "123456"
```

| 字段 | 含义 | 说明 |
| --- | --- | --- |
| `base_url` | 站点根地址 | 页面地址由 PO 的 `path` 拼出来，如 `/album` |
| `timeout` | 元素等待超时（毫秒） | 传给 `page.set_default_timeout`，不要设太小 |
| `headless` | 是否无头 | CI 必须 `true`；本地调试可设 `false` |
| `slow_mo` | 每步操作后的停顿（毫秒） | 只用于观察，不建议在 CI 打开 |
| `account` | 登录账号 | Mock 站点固定账号 |

生效顺序：`BASE_URL` / `ENV` / `HEADLESS` 环境变量 → `config/env_local.yaml` → `config/env.yaml`。
`env_local.yaml` 只写要覆盖的字段，结构同 `env.yaml`。

## 测试数据

`data/test_data.yaml` 存放会变的参数，用例从 `load_test_data()` 读：

```yaml
album:
  search_keyword: "日常照片"
  initial_count: 3
camera:
  default: { resolution: "1080P", fps: 30 }
  high:    { resolution: "4K", fps: 60 }
browser:
  collect_limit: 200
dj:
  volume: 60
  eq: "rock"
  eq_text: "摇滚"
  play_mode: "loop"
  play_mode_text: "列表循环"
```

改参数（比如换成 720P 或调整收藏上限）只需要改这里，用例代码不动。
`eq_text` / `play_mode_text` 是页面上显示的中文，用来断言回显；`eq` / `play_mode` 是 `<option value>`，用来操作。

## 新增一条用例

### 同一页面加场景

在已有的 page 类里加一个方法（如果现有方法不够用），再在对应 test 文件里加一条：

```python
@allure.story("搜索不存在的相册")
def test_search_not_exist(self, page):
    album = AlbumManagePage(page)
    album.enter_album_page()
    album.search_album_name("不存在的相册")
    assert album.remaining_albums() == 0, "检索不存在的相册应无结果"
```

### 加一个新页面

1. `mock_site/app.py` 加路由和页面 HTML，元素 id / name 要和后面写的定位器对得上；
2. `page_objects/` 新建一个 page 类，继承 `BasePage`，定义 `path` 和定位器，操作方法不写断言；
3. `testcases/` 新建测试文件，构造 page 对象、调方法、写断言；
4. 需要新参数就加到 `data/test_data.yaml`。

### 断言怎么写

页面上有明确反馈的，断言反馈本身和回显值两处，不要只判断「点了没报错」：

```python
assert cam.is_visible(cam.save_tip), "应出现「配置保存成功」提示"
preview = cam.current_preview()
assert "1080P" in preview, "分辨率回显应为 1080P"
```

只断言可见性容易漏掉「提示出现了但值没写进去」这类问题。

## fixture 设计

`testcases/conftest.py` 里有四个 fixture，作用域不同，混用会导致状态串味：

| fixture | 作用域 | 作用 |
| --- | --- | --- |
| `site_ready` | session，autouse | 起手调 `/__admin/reset`，站点没起来时给出明确报错 |
| `engine` | session | 整个 session 只启动一次 Chromium，结束时关闭 |
| `page` | function | 新 context + page，自动登录，用例结束后关闭 context |
| `fresh_site` | function | 再调一次 `/__admin/reset`，给破坏性用例（批量删除）用 |

为什么每个用例都新建 context：不同用例登录态、页面滚动位置、DOM 改动互不影响；
代价是每个用例多一次登录（约 0.3 秒），8 条用例整体 15 秒左右，可以接受。
如果用例数上百，可以改成 session 级 `storage_state` 复用登录态。

## 踩过的坑

**1. `conftest.py` 放在 `common/` 下，fixture 不生效**

pytest 只会加载 rootdir 和用例目录树下的 `conftest.py`。放在 `common/` 里，
用例会直接报 `fixture 'page' not found`，全部失败。现已移到 `testcases/conftest.py`。

**2. 浏览器在 import 时就被启动**

旧写法是模块级 `web_driver = BrowserEngine()`，pytest 收集用例阶段就会启动 Chromium，
`headless=False` 时还会弹窗。现在改为由 `engine` fixture 创建，收集阶段不碰浏览器。

**3. 隐藏的弹窗挡住了按钮点击**

弹窗初始状态是 `<div hidden class="modal">`，样式里写了 `.modal { display: flex }`，
`display: flex` 覆盖了 `hidden` 默认的 `display: none`，元素实际仍然占位，
Playwright 报 `intercepts pointer events`，点了 10 秒超时。

```css
.modal { display: flex; }
.modal[hidden] { display: none; }   /* 必须补这一条 */
```

用 `hidden` 属性控制显隐时，如果该元素有 `display` 类样式，务必补一条 `[hidden]` 规则。

**4. 三个页面的保存按钮名字不一样**

浏览器配置页是「保存」，相机配置页是「保存配置」，DJ 页是「保存设置」。
`text()='保存'` 是精确匹配，只命中浏览器页；如果为了「通用」改成 `contains(text(),'保存')`，
三个页面都会命中，且定位到的是第一个匹配元素，点到哪个页面上就不确定了。
三个页面各自维护自己的定位器，不做「通用保存按钮」这种抽象。

## 报告与日志

```powershell
pytest
allure generate report/allure_raw -o report/allure_html --clean
allure open report/allure_html
```

- 日志：`report/logs/admin_web_YYYYMMDD.log`，记录每次页面跳转和提示出现
- Allure：按页面分组，失败时可以直接看到断言消息
- 需要失败截图时，在 page 类里调 `screenshot(path)`，`BasePage` 已封装

## CI

`docker-compose.yml` 用官方镜像 `mcr.microsoft.com/playwright/python`，镜像自带 Chromium，
容器里不用再 `playwright install`。站点容器跑 `mock_site/app.py`，用例容器的 `BASE_URL` 指向服务名。

`Jenkinsfile` 用同一个镜像作为 agent，流程是：拉代码 → 轮询 `/health` → 装依赖 → 跑 pytest → 发布报告。
宿主机起站点时用 `host.docker.internal:9100`。

## 排错对照

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `fixture 'page' not found` | `conftest.py` 不在用例目录树内 | 确认文件在 `testcases/conftest.py` |
| `Executable doesn't exist ... chromium` | 没装浏览器内核 | `playwright install chromium` |
| 启动就报 `RuntimeError` 站点未启动 | `mock_site` 没起 | `python mock_site/app.py`，或 `python run.py` |
| 点击超时，提示 `intercepts pointer events` | 有隐藏元素挡住了目标 | 用 `hidden` 控制显隐时补 `[hidden] { display: none }`，或改用 `visible` 判断后再点 |
| 断言提示文案失败，但页面看着有提示 | 同一个提示 div 被别的操作改了文本 | 提示文案断言用 `contains`，不要用 `text()` 全等 |
| CI 里弹窗、跑得慢 | `headless` 没开或 `slow_mo` 没关 | 环境变量 `HEADLESS=true`，`SLOW_MO=0` |
| 用例单独跑通过，一起跑失败 | 用了上一个用例的页面状态 | 确认破坏性用例挂了 `fresh_site`，不要跨用例传数据 |

## 已知限制

- 只跑 Chromium，没有做 Firefox / WebKit 的跨浏览器矩阵。
- 用例按串行执行，没有并发方案；`pytest-xdist` 需要每个 worker 独立站点实例才能用。
- 断言用原生 `assert`，失败信息靠消息文本，没有做统一断言层。
- 站点是纯前端 JS 模拟，没有真实后端和数据库，只能验证交互和回显，验证不了服务端逻辑。
