import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page();errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/ravnovesie_prototype.html')
        print('canplay', await pg.evaluate("new Audio().canPlayType('audio/mpeg')"))
        await pg.evaluate("""(c)=>{$('#lgPhone').value='9001234567';$('#lgForm1').dispatchEvent(new Event('submit'));$('#lgCode').value=c;$('#lgForm2').dispatchEvent(new Event('submit'))}""",'333')
        await pg.wait_for_timeout(800)
        for id in ['breath','ground','pmr','small','kind','scan','leaves']:
            await pg.evaluate(f"playTech('{id}')")
            await pg.click('#plBtn');await pg.wait_for_timeout(1500)
            r=await pg.evaluate("({d:PL.au&&PL.au.duration,t:PL.au&&PL.au.currentTime,pos:$('#plPos').textContent,on:PL.on,au:!!PL.au})")
            print(id,r)
            await pg.evaluate("closeModal()")
            print(' after close PL', await pg.evaluate("PL"))
        await pg.evaluate("playTech('breath')");await pg.wait_for_timeout(300)
        await pg.screenshot(path='player.png')
        print('errs',errs);await b.close()
asyncio.run(main())
