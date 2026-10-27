import pymorphy3, random, json, time, re
m = pymorphy3.MorphAnalyzer(); R = random.Random(5); t = time.time()
BAD = re.compile(r'смер|умер|умир|жив|жизн|жить|суиц|самоуб|убий|убив|убит|убь|реза|резн|порез|режу|кров|таблет|петл|верёв|верев|повес|вешат|стрел|прыг|крыш|мост|яд|травит|отрав|гроб|могил|похорон|кладб|труп|покойн|мёрт|мерт|гибе|гибн|погиб|ненав|безнад|бессмысл|пуст|никчём|ничтож|обуз|прощ|завещ|исчез|болезн|рак|боль|бол|тоск|уныл|отчая|страда|мучит|муч|депресс|плак|слёз|слез|горе|беда|ужас|страх|страш|тревог|паник|одино|ненуж|выход|конец|конч|навсегд|навек|последн|секс|наркот|алког|спирт|водк|пьян|оруж|нож|бомб|войн|насил|бить|избив')
pools = {'NOUN': [], 'ADJF': [], 'INFN': [], 'ADVB': []}
seen = set()
for i, (w, tag, nf, pid, idx) in enumerate(m.dictionary.iter_known_words('')):
    if i % 7: continue
    if nf in seen or len(nf) < 3 or not nf.isalpha() or BAD.search(nf): continue
    if any(x in tag for x in ('Name', 'Surn', 'Patr', 'Geox', 'Orgn', 'Abbr', 'Infr', 'Slng', 'Arch', 'Erro', 'Dist', 'Init', 'Trad')): continue
    p = m.parse(nf)[0]
    if p.normal_form != nf or p.score < .5: continue
    pos = p.tag.POS
    if pos in pools: pools[pos].append(nf); seen.add(nf)
    if i > 6_000_000: break
print({k: len(v) for k, v in pools.items()}, round(time.time() - t), 's')
for k in pools: R.shuffle(pools[k]); pools[k] = pools[k][:6000]
json.dump(pools, open('lex.json', 'w'), ensure_ascii=False)
print({k: v[:12] for k, v in pools.items()})
