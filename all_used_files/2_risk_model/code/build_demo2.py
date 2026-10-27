import json, html
M = json.load(open('metrics2.json')); B = json.load(open('baseline.json')); RMJ = open('risk_model_ens.json').read(); RMJS = open('rm2.js').read()
co = json.load(open('data2/contrast_clean.json'))
cores = []
for x in co:
    if x['core'] not in cores: cores.append(x['core'])
demo = [x for x in co if x['core'] in [cores[0], cores[2], cores[6]]]
R = M['results']; pct = lambda v: f'{100*v:.1f}%'.replace('.', ',')
n_train = len(json.load(open('data2/train.json')))
def row(name, k):
    m, b = R[k], B[k]
    return f'<tr><td>{name}</td><td>{pct(b["high_recall"])}</td><td><b>{pct(m["high_recall"])}</b></td><td>{pct(b["false_alarm"])}</td><td><b>{pct(m["false_alarm"])}</b></td><td>{pct(b["accuracy"])}</td><td><b>{pct(m["accuracy"])}</b></td></tr>'
cm = R['fresh']['cm']; L = ['нет', 'безнадёжность', 'высокий']
cm_html = '<table class="cm"><tr><th>Разметка \\ Модель</th>' + ''.join(f'<th>{l}</th>' for l in L) + '</tr>' + ''.join('<tr><th>' + L[i] + '</th>' + ''.join(f'<td class="{"d" if i==j else ("bad" if (i>j) else "fa") if cm[i][j] else ""}">{cm[i][j]}</td>' for j in range(3)) + '</tr>' for i in range(3)) + '</table>'
TYPES0 = {'обычная запись': 'обычные записи', 'indirect': 'косвенные формулировки', 'idiom': 'идиомы («умираю от скуки»)', 'negation': 'отрицание («мыслей о смерти нет»)', 'third_party': 'о другом человеке',
         'media': 'фильм, статья, учёба', 'past': 'в прошлом', 'sarcasm': 'ирония', 'slang': 'сленг', 'typo': 'опечатки'}
GR = {'Высокий риск — о себе': ['прямо', 'обуза', 'о себе с оговоркой', 'цитата о себе', 'на фоне позитива', 'длинная/высокий'], 'Высокий риск — план и подготовка': ['план'], 'Высокий риск — самоповреждение': ['самоповреждение'],
      'Высокий риск — косвенно': ['косвенно'], 'Высокий риск — сленг и опечатки': ['сленг/высокий', 'опечатки/высокий'], 'Безнадёжность': ['будущее', 'ценность', 'смысл', 'ангедония', 'лечение', 'беспомощность', 'одиночество', 'сленг/безн', 'опечатки/безн', 'длинная/безн'],
      'Без риска — обычные записи, тревога, грусть, позитив': ['обычная', 'позитив', 'тревога', 'грусть', 'длинная/нет'], 'Без риска — отрицание («мыслей о смерти нет»)': ['отрицание'], 'Без риска — о другом человеке': ['другой человек'],
      'Без риска — фильм, книга, учёба': ['фильм/книга', 'учёба/работа'], 'Без риска — в прошлом, сейчас нет': ['прошлое'], 'Без риска — идиомы и ирония («умираю от скуки»)': ['идиома', 'сарказм']}
import collections
FR = json.load(open('fresh/fresh_test.json')); ER = {e['text'] for e in json.load(open('errors2.json'))['fresh']}
import subprocess
def key(x):
    t = x['type']
    if t in ('длинная', 'сленг', 'опечатки'): t += '/' + ['нет', 'безн', 'высокий'][x['label']]
    return t
agg = collections.OrderedDict((g, [0, 0, 0]) for g in GR)
BD = json.load(open('fresh_base_preds.json'))
for x in FR:
    for g, ts in GR.items():
        if key(x) in ts: agg[g][0] += 1; agg[g][1] += int(x['text'] not in ER); agg[g][2] += int(BD[x['id']] == x['label'])
bars = ''.join(f'<div class="bar"><span class="bl">{g} <span class="muted">· {v[0]} зап.</span></span><span class="track"><i class="old" style="width:{100*v[2]/v[0]:.0f}%"></i><i class="new" style="width:{100*v[1]/v[0]:.0f}%"></i></span><span class="bv">{pct(v[1]/v[0])}</span></div>' for g, v in agg.items() if v[0])
EX = ["Мне больше не хочется жить", "Сестра сказала, что ей не хочется жить. Я её обняла и мы поехали к врачу", "Сестра сказала, что ей не хочется жить. Я её обняла, но думала о том же, что и она", "В сериале героиня повторяла: «мне не хочется жить»", "Три года назад мне не хотелось жить. Сейчас этого нет, лечение помогло",
      "Мыслей о смерти нет, просто очень устала", "Умираю, как хочу в отпуск", "Опять всех подвела. Ничего не изменится", "Поймала себя на мысли, что всем будет лучше без меня", "Друзья съездили на море без меня, обидно", "не хачу жыть", "Сегодня был хороший день, погуляли с подругой"]
M_TH=f"{json.load(open('risk_model_ens.json'))['TH']:.2f}".replace('.',',');M_TM=f"{json.load(open('risk_model_ens.json'))['TM']:.2f}".replace('.',',')
page = f'''<!doctype html><html lang="ru"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Модель риска в дневнике</title>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@300;400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{{--bg:#FBF8F4;--paper:#fff;--ink:#1E1A22;--muted:#6E6674;--line:#ECE2F0;--lilac:#EECDF7;--lilac2:#F7EBFB;--deep:#A874BF;--ok:#3C845D;--okBg:#E5F2EA;--must:#B5362A;--mustBg:#FCEAE7;--want:#A86E0C;--wantBg:#FDF2DC;--old:#D8CDE0}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#17141B;--paper:#211D26;--ink:#F2EEF5;--muted:#A99FB0;--line:#342E3B;--lilac:#4A3657;--lilac2:#2C2433;--deep:#C9A3DC;--ok:#79C59A;--okBg:#1F3328;--must:#F08878;--mustBg:#3A2220;--want:#E2B260;--wantBg:#3A2F1C;--old:#4A4152}}}}
:root[data-theme="dark"]{{--bg:#17141B;--paper:#211D26;--ink:#F2EEF5;--muted:#A99FB0;--line:#342E3B;--lilac:#4A3657;--lilac2:#2C2433;--deep:#C9A3DC;--ok:#79C59A;--okBg:#1F3328;--must:#F08878;--mustBg:#3A2220;--want:#E2B260;--wantBg:#3A2F1C;--old:#4A4152}}
*{{box-sizing:border-box}}body{{margin:0;font-family:Manrope,system-ui,sans-serif;background:var(--bg);color:var(--ink);font-size:15px;line-height:1.5}}
.hero{{background:linear-gradient(160deg,#7C9BCB 0%,#A8A9DD 55%,#D3BDEE 100%);color:#fff;padding:44px 20px 64px;text-align:center}}
.hero h1{{font-size:40px;font-weight:300;margin:6px 0 10px;color:#F6E2FC}}.hero p{{max-width:640px;margin:0 auto;opacity:.95}}.kick{{font-size:12px;letter-spacing:.2em;text-transform:uppercase;opacity:.85}}
.wrap{{max-width:1040px;margin:-36px auto 0;padding:0 16px 60px;position:relative}}
.card{{background:var(--paper);border:1px solid var(--line);border-radius:22px;padding:22px;margin-bottom:18px}}
h2{{font-size:22px;margin:0 0 6px}}h3{{margin:0 0 6px}}.muted{{color:var(--muted)}}.small{{font-size:13px}}
.tiles{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:18px}}.tile{{background:var(--paper);border:1px solid var(--line);border-radius:20px;padding:18px}}
.tile .n{{font-size:34px;font-weight:300;line-height:1.1}}.tile .was{{font-size:13px;color:var(--muted)}}
textarea{{width:100%;min-height:90px;border:1px solid var(--line);border-radius:14px;padding:12px;font:inherit;font-size:16px;background:var(--paper);color:var(--ink);resize:vertical}}
.chips{{display:flex;flex-wrap:wrap;gap:6px;margin:10px 0}}.chips button{{border:1px solid var(--line);background:var(--paper);color:var(--ink);border-radius:999px;padding:6px 12px;font:inherit;font-size:13px;cursor:pointer}}.chips button:hover{{background:var(--lilac2)}}
.res{{display:grid;grid-template-columns:200px 1fr;gap:16px;align-items:center;margin-top:12px}}
.pill{{display:inline-block;padding:10px 16px;border-radius:14px;font-weight:700;text-align:center}}.p0{{background:var(--okBg);color:var(--ok)}}.p1{{background:var(--wantBg);color:var(--want)}}.p2{{background:var(--mustBg);color:var(--must)}}
.pb{{display:grid;grid-template-columns:120px 1fr 52px;gap:10px;align-items:center;font-size:13px;margin:4px 0}}.pt{{height:10px;border-radius:6px;background:var(--lilac2);overflow:hidden}}.pt i{{display:block;height:100%;border-radius:6px}}
table{{width:100%;border-collapse:collapse;font-size:14px}}th,td{{text-align:left;padding:9px 8px;border-bottom:1px solid var(--line)}}th{{color:var(--muted);font-weight:600}}
.ctx td:nth-child(3),.ctx td:nth-child(4){{white-space:nowrap}}.ok{{color:var(--ok);font-weight:700}}.no{{color:var(--must);font-weight:700}}
.cm td,.cm th{{text-align:center}}.cm td.d{{background:var(--okBg);font-weight:700}}.cm td.bad{{background:var(--mustBg)}}.cm td.fa{{background:var(--wantBg)}}
.bar{{display:grid;grid-template-columns:minmax(0,260px) 1fr 56px;gap:10px;align-items:center;margin:7px 0;font-size:13.5px}}.track{{position:relative;height:12px;border-radius:7px;background:var(--lilac2)}}.track i{{position:absolute;left:0;top:0;height:100%;border-radius:7px}}
.track i.old{{background:var(--old)}}.track i.new{{background:var(--deep);height:6px;top:3px}}.bv{{text-align:right;font-weight:700}}
.leg{{display:flex;gap:16px;font-size:12.5px;color:var(--muted);margin:6px 0 10px}}.leg span::before{{content:"";display:inline-block;width:12px;height:8px;border-radius:4px;margin-right:6px;vertical-align:middle}}.leg .o::before{{background:var(--old)}}.leg .n::before{{background:var(--deep)}}
.sc{{overflow-x:auto;max-width:100%}}.grid2>*{{min-width:0}}.cm{{font-size:13px}}.cm th,.cm td{{padding:7px 4px}}.grid2{{display:grid;grid-template-columns:1fr 1fr;gap:18px}}ul{{margin:6px 0 0 18px;padding:0}}li{{margin:4px 0}}
@media(max-width:720px){{.tiles,.grid2{{grid-template-columns:1fr}}.res{{grid-template-columns:1fr}}.hero h1{{font-size:28px}}.bar{{grid-template-columns:1fr 50px}}.bar .track{{grid-column:1/-1;order:3}}table{{font-size:13px}}.ctx td:nth-child(3),.ctx td:nth-child(4){{white-space:normal}}.ctx td:nth-child(2),.ctx th:nth-child(2){{display:none}}}}
</style></head><body>
<div class="hero"><div class="kick">Равновесие · дневник эмоций</div><h1>Модель риска в дневнике</h1><p>Компактный трансформер, который читает запись пациента и отличает настоящий сигнал риска от похожих слов в другом контексте. Работает прямо в браузере, без отправки текста на сервер.</p></div>
<div class="wrap">
<div class="tiles"><div class="tile"><div class="small muted">Находит записи с высоким риском</div><div class="n">{pct(R['fresh']['high_recall'])}</div><div class="was">словарь: {pct(B['fresh']['high_recall'])} · новый тестовый набор</div></div>
<div class="tile"><div class="small muted">Верно определяет уровень риска</div><div class="n">{pct(R['fresh']['accuracy'])}</div><div class="was">словарь: {pct(B['fresh']['accuracy'])} · 3 класса, 198 записей</div></div>
<div class="tile"><div class="small muted">Отличает контекст: одна фраза в 5 ситуациях</div><div class="n">{pct(R['contrast']['accuracy'])}</div><div class="was">словарь: {pct(B['contrast']['accuracy'])} · контрастный тест</div></div></div>

<div class="card"><h2>Попробуйте сами</h2><p class="muted small">Напишите запись, как в дневнике, или выберите пример.</p>
<textarea id="t" placeholder="Например: подруга сказала, что не хочет жить"></textarea>
<div class="chips">{''.join(f'<button onclick="setT(this.textContent)">{html.escape(e)}</button>' for e in EX)}</div>
<div class="res"><div><div class="small muted">Решение модели</div><div id="lab" class="pill p0">—</div></div><div id="bars"></div></div></div>

<div class="card"><h2>Одна фраза — разный контекст</h2><p class="muted small">Эти фразы модель не видела при обучении. Ответы ниже вычисляются моделью прямо сейчас, в вашем браузере.</p>
<div class="sc"><table class="ctx"><tr><th>Запись</th><th>Контекст</th><th>Ожидается</th><th>Модель</th></tr><tbody id="ctx"></tbody></table></div></div>

<div class="card"><h2>Сравнение со словарём</h2><p class="muted small">Словарь — прежний детектор из прототипа (поиск фраз-маркеров).</p>
<div class="sc"><table><tr><th>Набор</th><th>Высокий риск найден: словарь</th><th>модель</th><th>Ложные тревоги: словарь</th><th>модель</th><th>Точность: словарь</th><th>модель</th></tr>
{row('Новый тестовый набор, 198 записей', 'fresh')}{row('Первый тестовый набор, 436 записей', 'independent')}{row('Контрастный тест, 100 записей', 'contrast')}</table></div>
<p class="small muted" style="margin-top:10px">«Высокий риск найден» — доля записей с высоким риском, которые модель отметила как высокий. Ещё {pct(R['fresh']['high_any_recall']-R['fresh']['high_recall'])} таких записей модель отметила как безнадёжность — врач их тоже увидит.</p></div>

<div class="grid2"><div class="card"><h2>Ошибки на новом тестовом наборе</h2><p class="muted small">Зелёное — верно, красное — пропуск (модель недооценила риск), жёлтое — лишняя тревога.</p>{cm_html}</div>
<div class="card"><h2>По типам записей</h2><div class="leg"><span class="o">словарь</span><span class="n">модель</span></div>{bars}</div></div>

<div class="card"><h2>Техническое описание модели</h2><div class="grid2"><ul>
<li><b>Задача:</b> классификация записи на 3 класса — нет риска / безнадёжность / высокий риск.</li>
<li><b>Токенизация:</b> нижний регистр, ё→е, слова и знаки препинания. Каждое слово кодируется хэшем слова (4096 корзин) и хэшами до 24 символьных 3- и 4-грамм (8192 корзины), хэш FNV-1a.</li>
<li><b>Вход:</b> эмбеддинг слова + среднее эмбеддингов его n-грамм + позиционный эмбеддинг, размерность 64, до 64 слов.</li>
<li><b>Энкодер:</b> 2 блока трансформера (pre-LayerNorm), 4 головы внимания, полносвязный слой 128, GELU.</li>
<li><b>Выход:</b> среднее и максимум по словам → линейный слой → softmax по 3 классам.</li></ul>
<ul><li><b>Длинные записи:</b> режутся на куски до 64 слов, по каждому классу берётся максимум.</li>
<li><b>Ансамбль:</b> 3 модели с разной инициализацией, вероятности усредняются.</li>
<li><b>Правило решения:</b> «высокий риск», если P(высокий риск) ≥ {M_TH}; иначе «безнадёжность», если P(безнадёжность) ≥ {M_TM}.</li>
<li><b>Обучение:</b> {format(n_train,',').replace(',',' ')} записей, AdamW (lr 2·10⁻³), OneCycle, батч 128, 10 эпох, взвешенная кросс-энтропия со сглаживанием меток 0,05, dropout 0,1.</li>
<li><b>Размер и запуск:</b> {format(M['params'],',').replace(',',' ')} параметров в каждой модели, веса int8 — {len(RMJ)//1024} КБ; инференс на JavaScript в браузере.</li></ul></div></div>
</div>
<script id="riskModel" type="application/json">{RMJ}</script>
<script>
{RMJS}
rmLoad(JSON.parse(document.getElementById('riskModel').textContent));
const NM=['нет риска','безнадёжность','высокий риск'],COL=['var(--ok)','var(--want)','var(--must)'];
const esc=s=>String(s).replace(/[&<>"]/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}}[c]));
function lab(p){{const d=rmDecide(p);return d==='high'?2:d==='mid'?1:0}}
function upd(){{const t=document.getElementById('t').value;if(!t.trim()){{document.getElementById('lab').textContent='—';document.getElementById('lab').className='pill p0';document.getElementById('bars').innerHTML='';return}}
  const p=rmProbs(t),l=lab(p);const e=document.getElementById('lab');e.textContent=NM[l];e.className='pill p'+l;
  document.getElementById('bars').innerHTML=[2,1,0].map(i=>`<div class="pb"><span>${{NM[i]}}</span><span class="pt"><i style="width:${{(p[i]*100).toFixed(0)}}%;background:${{COL[i]}}"></i></span><span>${{(p[i]*100).toFixed(0)}}%</span></div>`).join('')}}
function setT(s){{document.getElementById('t').value=s;upd()}}
document.getElementById('t').addEventListener('input',upd);
const CTX={json.dumps([{'text':x['text'],'label':x['label'],'type':x['type']} for x in demo],ensure_ascii=False)};
document.getElementById('ctx').innerHTML=CTX.map(x=>{{const l=lab(rmProbs(x.text));return `<tr><td>${{esc(x.text)}}</td><td class="muted">${{x.type}}</td><td>${{NM[x.label]}}</td><td class="${{l===x.label?'ok':'no'}}">${{NM[l]}} ${{l===x.label?'✓':'✕'}}</td></tr>`}}).join('');
setT({json.dumps(EX[1],ensure_ascii=False)});
</script></body></html>'''
open('risk_model_demo.html', 'w').write(page); print('demo KB', len(page.encode()) // 1024)
