# encoding:utf-8

from bs4 import BeautifulSoup
import requests
import json
import sys
import urllib.parse as parse
import threading
import re
import time
import os


def download_html(name, response):
    with open('./'+name+'.html', 'wb') as f:
        f.write(response.content)



class Counter(object):
    size = 0
    total = 0


def downloads(url, filename, headers, start, end=0):
    session = requests.session()
    if end is 0:
        headers['Range'] = 'bytes={}-'.format(start)
    else:
        headers['Range'] = 'bytes={}-{}'.format(start, end)

    r = session.get(url, headers=headers, stream=True)
    if r.ok:
        with open(filename, 'rb+') as file:
            file.seek(start)
            for data in r.iter_content(chunk_size=102400 * 4):
                file.write(data)
                Counter.size += len(data)
                file.flush()
                sys.stdout.write('%s : [下载进度] : %.2f%%' % (
                    filename, float(Counter.size / Counter.total * 100)) + '\r')
                sys.stdout.flush()
                if Counter.size / Counter.total == 1:
                    print('\n')
    else:
        print(r.ok)
        print(str(r.status_code)+' error')


def video_downloader(session, url, filename, thread_number=20, headers=[], hread_range='Range'):
    head_rep = session.head(url)
    video_length = int(head_rep.headers['Content-Length'])
    Counter.total = video_length
    ran = video_length//thread_number
    range_list = [0]
    for i in range(1, thread_number):
        range_list.append(ran*i+1)

    # create file
    with open(filename, 'wb') as f:
        f.write(os.urandom(video_length))

    threads = []
    for i in range(thread_number-1):
        th = th = threading.Thread(target=downloads, name=i+1, args=(
            url, filename, headers, range_list[i], range_list[i+1]-2))
        th.setDaemon(True)
        threads.append(th)
    th = threading.Thread(target=downloads, name=thread_number, args=(
        url, filename, headers, range_list[-1]))
    th.setDaemon(True)
    threads.append(th)
    for t in threads:
        t.start()
        time.sleep(2)
    time.sleep(2)
    for t in threads:
        t.join()


def default_video(url, session, headers=[]):
    a = ['&q=1080p', '&q=720p', '&q=480p']
    for i in range(len(a)):
        w = a[i]
        r = session.get(url+w, headers=headers)
        print(url+w)
        if r.ok:
            soup = BeautifulSoup(r.text, 'lxml')
            infos = soup.find_all('source')
            if len(infos) == 0:
                continue
            info = infos[0]
            data = {}
            data['file'] = info.get('src')
            data['type'] = info.get('type').split('/')[-1]
            data['label'] = info.get('data-res')
            return data


def api_video(iframe_url, session, headers=[]):
    video_api = 'https://www.fembed.com/api/sources/{}'.format('&p=1080p')
    data_info = session.post(video_api, headers=headers)
    data = json.loads(data_info.content)
    if data['success'] == False:
        return None
    return data['data'][0]


def downloader(url, headers=[]):
    session = requests.session()
    host = parse.urlparse(url).netloc
    headers['Referer'] = host
    html_r = session.get(url, headers=headers)
    if html_r.ok:
        soup = BeautifulSoup(html_r.text, 'lxml')
        iframe = soup.find(
            'iframe', src=re.compile('^https://www.rapidvideo.com/e/'))
        name = soup.title.string
        name = re.sub('[ |-|!]', '_', name)

        if iframe is None:
            return "error"

        iframe_url = iframe.get('src')
        video_data = default_video(iframe_url, session, headers=headers)
        # if video_data is None:
        #     print('download default')
        #     if len(iframe_list) < 6:
        #         print('no video')
        #         return
        #     video_data = default_video(
        #         iframe_list[5].get('src'), session, headers=headers)

        print('[name] : {} \n[video_url] : {} \n[video_type] : {} \n[video_lable] : {}'.format(
            name, video_data['file'], video_data['type'], video_data['label']))
        print('begin download')
        name = '{}.{}'.format(name, video_data['type'])
        video_downloader(
            session, video_data['file'], 'G://'+name, thread_number=20, headers=headers)
        print('\n')


def main():
    headers = {'Referer': 'https://www.bilibili.com',
               'Accept': '*/*',
               'Accept-Language': 'zh-CN,zh;q=0.9',
               'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36'}

    url = input()
    downloader(url, headers=headers)

# https://javkimochiii.com/ssni-329-%E5%BD%BC%E5%A5%B3%E3%81%AE%E7%BE%8E%E4%BA%BA%E3%81%8A%E5%A7%89%E3%81%95%E3%82%93%E3%81%8C%E5%85%A8%E5%8A%9B%E3%81%A7%E6%AC%B2%E6%B1%82%E4%B8%8D%E6%BA%80%E3%82%A2%E3%83%94%E3%83%BC%E3%83%AB/

if __name__ == '__main__':
    main()
