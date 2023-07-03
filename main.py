# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
# See PyCharm help at https://www.jetbrains.com/help/pycharm/

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import TimeoutException
from time import sleep
from datetime import datetime
import threading

driver_path = r"C:\Download\chromedriver_win32\chromedriver.exe"
time_out = 60
is_webvpn = True

student_id = input("请输入学号")
student_pwd = input("请输入密码")
website = input("请输入选课页面的网址")
select_names = []


# 使用 Chrome
chrome_options = Options()
chrome_options.add_argument('--headless')   # 无头模式


def login():
    try:
        driver = webdriver.Chrome(executable_path=driver_path, options=chrome_options)

        # 登录WebVPN
        if is_webvpn:
            driver.get('https://jwcnew.webvpn.nefu.edu.cn/dblydx_jsxsd/xk/AccessToXk')
            driver.find_element_by_xpath('//*[@id="un"]').send_keys(str(student_id))
            driver.find_element_by_xpath('//*[@id="pd"]').send_keys(str(student_pwd))
            driver.find_element_by_xpath('//*[@id="rememberName"]').click()
            driver.find_element_by_xpath('//*[@id="index_login_btn"]/input').click()
            sleep(2)  # 登录成功延时2s

            # 继续登录教务系统
            driver.get('https://jwcnew.webvpn.nefu.edu.cn/dblydx_jsxsd/xk/AccessToXk')  # 防止高负载下没有跳转
            driver.find_element_by_xpath('//*[@id="Form1"]/div/div/div[2]/div[1]/div[2]/input[1]').send_keys(
                str(student_id))
            driver.find_element_by_xpath('//*[@id="pwd"]').send_keys(str(student_pwd))
            driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()

        else:
            driver.get('https://jwcnew.nefu.edu.cn/dblydx_jsxsd/')  # 仅在学校内校园网有效
            driver.find_element_by_xpath('//*[@id="Form1"]/div/div/div[2]/div[1]/div[2]/input[1]').send_keys(
                str(student_id))
            driver.find_element_by_xpath('//*[@id="pwd"]').send_keys(str(student_pwd))
            driver.find_element_by_xpath('//*[@id="btnSubmit"]').click()

        print("登录成功！ %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
        sleep(2)  # 登录成功延时2s
    except Exception as err:
        print(str(err))
        print("请检查账号密码")
        return
    return driver


def select_course(web_page, select_name):
    # 获取全部课程名称
    driver = login()
    driver.get(web_page)
    element = driver.find_element_by_css_selector('#divFrmLeft')
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
    print("获取全部课程成功 %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

    if select_name in name_id_dict:
        print("查询成功！正在选 %s 这门课 %s" % (select_name, datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]))
    else:
        print("查询失败,请确认该页面是否有该课程")
        return

    # 开始抢课
    try:
        attempt = 1
        while True:
            driver.find_element_by_xpath('//*[@id="%s"]/td[1]/a' % name_id_dict[select_name]).click()
            alert = driver.switch_to.alert
            alert.accept()

            wait = WebDriverWait(driver, timeout=time_out)      # 显式等待下一个alert弹出 频率为0.5s
            alert = None
            while alert is None:
                try:
                    alert = wait.until(ec.alert_is_present())   # 等待弹窗出现
                except TimeoutException:
                    driver.quit()
                    print("重新登录中 %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])
                    driver = login()
                    print("重新登录成功！ %s" % datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3])

            if alert.text == '选课成功！':
                print(alert.text)
                break
            msg = "第{}次尝试：{} {}".format(
                attempt,
                alert.text,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
            )
            print(msg)
            alert.accept()
            attempt += 1
    except Exception as e:
        print(str(e))
    driver.close()


def run_threads(web_page, select__names):
    threads = []
    for select_name in select__names:
        thread = threading.Thread(target=select_course, args=(web_page, select_name))
        # 启动线程
        thread.start()
        threads.append(thread)
    # 等待所有线程完成
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    # select_course(website, select_name)

    # 处理输入
    while True:
        name = input("请输入课程名称 （名称打完后按回车完成输入，直接输入回车结束输入）：")
        if name == "":
            break
        select_names.append(name)
    webvpn_input = input("请输入是否使用校园外网WebVPN（True/False）：").lower()
    if webvpn_input == "true":
        is_webvpn = True
    else:
        is_webvpn = False

    run_threads(website, select_names)
