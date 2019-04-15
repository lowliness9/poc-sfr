# -*- coding:utf-8 -*-
import threading
import requests
import re

def webSpider(url):
    lock = threading.Lock()
    """
    1.爬行建议从域名 / 开始，不可携带 /
    :param url:
    :return:
    """
    #过滤下面后缀
    filter = ['.css','.js','.jpg','png','.html','.gif','#content']
    domain = ''

    if 'http://' in url:
        if '/' in url.replace('http://',''):
            domain = url.replace('http://','').split('/')[0]
        else:
            domain = url
    else:
        if '/' in url.replace('https://',''):
            domain = url.replace('https://','').split('/')[0]
        else:
            domain = url
    #获取当前域名flag信息，防止爬行到其它网站
    flag = ''
    if 'https' in domain:
        flag = domain.replace('https://', '').split('.')[0] + '.' + domain.replace('https://', '').split('.')[1]
    else:
        flag = domain.replace('http://', '').split('.')[0] + '.' + domain.replace('https://', '').split('.')[1]
    #print flag
    resdb = []
    tmpdb = []
    tmpdb.append(url+'/')
    resdb.append(url)
    resdb.append(domain)

    while 1:
            if len(tmpdb)>0:
                url = tmpdb[0]
                lock.acquire()
                print 'Logs:resdb数量:%d tmpdb 数量:%d %s'%(len(resdb),len(tmpdb),url)
                lock.release()
                resdb.append(url)
                #baseUrl 为当前目录路径
                baseUrl = ''
                if url.endswith('/'):
                    baseUrl = url
                else:
                    #需要考虑
                    baseUrl = url.replace(url.split('/')[-1],'')
                headers = {
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36',
                    'Cache-Control':'no-cache',
                    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                    'Connection':'Keep-Alive',
                }
                try:
                    linkdb = []
                    #使用代理
                    my_proxies = {
                        'http':'http://127.0.0.1:1080',
                        'https': 'https://127.0.0.1:1080',
                    }
                    p=requests.get(url= baseUrl,headers=headers,timeout=5,proxies=my_proxies,allow_redirects=False,verify=False)
                    if 300 < p.status_code and p.status_code < 400:
                        if 'http' in p.headers['Location']:
                            if flag in p.headers['Location']:
                                tmpdb.append(p.headers['Location'])
                        else:
                            tmpdb.append(domain+'/'+p.headers['Location'])
                        tmpdb = list(set(tmpdb) - set(resdb))
                        continue
                    html= p.content
                    regex = re.compile("href=\"(.+?)\"")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("href=\'(.+?)\'")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("src=\'(.+?)\'")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("src=\"(.+?)\"")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("action=\'(.+?)\'")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("action=\"(.+?)\"")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("\'(http.*?)\'")
                    linkdb.extend(regex.findall(html))
                    regex = re.compile("\"(http.*?)\"")
                    linkdb.extend(regex.findall(html))
                    #href="#content"  action="j_acegi_security_check
                    # 抓取的链接数据处理
                    for link in linkdb:
                        if 'http' in link:
                            if flag in link:
                                isDel = False;
                                for uend in filter:
                                    if uend in link:
                                        isDel = True
                                        break
                                if isDel:
                                    pass
                                else:
                                    link = str(link).strip().replace('\\', '')
                                    link = link.split('://')[0] + '://' + re.sub('//+', '/', link.split('://')[1])
                                    tmpdb.append(link)
                            else:
                                pass
                        else:
                            if str(link).startswith('/'):
                                link= domain + link
                                isDel =False
                                for uend in filter:
                                    if uend in link:
                                        isDel =True
                                        break
                                if isDel:
                                    pass
                                else:
                                    link = str(link).strip().replace('\\','')
                                    link = link.split('://')[0] + '://' + re.sub('//+', '/', link.split('://')[1])
                                    tmpdb.append(link)
                            else:
                                link= baseUrl + '/' + link
                                isDel =False
                                for uend in filter:
                                    if uend in link:
                                        isDel = True
                                        break
                                if isDel:
                                    pass
                                else:
                                    link = str(link).strip().replace('\\','')
                                    link = link.split('://')[0] + '://' + re.sub('//+','/',link.split('://')[1])
                                    tmpdb.append(link)
                    tmpdb = list(set(tmpdb)-set(resdb))
                except Exception as e:
                    tmpdb = list(set(tmpdb) - set(resdb))
                    lock.acquire()
                    print 'Logs: error'
                    lock.release()
            else:
                break
    for link in resdb:
        #print link
        lock.acquire()
        with open('spiderUrl.txt','a+') as f:
            f.write(link+'\n')
        lock.release()
    #print 'Logs:url总数 %d'%len(resdb)



