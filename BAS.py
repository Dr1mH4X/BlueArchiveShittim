import json
import time
import os
import subprocess
import cv2  # opencv实现图像模板匹配定位
import numpy as np

with open('config.json', 'r') as f:     # 读取config.json文件
    config = json.load(f)

ip_address = config.get('ip_address')   # 获取ip_address
port = config.get('port')               # 获取port
mumu_path = config.get('mumu_path')     # 获取mumu_path

with open('basmainconfig.json', 'r') as f:
    basconfig = json.load(f)

SETTING_SIGN_REWARD = basconfig.get('SIGN_REWARD')
SETTING_CLUB = basconfig.get('CLUB')
mumu_manager_path = os.path.join(mumu_path, 'shell', 'MumuManager.exe')     # 获取MumuManager.exe路径
MUMU_ADB_PATH = os.path.join(mumu_path, 'shell', 'adb.exe')                 # MuMu的adb路径
LOCAL_ADB_PATH = os.path.join('adb', 'adb.exe')                             # 本地adb路径
current_dir = os.path.dirname(os.path.abspath(__file__))                    # 构造相对路径
# 包名获取
JP_PACKAGE_NAME = 'com.YostarJP.BlueArchive'
# 模板图片路径获取
# JP_APPICON_PATH = os.path.join('galbol', 'yostarjapan', 'resources', 'template', 'appicon.jpg')       # MuMuManager使用包名启动应用
JP_LOGIN_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'login.png')
JP_SIGN_REWARDS_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'sign_rewards.png')
JP_CLOSE_NEWS_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'close_news.png')
JP_SOCIAL_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'social.png')
JP_CLUB_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'club.png')
JP_OK_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'ok.png')
JP_HOME_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'home.png')
JP_MAIL_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'mail.png')
JP_RECEIVE_MAIL_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'receive_mail.png')
JP_SCHOOL_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'school.png')
JP_SCHOOL01_PATH = os.path.join('golbal', 'yostarjapan', 'resources', 'template', 'school01.png')
current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

template = os.path.join('screenshot', 'BASscreencap.png')

class Template:
    def __init__(self):
        self.template = template
    
    def match(self, template_path, target_path):
        start_time = time.time()
        while True:
            if time.time() - start_time > 60:
                break
            target_image = cv2.imread(target_path)  # 读取截图
            template_image = cv2.imread(template_path)
            target_gray = cv2.cvtColor(target_image, cv2.COLOR_BGR2GRAY)  # 转换为灰度图 
            template_gray = cv2.cvtColor(template_image, cv2.COLOR_BGR2GRAY)
            w, h = template_gray.shape[::-1]  # 获取模板图片宽高
            match = cv2.matchTemplate(target_gray, template_gray, cv2.TM_CCOEFF_NORMED)  # 模板匹配
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(match)
            threshold = 0.8
            if max_val > threshold:
                top_left = max_loc
                bottom_right = (top_left[0] + w, top_left[1] + h)
                center_x = top_left[0] + w // 2
                center_y = top_left[1] + h // 2
                template_center_point = (center_x, center_y)
                time.sleep(0.5)
                yield template_center_point
            else :
                yield None

class Connect:                          # 连接adb/MuMuManager
    def __init__(self, mumu_manager_path, MUMU_ADB_PATH, LOCAL_ADB_PATH, ip_address, port):     # 初始化
        self.mumumanager_path = mumu_manager_path
        self.MUMU_ADB_PATH = MUMU_ADB_PATH
        self.LOCAL_ADB_PATH = LOCAL_ADB_PATH
        self.ip_address = ip_address
        self.port = port

    def connect_mumumanager(self):      # 连接MuMuManager
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{current_time}] 正在连接MuMuManager...')
        MUMU_NUM = 0
        while True:
            connect_mumumanager = subprocess.run([self.mumumanager_path, 'api' , '-v', str(MUMU_NUM), 'player_state' ], capture_output=True, text=True) # MuMuManager.exe api -v [模拟器序号] player_state  //获取模拟器状态
            if 'current select player index: {}'.format(MUMU_NUM) in connect_mumumanager.stdout.strip() and 'check player state: state=start_finished' in connect_mumumanager.stdout.strip():
                # print(connect_mumumanager.stdout)     # 调试信息，输出MuMuManager.exe api -v [模拟器序号] player_state的输出
                # MuMuManager.exe adb -v [模拟器序号] connect  //连接指定模拟器adb端口
                subprocess.run([self.mumumanager_path, 'adb', '-v', str(MUMU_NUM), 'connect'], capture_output=True, text=True)
                # print(f'[{current_time}]已连接MuMuManager')
                # 从Startup类的startup_app开始执行
                return MUMU_NUM
            MUMU_NUM += 1
            if MUMU_NUM == 10:
                current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                print(f'[{current_time}] 连接MuMuManager失败')
                return None
            
    def screenshot_time(self, MUMU_NUM):
        start_time = time.time()
        subprocess.run([self.mumumanager_path, 'adb', '-v', str(MUMU_NUM), 'shell', 'screencap', '-p', '/sdcard/Screenshots/BASscreencap.png'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([mumu_manager_path, 'adb', '-v', str(MUMU_NUM), 'pull', '/sdcard/Screenshots/BASscreencap.png', './screenshot/BASscreencap.png'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        end_time = time.time()
        single_screenshot_time = end_time - start_time
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{current_time}] 截图耗时: ', single_screenshot_time)
    
    def mumumanager_screenshots(self, MUMU_NUM):
        # while True: # ~~进入MuMuMnager的adbshell，在connect_mumumanager获取到MUMU_NUM后执行，然后等待判断应用是否启动后进入shell 开始0.5s/截图并拉取~~ 去除无限循环，改为在主程序中匹配时才调用循环     
        subprocess.run([self.mumumanager_path, 'adb', '-v', str(MUMU_NUM), 'shell', 'screencap', '-p', '/sdcard/Screenshots/BASscreencap.png'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.run([mumu_manager_path, 'adb', '-v', str(MUMU_NUM), 'pull', '/sdcard/Screenshots/BASscreencap.png', './screenshot/BASscreencap.png'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
    def connect_adb(self):              # 连接adb 后面再写 先用MuMuManager
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{current_time}] 正在连接adb...')
        pass

class Startup:

    def __init__(self, mumu_manager_path, MUMU_ADB_PATH, ip_address, port, JP_PACKAGE_NAME):
        self.mumumanager_path = mumu_manager_path
        self.MUMU_ADB_PATH = MUMU_ADB_PATH
        self.ip_address = ip_address
        self.port = port
        self.JP_PACKAGE_NAME = JP_PACKAGE_NAME

    def startup_app(self, MUMU_NUM):
        #MuMuManager.exe api -v [模拟器序号] launch_app [package]  //启动app，带包名
        subprocess.run([self.mumumanager_path, 'api', '-v', str(MUMU_NUM), 'launch_app', JP_PACKAGE_NAME], capture_output=True, text=True)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{current_time}] 已启动什亭之匣')

class Click:

    def __init__(self, mumu_manager_path, MUMU_ADB_PATH, MUMU_NUM, ip_address, port):
        self.mumumanager_path = mumu_manager_path
        self.MUMU_ADB_PATH = MUMU_ADB_PATH
        self.MUMU_NUM = MUMU_NUM
        self.ip_address = ip_address
        self.port = port
        self.device_uuid = f'{ip_address}:{port}'

    def send_touch_event(self, x, y):
        # 模拟按下
        press_cmd = [
            self.mumumanager_path, 
            'adb', 
            '-v', 
            str(self.MUMU_NUM), 
            'shell', 
            'input tap', 
            str(x), 
            str(y), 
        ]
        subprocess.run(press_cmd)
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{current_time}] Using ADB Input Tap: {x} {y}')
        
if __name__ == "__main__":  # 创建 Connect 类实例并连接 MuMuManager
    connect_instance = Connect(mumu_manager_path, MUMU_ADB_PATH, LOCAL_ADB_PATH, ip_address, port)
    MUMU_NUM = connect_instance.connect_mumumanager()

    if MUMU_NUM is not None:
        startup_instance = Startup(mumu_manager_path, MUMU_ADB_PATH, ip_address, port, JP_PACKAGE_NAME)                         # 创建 Startup 类实例
        startup_instance.startup_app(MUMU_NUM)
        connect_instance.screenshot_time(MUMU_NUM)                                                                              # 创建Connect类实例
        connect_instance.mumumanager_screenshots(MUMU_NUM)
        template_instance = Template()                                                                                          # 创建 Template 类实例
        templates_to_match = [JP_LOGIN_PATH]                                                                                    # 列表中可以包含多个模板路径
        match_points = []
        click_instance = Click(mumu_manager_path, MUMU_ADB_PATH, MUMU_NUM, ip_address, port)                     # 创建Click类实例
        for template_path in templates_to_match:  # 循环等待模板匹配
            match_generator = template_instance.match(template_path, template)
            while True:
                connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                template_center_point = next(match_generator)
                if template_center_point is not None:
                    match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                    click_instance.send_touch_event(600, 600)
                    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    print(f'[{current_time}] Login Success')
                    break
                else:
                    time.sleep(2)

        if SETTING_SIGN_REWARD==1:
            templates_to_match = [JP_SIGN_REWARDS_PATH]  # 列表中可以包含多个模板路径
            match_points = []
            for template_path in templates_to_match:  # 循环等待模板匹配
                match_generator = template_instance.match(template_path, template)
                while True:
                    connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                    template_center_point = next(match_generator)
                    if template_center_point is not None:
                        match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                        click_instance.send_touch_event(600, 600)
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        print(f'[{current_time}] Login Rewards Success')
                        break
                    else:
                        time.sleep(2)

            templates_to_match = [JP_CLOSE_NEWS_PATH]
            match_points = []
            for template_path in templates_to_match:  # 循环等待模板匹配
                match_generator = template_instance.match(template_path, template)
                while True:
                    connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                    template_center_point = next(match_generator)
                    if template_center_point is not None:
                        match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                        click_instance.send_touch_event(*template_center_point)
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        print(f'[{current_time}] Close news Success')
                        break
                    else:
                        time.sleep(2)

        else:
            templates_to_match = [JP_CLOSE_NEWS_PATH]
            match_points = []
            for template_path in templates_to_match:  # 循环等待模板匹配
                match_generator = template_instance.match(template_path, template)
                while True:
                    connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                    template_center_point = next(match_generator)
                    if template_center_point is not None:
                        match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                        click_instance.send_touch_event(*template_center_point)
                        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                        print(f'[{current_time}] Close news Success')
                        break
                    else:
                        time.sleep(2)

            if SETTING_CLUB==1:
                templates_to_match = [JP_SOCIAL_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Go To Social Success')
                            break
                        else:
                            time.sleep(2)

                templates_to_match = [JP_CLUB_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Receive Success')
                            break
                        else:
                            time.sleep(2)
                
                templates_to_match = [JP_OK_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            break
                        else:
                            time.sleep(2)

                templates_to_match = [JP_HOME_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Back Home Success')
                            break
                        else:
                            time.sleep(2)

                templates_to_match = [JP_MAIL_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Go Mail Success')
                            break
                        else:
                            time.sleep(2)
                            
                templates_to_match = [JP_RECEIVE_MAIL_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Receive Mail Success')
                            break
                        else:
                            time.sleep(2)
                
                templates_to_match = [JP_OK_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            break
                        else:
                            time.sleep(2)

                templates_to_match = [JP_HOME_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Back Home Success')
                            break
                        else:
                            time.sleep(2)

            else:
                templates_to_match = [JP_SCHOOL_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Go School Success')
                            break
                        else:
                            time.sleep(2)

                templates_to_match = [JP_SCHOOL01_PATH]
                match_points = []
                for template_path in templates_to_match:  # 循环等待模板匹配
                    match_generator = template_instance.match(template_path, template)
                    while True:
                        connect_instance.mumumanager_screenshots(MUMU_NUM)  # 更新截图
                        template_center_point = next(match_generator)
                        if template_center_point is not None:
                            match_points.append(template_center_point)  # Click用的时候*template_center_point展开为x,y
                            click_instance.send_touch_event(*template_center_point)
                            current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                            print(f'[{current_time}] Go School01 Success')
                            break
                        else:
                            time.sleep(2)

        
# next class
        

    else:
        current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{current_time}] 无法连接到 MuMuManager')