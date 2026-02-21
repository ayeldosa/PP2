from datetime import datetime, timedelta
import re
import math

def parse_datetime(s):
    date_part, tz_part = s.split(' UTC')
    date = datetime.strptime(date_part, '%Y-%m-%d')
    
    match = re.match(r'([+-])(\d{2}):(\d{2})', tz_part)
    sign = match.group(1)
    hours = int(match.group(2))
    minutes = int(match.group(3))
    
    offset = timedelta(hours=hours, minutes=minutes)
    if sign == '-':
        offset = -offset
    
    return date, offset

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def next_birthday(birth_date, birth_offset, current_date, current_offset):
    # Переводим текущий момент в UTC
    current_utc = current_date - current_offset
    
    # Берем месяц и день из рождения
    month = birth_date.month
    day = birth_date.day
    
    # Начинаем с текущего года
    year = current_date.year
    
    while True:
        try:
            if month == 2 and day == 29 and not is_leap_year(year):
                birthday_local = datetime(year, 2, 28)
            else:
                birthday_local = datetime(year, month, day)
        except ValueError:
            year += 1
            continue
        
        # Переводим день рождения в UTC (полночь по местному времени дня рождения)
        birthday_utc = birthday_local - birth_offset
        
        # Если день рождения >= текущего момента в UTC
        if birthday_utc >= current_utc:
            diff_seconds = (birthday_utc - current_utc).total_seconds()
            # Используем ceil для округления вверх
            return math.ceil(diff_seconds / 86400)
        
        year += 1

# Читаем входные данные
birth_str = input().strip()
current_str = input().strip()

# Парсим
birth_date, birth_offset = parse_datetime(birth_str)
current_date, current_offset = parse_datetime(current_str)

# Вычисляем
days_left = next_birthday(birth_date, birth_offset, current_date, current_offset)
print(days_left)