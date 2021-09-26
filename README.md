# cloud189app-action-simplify

forked from [xtyuns/cloud189app-action](https://github.com/xtyuns/cloud189app-action)

简易修改版

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

接收的邮件能在垃圾邮件找到。

---

填写信息

Ubuntu服务器可用

```shell
pip install -r requirements.txt
```

计划任务定时运行 `action.py` 即可。

