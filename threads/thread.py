import json
from queue import Queue
from tkinter import N
import urllib
import threading
from concurrent.futures import ThreadPoolExecutor,as_completed
import os
import re


class WorldPingTest():
    __thread_pool = None
    __resultQueue = None

    
    def __init__(self):
        if self.__resultQueue == None:
            print(" 新建 Queue < WorldPingTest。")
            self.__resultQueue = Queue()
        pass
        

    def ping_test(self, the_website_ips):
        self.max_workers = len(the_website_ips)
        if self.max_workers == 0:
            print(" no task at thread_pool。")
            return 
        if self.__thread_pool == None :
            print(" 新建线程池 thread_pool。")
            self.__thread_pool = ThreadPoolExecutor(max_workers=self.max_workers)
        else:
            print(" 复用 thread_pool。")

        thread_runIndes = 1
        tasks = []
        domain = ""
        for dict_ in the_website_ips:
            domain = dict_["domain"]
            guid = dict_["guid"]
            token = dict_["token"]
            dict_["thread_id"] = thread_runIndes
            task = self.__thread_pool.submit(self.ping_run, dict_ )
            thread_runIndes += 1
            tasks.append(task)
        print(f" Started test-points to Thread pool are {thread_runIndes -1 } | {domain} ")
        done_id = 1
        for task in tasks:
            r = task.result()
            done_id += 1
        self.__thread_pool.shutdown(wait=True)
        print(f"\n Threads executing done. Test result are {self.__resultQueue.qsize()}")
        return self.__resultQueue

                
    def ping_run(self,web_ips):
        cookie = web_ips["cookie"]
        headers = web_ips["headers"]
        domain = web_ips["domain"]
        url = web_ips["url"]
        handler = urllib.request.HTTPCookieProcessor(cookie)
        opener = urllib.request.build_opener(handler)
        opener.addheaders = headers
        resp = opener.open( url )
        result = resp.read().decode('utf-8')
        res_json = json.loads(result)
        res_json["domain"] = domain
        self.__resultQueue.put(res_json)
        print(f"\r the Test-point done. processing ： {self.__resultQueue.qsize()} / {self.max_workers}",end="")
        return res_json


class BatchCmdPing():
    __resultQueue = None
    
    def __init__(self):
        if self.__resultQueue == None:
            print(" 新建 Queue < BatchCmdPing。")
            self.__resultQueue = Queue()
        pass
    
    def cmd_pint(self,ips):
        max_workers = len(ips)
        if max_workers > 0 :
            with ThreadPoolExecutor(max_workers=max_workers) as threadPool:
                thread_pools = []
                for ipi in ips:
                    future_ = threadPool.submit(self.cmd_ping_run,ipi)
                    thread_pools.append(future_)

                for future in as_completed(thread_pools):
                    result = future.result()
                    if result != None:
                        self.__resultQueue.put(result)
                threadPool.shutdown(wait=True)
        return self.__resultQueue

    def cmd_ping_run(self,ipi):
        domain = ipi["domain"]
        ip = ipi["address"]
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
        divint = len(time_group)
        is_NotFound_mianhost = False
        if divint ==0:
            is_NotFound_mianhost = True
            divint = 1
        timeout = timeout // divint
        # print(f" ping {domain} {ip} {timeout}ms")
        if is_NotFound_mianhost:
            ping_result = None
            print("Error:",ipi,outs)
        else:
            ping_result = {
                            "address":ip,
                            "ipAddress":ipi["ipAddress"],
                            "timeout":timeout,
                            "domain":domain
                        }
        return ping_result
