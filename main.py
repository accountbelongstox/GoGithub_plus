from multiprocessing.connection import wait
from queue import Queue
import re
import urllib
import http.cookiejar
from threads import thread
import subprocess
import os

class GoGitHub():
    __ping_website = ''
    __cookie = None
    __all_web = []
    #将待单元测试的服务器URL压下队列
    the_website_ips = Queue()
    #线程处理后的结果同时加入队列
    result_website_ips_queue = Queue()

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
        url_ = f'{self.__ping_website}/{domain_url}'

        if self.__cookie == None:
            self.__cookie = http.cookiejar.CookieJar()
        handler = urllib.request.HTTPCookieProcessor(self.__cookie)
        opener = urllib.request.build_opener(handler)
        headers = self.set_headers()
        opener.addheaders = headers
        resp = opener.open(url_)
        body = resp.read().decode('utf-8')
        

        find_id_and_token_pattarn = re.compile(r'id\="([0-9a-z\-]+(?=\"))".+token\=\"(.+)"',re.I)
        findall_group = re.findall(r'row listw tc clearfix.+\>',body,re.I)

        for test_orgine in findall_group:
            result_group = re.search(find_id_and_token_pattarn,test_orgine)
            guid = result_group.groups()[0]
            token = result_group.groups()[1]
            self.the_website_ips.put({
                "domain" :domain_url,
                "guid" : guid,
                "token" :token
            })

        unique_ping_threads = []
        while self.the_website_ips.qsize() > 0:
            web_dict = self.the_website_ips.get()
            thread_name = f"id-{self.the_website_ips.qsize()}-guid-{web_dict['guid']}"
            unique_thread = thread.unit_world_ping(thread_name, web_dict, self.result_website_ips_queue, (self.__cookie) , headers,self.__ping_website)
            unique_ping_threads.append(unique_thread)

        print(f" 一共有 {self.the_website_ips.qsize()} 个测试点, 正在准备调用多线程!")

        for unique_thread in unique_ping_threads:
            unique_thread.start()
        
        for unique_thread in unique_ping_threads:
            unique_thread.join()

        print(f" \n -\n -\n -\n -\n -\n -\n")
        print(f" 线程执行完毕 网站为{domain_url}")
        print(f" \n -\n -\n -\n -\n -\n -\n")
        self.ping_cmd_and_write_hosts(domain_url)

    def ping_cmd_and_write_hosts(self,domain_url):
        ips = set()
        while self.result_website_ips_queue.qsize() > 0:
            res = self.result_website_ips_queue.get()
            ips.add(res["data"]["address"])

        print(f" {len(ips)} IP需要测速, 正在准备以线程池方式! ")
        thread.batch_cmd_ping(ips,self.result_website_ips_queue)
        # write_hosts
        timeouts = []
        for ip in ips:
            timeouts.append(self.result_website_ips_queue.get())
        timeouts.sort(key= lambda x: x["ms"])
        timeout = timeouts[0]

        print(f"\n{timeout['ip']} {domain_url}")
        self.set_hosts(timeout['ip'],domain_url,timeout['ms'])
    
    def set_hosts(self,k,v,ms=""):

        hosts_fs = ["./HOSTS","C:/Windows/System32/drivers/etc/HOSTS"]

        for f in hosts_fs:
            local_f = open(f,"r+",encoding="utf-8")
            local_text = local_f.read()
            local_f.close()
            local_text = local_text.strip()
            local_text = local_text.replace('[\n\r]+','')

            local_text = local_text.split("\n")
            local_text = [t for t in local_text if t != '']
            print(local_text)
            hosts = {}
            for host in local_text:
                host = host.strip()
                if not host.startswith("#"):
                    r = re.compile(r"\s+")
                    host = re.sub(r," ",host)
                    host = host.split(r" ")
                    key = host[0]
                    if len(host) > 0:
                        value = host[1]
                    else:
                        value = 000
                    hosts[key] = value
                else:
                    key = host
                    value = ""
                    hosts[value] = key

            #set HOSTS key and value;
            k_ = f"# ms = {ms}"
            hosts[k_] = ""
            print(hosts.keys())
            print("k",k)
            hosts[k] = v
            print(hosts.keys())
            print(hosts.values())

            line_text  = ""
            for host_k, host_v in hosts.items():
                line_text += f"{host_k} {host_v}\n"
                
            local_f = open(f,"w+",encoding="utf-8")
            local_f.write(line_text)
            local_f.close()
        self.flushdns()

    def flushdns(self):
        cmd = "ipconfig /flushdns"
        out = subprocess.Popen(cmd)
        out.wait()
        print(out.stdout)
        
        
    def format_url(self,url):
        http_pattarn = re.compile(r"^[\s+|https\:\/\/|http\:\/\/|\/$]")
        url = re.sub(http_pattarn,'',url)
        return url

    def ping_all_web(self):
        webs_f = open("./webs.txt","r",encoding="utf-8")
        all_web = webs_f.read()
        webs_f.close()
        all_web = all_web.replace(r'\s+','')
        all_web = all_web.split('\n')
        self.__all_web = [web for web in all_web if web != '']
        for courrent_web in self.__all_web:
            self.ping_web(courrent_web)
        self.ping_next_website()


    def __del__(self):
        print(" 所有网站都已经 ping 结束。")
        return   

if __name__ == '__main__':
    ins = GoGitHub()
    ins.ping_all_web()
    