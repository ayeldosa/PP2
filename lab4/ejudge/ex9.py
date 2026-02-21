def power2(n):
    for i in range(0, n + 1):
        yield 2 ** i

n = int(input())

print(*power2(n))