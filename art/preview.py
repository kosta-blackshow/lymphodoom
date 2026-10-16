import sys
from PIL import Image, ImageDraw
from common import SCALE
sys.path.insert(0, '../tools')
import doomgfx as g
from pixel_kit.palette import P

def sheet(groups, out, scale=3, bg=(20, 26, 50)):
    rows = []
    for name, frames in groups:
        ims = [(L, fr.spr.image(scale)) for L, fr in sorted(frames.items())]
        rows.append((name, ims))
    W = max(sum(im.width + 6 for _, im in ims) for _, ims in rows) + 60
    H = sum(max(im.height for _, im in ims) + 18 for _, ims in rows)
    img = Image.new('RGB', (W, H), bg)
    d = ImageDraw.Draw(img)
    y = 0
    for name, ims in rows:
        h = max(im.height for _, im in ims)
        d.text((2, y + 2), name, fill=(255, 236, 39))
        x = 50
        for L, im in ims:
            img.paste(im, (x, y + 14 + h - im.height), im)
            d.text((x, y + 2), L, fill=(194, 195, 199))
            x += im.width + 6
        y += h + 18
    img.save(out)

if __name__ == '__main__':
    import monsters
    sheet([(k, fn()) for k, fn in monsters.ALL.items()], sys.argv[1] if len(sys.argv) > 1 else 'monsters.png', scale=2)

def grid(d, out, scale=3, cols=8, bg=(20, 26, 50)):
    cells = []
    for name, frames in d.items():
        for L in sorted(frames)[:4]:
            cells.append((name + L, frames[L].spr.image(scale)))
    cw = max(im.width for _, im in cells) + 8
    ch = max(im.height for _, im in cells) + 16
    cw = min(cw, 140); ch = min(ch, 150)
    rows = (len(cells) + cols - 1) // cols
    img = Image.new('RGB', (cw * cols, ch * rows), bg)
    dr = ImageDraw.Draw(img)
    for i, (n, im) in enumerate(cells):
        x, y = (i % cols) * cw, (i // cols) * ch
        if im.width > cw - 4 or im.height > ch - 16:
            k = min((cw - 4) / im.width, (ch - 16) / im.height)
            im = im.resize((max(1, int(im.width * k)), max(1, int(im.height * k))), Image.NEAREST)
        img.paste(im, (x + 2, y + ch - im.height - 2), im)
        dr.text((x + 2, y + 1), n, fill=(255, 236, 39))
    img.save(out)
