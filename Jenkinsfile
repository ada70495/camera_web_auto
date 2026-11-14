// ============================================
// mobile_admin_web_auto —— Jenkins 流水线
//
// 前提：
//   1. 宿主机已启动本地站点：docker compose up -d admin-site（监听 9100）
//   2. Jenkins 使用 Playwright 官方镜像执行（自带 Chromium），或宿主机已 playwright install chromium
//   3. 容器访问宿主机用 host.docker.internal
//   4. 需要插件：JUnit、Allure Jenkins Plugin
// ============================================

pipeline {
    agent {
        docker {
            // 官方镜像自带浏览器内核
            image 'mcr.microsoft.com/playwright/python:v1.49.0-jammy'
            reuseNode true
        }
    }

    environment {
        ENV = 'ci'
        BASE_URL = 'http://host.docker.internal:9100'
        HEADLESS = 'true'
        PYPI = 'https://pypi.tuna.tsinghua.edu.cn/simple'
    }

    stages {
        stage('1. 拉取代码') {
            steps {
                git url: 'https://github.com/ada70495/mobile_admin_web_auto.git', branch: 'main'
            }
        }

        stage('2. 等待后台站点就绪') {
            steps {
                sh '''
                    echo "等待站点：$BASE_URL/health"
                    for i in $(seq 1 30); do
                        if curl -fsS "$BASE_URL/health" >/dev/null 2>&1; then
                            echo "站点已就绪"
                            exit 0
                        fi
                        sleep 2
                    done
                    echo "站点未就绪，请先在宿主机执行：docker compose up -d admin-site"
                    exit 1
                '''
            }
        }

        stage('3. 安装依赖') {
            steps {
                sh '''
                    python3 -m pip install -q -i $PYPI pytest allure-pytest pytest-rerunfailures pyyaml loguru requests
                    python3 -m pytest --version
                '''
            }
        }

        stage('4. 执行 UI 用例') {
            steps {
                sh '''
                    mkdir -p report
                    python3 -m pytest \\
                        --junitxml=report/junit-result.xml \\
                        --alluredir=report/allure_raw
                '''
            }
        }
    }

    post {
        always {
            junit testResults: 'report/junit-result.xml', allowEmptyResults: true
            allure includeProperties: false, jdk: '', results: [[path: 'report/allure_raw']]
            archiveArtifacts artifacts: 'report/**', allowEmptyArchive: true
        }
        success {
            echo '后台管理 UI 自动化全部通过'
        }
        failure {
            echo 'UI 用例存在失败，请查看 Allure 报告与截图'
        }
    }
}
