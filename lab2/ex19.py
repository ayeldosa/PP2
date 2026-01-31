n = int(input())

episodes = {}

for _ in range(n):
    name, count = input().split()
    count = int(count)

    if name not in episodes:
        episodes[name] = 0
    episodes[name] += count

for name in sorted(episodes.keys()):
    print(name, episodes[name])
