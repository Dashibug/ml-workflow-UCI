# Версионирование данных с DVC

Продолжение HW-1: тот же датасет UCI Adult и те же модули подготовки данных, но теперь исходные и подготовленные данные — DVC-выходы.

## Пайплайн

```text
get_data [UCI → data/raw] → prepare_data [data/raw → train.csv / val.csv / test.csv / data_info.json]
```

DVC запускается **из корня** `ml-workflow-UCI`, а Python-модули выполняются в `HW-2`.

## Установка

```bash
cd ml-workflow-UCI
source .venv/bin/activate
python -m pip install -r HW-2/requirements-dev.txt
# В уже существующем Git-репозитории один раз:
dvc init
# Локальное хранилище вне репозитория:
mkdir -p ../ml-workflow-UCI-dvc-storage
dvc remote add -d local_storage ../ml-workflow-UCI-dvc-storage
```

Затем из корня:

```bash
dvc repro
dvc dag
dvc status
dvc push
```

`dvc repro` запускает **get_data** и **prepare_data**, создаёт `dvc.lock` и кэширует выходы.

## Версии

1. `configs/data.yaml`: `val_size: 0.20`; `dvc repro`; `dvc push`; коммит; Git-тег `data-v1`.
2. `configs/data.yaml`: `val_size: 0.25`; `dvc repro`; `dvc push`; коммит; Git-тег `data-v2`.
3. Восстановление тегов: `git switch --detach data-v1` → `dvc pull` → проверить `data_info.json`; повторить для `data-v2`. Вернуться в `main` командой `git switch main && dvc checkout`.

**Важно:** хранилище `../ml-workflow-UCI-dvc-storage` находится на твоём Mac, не на GitHub. Другому человеку потребуется доступ к этому хранилищу (или повторная загрузка открытых данных через `dvc repro`). Для совместной удалённой проверки нужен доступный облачный remote.

Отчёт со скриншотами: [`../reports/hw-2.md`](../reports/hw-2.md). Описание датасета: [`data/README.md`](data/README.md).
