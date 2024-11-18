#main.py
from adb_operations import Adbconn, Adbdisconn, Adbstart, main_task

def login():
    # 登录
    main_task('login')
    main_task('login_event') # 每日奖励
    main_task('close_news')

def club_reward():
    # 社团奖励领取
    main_task('social')
    main_task('club')
    main_task('ok')
    main_task('home')

def mail_reward():
    # 邮件领取
    main_task('mail')
    main_task('receive_mail')
    main_task('get_rewarded')
    main_task('home')
# pass

ADBaddress, diserror = Adbconn()                                # 开始连接
Adbstart(ADBaddress, diserror)
login()
club_reward()
mail_reward()
Adbdisconn(ADBaddress)                                          # 断开连接