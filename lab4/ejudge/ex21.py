import importlib

n = int(input())

for _ in range(n):
    module_path, attr = input().split()
    
    try:
        module = importlib.import_module(module_path)
    except ModuleNotFoundError:
        print("MODULE_NOT_FOUND")
        continue
    
    if not hasattr(module, attr):
        print("ATTRIBUTE_NOT_FOUND")
        continue
    
    attr_value = getattr(module, attr)
    if callable(attr_value):
        print("CALLABLE")
    else:
        print("VALUE")