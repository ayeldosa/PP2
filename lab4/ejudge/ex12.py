import json

def deep_diff(obj1, obj2, path=""):
    differences = []
    all_keys = set(obj1.keys()) | set(obj2.keys()) if isinstance(obj1, dict) and isinstance(obj2, dict) else set()
    
    if isinstance(obj1, dict) and isinstance(obj2, dict):
        for key in sorted(all_keys):
            current_path = f"{path}.{key}" if path else key
            
            if key not in obj1:
                old_val = "<missing>"
                new_val = json.dumps(obj2[key], separators=(',', ':'))
                differences.append(f"{current_path} : {old_val} -> {new_val}")
            elif key not in obj2:
                old_val = json.dumps(obj1[key], separators=(',', ':'))
                new_val = "<missing>"
                differences.append(f"{current_path} : {old_val} -> {new_val}")
            elif isinstance(obj1[key], dict) and isinstance(obj2[key], dict):
                differences.extend(deep_diff(obj1[key], obj2[key], current_path))
            elif obj1[key] != obj2[key]:
                old_val = json.dumps(obj1[key], separators=(',', ':'))
                new_val = json.dumps(obj2[key], separators=(',', ':'))
                differences.append(f"{current_path} : {old_val} -> {new_val}")
    
    return differences

obj1 = json.loads(input().strip())
obj2 = json.loads(input().strip())

result = deep_diff(obj1, obj2)

if result:
    for line in sorted(result):
        print(line)
else:
    print("No differences")