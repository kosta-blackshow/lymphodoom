"""Render the game page in English and Russian from web/page.template.html."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = "https://github.com/kosta-blackshow/lymphodoom"

EN = {
    "lang": "en", "title": "LYMPHODOOM — Doom inside the human body",
    "description": "A browser Doom where you are a killer T cell fighting viruses, bacteria and cancer cells inside the human body.",
    "canonical": "https://kostachernyshov.com/lymphodoom/", "origin": "https://kostachernyshov.com",
    "home": "Kosta Chernyshov", "other_url": "https://kostachernyshov.ru/lymphodoom/", "other_lang": "ru",
    "other_label": "По-русски",
    "poster_alt": "LYMPHODOOM title screen: a killer T cell facing a virus, a tumor cell and a bacterium",
    "play": "Play", "fullscreen": "Full screen",
    "mobile": "LYMPHODOOM needs a keyboard and a mouse. Open this page on a computer.",
    "anyway": "Start anyway",
    "h1": "You are a killer T cell. The body is infected.",
    "about": "<p>LYMPHODOOM is Doom (1993) rebuilt inside a human body. Three levels take you from a lymph node, "
             "through the bloodstream, into a tumor, where the tumor mass is waiting.</p>"
             "<p>The enemies are viruses, bacteria, parasites, phages, fungal spores and tumor cells, including the "
             "ones that lost their MHC-I and are hard to see. The weapons are what an immune cell really uses: "
             "granules, cytokines, antibodies, interferon.</p>"
             "<p>Game progress is saved in your browser.</p>",
    "controls": "Controls", "mouse": "Mouse", "lmb": "Left click", "rmb": "right click", "or": "or",
    "k_move": "move", "k_turn": "turn and aim", "k_fire": "fire", "k_use": "open gates, press receptors",
    "k_walk": "walk (running is on by default)", "k_weapons": "weapons", "k_map": "map", "k_menu": "menu, save, load",
    "fine": "Engine: <a href=\"https://github.com/GMH-Code/Dwasm\">Dwasm</a> (PrBoomX / PrBoom+), GNU GPL v2. "
            "Characters drawn from the Cancer Wars bible. Music instruments: Freedoom (BSD). "
            "Not affiliated with id Software or ZeniMax. <a href=\"" + REPO + "\">Source code</a>.",
    "js": {"loading": "Loading…", "preparing": "Starting the engine…", "failed": "The game files did not load. Check the connection and press Play again.",
           "crashed": "The engine stopped. Reload the page to play again."},
}

RU = {
    "lang": "ru", "title": "LYMPHODOOM — Doom внутри человеческого тела",
    "description": "Doom в браузере: вы — Т-киллер и сражаетесь с вирусами, бактериями и раковыми клетками внутри тела человека.",
    "canonical": "https://kostachernyshov.ru/lymphodoom/", "origin": "https://kostachernyshov.ru",
    "home": "Константин Чернышов", "other_url": "https://kostachernyshov.com/lymphodoom/", "other_lang": "en",
    "other_label": "In English",
    "poster_alt": "Титульный экран LYMPHODOOM: Т-киллер против вируса, опухолевой клетки и бактерии",
    "play": "Играть", "fullscreen": "На весь экран",
    "mobile": "Для LYMPHODOOM нужны клавиатура и мышь. Откройте страницу на компьютере.",
    "anyway": "Всё равно запустить",
    "h1": "Вы — Т-киллер. Организм заражён.",
    "about": "<p>LYMPHODOOM — это Doom 1993 года, перенесённый внутрь человеческого тела. Три уровня ведут из "
             "лимфоузла через кровоток в опухоль, где ждёт опухолевая масса.</p>"
             "<p>Враги — вирусы, бактерии, паразиты, фаги, споры грибка и опухолевые клетки, в том числе те, что "
             "потеряли MHC-I и почти невидимы. Оружие — то, чем на самом деле пользуется иммунная клетка: "
             "гранулы, цитокины, антитела, интерферон.</p>"
             "<p>Игра на английском. Прогресс сохраняется в браузере.</p>",
    "controls": "Управление", "mouse": "Мышь", "lmb": "Левая кнопка", "rmb": "правая кнопка", "or": "или",
    "k_move": "движение", "k_turn": "поворот и прицел", "k_fire": "огонь", "k_use": "открыть ворота, нажать рецептор",
    "k_walk": "шагом (бег включён по умолчанию)", "k_weapons": "оружие", "k_map": "карта", "k_menu": "меню, сохранение, загрузка",
    "fine": "Движок: <a href=\"https://github.com/GMH-Code/Dwasm\">Dwasm</a> (PrBoomX / PrBoom+), GNU GPL v2. "
            "Персонажи нарисованы по библии Cancer Wars. Инструменты музыки: Freedoom (BSD). "
            "Игра не связана с id Software и ZeniMax. <a href=\"" + REPO + "\">Исходный код</a>.",
    "js": {"loading": "Загрузка…", "preparing": "Запускаю движок…", "failed": "Файлы игры не загрузились. Проверьте соединение и нажмите «Играть» ещё раз.",
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
    open(os.path.join(ROOT, "web", "index.html"), "w", encoding="utf-8").write(render(EN))
    open(os.path.join(ROOT, "web", "ru.html"), "w", encoding="utf-8").write(render(RU))
    print("ok")
