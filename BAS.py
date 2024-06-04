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
        # 输出匹配位置及匹配到的模板图片名称
        print(f"Match Location: {max_loc}, Matched Template: {os.path.basename(template_path)}")
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

    def main_operation(self, target_icon_path, login_icon_path, sign_rewards_path, JP_news_path, close_news_path, tolerance=0.8):
        while True:
            screenshot_path = self.take_screenshot()
            if screenshot_path:
                app_icon_position = match_template(screenshot_path, target_icon_path, tolerance)
                if app_icon_position:
                    print("Found app icon, sending touch event...")
                    x, y = app_icon_position
                    self.send_touch_event(x, y)
                    break  # 找到应用图标后跳出循环
                else:
                    login_icon_position = match_template(screenshot_path, login_icon_path, tolerance)
                    if login_icon_position:
                        print("Found login icon, sending touch event directly...")
                        x, y = login_icon_position
                        self.send_touch_event(x, y)
                        print("Login successful, ending operation.")
                        return  # 登录成功后结束方法

                    # 检查新闻图标
                    news_icon_position = match_template(screenshot_path, JP_news_path, tolerance)
                    if news_icon_position:
                        print("Found news icon, attempting to close news...")
                        x, y = news_icon_position
                        self.send_touch_event(x, y)  # 点击新闻图标的关闭按钮
                        if not self.close_news(sign_rewards_path, JP_news_path, close_news_path, tolerance):
                            print("No need to close news, continuing with the script...")
                        else:
                            print("News closed, ending operation.")
                            return
                        continue 

                    print("Neither app icon nor login icon found, retrying in 0.5 seconds...")
                    time.sleep(0.5)
            else:
                print("Failed to take a screenshot, retrying in 0.5 seconds...")
                time.sleep(0.5)

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
    
    def close_news(self, sign_rewards_path, JP_news_path, close_news_path, tolerance=0.8):
        # 获取新的截图
        screenshot_path = self.take_screenshot()
        
        # 检查是否有签到奖励
        sign_rewards_position = match_template(screenshot_path, sign_rewards_path, tolerance)
        if sign_rewards_position:
            print("Found sign rewards, sending touch event to the center of the screen...")
            self.send_touch_event_to_center()  # 假设有一个方法发送触摸事件到屏幕中心
            print("Sign rewards clicked.")
        else:
            print("Sign rewards not found, continuing to check JP_news...")

        # 检查是否有新闻
        JP_news_position = match_template(screenshot_path, JP_news_path, tolerance)
        if JP_news_position:
            print("Found JP_news, searching for close_news button...")
            close_news_position = match_template(screenshot_path, close_news_path, tolerance)
            if close_news_position:
                print("Found close_news button, sending touch event...")
                x, y = close_news_position
                self.send_touch_event(x, y)
                print("News closed.")
                return True  # 新闻已关闭，返回True
            else:
                print("Close_news button not found, clicking on screen center instead...")
                self.send_touch_event_to_center()
                print("News not closed, but clicked on screen center.")
                return False  # 新闻未关闭，但点击了屏幕中心，返回False
        else:
            print("JP_news not found, nothing to do.")
            return False  # 未找到新闻，返回False
    def post_login_actions(self):
        sign_rewards_path = "./search/sign_rewards.png"
        jp_news_path = "./search/JP_news.png"
        close_news_path = "./search/close_news.png"
        screen_width, screen_height = 1280, 720  # 固定的屏幕分辨率

        # 查找签到奖励图标
        sign_rewards_pos = match_template(self.take_screenshot(), sign_rewards_path, tolerance=0.8)
        if sign_rewards_pos:
            print("Found sign rewards icon, tapping center of the screen...")
            self.send_touch_event(screen_width // 2, screen_height // 2)
        else:
            print("Sign rewards icon not found.")

        # 直接查找日服新闻图标，一旦找到就尝试关闭
        jp_news_pos = match_template(self.take_screenshot(), jp_news_path, tolerance=0.8)
        if jp_news_pos:
            print("Found JP news icon, attempting to close news...")

            # 尝试关闭新闻
            for _ in range(3):  # 尝试三次查找并关闭
                close_news_pos = match_template(self.take_screenshot(), close_news_path, tolerance=0.8)
                if close_news_pos:
                    print("Closing news...")
                    x, y = close_news_pos
                    self.send_touch_event(x, y)
                    break  # 成功点击关闭按钮后退出循环
                else:
                    print("Trying to find close button again...")
                    time.sleep(0.5)  # 等待0.5秒再次尝试

            if not close_news_pos:
                print("Close news button not found after attempts, tapping center of the screen instead...")
                self.send_touch_event(screen_width // 2, screen_height // 2)
        else:
            print("JP news icon not found, tapping center of the screen and ending script...")
            self.send_touch_event(screen_width // 2, screen_height // 2)

# 实例化并调用主操作
emu_console = MuMuEmulator(r'E:\MuMuPlayer-12.0\shell\MuMuManager.exe', None)
target_icon_path = './search/JP_appicon.png'
login_icon_path = './search/JP_login.png'
sign_rewards_path = './search/sign_rewards.png'
close_news_path = './search/close_news.png'
JP_news_path = './search/JP_news.png'
emu_console.main_operation(
    target_icon_path, 
    login_icon_path, 
    sign_rewards_path, 
    JP_news_path, 
    close_news_path,
    tolerance=0.8  # 可以根据需要调整这个值
)



