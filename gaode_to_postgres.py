# coding=utf-8
import json
import requests
import time
import sys
import psycopg2  # pg 类库
import mylogger  # 日志文件

logger = mylogger.LogObject()

'''
说明：
本程序用于爬取高德poi数据，其基本流程如下：
（1）读取city.json，获得需要遍历的城市
（2）读取poicode.json，获取需要爬虫的数据类型
（3）通过高德的rest api，爬虫数据，并存到postgres数据库中，这里是分页爬取，每页20条数据，每次获取数据都会暂停1s
（4）若key超过了限制，则会自动切换到备用key，若所有的key都不能用了，则系统自动暂停3个小时
（5）翻页查询高德有最大页数限制，目前限制为100页，所以有的poi大于100页的，需要重新爬取，理想的方法是通过网格的方式爬取，但是本代码没有实现，只是将其记录在了日志文件中
'''


def get_data(page_index, url_amap):
    global total_record
    global amap_key_index
    global page_size
    time.sleep(1)  # 休眠1秒
    logger.info('---  GET POI START, CURRENT PAGE IS '+str(page_index)+' ---')
    url = url_amap.replace('page_index', str(page_index))
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False

    try:
        response = requests.get(url)
    except Exception as e:
        logger.error('--- Request was refuesed ! wait 2 minutes... ...')
        time.sleep(120)
        getPOIdata(page_size, url_amap)  # 重新执行方法
        return

    poi_json = response.json()

    # 判断key是否可用，如果不可用，则重新获取key
    amap_info = poi_json.get('info')  # 返回的信息
    if (amap_info == 'DAILY_QUERY_OVER_LIMIT' or amap_info == 'INVALID_USER_KEY'):

        # 这个地方有点问题，每次遍历不同的城市的时候，key会从0开始
        if(url.find(amap_keys[0]['key']) > 0 and amap_key_index > 1):
            old_key = amap_keys[0]['key']
            amap_key_index -= 1
        else:
            old_key = amap_keys[amap_key_index]['key']

        amap_key_index += 1

        if amap_key_index > 9:
            logger.info(
                '--- No key available , we will retry after 3 hours... ...')
            amap_key_index = 0
            time.sleep(10800)  # 睡眠3个小时

        curr_key = amap_keys[amap_key_index]['key']
        logger.info('--- Old Key : '+old_key+' ; Current Key : '+curr_key +
                    '; Current Key Index : '+str(amap_key_index))
        curr_url = url_amap.replace(old_key, curr_key)
        logger.info('--- The Curent Url is : ' + curr_url + ' ---')
        getPOIdata(page_size, curr_url)  # 重新获取数据
        return

    if total_record == 0:
        total_record = int(poi_json.get('count', 0))
        if total_record > 2500:
            logger.critical(
                'the number of POIs is more than 2500, the url is :'+url)

    poi_lists = poi_json.get("pois")
    if poi_lists != None or '':
        for poi in poi_lists:

            try:
                cursor = connector.cursor()
                sql = "insert into TABLE_NAME(id,name,type,address,tel,location,pcode,pname,citycode,cityname,adcode,adname) " \
                      "VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"
                logger.info(sql)
                data = (''.join(poi.get('id')),
                        ''.join(poi.get('name')),
                        ''.join(poi.get('type')),
                        ''.join(poi.get('address')),
                        ''.join(poi.get('tel')),
                        ''.join(poi.get('location')),
                        ''.join(poi.get('pcode')),
                        ''.join(poi.get('pname')),
                        ''.join(poi.get('citycode')),
                        ''.join(poi.get('cityname')),
                        ''.join(poi.get('adcode')),
                        ''.join(poi.get('adname')))

                cursor.execute(sql % data)
                connector.commit()
            except Exception as e:
                connector.rollback()  # 出现错误后回滚
                logger.error('--- INSERT ERROR, THE DETAIL AS BELOW: ')
                logger.error(str(e))
    else:
        pass
    return poi_json.get("pois")


def getPOIdata(page_size, url_amap):
    global total_record

    logger.critical('--- THE CURRENT URL IS : ' + url_amap + ' ---')

    try:
        json_data = get_data(1, url_amap)
        if (total_record / page_size) != 0:
            page_number = int(total_record / page_size) + 2
        else:
            page_number = int(total_record / page_size) + 1

        logger.critical('--- CURRENT PAGE NUMBER IS : ' +
                        str(page_number)+' ---')

        for each_page in range(2, page_number):
            get_data(each_page, url_amap)
    except Exception as e:
        logger.error('--- GET POI DATA FUNCTION ERROR , DETAIL AS BELOW: ---')
        logger.error(str(e))
        time.sleep(60)
        getPOIdata(page_size, url_amap)


def pg_connector():
    connector = psycopg2.connect(database="postgres", user="postgres",
                                 password="postgres", host="xxx.xxx.xxx.xxx", port="5432")

    return connector


if __name__ == '__main__':
    global connector  # pg连接
    global amap_keys  # 高德地图的keys
    global amap_key_index  # 当前key的下标，默认为0，是第一个key
    global page_size
    global current_amp_key  # 当前的key
    amap_key_index = 0

    connector = pg_connector()
    city = []
    data = open("city.json", encoding="utf-8-sig")
    strJson = json.load(data)

    poiCodeData = open('poicode.json', encoding="utf-8-sig")  # poi 的类型
    poiCodeJson = json.load(poiCodeData)

    keysData = open("amap_keys.json", encoding="utf-8-sig")
    amap_keys = json.load(keysData)  # 获取所有备用的key
    logger.critical('--- ALL AMAP KEYS:'+json.dumps(amap_keys))  # 输出所有的keys

    for i in range(len(strJson)):
        city.append(strJson[i]['adcode'])
    logger.critical('--- TRAVERSAL CITIES: '+','.join(city))

    for y in range(0, len(city)):
        for j in range(len(poiCodeJson)):
            url_amap = 'http://restapi.amap.com/v3/place/text?key='+amap_keys[amap_key_index]['key']+'&types='+poiCodeJson[j]['type'] + \
                '&city=' + \
                city[y] + '&citylimit=true&children=1&offset=25&page=page_index&extensions=all'
            logger.info('--- CURRENT URL ---')
            logger.info(url_amap)
            page_size = 25
            page_index = r'page=1'
            global total_record
            total_record = 0
            getPOIdata(page_size, url_amap)

    logger.info("--- all data has stored, my lord ! ---")
    sys.exit()  # 退出程序
