import re

text = "abbb"

pattern = r"ab*"

if re.fullmatch(pattern, text):
    print("Match")
else:
    print("No match")