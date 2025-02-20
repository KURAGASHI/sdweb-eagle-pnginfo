# seealso: https://api.eagle.cool/application/info
#
import requests

from . import api_util

def info(server_url="http://localhost", port=41595, timeout_connect=3, timeout_read=10, token=None):
    """EAGLE API:/api/application/info

    Returns:
        Response: return of requests.post
    """

    API_URL = f"{server_url}:{port}/api/application/info"
    API_URL = api_util.append_token_to_url(API_URL, token)

    try:
        r_get = requests.get(API_URL, timeout=(timeout_connect, timeout_read))
    except requests.exceptions.Timeout as e:
        print("Error: api_application.info")
        print(e)
        return

    return r_get

#
# Support function
#
def is_alive(server_url="http://localhost", port=41595, timeout_connect=3, timeout_read=10, token=None):
    if not port or type(port) != int or port == "":
        port=41595
    try:
        r_get = info(server_url, port, timeout_connect, timeout_read, token=token)
    except Exception as e:
        print("Error: api_application.is_alive")
        print(e)
        return False
    try:
        r_get.raise_for_status()
        return True
    except:
        return False

# api_application.py

def is_valid_url_port(server_url_port="", timeout_connect=3, timeout_read=3, token=None):
    """指定されたサーバーURLとポートが有効かチェックする

    Args:
        server_url_port (str): チェックするURL:PORT形式の文字列
        timeout_connect (int): 接続タイムアウト時間
        timeout_read (int): 読み取りタイムアウト時間
        token (str, optional): APIトークン

    Returns:
        bool: 有効な場合True
    """
    if not server_url_port or server_url_port == "":
        # outside_server_url_portが設定されていない場合はlocalhostを使用しない
        return False

    # URLとポートを分解
    server_url, port = api_util.get_url_port(server_url_port)
    if not server_url or not port:
        return False

    try:
        # サーバーの生存確認
        if not is_alive(
            server_url=server_url, 
            port=port, 
            timeout_connect=timeout_connect, 
            timeout_read=timeout_read, 
            token=token
        ):
            return False
        return True
    except Exception as e:
        print(f"Error checking server: {e}")
        return False
