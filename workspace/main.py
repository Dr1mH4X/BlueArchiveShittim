#main.py
from adb_operations import Adbconn, Adbdisconn, Adbstart, main_task, touch_and_wait, Touch
import time

def login():
    # 登录
    main_task('login', touch=True)
    main_task('login_event', touch=True)                                    # 每日奖励
    main_task('close_news', touch=True)

def club_reward():
    # 社团奖励领取
    main_task('social', touch=True)
    main_task('club', touch=True)
    main_task('ok', touch=True)
    main_task('home', touch=True)

def mail_reward():
    # 邮件领取
    main_task('mail', touch=True)
    main_task('receive_mail', touch=True)
    main_task('get_rewarded', touch=True)
    main_task('home', touch=True)
def calendar():
    # 日程表
    main_task('calendar', touch=True)
    main_task('schale_office_area', touch=True)
    # 循环开始
    main_task('all_calendar', touch=True)
    main_task('first_room', touch=True)
    main_task('start_calendar', touch=True)
    touch_and_wait()
    #循环结束
    for z in range(6):
        main_task('all_calendar', touch=True)
        time.sleep(2)
        Touch('first_room')
        main_task('start_calendar', touch=True)
        touch_and_wait()
    main_task('home', touch=True)
def cafe():
    main_task('cafe', touch=True)
    time.sleep(5)
    Touch('next_calendar')
    

ADBaddress, diserror = Adbconn()                                # 开始连接
Adbstart(ADBaddress, diserror)
login()
club_reward()
mail_reward()
calendar()
Adbdisconn(ADBaddress)                                          # 断开连接