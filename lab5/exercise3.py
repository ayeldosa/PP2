import re

text = "hello_world test_text"

matches = re.findall(r"[a-z]+_[a-z]+", text)

print(matches)