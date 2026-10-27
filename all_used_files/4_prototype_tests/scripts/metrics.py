import asyncio, json, time, statistics as st
from playwright.async_api import async_playwright
LOGIN="""(c)=>{if(S.auth)logout();$('#lgPhone').value='9001234567';$('#lgForm1').dispatchEvent(new Event('submit'));$('#lgCode').value=c;$('#lgForm2').dispatchEvent(new Event('submit'))}"""
M={}
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':1440,'height':900}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        loads=[]
        for i in range(5):
            t=time.time(); await pg.goto('file:///home/claude/v10/final.html'); await pg.wait_for_function('typeof RM!=="undefined"&&RM.ready'); loads.append(time.time()-t)
        M['load_s']=[round(min(loads),2),round(st.median(loads),2),round(max(loads),2)]
        await pg.evaluate(LOGIN,'333'); await pg.evaluate("()=>{[...document.querySelectorAll('#modal button')].find(b=>/со всеми/.test(b.textContent)).click();$('#consGo').click();closeModal()}")
        M['patient_tab_ms']=await pg.evaluate("""()=>{const r=[];for(let k=0;k<20;k++)for(const t of ['home','mood','sleep','goals','techs','meds','tests','chat','book','about','docs','data']){const a=performance.now();showTab(t);document.body.offsetHeight;r.push(performance.now()-a)}r.sort((a,b)=>a-b);return [r[Math.floor(r.length/2)],r[Math.floor(r.length*.95)],r.at(-1)]}""")
        M['risk_model_ms']=await pg.evaluate("""()=>{const T=['Сегодня ходила к маме, потом долго думала о том, что всем будет лучше без меня.','Хорошо погуляли','Читала статью о профилактике суицида для курсовой, тяжёлая тема, но полезная. Потом готовила ужин и звонила сестре.'];const r=[];for(let k=0;k<30;k++)for(const t of T){const a=performance.now();rmProbs(t);r.push(performance.now()-a)}r.sort((a,b)=>a-b);return [r[Math.floor(r.length/2)],r[Math.floor(r.length*.95)]]}""")
        M['alert_diary_ms']=await pg.evaluate("""()=>{S.given.nlp=S.given.nlp||new Date();S.smerMode=0;showTab('mood');const n=S.alerts.length;const a=performance.now();pickMood(0);$('#dText').value='Не хочу больше жить, всё решено.';saveDiary();const ok=S.alerts.length>n&&S.alerts[0].level==='critical';const persisted=JSON.parse(sessionStorage.getItem(SKEY)).S.alerts.length>n;return {ms:performance.now()-a,ok,persisted,reason:S.alerts[0].reason}}""")
        M['alert_sos_ms']=await pg.evaluate("""()=>{const n=S.alerts.length;const a=performance.now();openSOS();return {ms:performance.now()-a,ok:S.alerts.length>n}}""")
        await pg.evaluate(LOGIN,'111')
        M['doctor_sees_alert']=await pg.evaluate("""()=>{S.dtab='today';renderDoctor();return /не хочу больше жить|высокий/i.test(document.body.textContent)}""")
        M['doctor_tab_ms']=await pg.evaluate("""()=>{const r=[];for(let k=0;k<10;k++)for(const t of ['today','patients','calendar','requests','messages']){const a=performance.now();S.dtab=t;renderDoctor();document.body.offsetHeight;r.push(performance.now()-a)}r.sort((a,b)=>a-b);return [r[Math.floor(r.length/2)],r[Math.floor(r.length*.95)],r.at(-1)]}""")
        M['patient_card_ms']=await pg.evaluate("""()=>{const r=[];S.dtab='patients';renderDoctor();for(let k=0;k<10;k++)for(const pid of ['anna','s1','s2','s5'])for(const t of ['overview','scales','therapy','monitor','plan','psy','log']){const a=performance.now();selectPt(pid,t);document.body.offsetHeight;r.push(performance.now()-a)}r.sort((a,b)=>a-b);return [r[Math.floor(r.length/2)],r[Math.floor(r.length*.95)],r.at(-1)]}""")
        M['recommend_ms']=await pg.evaluate("""()=>{const P=allPts();const a=performance.now();let n=0;for(let k=0;k<200;k++)for(const p of P){aviCheck(p);routing(p);n++}return (performance.now()-a)/n}""")
        M['extract_ms']=await pg.evaluate("""()=>{const a=performance.now();for(let k=0;k<100;k++)extractNote(SAMPLE_EXTRACT);return (performance.now()-a)/100}""")
        load=[]
        for N in [100,1000,5000]:
            r=await pg.evaluate("""(N)=>{const base=allPts().find(p=>p.id==='s1');const keep=EXTRA.length;for(let i=0;i<N;i++){const c=JSON.parse(JSON.stringify(base),(k,v)=>typeof v==='string'&&/^\\d{4}-\\d\\d-\\d\\dT/.test(v)?new Date(v):v);c.id='L'+i;c.name='Тест '+i;EXTRA.push(c);S.teams[c.id]={med:S.me,ther:S.me}}
              S.dtab='patients';const a=performance.now();renderDoctor();document.body.offsetHeight;const ms=performance.now()-a;const a2=performance.now();const urgent=myPts().filter(p=>routing(p).m.length).length;const ms2=performance.now()-a2;
              EXTRA.splice(keep);for(let i=0;i<N;i++)delete S.teams['L'+i];return {N,render_ms:ms,filter_ms:ms2,urgent}}""",N)
            load.append(r)
        M['doctor_list_scaling']=load
        await pg.reload(); await pg.wait_for_function('typeof RM!=="undefined"&&RM.ready')
        M['restore_after_reload']=await pg.evaluate("""()=>({auth:!!S.auth,alerts:S.alerts.filter(a=>/жить/.test(a.reason)).length,diary:S.diary.length})""")
        fuzz=await pg.evaluate("""()=>{const ch='абвгдеёжзийклмнопрстуфхцчшщъыьэюяABCXYZ0123456789 .,:;!?—-«»\\n';let ex=0,n=0;const rnd=k=>Array.from({length:k},()=>ch[Math.floor(Math.random()*ch.length)]).join('');
          const samples=['',' ','\\n\\n','💥🙂','<script>alert(1)</script>','x'.repeat(20000),'а'.repeat(5000)+' не хочу жить',null,undefined,12345];
          for(let i=0;i<2000;i++){const t=i<samples.length?samples[i]:rnd(Math.floor(Math.random()*400));for(const f of [()=>analyze(t),()=>extractNote(String(t??'')),()=>findDrug(String(t??'')),()=>interAvi(String(t??''))]){n++;try{f()}catch(e){ex++}}}
          const P=allPts()[1];for(const k of Object.keys(P.intake)){const c=JSON.parse(JSON.stringify(P));c.phq=P.phq;c.gad=P.gad;delete c.intake[k];n++;try{aviCheck(c);routing(c)}catch(e){ex++}}
          return {calls:n,exceptions:ex}}""")
        M['fuzz']=fuzz
        M['errors']=errs
        cross=[]
        for w,h in [(360,740),(390,844),(768,1024),(1024,768),(1440,900),(1920,1080)]:
            q=await b.new_page(viewport={'width':w,'height':h}); await q.goto('file:///home/claude/v10/final.html'); await q.wait_for_function('typeof RM!=="undefined"&&RM.ready')
            bad=[]
            await q.evaluate(LOGIN,'333'); await q.evaluate("()=>{[...document.querySelectorAll('#modal button')].find(b=>/со всеми/.test(b.textContent)).click();$('#consGo').click();closeModal()}")
            for t in ['home','mood','sleep','goals','techs','meds','tests','chat','book','about','docs','data']:
                await q.evaluate(f"()=>showTab('{t}')")
                if await q.evaluate("()=>document.documentElement.scrollWidth>innerWidth+1"): bad.append('p_'+t)
            await q.evaluate(LOGIN,'111')
            for t in ['today','patients','calendar','requests','messages']:
                await q.evaluate(f"()=>{{S.dtab='{t}';renderDoctor()}}")
                if await q.evaluate("()=>document.documentElement.scrollWidth>innerWidth+1"): bad.append('d_'+t)
            cross.append({'w':w,'overflow':bad}); await q.close()
        M['viewports']=cross
        await b.close()
asyncio.run(main())
print(json.dumps(M,ensure_ascii=False,indent=1)); json.dump(M,open('/home/claude/tech_metrics.json','w'),ensure_ascii=False,indent=1)
