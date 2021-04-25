import requests
import json
import re
import pymysql
from datetime import datetime

ENTITY_TYPE = 'resblock'

class Room:
    def __init__(self, s, rent_type, community, house_type, longitude, latitude):
        self.rent_type = rent_type
        self.community = community
        self.house_type = house_type
        self.desc = s['desc']
        price = s['priceStr'].split('元')[0]
        self.price = price
        self.url = s['actionUrl']
        self.card_type = s['cardType']
        self.longitude = longitude
        self.latitude = latitude
        
    def store(self):
        conn = pymysql.connect(host="127.0.0.1", user="root", password="password", database="house-statistics")
        cursor = conn.cursor()

        sql = 'select * from house where url = \'{}\';'.format(self.url)
        cursor.execute(sql)
        data = cursor.fetchone()
        house_id = ''
        now = datetime.now()
        now_str = now.strftime('%Y-%m-%d %H:%M:%S')
        if data is not None:
            house_id = data[0]
        else:
            sql = 'insert into house(rent_type, community, longitude, latitude, `desc`, url, card_type, created_at, updated_at) values (\'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\', \'{}\');'.format(self.rent_type, self.community, self.longitude, self.latitude, self.desc, self.url, self.card_type, now_str, now_str)
            cursor.execute(sql)
            house_id = conn.insert_id()
            conn.commit()
        if not house_id == '':
            sql = 'insert into house_price_record(house_id, price, record_date, created_at) values(\'{}\', {}, \'{}\', \'{}\');'.format(house_id, self.price, now.strftime('%Y-%m-%d'), now_str)
            cursor.execute(sql)
            conn.commit()

        cursor.close()
        conn.close()

max_latitude = '39.994535001451'
min_latitude = '39.95779416509445'
max_longitude = '116.5240527070343'
min_longitude = '116.47284929296556'

city_id = '110000'
data_source = 'ZF'
cur_page = '1'
condition = ''
type = '30002'


def make_valid(data):
    return ''.join(re.split(r'<i.*/i>', data))

def save_price(community_info):
    url = "https://map.ke.com/proxyApi/i.c-pc-webapi.ke.com/map/houselist?cityId={}&dataSource={}&curPage={}&condition={}&type={}&resblockId={}&maxLatitude={}&minLatitude={}&maxLongitude={}&minLongitude={}".format(city_id, data_source, cur_page, condition, type, community_info[0], max_latitude, min_latitude, max_longitude, min_longitude)

    r = requests.get(url)
    if r.status_code == 200:
        resp = r.text.encode('utf-8').decode('unicode-escape')
        r_json = json.loads(make_valid(resp))
        list = r_json['data']['list']
        for l in list:
            title = l['title']
            r_c_h = title.split('·')
            r_type = r_c_h[0]
            c_h = r_c_h[1].split(' ')
            community = c_h[0]
            h_type = c_h[1]
            room = Room(l, r_type, community, h_type, community_info[1], community_info[2])
            room.store()
    else:
        print('Error request')


def get_communities():
    group_type = 'community'
    url =  'https://map.ke.com/proxyApi/i.c-pc-webapi.ke.com/map/bubblelist?cityId={}&dataSource={}&condition=&id=&groupType={}&maxLatitude={}&minLatitude={}&maxLongitude={}&minLongitude={}'.format(city_id, data_source, group_type, max_latitude, min_latitude, max_longitude, min_longitude)
    r = requests.get(url)
    if r.status_code == 200:
        resp = r.text.encode('utf-8').decode('unicode-escape')
        resp_json = json.loads(resp)
        community_list = [ [i['entityId'], i['longitude'], i['latitude']] for i in resp_json['data']['bubbleList'] if i['entityType'] == ENTITY_TYPE ]
        return community_list

def run():
    community_list = get_communities()
    for community in community_list:
        save_price(community)

if __name__ == '__main__':
    run()
