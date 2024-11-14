#main.py
from adb_operations import Adbconn, Adbdisconn, Adbstart, main_task

ADBaddress, diserror = Adbconn()
Adbstart(ADBaddress, diserror)
main_task('login')
# main_task('login_event')
main_task('close_news')

# 社团奖励领取
# main_task('social')
# main_task('club')
# main_task('ok')
# main_task('home')

# 邮件领取
main_task('mail')
main_task('receive_mail')
main_task('get_rewarded')
main_task('home')
# pass
Adbdisconn(ADBaddress)                                          # 断开连接