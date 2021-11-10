import glob
import yaml
import json

def to_json(path):
    # print(f"path: {path}")
    stem = path.rsplit(".", 1)[0]
    data = yaml.load(open(path, "r", encoding="UTF-8"), Loader=yaml.FullLoader)

    print(f"stem: {stem}.json")
    json.dump(data, open(f"{stem}.json", "w", encoding="utf-8"), ensure_ascii=False, indent=4)


for path in [f.replace("\\", "/") for f in glob.glob("./configs/*.yml")]:
    to_json(path)