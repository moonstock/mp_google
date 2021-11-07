
import os, sys
import os.path
import yaml
import csv
import pandas as pd
# import pickle
import json
import gspread

##------------------------------------------------------------
## User 모듈
##------------------------------------------------------------
# sys.path.append(os.path.join(os.path.dirname(__file__), '.')) ## Note: 현재 디렉토리 기준 상대 경로 설정
from _session import (session)
# from utils_basic import (_create_folder, _dicts_to_lists, _fn)


NEW_ROWS = 500
NEW_COLS = 30

## 보조 함수(rows, list, dicts, csv)
##=========================================================
def _create_folder(name):
    """
    폴더가 있는지 확인하고, 없으면 생성
    """
    print(f"folder: {os.path.dirname(name)}")
    os.makedirs(os.path.dirname(name), exist_ok=True)


def _dicts_to_lists(dicts):
    """dicts(dictionary 리스트) -> lists(list 리스트)

    Args:

    Returns:
        [list of list]: list 리스트 ex) [['a', 'b'], [1, 2], [3, 4]]
    """
    return [list(dicts[0].keys())] + pd.DataFrame(dicts).values.tolist()


def _fn(level=0):
    """함수 이름 출력

    Args:
        level (int, optional): 함수 위치(레벨): 0: 현재 함수, 1: 호출한 함수, 2: 1을 호출한 함수. Defaults to 0.

    Returns:
        str: 함수 이름
    """
    return sys._getframe(level).f_code.co_name


def _set_data_lists(data, overwrite=True, noheader=False):
    """data를 추가, 덮어쓰기(write_sheet_new)/뒤에 추가(write_sheet_add) 맞게 변경

    Args:
        data ([type]): [description]
        overwrite (bool, optional): True: (data 덮어쓰기, header 포함), False: (data 추가, header 제외). Defaults to False.
        noheader (bool, optional): True: header가 없는 데이터(lists만 해당). Defaults to False.
    """
    if overwrite:  ## NOTE: 덮어쓰기, header 포함
        if 'frame' in str(type(data)):
            data = [list(data.columns)] + data.values.tolist()  ## TODO: 확인 필요
            # [dataframe.columns.values.tolist()] + dataframe.values.tolist()
        elif type(data[0]) == dict:
            data = _dicts_to_lists(data)
        
        if noheader and type(data[0]) == list:  ## NOTE: header 임의 생성
            header = [f"field{i}" for i in range(len(data[0]))]
            data = [header] + data
    else:  ## NOTE: data 추가, header 제외
        if 'frame' in str(type(data)):
            data = data.values.tolist()  ## TODO: 확인 필요
            # [dataframe.columns.values.tolist()] + dataframe.values.tolist()
        elif type(data[0]) == dict:
            start = 0 if len(data) < 2 else 1  ## NOTE: 0: len(data) < 2인 경우
            data = _dicts_to_lists(data)[start:]
        
        if not noheader and type(data[0]) == list:  ## NOTE: header 리스트 제외
            start = 0 if len(data) < 2 else 1  ## NOTE: 0: len(data) < 2인 경우
            data = data[start:]

    return data



def _first_filled_cell(rows):
    """비어있지 않은 첫번째 cell 
    TODO: <가정> 비어있지 않은 첫번째 행row(header)에서의 비어있지 않는 첫번째 열column은 이후에도 적용됨
          <가정>에 맞지 않는 일반적인 경우에도 적용되도록 변경 (다소 복잡하지만) 
    Args:
        rows (list of list): [['', '', '', ''], ['', '', '', ''], ['', '', 'host', 'port'], ['', '', '127.0.0.1', '27017']]

    Returns:
        [list]: 비어있지 않은 첫번째 cell [2, 2]
    """
    cell = [0, 0]
    for i, row in enumerate(rows):
        if ''.join(row) != '':
            cell[0] = i
            break

    for j, v in enumerate(rows[cell[0]]):
            if v != '':
                cell[1] = j
                break

    return cell


def _last_filled_cell(rows):
    """비어있지 않은 마지막 cell
    TODO: <가정> 비어있지 않은 첫번째 행row(header)에서의 비어있지 않는 첫번째 열column은 이후에도 적용됨
          <가정>에 맞지 않는 일반적인 경우에도 적용되도록 변경 (다소 복잡하지만) 
    Args:
        rows (list of list): [['', '', '', ''], ['', '', '', ''], ['', '', 'host', 'port'], ['', '', '127.0.0.1', '27017']]

    Returns:
        [list]: 비어있지 않은 마지막 cell [2, 2]
    """
    cell = [len(rows), 0]
    first_row = 0
    for i, row in enumerate(rows):
        if ''.join(row) != '':
            first_row = i
            break
    
    if first_row == 0:
        return cell
    
    for j, v in enumerate(rows[first_row]):
            if v != '':
                cell[1] = j
                break

    return cell

# def _rows_to_dicts(rows, first=(0, 0), header=0):
#     """rows -> dicts
#     TODO: header가 여러 행에 걸쳐 있는 경우 처리

#     Args:
#         rows (list of list): ex) [['', '', '', ''], ['', '', '', ''], ['', '', 'host', 'port'], ['', '', '127.0.0.1', '27017']]
#         first (tuple, optional): 값이 있는 첫번째 cell(행번호, 열번호). Defaults to (2, 2).
#         header (int, optional): header 행번호(first 셀 기준) . Defaults to 0.
#     """
#     rows = [row[first[1]:] for row in rows[first[0]:]]
#     _header = rows[header]
#     rows = rows[header+1:]
#     # print(f"_header: {_header}, rows: {rows}")
#     return [{_header[i]: cell for i, cell in enumerate(row)} for row in rows]


# def _save_rows_csv(path, rows, first=(0, 0), header=0):
#     """rows -> csv spreadsheet

#     Args:
#         path (str): 저장할 csv 파일 경로
#         rows (list of list): ex) [['', '', '', ''], ['', '', '', ''], ['', '', 'host', 'port'], ['', '', '127.0.0.1', '27017']]
#         first (tuple, optional): 값이 있는 첫번째 cell(행번호, 열번호). Defaults to (2, 2).
#         header (int, optional): header 행번호(first 셀 기준) . Defaults to 0.
#     """
#     with open(path, 'w', newline='') as outcsv:
#         writer = csv.writer(outcsv)
#         writer.writerows([row[first[1]:] for row in rows[first[0]:]][header:])


## 보조 함수(connect, spreadsheet, worksheet)
##=========================================================
def api(path="settings/google_account_mats.yml"):
    return gspread.authorize(session(path=path, api="gspread"))


# def _set_gspread_spreadsheets(config):
#     """config의 'sheets' 'ids' => spreadsheet 리스트

#     Args:
#         config (dict): google api 설정 파일(ex) settings/api_google_mats.yml) -> dict

#     Returns:
#         [dict]: spreadsheet 파일 리스트
#     """
#     return {
#         title: config['prefix']['sheets'] + id
#         # title: config['prefix']['sheets'] + id + config['sheets']['suffix']
#         for title, id in config['ids']['sheets'].items()
#     }


def _spreadsheet_by_url(url, api):
    """[summary]

    Args:
        url ([type]): [description]
        api (obj): gspread object

    Returns:
        [type]: [description]
    """
    return api.open_by_url(url)


def _spreadsheet_by_title(title, api):
    """title 이름의 spreadsheet

    Args:
        api (obj): gspread object

    Returns:
        [obj]: spreadsheet obj
    """
    for spreadsheet in api.openall():
        if spreadsheet.title == title:
            return spreadsheet


def _spreadsheet_by_title(title, api):
    """title 이름의 spreadsheet

    Args:
        api (obj): gspread object

    Returns:
        [obj]: spreadsheet obj
    """
    spreadsheet = None
    for _spreadsheet in api.openall():
        if _spreadsheet.title == title:
            spreadsheet = _spreadsheet
            break
    
    return spreadsheet


# def _sheet_by_title(spreadsheet, title):
#     """[summary]

#     Args:
#         title (str): worksheet 이름
#     Returns:
#         [type]: [description]
#     """
#     return spreadsheet.worksheet(title)


## CRUD
##=========================================================

def _spreadsheet_list(api):
    """sheets 파일 리스트(google cloud account 내에 있는 모든 spreadsheets)

    Args:
        api (obj): gspread object

    Returns:
        [dict]: {<title>: <id>}
    """
    return {
        spreadsheet.title: spreadsheet.id
        for spreadsheet in api.openall()
    }


def _sheet_list(spreadsheet):
    """sheets 파일 리스트

    Args:
        spreadsheet (obj): spreadsheet

    Returns:
        [dict]: {<title>: <id>}
    """
    return {
        worksheet.title: worksheet.id
        for worksheet in spreadsheet.worksheets()
    }


def create_spreadsheet_by_title(spreadsheet_title, shares=[{'email': 'moonitdev@gmail.com', 'perm': 'user', 'role': 'owner'}], api=None):
    """sheet spreadsheet 생성

    Args:
        spreadsheet_title (str): spreadsheet 이름
        api (obj): gspread object
    """
    spreadsheet = api.create(spreadsheet_title)
    # sh.share('otto@example.com', perm_type='user', role='writer')
    for _share in shares:
        spreadsheet.share(_share['email'], perm_type=_share['perm'], role=_share['role'])

    return spreadsheet  ## TODO: 리스트에 추가    
    # return {title: sh.id}  ## TODO: 리스트에 추가
    # <Spreadsheet 'A new spreadsheet2' id:15i0pwllckCcK-GxSTDjjLt5bj3Qpmss_rPBWeY2psko>


## NOTE: 별 의미 없음, 그냥 gspread 제목 함수 그대로 쓰는 게 나을 듯
# def create_sheet_by_title(title, spreadsheet):
#     """파일spreadsheet에 title의 worksheet 생성

#     Args:
#         title (str): worksheet 제목
#         spreadsheet (obj): spreadsheet
#     """
#     spreadsheet.add_worksheet(title=title, rows="NEW_ROWS", cols="20")


# def delete_sheet_by_title(title, spreadsheet):
#     # Deleting a Worksheet
#     spreadsheet.del_worksheet(title)


def _read_sheet(worksheet, first=None, header=0, out_type='lists'):
    """sheet에서 값이 있는 영역만 반환

    Args:
        worksheet (obj): worksheet object
        first (list, optional): 첫번째 cell[row, column]. Defaults to None.
        header (int, optional): header행 번호. Defaults to 0.
        out_type (str, optional): 출력 형식(list/dicts/frame). Defaults to 'lists'.

    Returns:
        [list/dicts/dateframe]: worksheet 내용
    """

    rows = worksheet.get_all_values()
    first = _first_filled_cell(rows) if first == None else first
    rows = [row[first[1]:] for row in rows[first[0]:]]
    _header = rows[header]
    rows = rows[header+1:]

    if out_type == 'lists':
        return _header + rows
    elif out_type == 'dicts':
        return [{_header[i]: cell for i, cell in enumerate(row)} for row in rows]
    # elif out_type == 'frame':
    else:  ## NOTE: dataframe
        return pd.DataFrame(rows ,columns=_header)


# def _read_sheet_by_title(spreadsheet, title, first=None, header=0, out_type='lists'):
#     """sheet 파일의 title 제목의 worksheet 내용 반환

#     Args:
#         spreadsheet (obj): spreadsheet object
#         title (str): worksheet 제목
#         first (list, optional): 첫번째 cell[row, column]. Defaults to None.
#         header (int, optional): header행 번호. Defaults to 0.
#         out_type (str, optional): 출력 형식(list/dicts/frame). Defaults to 'lists'.

#     Returns:
#         [list/dicts/dateframe]: worksheet 내용
#     """  
#     return _read_sheet(spreadsheet.worksheet(title), first=first, header=header, out_type=out_type)


def read_sheet(spreadsheet_title, worksheet_title, first=None, header=0, out_type='lists', api=None):
    """spreadsheet_title제목의 spreadsheet에서, worksheet_title 제목의 worksheet 내용 반환

    Args:
        spreadsheet_title (str): spreadsheet 제목
        worksheet_title (str): worksheet 제목
        first (list, optional): 첫번째 cell[row, column]. Defaults to None.
        header (int, optional): header행 번호. Defaults to 0.
        out_type (str, optional): 출력 형식(list/dicts/frame). Defaults to 'lists'.
        api (obj): gspread object
    Returns:
        [list/dicts/dateframe]: worksheet 내용
    """ 
    return _read_sheet(
        _spreadsheet_by_title(spreadsheet_title, api=api).worksheet(worksheet_title), 
        first=first, 
        header=header, 
        out_type=out_type
    )


def download_sheet(folder='.', spreadsheet_title='', worksheet_title='', first=None, header=0, api=None):
    """sheet -> csv file

    Args:
        path (str): csv 파일을 저장할 폴더 이름
        spreadsheet_title (str): spreadsheet 제목
        worksheet_title (str): worksheet 제목
        first (list, optional): 첫번째 cell[row, column]. Defaults to None.
        header (int, optional): header행 번호. Defaults to 0.
        api (obj): gspread object
    """
    ls = read_sheet(spreadsheet_title, worksheet_title, first=first, header=header, out_type='lists', api=api)
    path = f"{folder}/{spreadsheet_title}_{worksheet_title}.csv"
    _create_folder(folder)

    with open(path, 'w', newline='', encoding='utf-8') as outcsv:
        writer = csv.writer(outcsv)
        writer.writerows(ls)


def upload_csv(path, spreadsheet_title='', worksheet_title='', rows=NEW_ROWS, cols=NEW_COLS, api=None):
    """csv 파일 업로드

    Args:
        path ([type]): [description]
        spreadsheet_title (str, optional): [description]. Defaults to ''.
        worksheet_title (str, optional): [description]. Defaults to ''.
        api ([type], optional): [description]. Defaults to None.
    """
    _spreadsheet = _spreadsheet_by_title(spreadsheet_title, api)
    spreadsheet = create_spreadsheet_by_title(spreadsheet_title, api=api) if _spreadsheet == None else _spreadsheet
    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
    except:
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows=rows, cols=cols)
    
    api.import_csv(worksheet.id, open(path, 'r', encoding='utf-8').read())


def _write_sheet(data, spreadsheet_title, worksheet_title, first=[0, 0], rows=NEW_ROWS, cols=NEW_COLS, api=None):
    """data를 worksheet(spreadsheet_title, worksheet_title)에 저장

    Args:
        data (lists/dicts/frame): worksheet에 쓸 data
        spreadsheet_title (str, optional): spreadsheet 제목, spreadsheet이 없으면 생성. Defaults to ''.
        worksheet_title (str, optional): worksheet 제목, worksheet가 없으면 생성. Defaults to ''.
        api ([type], optional): [description]. Defaults to None.
    """
    _spreadsheet = _spreadsheet_by_title(spreadsheet_title, api)
    spreadsheet = create_spreadsheet_by_title(spreadsheet_title, api=api) if _spreadsheet == None else _spreadsheet
    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
    except:
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows=rows, cols=cols)

    # data = _set_data_lists(data, overwrite=True, noheader=False)  ## NOTE: header 포함
    if 'frame' in str(type(data)):
        data = [list(data.columns)] + data.values.tolist()  ## TODO: 확인 필요
        # [dataframe.columns.values.tolist()] + dataframe.values.tolist()
    elif type(data[0]) == dict:
        data = _dicts_to_lists(data)

    # worksheet.update('A2', data)
    _first = gspread.utils.rowcol_to_a1(first[0]+1, first[1]+1)
    worksheet.update(_first, data)


def write_sheet_add(data, spreadsheet_title, worksheet_title, first=None, api=None):
    """data를 worksheet(spreadsheet_title, worksheet_title)에 추가 저장

    Args:
        data (lists/dicts/frame): worksheet에 쓸 data
        spreadsheet_title (str, optional): spreadsheet 제목, spreadsheet이 없으면 생성. Defaults to ''.
        worksheet_title (str, optional): worksheet 제목, worksheet가 없으면 생성. Defaults to ''.
        api ([type], optional): [description]. Defaults to None.
    """
    ## TODO: 없으면 생성(header 추가)
    _spreadsheet = _spreadsheet_by_title(spreadsheet_title, api)
    spreadsheet = create_spreadsheet_by_title(spreadsheet_title, api=api) if _spreadsheet == None else _spreadsheet

    try:
        worksheet = spreadsheet.worksheet(worksheet_title)
        data = _set_data_lists(data, overwrite=False, noheader=False)  ## header 제외
    except:
        print("해당 이름의 worksheet가 없습니다.")
        worksheet = spreadsheet.add_worksheet(title=worksheet_title, rows=NEW_ROWS, cols=NEW_COLS)
        data = _set_data_lists(data, overwrite=True, noheader=False)  ## NOTE: 새로운 sheet를 만들었으므로 header 포함

    # worksheet = _spreadsheet_by_title(spreadsheet_title, api).worksheet(worksheet_title)
    rows = worksheet.get_all_values()
    first = _last_filled_cell(rows) if first == None else first
    print(f"{_fn(1)} data2: {data}")
    _write_sheet(data, spreadsheet_title, worksheet_title, first=first, rows=NEW_ROWS, cols=NEW_COLS, api=api)


def write_sheet_new(data, spreadsheet_title, worksheet_title, rows=NEW_ROWS, cols=NEW_COLS, api=None):
    """data를 worksheet(spreadsheet_title, worksheet_title)에 새로 저장

    Args:
        data (lists/dicts/frame): worksheet에 쓸 data
        spreadsheet_title (str, optional): spreadsheet 제목, spreadsheet이 없으면 생성. Defaults to ''.
        worksheet_title (str, optional): worksheet 제목, worksheet가 없으면 생성. Defaults to ''.
        api ([type], optional): [description]. Defaults to None.
    """
    # data = _set_data_lists(data, overwrite=True, noheader=False)  ## NOTE: header 포함
    _write_sheet(data, spreadsheet_title, worksheet_title, first=[0, 0], rows=rows, cols=cols, api=api)
  

# Updating Cells
# Using A1 notation:

# worksheet.update('B1', 'Bingo!')
# Or row and column coordinates:

# worksheet.update_cell(1, 2, 'Bingo!')
# Update a range

# worksheet.update('A1:B2', [[1, 2], [3, 4]])



if __name__ == "__main__":
    api = api(path="settings/google_account_mats.yml")

    # ls = _spreadsheet_list(api)
    spreadsheet = 'APIs'
    # spreadsheet = 'test_write'
    ls = _sheet_list(_spreadsheet_by_title(spreadsheet, api))
    print(ls)

    # title = 'APIs'
    # print(_spreadsheet_by_title(title, api))
    # ws = _spreadsheet_by_title(title, api).worksheet('abc')
    # print(ws)
    # dicts = [{'a': 1, 'b': 2}, {'a': 3, 'b': 4}, {'a': 5, 'b': 6}, {'a': 7, 'b': 8}]
    # # print(_dicts_to_lists(dicts))

    # write_sheet_add(dicts, spreadsheet_title='test_write', worksheet_title='test_sheet', api=api)
    # write_sheet(dicts, 'test_write', 'test_sheet', api=api)
    # print(read_sheet(spreadsheet_title='test_write', worksheet_title='test_sheet', out_type='frame', api=api))
    
    # print(read_sheet('google_log', 'test3', out_type='dicts', api=api))

    # print(_sheet_list(_spreadsheet_by_title(title, api)))
    # spreadsheet_title = 'APIs'
    # worksheet_title = 'upbit'
    # # r = read_sheet(spreadsheet_title, worksheet_title, out_type='lists', api=api)
    # download_sheet(folder='spreadsheets', spreadsheet_title=spreadsheet_title, worksheet_title=worksheet_title, api=api)
    # r = read_sheet(spreadsheet_title, worksheet_title, out_type='frame', api=api)
    # print(r)
    # gs = _gspread_obj(api)
    # sh = gs.create('A new spreadsheet3')
    # # sh.share('otto@example.com', perm_type='user', role='writer')
    # sh.share('moonitdev@gmail.com', perm_type='user', role='owner')

    # print(sh)
    # spreadsheet = "MATS_STORAGE"
    # worksheet = 'MongoDB'
    # sh = _sheet_by_title(worksheet, spreadsheet, api)
    # # print(sh)
    # print(sh.id)


