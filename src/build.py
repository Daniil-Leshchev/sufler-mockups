"""Собирает три макета «Подсказки ответа» из одного шаблона.

Запуск: python3 build.py (из любой папки). Результат - v1-card.html, v2-card-strip.html,
v3-tab.html рядом с папкой src; каждый файл самодостаточный, без внешних запросов.
"""

from pathlib import Path

SRC = Path(__file__).resolve().parent
OUT = SRC.parent

VARIANTS = [
    ("v1-card.html", "v1", "Подсказка ответа · вариант 1 · карточка"),
    ("v2-card-strip.html", "v2", "Подсказка ответа · вариант 2 · карточка и полоса"),
    ("v3-tab.html", "v3", "Подсказка ответа · вариант 3 · вкладка"),
]


def main() -> None:
    template = (SRC / "template.html").read_text(encoding="utf-8")
    for file_name, variant, title in VARIANTS:
        html = template.replace("%%VARIANT%%", variant).replace("%%TITLE%%", title)
        (OUT / file_name).write_text(html, encoding="utf-8")
        print(f"written {file_name}")


if __name__ == "__main__":
    main()
