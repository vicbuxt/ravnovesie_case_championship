import asyncio, time, json
from playwright.async_api import async_playwright
LOGIN="""(c)=>{if(S.auth)logout();$('#lgPhone').value='9001234567';$('#lgForm1').dispatchEvent(new Event('submit'));$('#lgCode').value=c;$('#lgForm2').dispatchEvent(new Event('submit'))}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport={'width':1440,'height':900})
        await pg.goto('file:///home/claude/v10/final.html');await pg.wait_for_function('typeof RM!=="undefined"&&RM.ready')
        pg.on('dialog',lambda d:asyncio.ensure_future(d.accept('ok')))
        R={}
        class C:
            def __init__(s):s.n=0;s.t=time.time();s.log=[]
            async def click(s,sel,txt=None,nth=0):
                loc=pg.locator(sel,has_text=txt) if txt else pg.locator(sel)
                await loc.nth(nth).click();s.n+=1;s.log.append(txt or sel);await pg.wait_for_timeout(60)
            async def fill(s,sel,v):await pg.locator(sel).first.fill(v);s.n+=1;s.log.append('ввод');await pg.wait_for_timeout(60)
            def done(s,name):R[name]={'actions':s.n,'steps':s.log}
        await pg.evaluate(LOGIN,'333');await pg.evaluate("()=>{[...document.querySelectorAll('#modal button')].find(b=>/со всеми/.test(b.textContent)).click();$('#consGo').click();closeModal();showTab('home')}")
        c=C();await c.click('#ptabs button','Дневник');await c.click('#pmain [onclick="pickMood(3)"]');await c.click('#pmain button','Своими словами');await c.fill('#dText','Спокойный день');await c.click('#pmain button','Сохранить запись');c.done('Пациент: запись в дневник')
        await pg.evaluate("()=>showTab('home')");c=C();await c.click('button','SOS');c.done('Пациент: SOS → номера помощи')
        await pg.evaluate("()=>showTab('home')");c=C();await c.click('#pmain button','Отметить');await c.click('#pmain button','Принял(а)');c.done('Пациент: отметить приём препарата')
        await pg.evaluate("()=>{showTab('home')}");c=C();await c.click('#pmain button','Заполнить');await c.click('#pmain button','Заполнить')
        nq=await pg.locator('#testArea .q').count()
        for i in range(nq): await pg.locator('#testArea .q').nth(i).locator('label').nth(1).click();c.n+=1
        print('questions',nq,await pg.locator('#testArea h3').inner_text())
        await c.click('#testArea button.dark') if await pg.locator('#testArea button.dark').count() else await c.click('#testArea button');c.done('Пациент: пройти PHQ-9')
        await pg.evaluate("()=>{S.given.nlp=S.given.nlp||new Date();S.smerMode=0;showTab('mood');pickMood(0);$('#dText').value='Не хочу больше жить';saveDiary()}")
        await pg.evaluate(LOGIN,'111');await pg.evaluate("()=>{S.dtab='today';renderDoctor()}")
        print('alert zone', await pg.locator('#alertsZone button').all_inner_texts())
        c=C();await c.click('#alertsZone button',nth=0);c.done('Врач: реакция на критический алерт')
        await pg.evaluate("()=>{S.dtab='patients';renderDoctor()}");c=C();await c.click('#doctorView button','Загрузить выписку');await c.click('#modal button','Извлечь');await c.click('#modal button','Проверено');c.done('Врач: внести пациента из выписки')
        await pg.evaluate("()=>{S.dtab='patients';renderDoctor();selectPt('s1','overview')}");c=C();await c.click('#ptCard button','Назначение');await c.click('#ptCard button','Назначить');
        mb=await pg.locator('#modal button').all_inner_texts();print('after prescribe modal',mb[:6]);c.done('Врач: назначить Авиандр (схема по инструкции)')
        print(json.dumps(R,ensure_ascii=False,indent=1));json.dump(R,open('/home/claude/ergo.json','w'),ensure_ascii=False,indent=1)
        await b.close()
asyncio.run(main())
