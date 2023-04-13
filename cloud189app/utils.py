import uuid
from urllib import parse

import requests
import xmltodict
import json
import os
import time
from configparser import ConfigParser


def initConfigInfo(deviceId: str, guid: str):
    r"""根目录下的配置文件优先级 > 本文件同级中的配置文件"""

    cur_dir = os.path.dirname(__file__)
    if os.path.exists(os.path.join(os.path.dirname(cur_dir), "ConfigInfo.ini")):
        conf_file = os.path.join(os.path.dirname(cur_dir), "ConfigInfo.ini")
    else:
        conf_file = os.path.join(cur_dir, "ConfigInfo.ini")
    ini = ConfigParser()
    ini.read(conf_file, encoding="utf-8")
    if ini.get("device", "deviceId") == "":
        ini.set("device", "deviceId", deviceId)
    if ini.get("device", "guid") == "":
        ini.set("device", "guid", guid)
    return ini


def initRequestSession(ua: str = ""):
    session = requests.session()
    session.headers['User-Agent'] = ua
    return session


def sendGetRequest(session, url, headers=None):
    r"""
    :rtype: requests.Response
    """

    if headers is None:
        headers = {}
    headers['Host'] = parse.urlparse(url).hostname
    return session.get(url, headers=headers)


def sendPostRequest(session, url, data, headers=None):
    r"""
    :rtype: requests.Response
    """

    if headers is None:
        headers = {}
    headers["x-request-id"] = str(uuid.uuid4())
    headers['Host'] = parse.urlparse(url).hostname
    return session.post(url, data=data, headers=headers)


def getRequestURI(url: str) -> str:
    url = url + "?"
    url = url[:url.find("?")]
    uri = "/" + "/".join(url.split("/")[3:])
    return uri


def getTimestamp(isSecond: bool = False) -> int:
    r"""return millisecond-timestamp(13) or second-timestamp(10)"""

    t = time.time()
    t = t if isSecond else t*1000
    return int(t)


def CST2GMTString(millisecond: int) -> str:
    r"""CST millisecond to GMT string"""

    millisecond -= 28800 * 1000
    t = time.strftime("%a, %d %b %Y %X GMT", time.localtime(millisecond / 1000))
    t = t.replace(", 0", ", ")
    return t


def xml2dict(xml_data: str) -> dict:
    data = json.dumps(xmltodict.parse(xml_data))
    return json.loads(data)
