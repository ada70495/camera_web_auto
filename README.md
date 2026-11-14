# camera_web_auto

后台管理站点「相机配置」页的 UI 自动化测试工程，用 Playwright 驱动 Chromium，按 PO（Page Object）分层。
覆盖分辨率与帧率设置、水印开关与位置、保存校验、配置回显、未保存不生效、未登录访问拦截。
技术栈：Python 3.13 + pytest + Playwright（Chromium）+ PyYAML + Allure + loguru，被测站点用 Flask 起在本地。

被测站点是仓库里的一个 Flask 应用（`mock_site/app.py`），带登录页和相机配置页，
元素结构与 `page_objects/` 里的定位器一一对应。克隆仓库、装好浏览器内核就能跑，当前 12 条用例。

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
| `playwright` | 浏览器驱动 | 同步 API，`sync_playwright()` |
| `pytest` | 用例组织与 fixture | `pytest.ini` 固定扫描路径，标记了 `ui` |
| `allure-pytest` | 报告 | 按 story 分组，失败可定位到断言 |
| `pytest-rerunfailures` | 失败重跑 | UI 抖动兜底，最多 1 次，间隔 2 秒 |
| `PyYAML` | 环境配置与测试数据 | `config/env.yaml`、`data/test_data.yaml` |
| `loguru` | 日志 | `report/logs/admin_web_日期.log` |
| `requests` | 调运维接口复位站点 | 只用于 `/__admin/reset`，不参与页面操作 |
| `flask` | 起被测站点 | 仅 `mock_site` 使用 |

安装：

```powershell
pip install -r requirements.txt
playwright install chromium
```

`playwright install chromium` 会下载约 200MB 浏览器内核，只需执行一次。

## 目录与职责

| 路径 | 职责 |
| --- | --- |
| `common/browser_handler.py` | 浏览器引擎。构造时才启动 Chromium，`new_page()` 每次返回独立 context + page |
| `common/conf_handler.py` | 读 `env.yaml` 与 `env_local.yaml`，产出 `config` 单例（base_url / timeout / headless / slow_mo） |
| `common/data_handler.py` | 读取 `data/test_data.yaml`，用例从这里取参数 |
| `common/logger_handler.py` | loguru 初始化 |
| `page_objects/base_page.py` | PO 父类：打开页面、显式等待后点击、填值、下拉选择、取文本、等待提示、截图 |
| `page_objects/login_page.py` | 登录页，`login()` 完成表单提交 |
| `page_objects/camera_page.py` | 相机配置页：分辨率、帧率、水印开关、水印位置、保存、读提示与回显 |
| `testcases/conftest.py` | `site_ready`（站点复位）、`engine`（浏览器）、`page`（已登录页面）、`anon_page`（未登录页面） |
| `testcases/test_camera.py` | 12 条用例，按 story 拆分，全部带断言 |
| `mock_site/app.py` | 被测站点：登录 + 相机配置页 + `/health` + `/__admin/reset` |
| `data/test_data.yaml` | 用例参数：默认/高/低三档分辨率与帧率、越界帧率、水印位置文案 |
| `run.py` | 起站点、跑用例、生成报告的入口 |

分层原则：元素定位只出现在 `page_objects/`，`testcases/` 里不出现 XPath。
页面改版只改 page 文件，用例不动。

## 跑起来

```powershell
# 方式一：一条命令（自动起站点、跑完自动关）
python run.py

# 方式二：分开执行
python mock_site/app.py    # 终端 1
pytest                      # 终端 2

# 只跑某一条
pytest testcases/test_camera.py -k position
```

正常输出结尾：

```
============================= 12 passed in 20.63s =============================
```

站点也可以直接在浏览器里点，用来对照用例行为：<http://127.0.0.1:9100/login>，账号 `testuser / 123456`。

调试时想看到浏览器逐步操作：

```powershell
$env:HEADLESS = "false"
$env:SLOW_MO = "500"     # 每个操作后停 500ms
pytest testcases/test_camera.py -k default
```

`HEADLESS` 和 `SLOW_MO` 也可以写进 `config/env_local.yaml`，不必每次设环境变量。

## 一次用例的执行过程

以「分辨率帧率 + 水印完整配置」为例：

```
testcases/test_camera.py::test_camera_full_config(page)
  → conftest.py::page                     新建 context + page，LoginPage 登录
  → CameraConfigPage.enter_camera_page()  goto /camera + 等 networkidle
  → set_camera_param("1080P", 30)         下拉选分辨率、填帧率
  → toggle_watermark()                    点击开关，位置下拉解除禁用
  → select_watermark_position("bottom")   选水印位置
  → save_config()                         点保存，等提示出现
  → 断言提示文案 + 回显文本（分辨率 / 帧率 / 水印状态 / 位置）
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
| `base_url` | 站点根地址 | 页面地址由 PO 的 `path` 拼出，如 `/camera` |
| `timeout` | 元素等待超时（毫秒） | 传给 `page.set_default_timeout` |
| `headless` | 是否无头 | CI 必须 `true`；本地调试可设 `false` |
| `slow_mo` | 每步操作后的停顿（毫秒） | 只用于观察，CI 里保持 0 |
| `account` | 登录账号 | Mock 站点固定账号 |

生效顺序：`BASE_URL` / `ENV` / `HEADLESS` 环境变量 → `config/env_local.yaml` → `config/env.yaml`。
`env_local.yaml` 只写要覆盖的字段，结构同 `env.yaml`。

## 测试数据

`data/test_data.yaml`：

```yaml
camera:
  default: { resolution: "1080P", fps: 30 }
  high:    { resolution: "4K", fps: 60 }
  low:     { resolution: "720P", fps: 15 }
  over_limit_fps: 61
  under_limit_fps: 14
  position:
    top: "top"
    top_text: "顶部"
    bottom: "bottom"
    bottom_text: "底部"
```

改参数只需要改这里，用例代码不动。`top` / `bottom` 是 `<option value>`，用来操作下拉；
`top_text` / `bottom_text` 是页面显示的中文，用来断言回显。

## 用例清单

| # | 用例 | 断言点 |
| --- | --- | --- |
| 1 | 默认配置回显 | 1080P / 30fps / 水印关闭 |
| 2 | 分辨率帧率 + 水印完整配置 | 提示文案 + 四项回显（含位置） |
| 3 | 切换到 4K | 回显 4K / 60fps，水印仍关闭 |
| 4 | 帧率下限边界 15 | 保存成功且回显生效 |
| 5 | 帧率 61 超上限 | 提示 15-60，回显不变 |
| 6 | 帧率 14 低于下限 | 提示 15-60，回显不含非法值 |
| 7 | 帧率为空 | 提示「帧率不能为空」 |
| 8 | 未开��水印时位置不可选 | 位置下拉 `disabled` |
| 9 | 开启水印后可选择位置 | 下拉可用 + 回显「顶部」 |
| 10 | 关闭水印后位置复位 | 下拉恢复 `disabled`，回显无位置文案 |
| 11 | 未保存的配置不生效 | 改成 4K 不保存，重新加载仍是 1080P |
| 12 | 未登录访问配置页 | 跳转到 `/login` |

## 新增一条用例

### 同一页面加场景

在 `camera_page.py` 里加方法（现有方法不够用时），再在 `test_camera.py` 里加一条：

```python
@allure.story("连续切换分辨率取最后一次")
def test_camera_multi_switch(self, page):
    cam = CameraConfigPage(page)
    cam.enter_camera_page()
    cam.set_camera_param("4K", 60)
    cam.set_camera_param("720P", 15)
    cam.save_config()

    preview = cam.current_preview()
    assert "720P" in preview, "应以最后一次选择为准"
    assert "15fps" in preview
```

### 加一个新页面

1. `mock_site/app.py` 加路由和 HTML，元素 `name` / `id` 要和后面写的定位器对得上；
2. `page_objects/` 新建 page 类，继承 `BasePage`，定义 `path` 和定位器，操作方法不写断言；
3. `testcases/` 新建测试文件，构造 page、调方法、写断言；
4. 需要新参数就加到 `data/test_data.yaml`。

### 断言怎么写

页面上有明确反馈的，同时断言提示和回显，不要只判「点了没报错」：

```python
cam.save_config()
assert "配置保存成功" in cam.tip_text(), "应出现保存成功提示"
preview = cam.current_preview()
assert "1080P" in preview, "分辨率回显应为 1080P"
```

只断言提示会漏掉「提示出现了但值没写进去」这一类问题；只断言回显会漏掉「值对了但没给用户反馈」。

## 实现要点

**1. `conftest.py` 必须放在用例目录下**

pytest 只加载 rootdir 和用例目录树下的 `conftest.py`。放在 `common/` 里，用例会报
`fixture 'page' not found`，全部失败。当前位置是 `testcases/conftest.py`。

**2. 浏览器不能在建模块时就启动**

旧写法是模块级 `web_driver = BrowserEngine()`，pytest 收集用例阶段就启动 Chromium，`headless=False` 还会弹窗。
现在由 `engine` fixture 创建，收集阶段不碰浏览器。

**3. 水印位置下拉是禁用状态**

未开启水印时 `select[name=watermark_position]` 带 `disabled`，Playwright 的 `select_option` 会一直等到超时。
用例顺序必须先点开关再选位置，中间用 `is_position_disabled()` 确认状态切换：

```python
cam.toggle_watermark()
assert not cam.is_position_disabled(), "开启水印后位置下拉应可用"
cam.select_watermark_position("bottom")
```

**4. 非法帧率只给提示，不回写回显**

前端在保存时校验帧率范围，非法值直接 return，回显区保持原值。用例要断言两件事：
提示里出现「15-60」，回显里不出现非法值——只断言提示会漏掉「非法值被写进配置」这类缺陷。

## 报告与日志

```powershell
pytest
allure generate report/allure_raw -o report/allure_html --clean
allure open report/allure_html
```

- 日志：`report/logs/admin_web_YYYYMMDD.log`，记录页面跳转和提示出现
- Allure：按页面与 story 分组，失败时直接看断言消息
- 失败截图：page 类里调 `screenshot(path)`，`BasePage` 已封装

## CI

`docker-compose.yml` 用 `mcr.microsoft.com/playwright/python` 镜像，镜像自带 Chromium，
容器里不需要再 `playwright install`。站点容器的 `BASE_URL` 指向服务名，用例容器同理。

`Jenkinsfile` 用同一镜像作为 agent：拉代码 → 轮询 `/health` → 装依赖 → 跑 pytest → 发布报告。
宿主机起站点时用 `host.docker.internal:9100`。

## 排错对照

| 现象 | 原因 | 处理 |
| --- | --- | --- |
| `fixture 'page' not found` | `conftest.py` 不在用例目录树内 | 确认文件在 `testcases/conftest.py` |
| `Executable doesn't exist ... chromium` | 没装浏览器内核 | `playwright install chromium` |
| 启动就报站点未启动 | `mock_site` 没起 | `python mock_site/app.py`，或 `python run.py` |
| 选位置时点击/选择超时 | 未开启水印，下拉是 `disabled` | 先 `toggle_watermark()` 再选位置 |
| 断言提示文案失败但页面看着有提示 | 提示 div 的文本被别的操作改写过 | 用 `in` 判包含，不要 `text()` 全等 |
| CI 里弹窗、跑得慢 | `headless` 没开或 `slow_mo` 没关 | `HEADLESS=true`、`SLOW_MO=0` |
| 单独跑通过、一起跑失败 | 复用了上一条用例的页面状态 | 每条用例独立 context，不要跨用例传数据 |

## 已知限制

- 只跑 Chromium，没有做 Firefox / WebKit 跨浏览器矩阵。
- 串行执行，没有并发方案；`pytest-xdist` 需要每个 worker 独立站点实例。
- 断言用原生 `assert`，失败信息靠消息文本，没有统一断言层。
- 站点是纯前端 JS 模拟，没有后端和数据库，只验证交互与回显，验证不了服务端持久化。
