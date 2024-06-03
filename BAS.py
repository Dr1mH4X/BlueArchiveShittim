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
    loc = np.where(res >= threshold)
    
    # 确保至少有一个匹配结果
    if len(loc[0]) == 0:
        return None
    
    # 返回第一个匹配位置的左上角坐标
    return loc[1][0], loc[0][0]  # 注意这里的索引顺序，因为loc返回的是(y, x)

# 更新find_element方法以使用match_template

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
    def find_element(self, target_image_path, tolerance=0.8, max_attempts=10):
        screenshot_path = self.take_screenshot()
        if screenshot_path is None:
            print("Failed to take a screenshot")
            return None
        
        # 使用match_template方法寻找图标
        for _ in range(max_attempts):
            position = match_template(screenshot_path, target_image_path, tolerance)
            if position:
                print(f"Found icon at position: {position}")
                return screenshot_path
            time.sleep(0.5)
        return None

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
        self.ensure_directory('./screenshot/')
        timestamp = int(time.time())
        screenshot_path = f'./screenshot/screenshot_{timestamp}.png'
        adb_path = os.path.join(os.path.dirname(self.mumu_manager_path), 'adb.exe')
        command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'shell', 'screencap', '/sdcard/screenshot.png']
        subprocess.run(command, check=True)
        pull_command = [adb_path, '-s', f'{self.ip_address}:{self.port}', 'pull', '/sdcard/screenshot.png', screenshot_path]
        subprocess.run(pull_command, check=True)
        self.manage_screenshots(screenshot_path)
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

    def main_operation(self, target_icon_path, tolerance=0.8, max_attempts=10):
        screenshot_path = self.find_element(target_icon_path, tolerance, max_attempts)
        if screenshot_path:
            print("Found app icon, sending touch event...")
            position = match_template(screenshot_path, target_icon_path, tolerance)
            if position:
                x, y = position
                self.send_touch_event(x, y)
                print(f"Clicked at position: {x}, {y}")

                print("Waiting for 1 minute...")
                time.sleep(60)  # 等待1分钟

                # 直接使用固定分辨率的屏幕中心坐标
                center_x = 1280 // 2  # 假设分辨率为1280x720
                center_y = 720 // 2
                self.send_touch_event(center_x, center_y)
                print("Clicked at the center of the screen after 1 minute.")
            else:
                print("Match found but failed to extract position.")
        else:
            print("Failed to locate the app icon.")

# 实例化并调用主操作
emu_console = MuMuEmulator(r'E:\MuMuPlayer-12.0\shell\MuMuManager.exe', None)
target_icon_path = 'app_icon.png'
emu_console.main_operation(target_icon_path)