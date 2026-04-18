with open("sample.txt", "a") as f:
    f.write("\nNew line added")

with open("sample.txt", "r") as f:
    print(f.read())