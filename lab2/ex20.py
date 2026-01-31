n = int(input())

doc = {}

for _ in range(n):
    parts = input().split()

    if parts[0] == "set":
        # parts = ["set", key, value]
        key = parts[1]
        value = parts[2]
        doc[key] = value

    elif parts[0] == "get":
        # parts = ["get", key]
        key = parts[1]
        if key in doc:
            print(doc[key])
        else:
            print(f"KE: no key {key} found in the document")
