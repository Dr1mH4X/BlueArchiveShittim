import os
import subprocess
import time
from PIL import Image, ImageChops, ImageStat, ImageFilter
import cv2
import numpy as np

def match_template(image_path, template_path, threshold=0.8):
    # 读取图像和模板
    img = cv2.imread(image_path, cv2.IMREAD_COLOR)
    template = cv2.imread(template_path, cv2.IMREAD_COLOR)

    # 获取模板的宽度和高度
    w, h = template.shape[:-1]

    # 使用matchTemplate
    res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # 输出匹配得分
    print(f"Match Score: {max_val}")

    # 确保至少有一个匹配结果
    if max_val >= threshold:
        # 输出匹配位置
        print(f"Match Location: {max_loc}")
        return max_loc
    else:
        print("No match found.")
        return None

def image_similarity(img1, img2, threshold=0.8):
    stat1 = ImageStat.Stat(img1)
    stat2 = ImageStat.Stat(img2)
    print(f"Stat1 Mean Type: {type(stat1.mean)}, Value: {stat1.mean}")
    print(f"Stat2 Mean Type: {type(stat2.mean)}, Value: {stat2.mean}")
    rms = (sum((s1-s2)**2 for s1,s2 in zip(stat1.mean, stat2.mean)) / len(stat1.mean))**0.5
    similarity = 1 - rms / max(sum(stat1.stddev) + sum(stat2.stddev), 1e-10)  
    print(f"RMS: {rms}, Similarity: {similarity}")
    return similarity >= threshold

class MuMuEmulator:
    def __init__(self, mumu_manager_path, emulator_path):
        self.mumu_manager_path = mumu_manager_path
        self.ip_address = '127.0.0.1'
        self.port = 16384

    def is_emulator_running(self):
        adb_path = os.path.join(os.path.dirname(self.mumu_manager_path), 'adb.exe')
        command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'get-state']
        try:
            output = subprocess.check_output(command, text=True)
            if output.strip() == 'device':
                return True
        except subprocess.CalledProcessError:
            pass
        return False

    def send_touch_event(self, x, y):
        adb_path = os.path.join(os.path.dirname(self.mumu_manager_path), 'adb.exe')
        command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'shell', '/data/local/tmp/minitouch', f"{x},{y}", 'd']
        subprocess.run(command, check=True)

    def take_screenshot(self):
        self.ensure_directory('./screenshot/')  # 确保截图目录存在
        timestamp = int(time.time())
        screenshot_path = f'./screenshot/screenshot_{timestamp}.png'
        adb_path = os.path.join(os.path.dirname(self.mumu_manager_path), 'adb.exe')
        screenshot_path = f'screenshot_{int(time.time())}.png'
        pull_command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'pull', '/sdcard/screenshot.png', screenshot_path]
        subprocess.run(pull_command, check=True)
        
        
        self.manage_screenshots(screenshot_path)  # 管理截图数量
        print(f"Screenshot path:{screenshot_path}")
        return screenshot_path
    
    def ensure_directory(self, directory):
        if not os.path.exists(directory):
            os.makedirs(directory)

    def manage_screenshots(self, screenshot_path):
        screenshot_dir = os.path.dirname(screenshot_path)
        screenshot_files = sorted(os.listdir(screenshot_dir), key=lambda x: os.path.getctime(os.path.join(screenshot_dir, x)))
        if len(screenshot_files) > 20:
            file_to_remove = os.path.join(screenshot_dir, screenshot_files[0])
            if os.path.exists(file_to_remove):
                os.remove(file_to_remove)

    def take_screenshot(self):
        timestamp = int(time.time())
        screenshot_path = f'./screenshot/screenshot_{timestamp}.png'
        adb_path = os.path.join(os.path.dirname(self.mumu_manager_path), 'adb.exe')
        command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'shell', 'screencap', '/sdcard/screenshot.png']
        subprocess.run(command, check=True)
        pull_command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'pull', '/sdcard/screenshot.png', screenshot_path]
        subprocess.run(pull_command, check=True)
        self.manage_screenshots(screenshot_path)
        print(f"Screenshot path: {screenshot_path}")
        return screenshot_path
    
    def send_touch_event(self, x, y):
        adb_path = os.path.join(os.path.dirname(self.mumu_manager_path), 'adb.exe')
        # 直接使用图标在截图中的像素坐标发送触摸事件
        command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'shell', 'input', 'tap', str(x), str(y)]
        subprocess.run(command, check=True)

    def find_similar(self, image_path, template_path, threshold=0.8):
        img = Image.open(image_path).convert('L')  # 转为灰度图像
        template = Image.open(template_path).convert('L')
        
        template_blur = template.filter(ImageFilter.BLUR)
        diff = ImageChops.difference(img, template_blur)
        histogram = diff.histogram()
        
        avg_brightness = sum(histogram[:256]) / len(histogram)
        if avg_brightness < threshold * 256:
            return True
        else:
            return False

    def main_operation(self, target_icon_path, login_icon_path, tolerance=0.8):
        app_icon_found = False
        while not app_icon_found:
            screenshot_path = self.take_screenshot()
            if screenshot_path:
                app_icon_position = match_template(screenshot_path, target_icon_path, tolerance)
                if app_icon_position:
                    print("Found app icon, sending touch event...")
                    x, y = app_icon_position
                    self.send_touch_event(x, y)
                    app_icon_found = True
                else:
                    login_icon_position = match_template(screenshot_path, login_icon_path, tolerance)
                    if login_icon_position:
                        print("Found login icon, sending touch event directly...")
                        x, y = login_icon_position
                        self.send_touch_event(x, y)
                        break  # 找到login_icon后，跳出循环
                    else:
                        print("Neither app icon nor login icon found, retrying in 0.5 seconds...")
                        time.sleep(0.5)
            else:
                print("Failed to take a screenshot, retrying in 0.5 seconds...")
                time.sleep(0.5)

            if app_icon_found:
                print("App icon found and tapped, now looking for login icon...")
                time.sleep(15)  # 假设应用打开后需要15秒加载至可操作界面

                # 搜索login_icon，每0.5秒截一次图
                start_time = time.time()
                while time.time() - start_time < 30:  # 设置最长等待时间为30秒
                    new_screenshot_path = self.take_screenshot()
                    if new_screenshot_path:
                        login_icon_position = match_template(new_screenshot_path, login_icon_path, tolerance)
                        if login_icon_position:
                            print("Login icon found, sending touch event...")
                            x, y = login_icon_position
                            self.send_touch_event(x, y)
                            # 在这里添加登录之后的操作逻辑
                            print("Login successful, proceeding with further actions...")
                            break
                    else:
                        print("Failed to take a screenshot after tapping app icon.")
                    time.sleep(0.5)

                if not login_icon_position:
                    print("Login icon not found within the given time.")

    def find_element(self, target_image_path, tolerance=0.8, max_attempts=10):
        screenshot_path = self.take_screenshot()
        if screenshot_path is None:
            print("Failed to take a screenshot")
            return None

        # 使用match_template方法寻找图标
        for _ in range(max_attempts):
            img = cv2.imread(screenshot_path, cv2.IMREAD_COLOR)  # 仅保留这一行，去掉下面的Image.open
            template = cv2.imread(target_image_path, cv2.IMREAD_COLOR)

            # 获取模板的宽度和高度
            w, h = template.shape[:-1]

            # 使用matchTemplate
            res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

            # 输出匹配得分
            print(f"Match Score: {max_val}")

            # 确保至少有一个匹配结果
            if max_val >= tolerance:  # 更新这里，使用传入的tolerance参数
                # 输出匹配位置
                print(f"Match Location: {max_loc}")
                return screenshot_path
            time.sleep(0.5)
        return None


# 实例化并调用主操作
emu_console = MuMuEmulator(r'E:\MuMuPlayer-12.0\shell\MuMuManager.exe', None)
target_icon_path = './search/JP_appicon.png'
login_icon_path = './search/JP_login.png'
emu_console.main_operation(target_icon_path, login_icon_path)