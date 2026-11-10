# Воспроизводимый ML-проект

Цель: собрать ML-проект, который можно скачать из Git, установить зависимости и воспроизвести с помощью команд CLI без ручного запуска ячеек ноутбука.

## Постановка задачи
На открытом датасете UCI Adult (Census Income) решается бинарная классификация: предсказать, превышает ли годовой доход человека $50 000.
- Исходный датасет: 48 842 строки, 14 признаков.
- Основная метрика выбора модели: ROC-AUC на валидации.
- Дополнительные метрики: F1, accuracy, precision, recall, log-loss и confusion matrix.
- Два эксперимента: Logistic Regression (baseline) и HistGradientBoosting (experiment).

## Окружение и установка
Нужны Python 3.11–3.13, Git и интернет при первом скачивании датасета. Использованные версии Python-библиотек зафиксированы в requirements.txt и requirements-dev.txt.

macOS/Linux — команды выполняются из корня репозитория:
```bash
python3 -m venv .venv
source .venv/bin/activate
cd HW-1
python -m pip install -r requirements-dev.txt
```

Если окружение уже создано в корне репозитория, повторно создавать его не нужно: активируйте .venv, перейдите в HW-1 и запускайте команды оттуда.

Windows PowerShell — из корня репозитория:
```bash
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
cd HW-1
python -m pip install -r requirements-dev.txt
```

## Воспроизведение результатов
Запустите команды из папки HW-1 в указанном порядке:
```bash
python -m pytest -q
python -m src.prepare_data
python -m src.train --config configs/baseline.yaml
python -m src.train --config configs/experiment.yaml
python -m src.compare
```

После сравнения по validation ROC-AUC выберите лучший эксперимент. Для результатов этого проекта лучший — HistGradientBoosting. Оценку на отложенном тесте запускаем отдельно:
```bash
python -m src.evaluate --config configs/experiment.yaml
```

При недоступности UCI можно вручную скачать adult.data и adult.test в data/raw/, затем запустить python -m src.prepare_data --skip-download.

## Эксперименты и результаты

| Модель | Val ROC-AUC | Val F1 | Val Accuracy |
| --- | ---: | ---: | ---: |
| Logistic Regression | 0.9078 | 0.6734 | 0.8558 |
| **HistGradientBoosting** | **0.9292** | **0.7185** | **0.8749** |

HistGradientBoosting выиграл по validation ROC-AUC на 0.0214 (2.14 процентного пункта).

## Финальная оценка выбранной модели на тестовой выборке

| Метрика | Значение |
| --- | ---: |
| ROC-AUC | **0.925723** |
| F1 | 0.704783 |
| Accuracy | 0.871875 |
| Precision | 0.773292 |
| Recall | 0.647426 |
| Log loss | 0.279811 |
| Число строк | 16 281 |

## Источник данных
Becker, B. & Kohavi, R. (1996). Adult [Dataset]. UCI Machine Learning Repository. DOI: 10.24432/C5XW20. Лицензия: CC BY 4.0.