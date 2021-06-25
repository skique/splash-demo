import requests
import json
# from scrapy_splash import SplashRequest
from scrapy.selector import Selector

lua_script = '''
function main(splash, args)
    splash:go(args.url)
    splash:wait(3)
  	splash:runjs("getValue = function() { return document.querySelector('ul.passport .login').text }")
  	local text = splash:evaljs("getValue()")
  	splash:evaljs("document.querySelector('.login-pop').style.display = 'block'")
    splash:runjs("getValue = function() { return document.querySelector('input.input.login_enter_password').value }")
    splash:runjs("keyboardInput = function (dom, st) {let evt = document.createEvent('HTMLEvents');evt.initEvent('input', true, true); dom.value = st; dom.dispatchEvent(evt);}")
    splash:evaljs("keyboardInput(document.querySelector('input.input.login_enter_password'), '13619604534')")
    local result1 = splash:evaljs("getValue()")
  	splash:evaljs("keyboardInput(document.querySelector('input[type=password].input.login_enter_password'), 'skique7')")
    splash:wait(2)
    return {
    	text = text,
        result1 = result1,
        png = splash:png(),
    }
end
'''



splash_url = 'http://localhost:8050/execute'
headers={'content-type':'application/json'}
data = json.dumps({'lua_source':lua_script})
args = {'url': 'http://quotes.toscrape.com/js', 'timeout': 60, 'image': 0}

response = requests.post(splash_url, headers=headers, data=data)
response.content

response.json()
sel = Selector(response)
sel.css('div.JDJRV-lable-refresh').extract()


    # 京东脚本
    # splash:runjs("document.querySelector('div.login-tab.login-tab-r').click()")
    # splash:runjs("keyboardInput(document.getElementById('loginname'),'userName')")
    # splash:runjs("keyboardInput(document.getElementById('nloginpwd'),'userPassword')")
    # splash:runjs("document.getElementById('loginsubmit').click()")



    # 拉钩脚本
    # splash:wait(2)
    # splash:runjs("document.querySelector('ul.passport .login').click()")
    # splash:runjs("keyboardInput(document.querySelector('input.input.login_enter_password'), '13619604534')")
    # splash:runjs("keyboardInput(document.querySelector('input[type=password].input.login_enter_password'), 'skique7')")
    # splash:runjs("document.querySelector('div.login-btn.login-password').click()")
    
    # 豆瓣脚本


# test：runjs定义一个函数,并且使用evaljs运行这个函数
# lua_script = '''
# function main(splash, args)
#     splash:go("https://www.baidu.com")
#     splash:runjs("foo = function() { return 'bar' }")
#     local result = splash:evaljs("foo()")
#     return result
# end
# '''


# 拉钩首页关闭弹窗模拟搜索python并点击搜索
lua_script = '''
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
    }
end
'''
