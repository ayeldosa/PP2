from functools import reduce

nums = [1, 2, 3, 4]

total = reduce(lambda x, y: x + y, nums)
print(total)