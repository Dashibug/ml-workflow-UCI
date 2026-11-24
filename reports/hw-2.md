# Отчёт по HW-2 — Версионирование данных с DVC

## Что сделано

- На основе проекта HW-1 подготовлена папка `HW-2`.
- Определён DVC DAG: `get_data → prepare_data`.
- Исходные файлы UCI Adult проверяются по SHA256 и отслеживаются DVC.
- Подготовленные данные (`train.csv`, `val.csv`, `test.csv`, `data_info.json`) сохраняются как DVC output.
- Настроен локальный remote за пределами Git-репозитория (адрес без секретов).
- Созданы две версии с Git-тегами `data-v1` и `data-v2` (заполнить после выполнения).

## Версии данных

| Git-тег | Доля валидации | Train | Validation | Test | SHA256 `train.csv` |
|---|---:|---:|---:|---:|---|
| `data-v1` | 20% | 26 048 | 6 513 | 16 281 | **Вставить вывод `shasum -a 256`** |
| `data-v2` | 25% | 24 420 | 8 141 | 16 281 | **Вставить вывод `shasum -a 256`** |

## Команды проверки

```bash
dvc dag
dvc remote list
dvc status
git tag --list 'data-v*'

# Для каждого тега:
git switch --detach data-v1
dvc pull
cat HW-2/data/processed/data_info.json
shasum -a 256 HW-2/data/processed/train.csv

git switch --detach data-v2
dvc pull
cat HW-2/data/processed/data_info.json
shasum -a 256 HW-2/data/processed/train.csv

# Возвращаемся к текущей версии
git switch main
dvc checkout
```

## Демонстрация восстановления из remote

Для текущей версии после `dvc push`:

```bash
rm -rf HW-2/data/raw HW-2/data/processed
dvc pull
dvc status
```

Ожидаемый результат: отсутствующие raw и processed файлы восстанавливаются и `dvc status` сообщает, что данные актуальны. **Выполнить и вставить фактический результат.**

## Скриншоты (вставить 2–4 штуки)

**1. DAG:** `dvc dag`.

<!-- ![DVC DAG](screenshots/hw-2/01-dag.png) -->

**2. Remote и статус:** `dvc remote list` + `dvc status`.

<!-- ![DVC remote and status](screenshots/hw-2/02-remote-status.png) -->

**3. Восстановление data-v1:** результаты `data_info.json` и SHA256.

<!-- ![Restored data-v1](screenshots/hw-2/03-data-v1.png) -->

**4. Восстановление data-v2 и проверка `dvc pull`.**

<!-- ![Restored data-v2](screenshots/hw-2/04-data-v2.png) -->

## Вывод

_Добавить после реальной проверки_: DVC позволил хранить версии больших CSV вне Git, а в Git фиксировать конфигурации, зависимости, контрольные суммы и набор данных, соответствующий каждому тегу.
