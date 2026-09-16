import math
import os
import re

import numpy as np
from PIL import Image, ImageDraw

ROOT = "/home/mullainathan/Documents/Coding/Projects/Festive"
SRC_TS = os.path.join(ROOT, "src", "data", "festivals.ts")
DEST = os.path.join(ROOT, "public", "images", "festivals")
OUT = os.path.join(ROOT, "image-gen", "output")

SIZE = 1024
SS = 4
C = SIZE * SS  # canvas

# gradient color pairs per festival (top-left -> bottom-right)
GRADS = {
    "Diwali": ((255, 122, 0), (255, 194, 75)),
    "Holi": ((255, 77, 141), (142, 92, 255)),
    "Navratri": ((255, 46, 147), (0, 184, 169)),
    "Durga Puja": ((214, 42, 60), (245, 166, 35)),
    "Dussehra / Vijayadashami": ((230, 57, 70), (244, 162, 97)),
    "Makar Sankranti": ((255, 140, 66), (76, 201, 240)),
    "Raksha Bandhan": ((230, 57, 70), (255, 179, 198)),
    "Janmashtami": ((0, 137, 123), (76, 175, 80)),
    "Ganesh Chaturthi": ((255, 143, 0), (233, 30, 99)),
    "Maha Shivratri": ((63, 81, 181), (156, 39, 176)),
    "Karva Chauth": ((63, 14, 99), (123, 31, 162)),
    "Eid-ul-Fitr": ((0, 137, 123), (212, 175, 55)),
    "Eid-ul-Adha (Bakrid)": ((27, 94, 32), (201, 162, 39)),
    "Christmas": ((211, 47, 47), (46, 125, 50)),
    "Guru Nanak Jayanti": ((26, 35, 126), (212, 175, 55)),
    "Buddha Purnima": ((124, 179, 66), (201, 162, 39)),
    "Rath Yatra": ((211, 47, 47), (245, 124, 0)),
    "Kumbh Mela": ((0, 105, 92), (2, 119, 189)),
    "Pongal": ((191, 91, 47), (242, 184, 128)),
    "Lohri": ((255, 109, 0), (183, 28, 28)),
    "Baisakhi": ((249, 168, 37), (85, 139, 47)),
    "Onam": ((46, 125, 50), (239, 108, 0)),
    "Ugadi / Gudi Padwa": ((245, 124, 0), (56, 142, 60)),
    "Vishu": ((230, 167, 0), (255, 213, 79)),
    "Rakhi / Nariyal Poornima": ((2, 119, 189), (0, 137, 123)),
    "Independence Day": ((255, 153, 51), (19, 136, 8)),
    "Republic Day": ((255, 153, 51), (26, 35, 126)),
    "Gandhi Jayanti": ((245, 240, 230), (141, 110, 99)),
}


def slugify(name):
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def gradient_img(c1, c2, canvas):
    x = np.linspace(0, 1, canvas)
    y = np.linspace(0, 1, canvas)[:, None]
    t = (x + y) / 2
    arr = np.zeros((canvas, canvas, 3), dtype=np.float64)
    for i in range(3):
        arr[:, :, i] = c1[i] * (1 - t) + c2[i] * t
    return arr.astype(np.uint8)


class ScaledDraw:
    """ImageDraw wrapper that scales 1024-space coords up to the SS canvas."""

    def __init__(self, d, s):
        self.d = d
        self.s = s

    def _box(self, b):
        return [c * self.s for c in b]

    def _pts(self, pts):
        return [[c * self.s for c in p] for p in pts]

    def ellipse(self, box, **kw):
        if "width" in kw:
            kw["width"] *= self.s
        self.d.ellipse(self._box(box), **kw)

    def polygon(self, pts, **kw):
        self.d.polygon(self._pts(pts), **kw)

    def rectangle(self, box, **kw):
        if "width" in kw:
            kw["width"] *= self.s
        self.d.rectangle(self._box(box), **kw)

    def pieslice(self, box, start, end, **kw):
        if "width" in kw:
            kw["width"] *= self.s
        self.d.pieslice(self._box(box), start, end, **kw)

    def arc(self, box, start, end, **kw):
        if "width" in kw:
            kw["width"] *= self.s
        self.d.arc(self._box(box), start, end, **kw)


def rounded_line(d, p1, p2, w):
    x1, y1 = p1
    x2, y2 = p2
    ang = math.atan2(y2 - y1, x2 - x1)
    hw = w / 2
    dx, dy = math.cos(ang + math.pi / 2) * hw, math.sin(ang + math.pi / 2) * hw
    quad = [(x1 + dx, y1 + dy), (x2 + dx, y2 + dy), (x2 - dx, y2 - dy), (x1 - dx, y1 - dy)]
    d.polygon(quad, fill=(255, 255, 255))
    d.ellipse([x1 - hw, y1 - hw, x1 + hw, y1 + hw], fill=(255, 255, 255))
    d.ellipse([x2 - hw, y2 - hw, x2 + hw, y2 + hw], fill=(255, 255, 255))


def star(d, cx, cy, R, r, n, rot=90):
    pts = []
    for i in range(n * 2):
        ang = math.radians(rot - 180) + i * math.pi / n
        rad = R if i % 2 == 0 else r
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    d.polygon(pts, fill=(255, 255, 255))


def arc(d, box, start, end, w):
    d.arc(box, start=start, end=end, fill=(255, 255, 255), width=w)


def ring(d, cx, cy, r, w):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=w)


def icon(name, d):
    f = ICONS.get(name)
    if f:
        f(d)


def _diwali(d):
    d.ellipse([446, 400, 578, 560], fill=(255, 255, 255))
    d.polygon([(512, 700), (438, 520), (586, 520)], fill=(255, 255, 255))
    d.pieslice([286, 600, 738, 820], start=180, end=360, fill=(255, 255, 255))
    d.ellipse([452, 690, 572, 780], fill=(255, 255, 255))


def _holi(d):
    d.ellipse([360, 420, 560, 620], fill=(255, 255, 255))
    d.ellipse([500, 480, 720, 700], fill=(255, 255, 255))
    d.ellipse([560, 330, 720, 490], fill=(255, 255, 255))
    for c in [(330, 560, 22), (470, 700, 18), (700, 600, 20), (640, 720, 16), (360, 360, 16)]:
        d.ellipse([c[0] - c[2], c[1] - c[2], c[0] + c[2], c[1] + c[2]], fill=(255, 255, 255))


def _navratri(d):
    rounded_line(d, (340, 360), (684, 664), 48)
    rounded_line(d, (340, 664), (684, 360), 48)
    for p in [(340, 360), (684, 664), (340, 664), (684, 360)]:
        d.ellipse([p[0] - 24, p[1] - 24, p[0] + 24, p[1] + 24], fill=(255, 255, 255))
    d.ellipse([487, 462, 537, 512], fill=(255, 255, 255))


def _durga(d):
    for a in range(-2, 3):
        ang = math.radians(a * 30 - 90)
        cx, cy = 512 + 150 * math.cos(ang), 520 + 150 * math.sin(ang)
        d.ellipse([cx - 72, cy - 72, cx + 72, cy + 72], fill=(255, 255, 255))
    d.ellipse([447, 447, 577, 577], fill=(255, 255, 255))


def _dussehra(d):
    arc(d, [300, 300, 724, 724], 200, 340, 20)
    rounded_line(d, (350, 580), (680, 470), 18)
    d.polygon([(690, 440), (720, 470), (680, 490)], fill=(255, 255, 255))
    d.ellipse([497, 497, 527, 527], fill=(255, 255, 255))


def _makar(d):
    d.polygon([(512, 300), (620, 500), (512, 700), (404, 500)], fill=(255, 255, 255))
    rounded_line(d, (512, 340), (512, 660), 14)
    rounded_line(d, (440, 500), (584, 500), 14)
    rounded_line(d, (340, 640), (404, 700), 10)
    d.ellipse([340, 620, 380, 660], fill=(255, 255, 255))
    d.ellipse([380, 660, 420, 700], fill=(255, 255, 255))


def _raksha(d):
    arc(d, [300, 300, 724, 724], 205, 335, 70)
    d.ellipse([586, 458, 638, 510], fill=(255, 255, 255))
    rounded_line(d, (612, 508), (612, 600), 12)
    rounded_line(d, (596, 508), (596, 580), 10)
    rounded_line(d, (628, 508), (628, 580), 10)


def _janmashtami(d):
    d.ellipse([372, 560, 652, 720], fill=(255, 255, 255))
    d.rectangle([362, 530, 662, 580], fill=(255, 255, 255))
    rounded_line(d, (500, 330), (500, 540), 14)
    d.ellipse([470, 370, 530, 430], fill=(255, 255, 255))
    arc(d, [460, 300, 540, 360], 160, 380, 12)


def _ganesh(d):
    d.ellipse([352, 350, 672, 670], fill=(255, 255, 255))
    d.ellipse([268, 420, 398, 560], fill=(255, 255, 255))
    d.ellipse([626, 420, 756, 560], fill=(255, 255, 255))
    arc(d, [420, 470, 560, 640], 200, 360, 70)


def _shivratri(d):
    rounded_line(d, (512, 300), (512, 640), 24)
    rounded_line(d, (512, 300), (512, 240), 30)
    rounded_line(d, (470, 320), (512, 440), 18)
    rounded_line(d, (554, 320), (512, 440), 18)
    arc(d, [620, 260, 780, 420], 40, 140, 22)
    d.ellipse([470, 640, 554, 660], fill=(255, 255, 255))


def _karva(d):
    arc(d, [262, 262, 762, 762], 205, 335, 24)
    d.pieslice([282, 420, 742, 820], start=200, end=340, outline=(255, 255, 255), width=14)
    d.ellipse([512, 620, 580, 668], fill=(255, 255, 255))


def _eid(d):
    arc(d, [312, 312, 712, 712], 205, 335, 26)
    star(d, 660, 330, 52, 22, 5)


def _bakrid(d):
    arc(d, [312, 312, 712, 712], 205, 335, 26)
    d.pieslice([340, 460, 560, 720], start=0, end=180, outline=(255, 255, 255), width=18)
    rounded_line(d, (330, 560), (330, 760), 16)
    rounded_line(d, (570, 560), (570, 760), 16)
    d.ellipse([318, 520, 342, 544], fill=(255, 255, 255))
    d.ellipse([558, 520, 582, 544], fill=(255, 255, 255))


def _christmas(d):
    star(d, 420, 420, 120, 50, 8)
    d.ellipse([600, 620, 740, 780], fill=(255, 255, 255))
    d.ellipse([650, 790, 690, 830], fill=(255, 255, 255))
    rounded_line(d, (600, 620), (740, 620), 12)


def _guru(d):
    rounded_line(d, (512, 280), (512, 640), 30)
    ring(d, 512, 512, 80, 20)
    rounded_line(d, (420, 430), (420, 620), 12)
    rounded_line(d, (604, 430), (604, 620), 12)


def _buddha(d):
    ring(d, 512, 470, 160, 18)
    for i in range(8):
        ang = math.radians(i * 45)
        rounded_line(d, (512, 470), (512 + 150 * math.cos(ang), 470 + 150 * math.sin(ang)), 12)
    d.ellipse([480, 438, 544, 502], fill=(255, 255, 255))
    for a in range(-2, 3):
        ang = math.radians(a * 28 - 90)
        cx, cy = 512 + 140 * math.cos(ang), 700 + 120 * math.sin(ang)
        d.ellipse([cx - 60, cy - 60, cx + 60, cy + 60], fill=(255, 255, 255))


def _rath(d):
    d.polygon([(512, 330), (430, 520), (594, 520)], fill=(255, 255, 255))
    d.rectangle([362, 600, 662, 680], fill=(255, 255, 255))
    d.ellipse([360, 660, 480, 780], fill=(255, 255, 255))
    d.ellipse([544, 660, 664, 780], fill=(255, 255, 255))
    d.ellipse([406, 706, 434, 734], fill=(255, 255, 255))
    d.ellipse([590, 706, 618, 734], fill=(255, 255, 255))
    d.ellipse([382, 600, 642, 640], fill=(255, 255, 255))
    d.polygon([(512, 270), (556, 300), (512, 320)], fill=(255, 255, 255))


def _kumbh(d):
    d.polygon([(430, 540), (594, 540), (572, 720), (452, 720)], fill=(255, 255, 255))
    d.ellipse([410, 490, 614, 560], fill=(255, 255, 255))
    d.ellipse([492, 440, 532, 480], fill=(255, 255, 255))
    arc(d, [320, 640, 704, 820], 20, 160, 12)
    d.ellipse([380, 520, 430, 560], fill=(255, 255, 255))
    d.ellipse([594, 520, 644, 560], fill=(255, 255, 255))


def _pongal(d):
    d.ellipse([392, 560, 632, 700], fill=(255, 255, 255))
    d.rectangle([382, 540, 642, 570], fill=(255, 255, 255))
    d.ellipse([492, 360, 532, 400], fill=(255, 255, 255))
    for i in range(8):
        ang = math.radians(i * 45 + 22)
        rounded_line(d, (512 + 60 * math.cos(ang), 390 + 60 * math.sin(ang)),
                     (512 + 160 * math.cos(ang), 390 + 160 * math.sin(ang)), 12)


def _lohri(d):
    d.ellipse([422, 330, 602, 470], fill=(255, 255, 255))
    d.polygon([(512, 700), (440, 520), (584, 520)], fill=(255, 255, 255))
    d.ellipse([352, 480, 420, 560], fill=(255, 255, 255))
    d.ellipse([604, 480, 672, 560], fill=(255, 255, 255))


def _baisakhi(d):
    rounded_line(d, (512, 280), (512, 640), 30)
    ring(d, 512, 512, 80, 20)
    rounded_line(d, (330, 460), (430, 600), 16)
    rounded_line(d, (694, 460), (594, 600), 16)
    for p in [(360, 500), (395, 545), (652, 500), (617, 545)]:
        d.polygon([(p[0], p[1] - 18), (p[0] + 18, p[1]), (p[0], p[1] + 18), (p[0] - 18, p[1])], fill=(255, 255, 255))


def _onam(d):
    d.ellipse([452, 452, 572, 572], fill=(255, 255, 255))
    for a in range(8):
        ang = math.radians(a * 45)
        cx, cy = 512 + 150 * math.cos(ang), 512 + 150 * math.sin(ang)
        d.ellipse([cx - 82, cy - 82, cx + 82, cy + 82], fill=(255, 255, 255))


def _ugadi(d):
    rounded_line(d, (512, 300), (512, 760), 20)
    d.polygon([(512, 360), (700, 420), (512, 480)], fill=(255, 255, 255))
    d.ellipse([466, 260, 558, 320], fill=(255, 255, 255))
    d.rectangle([492, 300, 532, 340], fill=(255, 255, 255))


def _vishu(d):
    d.ellipse([420, 640, 604, 720], fill=(255, 255, 255))
    rounded_line(d, (512, 420), (512, 640), 20)
    d.ellipse([432, 370, 592, 470], fill=(255, 255, 255))
    d.ellipse([476, 330, 548, 410], fill=(255, 255, 255))
    ring(d, 650, 340, 60, 16)
    d.ellipse([608, 530, 656, 578], fill=(255, 255, 255))
    d.ellipse([710, 560, 758, 608], fill=(255, 255, 255))


def _nariyal(d):
    d.ellipse([400, 460, 560, 620], fill=(255, 255, 255))
    d.ellipse([520, 460, 680, 620], fill=(255, 255, 255))
    arc(d, [400, 430, 680, 650], 210, 330, 22)
    arc(d, [300, 560, 724, 840], 20, 160, 12)


def _independence(d):
    ring(d, 512, 512, 150, 18)
    for i in range(12):
        ang = math.radians(i * 30)
        rounded_line(d, (512, 512), (512 + 140 * math.cos(ang), 512 + 140 * math.sin(ang)), 14)
    d.ellipse([486, 486, 538, 538], fill=(255, 255, 255))
    d.rectangle([330, 250, 430, 460], fill=(255, 255, 255))


def _republic(d):
    arc(d, [312, 380, 712, 800], 0, 180, 20)
    rounded_line(d, (332, 800), (332, 540), 26)
    rounded_line(d, (692, 800), (692, 540), 26)
    rounded_line(d, (512, 560), (512, 800), 26)
    d.rectangle([332, 780, 692, 830], fill=(255, 255, 255))
    d.ellipse([432, 430, 592, 590], fill=(255, 255, 255))


def _gandhi(d):
    ring(d, 512, 540, 130, 16)
    for i in range(8):
        ang = math.radians(i * 45)
        rounded_line(d, (512, 540), (512 + 115 * math.cos(ang), 540 + 115 * math.sin(ang)), 12)
    d.ellipse([480, 508, 544, 572], fill=(255, 255, 255))
    ring(d, 440, 350, 55, 16)
    ring(d, 584, 350, 55, 16)
    rounded_line(d, (495, 350), (529, 350), 10)
    rounded_line(d, (385, 350), (385, 300), 10)
    rounded_line(d, (639, 350), (639, 300), 10)


ICONS = {
    "Diwali": _diwali,
    "Holi": _holi,
    "Navratri": _navratri,
    "Durga Puja": _durga,
    "Dussehra / Vijayadashami": _dussehra,
    "Makar Sankranti": _makar,
    "Raksha Bandhan": _raksha,
    "Janmashtami": _janmashtami,
    "Ganesh Chaturthi": _ganesh,
    "Maha Shivratri": _shivratri,
    "Karva Chauth": _karva,
    "Eid-ul-Fitr": _eid,
    "Eid-ul-Adha (Bakrid)": _bakrid,
    "Christmas": _christmas,
    "Guru Nanak Jayanti": _guru,
    "Buddha Purnima": _buddha,
    "Rath Yatra": _rath,
    "Kumbh Mela": _kumbh,
    "Pongal": _pongal,
    "Lohri": _lohri,
    "Baisakhi": _baisakhi,
    "Onam": _onam,
    "Ugadi / Gudi Padwa": _ugadi,
    "Vishu": _vishu,
    "Rakhi / Nariyal Poornima": _nariyal,
    "Independence Day": _independence,
    "Republic Day": _republic,
    "Gandhi Jayanti": _gandhi,
}


def make_logo(c1, c2, name):
    bg = Image.fromarray(gradient_img(c1, c2, C)).convert("RGBA")
    mask = Image.new("L", (C, C), 0)
    md = ImageDraw.Draw(mask)
    r = int(150 * SS)
    md.rounded_rectangle([0, 0, C - 1, C - 1], radius=r, fill=255)
    bg.putalpha(mask)

    icon_layer = Image.new("RGBA", (C, C), (0, 0, 0, 0))
    d = ScaledDraw(ImageDraw.Draw(icon_layer), SS)
    d.ellipse([512 - 330, 512 - 330, 512 + 330, 512 + 330], outline=(255, 255, 255, 235), width=10)
    icon(name, d)

    bg.alpha_composite(icon_layer)
    bg = bg.resize((SIZE, SIZE), Image.LANCZOS)
    out = Image.new("RGB", (SIZE, SIZE), (255, 255, 255))
    out.paste(bg, (0, 0), bg)
    return out


def main():
    content = open(SRC_TS).read()
    names = list(dict.fromkeys(re.findall(r'M\("([^"]+)"', content)))
    os.makedirs(DEST, exist_ok=True)
    os.makedirs(OUT, exist_ok=True)
    ok = 0
    for name in names:
        slug = slugify(name)
        if name not in GRADS:
            print(f"[skip] {name}: no gradient")
            continue
        try:
            img = make_logo(GRADS[name][0], GRADS[name][1], name)
            img.save(os.path.join(DEST, f"{slug}.jpg"), "JPEG", quality=93)
            img.save(os.path.join(OUT, f"logo_{slug}.png"))
            ok += 1
            print(f"[ok] {slug}")
        except Exception as e:
            print(f"[fail] {name}: {e}")
    print(f"generated {ok}/{len(names)}")


if __name__ == "__main__":
    main()
