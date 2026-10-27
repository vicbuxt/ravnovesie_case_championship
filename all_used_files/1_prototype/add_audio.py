import base64,json,sys
p=sys.argv[1];s=open(p,encoding='utf-8').read()
d={k:base64.b64encode(open(f'/home/claude/audio/{k}.mp3','rb').read()).decode() for k in ['breath','ground','pmr','small','kind','scan','leaves']}
tag='<script id="techAudio" type="application/json">'+json.dumps(d)+'</script>\n'
i=s.index('<script id="riskModel"')
s=s[:i]+tag+s[i:]
open(p,'w',encoding='utf-8').write(s)
