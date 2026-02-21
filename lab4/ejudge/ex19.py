import math

R = float(input())
x1, y1 = map(float, input().split())
x2, y2 = map(float, input().split())

def dist(x1, y1, x2, y2):
    return math.hypot(x1 - x2, y1 - y2)

# Проверяем, пересекает ли отрезок AB окружность
dx, dy = x2 - x1, y2 - y1
a = dx*dx + dy*dy
if a == 0:
    print(f"{dist(x1, y1, x2, y2):.10f}")
    exit()

b = 2*(x1*dx + y1*dy)
c = x1*x1 + y1*y1 - R*R

disc = b*b - 4*a*c

# Если дискриминант < 0, отрезок не пересекает окружность
if disc <= 1e-12:
    print(f"{dist(x1, y1, x2, y2):.10f}")
    exit()

t1 = (-b - math.sqrt(disc)) / (2*a)
t2 = (-b + math.sqrt(disc)) / (2*a)

# Если пересечения вне отрезка [0,1], то отрезок не пересекает окружность
if (t1 < 0 and t2 < 0) or (t1 > 1 and t2 > 1):
    print(f"{dist(x1, y1, x2, y2):.10f}")
    exit()

# Иначе нужно идти по касательным и дуге
d1 = math.hypot(x1, y1)
d2 = math.hypot(x2, y2)

angle1 = math.atan2(y1, x1)
angle2 = math.atan2(y2, x2)

# Угол между точками
delta = abs(angle2 - angle1)
if delta > math.pi:
    delta = 2*math.pi - delta

# Углы касательных
alpha1 = math.acos(R / d1)
alpha2 = math.acos(R / d2)

# Выбираем меньший путь
path1 = math.sqrt(d1*d1 - R*R) + math.sqrt(d2*d2 - R*R) + R * abs(delta - alpha1 - alpha2)
path2 = math.sqrt(d1*d1 - R*R) + math.sqrt(d2*d2 - R*R) + R * (2*math.pi - abs(delta - alpha1 - alpha2))

print(f"{min(path1, path2):.10f}")