const fs=require('fs');const {JSDOM}=require('jsdom');
const dom=new JSDOM(fs.readFileSync('/home/claude/v9/final.html','utf8'),{runScripts:'dangerously',url:'https://x.test/'});const w=dom.window;w.alert=()=>{};
setTimeout(()=>{const M={high:2,mid:1};const out={};
 const sets={selfid:JSON.parse(fs.readFileSync('fresh/selfid_test.json')),contrast:JSON.parse(fs.readFileSync('data2/contrast_clean.json'))};
 const csv=fs.readFileSync('/home/claude/testset/data/diary_entries.csv','utf8').replace(/^﻿/,'');
 const rows=[];let row=[],cell='',q=false;for(let i=0;i<csv.length;i++){const c=csv[i];if(q){if(c==='"'&&csv[i+1]==='"'){cell+='"';i++}else if(c==='"')q=false;else cell+=c}else if(c==='"')q=true;else if(c===','){row.push(cell);cell=''}else if(c==='\n'){row.push(cell);rows.push(row);row=[];cell=''}else if(c!=='\r')cell+=c}
 const h=rows.shift();const LM={'нет':0,'безнадёжность':1,'высокий':2};sets.independent=rows.filter(r=>r.length===h.length).map(r=>{const o=Object.fromEntries(h.map((k,i)=>[k,r[i]]));return {text:o.full_text,label:LM[o.risk_label],type:o.trap_type}});
 for(const [k,d] of Object.entries(sets)){const cm=[[0,0,0],[0,0,0],[0,0,0]];const by={};for(const x of d){const p=M[w.analyze(x.text)]??0;cm[x.label][p]++;const t=x.type||'';by[t]=by[t]||[0,0];by[t][0]++;if(p===x.label)by[t][1]++}
  const s=a=>a.reduce((x,y)=>x+y,0);out[k]={cm,high_recall:cm[2][2]/s(cm[2]),any_recall:(cm[1][1]+cm[1][2]+cm[2][1]+cm[2][2])/(s(cm[1])+s(cm[2])),false_alarm:(cm[0][1]+cm[0][2])/s(cm[0]),accuracy:(cm[0][0]+cm[1][1]+cm[2][2])/d.length,by}}
 fs.writeFileSync('baseline.json',JSON.stringify(out,null,1));for(const [k,v] of Object.entries(out))console.log(k,'acc',v.accuracy.toFixed(3),'highRec',v.high_recall.toFixed(3),'anyRec',v.any_recall.toFixed(3),'FA',v.false_alarm.toFixed(3));process.exit(0)},300);
