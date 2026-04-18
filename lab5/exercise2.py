import re

text = "abbb"

pattern = r"ab{2,3}"

if re.fullmatch(pattern, text):
    print("Match")