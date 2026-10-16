# Палитра PICO-8 (lospec.com/palette-list/pico-8): 16 цветов, без полупрозрачности.
# Цвет закреплён за ролью на весь цикл — см. 02_библия.md.

P = [(0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81), (171, 82, 54), (95, 87, 79),
     (194, 195, 199), (255, 241, 232), (255, 0, 77), (255, 163, 0), (255, 236, 39),
     (0, 228, 54), (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170)]
BLACK, NAVY, PLUM, DGREEN, BROWN, DGREY, LGREY, WHITE, RED, ORANGE, YELLOW, GREEN, BLUE, LAV, PINK, PEACH = range(16)
NAMES = ["BLACK", "NAVY", "PLUM", "DGREEN", "BROWN", "DGREY", "LGREY", "WHITE",
         "RED", "ORANGE", "YELLOW", "GREEN", "BLUE", "LAV", "PINK", "PEACH"]


def C(i):
    return P[i]


def CA(i):
    return P[i] + (255,)
