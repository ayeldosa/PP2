from datetime import datetime, timedelta
import re

def parse_datetime(s):
    # Пример: 2026-01-01 00:00:00 UTC+03:00
    datetime_part, tz_part = s.split(' UTC')
    dt = datetime.strptime(datetime_part, '%Y-%m-%d %H:%M:%S')
    
    match = re.match(r'([+-])(\d{2}):(\d{2})', tz_part)
    sign = match.group(1)
    hours = int(match.group(2))
    minutes = int(match.group(3))
    
    offset = timedelta(hours=hours, minutes=minutes)
    if sign == '-':
        offset = -offset
    
    return dt, offset

# Читаем входные данные
start_str = input().strip()
end_str = input().strip()

# Парсим
start_dt, start_offset = parse_datetime(start_str)
end_dt, end_offset = parse_datetime(end_str)

# Переводим в UTC
start_utc = start_dt - start_offset
end_utc = end_dt - end_offset

# Разница в секундах
duration = int((end_utc - start_utc).total_seconds())

print(duration)