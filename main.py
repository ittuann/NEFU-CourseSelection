# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from datetime import datetime
import threading
from time import sleep

from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options

DRIVER_PATH = r"C:\Download\chromedriver_win32\chromedriver.exe"
TIME_OUT = 30                                   # 教务系统选课时最长无响应等待时间
SLEEP_TIME = 2                                  # 登录成功后延时等待时间
URL_MAX_ATTEMPTS = 100                          # 页面加载失败后最大尝试次数

# 使用 Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')       # 无头模式
# chrome_options.add_argument('--disable-gpu')    # 禁用GPU加速
chrome_options.add_argument('--blink-settings=imagesEnabled=false')  # 禁用图片加载


def continue_driver_get(driver, url, max_attempts):
    attempt = 0
    while attempt < max_attempts:
        try:
            driver.get(url)
            break
        except WebDriverException as err:
            print("加载网页时发生错误:", str(err))
            attempt += 1
            if attempt < max_attempts:
                print(f"正在尝试重新加载网页 {url} 尝试次数: {attempt}/{max_attempts}")
            else:
                print(f"达到最大尝试次数 {max_attempts} 次，停止加载网页。")
        finally:
            if attempt >= max_attempts:
                driver.quit()


def continue_driver_find_element_by_xpath(driver, xpath, send_key, reload_url):
    while True:
        try:
            driver.find_element_by_xpath(xpath).send_keys(send_key)
            break
        except WebDriverException as err:
            # 防止高负载下教务系统网页返回不全导致无法登录
            print("登录时出现网页错误:", str(err))
            print("正在尝试重新加载网页...")
            continue_driver_get(driver, reload_url, URL_MAX_ATTEMPTS)
            continue


def login():
    driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=chrome_options)

    # 登录WebVPN
    if IS_WEBVPN:
        continue_driver_get(driver, 'https://jwcnew.webvpn.nefu.edu.cn/dblydx_jsxsd/xk/AccessToXk',
                            URL_MAX_ATTEMPTS)

        continue_driver_find_element_by_xpath(driver, '//*[@id="un"]',
                                              str(student_id),
                                              'https://jwcnew.webvpn.nefu.edu.cn/dblydx_jsxsd/xk/AccessToXk')
        driver.find_element_by_xpath('//*[@id="pd"]').send_keys(str(student_pwd))
        driver.find_element_by_xpath('//*[@id="rememberName"]').click()
        driver.find_element_by_xpath('//*[@id="index_login_btn"]/input').click()
        sleep(SLEEP_TIME)   # 登录成功后延时等待

        # 继续登录教务系统
        continue_driver_find_element_by_xpath(driver, '//*[@id="Form1"]/div/div/div[2]/div[1]/div[2]/input[1]',
                                              str(student_id),
                                              'https://jwcnew.webvpn.nefu.edu.cn/dblydx_jsxsd/xk/AccessToXk')
        driver.find_element_by_xpath('//*[@id="pwd"]').send_keys(str(student_pwd))
        driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()

    else:
        # 校园网内网登录
        continue_driver_get(driver, 'http://jwcnew.nefu.edu.cn/dblydx_jsxsd/',
                            URL_MAX_ATTEMPTS)    # 不用https

        continue_driver_find_element_by_xpath(driver, '//*[@id="Form1"]/div/div/div[2]/div[1]/div[2]/input[1]',
                                              str(student_id),
                                              'http://jwcnew.nefu.edu.cn/dblydx_jsxsd/')
        driver.find_element_by_xpath('//*[@id="pwd"]').send_keys(str(student_pwd))
        driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()

    print(f"登录成功！ {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    sleep(SLEEP_TIME)       # 登录成功后延时等待
    return driver


def select_course(web_page, select_name, info):
    print("脚本开始运行！")

    driver = login()
    continue_driver_get(driver, web_page, URL_MAX_ATTEMPTS)

    # 获取全部课程名称
    element = None
    while True:
        try:
            element = driver.find_element_by_css_selector('#divFrmLeft')
            break
        except WebDriverException as err:
            # 防止高负载下教务系统网页返回不全导致无法登录
            print("获取全部课程名称时出现网页错误:", str(err))
            print("正在尝试重新加载网页...")
            continue_driver_get(driver, web_page, URL_MAX_ATTEMPTS)
            continue
    tr = element.find_elements_by_xpath("//tr[contains(@id,'xk')]")
    id_list = []
    course_list = []
    name_list = []
    for td in tr:
        id_list.append(td.get_attribute("id"))
        course_list.append(td.text)
    for course_name in course_list:
        name_list.append(course_name.split()[4])  # 获得所有课程名字
    name_id_dict = dict(zip(name_list, id_list))  # 课程与课程代码键值对
    print(f"获取全部课程成功 {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

    if select_name in name_id_dict:
        print(f"查询成功！正在选 {select_name} 这门课 {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
    else:
        print("查询失败，请确认该页面是否有该课程。")
        return

    # 开始抢课
    try:
        attempt = 1
        while True:
            driver.find_element_by_xpath('//*[@id="%s"]/td[1]/a' % name_id_dict[select_name]).click()
            alert = driver.switch_to.alert
            alert.accept()

            wait = WebDriverWait(driver, timeout=TIME_OUT)      # 显式等待下一个alert弹出 频率为0.5s
            alert = None
            while alert is None:
                try:
                    alert = wait.until(ec.alert_is_present())   # 等待弹窗出现
                except TimeoutException:
                    driver.quit()
                    print(f"重新登录中 {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
                    driver = login()
                    print(f"重新登录成功！ {datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")

            if alert.text == '选课成功！':
                print(alert.text)
                break
            msg = "课程\"{}\"第{}线程的第{}次尝试: {} {}".format(
                select_name,
                info,
                attempt,
                alert.text,
                datetime.now().strftime("%d-%H:%M:%S.%f")[:-3]
            )
            print(msg)
            alert.accept()
            attempt += 1
    except WebDriverException as err:
        print(str(err))
    driver.close()


def run_threads(web_page, selected_names, course_thread_counts):
    threads = []
    for select_name in selected_names:
        for num in range(course_thread_counts):
            thread = threading.Thread(target=select_course, args=(web_page, select_name, num))
            # 启动线程
            threads.append(thread)
            thread.start()
    # 等待所有线程完成
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    # select_course(website, select_name)

    # 处理输入
    student_id = input("请输入学号:")
    student_pwd = input("请输入密码:")
    IS_WEBVPN = True
    website = input("请输入选课页面的网址:")
    select_names = []
    course_thread_count = int(input("请输入抢每门课程要同时并发的线程数量:"))

    webvpn_input = input("请输入是否使用校园外网WebVPN (True/False):").lower()
    if webvpn_input == "false":
        IS_WEBVPN = False
    else:
        IS_WEBVPN = True
    select_names = input("请输入完整的课程名称 (多个课程名称之间用空格分隔):").split()
    course_thread_count = max(course_thread_count, 1)

    run_threads(website, select_names, course_thread_count)
