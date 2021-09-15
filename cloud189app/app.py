import random
from urllib import parse
from cloud189app import utils, consts
from cloud189app.libs import *


class Client:
    def __init__(self, username, password):
        self.configInfo = utils.initConfigInfo(crypto.md5(username+password), crypto.md5(password))
        self.__session = utils.initRequestSession(self.__getUserAgentString(2) + " " + self.__getUserAgentString(3))
        self.user = UserInfo(username, password)
        self.msg = ""
        self.isLogin = self.login()

    def __checkLogin(self):
        if self.isLogin:
            return True
        else:
            self.msg = "请先登录账号"
            return False

    def __needCaptcha(self):
        data = {
            "appKey": "cloud",
            "userName": "{RSA}" + crypto.rsa_encryptHex(self.user.username),
            "guid": self.configInfo.get("device", "guid"),
            "reqId": "undefined",
            "headerDeviceId": self.configInfo.get("device", "guid")
        }
        headers = {
            "X-Requested-With": self.configInfo.get("client", "clientPackageName")
        }
        response = utils.sendPostRequest(self.__session, consts.URL_1_needCaptcha, data, headers)

        if response.text != "0":
            self.msg = "当前账号登录需要验证, 请在手机端完成登录后重试"
            return True
        return False

    def __mergedSession(self, accessToken: str):
        # build url
        url = consts.URL_2_login4MergedClient

        # build data
        rand = str(utils.getTimestamp())
        data = {
            "rand": rand,
            "accessToken": accessToken,
            "clientType": self.configInfo.get("client", "clientType"),
            "version": self.configInfo.get("client", "clientVersion"),
            "clientSn": "null",
            "model": self.configInfo.get("device", "mobileModel"),
            "osFamily": self.configInfo.get("device", "osType"),
            "osVersion": self.configInfo.get("device", "osAPI"),
            "networkAccessMode": "WIFI",
            "telecomsOperator": "unknow",
            "channelId": "uc"
        }

        # build headers
        appkey = "600100885"
        sign = f"AppKey={appkey}&Operate=POST&RequestURI={utils.getRequestURI(url)}&Timestamp={rand}"
        headers = {
            "appkey": appkey,
            "appsignature": crypto.getSignatureHex(sign).upper(),
            "timestamp": rand,
            "user-agent": self.__getUserAgentString(4)
        }

        # send request
        response = utils.sendPostRequest(self.__session, url, data, headers)

        # parse data
        data = utils.xml2dict(response.text)
        if "userSession" in data:
            self.user.sessionKey = data['userSession']['sessionKey']
            self.user.sessionSecret = data['userSession']['sessionSecret']
            self.user.eAccessToken = data['userSession']['eAccessToken']
            self.user.familySessionKey = data['userSession']['familySessionKey']
            self.user.familySessionSecret = data['userSession']['familySessionSecret']
            return True
        else:
            self.msg = data['error']['message']
            return False

    def login(self):
        r"""登录失败则由失败方法设置提示信息, login() 方法中只负责设置最终登录成功提示"""

        if self.__needCaptcha():
            return False

        url = consts.URL_1_oAuth2SdkLoginByPassword

        deviceInfo = str(self.__buildDeviceInfo()).replace("'", '"')
        data = {
            "appKey": "cloud",
            "deviceInfo": crypto.encryptHex(deviceInfo),
            "apptype": "wap",
            "loginType": "1",
            "dynamicCheck": "false",
            "userName": "{RSA}" + crypto.rsa_encryptHex(self.user.username),
            "password": "{RSA}" + crypto.rsa_encryptHex(self.user.password),
            "validateCode": "",
            "captchaToken": "",
            "jointWay": "1|2",
            "jointVersion": "v" + self.configInfo.get("client", "ctaSdkVersion"),
            "operator": "",
            "nwc": "WIFI",
            "nws": "2",
            "guid": self.configInfo.get("device", "guid"),
            "reqId": "undefined",
            "headerDeviceId": self.configInfo.get("device", "guid")
        }
        headers = {
            "User-Agent": self.__getUserAgentString(2) + " " + self.__getUserAgentString(3),
            "X-Requested-With": self.configInfo.get("client", "clientPackageName")
        }

        response = utils.sendPostRequest(self.__session, url, data, headers=headers)
        result = response.json()
        if str(result["result"]) != "0":
            self.msg = result["msg"]

            r"""(需要设备锁验证) -> "result":-133, "msg":"绑定设备ID不存在", "isSystem":0... """
            if result['result'] == -133:
                if result['isSystem'] == 1:
                    self.msg = "为了您的账号安全，请进行短信验证，并修改密码解除异常。"
                else:
                    self.msg = "(设备锁)为保障您的天翼账号安全，当前设备需进行身份验证。"
            return False
        data = parse.parse_qs(crypto.decryptHex(parse.parse_qs(result["returnParas"]).get("paras")[0]))
        self.user.nickName = data.get("nickName")[0]
        if self.__mergedSession(data.get("accessToken")[0]):
            self.msg = self.user.nickName + ", 登录成功"
            return True
        return False

    def sign(self):
        if not self.__checkLogin():
            return False

        rand = str(utils.getTimestamp())
        params = {
            "rand": rand,
            "clientType": self.configInfo.get("client", "clientType"),
            "version": self.configInfo.get("client", "clientVersion"),
            "model": self.configInfo.get("device", "mobileModel")
        }
        url = consts.URL_2_userSign + "?" + parse.urlencode(params)
        t = utils.CST2GMTString(int(rand))
        sign = f"SessionKey={self.user.sessionKey}&Operate=GET&RequestURI={utils.getRequestURI(url)}&Date={t}"
        headers = {
            "sessionkey": self.user.sessionKey,
            "date": t,
            "signature": crypto.getSignatureHex(sign, self.user.sessionSecret),
            "user-agent": self.__getUserAgentString(4)
        }
        response = utils.sendGetRequest(self.__session, url, headers)
        result = utils.xml2dict(response.text)

        flag = False
        if "error" in result:
            self.msg = result['error']['message']
        elif "userSignResult" not in result:
            self.msg = response.text if response.text != "" else "请求失败"
        elif result['userSignResult']['result'] == '1':
            flag = True
            self.msg = "签到成功, " + result['userSignResult']['resultTip']
        elif result['userSignResult']['result'] == '-1':
            self.msg = "不能重复签到, 今日已" + result['userSignResult']['resultTip']
        else:
            self.msg = "[" + result['userSignResult']['result'] + "]: " + result['userSignResult']['resultTip']
        return flag

    def draw(self):
        if not self.__checkLogin():
            return False
        url = consts.URL_1_drawPage + "?albumBackupOpened=0"
        self.__ssoLogin(url)

        headers = {
            "user-agent": self.__getUserAgentString(2) + " " + self.__getUserAgentString(3),
            "x-requested-with": "XMLHttpRequest",
            "referer": url
        }
        params = {
            "activityId": "ACT_SIGNIN",
            "taskId": "TASK_SIGNIN",
            "noCache": str(random.random())
        }
        url = consts.URL_1_drawPrizeMarketDetails + "?" + parse.urlencode(params)

        response = utils.sendGetRequest(self.__session, url, headers)
        result = response.json()
        self.msg = "签到抽奖: "
        if "prizeName" in result:
            self.msg += result['prizeName']
        elif "errorCode" in result:
            self.msg += result['errorCode']
        else:
            self.msg = response.text

        utils.sendGetRequest(self.__session, consts.URL_1_act + "?act=10", headers)

        params['noCache'] = str(random.random())
        params['taskId'] = "TASK_SIGNIN_PHOTOS"
        url = consts.URL_1_drawPrizeMarketDetails + "?" + parse.urlencode(params)
        headers['referer'] = str(headers['referer'])[:-1] + "1"
        response = utils.sendGetRequest(self.__session, url, headers)

        result = response.json()
        self.msg += "\n相册抽奖: "
        if "prizeName" in result:
            self.msg += result['prizeName']
        elif "errorCode" in result:
            self.msg += result['errorCode']
        else:
            self.msg = response.text
        return self.msg

    def __ssoLogin(self, redirectUrl) -> str:
        r"""add ['COOKIE_LOGIN_USER']"""

        params = {
            "sessionKey": self.user.sessionKey,
            "sessionKeyFm": self.user.familySessionKey,
            "appName": self.configInfo.get("client", "clientPackageName"),
            "redirectUrl": redirectUrl
        }
        url = consts.URL_1_ssoLoginMerge + "?" + parse.urlencode(params)
        headers = {
            "User-Agent": self.__getUserAgentString(2) + " " + self.__getUserAgentString(3),
            "x-requested-with": self.configInfo.get("client", "clientPackageName")
        }
        response = utils.sendGetRequest(self.__session, url, headers)

        return response.text

    def __buildDeviceInfo(self) -> dict:
        deviceInfo = {
            'imei': None, 'imsi': None, 'deviceId': None, 'terminalInfo': None,
            'osInfo': None, 'mobileBrand': None, 'mobileModel': None
        }
        for key in deviceInfo.keys():
            if self.configInfo.has_option("device", key):
                deviceInfo[key] = self.configInfo.get("device", key)
            deviceInfo['terminalInfo'] = deviceInfo['mobileModel']
            deviceInfo['osInfo'] = self.configInfo.get("device", "osType")
            deviceInfo['osInfo'] = deviceInfo['osInfo'] + ":" + self.configInfo.get("device", "osVersion")

        return deviceInfo

    def __getUserAgentString(self, ua_type: int = 1):
        r""" return User-Agent info

        1. (http.agent): Dalvik/2.1.0 (Linux; U; Android 5.1.1; OPPO R11 Plus Build/NMF26X)
        2. (webview User-Agent): Mozilla/5.0 (Linux; Android 10; MI MIX3 Build/QKQ1.190828.002; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.66 Mobile Safari/537.36
        3. (client info): clientCtaSdkVersion/v3.8.1 deviceSystemVersion/10 deviceSystemType/Android clientPackageName/com.cn21.ecloud clientPackageNameSign/1c71af12beaa24e4d4c9189f3c9ad576
        4. (util_User-Agent_3): Ecloud/8.9.0 (MI MIX3; ; uc) Android/29
        5. (util_User-Agent_4): Ecloud/8.9.0 Android/29 clientId/null clientModel/MIX 3 imsi/null clientChannelId/uc proVersion/1.0.6
        """

        if ua_type in (1, 2):
            osType = self.configInfo.get("device", "osType")
            osVersion = self.configInfo.get("device", "osVersion")
            mobileModel = self.configInfo.get("device", "mobileModel")
            buildId = self.configInfo.get("device", "buildId")

            if ua_type == 1:
                return f"Dalvik/2.1.0 (Linux; U; {osType} {osVersion}; {mobileModel} Build/{buildId})"
            elif ua_type == 2:
                return f"Mozilla/5.0 (Linux; {osType} {osVersion}; {mobileModel} Build/{buildId}; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/87.0.4280.66 Mobile Safari/537.36"
        elif ua_type == 3:
            clientCtaSdkVersion = self.configInfo.get("client", "ctaSdkVersion")
            osVersion = self.configInfo.get("device", "osVersion")
            osType = self.configInfo.get("device", "osType")
            clientPackageName = self.configInfo.get("client", "clientPackageName")
            clientPackageNameSign = self.configInfo.get("client", "clientPackageNameSign")

            return f"clientCtaSdkVersion/v{clientCtaSdkVersion} deviceSystemVersion/{osVersion} deviceSystemType/{osType} clientPackageName/{clientPackageName} clientPackageNameSign/{clientPackageNameSign}"
        elif ua_type in (4, 5):
            clientVersion = self.configInfo.get("client", "clientVersion")
            proVersion = self.configInfo.get("client", "proVersion")
            mobileModel = self.configInfo.get("device", "mobileModel")
            osType = self.configInfo.get("device", "osType")
            osVersion = self.configInfo.get("device", "osVersion")
            imei = self.configInfo.get("device", "imei")
            imsi = self.configInfo.get("device", "imsi")
            imei = imei if imsi != "" else "null"
            imsi = imsi if imsi != "" else "null"

            if ua_type == 4:
                return f"Ecloud/{clientVersion} ({mobileModel}; ; uc) {osType}/{osVersion}"
            elif ua_type == 5:
                return f"Ecloud/{clientVersion} {osType}/{osVersion} clientId/{imei} clientModel/{mobileModel} imsi/{imsi} clientChannelId/uc proVersion/{proVersion}"


class UserInfo:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.nickName = None

        self.sessionKey = None
        self.sessionSecret = None
        self.eAccessToken = None
        self.familySessionKey = None
        self.familySessionSecret = None