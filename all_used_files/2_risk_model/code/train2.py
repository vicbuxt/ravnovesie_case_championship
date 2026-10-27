import json, re, math, time, os, base64, random, csv
import os
import numpy as np, torch, torch.nn as nn, torch.nn.functional as F
SEED = int(os.environ.get('SEED', 3)); torch.manual_seed(SEED); random.seed(SEED); torch.set_num_threads(2)
CFG = dict(d=64, heads=4, layers=2, ff=128, maxt=64, bw=4096, bn=8192, k=24)
TOK = re.compile(r'[а-яa-z0-9]+|[«»"\'():;!?.,…—-]')

def fnv(s):
    h = 2166136261
    for c in s: h = ((h ^ ord(c)) * 16777619) & 0xffffffff
    return h

def toks(t):
    return TOK.findall(t.lower().replace('ё', 'е'))

def enc_tok(w):
    wid = 1 + fnv('w:' + w) % (CFG['bw'] - 1)
    g = '<' + w + '>'
    ng = [1 + fnv('n:' + g[i:i + n]) % (CFG['bn'] - 1) for n in (3, 4) for i in range(len(g) - n + 1)][:CFG['k']]
    return wid, ng

def chunks(t):
    ws = toks(t)
    if len(ws) <= CFG['maxt']: return [ws]
    out, cur = [], []
    for w in ws:
        cur.append(w)
        if len(cur) >= CFG['maxt'] or (w in '.!?…' and len(cur) > CFG['maxt'] - 16):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def batch(list_of_toklists):
    T = max(1, max(len(x) for x in list_of_toklists)); B = len(list_of_toklists)
    W = torch.zeros(B, T, dtype=torch.long); N = torch.zeros(B, T, CFG['k'], dtype=torch.long); M = torch.zeros(B, T, dtype=torch.bool)
    for b, ws in enumerate(list_of_toklists):
        for t, w in enumerate(ws):
            wid, ng = enc_tok(w); W[b, t] = wid; N[b, t, :len(ng)] = torch.tensor(ng); M[b, t] = True
    return W, N, M

class Block(nn.Module):
    def __init__(s, c):
        super().__init__(); d = c['d']; s.h = c['heads']
        s.ln1 = nn.LayerNorm(d); s.qkv = nn.Linear(d, 3 * d); s.o = nn.Linear(d, d); s.ln2 = nn.LayerNorm(d); s.f1 = nn.Linear(d, c['ff']); s.f2 = nn.Linear(c['ff'], d); s.dr = nn.Dropout(.1)
    def forward(s, x, m):
        B, T, D = x.shape; hd = D // s.h
        q, k, v = s.qkv(s.ln1(x)).split(D, -1)
        q, k, v = [z.view(B, T, s.h, hd).transpose(1, 2) for z in (q, k, v)]
        a = (q @ k.transpose(-1, -2)) / math.sqrt(hd)
        a = a.masked_fill(~m[:, None, None, :], -1e9).softmax(-1)
        y = (a @ v).transpose(1, 2).reshape(B, T, D)
        x = x + s.dr(s.o(y))
        return x + s.dr(s.f2(F.gelu(s.f1(s.ln2(x)), approximate='tanh')))

class Net(nn.Module):
    def __init__(s, c):
        super().__init__(); d = c['d']
        s.ew = nn.Embedding(c['bw'], d); s.en = nn.Embedding(c['bn'], d, padding_idx=0); s.pos = nn.Embedding(c['maxt'], d)
        s.blocks = nn.ModuleList([Block(c) for _ in range(c['layers'])]); s.lnf = nn.LayerNorm(d); s.head = nn.Linear(2 * d, 3)
    def forward(s, W, N, M):
        cnt = (N > 0).sum(-1, keepdim=True).clamp(min=1)
        x = s.ew(W) + s.en(N).sum(2) / cnt + s.pos(torch.arange(W.shape[1]))[None]
        for b in s.blocks: x = b(x, M)
        x = s.lnf(x); mf = M[..., None].float()
        mean = (x * mf).sum(1) / mf.sum(1).clamp(min=1); mx = x.masked_fill(~M[..., None], -1e4).max(1).values
        return s.head(torch.cat([mean, mx], -1))

def probs(m, texts, bs=256):
    m.eval(); res = []
    with torch.no_grad():
        for i in range(0, len(texts), bs):
            part = texts[i:i + bs]; idx, flat = [], []
            for j, t in enumerate(part):
                for c in chunks(t): idx.append(j); flat.append(c)
            P = F.softmax(m(*batch(flat)), -1).numpy()
            agg = np.zeros((len(part), 3)); agg[:, 0] = 1
            first = [True] * len(part)
            for j, p in zip(idx, P):
                if first[j]: agg[j] = p; first[j] = False
                else: agg[j] = np.maximum(agg[j], p) if True else p
            res.extend(agg.tolist())
    return res

if __name__ == '__main__':
    D = '/home/claude/model/data2'
    tr = json.load(open(f'{D}/train.json')); va = json.load(open(f'{D}/val.json'))
    pre = [(toks(x['text'])[:CFG['maxt']], x['label']) for x in tr]
    m = Net(CFG); print('params', sum(p.numel() for p in m.parameters()))
    EP = int(os.environ.get('EP', 8)); BS = 128; steps = EP * math.ceil(len(pre) / BS)
    opt = torch.optim.AdamW(m.parameters(), 2e-3, weight_decay=.01); sch = torch.optim.lr_scheduler.OneCycleLR(opt, 2e-3, total_steps=steps, pct_start=.1)
    cw = torch.tensor([1., 1.5, 2.]); t0 = time.time()
    for ep in range(EP):
        m.train(); random.shuffle(pre); tot = 0
        for i in range(0, len(pre), BS):
            bt = pre[i:i + BS]
            tl = [[w for w in ws if random.random() > .05] or ws for ws, _ in bt]
            y = torch.tensor([l for _, l in bt])
            loss = F.cross_entropy(m(*batch(tl)), y, weight=cw, label_smoothing=.05)
            opt.zero_grad(); loss.backward(); nn.utils.clip_grad_norm_(m.parameters(), 1.); opt.step(); sch.step(); tot += loss.item() * len(bt)
        P = np.array(probs(m, [x['text'] for x in va])); y = np.array([x['label'] for x in va])
        pr = P.argmax(1); print(f'ep {ep + 1} loss {tot / len(pre):.3f} val acc {(pr == y).mean():.3f} high rec {(pr[y == 2] == 2).mean():.3f} {time.time() - t0:.0f}s', flush=True)
    P = np.array(probs(m, [x['text'] for x in va])); y = np.array([x['label'] for x in va])
    best = None
    for th in np.arange(.05, .9, .01):
        rec = (P[y == 2, 2] >= th).mean()
        if rec >= .97: best = th
    TH = float(best if best is not None else .3)
    bt = None
    for tm in np.arange(.05, .9, .01):
        dec = np.where(P[:, 2] >= TH, 2, np.where(P[:, 1] >= tm, 1, 0))
        f = sum((((dec == c) & (y == c)).sum() * 2) / max(1, (dec == c).sum() + (y == c).sum()) for c in range(3)) / 3
        if bt is None or f > bt[0]: bt = (f, tm)
    TM = float(bt[1]); print('thresholds high', round(TH, 2), 'hope', round(TM, 2))
    torch.save(m.state_dict(), f'/home/claude/model/model2_s{SEED}.pt')
    W = {}
    for k, v in m.state_dict().items():
        a = v.numpy().astype(np.float32); sc = float(np.abs(a).max() / 127) or 1e-8
        W[k] = dict(shape=list(a.shape), scale=sc, b64=base64.b64encode(np.clip(np.round(a / sc), -127, 127).astype(np.int8).tobytes()).decode())
    json.dump(dict(cfg=CFG, TH=TH, TM=TM, w=W), open(f'/home/claude/model/risk_model2_s{SEED}.json', 'w'))
    print('size json KB', os.path.getsize(f'/home/claude/model/risk_model2_s{SEED}.json') // 1024)
