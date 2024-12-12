# adb_operations.py
import uiautomator2 as u2
import os
import time

def Adbconn():                                                  # adb连接
    ADBaddress = input(f"输入ADB地址，格式为 [IP]:[PORT]\n")      # 获取ADB连接地址
    # print("尝试连接ADB：", ADBaddress)
    os.system(f'adb connect {ADBaddress}')
    status = u2.connect()                                       # connect to device
    width, height = status.window_size()                        # 获取屏幕信息
    if width == 1280 and height == 720:                         # 判断屏幕大小 
        print(f"屏幕大小为：{width}x{height}")
        diserror = 0
    else:
        print(f"屏幕大小错误，请设置为1280x720！")
        diserror = 1
    current_info = status.app_current()  
    if current_info['package'] == "com.YostarJP.BlueArchive":   #判断当前应用是否为日服BA，是则继续，否则打开
        print(f"当前前台已运行日服碧蓝档案")
    else:
        app = status.session("com.YostarJP.BlueArchive")        # 启动应用并获取session # session的用途是操作的同时监控应用是否闪退，当闪退时操作，会抛出SessionBrokenError
        print(f"启动碧蓝档案[jp]")
    return ADBaddress,diserror

def Adbdisconn(ADBaddress):                                     # adb断开
    os.system(f'adb disconnect {ADBaddress}')
    # print("ADB已释放")

def Adbstart(ADBaddress, diserror):                             # 屏幕大小错误则提示用户并断开ADB
    if diserror == 1:
        Adbdisconn(ADBaddress)
    return 0

def Screenshot(WorkSignal):
    status = u2.connect()
    screenshot_dir = './workspace/screenshot'
    screenshot_path = os.path.join(screenshot_dir, 'current_screen.jpg')
    os.makedirs(screenshot_dir, exist_ok=True)                  # 确保目录存在

    if WorkSignal == 1:
        while Screenshot.running:
            try:
                # 截图并保存
                status.screenshot().save(screenshot_path)
            except Exception as e:
                print(f"Error saving screenshot: {e}")
            time.sleep(1)
Screenshot.running = False                                      # 初始状态为未运行
    

def CompareScreenshot(Template):
    import cv2
    threshold = 0.8                                             # 匹配相似度
    img_path = './workspace/screenshot/current_screen.jpg'
    template_path = os.path.join('./workspace/resource/jp/', f'{Template}.png')
    while True:
        img = cv2.imread(img_path)
        template_img = cv2.imread(template_path) 
        if img is None:
            print(f"Error: Unable to read screenshot from {img_path}")
        if template_img is None:
            print(f"Error: Unable to read template image from {template_path}")
        h, w = template_img.shape[:2]
        result = cv2.matchTemplate(img, template_img, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, _ = cv2.minMaxLoc(result)
        if max_val >= threshold:                                # 判断是否匹配成功
            print(f"找到{Template}")
            if os.path.exists('./workspace/screenshot/current_screen.jpg'):
                os.remove('./workspace/screenshot/current_screen.jpg')  # 删除文件
                # print(f"current_screen.jpg 文件已删除")
            else:
                print(f"current_screen.jpg 文件不存在")
            return 1
        else:
            time.sleep(1.5)

def Touch(location):                                            # 例：Touch('login')
    import json
    with open('./workspace/location.json', 'r') as file:
        data = json.load(file)
    coords = data.get(location)
    if coords is None:
        print(f"Error: '{location}' key not found in location.json")
        return
    x, y = coords
    status = u2.connect()
    status.click(x, y)
    print(f'click {x},{y}')

def main_task(Template, touch):                                 
    """
    主流程函数，协调 Screenshot、CompareScreenshot 和 Touch。
    通过 touch 参数判断是否需要触摸。
    :param Template: 模板图片，用于比对。
    :param touch: 布尔值，True 表示执行点击操作，False 表示仅比对不触摸。
    """
    import threading
    import time

    Screenshot.running = True                                   # 启动截图线程
    screenshot_thread = threading.Thread(target=Screenshot, args=(1,))
    screenshot_thread.start()
    time.sleep(1)                                               # 等待截图线程启动

    try:
        result = CompareScreenshot(Template)                    # 比对截图
        if result == 1:
            if touch:                                           # 判断是否需要点击
                Touch(Template)                                
                print(f"已完成动作「'{Template}'」")
            else:
                print(f"模板 '{Template}' 匹配成功，但未执行点击操作")
    finally:
        Screenshot.running = False                              # 停止截图
        screenshot_thread.join()                                # 等待线程结束

def touch_and_wait():
    time.sleep(5)
    Touch('next_calendar')
    time.sleep(2)
    Touch('next_calendar')
    time.sleep(2)
    Touch('next_calendar')