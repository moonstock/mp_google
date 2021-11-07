import json

def save_to_json(data, path):
    with open(path, 'w', encoding='utf8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


