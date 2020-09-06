# coding=utf-8
import os
import re
import time
import json
import random
import threading
import requests
from queue import Queue
UA_WEB_LIST = [
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5"
]
UA_AND_LIST = [
    "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 7.1.1_r58; zh-cn; MI 6 Build/XPGCG5c067mKE4bJT2oz99wP491yRmlkbGVY2pJ8kELwnF9lCktxB2baBUrl3zdK) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 MQQBrowser/9.9 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 7.1.1_r58; zh-cn; R7Plusm Build/hccRQFbhDEraf5B4M760xBeyYwaxH0NjeMsOymkoLnr31TcAhlqfd2Gl8XGdsknO) AppleWebKit/537.36 (KHTML, like Gecko)Version/4.0 MQQBrowser/9.9 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 9; BLA-AL00 Build/HUAWEIBLA-AL00; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/76.0.3809.89 Mobile Safari/537.36 T7/11.19 SP-engine/2.15.0 baiduboxapp/11.19.5.10 (Baidu; P1 9)",
    "Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; BLA-AL00 Build/HUAWEIBLA-AL00) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.132 MQQBrowser/8.9 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 7.1.2; zh-cn; Redmi 5 Plus Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/71.0.3578.141 Mobile Safari/537.36 XiaoMi/MiuiBrowser/11.7.34",
]
IP_LIST = [
{"ip": "222.85.28.130", "port": "52590", "type": "HTTP"},
{"ip": "223.199.27.86", "port": "9999", "type": "HTTP"},
{"ip": "36.248.132.198", "port": "9999", "type": "HTTP"},
{"ip": "113.195.168.32", "port": "9999", "type": "HTTP"},
{"ip": "175.42.123.196", "port": "9999", "type": "HTTP"},
{"ip": "119.108.165.153", "port": "9000", "type": "HTTP"},
{"ip": "175.42.158.224", "port": "9999", "type": "HTTP"},
{"ip": "180.118.128.55", "port": "9000", "type": "HTTP"},
{"ip": "125.108.114.170", "port": "9000", "type": "HTTP"}
]
USER_ITEM = {}
COOKIE = "_uuid=4CE7BD2F-D396-85FA-B0FD-5ABAE9AEB14005199infoc; buvid3=232B250D-5A2D-425A-93CD-0E079B9C438C53937infoc; CURRENT_FNVAL=16; rpdid=|(RYlkYm~R|0J'ulm|uluRkR; LIVE_BUVID=AUTO5715954174586716; sid=503f5cg3; DedeUserID=388356129; DedeUserID__ckMd5=b649abb4f114d81e; SESSDATA=222c0d91%2C1610969613%2C472ed*71; bili_jct=d8b4794212bcc8a1ab2d56b944eb195d; blackside_state=1; bsource=share_source_copy_link; PVID=2"
# 后台爬虫
class spider_bl():

    def __init__(self,start_url):
        self.q_urls = Queue()
        self.q_resps = Queue()
        self.q_items = Queue()
        self.q_video = Queue()
        self.items = {}
        self.file_playurl = {}
        self.pages = 0
        self.start_url = ''.join(start_url.split('\n')).strip()
        # 获取用户播放数，点赞数
        self.user_url1 = 'https://api.bilibili.com/x/space/upstat?mid={}&jsonp=jsonp'
        # 获取用户关注数，粉丝数
        self.user_url2 = 'https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp'
        # 获取用户头像，背景图，昵称，签名
        self.user_url3 = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'
        # 获取用户视频列表
        self.video_list_url = 'https://api.bilibili.com/x/space/arc/search?mid={0}&ps=30&pn={1}&jsonp=jsonp'
        # 视频播放页
        self.video_url = 'https://m.bilibili.com/video/{}'

    def get_resp(self):
        '''发送请求'''
        while True:
            url = self.q_urls.get()

            if '/video/' not in url and '/b23.tv/' not in url:
                headers = {"User-Agent": random.choice(UA_WEB_LIST)}
            else:
                headers = {"User-Agent": random.choice(UA_AND_LIST)}
            headers["cookie"] = COOKIE
            proxy = random.choice(IP_LIST)
            proxies = {'{}'.format(proxy['type']): '{0}:{1}'.format(proxy['ip'], proxy['port'])}
            try:
                response = requests.get(url, headers=headers,timeout=30,
                               proxies=proxies
                               )
                print('>>>>',response.status_code,url)
                response.raise_for_status()
                self.q_resps.put([url,response])
                self.q_urls.task_done()
            except Exception as e:
                print(e)
                self.q_urls.task_done()

    def parse(self):
        '''解析响应'''
        while True:
            task_ = self.q_resps.get()
            try:
                url,resp = task_[0],task_[1]
                if 'upstat?mid' in url:
                    '''获取用户播放数，点赞数'''
                    resp_json = json.loads(resp.text)
                    mid = url.split('mid=')[-1].split('&')[0]
                    item = self.items.get(mid)
                    if item ==None:
                        item = {}
                    item['UID'] = mid
                    item['播放'] = resp_json['data']['archive']['view']
                    item['点赞'] = resp_json['data']['likes']
                    self.items.update({mid:item})
                    self.q_resps.task_done()
                elif 'stat?vmid' in url:
                    '''获取用户关注数，粉丝数'''
                    resp_json = json.loads(resp.text)
                    mid = url.split('vmid=')[-1].split('&')[0]
                    item = self.items.get(mid)
                    if item == None:
                        item = {}
                    item['关注'] = resp_json['data']['following']
                    item['粉丝'] = resp_json['data']['follower']
                    self.items.update({mid:item})
                    self.q_resps.task_done()
                elif 'info?mid' in url:
                    '''获取用户头像，背景图，昵称，签名'''
                    resp_json = json.loads(resp.text)
                    mid = url.split('mid=')[-1].split('&')[0]
                    item = self.items.get(mid)
                    if item == None:
                        item = {}
                    item['作者'] = resp_json['data']['name']
                    item['签名'] = resp_json['data']['sign']
                    item['头像'] = resp_json['data']['face']
                    item['等级'] = resp_json['data']['level']
                    item['背景'] = resp_json['data']['top_photo']
                    self.items.update({mid: item})
                    self.q_resps.task_done()
                elif 'search?mid' in url:
                    '''循环获取video_list'''
                    resp_json = json.loads(resp.text)
                    mid = url.split('mid=')[-1].split('&ps')[0]
                    item = self.items.get(mid)
                    if item == None:
                        item = {}
                    video_count = resp_json['data']['page']['count']
                    item['作品'] = video_count
                    if 'pn=1' in url:
                        item['video_list'] = []
                        pages = int(video_count) // 30
                        # pages = 3
                        self.pages = int(pages) + 1
                        # 获取下一页内容
                        for i in range(pages):
                            page = i + 2
                            url_page = self.video_list_url.format(mid,page)
                            self.q_urls.put(url_page)
                    videos = resp_json['data']['list']['vlist']
                    video_list = []
                    for video in videos:
                        video_item = {}
                        bvid = video['bvid']
                        video_url = self.video_url.format(bvid)
                        self.q_urls.put(video_url)
                        video_item['VID'] = bvid
                        video_item['名称'] = video['title']
                        video_item['播放'] = video['play']
                        video_item['评论'] = video['comment']
                        video_item['弹幕'] = video['video_review']
                        video_item['封面'] = video['pic']
                        video_item['链接'] = video_url
                        video_list.append(video_item)
                    item['video_list'] = item['video_list'] + video_list
                    self.items.update({mid:item})
                    pn = url.split('pn=')[-1].split('&')[0]
                    if int(pn) == self.pages:
                        self.q_items.put(item)
                    self.q_resps.task_done()
                elif '/video/' in url or '/b23.tv/' in url:
                    '''获取视频下载地址'''
                    file_name = re.search("bvid: '(.*?)',",resp.text).group(1)
                    playUrl = re.search("readyVideoUrl: '(.*?)',",resp.text).group(1)
                    self.q_urls.put(playUrl)
                    self.file_playurl.update({playUrl: file_name})
                    if '/b23.tv/' in url:
                        viewinfo = re.search('"viewInfo":(.*?)}},"',resp.text).group(1) + '}}'
                        view_json = json.loads(viewinfo)
                        item = {}
                        item['VID'] = file_name
                        item['链接'] = playUrl
                        item['名称'] = view_json['title']
                        item['作者'] = view_json['owner']['name']
                        pic = view_json['pic']
                        item['封面'] = re.sub('\u002F','/',pic)
                        item['播放'] = view_json['stat']['view']
                        item['弹幕'] = view_json['stat']['danmaku']
                        item['评论'] = view_json['stat']['reply']
                        item['点赞'] = view_json['stat']['like']
                        item['投币'] = view_json['stat']['coin']
                        item['收藏'] = view_json['stat']['favorite']
                        item['分享'] = view_json['stat']['share']
                        self.q_items.put(item)
                    self.q_resps.task_done()
                elif '.mp4' in url:
                    '''下载视频'''
                    content = resp.content
                    file_name = self.file_playurl.get(url)
                    self.q_video.put([file_name, content])
                    self.q_resps.task_done()
                else:
                    self.q_resps.task_done()
            except:
                self.q_resps.task_done()

    def save_json(self):
        path1 = './json/'
        if not os.path.exists(path1):
            os.mkdir(path1)
        while True:
            item = self.q_items.get()
            try:
                with open(path1 + '{}.json'.format(item['作者']), 'w', encoding='utf-8') as f:
                    json.dump({'item': item}, f, indent=4, ensure_ascii=False)
                self.q_items.task_done()
            except Exception as e:
                print(e)
                self.q_items.task_done()

    def save_video(self):
        path1 = './video/'
        if not os.path.exists(path1):
            os.mkdir(path1)
        while True:
            name_video = self.q_video.get()
            name, video = name_video[0], name_video[1]
            try:
                with open(path1 + name + '.mp4', 'wb') as f:
                    f.write(video)
                self.q_video.task_done()
            except:
                self.q_video.task_done()

    def put_url(self):
        if 'space.bilibili.com' in self.start_url:
            mid = self.start_url.split('space.bilibili.com/')[-1].split('?')[0]
            mid = ''.join(mid.split('/')).strip()
            user_url1 = self.user_url1.format(mid)
            user_url2 = self.user_url2.format(mid)
            user_url3 = self.user_url3.format(mid)
            video_list_url = self.video_list_url.format(mid,1)
            self.q_urls.put(user_url1)
            self.q_urls.put(user_url2)
            self.q_urls.put(user_url3)
            self.q_urls.put(video_list_url)
        else:
            self.q_urls.put(self.start_url)

    def run(self):
        thread_list = []
        # print('1.放入起始url')
        t_url = threading.Thread(target=self.put_url)
        thread_list.append(t_url)
        # print('2.遍历，发送请求')
        for i in range(50):  # 三个线程发送请求
            t_parse = threading.Thread(target=self.get_resp)
            thread_list.append(t_parse)
        # print('3.解析响应')
        for i in range(10):
            t_parse = threading.Thread(target=self.parse)
            thread_list.append(t_parse)
        # print('4.保存数据')
        t_save = threading.Thread(target=self.save_json)
        thread_list.append(t_save)
        # print('5.保存视频')
        for _ in range(20):
            t_video = threading.Thread(target=self.save_video)
            thread_list.append(t_video)
        # print('6.启动线程')
        for t in thread_list:
            t.setDaemon(True)  # 把子线程设置为守护线程，当前这个线程不重要，主线程结束，子线程技术
            t.start()
        # print('7.等待队列为空')
        time.sleep(0.5)
        for q in [self.q_urls, self.q_resps,self.q_items,self.q_video]:
            q.join()  # 让主线程阻塞，等待队列的计数为0，
        # print("8.主线程结束")
        time.sleep(0.5)

if __name__ == '__main__':
    # start_url = 'https://b23.tv/w4JvmO'
    # start_url = 'https://m.bilibili.com/video/BV17p4y1D72i'
    start_url = 'https://space.bilibili.com/20977786/?spm_id_from=333.788.b_7265636f5f6c697374.6'
    # start_url = 'https://space.bilibili.com/34413182?spm_id_from=333.788.b_765f7570696e666f.2'
    spider_BL = spider_bl(start_url)
    spider_BL.run()


