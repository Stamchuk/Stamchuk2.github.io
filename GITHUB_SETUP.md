# Быстрая инструкция по загрузке на GitHub

## ✅ Что уже сделано:

1. ✅ Git репозиторий инициализирован
2. ✅ Все файлы добавлены и закоммичены
3. ✅ LICENSE файл создан (MIT)
4. ✅ GitHub Actions настроены (автоматическая публикация на PyPI)
5. ✅ .gitignore настроен

## 📋 Следующие шаги:

### Шаг 1: Создайте репозиторий на GitHub

1. Откройте https://github.com/new
2. Заполните форму:
   - **Repository name**: `minecraft-mcp-server`
   - **Description**: `MCP сервер для доступа к документации Minecraft и API`
   - **Visibility**: Public
   - **НЕ добавляйте** README, .gitignore или LICENSE (они уже есть)
3. Нажмите **"Create repository"**

### Шаг 2: Свяжите локальный репозиторий с GitHub

Скопируйте и выполните эти команды (замените `YOUR_USERNAME` на ваше имя пользователя GitHub):

```bash
# Добавьте удаленный репозиторий
git remote add origin https://github.com/YOUR_USERNAME/minecraft-mcp-server.git

# Переименуйте ветку в main
git branch -M main

# Отправьте код на GitHub
git push -u origin main
```

### Шаг 3: Проверьте загрузку

Откройте ваш репозиторий на GitHub и убедитесь, что все файлы загружены.

## 🚀 Опционально: Публикация на PyPI

Если хотите опубликовать пакет на PyPI (чтобы его можно было установить через `pip install`):

### 1. Зарегистрируйтесь на PyPI

- Перейдите на https://pypi.org
- Создайте аккаунт
- Подтвердите email

### 2. Создайте API токен

1. Войдите в PyPI
2. Перейдите в **Account Settings** → **API tokens**
3. Нажмите **"Add API token"**
4. Заполните:
   - **Token name**: `minecraft-mcp-server`
   - **Scope**: "Entire account"
5. Скопируйте токен (показывается только один раз!)

### 3. Добавьте токен в GitHub Secrets

1. Откройте ваш репозиторий на GitHub
2. Перейдите в **Settings** → **Secrets and variables** → **Actions**
3. Нажмите **"New repository secret"**
4. Заполните:
   - **Name**: `PYPI_API_TOKEN`
   - **Secret**: вставьте ваш PyPI токен
5. Нажмите **"Add secret"**

### 4. Создайте релиз

1. В вашем репозитории перейдите в **Releases**
2. Нажмите **"Create a new release"**
3. Нажмите **"Choose a tag"** → введите `v0.1.0` → **"Create new tag"**
4. Заполните:
   - **Release title**: `v0.1.0 - Initial Release`
   - **Description**: 
     ```
     Первый релиз Minecraft MCP Server!
     
     Возможности:
     - Получение документации Paper MC, Leaf MC, Purpur MC
     - Поиск по Minecraft Wiki
     - Доступ к Mojang API
     - Кэширование запросов
     ```
5. Нажмите **"Publish release"**

GitHub Actions автоматически соберет и опубликует пакет на PyPI!

## 📦 После публикации

Ваш пакет будет доступен для установки:

```bash
# Через pip
pip install minecraft-mcp-server

# Через uvx
uvx minecraft-mcp-server
```

## 🔄 Обновление версии

Когда захотите выпустить новую версию:

1. Обновите версию в `pyproject.toml`:
   ```toml
   version = "0.2.0"
   ```

2. Обновите версию в `src/minecraft_mcp_server/__init__.py`:
   ```python
   __version__ = "0.2.0"
   ```

3. Закоммитьте изменения:
   ```bash
   git add .
   git commit -m "Bump version to 0.2.0"
   git push
   ```

4. Создайте новый релиз на GitHub с тегом `v0.2.0`

## 📝 Полезные команды

```bash
# Проверить статус Git
git status

# Посмотреть историю коммитов
git log --oneline

# Посмотреть удаленные репозитории
git remote -v

# Отправить изменения на GitHub
git push

# Получить изменения с GitHub
git pull
```

## ❓ Нужна помощь?

Если возникли проблемы, обратитесь к полному руководству в файле `DEPLOYMENT.md`.
