n = int(input())
arr = list(map(int, input().split()))

freq = {} 
for x in arr:
    freq[x] = freq.get(x, 0) + 1

max_count = max(freq.values())
most_frequent = min(k for k, v in freq.items() if v == max_count)

print(most_frequent)
