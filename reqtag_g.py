# -*- coding:utf-8 -*-
import time
import pickle
import os
import multiprocessing
import grequests
from bs4 import BeautifulSoup
import demjson
from html import unescape
import sys
import random
import gc#别拆函数了，联系太密根本拆不开
psnum=6   #15 15 1000 6m-600k  13 15 150 3m 现在是12
path='/content/onedrive/p1'#r'C:\0\pixiv2022\p'
urls_num=20
group_num=1000
loop_num=10
params = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/76.0.3809.132 Safari/537.36',
    'authority': 'www.pixiv.net',
    'content-type': 'application/x-www-form-urlencoded',
    'accept-language': 'zh-CN;q=0.9,zh;q=0.8,zh-TW;q=0.7,en-US,en;q=0.6,ja;q=0.6',
    'dnt': '1',
    'referer': 'https://www.pixiv.net/'
}
task={}
    
for nu in range(psnum):#任务组初始化
    task[nu]=[]
os_listdir_path=os.listdir(path)
random.shuffle(os_listdir_path)
for index, value in enumerate(os_listdir_path):#任务组分配
    if value.find('TO')!=-1:
        task[index%psnum].append(value)
    
import requests

def run(n):
    temp=task[n]#任务组v
    time.sleep(n*3)
    random.shuffle(temp)
    for pta in temp: #序号组分配'1300000TO1400000'
        #pta='87000000TO87001000'#'0TO10000'
        if os.path.exists(path+'/'+pta+'/'+'tag.pickle'):
            continue
        print(pta,'start')
        start=int(pta[:pta.find('TO')])#'1300000'
        end=int(pta[pta.find('TO')+2:])#'1400000' 
        tag={}
        tag['pics']={}
        tag['trans']={}
        tag['error']={}
        tag['error']['404_not_found']=[]
        tag['error']['sp']=[]
        tag['error']['except']=[]
        all_pid=list(range(start,end))
        pic_task=[]
        for schedule in range(loop_num):
            s=requests.session()
            now_task=[ all_pid[i:i+group_num] for i in range(0,len(all_pid),group_num) ]
            if len(all_pid)!=0:
                print(pta+'   error retry  '+str(schedule)+' '+ str(len(all_pid)))  
            for now_group in now_task:
                if schedule%2==0 or schedule==1:
                    rs_group = [grequests.get('https://www.pixiv.net/artworks/'+str(id0), headers=params, session=s) for id0 in now_group]
                else:
                    rs_group = [grequests.get('https://www.pixiv.net/artworks/'+str(id0), headers=params) for id0 in now_group ]

                all_req=grequests.map( rs_group , size=urls_num )
                #print(all_req )
                for req in all_req:#序号组
                    if req==None:
                        continue
                    reqstatuscode=int(req.status_code)
                    url_now=req.url
                    url_pid_now=int(url_now[url_now.rfind('/')+1:])
                    new_soup = BeautifulSoup(req.text,'html.parser')
                    if reqstatuscode==404 and (new_soup.find(class_="_unit error-unit").find(class_="error-message").contents[0]=='该作品已被删除，或作品ID不存在。'):
                        tag['error']['404_not_found'].append(url_pid_now)
                        all_pid.remove(url_pid_now)
                        continue
                    if reqstatuscode !=200 and schedule==loop_num-1:
                        if reqstatuscode not in tag['error']:
                            tag['error'][reqstatuscode]=[]
                        tag['error'][reqstatuscode].append(url_now)
                        continue

                    try:
                        if new_soup.find_all(class_="_unit error-unit")==[]:
                            json_data_0 = new_soup.find(name='meta',attrs={'name':'preload-data'})
                            if json_data_0==None:
                                continue
                            else:
                                json_data =json_data_0.attrs['content']
                            format_json_data = demjson.decode(json_data)
                            pre_catch_id = list(format_json_data['illust'].keys())[0]
                            illust_info = format_json_data['illust'][pre_catch_id]
                            id00=int(illust_info['illustId'])
                            if (id00 not in tag['pics']) and (illust_info['urls']['original']!=[]):
                                tag['pics'][id00] = {}#restrict=0所有人 1仅限好P友 2不公开   xRestrict'0全年龄 1 R-18 2 R-18G
                                tag['pics'][id00]['ti'] = illust_info['illustTitle']#tag[id0]['co'] = illust_info['illustComment']#title下面小字
                                tag['pics'][id00]['cm'] = unescape(illust_info['illustComment'])[:500]
                                tag['pics'][id00]['da'] = illust_info['createDate']#haiyou uploadDate
                                tag['pics'][id00]['ty'] = illust_info['illustType']#少图0 多图1 动图2
                                tag['pics'][id00]['re']=illust_info['restrict']#
                                tag['pics'][id00]['xR']=illust_info['xRestrict']#
                                tag['pics'][id00]['ur'] = illust_info['urls']['original']#'original'
                                tag['pics'][id00]['ui'] =illust_info['userId']
                                tag['pics'][id00]['uN']=illust_info['userName']#
                                tag['pics'][id00]['uA']=illust_info['userAccount']#
                                tag['pics'][id00]['LD']=illust_info['likeData']#
                                tag['pics'][id00]['wi']=illust_info['width']#
                                tag['pics'][id00]['he']=illust_info['height']#
                                tag['pics'][id00]['pc'] = illust_info['pageCount']#
                                tag['pics'][id00]['bc'] = illust_info['bookmarkCount']#
                                tag['pics'][id00]['lc'] = illust_info['likeCount']#
                                tag['pics'][id00]['cc'] = illust_info['commentCount']#
                                tag['pics'][id00]['vc'] = illust_info['viewCount']#
                                tag['pics'][id00]['iO']=illust_info['isOriginal']#
                                per_tags = illust_info['tags']['tags']#
                                bmc=int(illust_info['bookmarkCount'])
                                tags_list = []
                                for t0 in range(len(per_tags)):
                                    tag00=per_tags[t0]['tag']
                                    tags_list.append(tag00)
                                    if ('translation' in per_tags[t0]) and ( tag00 not in tag['trans'] ) :
                                        tag['trans'][tag00]=per_tags[t0]['translation']['en']
                                tag['pics'][id00]['ta']=tags_list
                                all_pid.remove(id00)
                            elif schedule==loop_num-1:
                                tag['error']['sp'].append(url_pid_now)
                        elif schedule==loop_num-1:
                            tag['error']['sp'].append(url_pid_now)
                    except:
                        if schedule==loop_num-1:
                            tag['error']['except'].append(url_pid_now)
                        print(url_pid_now, sys.exc_info())
                del all_req
                del rs_group
            del s
        tag['error']['failed']=all_pid
        gc.collect()
        print(pta+'  ok  '+str(len(all_pid))+'  '+str(len(tag['pics']))+'  '+str(len(tag['error']['404_not_found'])))
        if len(all_pid)>10 or (10000-len(tag['pics'])-len(tag['error']['404_not_found']) )>10:
            print(all_pid)
            break
        if os.path.exists(path+'/'+pta+'/'+'tag.pickle'):
            continue
        f=open(path+'/'+pta+'/'+'tag.pickle','wb')
        pickle.dump(tag,f)
        f.close()
        with open(path+'/'+pta+'/'+'tag.pickle','rb') as g:
            tag0= pickle.load(g)
        if tag!=tag0:
            print('tag!=tag0   '+pta)
            f=open(path+'/'+pta+'/'+'tag.pickle','wb')
            pickle.dump(tag,f)
            f.close()
            with open(path+'/'+pta+'/'+'tag.pickle','rb') as g:
                tag0= pickle.load(g)
            if tag!=tag0:
                print('tag!=tag0+++++++++++++++++++++++++++++   '+pta)
                os,remove(path+'/'+pta+'/'+'tag.pickle')
                

if __name__ == '__main__':
    ps = []
    for i in range(psnum):
        exec('t'+str(i)+'=multiprocessing.Process(target=run, args=('+str(i)+',))')
        exec('t'+str(i)+'.start()')
        exec('ps.append('+'t'+str(i)+')')
    for p in ps:
        p.join()
    print(1)
