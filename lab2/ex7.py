n = int(input())
arr = list(map(int, input().split()))

max_value = arr[0]
max_pos = 1

for i in range(1, n):
    if arr[i] > max_value:
        max_value = arr[i]
        max_pos = i + 1

print(max_pos)
