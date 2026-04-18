import re

text = "hello_world_test"

result = re.sub(r"_([a-z])", lambda m: m.group(1).upper(), text)

print(result)