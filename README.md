# Точечные патчеры Antigravity для macOS

## Antigravity CLI

Скрипт создаёт локально подписанную копию Antigravity CLI `1.5.3` для Apple Silicon. Перед переподписью он меняет два байта в protobuf-дескрипторе `ineligible_tiers`. CLI продолжает использовать штатные настройки прокси.

Скрипт проверяет SHA-256 и подпись Google у исходной сборки, ищет ровно одно совпадение дескриптора и записывает результат в новый файл. Если файл по указанному пути уже есть, скрипт сообщает об ошибке.

### Сборка и проверка CLI

На Mac с Apple Silicon запустите скрипт через нативный Python 3 и передайте ему оригинальный `agy` с подписью Google.

```sh
python3 patch_agy.py /путь/к/оригиналу/agy ./agy-patched
AGY_CLI_DISABLE_AUTO_UPDATE=true ./agy-patched --model gemini-4-argon-high -p 'Ответь только словом OK.'
```

### Установка и откат CLI

Сохраните исполняемый файл с подписью Google для отката. Чтобы установить патч, создайте пропатченную копию рядом с установленным `agy` и переименуйте её в `agy` с заменой файла. Для отката скопируйте подписанный оригинал в новый файл в том же каталоге и переименуйте его в `agy` с заменой. Обновление CLI может перезаписать патч.

## Antigravity App 2.35.0

`patch_app.py` создаёт локально подписанную копию `language_server` из Antigravity App `2.35.0` для Apple Silicon. Скрипт проверяет SHA-256 и подпись Google, меняет два байта в protobuf-дескрипторе `ineligible_tiers` и проверяет подпись результата. Настройки прокси берутся из штатной переменной `https_proxy`.

Патч снимает клиентскую проверку региона. Для серверных запросов нужен доступ к Google из поддерживаемого региона.

### Сборка и проверка приложения

Передайте оригинальный `language_server` с подписью Google. Файл результата должен отсутствовать.

```sh
python3 patch_app.py /Applications/Antigravity.app/Contents/Resources/bin/language_server ./language_server-patched
./language_server-patched --stamp
```

### Установка и откат приложения

Сохраните копию оригинального `Antigravity.app` для отката и закройте приложение. Создайте пропатченную копию рядом с `language_server` и переименуйте её с заменой файла.

```sh
python3 patch_app.py /Applications/Antigravity.app/Contents/Resources/bin/language_server /Applications/Antigravity.app/Contents/Resources/bin/language_server-patched
mv /Applications/Antigravity.app/Contents/Resources/bin/language_server-patched /Applications/Antigravity.app/Contents/Resources/bin/language_server
xattr -dr com.apple.quarantine /Applications/Antigravity.app
open /Applications/Antigravity.app
```

Правка нарушает внешнюю подпись `.app`, поэтому перед запуском снимается карантин Gatekeeper. Если macOS запрещает запись, разрешите приложению, из которого запущен скрипт, «Управление приложениями» в системных настройках.

Для отката закройте приложение и восстановите оригинальный `Antigravity.app` из копии. Обновление приложения может перезаписать патч.

Идея правки бинарника основана на подходе [Antigravity Unlocker](https://github.com/confeden/Antigravity/releases/tag/v2.34.0).
