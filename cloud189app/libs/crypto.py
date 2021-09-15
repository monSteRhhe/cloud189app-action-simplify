import xxtea
import rsa
import hmac
import hashlib


def getSignatureHex(data: str, sessionSecret: str = None):
    r"""signature the data to hex
    when the sessionSecret is empty, the default key is used.

    data: signature data
        such as:
        AppKey=600100885&Operate=POST&RequestURI=/login4MergedClient.action&Timestamp=1614425058
        OR
        SessionKey=1d2fg457-8f6e-6849-3571-5t3h1gu3ik1d_family&Operate=GET&RequestURI=/family/file/getFamilyDynamicListNew.action&Date=Sat, 27 Feb 2021 11:24:24 GMT
    """

    key = bytes.fromhex(Keys.default_signature) if sessionSecret is None else sessionSecret.encode("utf-8")
    return hmac.new(key, data.encode("utf-8"), "sha1").hexdigest()


def encryptHex(string: str):
    r"""encrypt str data to hex string"""

    return xxtea.encrypt(string, bytes.fromhex(Keys.paras)).hex()


def decryptHex(data: str) -> str:
    r"""decrypt hex string data to str"""

    return xxtea.decrypt_utf8(bytes.fromhex(data), bytes.fromhex(Keys.paras))


def rsa_encryptHex(data: str, publicKey: str = None):
    r"""encrypt data with the public key of base64 to hex string.

    """

    if publicKey is None:
        rsa_publicKey = Keys.default_rsa_publicKey
    else:
        rsa_publicKey = rsa.PublicKey.load_pkcs1_openssl_pem(f"-----BEGIN PUBLIC KEY-----\n{publicKey}\n-----END PUBLIC KEY-----".encode("utf-8"))
    return rsa.encrypt(data.encode("utf-8"), rsa_publicKey).hex()


def md5(string: str, encoding="utf-8"):
    return hashlib.md5(string.encode(encoding)).hexdigest()


class Keys:
    paras = "67377150343554566b51354736694e6262686155356e586c41656c4763416373"
    default_signature = "6665353733346337346332663936613338313537663432306233326463393935"
    default_rsa_publicKey = rsa.PublicKey(152334346597938436293356441115719435124636105143326532780542577723094703991678344742000021867588140450685721745211231553599381639990706123205672974928645595682727909568532858444056192955490635499533969753560238390855204373585601526650632417250726199698579300301057558260951102971295524642685968805111112239701, 65537)
