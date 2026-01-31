n = int(input())
arr = list(map(int, input().split()))

squares = [x**2 for x in arr]

print(*squares)
