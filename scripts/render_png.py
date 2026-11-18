"""Перерисовывает png/*.png из HTML-макетов через headless Chromium.

Запуск из корня репозитория: python3 scripts/render_png.py
Поднимает временный http.server на 127.0.0.1, снимает каждый макет с ?static=1
в 1920x1080 и останавливает сервер. Путь к браузеру - переменная CHROMIUM или
Chromium из pyppeteer.
"""

import os
import shutil
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PAGES = ["v1-card", "v2-card-strip", "v3-tab"]
DEFAULT_CHROMIUM = Path.home() / (
    "Library/Application Support/pyppeteer/local-chromium/1181205/"
    "chrome-mac/Chromium.app/Contents/MacOS/Chromium"
)


def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


def render(chromium: str, url: str, out: Path) -> bool:
    tmp = out.with_suffix(".new.png")
    tmp.unlink(missing_ok=True)
    profile = tempfile.mkdtemp()
    # --headless=new не завершается сам: ждём файл и гасим процесс; окно 1165 даёт картинку 1080
    proc = subprocess.Popen(
        [chromium, "--headless=new", "--disable-gpu", "--hide-scrollbars",
         "--force-device-scale-factor=1", f"--user-data-dir={profile}",
         "--window-size=1920,1165", f"--screenshot={tmp}", url],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        deadline = time.time() + 60
        while time.time() < deadline:
            if tmp.exists() and tmp.stat().st_size > 10_000:
                time.sleep(1.5)
                break
            time.sleep(0.5)
    finally:
        proc.kill()
        proc.wait()
        shutil.rmtree(profile, ignore_errors=True)
    if not tmp.exists():
        return False
    tmp.replace(out)
    return True


def main() -> int:
    chromium = os.environ.get("CHROMIUM", str(DEFAULT_CHROMIUM))
    if not Path(chromium).exists():
        print(f"Chromium не найден: {chromium}. Укажите путь в переменной CHROMIUM.")
        return 1
    port = free_port()
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", "127.0.0.1", "--directory", str(ROOT)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    try:
        time.sleep(1)
        failed = []
        for page in PAGES:
            ok = render(chromium, f"http://127.0.0.1:{port}/{page}.html?static=1", ROOT / "png" / f"{page}.png")
            print(f"{page}: {'ok' if ok else 'НЕ ВЫШЛО'}")
            if not ok:
                failed.append(page)
        return 1 if failed else 0
    finally:
        server.terminate()
        server.wait()


if __name__ == "__main__":
    sys.exit(main())
