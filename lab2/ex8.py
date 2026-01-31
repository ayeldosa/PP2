n = int(input())

power = 1
result = []

while power <= n:
    result.append(str(power))
    power *= 2

print(" ".join(result))
