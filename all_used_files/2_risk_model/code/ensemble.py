import sys; sys.path.insert(0, '/home/claude/model')
import json, base64, glob, numpy as np, torch, torch.nn.functional as F
from train2 import Net, chunks, batch, CFG
def load(fn):
    J = json.load(open(fn)); m = Net(J['cfg'])
    m.load_state_dict({k: torch.tensor(np.frombuffer(base64.b64decode(v['b64']), dtype=np.int8).astype(np.float32).reshape(v['shape']) * v['scale']) for k, v in J['w'].items()}); m.eval(); return J, m
def eprobs(models, texts, bs=256):
    res = []
    with torch.no_grad():
        for i in range(0, len(texts), bs):
            part = texts[i:i + bs]; idx, flat = [], []
            for j, t in enumerate(part):
                for c in chunks(t): idx.append(j); flat.append(c)
            b = batch(flat); P = sum(F.softmax(m(*b), -1).numpy() for m in models) / len(models)
            agg = [None] * len(part)
            for j, p in zip(idx, P): agg[j] = p if agg[j] is None else np.maximum(agg[j], p)
            res.extend([a.tolist() for a in agg])
    return res
if __name__ == '__main__':
    fns = sys.argv[1:]; JM = [load(f) for f in fns]; models = [m for _, m in JM]
    va = json.load(open('/home/claude/model/data2/val.json')); P = np.array(eprobs(models, [x['text'] for x in va])); y = np.array([x['label'] for x in va])
    TH = .5
    for th in np.arange(.05, .51, .01):
        if (P[y == 2, 2] >= th).mean() >= .985: TH = float(th)
    bt = None
    for tm in np.arange(.05, .9, .01):
        dec = np.where(P[:, 2] >= TH, 2, np.where(P[:, 1] >= tm, 1, 0))
        f = sum((((dec == c) & (y == c)).sum() * 2) / max(1, (dec == c).sum() + (y == c).sum()) for c in range(3)) / 3
        if bt is None or f > bt[0]: bt = (f, float(tm))
    TM = bt[1]; print('TH', round(TH, 2), 'TM', round(TM, 2))
    json.dump(dict(cfg=JM[0][0]['cfg'], TH=TH, TM=TM, models=[J['w'] for J, _ in JM]), open('/home/claude/model/risk_model_ens.json', 'w'))
