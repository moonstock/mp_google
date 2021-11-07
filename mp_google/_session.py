# - pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
# - pip install --upgrade oauth2client
# - pip install gspread

import os, sys
import yaml
import json

from googleapiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials  ## googledrive 인증


PATH_VERSIONS = os.path.join(os.path.dirname(__file__), "settings/google_api_versions.yml")


def _file_to_dict(path):
    """yml/json -> dict

    Args:
        path (str): yml/json 파일 경로

    Returns:
        [dict]: yml/json -> dict
    """
    ext = path.split('.')[-1]
    if ext == 'yml' or ext == 'yaml':  ## NOTE: yml 파일
        return yaml.load(open(path, "r", encoding="UTF-8"), Loader=yaml.FullLoader)
    elif ext == 'json':  ## NOTE: json 파일
        return json.load(open(path, "r", encoding="UTF-8"))


def _account_scopes_by_path(path="settings/google_account_mats.yml"):
    """account, scopes 반환

    Args:
        path (str, optional): google service account 파일(yml or json). Defaults to ["settings/api_google_mats.yml", "settings/account_google_mats.yml"].

    Returns:
        [tuple]: (account:dict, scopes:list)
    """
    path = [path, os.path.join(os.path.dirname(__file__), "settings/google_scopes.yml")]
    return tuple(_file_to_dict(_path) for _path in path)


def session(path="settings/google_account_mats.yml", api="gspread"):
    """session(connect google api service)

    Args:
        path (str, optional): google service account 파일(yml or json). Defaults to "settings/google_account_mats.yml".
        api (str, optional): google api(sheets/drive/...). Defaults to "gspread".

    Returns:
        [type]: [description]
    """

    (account, scopes) = _account_scopes_by_path(path)

    ## NOTE: Google API 접속 인증, client 생성, api에 따라서 scopes 변경
    credentials = ServiceAccountCredentials.from_json_keyfile_dict(account, scopes[api])

    ## NOTE: gspread는 credentials, google api는 service 반환
    api = api.lower()
    if 'gspread' in api:
        return credentials
    else:
        return build(api, _file_to_dict(PATH_VERSIONS)[api], credentials=credentials)


if __name__ == "__main__":
    api = session(path="settings/google_account_mats.yml", api="sheets")
    print(api)
    