import os

import gradio as gr

from modules import paths, script_callbacks, shared

from scripts.eagleapi import api_application
from scripts.eagleapi import api_item
from scripts.eagleapi import api_util
from scripts.parser import Parser
from scripts.tag_generator import TagGenerator

DEBUG = True  # デバッグ出力を有効化
def dprint(str):
    if DEBUG:
        print(str)

path_root = paths.script_path

def on_ui_settings():
    # flg: Enable/Disable
    shared.opts.add_option("enable_eagle_integration", shared.OptionInfo(False, "Send all image to Eagle", section=("eagle_pnginfo", "Eagle Pnginfo")))
    # flg: save generation info to annotation
    shared.opts.add_option("save_generationinfo_to_eagle_as_annotation", shared.OptionInfo(False, "Save Generation info as Annotation", section=("eagle_pnginfo", "Eagle Pnginfo")))
    # flg: save positive prompt to tags
    shared.opts.add_option("save_positive_prompt_to_eagle_as_tags", shared.OptionInfo(False, "Save positive prompt to Eagle as tags", section=("eagle_pnginfo", "Eagle Pnginfo")))
    shared.opts.add_option("save_negative_prompt_to_eagle_as", shared.OptionInfo("n:tag", "Save negative prompt as", gr.Radio, {"choices": ["None", "tag", "n:tag"]}, section=("eagle_pnginfo", "Eagle Pnginfo")))
    shared.opts.add_option("use_prompt_parser_when_save_prompt_to_eagle_as_tags", shared.OptionInfo(False, "Use prompt parser when save prompt to eagle as tags", section=("eagle_pnginfo", "Eagle Pnginfo")))
    # txt: Additinal tags
    shared.opts.add_option("additional_tags_to_eagle", shared.OptionInfo("", "Additinal tag pattern", section=("eagle_pnginfo", "Eagle Pnginfo")))
    # txt: server_url
    shared.opts.add_option("outside_server_url_port", shared.OptionInfo("", "Outside Eagle server connection (url:port)", section=("eagle_pnginfo", "Eagle Pnginfo")))
    # specify Eagle folderID
    shared.opts.add_option("save_to_eagle_folderid", shared.OptionInfo("", "(option) FolderID or FolderName on Eagle", component_args=shared.hide_dirs, section=("eagle_pnginfo", "Eagle Pnginfo")))
    # specify Eagle folderID
    shared.opts.add_option("allow_to_create_folder_on_eagle", shared.OptionInfo(False, "(option) Allow to create folder on Eagle, if specified foldername dont exists.", section=("eagle_pnginfo", "Eagle Pnginfo")))
    # txt: API token
    shared.opts.add_option("eagle_api_token", shared.OptionInfo("", "Eagle API Token", section=("eagle_pnginfo", "Eagle Pnginfo")))

# image saved callback
def on_image_saved(params:script_callbacks.ImageSaveParams):
    if not shared.opts.enable_eagle_integration:
        dprint(f"DEBUG: Eagle integration is DISABLED")
        return

    try:
        dprint(f"DEBUG: Eagle integration is ENABLED")
        # collect info
        fullfn = os.path.join(path_root, params.filename)
        dprint(f"DEBUG: Full file path: {fullfn}")
        info = params.pnginfo.get('parameters', None)
        filename = os.path.splitext(os.path.basename(fullfn))[0]
        dprint(f"DEBUG: File name: {filename}")
        #
        pos_prompt = params.p.prompt
        neg_prompt = params.p.negative_prompt
        #
        annotation = None
        tags = []
        if shared.opts.save_generationinfo_to_eagle_as_annotation:
            annotation = info
        if shared.opts.save_positive_prompt_to_eagle_as_tags:
            if len(pos_prompt.split(",")) > 0:
                tags += Parser.prompt_to_tags(pos_prompt)
        if shared.opts.save_negative_prompt_to_eagle_as == "tag":
            if len(neg_prompt.split(",")) > 0:
                tags += Parser.prompt_to_tags(neg_prompt)
        elif shared.opts.save_negative_prompt_to_eagle_as == "n:tag":
            if len(neg_prompt.split(",")) > 0:
                tags += [ f"n:{x}" for x in Parser.prompt_to_tags(neg_prompt) ]
        if shared.opts.additional_tags_to_eagle != "":
            gen = TagGenerator(p=params.p, image=params.image)
            _tags = gen.generate_from_p(shared.opts.additional_tags_to_eagle)
            if _tags and len(_tags) > 0:
                tags += _tags
        
        dprint(f"DEBUG: Tags: {tags}")
        dprint(f"DEBUG: Annotation available: {'Yes' if annotation else 'No'}")

        def _get_folderId(folder_name_or_id, allow_create_new_folder, server_url="http://localhost", port=41595, token=None):
            try:
                dprint(f"DEBUG: Getting folder ID")
                dprint(f"DEBUG: Server URL: {server_url}, Port: {port}")
                dprint(f"DEBUG: Folder name/ID: {folder_name_or_id}")
                dprint(f"DEBUG: Token: {token[:8]}... (truncated)") if token else dprint("DEBUG: No token")
                
                _ret = api_util.find_or_create_folder(folder_name_or_id, allow_create_new_folder, server_url, port, token=token)
                dprint(f"DEBUG: Folder ID result: {_ret}")
                return _ret
            except Exception as e:
                print(f"Error getting folder ID: {e}")
                return ""

        # send to Eagle
        token = shared.opts.eagle_api_token
        dprint(f"DEBUG: Token configured: {'Yes' if token else 'No'}")

        if shared.opts.outside_server_url_port != "" and api_application.is_valid_url_port(shared.opts.outside_server_url_port, token=token):
            # send by URL
            try:
                dprint(f"DEBUG: Using remote server: {shared.opts.outside_server_url_port}")
                item = api_item.EAGLE_ITEM_URL(
                        url=fullfn,
                        name=filename,
                        tags=tags,
                        annotation=annotation
                    )
                server_url, port = api_util.get_url_port(shared.opts.outside_server_url_port)
                dprint(f"DEBUG: Parsed server URL: {server_url}, port: {port}")

                if not server_url or not port:
                    print("Error: Invalid server URL or port")
                    return

                folderId = _get_folderId(
                    shared.opts.save_to_eagle_folderid, 
                    shared.opts.allow_to_create_folder_on_eagle, 
                    server_url=server_url, 
                    port=port,
                    token=token
                )
                dprint(f"DEBUG: Using folder ID: {folderId}")

                _ret = api_item.add_from_URL_base64(
                    item,
                    folderId=folderId,
                    server_url=server_url,
                    port=port,
                    token=token
                )
                dprint(f"DEBUG: API Response status: {_ret.status_code}")
                dprint(f"DEBUG: API Response content: {_ret.content.decode('utf-8') if _ret.content else 'No content'}")
            except Exception as e:
                print(f"Error sending to remote Eagle server: {e}")
        else:
            # send to local
            try:
                dprint("DEBUG: Using local server")
                item = api_item.EAGLE_ITEM_PATH(
                    filefullpath=fullfn,
                    filename=filename,
                    annotation=annotation,
                    tags=tags
                )
                folderId = _get_folderId(
                    shared.opts.save_to_eagle_folderid, 
                    shared.opts.allow_to_create_folder_on_eagle,
                    token=token
                )
                dprint(f"DEBUG: Using local folder ID: {folderId}")

                _ret = api_item.add_from_path(
                    item=item,
                    folderId=folderId,
                    token=token
                )
                dprint(f"DEBUG: Local API Response status: {_ret.status_code}")
                dprint(f"DEBUG: Local API Response content: {_ret.content.decode('utf-8') if _ret.content else 'No content'}")
            except Exception as e:
                print(f"Error sending to local Eagle server: {e}")
    except Exception as e:
        print(f"Error in on_image_saved: {e}")

# on_image_saved
script_callbacks.on_image_saved(on_image_saved)

#
script_callbacks.on_ui_settings(on_ui_settings)
