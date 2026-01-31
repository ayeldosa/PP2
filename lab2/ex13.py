n = int(input())

if n <= 1:
    print("No")
else:
    is_prime = True
    for i in range(2, int(n**0.5) + 1):  # проверяем делители до √n
        if n % i == 0:
            is_prime = False
            break
    print("Yes" if is_prime else "No")
