"""Render the game page in English and Russian from web/page.template.html."""
import json
import os
from music import web_score

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/kosta-blackshow/lymphodoom"

EN = {
    "lang": "en", "title": "LYMPHODOOM",
    "enter": "Click to play", "sound_on": "Music on", "sound_off": "Music off",
    "description": "A browser Doom where you are a killer T cell fighting viruses, bacteria and cancer cells inside the human body.",
    "canonical": "https://kostachernyshov.com/lymphodoom/", "origin": "https://kostachernyshov.com",
    "home": "Kosta Chernyshov", "other_url": "https://kostachernyshov.ru/lymphodoom/", "other_lang": "ru",
    "other_label": "По-русски",
    "poster_alt": "LYMPHODOOM. Controls: W A S D move, mouse aims and fires, E or right click opens, 1 to 7 weapons, Tab map.",
    "easy": "Play: Common cold (easy)", "hard": "Play: Metastasis (hard)",
    "fullscreen": "Full screen",
    "mobile": "LYMPHODOOM needs a keyboard and a mouse. Open this page on a computer.",
    "anyway": "Start anyway",
    "howto_alt": "You are a killer T cell. Shoot viruses, bacteria, tumor cells, parasites, phages, spores and the boss. "
                 "Pick up glucose for health, membranes for armor, ammo and dendritic scouts for the map; MHC-I keys open gates. "
                 "Three levels: lymph node, bloodstream, tumor.",
    "fine": "Engine: <a href=\"https://github.com/GMH-Code/Dwasm\">Dwasm</a> (PrBoomX / PrBoom+), GNU GPL v2. "
            "Music instruments: Freedoom (BSD). Not affiliated with id Software or ZeniMax. "
            "<a href=\"" + REPO + "\">Source code</a>.",
    "js": {"loading": "Loading…", "preparing": "Starting the engine…",
           "failed": "The game files did not load. Check the connection and pick a difficulty again.",
           "crashed": "The engine stopped. Reload the page to play again."},
}

RU = {
    "lang": "ru", "title": "LYMPHODOOM",
    "enter": "Нажмите, чтобы играть", "sound_on": "Включить музыку", "sound_off": "Выключить музыку",
    "description": "Doom в браузере: вы — Т-киллер и сражаетесь с вирусами, бактериями и раковыми клетками внутри тела человека.",
    "canonical": "https://kostachernyshov.ru/lymphodoom/", "origin": "https://kostachernyshov.ru",
    "home": "Константин Чернышов", "other_url": "https://kostachernyshov.com/lymphodoom/", "other_lang": "en",
    "other_label": "In English",
    "poster_alt": "LYMPHODOOM. Управление: W A S D — движение, мышь — прицел и огонь, E или правая кнопка — открыть, 1–7 — оружие, Tab — карта.",
    "easy": "Играть: Common cold (легко)", "hard": "Играть: Metastasis (сложно)",
    "fullscreen": "На весь экран",
    "mobile": "Для LYMPHODOOM нужны клавиатура и мышь. Откройте страницу на компьютере.",
    "anyway": "Всё равно запустить",
    "howto_alt": "Вы — Т-киллер. Стреляйте в вирусы, бактерии, опухолевые клетки, паразитов, фагов, споры и босса. "
                 "Глюкоза лечит, мембрана защищает, ещё есть патроны и дендритная клетка с картой; MHC-I-ключи открывают ворота. "
                 "Три уровня: лимфоузел, кровоток, опухоль.",
    "fine": "Движок: <a href=\"https://github.com/GMH-Code/Dwasm\">Dwasm</a> (PrBoomX / PrBoom+), GNU GPL v2. "
            "Инструменты музыки: Freedoom (BSD). Игра не связана с id Software и ZeniMax. "
            "<a href=\"" + REPO + "\">Исходный код</a>.",
    "js": {"loading": "Загрузка…", "preparing": "Запускаю движок…",
           "failed": "Файлы игры не загрузились. Проверьте соединение и выберите сложность ещё раз.",
           "crashed": "Движок остановился. Обновите страницу, чтобы играть снова."},
}


def render(d):
    t = open(os.path.join(ROOT, "web", "page.template.html"), encoding="utf-8").read()
    for k, v in d.items():
        if k == "js":
            t = t.replace("{{js_strings}}", json.dumps(v, ensure_ascii=False))
        else:
            t = t.replace("{{%s}}" % k, v)
    assert "{{" not in t, t[t.index("{{"):t.index("{{") + 40]
    return t


if __name__ == "__main__":
    with open(os.path.join(ROOT, "web", "title-score.json"), "w", encoding="utf-8") as f:
        json.dump(web_score(), f, separators=(",", ":"))
    open(os.path.join(ROOT, "web", "index.html"), "w", encoding="utf-8").write(render(EN))
    open(os.path.join(ROOT, "web", "ru.html"), "w", encoding="utf-8").write(render(RU))
    print("ok")
