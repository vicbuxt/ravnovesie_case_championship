import asyncio, sys
from playwright.async_api import async_playwright
OUT='/home/claude/shots/'
LOGIN="""(c)=>{if(S.auth)logout();$('#lgPhone').value='9001234567';$('#lgForm1').dispatchEvent(new Event('submit'));$('#lgCode').value=c;$('#lgForm2').dispatchEvent(new Event('submit'))}"""
async def main(vw, tag, full):
    async with async_playwright() as p:
        b=await p.chromium.launch();pg=await b.new_page(viewport=vw,device_scale_factor=2);errs=[];pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file:///home/claude/v10/final.html');await pg.wait_for_function('typeof RM!=="undefined"&&RM.ready')
        async def shot(n,fp=full): await pg.wait_for_timeout(250); await pg.screenshot(path=f'{OUT}{tag}_{n}.png',full_page=fp)
        await shot('00_login',False)
        await pg.evaluate(LOGIN,'333');await shot('01_consent',False)
        await pg.evaluate("()=>{[...document.querySelectorAll('#modal button')].find(b=>/со всеми/.test(b.textContent)).click();$('#consGo').click();closeModal()}")
        for t in ['home','mood','sleep','goals','techs','meds','tests','chat','book','about','data']:
            await pg.evaluate(f"()=>{{showTab('{t}');scrollTo(0,0)}}");await shot('p_'+t)
        await pg.evaluate("()=>{openSOS()}");await shot('p_sos',False);await pg.evaluate("()=>closeModal()")
        await pg.evaluate("()=>{showTab('tests');scrollTo(0,0)}")
        await pg.evaluate("()=>{const b=[...document.querySelectorAll('#pmain button')].find(x=>/Пройти|Начать/.test(x.textContent));b&&b.click()}");await shot('p_test_open')
        await pg.evaluate("()=>{showTab('mood');S.given.nlp=S.given.nlp||new Date()}")
        await pg.evaluate("()=>{const ta=$('#dText');if(ta){ta.value='Весь день лежала. Кажется, всем будет лучше без меня.';}const b=[...document.querySelectorAll('#pmain button')].find(x=>/Сохранить/.test(x.textContent));b&&b.click()}");await shot('p_mood_alert')
        await pg.evaluate(LOGIN,'111');await shot('d_today')
        for t in ['patients','calendar','requests','cons','messages','drugs']:
            await pg.evaluate(f"()=>{{S.dtab='{t}';renderDoctor();scrollTo(0,0)}}");await shot('d_'+t)
        for pid in ['anna','s3','s2']:
            for t in ['overview','scales','therapy','monitor','plan','psy','log']:
                await pg.evaluate(f"()=>{{S.dtab='patients';renderDoctor();selectPt('{pid}','{t}');scrollTo(0,0)}}");await shot(f'd_pt_{pid}_{t}')
        await pg.evaluate("()=>{openExtract()}");await pg.evaluate("()=>runExtract()");await shot('d_extract',False);await pg.evaluate("()=>closeModal()")
        await pg.evaluate("()=>{openCSSRS('anna')}");await shot('d_cssrs',False);await pg.evaluate("()=>closeModal()")
        await pg.evaluate("()=>{openSummary&&openSummary('anna')}");await shot('d_summary',False);await pg.evaluate("()=>closeModal()")
        await pg.evaluate("()=>{cfgModal()}");await shot('d_cfg',False);await pg.evaluate("()=>closeModal()")
        await pg.evaluate(LOGIN,'555');await shot('a_admin')
        await pg.evaluate(LOGIN,'000');await shot('m_master')
        print(tag,'errors',errs)
        await b.close()
asyncio.run(main({'width':1440,'height':900},'desk',True))
asyncio.run(main({'width':390,'height':844},'phone',False))
