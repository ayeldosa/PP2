n = int(input())
freq = {}

for _ in range(n):
    num = input().strip()     # читаем как строку!
    freq[num] = freq.get(num, 0) + 1

count_three = 0
for v in freq.values():
    if v == 3:
        count_three += 1

print(count_three)
