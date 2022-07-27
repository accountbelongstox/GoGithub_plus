# PingGithub 加强版

## 一、介绍
针对网上比较流行的Gogithub做了改进开发，
该软件主要解决访问全球最大程序员网站github速度慢的问题
但原软件存在诸多问题，如：
获取到的IP并不是真实最快的IP，而是检测点最快的IP。（即是本地最快的IP和相对检测点最快的IP并不是同一个）
本软件改进了以上问题，即抓取全球可用IP并依次在本地做测试，而有粗暴的将检测点的响应程度视为本地的
同时使用了多线程技术，这是非常重要的该软件就是靠多线程保证问题速度。
亮点：支持多网站速度测试、自动配置。
（相较于原软件只支持github本软件支持了N多网站并方便自定义添加）
以以上功能本软件工作室快速度的访问了诸如scrapy.com等国外封锁的网站(scrapy.com是一个爬虫官方网站)。

*注：* 本软件属于多线程，比较耗资源，但运行时短，请在软件运行有效果后停止运行

---
## 三、效果对比
在使用本软件后成功访问到了scrapy.com等网站且速度惊人


## 使用功能介绍
- [x] 将要优化速度的网站添加到项目 webs.txt文件中
- [x] 运行软件即可 `python main.py`



## 声明
<a rel="license" href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh"><img alt="知识共享许可协议" style="border-width: 0" src="https://licensebuttons.net/l/by-nc-nd/4.0/88x31.png"></a><br>本作品采用 <a rel="license" href="https://creativecommons.org/licenses/by-nc-nd/4.0/deed.zh">署名-非商业性使用-禁止演绎 4.0 国际</a> 进行许可。

#PING网站列表
    [https://zijian.aliyun.com/](https://zijian.aliyun.com/)
    [https://tools.ipip.net/ping.php](https://tools.ipip.net/ping.php)
    [http://www.webkaka.com/UrlCheck.aspx](http://www.webkaka.com/UrlCheck.aspx)
    [https://www.itdog.cn/ping/github.com](https://www.itdog.cn/ping/github.com)
    [https://tools.ipip.net/ping.php](https://tools.ipip.net/ping.php)