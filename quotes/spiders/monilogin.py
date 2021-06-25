from scrapy_splash import SplashRequest

lua_script = '''
function main(splash)
    local keyboardInput = splash:jsfunc([[
        function () {
             var evt = new InputEvent('input', {
                inputType: 'insertText',
                data: st,
                dataTransfer: null,
                isComposing: false
            });
            dom.value = st;
            dom.dispatchEvent(evt);
        }
    ]])
    splash:go(splash.args.url)
    splash:wait(2)
    splash:runjs("keyboardInput(document.getElementById('loginname'),'userName')")
    splash:runjs("keyboardInput(document.getElementById('nloginpwd'),'userPassword')")
    splash:runjs("document.getElementById('loginsubmit').click()")

    splash:wait(2)
    return splash:html()
end
'''