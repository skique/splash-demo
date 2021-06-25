# splash渲染引擎

Splash是Scrapy官方推荐的JavaScript渲染引擎，它是使用Webkit开发的轻量级无界面浏览器，提供基于HTTP接口的JavaScript渲染服务，支持以下功能：
- 为用户返回经过渲染的HTML页面或页面截图。
- 并发渲染多个页面。
- 关闭图片加载，加速渲染。
- 在页面中执行用户自定义的JavaScript代码。
- 执行用户自定义的渲染脚本（lua），功能类似于PhantomJS。

# 安装并开启splash服务
1. 在docker中安装Splash
`sudo docker pull scrapinghub/splash`

2. 在本机的8050和8051端口开启Splash服务：
`sudo docker run -p 8050:8050 -p 8051:8051 scrapinghub/splash`

3. 查看容器是否启动：
`docker ps -a`

Splash功能丰富，包含多个服务端点，这里只介绍其中两个最常用的端点：
- render.html提供JavaScript页面渲染服务。
- execute执行用户自定义的渲染脚本（lua），利用该端点可在页面中执行JavaScript代码。

[Splash文档地址](http://splash.readthedocs.io/en/latest/api.html)。

# splash脚本
Splash服务开启成功后，浏览器打开[http://localhost:8050/](http://localhost:8050/)，如图：
![](https://img-blog.csdnimg.cn/20200114210258848.png?x-oss-process=image/watermark,type_ZmFuZ3poZW5naGVpdGk,shadow_10,text_aHR0cHM6Ly9ibG9nLmNzZG4ubmV0L2JhaWR1XzE5NDczNTI5,size_16,color_FFFFFF,t_70)

可以直接在这个页面lua_script是否可用,例如：
demo：渲染的url通过参数传进去
```
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
```
function main(splash, args)
    splash:go(args.url)
    splash:runjs("foo = function() { return 'bar' }")
    local result = splash:evaljs("foo()")
    return result
end
```

在浏览器模拟打开拉钩网站,取搜索框的值赋值给result1,模拟搜索框输入关键系”python“,再取搜索框的值赋值result2，模拟点击搜索按钮，跳转页面。
```
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
args.url = "https://www.lagou.com/jobs/list_python?city=6&gm=&jd=&px=default"
```
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
1. splash.py脚本: 使用requests库调用render.html端点服务对页面http://quotes.toscrape.com/js/进行渲染的示例代码
2. splash_execute脚本：利用Splash的execute端点提供的服务可以实现在页面中执行一些用户自定义的JavaScript代码这样的功能
3. monilogin脚本：尝试利用Splash的execute端点，在页面中执行一些用户自定义的JavaScript代码，比如登陆功能，登陆后返回页面html。

## 在Scrapy中使用Splash
在Scrapy中调用Splash服务需要用到Python库的scrapy-splash
`pip install scrapy-splash`

创建一个Scrapy项目，取名为splash_examples：
`scrapy startproject quotes`

首先在项目配置文件settings.py中对scrapy-splash进行配置，添加内容如下：
```
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

1. 实战一：爬取toscrape中的名人名言
创建一个quote的爬虫   
`scrapy genspider quote quotes.toscrape.com`   
在这个案例中，我们只需使用Splash的render.html端点渲染页面，再进行爬取即可实现QuoteSpider，具体代码见spiders/quote.py

2. 实战二：爬取京东商城中的书籍信息

在京东商城中的书籍列表使用了动态渲染方式，即页面中的60本书不是同时加载的，开始只有30本书，当我们使用鼠标滚轮滚动到页面下方某位置时，后30本书才由JavaScript脚本加载。

既然如此，爬取这个页面时，可以先执行一段JavaScript代码，将滚动条拖到页面下方某位置，触发加载后30本书的事件

创建一个jdbook的爬虫：
`scrapy genspider jdbook search.jd.com`   

经上述分析，在爬取每一个书籍列表页面时都需要执行一段JavaScript代码，以让全部书籍加载，因此选用execute端点完成该任务，实现JDBookSpider代码见spiders/jdbook.py：


## 参考资料
-《精通Scrapy网络爬虫》第11章
-《Python 3网络爬虫实战》第7章