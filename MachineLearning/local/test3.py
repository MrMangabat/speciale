import os
import json

from msc.utils.utility import get_root_path

json_path = os.path.join(get_root_path(), 'data', 'json')
ls_dir = os.listdir(json_path)
json_file = os.path.join(json_path, 'V-0161-03.json')
with open(json_file, 'r') as f:
    case_json = json.load(f)
    print(case_json['summary'])
