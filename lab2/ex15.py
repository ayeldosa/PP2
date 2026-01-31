n = int(input())      # сколько фамилий записано
unique = set()

for _ in range(n):
    surname = input().strip()
    unique.add(surname)

print(len(unique))
