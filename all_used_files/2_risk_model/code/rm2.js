/* ===== Модель распознавания риска в дневнике: словесный трансформер с хэш-n-граммами, работает в браузере ===== */
const RM={ready:false};
function rmLoad(J){RM.cfg=J.cfg;RM.TH=J.TH;RM.TM=J.TM;RM.models=(J.models||[J.w]).map(w=>{const o={};
  for(const [k,v] of Object.entries(w)){const b=atob(v.b64);const a=new Float32Array(b.length);for(let i=0;i<b.length;i++){let x=b.charCodeAt(i);if(x>127)x-=256;a[i]=x*v.scale}o[k]=a}return o});RM.ready=true}
function rmFnv(s){let h=2166136261;for(let i=0;i<s.length;i++){h^=s.charCodeAt(i);h=Math.imul(h,16777619)>>>0}return h}
function rmToks(t){return String(t).toLowerCase().replace(/ё/g,'е').match(/[а-яa-z0-9]+|[«»"'():;!?.,…—-]/g)||[]}
function rmChunks(t){const ws=rmToks(t),C=RM.cfg;if(ws.length<=C.maxt)return [ws];const out=[];let cur=[];
  for(const w of ws){cur.push(w);if(cur.length>=C.maxt||('.!?…'.includes(w)&&cur.length>C.maxt-16)){out.push(cur);cur=[]}}if(cur.length)out.push(cur);return out}
function rmLin(x,T,inD,W,b,outD){const y=new Float32Array(T*outD);for(let t=0;t<T;t++){const xo=t*inD,yo=t*outD;for(let o=0;o<outD;o++){let s=b[o];const wo=o*inD;for(let i=0;i<inD;i++)s+=x[xo+i]*W[wo+i];y[yo+o]=s}}return y}
function rmLN(x,T,D,g,b){const y=new Float32Array(T*D);for(let t=0;t<T;t++){const o=t*D;let m=0;for(let i=0;i<D;i++)m+=x[o+i];m/=D;let v=0;for(let i=0;i<D;i++){const d=x[o+i]-m;v+=d*d}v/=D;const r=1/Math.sqrt(v+1e-5);for(let i=0;i<D;i++)y[o+i]=(x[o+i]-m)*r*g[i]+b[i]}return y}
function rmForward(ws,W){const C=RM.cfg,D=C.d,H=C.heads,hd=D/H,T=ws.length;if(!T)return [1,0,0];
  const x=new Float32Array(T*D);
  for(let t=0;t<T;t++){const w=ws[t];const wid=1+rmFnv('w:'+w)%(C.bw-1);const g='<'+w+'>';const ng=[];
    for(const n of [3,4])for(let i=0;i+n<=g.length;i++)ng.push(1+rmFnv('n:'+g.slice(i,i+n))%(C.bn-1));const K=Math.min(ng.length,C.k);
    for(let i=0;i<D;i++){let s=0;for(let j=0;j<K;j++)s+=W['en.weight'][ng[j]*D+i];x[t*D+i]=W['ew.weight'][wid*D+i]+(K?s/K:0)+W['pos.weight'][t*D+i]}}
  for(let L=0;L<C.layers;L++){const p='blocks.'+L+'.';
    const h=rmLN(x,T,D,W[p+'ln1.weight'],W[p+'ln1.bias']);const qkv=rmLin(h,T,D,W[p+'qkv.weight'],W[p+'qkv.bias'],3*D);const y=new Float32Array(T*D);const sc=1/Math.sqrt(hd);const row=new Float32Array(T);
    for(let hh=0;hh<H;hh++){for(let i=0;i<T;i++){let mx=-1e30;for(let j=0;j<T;j++){let s=0;for(let d=0;d<hd;d++)s+=qkv[i*3*D+hh*hd+d]*qkv[j*3*D+D+hh*hd+d];s*=sc;row[j]=s;if(s>mx)mx=s}
      let z=0;for(let j=0;j<T;j++){row[j]=Math.exp(row[j]-mx);z+=row[j]}for(let d=0;d<hd;d++){let s=0;for(let j=0;j<T;j++)s+=row[j]*qkv[j*3*D+2*D+hh*hd+d];y[i*D+hh*hd+d]=s/z}}}
    const o=rmLin(y,T,D,W[p+'o.weight'],W[p+'o.bias'],D);for(let i=0;i<T*D;i++)x[i]+=o[i];
    const h2=rmLN(x,T,D,W[p+'ln2.weight'],W[p+'ln2.bias']);const f=rmLin(h2,T,D,W[p+'f1.weight'],W[p+'f1.bias'],C.ff);
    for(let i=0;i<f.length;i++){const v=f[i];f[i]=.5*v*(1+Math.tanh(.7978845608*(v+.044715*v*v*v)))}
    const f2=rmLin(f,T,C.ff,W[p+'f2.weight'],W[p+'f2.bias'],D);for(let i=0;i<T*D;i++)x[i]+=f2[i]}
  const xf=rmLN(x,T,D,W['lnf.weight'],W['lnf.bias']);const pool=new Float32Array(2*D);for(let i=0;i<D;i++)pool[D+i]=-1e4;
  for(let t=0;t<T;t++)for(let i=0;i<D;i++){const v=xf[t*D+i];pool[i]+=v/T;if(v>pool[D+i])pool[D+i]=v}
  const lg=rmLin(pool,1,2*D,W['head.weight'],W['head.bias'],3);const m=Math.max(...lg);const e=[...lg].map(v=>Math.exp(v-m));const z=e.reduce((a,b)=>a+b,0);return e.map(v=>v/z)}
function rmProbs(text){if(!RM.ready)return null;let agg=null;for(const c of rmChunks(text)){const ps=RM.models.map(W=>rmForward(c,W));const p=[0,1,2].map(i=>ps.reduce((a,q)=>a+q[i],0)/ps.length);agg=agg?agg.map((v,i)=>Math.max(v,p[i])):p}return agg||[1,0,0]}
function rmDecide(p){return p[2]>=RM.TH?'high':p[1]>=RM.TM?'mid':null}
function analyze(t){if(!t||!String(t).trim())return null;const p=rmProbs(t);return p?rmDecide(p):null}
