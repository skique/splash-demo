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
# sel = Selector(response)
# sel.css('div.JDJRV-lable-refresh').extract()
