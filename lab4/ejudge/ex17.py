import math

# Читаем входные данные
R = float(input().strip())
x1, y1 = map(float, input().strip().split())
x2, y2 = map(float, input().strip().split())

# Вектор направления
dx = x2 - x1
dy = y2 - y1
dx2 = dx * dx
dy2 = dy * dy
segment_length_sq = dx2 + dy2

# Если точка A и B совпадают
if segment_length_sq == 0:
    # Проверяем, лежит ли точка внутри круга
    if x1*x1 + y1*y1 <= R*R:
        print("0.0000000000")
    else:
        print("0.0000000000")
    exit()

# Параметрическое уравнение: P(t) = A + t*(B-A), t from 0 to 1
# Найдем t, где |P(t)|^2 = R^2
# |A + t*V|^2 = R^2
# (V·V) t^2 + 2 (A·V) t + (A·A - R^2) = 0

a = segment_length_sq
b = 2 * (x1*dx + y1*dy)
c = x1*x1 + y1*y1 - R*R

discriminant = b*b - 4*a*c

# Если дискриминант отрицательный, нет пересечений
if discriminant <= 0:
    # Проверяем, лежит ли весь отрезок внутри круга
    # Для этого проверим расстояние от центра до отрезка
    # Если весь отрезок внутри, то длина = длина отрезка
    # Иначе 0
    
    # Найдем ближайшую точку на отрезке к центру
    t = -b / (2*a) if a != 0 else 0
    t = max(0, min(1, t))
    
    closest_x = x1 + t * dx
    closest_y = y1 + t * dy
    dist_to_center_sq = closest_x*closest_x + closest_y*closest_y
    
    if dist_to_center_sq <= R*R:
        # Весь отрезок внутри
        print(f"{math.sqrt(segment_length_sq):.10f}")
    else:
        # Нет пересечений
        print("0.0000000000")
    exit()

# Находим корни квадратного уравнения
sqrt_disc = math.sqrt(discriminant)
t1 = (-b - sqrt_disc) / (2*a)
t2 = (-b + sqrt_disc) / (2*a)

# Сортируем корни
t_min = min(t1, t2)
t_max = max(t1, t2)

# Находим пересечение с отрезком [0, 1]
intersection_start = max(0, t_min)
intersection_end = min(1, t_max)

# Если пересечение непусто
if intersection_end > intersection_start:
    # Длина пересечения = длина отрезка * доля пересечения
    intersection_length = math.sqrt(segment_length_sq) * (intersection_end - intersection_start)
    print(f"{intersection_length:.10f}")
else:
    print("0.0000000000")