# gaode_pois_scraping
Scraping AMap(GaoDe) POIs which through the rest api based on Python
# python3 爬虫高德POI数据到Postgis中
## 基本说明
本代码是基于python3来实现的，利用高德的poi搜索接口进行爬虫。</br>
高德poi接口分为四类：</br>
（1）关键字搜索：主要是根据关键字对poi进行搜索（本代码中使用）；缺点是翻页数限制，可能导致有些poi爬取不全</br>
（2）周边搜索：输入指定位置和半径</br>
（3）多边形搜索：根据输入的多边形进行搜索，可以将待爬取区域划分成网格来遍历；根据此方法，如果合理划分网格的话，可以爬取全量的poi数据，但是网格划分的太细会大大增加系统负担，网格划分太粗又会导致数据爬取不全，如果能做到自适应的划分是最好的（希望有大牛能指导一下）</br>
（4）ID搜索：根据id来搜索，这个的好处是，如果知道高德ID的生成规律的话，直接通过id，即可爬取全量的数据，缺点是ID是36进制的，遍历一遍小系统做不到。</br>
参考：https://lbs.amap.com/api/webservice/guide/api/search/#introduce
## 爬虫思路
本代码只是实现了一个简单的爬虫，供爱好者参考使用，爬虫的基本思路是：</br>
（1）读取city.json，获得需要遍历的城市</br>
（2）读取poicode.json，获取需要爬虫的数据类型</br>
（3）通过高德关键字搜索poi的rest api，爬虫数据，并存到postgres数据库中，这里是分页爬取，每页25条数据，每次获取数据都会暂停1s</br>
（4）若key超过了限制，则会自动切换到备用key，若所有的key都不能用了，则系统自动暂停3个小时</br>
（5）翻页查询高德有最大页数限制，目前限制为100页，所以有的poi大于100页的，需要重新爬取，理想的方法是通过网格的方式爬取，但是本代码没有实现，只是将其记录在了日志文件中</br>
## 待解决的问题
（1）未结合使用网格爬虫</br>
（2）日志没有分片存储</br>
（3）没有做爬虫监控</br>
## 使用说明
### 目录说明
- gaode_to_postgres.py --主要爬虫代码
- mylogging.py --日志记录文件
- city.json --全国城市信息（来自高德）
- poicode.json --poi的分类（来自高德）
- amap_keys.json --高德申请的秘钥
### 程序运行（环境：CentOS7+Python3.7）
- 将程序上传至服务器，并安装好Pyhon3.7以及psycopg、requests等类库，运行如下脚本：
```
cd gaode_poi #程序所在目录
nohup python3 gaode_to_postgres.py >logs/log.log 2>&1 &
```
程序会自动在当前目录的logs下面生成日志文件
# 特别说明
本代码主要参考了：</br>
https://github.com/kenneth663/gaode_spider
https://www.cnblogs.com/watchslowly/p/9081423.html
- 如有侵权，纯属无意，请联系我删除
