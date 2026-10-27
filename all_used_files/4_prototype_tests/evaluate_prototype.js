const fs = require('fs'), path = require('path');
const { JSDOM } = require('jsdom');
const HTML = process.argv[2] || 'ravnovesie_prototype.html';
const DATA = process.argv[3] || 'data';
const OUT = process.argv[4] || 'results';
fs.mkdirSync(OUT, { recursive: true });

function readCSV(f) {
  const t = fs.readFileSync(path.join(DATA, f), 'utf8').replace(/^﻿/, '');
  const rows = []; let row = [], cell = '', q = false;
  for (let i = 0; i < t.length; i++) {
    const c = t[i];
    if (q) { if (c === '"' && t[i + 1] === '"') { cell += '"'; i++ } else if (c === '"') q = false; else cell += c }
    else if (c === '"') q = true; else if (c === ',') { row.push(cell); cell = '' }
    else if (c === '\n') { row.push(cell); rows.push(row); row = []; cell = '' } else if (c !== '\r') cell += c;
  }
  if (cell || row.length) { row.push(cell); rows.push(row) }
  const h = rows.shift(); return rows.filter(r => r.length === h.length).map(r => Object.fromEntries(h.map((k, i) => [k, r[i]])));
}
const csvOut = (f, rows) => { if (!rows.length) return; const h = Object.keys(rows[0]); fs.writeFileSync(path.join(OUT, f), '﻿' + [h.join(','), ...rows.map(r => h.map(k => `"${String(r[k] ?? '').replace(/"/g, '""')}"`).join(','))].join('\n')) };
const pct = (a, b) => b ? (100 * a / b).toFixed(1) + '%' : '—';

const dom = new JSDOM(fs.readFileSync(HTML, 'utf8'), { runScripts: 'dangerously', pretendToBeVisual: true, url: 'https://local.test/' });
const w = dom.window; w.alert = () => {}; w.prompt = () => ''; w.confirm = () => true; w.scrollTo = () => {}; w.Element.prototype.scrollIntoView = function () {};

setTimeout(() => {
  const R = { generated: new Date().toISOString() }; const md = [];

  const diary = readCSV('diary_entries.csv');
  const MAP = { high: 'высокий', mid: 'безнадёжность' };
  const L = ['нет', 'безнадёжность', 'высокий'];
  const cm = Object.fromEntries(L.map(a => [a, Object.fromEntries(L.map(b => [b, 0]))]));
  const errs = [], byTrap = {};
  w.eval('S.given.nlp=new Date()');
  for (const x of diary) {
    const p = MAP[w.analyze(x.full_text)] || 'нет';
    cm[x.risk_label][p]++;
    const t = x.trap_type === 'нет' ? 'обычная запись' : x.trap_type; byTrap[t] = byTrap[t] || { n: 0, ok: 0 }; byTrap[t].n++; if (p === x.risk_label) byTrap[t].ok++;
    if (p !== x.risk_label) errs.push({ entry_id: x.entry_id, expected: x.risk_label, predicted: p, trap_type: t, text: x.full_text });
  }
  const nHigh = L.reduce((a, k) => a + cm['высокий'][k], 0), nHope = L.reduce((a, k) => a + cm['безнадёжность'][k], 0);
  const highFound = cm['высокий']['высокий'], highAny = cm['высокий']['высокий'] + cm['высокий']['безнадёжность'];
  const anyPos = nHigh + nHope, anyTP = highAny + cm['безнадёжность']['высокий'] + cm['безнадёжность']['безнадёжность'];
  const predAny = L.reduce((a, k) => a + cm[k]['высокий'] + cm[k]['безнадёжность'], 0);
  const neg = L.reduce((a, k) => a + cm['нет'][k], 0), fp = cm['нет']['высокий'] + cm['нет']['безнадёжность'];
  R.diary = { n: diary.length, confusion: cm, high_recall_exact: highFound / nHigh, high_recall_flagged_any: highAny / nHigh, any_risk_recall: anyTP / anyPos, any_risk_precision: anyTP / predAny, false_alarm_rate_on_no_risk: fp / neg, by_trap: byTrap };
  csvOut('diary_errors.csv', errs);
  md.push('## 1. Детектор риска в дневнике', '', `Записей: ${diary.length} (высокий риск — ${nHigh}, безнадёжность — ${nHope}, без риска — ${neg}).`, '',
    '| Ожидалось \\ Предсказано | нет | безнадёжность | высокий |', '|---|---|---|---|', ...L.map(a => `| ${a} | ${L.map(b => cm[a][b]).join(' | ')} |`), '',
    `- **Чувствительность к высокому риску** (найден именно как «высокий»): **${pct(highFound, nHigh)}**`,
    `- Высокий риск, отмеченный хотя бы каким-то сигналом: ${pct(highAny, nHigh)}`,
    `- Чувствительность к любому риску: ${pct(anyTP, anyPos)}; точность сигналов: ${pct(anyTP, predAny)}`,
    `- Ложные тревоги на записях без риска: ${pct(fp, neg)}`, '', '| Тип записи | Верно |', '|---|---|',
    ...Object.entries(byTrap).sort((a, b) => a[1].ok / a[1].n - b[1].ok / b[1].n).map(([k, v]) => `| ${k} | ${v.ok} из ${v.n} (${pct(v.ok, v.n)}) |`), '',
    'Пропущенные записи с высоким риском:', ...errs.filter(e => e.expected === 'высокий' && e.predicted !== 'высокий').map(e => `- ${e.entry_id} → ${e.predicted}: «${e.text}»`), '');

  const notes = readCSV('discharge_notes.csv');
  const F = { age: 0, sex: 0, icd10_main: 0, meds: 0, pregnancy: 0, gfr: 0, epilepsy: 0, liver: 0 }; const nerr = [];
  for (const n of notes) {
    w.openExtract(); w.document.querySelector('#exIn').value = n.text; w.runExtract(); const E = w.eval('EXTRACTED'); w.closeModal();
    const gtMeds = n.gt_meds_inn === '—' ? [] : n.gt_meds_inn.split('; ').map(s => s.trim()).sort();
    const prMeds = [...new Set((E.meds || []).map(m => { const d = w.findDrug(m); return d.inn || m.toLowerCase() }))].sort();
    const ok = {
      age: String(E.age) === n.gt_age, sex: E.sex === n.gt_sex, icd10_main: (E.icd || []).includes(n.gt_icd10_main),
      meds: JSON.stringify(gtMeds) === JSON.stringify(prMeds), pregnancy: (E.preg === 'да') === (n.gt_pregnancy === 'да'),
      gfr: (E.gfr || 'не указано') === n.gt_gfr, epilepsy: (E.epilepsy === 'да') === (n.gt_epilepsy === 'да'), liver: (E.liver === 'да') === (n.gt_liver_failure === 'да')
    };
    for (const k in ok) if (ok[k]) F[k]++;
    const bad = Object.keys(ok).filter(k => !ok[k]);
    if (bad.length) nerr.push({ note_id: n.note_id, style: n.style, wrong_fields: bad.join(' '), gt_meds: gtMeds.join('; '), pred_meds: prMeds.join('; '), gt_age: n.gt_age, pred_age: E.age, gt_sex: n.gt_sex, pred_sex: E.sex, gt_preg: n.gt_pregnancy, pred_preg: E.preg });
  }
  R.notes = { n: notes.length, field_accuracy: Object.fromEntries(Object.entries(F).map(([k, v]) => [k, v / notes.length])) };
  csvOut('notes_errors.csv', nerr);
  const FL = { age: 'Возраст', sex: 'Пол', icd10_main: 'Основной код МКБ-10', meds: 'Список препаратов (полностью)', pregnancy: 'Беременность', gfr: 'СКФ', epilepsy: 'Эпилепсия', liver: 'Печёночная недостаточность' };
  md.push('## 2. Разбор выписок', '', `Выписок: ${notes.length}, 5 стилей оформления.`, '', '| Поле | Точность |', '|---|---|', ...Object.entries(F).map(([k, v]) => `| ${FL[k]} | ${v} из ${notes.length} (${pct(v, notes.length)}) |`), '');

  const pts = readCSV('patients.csv');
  const C = { decision: 0, contra: 0, routing: 0, vk: 0 }; const perr = [];
  const decOf = (A, meds) => A.contra.length ? 'противопоказан' : !A.ind.ok ? 'вне зарегистрированных показаний' : (A.caution.length || meds.some(m => ['caution', 'avoid'].includes(w.interAvi(m).lv))) ? 'возможен по инструкции, с осторожностью' : 'возможен по инструкции';
  for (const P of pts) {
    const meds = P.meds ? P.meds.split('; ') : [];
    const ser = (a, b, c, i9) => [a, b, c].filter(v => v !== '').map((v, i, arr) => ({ d: new Date(), s: +v, i9: i === arr.length - 1 ? +i9 : 0 }));
    const p = {
      id: 'eval_' + P.patient_id, name: P.patient_id, dx: `${P.icd10} ${P.diagnosis}`, weeks: +P.weeks_on_therapy, adh: P.adherence_pct ? +P.adherence_pct : 100, side: [], onAvi: P.on_aviandr === 'да',
      flags: P.diary_max_risk === 'высокий' ? [{ level: 'high', text: '', d: new Date() }] : P.diary_max_risk === 'безнадёжность' ? [{ level: 'mid', text: '', d: new Date() }] : [],
      phq: ser(P.phq9_w0, P.phq9_w4, P.phq9_w8, P.phq9_item9_last), gad: ser(P.gad7_w0, P.gad7_w4, P.gad7_w8, 0),
      intake: { age: +P.age, sex: P.sex, pregnancy: P.pregnancy, lactation: P.lactation, planning: P.planning_pregnancy, medlist: meds, maoi2w: P.maoi_last_2w, allergy: P.allergy, epilepsy: P.epilepsy, brain: P.brain_organic, liver: P.liver_failure,
        kidney: P.gfr && +P.gfr < 60 ? 'да' : 'нет', gfr: P.gfr, cvd: P.cvd, endocrine: P.endocrine, alcohol: P.alcohol, subst: P.substance, lactose: P.lactose_intolerance, driving: P.drives, bipolar: P.bipolar_self_or_family, suicideHistory: P.suicide_attempt_history, prevEpisodes: 'нет' }
    };
    const A = w.aviCheck(p), r = w.routing(p);
    const dec = decOf(A, meds), route = r.m.length ? 'обязательно' : r.w.length ? 'желательно' : 'не требуется';
    const vk = A.caution.some(c => /1094н/.test(c)) ? 'да' : 'нет';
    const contraOk = (A.contra.length > 0) === (P.exp_aviandr_contraindications !== '—');
    const ok = { decision: dec === P.exp_aviandr_decision, contra: contraOk, routing: route === P.exp_psychiatrist_referral, vk: vk === P.exp_vk_required_5plus_meds };
    for (const k in ok) if (ok[k]) C[k]++;
    if (Object.values(ok).some(v => !v)) perr.push({ patient_id: P.patient_id, archetype: P.archetype, exp_decision: P.exp_aviandr_decision, pred_decision: dec, exp_contra: P.exp_aviandr_contraindications, pred_contra: A.contra.join('; ') || '—', exp_routing: P.exp_psychiatrist_referral, pred_routing: route, exp_reasons: P.exp_referral_reasons, pred_reasons: [...r.m, ...r.w].join(' | '), exp_vk: P.exp_vk_required_5plus_meds, pred_vk: vk });
  }
  R.rules = { n: pts.length, accuracy: Object.fromEntries(Object.entries(C).map(([k, v]) => [k, v / pts.length])) };
  csvOut('rules_errors.csv', perr);
  md.push('## 3. Правила: Авиандр и маршрутизация', '', `Профилей: ${pts.length}.`, '', '| Проверка | Совпало с эталоном |', '|---|---|',
    `| Решение по Авиандру (противопоказан / вне показаний / с осторожностью / можно) | ${C.decision} из ${pts.length} (${pct(C.decision, pts.length)}) |`,
    `| Наличие противопоказаний | ${C.contra} из ${pts.length} (${pct(C.contra, pts.length)}) |`,
    `| Направление к психиатру (обязательно / желательно / не требуется) | ${C.routing} из ${pts.length} (${pct(C.routing, pts.length)}) |`,
    `| Врачебная комиссия при ≥ 5 препаратах | ${C.vk} из ${pts.length} (${pct(C.vk, pts.length)}) |`, '',
    'Расхождения:', ...perr.map(e => `- ${e.patient_id} (${e.archetype}): ` + [e.exp_decision !== e.pred_decision ? `решение ${e.pred_decision} вместо «${e.exp_decision}»` : '', e.exp_routing !== e.pred_routing ? `направление «${e.pred_routing}» вместо «${e.exp_routing}» (эталон: ${e.exp_reasons})` : '', e.exp_vk !== e.pred_vk ? `ВК ${e.pred_vk} вместо ${e.exp_vk}` : ''].filter(Boolean).join('; ')), '');

  fs.writeFileSync(path.join(OUT, 'results.json'), JSON.stringify(R, null, 2));
  fs.writeFileSync(path.join(OUT, 'results.md'), '# Результаты прототипа на синтетическом наборе\n\n' + md.join('\n'));
  console.log(md.join('\n'));
  process.exit(0);
}, 400);
