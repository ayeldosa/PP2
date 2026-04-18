from datetime import datetime, timedelta

a = input()
data = datetime.strptime(a, "%Y.%m.%d")
new_data = data + timedelta(days=10)
new2 = datetime.strftime(new_data, "%Y.%m.%d")
print(new2)