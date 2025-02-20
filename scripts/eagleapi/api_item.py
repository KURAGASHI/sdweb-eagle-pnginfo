# seealso: https://api.eagle.cool/item/add-from-path
# seealso: https://api.eagle.cool/item/add-from-paths
#
import requests
import os
import base64

from . import api_util

DEBUG = True
def dprint(str):
    if DEBUG:
        print(str)

class EAGLE_ITEM_PATH:
    def __init__(self, filefullpath, filename="", website="", tags:list=[], annotation=""):
        """Data container for addFromPath, addFromPaths

        Args:
            filefullpath : Required, full path of the local files.
            filename     : (option), name of image to be added.
            website      : (option), address of the source of the image.
            tags (list)  : (option), tags for the image.
            annotation   : (option), annotation for the image.
        """
        self.filefullpath = filefullpath
        self.filename = filename
        self.website = website
        self.tags = tags
        self.annotation = annotation

    def output_data(self):
        """
        output data in json format for POST
        """
        _data = {
                "path": self.filefullpath,
                "name": os.path.splitext(os.path.basename(self.filefullpath))[0] if (self.filename == None or self.filename == "") else self.filename
            }
        if self.website and self.website != "":
            _data.update({"website": self.website})
        if self.tags and len(self.tags) > 0:
            _data.update({"tags": self.tags})
        if self.annotation and self.annotation != "":
            _data.update({"annotation": self.annotation})
        return _data


class EAGLE_ITEM_URL:
    def __init__(self, url, name, website="", tags=[], annotation="", modificationTime="", folderId="", headers={}):
        """Data container for addFromURL, addFromURLs
            url  : Required, the URL of the image to be added. Supports http, https, base64
            name : Required, The name of the image to be added.
            website : The Address of the source of the image
            tags: Tags for the image.
            annotation: The annotation for the image.
            modificationTime: The creation date of the image. The parameter can be used to alter the image's sorting order in Eagle.
            headers: Optional, customize the HTTP headers properties, this could be used to circumvent the security of certain websites.

            folderId: If this parameter is defined, the image will be added to the corresponding folder.
        """
        self.url = url
        self.name = name
        self.website = website
        self.tags = tags
        self.annotation = annotation
        self.modificationTime = modificationTime
        self.folderId = folderId
        self.headers = headers

    def convert_file_to_base64url(self, filepath=None):
        if (not filepath or filepath == ""):
            if self.url and self.url != "":
                filepath = self.url
            else:
                print("Error convert_file_to_base64url: invalid filepath")
                return filepath
        else:
            self.url = filepath
            
        dprint(f"DEBUG [convert_file_to_base64url] File path: {filepath}")
        
        if not os.path.exists(filepath):
            print("Error convert_file_to_base64url: file not found.")
            return filepath
            
        try:
            with open(filepath, "rb") as file:
                dprint("DEBUG [convert_file_to_base64url] Reading file content")
                enc_file = base64.urlsafe_b64encode(file.read())
                self.url = f"data:image/png;base64, {enc_file.decode('utf-8')}"
                dprint("DEBUG [convert_file_to_base64url] Successfully converted to base64")
                return self.url
        except Exception as e:
            print("Error convert_file_to_base64url: encode failed")
            print(e)
            return filepath

    def output_data(self):
        """
        output data in json format for POST
        """
        _data = {
                "url": self.url,
                "name": self.name
        }
        # add optional data
        if self.website and self.website != "":
            _data.update({"website": self.website})
        if self.tags and len(self.tags) > 0:
            _data.update({"tags": self.tags})
        if self.annotation and self.annotation != "":
            _data.update({"annotation": self.annotation})
        if self.modificationTime and self.modificationTime != "":
            _data.update({"modificationTime": self.modificationTime})
        if self.folderId and self.folderId != "":
            _data.update({"folderId": self.folderId})
        if self.headers and len(self.headers) > 0:
            _data.update({"headers": self.headers})
        return _data


def add_from_URL(item:EAGLE_ITEM_URL, folderId=None, server_url="http://localhost", port=41595, token=None):
    API_URL = f"{server_url}:{port}/api/item/addFromURL"
    
    dprint(f"DEBUG [add_from_URL] API URL: {API_URL}")
    dprint(f"DEBUG [add_from_URL] FolderID: {folderId}")
    
    _data = item.output_data()
    if folderId and folderId != "":
        _data.update({"folderId": folderId})
    if token:
        _data.update({"token": token})
        
    dprint(f"DEBUG [add_from_URL] Request data keys: {list(_data.keys())}")
    r_post = requests.post(API_URL, json=_data)
    
    dprint(f"DEBUG [add_from_URL] Response status: {r_post.status_code}")
    dprint(f"DEBUG [add_from_URL] Response content: {r_post.content.decode('utf-8') if r_post.content else 'No content'}")
    return r_post


def add_from_URL_base64(item:EAGLE_ITEM_URL, folderId=None, server_url="http://localhost", port=41595, token=None):
    API_URL = f"{server_url}:{port}/api/item/addFromURL"
    
    dprint(f"DEBUG [add_from_URL_base64] API URL: {API_URL}")
    dprint(f"DEBUG [add_from_URL_base64] FolderID: {folderId}")
    
    dprint("DEBUG [add_from_URL_base64] Converting file to base64")
    item.url = item.convert_file_to_base64url()
    _data = item.output_data()
    if folderId and folderId != "":
        _data.update({"folderId": folderId})
    if token:
        _data.update({"token": token})
        
    dprint(f"DEBUG [add_from_URL_base64] Request data keys: {list(_data.keys())}")
    dprint(f"DEBUG [add_from_URL_base64] Base64 URL length: {len(item.url) if item.url else 0}")
    r_post = requests.post(API_URL, json=_data)
    
    dprint(f"DEBUG [add_from_URL_base64] Response status: {r_post.status_code}")
    dprint(f"DEBUG [add_from_URL_base64] Response content: {r_post.content.decode('utf-8') if r_post.content else 'No content'}")
    return r_post


def add_from_path(item:EAGLE_ITEM_PATH, folderId=None, server_url="http://localhost", port=41595, token=None):
    API_URL = f"{server_url}:{port}/api/item/addFromPath"
    
    dprint(f"DEBUG [add_from_path] API URL: {API_URL}")
    dprint(f"DEBUG [add_from_path] FolderID: {folderId}")
    dprint(f"DEBUG [add_from_path] File path: {item.filefullpath}")
    
    _data = item.output_data()
    if folderId and folderId != "":
        _data.update({"folderId": folderId})
    if token:
        _data.update({"token": token})
        
    dprint(f"DEBUG [add_from_path] Request data keys: {list(_data.keys())}")
    r_post = requests.post(API_URL, json=_data)
    
    dprint(f"DEBUG [add_from_path] Response status: {r_post.status_code}")
    dprint(f"DEBUG [add_from_path] Response content: {r_post.content.decode('utf-8') if r_post.content else 'No content'}")
    return r_post


def add_from_paths(files, folderId=None, server_url="http://localhost", port=41595, step=None, token=None):
    """EAGLE API:/api/item/addFromPaths

    Method: POST

    Args:
        path: Required, the path of the local files.
        name: Required, the name of images to be added.
        website: The Address of the source of the images.
        annotation: The annotation for the images.
        tags: Tags for the images.
        folderId: If this parameter is defined, the image will be added to the corresponding folder.
        step: interval image num of doing POST. Defaults is None (disabled)
        token: API token for authentication. Defaults to None.

    Returns:
        Response: return of requests.posts
    """
    API_URL = f"{server_url}:{port}/api/item/addFromPaths"
    
    dprint(f"DEBUG [add_from_paths] API URL: {API_URL}")
    dprint(f"DEBUG [add_from_paths] FolderID: {folderId}")
    dprint(f"DEBUG [add_from_paths] Number of files: {len(files)}")

    if step:
        step = int(step)
        dprint(f"DEBUG [add_from_paths] Using step: {step}")

    def _init_data():
        _data = {"items": []}
        if folderId and folderId != "":
            _data.update({"folderId": folderId})
        if token:
            _data.update({"token": token})
        return _data

    r_posts = []
    data = _init_data()
    for _index, _item in enumerate(files):
        _item:EAGLE_ITEM_PATH = _item
        _data = _item.output_data()
        if _data:
            data["items"].append(_data)
        if step and step > 0:
            if ((_index + 1) - ((_index + 1) // step) * step) == 0:
                dprint(f"DEBUG [add_from_paths] Sending batch {_index + 1}")
                _ret = requests.post(API_URL, json=data)
                try:
                    r_posts.append(_ret.json())
                    dprint(f"DEBUG [add_from_paths] Batch response: {_ret.json()}")
                except:
                    r_posts.append(_ret)
                    dprint(f"DEBUG [add_from_paths] Raw batch response: {_ret}")
                data = _init_data()
    if (len(data["items"]) > 0) or (not step or step <= 0):
        dprint("DEBUG [add_from_paths] Sending final batch")
        _ret = requests.post(API_URL, json=data)
        try:
            r_posts.append(_ret.json())
            dprint(f"DEBUG [add_from_paths] Final batch response: {_ret.json()}")
        except:
            r_posts.append(_ret)
            dprint(f"DEBUG [add_from_paths] Raw final batch response: {_ret}")

    return [ x for x in r_posts if x != "" ]