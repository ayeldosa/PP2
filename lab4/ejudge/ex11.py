import json

def apply_patch(source, patch):
    for key, value in patch.items():
        if value is None:
            if key in source:
                del source[key]
        elif key not in source:
            source[key] = value
        elif isinstance(source[key], dict) and isinstance(value, dict):
            apply_patch(source[key], value)
        else:
            source[key] = value
    
    return source

source = json.loads(input().strip())
patch = json.loads(input().strip())

result = apply_patch(source, patch)

print(json.dumps(result, sort_keys=True, separators=(',', ':')))