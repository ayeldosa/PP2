from datetime import datetime, timedelta
import re

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

dt1_str = input().strip()
dt2_str = input().strip()

date1, offset1 = parse_datetime(dt1_str)
date2, offset2 = parse_datetime(dt2_str)

utc1 = date1 - offset1
utc2 = date2 - offset2

diff_seconds = abs((utc2 - utc1).total_seconds())
diff_days = int(diff_seconds // 86400)

print(diff_days)