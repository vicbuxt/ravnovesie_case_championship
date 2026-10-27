import sys; sys.path.insert(0, "/home/claude/model")
import json, base64, csv, collections, sys
import numpy as np, torch
from train2 import Net, probs, CFG
import ensemble, os
FN = os.environ.get('MODEL', 'risk_model_ens.json')
J = json.load(open(FN)); WS = J.get('models') or [J['w']]
def mk(w):
    m = Net(J['cfg']); m.load_state_dict({k: torch.tensor(np.frombuffer(base64.b64decode(v['b64']), dtype=np.int8).astype(np.float32).reshape(v['shape']) * v['scale']) for k, v in w.items()}); m.eval(); return m
MS = [mk(w) for w in WS]; TH, TM = J['TH'], J['TM']
if os.environ.get('TH'): TH = float(os.environ['TH'])
if os.environ.get('TM'): TM = float(os.environ['TM'])
def probs(_m, texts): return ensemble.eprobs(MS, texts)
m = MS[0]
NAMES = ['нет', 'безнадёжность', 'высокий']
def dec(p): return 2 if p[2] >= TH else 1 if p[1] >= TM else 0
def report(name, data):
    P = probs(m, [x['text'] for x in data]); pr = [dec(p) for p in P]
    cm = np.zeros((3, 3), int)
    for x, p in zip(data, pr): cm[x['label'], p] += 1
    by = collections.defaultdict(lambda: [0, 0])
    for x, p in zip(data, pr): by[x['type']][0] += 1; by[x['type']][1] += int(p == x['label'])
    r = dict(name=name, n=len(data), cm=cm.tolist(), accuracy=float(np.trace(cm) / cm.sum()), high_recall=float(cm[2, 2] / max(1, cm[2].sum())),
             high_any_recall=float(cm[2, 1:].sum() / max(1, cm[2].sum())), any_recall=float(cm[1:, 1:].sum() / max(1, cm[1:].sum())),
             false_alarm=float(cm[0, 1:].sum() / max(1, cm[0].sum())), false_high=float(cm[0, 2] / max(1, cm[0].sum())), by={k: v for k, v in by.items()})
    errs = [dict(id=x.get('id', ''), expected=NAMES[x['label']], predicted=NAMES[p], type=x['type'], text=x['text'], p=[round(v, 3) for v in q]) for x, p, q in zip(data, pr, P) if p != x['label']]
    return r, errs
sets = {}
sets['fresh'] = ('Новый независимый набор (198 записей, написан до генератора)', json.load(open('fresh/fresh_test.json')))
rows = list(csv.DictReader(open('/home/claude/testset/data/diary_entries.csv', encoding='utf-8-sig'))); LM = {'нет': 0, 'безнадёжность': 1, 'высокий': 2}
sets['selfid'] = ('Чужие слова + «и я тоже» (30 записей)', json.load(open('fresh/selfid_test.json')))
sets['independent'] = ('Первый тестовый набор (436 записей)', [{'id': r['entry_id'], 'text': r['full_text'], 'label': LM[r['risk_label']], 'type': r['trap_type'] if r['trap_type'] != 'нет' else 'обычная запись'} for r in rows])
sets['contrast'] = ('Контрастный тест: одна фраза — разный контекст', json.load(open('data2/contrast_clean.json')))
sets['test_synth'] = ('Отложенная синтетика (новые формулировки)', json.load(open('data2/test_synth.json')))
OUT = {}; ERR = {}
for k, (nm, d) in sets.items():
    OUT[k], ERR[k] = report(nm, d)
    v = OUT[k]; print(f"\n== {nm} n={v['n']}\n acc {v['accuracy']:.3f} | высокий recall {v['high_recall']:.3f} (как любой риск {v['high_any_recall']:.3f}) | любой риск recall {v['any_recall']:.3f} | ложные тревоги {v['false_alarm']:.3f} (ложн. высокий {v['false_high']:.3f})")
    print(' cm', v['cm']); print(' по типам', {t: f'{a[1]}/{a[0]}' for t, a in v['by'].items()})
json.dump(dict(TH=TH, TM=TM, params=sum(p.numel() for p in m.parameters()), n_models=len(MS), results=OUT), open('metrics2.json', 'w'), ensure_ascii=False, indent=1)
json.dump(ERR, open('errors2.json', 'w'), ensure_ascii=False, indent=1)
if '-v' in sys.argv:
    for k in ('fresh', 'independent'):
        print('\nERR', k, len(ERR[k]))
        for e in ERR[k][:60]: print(' ', e['expected'], '->', e['predicted'], '|', e['type'], '|', e['p'], '|', e['text'][:120])
