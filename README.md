# mobile_admin_web_auto
基于Playwright+标准PO分层架构的后台UI自动化项目，用于相册/相机/手机浏览器后台配置平台版本回归

## 技术栈
Python3 + Playwright + Pytest + PO分层设计 + Allure可视化报告

## 分层架构
1. common：浏览器驱动、日志、全局前置后置统一封装
2. config：后台地址、账号、超时统一配置管理
3. page_objects：标准PO层，页面元素、操作全部封装，页面修改只改此处
4. testcases：测试用例层，只写业务流程，完全不写元素定位
5. report：运行日志、Allure可视化报告

## 核心优势
1. BasePage封装全部通用操作+显式等待，彻底解决传统Selenium自动化元素不稳定、超时报错问题
2. PO分层完全解耦：前端页面改版只修改对应page文件，测试用例无需改动，大幅降低维护成本
3. 完整适配办公后台场景：搜索、批量勾选、批量删除、弹窗确认、参数保存
4. 贴合本职测试：相册资源管理、相机参数配置、浏览器后台管控三大业务

## 业务覆盖
相册管理：相册检索、图片上传、批量删除
相机配置：分辨率、帧率、水印开关配置保存
浏览器配置：缓存一键清理、收藏最大数量配置

## 运行步骤
1. pip install -r requirements.txt
2. 执行浏览器驱动安装：playwright install chrome
3. python run.py 一键执行全部用例