const fs=require('fs');eval(fs.readFileSync('rm2.js','utf8')+';globalThis.RM=RM;globalThis.rmLoad=rmLoad;globalThis.rmProbs=rmProbs;');
globalThis.atob=s=>Buffer.from(s,'base64').toString('binary');
rmLoad(JSON.parse(fs.readFileSync(process.argv[2])));const T=JSON.parse(fs.readFileSync('parity_in.json'));const t0=Date.now();
const out=T.map(t=>rmProbs(t));console.log(JSON.stringify({out,ms:(Date.now()-t0)/T.length}));
