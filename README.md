# NEFU Fuxk Courses Selection

这是一个使用 selenium 编写的一个简单的林带自动选课抢课脚本，实现了多线程并发模拟输入并自动登录，以及批量数据爬取的功能。

# 使用方法

以 Windows 为例：

## 环境配置

首先需要简单的环境配置：

1. [下载脚本:](https://github.com/ittuann/NEFU-CoursesSelection/releases/latest) <https://github.com/ittuann/NEFU-CoursesSelection/releases/latest>

2. 需要 Python 环境，然后安装`Selenium`

   ```python
   pip install selenium
   ```

3. 然后需要下载 `Chrome Driver`

   打开 <https://chromedriver.chromium.org/downloads> 网页，找到适合的版本然后下载`chromedriver_win32.zip`

4. 将压缩包解压，并复制`chromedriver.exe`的路径

5. 修改脚本第`17`行`driver_path`变量，将路径更换成刚刚复制的内容。

   例如，把默认的内容

   ```python
   driver_path = r"C:\Download\chromedriver_win32\chromedriver.exe"
   ```

   修改为你的路径。如：

   ```python
   driver_path = r"D:\chromedriver.exe"
   ```

## 运行脚本

首先在Windows中搜索并打开 “命令提示符”

然后进入到脚本所在文件夹（文件夹的路径需要替换成你自己的）

```shell
cd C:\Users\Download\NEFUCourseSelection
```

之后即可运行脚本。

```shell
python main.py
```

脚本需要依次输入学号、密码、选课页面的网站、课程名称、抢每门课程要同时并发的线程数量、是否使用WebVPN

1. 选课页面的网站需要在教务系统中手动获得。在 `培养管理 -> 选课中心` ，复制`[进入选课]`的链接并粘贴到脚本即可。
2. 课程名称可以输入单个或多个，每行一个名称。
3. 是否使用WebVPN，取决于是否在校园网内。如果没连接校园网则必须使用，在校园网内则都可以。
4. 抢每门课程要同时并发的线程数量，就是字面意思，注意要输入一个大于等于1的数字。也不要输入太大的并发数量。

脚本使用示例：

```
请输入学号:1111111111
请输入密码:2222222222
请输入是否使用校园外网WebVPN (True/False):True
请输入选课页面的网址:https://jwcnew.webvpn.nefu.edu.cn/dblydx_jsxsd/xk/getXkInfo?jx0502zbid=333&jx0502id=133
请输入抢每门课程要同时并发的线程数量:2
请输入课程名称 (多个课程名称之间用空格分隔):西方文化名著导读 中国古典小说巅峰—四大名著鉴赏 创新工程实践
脚本开始运行！
...
```

脚本的原理简单来说就是每0.5s左右轮询来选一次这门课，检查是否有同学退课。或是当有奸商在尝试退掉课程准备去卖课的时候时，脚本也能以尽快的速度选上。如果网页长时间没有反应被弹出则自动重新登录。我测试的是在暑期小学期来抢通识教育选修课，挂一天抢到的概率还是蛮大的。

脚本对于每个课程都可以创建一个或多个独立并发的线程来抢课。当然也可以同时运行多个脚本。

最后，使用脚本后果自负，以及Fuxk抢课来卖的同学

# 运行截图

![RunScreenshot1](./img/RunScreenshot1.png)

![RunScreenshot1](./img/RunScreenshot2.png)
