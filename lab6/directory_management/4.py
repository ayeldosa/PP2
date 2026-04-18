import os
import shutil

# создаем файл
with open("sample.txt", "w") as f:
    f.write("hello")

os.makedirs("folder/subfolder", exist_ok=True)

shutil.move("sample.txt", "folder/sample.txt")
shutil.copy("folder/sample.txt", "folder/subfolder/sample_copy.txt")