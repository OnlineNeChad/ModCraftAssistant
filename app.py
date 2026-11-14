"""
ModCraft Assistant — Десктопное приложение для управления модами Minecraft.
Современный веб-интерфейс внутри нативного окна Windows на pywebview.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path
import webview

# PyInstaller freeze handling: переключаем рабочую директорию в каталог .exe
if getattr(sys, "frozen", False):
    os.chdir(Path(sys.executable).resolve().parent)

# Заглушка для BOT_TOKEN, чтобы импорт parsers/config не падал при отсутствии .env
os.environ.setdefault("BOT_TOKEN", "standalone_gui_mode")

# Импорт бэкенд-модуля Api и путей
from backend.api import Api, get_default_db_path, get_default_mods_dir


def get_assets_dir() -> Path:
    """
    Определяет путь к папке assets/ как при запуске из исходников,
    так и внутри скомпилированного PyInstaller пакета.
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            meipass_assets = Path(sys._MEIPASS) / "assets"
            if meipass_assets.exists():
                return meipass_assets
        exe_assets = Path(sys.executable).resolve().parent / "assets"
        if exe_assets.exists():
            return exe_assets

    return Path(__file__).resolve().parent / "assets"


def get_web_dir() -> Path:
    """
    Определяет путь к папке web/ как при запуске из исходников,
    так и внутри скомпилированного PyInstaller пакета.
    """
    if getattr(sys, "frozen", False):
        if hasattr(sys, "_MEIPASS"):
            meipass_web = Path(sys._MEIPASS) / "web"
            if meipass_web.exists():
                return meipass_web
        exe_web = Path(sys.executable).resolve().parent / "web"
        if exe_web.exists():
            return exe_web

    return Path(__file__).resolve().parent / "web"


def main():
    """
    Точка входа приложения. Создаёт окно pywebview и связывает JS с Python Api.
    """
    web_dir = get_web_dir()
    index_html = web_dir / "index.html"

    # Создаём экземпляр Python API
    api = Api()

    # Создаём нативное окно pywebview с подключением веб-интерфейса и JS API
    window = webview.create_window(
        title="ModCraft Assistant — Умный менеджер модов Minecraft",
        url=str(index_html.resolve()),
        js_api=api,
        width=1280,
        height=800,
        min_size=(1060, 650),
        background_color="#0B0D12",
        text_select=False,
    )

    # Передаём ссылку на окно в Api для отправки обратных вызовов в JS
    api.set_window(window)

    # Определяем путь к иконке приложения
    assets_dir = get_assets_dir()
    icon_path = assets_dir / "icon.ico"
    icon_str = str(icon_path.resolve()) if icon_path.exists() else None

    # Запуск оконного цикла с привязкой иконки и встроенного локального HTTP-сервера
    # http_server=True обеспечивает мгновенный рендеринг WebView2 без ожидания изменения размера окна
    if icon_str:
        webview.start(debug=False, http_server=True, icon=icon_str)
    else:
        webview.start(debug=False, http_server=True)


if __name__ == "__main__":
    main()
