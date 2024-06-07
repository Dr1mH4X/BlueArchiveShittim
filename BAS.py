import json
import time
import os
import subprocess

with open('config.json', 'r') as f:     # 读取config.json文件
    config = json.load(f)

ip_address = config.get('ip_address')   # 获取ip_address
port = config.get('port')               # 获取port
mumu_path = config.get('mumu_path')     # 获取mumu_path

mumu_manager_path = os.path.join(mumu_path, 'shell', 'MumuManager.exe')     # 获取MumuManager.exe路径
MUMU_ADB_PATH = os.path.join(mumu_path, 'shell', 'adb.exe')                 # MuMu的adb路径
LOCAL_ADB_PATH = os.path.join('adb', 'adb.exe')                             # 本地adb路径
# 包名获取
JP_PACKAGE_NAME = 'com.YostarJP.BlueArchive'

# 模板图片路径获取
# JP_APPICON_PATH = os.path.join('galbol', 'yostarjapan', 'resources', 'template', 'appicon.jpg')       # MuMuManager使用包名启动应用
JP_LOGIN_PATH = os.path.join('galbol', 'yostarjapan', 'resources', 'template', 'login.jpg')

current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())         # 获取当前时间

class Connect:                          # 连接adb/MuMuManager
    def __init__(self, mumu_manager_path, MUMU_ADB_PATH, LOCAL_ADB_PATH, ip_address, port):     # 初始化
        self.mumumanager_path = mumu_manager_path
        self.MUMU_ADB_PATH = MUMU_ADB_PATH
        self.LOCAL_ADB_PATH = LOCAL_ADB_PATH
        self.ip_address = ip_address
        self.port = port

    def connect_mumumanager(self):      # 连接MuMuManager
        print(f'[{current_time}]正在连接MuMuManager...')
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
                print(f'[{current_time}]连接MuMuManager失败')
                return None
            
    def screenshot_time(self, MUMU_NUM):
        start_time = time.time()
        subprocess.run([self.mumumanager_path, 'adb', '-v', str(MUMU_NUM), 'shell', 'screencap', '-p', '/sdcard/Screenshots/BASscreencap.png'])
        subprocess.run([mumu_manager_path, 'adb', '-v', str(MUMU_NUM), 'pull', '/sdcard/Screenshots/BASscreencap.png', './screenshot/BASscreencap.png'])
        end_time = time.time()
        single_screenshot_time = end_time - start_time
        print(f'[{current_time}]截图耗时: ', single_screenshot_time)
    
    def mumumanager_screenshots(self, MUMU_NUM):
        # 进入MuMuMnager的adbshell，在connect_mumumanager获取到MUMU_NUM后执行，然后等待判断应用是否启动后进入shell
        while True:     # 开始0.5s/截图并拉取
            subprocess.run([self.mumumanager_path, 'adb', '-v', str(MUMU_NUM), 'shell', 'screencap', '-p', '/sdcard/Screenshots/BASscreencap.png'])
            subprocess.run([mumu_manager_path, 'adb', '-v', str(MUMU_NUM), 'pull', '/sdcard/Screenshots/BASscreencap.png', './screenshot/BASscreencap.png'])
            time.sleep(0.5)
                
    def connect_adb(self):              # 连接adb 后面再写 先用MuMuManager
        print(f'[{current_time}]正在连接adb...')
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
        print(f'[{current_time}]已启动什亭之匣')
        
if __name__ == "__main__":
    # 创建 Connect 类实例并连接 MuMuManager
    connect_instance = Connect(mumu_manager_path, MUMU_ADB_PATH, LOCAL_ADB_PATH, ip_address, port)
    MUMU_NUM = connect_instance.connect_mumumanager()

    if MUMU_NUM is not None:
        # 创建 Startup 类实例
        startup_instance = Startup(mumu_manager_path, MUMU_ADB_PATH, ip_address, port, JP_PACKAGE_NAME)
        startup_instance.startup_app(MUMU_NUM)
        connect_instance.screenshot_time(MUMU_NUM)
        connect_instance.mumumanager_screenshots(MUMU_NUM)
    else:
        print(f'[{current_time}] 无法连接到 MuMuManager')

# 包名启动有问题，打开一直黑屏，不知道是我的问题还是什么情况(...重启模拟器好了)， 换成模拟点击再试试 图片模板对比还没写