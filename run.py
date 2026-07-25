import pytest
import os

if __name__ == "__main__":
    pytest.main()
    os.system("allure generate report/allure_raw -o report/allure_html --clean")
    print("Web自动化执行完成，Allure报告生成完毕")