s = open('/home/claude/v10/w.html').read()
RMJ = open('/home/claude/model/risk_model_ens.json').read(); RMJS = open('/home/claude/model/rm2.js').read()
i = s.index('const RISK_HIGH='); j = s.index('\n', s.index('function analyze(t){', i)) + 1
assert s[i:j].count('\n') <= 4
s = s[:i] + "function riskPct(t){const p=rmProbs(t);return p?Math.round(p[2]*100):0}\nfunction hopePct(t){const p=rmProbs(t);return p?Math.round(p[1]*100):0}\n" + s[j:]
R = [("'Дневник: маркеры суицидального риска — «'", "'Дневник: модель оценила риск как высокий ('+riskPct(text)+'%) — «'"),
     ("'Дневник: маркеры безнадёжности — «'", "'Дневник: модель отметила безнадёжность ('+hopePct(text)+'%) — «'"),
     ("'Чат: маркеры суицидального риска — «'", "'Чат: модель оценила риск как высокий ('+riskPct(v)+'%) — «'"),
     (", маркеры риска в дневнике'", ", модель отметила высокий риск в дневнике'")]
for a, b in R:
    assert s.count(a) == 1, a; s = s.replace(a, b)
k = s.index('<script>\n')
s = s[:k] + '<script id="riskModel" type="application/json">' + RMJ + '</script>\n<script>\n' + RMJS + "\nrmLoad(JSON.parse(document.getElementById('riskModel').textContent));\n</script>\n" + s[k:]
open('/home/claude/v10/final.html', 'w').write(s); print('ok', len(s.encode()) // 1024, 'KB')
