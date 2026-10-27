const {JSDOM}=require('jsdom');const fs=require('fs');
const dom=new JSDOM(fs.readFileSync(process.argv[2]||'/home/claude/v10/final.html','utf8'),{runScripts:'dangerously',pretendToBeVisual:true,url:'https://x.test/'});const w=dom.window;
const errs=[];w.addEventListener('error',e=>errs.push(e.message+' @'+e.lineno));w.alert=m=>console.log('ALERT',m);w.prompt=()=>'ok';w.confirm=()=>true;w.scrollTo=()=>{};w.Element.prototype.scrollIntoView=function(){};
w.matchMedia=w.matchMedia||(()=>({matches:false}));
const $=s=>w.document.querySelector(s);const ev=x=>w.eval(x);
function login(code,phone='9001234567'){w.logout&&ev('S.auth')&&w.logout();$('#lgPhone').value=phone;$('#lgForm1').dispatchEvent(new w.Event('submit'));$('#lgCode').value=code;$('#lgForm2').dispatchEvent(new w.Event('submit'));}
setTimeout(()=>{try{
 login('333');const M=$('#modal').textContent;console.log('no req tags',!/(^|[^е])(обязательн|желательн)/i.test(M.replace(/нежелательн/gi,'')));
 $('#consGo').click();console.log('consErr',$('#consErr').textContent,'onboarded',ev('S.onboarded'));
 [...w.document.querySelectorAll('#modal button')].find(b=>/со всеми/.test(b.textContent)).click();$('#consGo').click();w.closeModal();
 const body=()=>w.document.body.textContent;
 for(const t of ['home','mood','sleep','goals','techs','meds','tests','chat','book','about','docs','data']){w.showTab(t);if(!$('#pmain').textContent.trim())console.log('EMPTY',t)}
 const all=[];for(const t of ['home','mood','sleep','goals','techs','meds','tests','chat','book','about','docs','data']){w.showTab(t);all.push($('#pmain').textContent)}const A=all.join(' ');
 for(const bad of ['Анализ текста ищет','консенсусному дневнику','достиг(ла)','в наушниках или вслух','опросники приходят по графику','Выберите опросник выше','Набор методик согласован','Право на доступ','бесплатно и не требует объяснений'])console.log('gone',bad,!A.includes(bad));
 console.log('goal text',A.includes('Выполнение цели отмечается во время обсуждения со специалистом'));
 w.showTab('about');console.log('profile about sub about',/Обо мне/.test($('#pmain').textContent)&&/anna\.k@example\.ru/.test($('#pmain').textContent),'phone',/\+7|900/.test($('#pmain').textContent),'life',/Анкета о жизни/.test($('#pmain').textContent));
 const tests=[['Не хочу больше жить, всё решено',2],['Посмотрела фильм, где герой хотел покончить с собой',0],['Устала, ничего не получается и не получится',1],['Сегодня гуляли в парке, было хорошо',0]];
 for(const [t,e] of tests){const p=w.rmProbs(t);console.log('model',w.analyze(t),'exp',e,p.map(x=>x.toFixed(2)).join('/'),t)}
 w.showTab('mood');const before=ev('S.alerts.length');ev("S.given.nlp=new Date()");
 $('#chatIn')||w.showTab('chat');w.showTab('chat');$('#chatIn').value='Я решила, что не хочу больше жить';w.sendMsg();console.log('chat alert raised',ev('S.alerts.length')>before);
 login('111');console.log('doc tabs',$('#dtabs').textContent);w.dTab?w.dTab('messages'):0;
 const mb=[...w.document.querySelectorAll('#dtabs button')].find(b=>/Сообщ/.test(b.textContent));mb&&mb.click();console.log('doc chat visible',!!$('#dIn'));$('#dIn').value='Анна, позвоню через 10 минут';w.docSend();console.log('doc msg',ev('S.messages.at(-1).text'));
 w.selectPt('anna');const pc=$('#ptCard')?.textContent||body();console.log('card email',/anna\.k@example/.test(pc),'write btn',/Написать/.test(pc));
 login('444');console.log('therapist tabs',$('#dtabs').textContent);
 login('555');console.log('admin',!!$('#adminView')&&!$('#adminView').hidden);
}catch(e){console.log('EXC',e.stack)}console.log('errors',errs);process.exit(0)},400);
