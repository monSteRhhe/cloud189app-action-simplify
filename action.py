from cloud189app import *
import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr

def send_mail(log):
    smtp_host = '' # 设置SMTP服务器
    smtp_port = '' # 设置SMTP端口
    mail_from = '' # 发信邮箱
    mail_auth = '' # 发信邮箱密码/授权码
    mail_to = [''] # 收信邮箱

    message = MIMEText(log, 'plain', 'utf-8')
    message['From'] = formataddr(['Bot', mail_from])

    subject = 'cloud189 action bot'
    message['Subject'] = subject
    
    try:
        smtpObj = smtplib.SMTP(smtp_host, smtp_port)
        smtpObj.ehlo()
        smtpObj.starttls()
        smtpObj.login(mail_from, mail_auth)
        smtpObj.sendmail(mail_from, mail_to, message.as_string())
        smtpObj.quit()
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

    exit(1)


def main(user: str, pwd: str, mail_enable: bool):
    log = ""
    try:
        print_msg()
        # log 变量记录消息推送内容
        log += print_msg(hide_username(user) + ":", True)
        cloud = Client(user, pwd)
        log += print_msg(cloud.msg)
        if not cloud.isLogin:
            exit(-1)
        cloud.sign()
        log += print_msg(cloud.msg)
        cloud.draw()
        log += print_msg(cloud.msg)
    except Exception:
        log += print_msg("任务执行失败, 请重试!")
    finally:
        if(mail_enable):
            send_mail(log)
        else:
            print('未启用邮箱发信。')
            exit(1)


def hide_username(name: str) -> str:
    u_len = len(name)
    fill_len = int(u_len * 0.3) + 1
    b_index = int((u_len - fill_len) / 2)
    e_index = u_len - fill_len - b_index
    return name[:b_index] + "*" * fill_len + name[-e_index:]


def print_msg(msg: str = "", isFirstLine: bool = False) -> str:
    if isFirstLine or msg == "":
        indent = ""
    else:
        indent = " " * 4
        msg = msg.replace("\n", "\n" + indent)
    msg = indent + msg + "\n"

    print(msg, end='')
    return msg


if __name__ == '__main__':
    # 多账号用单个空格 间隔开
    USERNAME = ''
    PASSWORD = ''
    
    # 启用邮箱发信
    mail_enable = True
    
    if not USERNAME or not PASSWORD:
        print('你没有添加任何账户')
        exit(1)

    user_list = USERNAME.strip().split()
    passwd_list = PASSWORD.strip().split()

    if len(user_list) != len(passwd_list):
        print('账号密码数量不匹配。')
        exit(1)

    for i in range(len(user_list)):
        print('正在签到第 %d 个账号' % (i + 1) + '，共 %d 个账号。' % (len(user_list)))
        main(user_list[i], passwd_list[i], mail_enable)
