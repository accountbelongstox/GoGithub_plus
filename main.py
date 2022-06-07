from queue import Queue
import time 
import re
import urllib
import http.cookiejar
from xml.etree.ElementTree import QName
from threads import thread
import subprocess
from concurrent.futures import ThreadPoolExecutor,as_completed
import threading
import os

lock = threading.Lock()

class GoGitHub():
    __ping_website = ''
    __cookie = None
    __resultQueue = Queue()

    def __init__(self):
        self.__ping_website = 'https://ping.chinaz.com'
        print(f" 正在初始化. 测速网站为：{self.__ping_website}")

    def set_headers(self,k=None,v=None):
        headers = [
            ("accept"," text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9"),
            ("accept-language", "zh-CN,zh;q=0.9,en;q=0.8"),
            ("cache-control", "max-age=0"),
            ("sec-ch-ua", "\" Not A;Brand\";v=\"99\", \"Chromium\";v=\"101\", \"Google Chrome\";v=\"101\""),
            ("sec-ch-ua-mobile", "?0"),
            ("sec-ch-ua-platform", "Windows"),
            ("sec-fetch-dest", "document"),
            ("sec-fetch-mode", "navigate"),
            ("sec-fetch-site", "none"),
            ("sec-fetch-user", "?1"),
            ("upgrade-insecure-requests", 1),
            ("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.41 Safari/537.36")
        ]
        if k != None:
            headers.append(
                (k,v)
            )
        return headers

    def ping_web(self,domain_url):
        domain_url = self.format_url(domain_url)
        print(f" -抓取 ： {domain_url} 的全球可用IP地址.")
        url_ = f'{self.__ping_website}/{domain_url}'

        if self.__cookie == None:
            self.__cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(self.__cookie)
        opener = urllib.request.build_opener(handler)
        headers = self.set_headers()
        opener.addheaders = headers
        resp = opener.open(url_)
        body = resp.read().decode('utf-8')
        the_website_ips = []

        find_id_and_token_pattarn = re.compile(r'id\="([0-9a-z\-]+(?=\"))".+token\=\"(.+)"',re.I)
        findall_group = re.findall(r'row listw tc clearfix.+\>',body,re.I)

        for test_orgine in findall_group:
            result_group = re.search(find_id_and_token_pattarn,test_orgine)
            guid = result_group.groups()[0]
            token = result_group.groups()[1]
            the_website_ips.append({
                "domain" :domain_url,
                "guid" : guid,
                "token" :token,
                'url':f'{self.__ping_website}/pingcheck?host={domain_url}&guid={guid}&token={token}',
                'cookie':self.__cookie,
                'headers':headers
            })
        print(f" {domain_url}{len(the_website_ips)} 个测试点, 启动多线程!")
        lock.acquire()
        WorldPingTest = thread.WorldPingTest()
        lock.release()
        result_ips_queue = WorldPingTest.ping_test(the_website_ips)
        print(" the website done.",result_ips_queue.qsize())

        self.ping_cmd_and_write_hosts(result_ips_queue)


    def ping_cmd_and_write_hosts(self,result_queue):
        ips = []
        domain = ""
        while result_queue.qsize() > 0:
            res = result_queue.get()
            if  "data" in res and "address" in res["data"]:
                address = res["data"]["address"]
                ipAddress = res["data"]["ipAddress"]
                domain = res["domain"]
                is_add = True
                for it in ips:
                    if it['address'] == address:
                        is_add = False
                if is_add:
                    ips.append({
                        "domain":domain,
                        "address":address,
                        "ipAddress":ipAddress
                    })
        print(f" 获取 {len(ips)} IP -{domain}, 多线程本地Ping 挑选最快IP! ")
        lock.acquire()
        BatchCmdPing = thread.BatchCmdPing()
        lock.release()
        cmdpingresult = BatchCmdPing.cmd_pint(ips)
        
        ping_timeouts = []
        while (cmdpingresult.empty() is False):
            ping_timeouts.append(cmdpingresult.get())
        ping_timeouts.sort(key = lambda x: x["timeout"])
        timeout_info = ping_timeouts[0]
        print(f"\n 挑选出的IP({domain})，将更新到HOSTS ： {timeout_info['address']} {timeout_info['ipAddress']} {timeout_info['timeout']}ms")
        self.__resultQueue.put(timeout_info)

    def set_hosts(self):
        filepath = "C:/Windows/System32/drivers/etc/HOSTS"
        hosts_list = self.format_hosts(filepath)  
        while self.__resultQueue.qsize() > 0:    
            timeout_info = self.__resultQueue.get()
            address = timeout_info['address']
            domain = timeout_info['domain']
            ipAddress = timeout_info['ipAddress']
            timeout = timeout_info['timeout']
            # hosts_fs = ["./hosts"]
            ma = f"#- {domain} -"
            subscript = f'#- {domain} - {time.strftime("%Y-%m-%d %H:%M:%S")}，{ipAddress},timeout:{timeout}ms '
            rang = len(hosts_list)
            n_hosts_list = []
            tid = 0
            # for id,hosts_tuple in enumerate(hosts_list):
            is_exist_domain = False
            while tid < rang:
                hosts_tuple = hosts_list[tid]
                hk = hosts_tuple[0]
                hv = hosts_tuple[1]
                if hk.startswith(ma):
                    n_hosts_list.append((subscript,""))
                elif hk.__eq__(domain):
                    is_exist_domain = True
                    n_hosts_list.append((domain,address))
                    prev = tid - 1
                    if prev >=0 and not hosts_list[prev][0].startswith(ma):
                        n_hosts_list.insert(tid , (subscript,""))
                else:
                    n_hosts_list.append((hk,hv))
                tid += 1
            #如果不存在,则添加
            if is_exist_domain is not True:
                n_hosts_list.append((subscript,""))
                n_hosts_list.append((domain,address))

        self.originize_hosts(n_hosts_list,filepath)
        self.flushdns()

    def originize_hosts(self,hosts_list,filepath):
        for tid,hosts_tuple in enumerate(hosts_list):
            hosts_list[tid] = f"{hosts_tuple[1]} {hosts_tuple[0]}"
        hosts_text = "\n".join(hosts_list)
        lock.acquire()
        local_f = open(filepath,"w+",encoding="utf-8")
        local_f.write(hosts_text)
        local_f.close()
        lock.release()
        return hosts_text

    def format_hosts(self,file_path):
        local_f = open(file_path,"r+",encoding="utf-8")
        local_text = local_f.read()
        local_f.close()
        local_text = local_text.strip()
        local_text = re.split('[\n\r]+',local_text)
        local_text = [t.strip() for t in local_text if t != ""]
        hosts_list = []
        tks = []
        for t in local_text:
            if t.startswith("#"):
                tk = t
                tv = ""
            else:
                ts = re.split(r'\s+',t)
                if len(ts) > 1:
                    tk = " ".join(ts[1:])
                    tv = ts[0]
                else:
                    tk = ts[0]
                    tv = ""
            if tk not in tks:
                hosts_list.append((tk,tv))
            tks.append(tk)
        return hosts_list


    def flushdns(self):
        cmd = "ipconfig /flushdns"
        out = os.popen(cmd,'r')
        
    def format_url(self,url):
        http_pattarn = re.compile(r"^[\s+|https\:\/\/|http\:\/\/|\/$]")
        url = re.sub(http_pattarn,'',url)
        return url

    def ping_all_web(self):
        lock.acquire()
        webs_f = open("./webs.txt","r",encoding="utf-8")
        all_web = webs_f.read()
        webs_f.close()
        lock.release()
        all_web = re.split(re.compile(r'[\n\r]+'),all_web)
        all_web = [re.sub(r'\s+','',web) for web in all_web if web != '']

        # for cweb in all_web:
        #     self.ping_web(cweb)
        with ThreadPoolExecutor(max_workers=10) as threadPool:
            thread_pools = []
            for cweb in all_web:
                future = threadPool.submit(self.ping_web,cweb)
                thread_pools.append(future)

            for future in as_completed(thread_pools):
                future.result()
            threadPool.shutdown(wait=True)
        self.set_hosts()

    def __del__(self):
        print(" Successfully flushed the DNS Resolver Cache.")
        print(" 所有网站都已经 ping 结束。")
        return   

if __name__ == '__main__':
    ins = GoGitHub()
    # ins.ping_web("cn.bing.com")
    ins.ping_all_web()
    