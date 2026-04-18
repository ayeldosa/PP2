import re

text = "HelloWorldPython"

result = re.split(r"(?=[A-Z])", text)

print(result)