import requests
import sys

from . import api_util

def create(newfoldername, server_url="http://localhost", port=41595, allow_duplicate_name=True, timeout_connect=3, timeout_read=10, token=None):
    """EAGLE API:/api/folder/create

    Method: POST

    Args:
        newfoldername: Name of the new folder to create
        server_url: Server URL (default: "http://localhost")
        port: Server port (default: 41595)
        allow_duplicate_name: Allow creating folders with same name (default: True)
        timeout_connect: Connection timeout in seconds (default: 3)
        timeout_read: Read timeout in seconds (default: 10)
        token: API token for authentication (default: None)

    Returns:
        Response: return of requests.post
    """
    API_URL = f"{server_url}:{port}/api/folder/create"
    API_URL = api_util.append_token_to_url(API_URL, token)

    def _init_data(newfoldername):
        _data = {}
        if newfoldername and newfoldername != "":
            _data.update({"folderName": newfoldername})
        return _data
    data = _init_data(newfoldername)

    # check duplicate if needed
    if not allow_duplicate_name:
        r_post = list(server_url=server_url, port=port, token=token)
        _ret = api_util.findFolderByName(r_post, newfoldername)
        if _ret != None or len(_ret) > 0:
            print(f"ERROR: create folder with same name is forbidden by option. [eagleapi.folder.create] foldername=\"{newfoldername}\"", file=sys.stderr)
            return

    r_post = requests.post(API_URL, json=data, timeout=(timeout_connect, timeout_read))
    return r_post


def rename(folderId, newName, server_url="http://localhost", port=41595, timeout_connect=3, timeout_read=10, token=None):
    """EAGLE API:/api/folder/rename

    Method: POST

    Args:
        folderId: ID of the folder to rename
        newName: New name for the folder
        server_url: Server URL (default: "http://localhost")
        port: Server port (default: 41595)
        timeout_connect: Connection timeout in seconds (default: 3)
        timeout_read: Read timeout in seconds (default: 10)
        token: API token for authentication (default: None)

    Returns:
        Response: return of requests.post
    """
    API_URL = f"{server_url}:{port}/api/folder/rename"
    API_URL = api_util.append_token_to_url(API_URL, token)

    data = {
        "folderId": folderId,
        "newName": newName
    }
    r_post = requests.post(API_URL, json=data, timeout=(timeout_connect, timeout_read))
    return r_post


def list(server_url="http://localhost", port=41595, timeout_connect=3, timeout_read=10, token=None):
    """EAGLE API:/api/folder/list

    Method: GET

    Args:
        server_url: Server URL (default: "http://localhost")
        port: Server port (default: 41595)
        timeout_connect: Connection timeout in seconds (default: 3)
        timeout_read: Read timeout in seconds (default: 10)
        token: API token for authentication (default: None)

    Returns:
        Response: return of requests.get
    """
    API_URL = f"{server_url}:{port}/api/folder/list"
    API_URL = api_util.append_token_to_url(API_URL, token)

    r_get = requests.get(API_URL, timeout=(timeout_connect, timeout_read))
    return r_get