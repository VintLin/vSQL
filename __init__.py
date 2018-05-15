from vSQL.vorm import create_all_table
import json

with open('./db.json', 'r', encoding='utf-8') as f:
    js = json.loads(f.read())


