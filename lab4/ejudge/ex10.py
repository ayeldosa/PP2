def limited_cycle(lst, n):
    for _ in range(n):
        yield from lst  

items = input().split()
n = int(input())

print(*limited_cycle(items, n))