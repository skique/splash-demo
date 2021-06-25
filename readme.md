

1.  在docker中安装Splash
`sudo docker pull scrapinghub/splash` 
1.  在本机的8050和8051端口开启Splash服务：
`sudo docker run -p 8050:8050 -p 8051:8051 scrapinghub/splash` 
1.  查看容器是否启动：
`docker ps -a` 



Splash功能丰富，包含多个服务端点，这里只介绍其中两个最常用的端点：


- render.html提供JavaScript页面渲染服务。
- execute执行用户自定义的渲染脚本（lua），利用该端点可在页面中执行JavaScript代码。



[Splash文档地址](http://splash.readthedocs.io/en/latest/api.html)。


## splash脚本


Splash服务开启成功后，浏览器打开[http://localhost:8050/](http://localhost:8050/)，如图：
![](https://img-blog.csdnimg.cn/20200114210258848.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2JhaWR1XzE5NDczNTI5,size_16,color_FFFFFF,t_70#id=Z7XQm&originHeight=884&originWidth=1353&originalType=binary&ratio=1&status=done&style=none)


可以直接在这个页面lua_script是否可用,例如：


demo：渲染的url通过参数传进去


```lua
function main(splash, args)
  assert(splash:go(args.url))
  assert(splash:wait(0.5))
  return {
    html = splash:html(),
    png = splash:png(),
    har = splash:har(),
  }
end
```


runjs定义一个函数,并且使用evaljs运行这个函数


```lua
function main(splash, args)
    splash:go(args.url)
    splash:runjs("foo = function() { return 'bar' }")
    local result = splash:evaljs("foo()")
    return result
end
```


在浏览器模拟打开拉钩网站,取搜索框的值赋值给result1,模拟搜索框输入关键系”python“,再取搜索框的值赋值result2，模拟点击搜索按钮，跳转页面。


```lua
function main(splash, args)
    splash:go("http://www.lagou.com")
    splash:wait(2)
    splash:runjs("document.querySelector('a.tab.focus').click()")
    splash:wait(2)
    splash:runjs("getValue = function() { return document.querySelector('#search_input').value }")
    local result1 = splash:evaljs("getValue()")
    splash:runjs("keyboardInput = function (dom, st) {let evt = document.createEvent('HTMLEvents');evt.initEvent('input', true, true); dom.value = st; dom.dispatchEvent(evt);}")
    splash:evaljs("keyboardInput(document.querySelector('#search_input'), 'python')")
    local result2 = splash:evaljs("getValue()")
    splash:evaljs("document.querySelector('#search_button').click()")
    splash:wait(5)
    return {
        result1 = result1,
        result2 = result2,
        png = splash:png(),
        html = splash:html(),
    }
end
```


拉勾模拟用户登陆，打开用户登陆的弹窗，分别在用户名和密码的输入框输入真实的用户名密码。再模拟点击登陆按钮
args.url = "[https://www.lagou.com/jobs/list_python?city=6&gm=&jd=&px=default](https://www.lagou.com/jobs/list_python?city=6&gm=&jd=&px=default)"


```lua
function main(splash, args)
    splash:go(args.url)
    splash:wait(3)
  	splash:evaljs("document.querySelector('.login-pop').style.display = 'block'")
    splash:runjs("getValue = function() { return document.querySelector('input.input.login_enter_password').value }")
    splash:runjs("keyboardInput = function (dom, st) {let evt = document.createEvent('HTMLEvents');evt.initEvent('input', true, true); dom.value = st; dom.dispatchEvent(evt);}")
    splash:evaljs("keyboardInput(document.querySelector('input.input.login_enter_password'), '136****4534')")
  	splash:evaljs("keyboardInput(document.querySelector('input[type=password].input.login_enter_password'), '12345678')")
    splash:evaljs("document.querySelector('div.login-btn.login-password').click()")
    splash:wait(2)
    return {
    	text = text,
        result1 = result1,
        png = splash:png(),
    }
end
```


## 在shell中使用splash脚本


建议在shell脚本中复制粘贴示例代码，因为在vscode中直接运行没有返回值


### 实例1 ：render.html端点
使用requests库调用render.html端点服务对页面 [http://quotes.toscrape.com/js/](http://quotes.toscrape.com/js/) 进行渲染的示例代码 。
在终端中进入python的编译环境，输入以下代码
```python
import requests
from scrapy.selector import Selector

splash_url = 'http://localhost:8050/render.html'
args = {'url': 'http://quotes.toscrape.com/js', 'timeout': 60, 'image': 0}

response = requests.get(splash_url, params=args)

sel = Selector(response)
sel.css('div.quote span.text::text').extract()
```
运行成功后即取到了页面上的名人名言，运行结果如图
![image.png](https://cdn.nlark.com/yuque/0/2021/png/638254/1624605796185-0974c6eb-abbe-435f-8b4e-99e8e8bde0be.png#clientId=u90185fc2-b9f5-4&from=paste&height=754&id=u6e455689&margin=%5Bobject%20Object%5D&name=image.png&originHeight=754&originWidth=1266&originalType=binary&ratio=1&size=483311&status=done&style=none&taskId=uae26be9d-ea3e-4503-b1bb-55dfc8c6234&width=1266)
### 实例2：execute端点
在爬取某些页面时，我们想在页面中执行一些用户自定义的JavaScript代码，例如，用JavaScript模拟点击页面中的按钮，或调用页面中的JavaScript函数与服务器交互，利用Splash的execute端点提供的服务可以实现这样的功能。
​

splash_execute脚本：利用Splash的execute端点提供的服务可以实现在页面中执行一些用户自定义JavaScript代码自定义的功能
​

下面是使用requests库调用execute端点服务的示例代码。
```python
import requests
import json

# 这段脚本需要在命令行运行
lua_script = '''
function main(splash)
    splash:go("http://quotes.toscrape.com") --打开页面
    splash:wait(0.5) --等待时间
    local title = splash:evaljs("document.title") --执行js代码获取结果
    return {title = title} --返回json形式的结果
    end
'''

splash_url = 'http://localhost:8050/execute'
headers={'content-type':'application/json', 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'}
data = json.dumps({'lua_source':lua_script})
# args = {'url': 'http://quotes.toscrape.com/js', 'timeout': 60, 'image': 0}

response = requests.post(splash_url, headers=headers, data=data)
response.content

response.json()
```
运行结果如图：
![image.png](https://cdn.nlark.com/yuque/0/2021/png/638254/1624606136457-bc0e765f-8ef8-4cda-9167-7fe1765088a3.png#clientId=u90185fc2-b9f5-4&from=paste&height=914&id=u80084fda&margin=%5Bobject%20Object%5D&name=image.png&originHeight=914&originWidth=1254&originalType=binary&ratio=1&size=464666&status=done&style=none&taskId=u647d5a1c-455c-4bb4-888c-7519b0cf035&width=1254)
## 在Scrapy中使用Splash


在Scrapy中调用Splash服务需要用到Python库的scrapy-splash
`pip install scrapy-splash`


创建一个Scrapy项目，取名为splash_examples：
`scrapy startproject quotes`


首先在项目配置文件settings.py中对scrapy-splash进行配置，添加内容如下：


```python
# Splash服务器地址
SPLASH_URL = 'http://localhost:8050'

# 开启Splash的两个下载中间件并调整HttpCompressionMiddleware的次序
DOWNLOADER_MIDDLEWARES = {
   'scrapy_splash.SplashCookiesMiddleware': 723,
   'scrapy_splash.SplashMiddleware': 725,
   'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
}

# 设置去重过滤器
DUPEFILTER_CLASS = 'scrapy_splash.SplashAwareDupeFilter'

# 用来支持cache_args（可选）
SPIDER_MIDDLEWARES = {
    'scrapy_splash.SplashDeduplicateArgsMiddleware': 100
}
```


编写Spider代码过程中，使用scrapy_splash调用Splash服务非常简单，scrapy_splash中定义了一个SplashRequest类，用户只需使用scrapy_splash.SplashRequest（替代scrapy.Request）提交请求即可。


### 实战一：爬取toscrape中的名人名言


创建一个quote的爬虫
`scrapy genspider quote quotes.toscrape.com`
在这个案例中，我们只需使用Splash的render.html端点渲染页面，再进行爬取即可实现QuoteSpider，具体代码见spiders/quote.py。
```python
import scrapy
from scrapy_splash import SplashRequest

class QuoteSpider(scrapy.Spider):
    name = 'quote'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['http://quotes.toscrape.com/js/']

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, args={'images':0, 'timeout': 30})

    def parse(self, response):
        for sel in response.css('div.quote'):
            quote = sel.css('span.text::text').extract_first()
            author= sel.css('small.author::text').extract_first(),
            # tags= sel.css('.tag::text').extract()
            yield {'quote':quote,'author':author}
            href = response.css('li.next > a::attr(href)').extract_first()
            if href:
                url = response.urljoin(href)
                yield SplashRequest(url, args = {'images': 0, 'timeout': 30})
```


运行这个爬虫并保存文件
`scrapy crawl quote -o quote.csv`
​

可以看到成功获取了网站下的名人名言。


### 实战二：爬取京东商城中的书籍信息


在京东商城中的书籍列表使用了动态渲染方式，即页面中的60本书不是同时加载的，开始只有30本书，当我们使用鼠标滚轮滚动到页面下方某位置时，后30本书才由JavaScript脚本加载。


既然如此，爬取这个页面时，可以先执行一段JavaScript代码，将滚动条拖到页面下方某位置，触发加载后30本书的事件


创建一个jdbook的爬虫：
`scrapy genspider jdbook search.jd.com`


经上述分析，在爬取每一个书籍列表页面时都需要执行一段JavaScript代码，以让全部书籍加载，因此选用execute端点完成该任务，实现JDBookSpider代码见spiders/jdbook.py。
​

```python
import scrapy
from scrapy import Request
from scrapy_splash import SplashRequest

lua_script = '''
function main(splash)
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("document.getElementsByClassName('page')[0].scrollIntoView(true)")
    splash:wait(2)
    return splash:html()
end
'''

class JdbookSpider(scrapy.Spider):
    name = 'jdbook'
    # allowed_domains = ['search.jd.book']
    base_url = 'https://search.jd.com/Search?keyword=python&enc=utf-8&wq=python'

    def start_requests(self):
        yield Request(self.base_url, callback=self.parse_urls, dont_filter=True)

    def parse_urls(self, response):
        # 获取商品总数，计算出总页数
        # total = int(response.css('span#J_resCount::text').extract_first())
        # pageNum = total // 60 + (1 if total % 60 else 0)
        # pageNum = response.css('.fp-text i::text').extract_first() || 100
        pageNum = 10

        # 构造每页的url，向Splash的execute端点发送请求
        for i in range(pageNum):
            url = '%s&page=%s' % (self.base_url, 2*i+1)
            yield SplashRequest(url, 
                endpoint='execute', 
                args={'lua_source': lua_script},
                cache_args=['lua_source'])

    def parse(self, response):
        # 获取一个页面中每本书的名字和价格
        for sel in response.css('ul.gl-warp.clearfix > li.gl-item'):
            yield {
                'name': sel.css('div.p-name').xpath('string(.//em)').extract_first(),
                'price': sel.css('div.p-price i::text').extract_first(),
            }

```


运行这个爬虫并保存文件
`scrapy crawl jdbook -o books.csv`
​

可以看到成功获取了网站下的所有图书的信息。


源码地址：[splash-demo](https://github.com/skique/splash-demo)   
别忘了点颗小星星🌟🌟

## 参考资料

- 《精通Scrapy网络爬虫》第11章
- 《Python 3网络爬虫实战》第7章
