from PIL import Image
import os
import datetime
from django.conf import settings
import hashlib
import calendar
import random
import math
import time
from typing import Dict


def save_image(file):
    try:
        img = Image.open(file)
    except Exception:
        raise

    if file.name.endswith('png'):
        format = 'png'
    else:
        format = 'jpeg'
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    pre_w = 960.0
    if w > pre_w:
        size = (int(pre_w), int(h * (pre_w / w)))
        img.thumbnail(size)

    images_path = os.path.join("images", datetime.datetime.now().strftime("%Y%m%d"))
    dir = os.path.join(settings.MEDIA_ROOT, images_path)
    if not os.path.exists(dir):
        os.makedirs(dir)

    name = "%s.%s" % (hashlib.md5(img.tobytes()).hexdigest(), format)
    dest = os.path.join(dir, name)
    img.save(dest, format)
    return images_path, name


def gen_invite_code(user_id: int) -> str:
    s = "A9C8EF7HIJ6LMN5Q3STUV2XYZ1WR4PKGDB"

    seed = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    i = 0

    array = [0, 0, 0, 0]

    #  生成4位id映射
    pk = user_id

    while pk > 0:
        a = pk % 34
        array[i] = a
        i += 1

        pk = pk // 34

    result = []

    for i in range(len(array) - 1, -1, -1):
        result.append(s[array[i]])

    #  头尾添加随机数
    head = random.choice(seed)
    tail = random.choice(seed)

    result.insert(0, head)
    result.append(tail)
    invite_code = "".join(result)
    return invite_code

def decode_invite_code(code: str) -> int:
    code_list = []
    s = "A9C8EF7HIJ6LMN5Q3STUV2XYZ1WR4PKGDB"

    for i in range(1, len(code) - 1):
        code_list.append(code[i])

    rate = 0
    pk = 0

    while len(code_list) > 0:
        mark = code_list.pop()
        pk = pk + s.index(mark) * (34 ** rate)
        rate += 1
    return pk


class GeoDistance(object):

    def __init__(self):
        self.EARTH_RADIUS = 6378137

    def get_scope(self, lat: float, lng: float, distance: float = 5000) -> Dict[str, float]:
        dlng = 2 * math.asin(math.sin(distance / (2 * self.EARTH_RADIUS)) / math.cos(math.radians(lat)))
        dlng = math.degrees(dlng)

        dlat = distance / self.EARTH_RADIUS
        dlat = math.degrees(dlat)

        min_lat = lat - dlat
        max_lat = lat + dlat
        min_lng = lng - dlng
        max_lng = lng + dlng
        return {"min_lat": min_lat, "max_lat": max_lat, "min_lng": min_lng, "max_lng": max_lng}

    def get_distance(self, lng1: float, lat1: float, lng2: float, lat2: float) -> float:
        radians_lat1 = math.radians(lat1)
        radians_lat2 = math.radians(lat2)
        a = radians_lat1 - radians_lat2
        b = math.radians(lng1) - math.radians(lng2)
        s = 2 * math.asin(math.sqrt(math.pow(math.sin(a / 2), 2) + math.cos(radians_lat1) * math.cos(radians_lat2)
                                    * math.pow(math.sin(b / 2), 2)))

        s = round(s * self.EARTH_RADIUS / 1000, 2)
        return s

def get_days_of_month(year,mon):
    '''''
    get days of month
    '''
    return calendar.monthrange(int(year), int(mon))[1]

def addzero(n):
    '''''
    add 0 before 0-9
    return 01-09
    '''
    nabs = abs(int(n))
    if(nabs<10):
        return "0" + str(nabs)
    else:
        return nabs 

def getyearandmonth(dt, n=0):
    '''''
    get the year,month,days from today
    befor or after n months
    '''
    thisyear = int(dt.year)
    thismon = int(dt.month)
    totalmon = thismon+n
    if(n>=0):
        if(totalmon<=12):
            if dt.day > get_days_of_month(thisyear,totalmon):
                days = str(get_days_of_month(thisyear,totalmon))
            else:
                days = str(dt.day)
            totalmon = addzero(totalmon)
            return (thisyear,totalmon,days)
        else:
            i = totalmon/12
            j = totalmon%12
            if(j==0):
                i-=1
                j=12
            thisyear += i
            if dt.day > get_days_of_month(thisyear,j):
                days = str(get_days_of_month(thisyear,j))
            else:
                days = str(dt.day)

            j = addzero(j)
            return (str(thisyear),str(j),days)
    else:
        if((totalmon>0) and (totalmon<12)):
            if dt.day > get_days_of_month(thisyear,totalmon):
                days = str(get_days_of_month(thisyear,totalmon))
            else:
                days = str(dt.day)
            totalmon = addzero(totalmon)
            return (year,totalmon,days)
        else:
            i = totalmon/12
            j = totalmon%12
            if(j==0):
                i-=1
                j=12
            thisyear +=i
            if dt.day > get_days_of_month(thisyear,j):
                days = str(get_days_of_month(thisyear,j))
            else:
                days = str(dt.day)
            j = addzero(j)
            return (str(thisyear),str(j),days) 

def change_month_to_year(month):
    year = month // 12
    rest_month = month % 12

    if year == 0:
        return "%d月" % rest_month
    if rest_month == 0:
        return "%d年" % year
    
    return "%d年%d月" % (year, rest_month)