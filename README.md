# cloud189app-action-simplify

> forked from [xtyuns/cloud189app-action](https://github.com/xtyuns/cloud189app-action)

简易修改版，加了个python的smtp

# 使用

打开action.py，找到 `USERNAME`、`PASSWORD`、`smtp_host`、`smtp_port`、`mail_from`、`mail_auth`、`mail_to` 填写。

多账号时 `USERNAME`、`PASSWORD` 的内容中间用单个空格[ ]隔开。

`smtp_host`、`smtp_port`、`mail_from`、`mail_auth`、`mail_to` 是发送邮件使用，可以不填，同时将 `mail_enable` 改为 `False` 来关闭使用邮箱发信。

如果要使用邮箱发信，以qq邮箱为例：

```python
smtp_host = 'smtp.qq.com' # 设置qq邮箱SMTP服务器
smtp_port = '587' # 设置端口 465或587
mail_from = 'xxxxxxx@qq.com' # qq邮箱
mail_auth = 'xxxxxx' # qq邮箱授权码
mail_to = ['xxxxx@xxx.com'] # 收信邮箱
```

如果收件箱里没找到邮件，可以到垃圾邮件中找找。

[常用邮箱客户端SMTP设置](https://blog.csdn.net/weixin_39578674/article/details/110922197)

Ubuntu服务器可用，win没试过‍ (¦3【▓▓】。

安装依赖：

```shell
pip install -r requirements.txt
```

定时每天运行 `action.py` 即可。

