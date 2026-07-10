Ниже готовый `README.md` для публичного репозитория. Замени `YOUR_BOT_USERNAME` и ссылку на репозиторий, если нужно.

# 💌 SecretAsk

Telegram-бот для анонимных сообщений.

Пользователь создаёт личную ссылку, делится ею в профиле или сторис и получает анонимные сообщения от других людей. Premium-подписка позволяет узнать отправителя сообщения ✨

## ✨ Возможности

- 🔗 Персональная ссылка для анонимных сообщений
- 📩 Отправка и получение анонимных сообщений
- 💬 Ответы на полученные сообщения
- 🛡️ Базовая защита и модерация сообщений
- ✨ Premium-подписка навсегда
- 👤 Раскрытие отправителя для Premium-пользователей
- ⭐ Оплата через Telegram Stars
- ↩️ Возврат средств в течение ограниченного срока
- 🧹 Автоматическая очистка старых сообщений
- 🛠️ Админ-команды и ручной возврат платежей

## 🧰 Стек

- Python
- [aiogram 3](https://docs.aiogram.dev/)
- [Peewee ORM](https://docs.peewee-orm.com/)
- SQLite 3
- Telegram Bot API
- Telegram Stars
- [uv](https://docs.astral.sh/uv/) — управление Python и зависимостями

## 📁 Структура проекта

```text
SecretAsk/
├── bot/
│   ├── database/
│   │   ├── models.py
│   │   └── requests.py
│   ├── filters/
│   │   └── admin.py
│   ├── handlers/
│   ├── keyboards/
│   ├── utils/
│   ├── common/
│   │   └── time.py
│   ├── config.py
│   └── main.py
├── .env.example
├── pyproject.toml
├── uv.lock
└── README.md
```

## 🚀 Быстрый запуск

### 1. Клонируй репозиторий

```bash
git clone https://github.com/YOUR_GITHUB_USERNAME/SecretAsk.git
cd SecretAsk
```

### 2. Установи uv

#### Windows

В PowerShell:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

После установки перезапусти терминал.

#### macOS и Linux

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Проверь установку:

```bash
uv --version
```

`uv` умеет управлять версиями Python, зависимостями, виртуальными окружениями и запуском проекта. [Документация uv](https://docs.astral.sh/uv/)

### 3. Установи Python

Если нужной версии Python ещё нет:

```bash
uv python install 3.12
```

Проверить доступные интерпретаторы:

```bash
uv python list
```

> Рекомендуемая версия Python: **3.12+**.

### 4. Установи зависимости

```bash
uv sync
```

Команда создаст виртуальное окружение `.venv` и установит зависимости из `pyproject.toml` и `uv.lock`.

Если lock-файл уже есть и нужно установить строго зафиксированные версии:

```bash
uv sync --locked
```

### 5. Создай `.env`

Скопируй шаблон:

#### Windows PowerShell

```powershell
Copy-Item .env.example .env
```

#### macOS / Linux

```bash
cp .env.example .env
```

Если шаблона ещё нет, создай файл `.env` вручную:

```env
BOT_TOKEN=123456789:YOUR_TELEGRAM_BOT_TOKEN
ADMIN_IDS=123456789,987654321

# Не публикуй этот файл в GitHub
```

Где:

- `BOT_TOKEN` — токен, который выдаёт [@BotFather](https://t.me/BotFather)
- `ADMIN_IDS` — Telegram ID администраторов через запятую

Узнать свой Telegram ID можно через [@userinfobot](https://t.me/userinfobot).

> ⚠️ Никогда не загружай `.env`, токен бота или файл SQLite-базы в публичный репозиторий.

Добавь в `.gitignore`:

```gitignore
.env
*.db
*.sqlite
*.sqlite3
__pycache__/
.venv/
```

### 6. Запусти бота

Если точка входа — `main.py` в корне проекта:

```bash
uv run python main.py
```

Если точка входа находится в `bot/main.py`:

```bash
uv run python -m bot.main
```

После успешного запуска бот начнёт получать обновления через long polling.

## ⚙️ Добавление зависимостей

Добавить новую зависимость:

```bash
uv add название-пакета
```

Например:

```bash
uv add aiogram peewee python-dotenv tzdata
```

Добавить зависимость только для разработки:

```bash
uv add --dev ruff
```

После этого `uv` автоматически обновит `pyproject.toml` и `uv.lock`.

## 🗄️ База данных

Бот использует SQLite 3 через Peewee ORM.

При первом запуске необходимо создать таблицы:

```python
from bot.database.models import create_tables

create_tables()
```

Не добавляй рабочую базу в публичный Git-репозиторий. Она может содержать Telegram ID, username, сообщения и платежные идентификаторы.

## ⭐ Premium и Telegram Stars

Premium-подписка оплачивается через Telegram Stars.

Бот сохраняет данные платежа:

- `telegram_payment_charge_id`
- сумму в Stars
- дату оплаты
- статус платежа
- срок доступности возврата
- дату возврата, если он был выполнен

Статусы платежа:

```text
paid       — платёж получен
refunding  — возврат обрабатывается
refunded   — платёж возвращён
```

Пользовательский возврат доступен только в пределах установленного окна возврата. Администратор может выполнить ручной возврат по ID операции через админ-команду.

## 🛡️ Админ-команды

Пример ручного возврата платежа:

```text
/admin_refund TELEGRAM_PAYMENT_CHARGE_ID
```

Команда доступна только пользователям из `ADMIN_IDS`.

> ⚠️ Возврат Stars нельзя отменить. Перед использованием команды проверь ID операции и пользователя.

## 🕒 Часовые пояса

Для отображения времени в Москве используется IANA timezone:

```python
from zoneinfo import ZoneInfo

MSK = ZoneInfo("Europe/Moscow")
```

На Windows для работы `ZoneInfo` обычно нужна база часовых поясов:

```bash
uv add tzdata
```

## 🔒 Privacy Policy

Перед публикацией бота рекомендуется указать публичную политику конфиденциальности через [@BotFather](https://t.me/BotFather).

Бесплатный вариант — GitHub Pages:

```text
https://YOUR_GITHUB_USERNAME.github.io/secretask-privacy/
```

Политика должна честно описывать:

- какие данные хранит бот;
- как работают анонимные сообщения;
- возможность раскрытия отправителя через Premium;
- обработку платежей и возвратов;
- способ запроса удаления данных.

## 🤝 Вклад в проект

1. Сделай fork репозитория
2. Создай ветку:

```bash
git checkout -b feature/my-feature
```

3. Внеси изменения
4. Проверь запуск:

```bash
uv run python -m bot.main
```

5. Создай Pull Request

## 📄 Лицензия

Проект распространяется под лицензией MIT. См. файл [LICENSE](LICENSE).

## ⚠️ Отказ от ответственности

Проект предоставляется «как есть». Разработчик не несёт ответственности за пользовательский контент, отправленный через бот. Пользователи обязаны соблюдать правила Telegram и применимое законодательство.

---

Создано с ❤️ и Python
```

## Уточни точку входа

В README оставлены два варианта запуска:

```bash
uv run python main.py
```

или:

```bash
uv run python -m bot.main
```

Оставь только тот, который соответствует твоей реальной структуре. `uv sync` синхронизирует зависимости проекта, а `uv run` запускает команду внутри управляемого окружения проекта.

aiogram устанавливается как обычная зависимость из PyPI, а Peewee поддерживает SQLite из коробки.

