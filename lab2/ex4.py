n = int(input())
numbers = list(map(int, input().split()))

count_positive = sum(1 for num in numbers if num > 0)

print(count_positive)
