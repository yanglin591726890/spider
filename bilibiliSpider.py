# encoding:utf-8

import requests
import json
import re
import sys
import time
session = requests.session()

url = input()
# 下载地址的镜像格式部分的可能替换值
video_mode = ['mirrorcos.', 'mirrorkodo.',
              'mirrorks3.', 'mirrorbos.', 'mirrorks3u.', ]

headers = {'Referer': 'https://www.bilibili.com',
           'Accept': '*/*',
           'Accept-Encoding': 'gzip, deflate, br',
           'Accept-Language': 'zh-CN,zh;q=0.9',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}
url = url.split("?")[0]
response = session.get(url, headers=headers, verify=False)
'''
verify=False 表示不验证，如果不设置，会出现454错误
 stream=True, 表示以流的方式接受数据，如果不设置，那么会直接下载到内存，当数据过大时，内存不够
 使用这个之后，
 通过content_size = int(response.headers['content-length'])得到数据总长度，
 然后用循环
 for data in response.iter_content(chunk_size=102400 * 4)
 每次取指定数据然后写到磁盘
'''


def sub(s):
    patn_1 = re.compile(r'\?')
    patn_2 = re.compile(r'\/')
    patn_3 = re.compile(r'\\')
    patn_4 = re.compile(r'\|')
    patn_5 = re.compile(r'\:')
    patn_6 = re.compile(r'\<')
    patn_7 = re.compile(r'\>')
    patn_8 = re.compile(r'\*')
    patn_9 = re.compile(r'\:')

    s = re.sub(patn_1, "", s)
    s = re.sub(patn_2, "", s)
    s = re.sub(patn_3, "", s)
    s = re.sub(patn_4, "", s)
    s = re.sub(patn_5, "", s)
    s = re.sub(patn_6, "", s)
    s = re.sub(patn_7, "", s)
    s = re.sub(patn_8, "", s)
    s = re.sub(patn_9, "", s)
    return s

if response.ok:
    html = response.text
    page_info = re.search(r'__INITIAL_STATE__=(.*?);\(function\(\)', html)
    p = re.search(r'window\.__playinfo__=(.*?)</script>', html)
    if page_info is not None:
        pages = json.loads(page_info.group(1))
        playinof = json.loads(p.group(1))

        play_url = [url['url'] for url in playinof['durl']]
        title = sub(pages['videoData']['title'])

        for vurl in play_url:
            #vurl = vurl.replace('mirrorkodo', 'mirrorcos')
            response = session.get(
                vurl, headers=headers, stream=True, verify=False)
            size = 0
            if response.status_code == 200:
                types = vurl.split('?')[0].split('.')[-1]
                name = title+'.'+types
                content_size = int(
                    response.headers['content-length'])
                with open('D://'+name, 'wb') as file:
                    for data in response.iter_content(chunk_size=102400 * 4):
                        file.write(data)
                        size += len(data)
                        file.flush()
                        sys.stdout.write('第%s个片段：[下载进度]:%.2f%%' % (
                            name, float(size / content_size * 100)) + '\r')
                        sys.stdout.flush()
                        if size / content_size == 1:
                            print('\n')
            else:
                print(response.status_code)
