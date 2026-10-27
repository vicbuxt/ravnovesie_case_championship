## 1_prototype — сайт

ravnovesie_prototype.html — готовый сайт

source_w.html — исходник сайта без модели и аудио

integrate2.py — встраивает модель в сайт

add_audio.py — встраивает аудио в сайт

audio/breath.mp3 — «Дыхание 4–6»

audio/ground.mp3 — «Заземление 5-4-3-2-1»

audio/pmr.mp3 — «Мышечное расслабление»

audio/small.mp3 — «Одно маленькое дело»

audio/kind.mp3 — «Доброе отношение к себе»

audio/scan.mp3 — «Сканирование тела»

audio/leaves.mp3 — «Листья на ручье»

## 2_risk_model — модель риска

code/gen2.py — генератор обучающих данных

code/train2.py — архитектура трансформера и обучение

code/ensemble.py — сборка ансамбля, подбор порогов

code/eval2.py — оценка на тестовых наборах

code/rm2.js — запуск модели в браузере

code/parity.js — сверка ответов JS и PyTorch

code/parity_in.json — фразы для этой сверки

code/lex.py — сборка словаря маркеров

code/lex.json — словарь маркеров риска

code/baseline.js — оценка словаря (база для сравнения)

code/build_demo2.py — сборка демо-страницы

weights/risk_model_ens.json — итоговые веса, встроенные в сайт

weights/model2_s1.pt — модель 1 ансамбля (PyTorch)

weights/model2_s2.pt — модель 2 ансамбля

weights/model2_s3.pt — модель 3 ансамбля

logs/train3_s1.log … train3_s3.log — логи обучения трёх моделей

results/metrics2.json — метрики модели по наборам

results/errors2.json — все ошибки модели

results/baseline.json — метрики словаря

risk_model_demo.html — демо: ввести текст → оценка модели

## 3_data — данные

train/train.json — обучающая выборка, 79 963 записи

train/val.json — проверочная выборка, по ней подбирались пороги

test/fresh_test.json — главный тест, 198 записей

test/fresh_test.py — исходник этого теста

test/selfid_test.json — тест «и я тоже», 30 записей

test/selfid.py — исходник этого теста

test/contrast_clean.json — одна фраза в 5 контекстах, 100 записей

test/test_synth.json — отложенная синтетика, 4 999 записей

test/fresh_notes.json — 15 новых выписок с эталоном

test/make.py — исходник новых выписок

test/testset/README.md — правила разметки первого набора

test/testset/data/patients.csv — 60 пациентов с эталонными решениями

test/testset/data/diary_entries.csv — 436 записей дневника с разметкой

test/testset/data/discharge_notes.csv — 30 выписок с эталонными полями

test/testset/data/notes_txt/N001–N030.txt — те же выписки текстом

test/testset/testset_ravnovesie.xlsx — весь первый набор в Excel

## 4_prototype_tests — проверка сайта

evaluate_prototype.js — прогон сайта по первому набору

results/results.md — отчёт прогона

results/results.json — тот же отчёт в JSON

results/diary_errors.csv — ошибки на записях дневника

results/tech_metrics.json — скорость, нагрузка, фазз-тест

results/ergo.json — вёрстка на 6 разрешениях экрана

scripts/run10.js — сквозной тест всех ролей

scripts/notes_eval.js — проверка 15 новых выписок

scripts/metrics.py — замер скорости и нагрузки

scripts/ergo.py — проверка вёрстки

scripts/tour.py — проход по интерфейсу

scripts/audiotest.py — проверка воспроизведения аудио
