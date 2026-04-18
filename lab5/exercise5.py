import re

text = "axxxb"

pattern = r"a.*b"

if re.fullmatch(pattern, text):
    print("Match")