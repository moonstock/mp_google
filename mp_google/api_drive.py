import sys, os, io
from apiclient.http import MediaFileUpload
from googleapiclient.http import MediaIoBaseDownload

##------------------------------------------------------------
## User 모듈
##------------------------------------------------------------
sys.path.append(os.path.join(os.path.dirname(__file__), '.')) ## Note: 현재 디렉토리 기준 상대 경로 설정
from _session import (session)
# from utils_basic import (_create_folder)

# from logger_csv import log_csv

## 보조 함수(file, sheet)
##=========================================================
def _create_folder(name):
    """
    폴더가 있는지 확인하고, 없으면 생성
    """
    print(f"folder: {os.path.dirname(name)}")
    os.makedirs(os.path.dirname(name), exist_ok=True)


def api(path="settings/google_account_mats.yml"):
    """google drive api

    Args:
        path (list, optional): [description]. Defaults to ["settings/api_google_mats.yml", "settings/account_google_mats.yml"].

    Returns:
        [type]: [description]
    """
    return session(path=path, api="drive")


def _identify_mimetype(title):
    pass


def _set_drive_files(config):
    """config의 'drive' 'ids' => file 리스트

    Args:
        config (dict): google api 설정 파일(ex) settings/api_google_mats.yml) -> dict

    Returns:
        [dict]: drive 파일 리스트
    """
    return {
        name: config['prefix']['drive'] + id
        for name, id in config['ids']['drive'].items()
    }


def _id_by_title(title, api):
    return api.files().list(
        q = f"name = '{title}'",
        fields = "nextPageToken, files(id, name)"
    ).execute().get('files', [])[0].get('id')


## list / CRUD
##========================================================

def file_list(api=None, type='file'):
    """파일 or 폴더 목록

    Args:
        type (str): 목록으로 얻으려는 대상(file/folder/both)
        api (obj): google drive service (<googleapiclient.discovery.Resource object>)

    Returns:
        [dict]: {<file_name>: <file_id>, ....}
    """
    query = None
    if type == 'file':
        query = "mimeType != 'application/vnd.google-apps.folder'"  ## folder가 아닌 파일
    elif type == 'folder':
        query = "mimeType = 'application/vnd.google-apps.folder'"  ## folder

    results = api.files().list(
        q = query,
        # spaces = 'drive',
        # pageSize=10,
        fields="nextPageToken, files(id, name)"
    ).execute()

    return {item['name']: item['id'] for item in results.get('files', [])}


def create_folder(title, api):
    """폴더 생성

    Args:
        title (str): 생성할 폴더 이름
        api ([type]): [description]

    Returns:
        [dict]: {<folder_name>: <folder_id>}
    """
    file_metadata = {
        'name': title,
        'mimeType': 'application/vnd.google-apps.folder'
    }
    folder = api.files().create(
        body = file_metadata,
        fields = 'id'
    ).execute()

    return {folder.get('name'): folder.get('id')}


def _delete_file_by_id(file_id, api):
    """파일 삭제(file id)

    Args:
        file_id (str): 삭제할 파일의 file_id
        api ([type]): [description]
    """
    api.files().delete(fileId=file_id).execute()


def delete_file(title, api):
    """파일 삭제

    Args:
        title (str): 삭제할 파일의 파일 이름
        api ([type]): [description]
    """
    file_id = _id_by_title(title, api)
    # print(f"file_id: {file_id}")
    _delete_file_by_id(file_id, api)
    return {title: file_id}


def upload_file(path, title=None, folder=None, mimetype=None, api=None):
    """파일 업로드

    Args:
        path (str): 업로드할 파일 경로
        title (str, optional): 저장할 이름(None: 경로의 파일이름). Defaults to None.
        folder (str, optional): 업로드할 drive 폴더 이름. Defaults to None.
        mimetype (str, optional): 업로드할 파일 mimetype(None: 자동 감지?). Defaults to None.
        api ([type], optional): [description]. Defaults to None.

    Returns:
         [dict]: {<file_name>: <file_id>}
    """

    file_metadata = {}
    file_metadata['name'] = path.split('/')[-1] if title == None else title

    if mimetype != None:
        file_metadata['mimetype'] = mimetype
        media = MediaFileUpload(path, mimetype=mimetype, resumable=True)
    else:
        media = MediaFileUpload(path, resumable=True)

    if folder != None:
        file_metadata['parents'] = [_id_by_title(folder, api)]

    file = api.files().create(
        body = file_metadata,
        media_body = media,
        fields = 'id'
    ).execute()

    return {file.get('name'): file.get('id')}


def _download_file_by_id(file_id, path=None, api=None, type='binary'):
    """파일 다운로드(file_id)

    Args:
        file_id (str): 다운로드할 파일의 file_id
        path (str): 저장할 경로
        api ([type]): [description]
        type (str): 다운로드할 파일 타입('binary': 이진 파일 / 'text': 텍스트 파일)
    """
    type = type[0].lower()

    _create_folder('/'.join(path.split('/')[:-1]))  ## NOTE: folder 생성
    if type == 'd':  ## Docs Editors files
        request = api.files().export_media(fileId=file_id, mimeType='text/csv')
        fh = io.BytesIO(path)
    else:  ## NOTE: type = binary / text 의미 없음
        request = api.files().get_media(fileId=file_id)
        fh = open(path, 'wb')

    downloader = MediaIoBaseDownload(fh, request)

    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}")


def download_file(title, folder='.', api=None):
    """파일 다운로드

    Args:
        title (str): google drive 내의 파일 이름
        folder (str, optional): 저장할 폴더 이름. Defaults to '.'
        api ([type], optional): [description]. Defaults to None.
    """
    path = f"{folder}/{title}"
    _download_file_by_id(_id_by_title(title, api), path=path, api=api, type='binary')


def download_doc(title, folder='.', api=None):
    """파일 다운로드(Docs Editors file)

    Args:
        title (str): google drive 내의 파일 이름
        folder (str, optional): 저장할 폴더 이름. Defaults to '.'
        api ([type], optional): [description]. Defaults to None.
    """
    path = f"{folder}/{title}"
    _download_file_by_id(_id_by_title(title, api), path=path, api=api, type='doc')


def share_file(file_id, api):
    # file_id = '1sTWaJ_j7PkjzaBWtNc3IzovK5hQf21FbOw9yLeeLPNQ'
    def callback(request_id, response, exception):
        if exception:
            # Handle error
            print(exception)
        else:
            print("Permission Id: %s" % response.get('id'))

    batch = api.new_batch_http_request(callback=callback)
    user_permission = {
        'type': 'user',
        'role': 'writer',
        # 'role': 'owner',
        'emailAddress': 'moonitdev@gmail.com'
        # 'emailAddress': 'monblue@snu.ac.kr'
    }
    batch.add(api.permissions().create(
            fileId=file_id,
            body=user_permission,
            fields='id',
    ))
    # domain_permission = {
    #     'type': 'domain',
    #     'role': 'reader',
    #     'domain': 'example.com'
    # }
    # batch.add(api.permissions().create(
    #         fileId=file_id,
    #         body=domain_permission,
    #         fields='id',
    # ))
    batch.execute()


if __name__ == "__main__":

    ## NOTE: 테스트
    api = api(path="settings/google_account_mats.yml")
    # # print(api)
    
    ls = file_list(api, type='both')
    print(ls)

    # sheets = {
    #     # 'Gatsby': '100PbplhMziDbU6fygezclb2wyWz6fmao-eR6LZ1Y4kk', 
    #     # 'Coin_Exchanges': '1x4su7uJELgcMMd0MlqvWFKf28QiKNQbDtMARnkAINY0',
    #     'ROK_SETTINGS': '1hJ4OyhvRNKSz1zBIagX9r3_O-t-Go5C0MmmK_Hh1AAs'
    # }

    # for name, id in sheets.items():
    #     share_file(id, api)

    # share_file(file_id, api)

    # _delete_file_by_id(file_id, api)

    # for k, id in dels.items():
    #     try:
    #         _delete_file_by_id(id, api)
    #     except:
    #         pass

    # log_csv(name='googledrive', msg='test from api_google_drive.py')

    # create_folder('users', api)

    # path = 'upbitAPI_.csv'
    # path = 'files/바이올린이미지2.webp'
    # path = 'files/바이올린.jfif'
    # upload_file(path, folder='API', api=api)

    # title = '바이올린이미지2.webp'
    # title = 'users'
    # title = '바이올린.jfif'
    
    # title = 'upbitAPI_.csv'
    # # path = 'files/'
    # type = 'text'
    # type = 'binary'
    # download_file(title, folder='_files', api=api)

    # print(delete_file(title, api))

    # path = 'aa.jpg'
    # upload_file(path, api, title=None, folder_id=None, mimetype=None)
