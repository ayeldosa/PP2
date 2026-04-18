import re

text = "Hello world Python"

matches = re.findall(r"[A-Z][a-z]+", text)

print(matches)