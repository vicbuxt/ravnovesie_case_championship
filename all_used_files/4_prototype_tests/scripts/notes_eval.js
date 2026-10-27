const fs=require('fs');const {JSDOM}=require('/tmp/claude-0/-home-claude/84909ad0-4cd4-5dec-b5af-f5ebecc6ef34/scratchpad/node_modules/jsdom');
const dom=new JSDOM(fs.readFileSync(process.argv[2],'utf8'),{runScripts:'dangerously',url:'https://x.test/'});const w=dom.window;w.scrollTo=()=>{};
const errs=[];w.addEventListener('error',e=>errs.push(e.message));
setTimeout(()=>{const set=JSON.parse(fs.readFileSync('/home/claude/testset/fresh_notes/fresh_notes.json'));const F={};const bad=[];const t0=Date.now();
 for(const n of set){const E=w.extractNote(n.text);const pm=[...new Set(E.meds.map(m=>{const d=w.findDrug(m);return d.inn||m.toLowerCase()}))].sort();
  const ok={age:String(E.age)===String(n.age),sex:E.sex===n.sex,icd:E.icd.includes(n.icd),meds:JSON.stringify(pm)===JSON.stringify(n.meds),preg:E.preg===n.preg,gfr:(E.gfr||'не указано')===n.gfr,epilepsy:E.epilepsy===n.epilepsy,liver:E.liver===n.liver};
  for(const k in ok)F[k]=(F[k]||0)+ok[k];const b=Object.keys(ok).filter(k=>!ok[k]);if(b.length)bad.push(n.id+' '+b.join(',')+' | '+JSON.stringify({age:E.age,sex:E.sex,meds:pm,preg:E.preg,ep:E.epilepsy,liv:E.liver,gfr:E.gfr}))}
 console.log('fresh notes',set.length,JSON.stringify(F),'ms/note',(Date.now()-t0)/set.length);if(process.argv[3])bad.forEach(x=>console.log(' ',x));console.log('errors',errs);process.exit(0)},300);
