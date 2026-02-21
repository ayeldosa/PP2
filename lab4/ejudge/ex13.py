import json
import re

def resolve_query(data, query):
    parts = re.split(r'\.|(?=\[)|(?<=\])', query)
    parts = [p for p in parts if p]
    
    current = data
    
    for part in parts:
        if part.startswith('[') and part.endswith(']'):
            index = int(part[1:-1])
            if isinstance(current, list) and 0 <= index < len(current):
                current = current[index]
            else:
                return "NOT_FOUND"
        else:
            if isinstance(current, dict) and part in current:
                current = current[part]
            else:
                return "NOT_FOUND"
    
    return json.dumps(current, separators=(',', ':'))

data = json.loads(input().strip())
n = int(input().strip())

for _ in range(n):
    query = input().strip()
    print(resolve_query(data, query))