import re

text = "Hello, world. Python is cool"

result = re.sub(r"[ ,.]", ":", text)

print(result)