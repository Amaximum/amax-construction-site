# Работа на втором компьютере (PC2)

Весь код, все правки и вся история работы хранятся в GitHub:
**https://github.com/Amaximum/amax-construction-site**

Локальная история чата Copilot хранится только на том компьютере, где
шёл разговор — она НЕ синхронизируется автоматически. Но все
**файлы и коммиты** попадают на оба компьютера через `git pull`.

## Первый запуск на PC2 (один раз)

1. Установить **Git for Windows**: https://git-scm.com/download/win
2. Установить **VS Code**: https://code.visualstudio.com/
3. Установить расширения VS Code:
   - GitHub Copilot
   - GitHub Copilot Chat
   - Python
4. Открыть PowerShell, перейти в нужную папку и склонировать проект:
   ```powershell
   cd C:\Projects\SEO_Tool
   git clone https://github.com/Amaximum/amax-construction-site.git
   cd amax-construction-site
   ```
5. Создать `.venv` и поставить зависимости (если нужны для скриптов):
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
6. Включить **Settings Sync** в VS Code (войти через тот же GitHub-аккаунт):
   - `Ctrl+Shift+P` → `Settings Sync: Turn On`
   - Это синхронизирует настройки, темы, расширения между PC1 и PC2.

## Каждое утро на PC2 (или PC1) перед работой

```powershell
cd C:\Projects\SEO_Tool\amax-construction-site
git pull origin main
```

После `git pull` все правки, которые я делал на другом компьютере,
появятся локально.

## Каждый вечер перед закрытием VS Code

Если делали правки локально — не забыть запушить:
```powershell
git status
git add -A
git commit -m "коротко что сделано"
git push origin main
```

## Что НЕ синхронизируется

- История чата Copilot (она локальная). Чтобы видеть прогресс работы
  ассистента, смотри:
  - `git log --oneline -30` — список коммитов с описанием
  - `BLOG_REWRITE_PROGRESS.md` — чеклист переписывания блогов
- Файлы из `.gitignore` (например, `.venv/`, временные `*.txt`-аудиты).

## Если нужно работать с компьютера без установки

Браузерная версия:
- https://github.dev/Amaximum/amax-construction-site
- https://vscode.dev/github/Amaximum/amax-construction-site

Это VS Code прямо в браузере с доступом к репо — без установки на PC2.
