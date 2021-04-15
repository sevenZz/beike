import requests
import json
import re

class Room:
    def __init__(self, s, rent_type, community, house_type):
        self.rent_type = rent_type
        self.community = community
        self.house_type = house_type
        self.desc = s['desc']
        self.price = s['priceStr']
        self.url = s['actionUrl']
        self.card_type = s['cardType']

max_latitude = '39.994535001451'
min_latitude = '39.95779416509445'
max_longitude = '116.5240527070343'
min_longitude = '116.47284929296556'

city_id = '110000'
data_source = 'ZF'
cur_page = '1'
condition = ''
type = '30002'
resblock_id = '1111027373915'

url = "https://map.ke.com/proxyApi/i.c-pc-webapi.ke.com/map/houselist?cityId={}&dataSource={}&curPage={}&condition={}&type={}&resblockId={}&maxLatitude={}&minLatitude={}&maxLongitude={}&minLongitude={}".format(city_id, data_source, cur_page, condition, type, resblock_id, max_latitude, min_latitude, max_longitude, min_longitude)

print(url)
def make_valid(data):
    return ''.join(re.split(r'<i.*/i>', data))


r = requests.get(url)
if r.status_code == 200:
    resp = r.text.encode('utf-8').decode('unicode-escape')
    r_json = json.loads(make_valid(resp))
    list = r_json['data']['list']
    print(r_json['data']['list'])
    for l in list:
        title = l['title']
        r_c_h = title.split('·')
        r_type = r_c_h[0]
        c_h = r_c_h[1].split(' ')
        community = c_h[0]
        h_type = c_h[1]
        if r_type == '整租':
            r = Room(l, r_type, community, h_type)
            print(r)

else:
    print('Error request')
