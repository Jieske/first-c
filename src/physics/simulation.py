import json
import os
import re

# 加载配置文件
config_path = os.path.join(os.path.dirname(__file__), '../../config/config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

# 加载所有 JSON 文件
data_dir = os.path.join(os.path.dirname(__file__), '../../data/db/')
all_data = {}

# 遍历 data/db/ 目录下的所有 JSON 文件
for filename in os.listdir(data_dir):
    if filename.endswith('.json'):
        file_path = os.path.join(data_dir, filename)
        with open(file_path, 'r') as f:
            try:
                data = json.load(f)
                all_data[filename] = data
            except json.JSONDecodeError as e:
                print(f"错误加载 {filename}: {e}")

# 辅助函数：从 nameString 字段中提取实际名称（去除 <link> 标签）
def extract_name(name_string):
    if not name_string:
        return None
    match = re.match(r'<link="[^"]+">(.*?)</link>', name_string)
    return match.group(1) if match else name_string

# 通用查找函数
def search_file(data, query, search_fields, is_list=False, recursive=False, path=None):
    if path is None:
        path = []
    
    if is_list:
        for item in data:
            if isinstance(item, dict):
                for field in search_fields:
                    value = item.get(field)
                    if value == query or (field == 'name' and extract_name(value) == query):
                        return item, path
                if recursive and 'children' in item:
                    result, child_path = search_file(item['children'], query, search_fields, is_list=True, recursive=True, path=path + [item.get('id', item.get('name'))])
                    if result:
                        return result, child_path
    else:
        for key, value in data.items():
            if isinstance(value, dict):
                for field in search_fields:
                    if value.get(field) == query or (field == 'name' and extract_name(value.get(field)) == query):
                        return value, path + [key]
                if recursive and 'children' in value:
                    result, child_path = search_file(value['children'], query, search_fields, is_list=True, recursive=True, path=path + [key])
                    if result:
                        return result, child_path
    return None, None

# 文件映射：定义每个文件的数据结构和查找字段
file_mappings = {
    'elements.json': {
        'data_key': 'elementTable',
        'search_fields': ['id', 'tag.Name'],
        'structure': 'dict'
    },
    'building.json': {
        'data_key': 'buildingDefs',
        'search_fields': ['PrefabID', 'Tag.Name'],
        'structure': 'list'
    },
    'codex.json': {
        'data_key': 'categoryEntries',
        'search_fields': ['id', 'name'],
        'structure': 'dict',
        'recursive': True
    },
    'db.json': {
        'data_key': 'diseases',
        'search_fields': ['Id', 'Name'],
        'structure': 'list'
    },
    'entities.json': {
        'data_key': 'entities',
        'search_fields': ['name', 'nameString'],
        'structure': 'list'
    },
    'food.json': {
        'data_key': 'food',
        'search_fields': ['id', 'name'],
        'structure': 'list'
    },
    'geyser.json': {
        'data_key': 'geysers',
        'search_fields': ['id', 'name'],
        'structure': 'list'
    },
    'plants.json': {
        'data_key': 'plants',
        'search_fields': ['id', 'name'],
        'structure': 'list'
    },
    'rooms.json': {
        'data_key': 'rooms',
        'search_fields': ['id', 'name'],
        'structure': 'list'
    },
    'tech.json': {
        'data_key': 'techs',
        'search_fields': ['id', 'name'],
        'structure': 'list'
    },
    'attributes.json': {
        'data_key': 'attributes',
        'search_fields': ['id', 'name'],
        'structure': 'list'
    }
}

# 通过名字或ID查找对象
def find_element(query):
    for filename, mapping in file_mappings.items():
        data = all_data.get(filename, {}).get(mapping['data_key'], {})
        if not data:
            continue
        
        search_fields = mapping['search_fields']
        structure = mapping['structure']
        recursive = mapping.get('recursive', False)
        
        if structure == 'dict':
            item, path = search_file(data, query, search_fields, is_list=False, recursive=recursive)
        elif structure == 'list':
            item, path = search_file(data, query, search_fields, is_list=True, recursive=recursive)
        
        if item:
            source_file = filename
            if path:
                source_file += f" (路径: {' -> '.join(path)})"
            return item, source_file
    
    print(f"未在任何 JSON 文件中找到 '{query}'。")
    return None, None

# 测试模拟程序
def run_simulation():
    print("欢迎使用《缺氧》数据查询模拟程序")
    while True:
        query = input("请输入名字或ID（输入 'exit' 退出）：")
        if query.lower() == 'exit':
            break
        
        item, source_file = find_element(query)
        if item:
            print(f"找到对象: {source_file}")
            print(json.dumps(item, indent=2, ensure_ascii=False))
            print("---")

if __name__ == "__main__":
    run_simulation()
