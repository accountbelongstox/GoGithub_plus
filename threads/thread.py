import json
import threading
import urllib
import threading
from concurrent.futures import ThreadPoolExecutor,as_completed
import os
import re

class unit_world_ping(threading.Thread):
    
    def __init__(self,name,web_dict,result_website_ips_queue,cookie,headers,ping_website):
        threading.Thread.__init__(self,name=name)
        self.web_dict = web_dict
        self.__result_website_ips_queue = result_website_ips_queue
        self.__cookie = cookie
        self.__name = name
        self.__headers = headers
        self.__ping_website = ping_website

    def run(self):
        domain = self.web_dict["domain"]
        guid = self.web_dict["guid"]
        token = self.web_dict["token"]
        url_ = f'{self.__ping_website}/pingcheck?host={domain}&guid={guid}&token={token}'
        handler = urllib.request.HTTPCookieProcessor(self.__cookie)
        opener = urllib.request.build_opener(handler)
        opener.addheaders = self.__headers
        resp = opener.open( url_ )
        result = resp.read().decode('utf-8')
        res_json = json.loads(result)
        #
        # print(f" Threading  : {self.__name} guid = {guid} token = {token} ",res_json)
        
        if res_json["code"] == 1:
            self.__result_website_ips_queue.put(res_json)
        else:
            print(f" error(unique test): {self.__name} ： {res_json}")


class batch_cmd_ping():
    def __init__(self,ips,result_website_ips_queue):
        self.__max_thread = len(ips)
        self.__result_website_ips_queue = result_website_ips_queue
        if self.__max_thread > 0 :
            with ThreadPoolExecutor(max_workers=self.__max_thread) as threadPool:
                thread_pools = []
                for ip in ips:
                    future_ = threadPool.submit(self.run,ip)
                    thread_pools.append(future_)

                for future in as_completed(thread_pools):
                    result = future.result()
                    self.__result_website_ips_queue.put({
                        "ip":ip,
                        "ms":result
                    })
                threadPool.shutdown(wait=True)
  
    def run(self,ip):
        cmd = f"ping {ip}"
        outs = os.popen(cmd,'r')
        out = outs.read()
        
        get_time = re.compile(r"time\=(\d+)")
        time_group = re.findall(get_time,out)
        time_outs = re.compile(r"request\s+timed\s+out",re.I)
        time_outs_group = re.findall(time_outs,out)

        time_group = [int(t) for t in time_group]
        #如果有 Request time out 
        time_outs_group = [1000 for t in time_outs_group]
        #合并所有延迟,并计算最终值.
        time_group = time_group + time_outs_group
        timeout = 0
        for t in time_group :
            timeout += t
        timeout = timeout // len(time_group)
        print(f"timeout {ip} -> {timeout}")
        return timeout
