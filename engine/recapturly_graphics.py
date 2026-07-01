"""
Recapturly branded social graphics engine  (v2 — official Brand Kit v1.0)
1080x1080 PNGs. Locked brand system: change a value once, every graphic updates.

Palette  : Deep Navy #0D1F3C · Electric Teal #00C2A8 · Soft Gold #C9A84C (sparingly)
           Warm Off-White #F6F4F0 · Slate Gray #4A5568 · White #FFFFFF
Fonts    : Plus Jakarta Sans (display) · Inter (body) · Lora Italic (quotes only)
Wordmark : white or teal on navy. NEVER gold. (per brand rules)

Templates: stat_card · quote_card · carousel_slide(kind="cover|body|cta")
Each supports theme="navy" (default, premium) or theme="light".
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# ---- BRAND (edit here only) -------------------------------------------
NAVY    = (13, 31, 60)      # #0D1F3C
TEAL    = (0, 194, 168)     # #00C2A8
GOLD    = (201, 168, 76)    # #C9A84C
OFFWHT  = (246, 244, 240)   # #F6F4F0
SLATE   = (74, 85, 104)     # #4A5568
WHITE   = (255, 255, 255)
NAVY_DK = (9, 22, 44)       # deeper navy for gradient
MUTEDLT = (150, 167, 188)   # muted light text on navy
S = 1080
M = 100
FD = os.environ.get("RCAP_FONT_DIR") or (os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts") + "/")  # portable font dir
_F = {
 "display_b":  FD+"PlusJakartaSans-Bold.ttf",
 "display_sb": FD+"PlusJakartaSans-SemiBold.ttf",
 "display_m":  FD+"PlusJakartaSans-Medium.ttf",
 "body":       FD+"Inter-Regular.ttf",
 "body_m":     FD+"Inter-Medium.ttf",
 "body_sb":    FD+"Inter-SemiBold.ttf",
 "quote":      FD+"Lora-Italic.ttf",
}
def f(name, size):
    fnt = ImageFont.truetype(_F[name], size)
    if name == "quote":
        try: fnt.set_variation_by_axes([600])  # SemiBold italic
        except Exception: pass
    return fnt

# ---- helpers ----------------------------------------------------------
def tracked(d, xy, text, font, fill, tr=0):
    x, y = xy
    for ch in text:
        d.text((x, y), ch, font=font, fill=fill); x += d.textlength(ch, font=font) + tr
    return x
def tw(d, text, font, tr=0):
    return sum(d.textlength(ch, font=font) + tr for ch in text) - (tr if text else 0)
def wrap(d, text, font, maxw):
    out, cur = [], ""
    for w in text.split():
        t = (cur+" "+w).strip()
        if d.textlength(t, font=font) <= maxw: cur = t
        else: out.append(cur); cur = w
    if cur: out.append(cur)
    return out

def _bg(theme):
    base = NAVY if theme == "navy" else OFFWHT
    img = Image.new("RGB", (S, S), base)
    if theme == "navy":
        # subtle vertical gradient for depth
        top = Image.new("RGB", (1, S))
        for y in range(S):
            t = y / S
            top.putpixel((0, y), tuple(int(NAVY[i]*(1-t)+NAVY_DK[i]*t) for i in range(3)))
        img = top.resize((S, S))
        # soft teal glow, upper-left, very low intensity
        glow = Image.new("L", (S, S), 0)
        gd = ImageDraw.Draw(glow); gd.ellipse([-200, -260, 620, 460], fill=70)
        glow = glow.filter(ImageFilter.GaussianBlur(170))
        tint = Image.new("RGB", (S, S), TEAL)
        img = Image.composite(tint, img, glow.point(lambda p: int(p*0.16)))
    return img

def _wordmark(d, theme):
    ink = WHITE if theme == "navy" else NAVY
    # teal envelope glyph
    x0, y0 = M, M
    d.rounded_rectangle([x0, y0, x0+40, y0+28], radius=5, outline=TEAL, width=3)
    d.line([x0+2, y0+3, x0+20, y0+17], fill=TEAL, width=3)
    d.line([x0+38, y0+3, x0+20, y0+17], fill=TEAL, width=3)
    d.text((x0+58, y0-8), "Recapturly", font=f("display_b", 40), fill=ink)

def _footer(d, theme, left="recapturly.com", right="No pitch. Just your numbers."):
    ink = WHITE if theme == "navy" else NAVY
    line = (255,255,255,30) if theme == "navy" else (13,31,60,30)
    y = S - M
    d.line([M, y-22, S-M, y-22], fill=(36,52,80) if theme=="navy" else (220,216,208), width=2)
    tracked(d, (M, y), left.upper(), f("body_m", 23), MUTEDLT if theme=="navy" else SLATE, tr=2)
    d.text((S-M-d.textlength(right, font=f("body_m", 23)), y), right,
           font=f("body_m", 23), fill=TEAL)

def _pill(d, xy, label):
    x, y = xy
    pad_x, h = 40, 74
    w = d.textlength(label, font=f("body_sb", 34)) + pad_x*2
    d.rounded_rectangle([x, y, x+w, y+h], radius=h//2, fill=TEAL)
    d.text((x+pad_x, y+18), label, font=f("body_sb", 34), fill=NAVY)
    return w

# ---- templates --------------------------------------------------------
def stat_card(number, headline, subline, out, theme="navy"):
    img = _bg(theme); d = ImageDraw.Draw(img)
    _wordmark(d, theme)
    ink = WHITE if theme == "navy" else NAVY
    d.text((M-6, 250), number, font=f("display_b", 300), fill=TEAL)
    d.line([M, 600, M+110, 600], fill=GOLD, width=8)
    y = 650
    for ln in wrap(d, headline, f("display_b", 78), S-2*M):
        d.text((M, y), ln, font=f("display_b", 78), fill=ink); y += 90
    y += 14
    for ln in wrap(d, subline, f("body", 38), S-2*M):
        d.text((M, y), ln, font=f("body", 38), fill=MUTEDLT if theme=="navy" else SLATE); y += 52
    _footer(d, theme)
    img.save(out); return out

def quote_card(quote, attribution, out, theme="navy"):
    img = _bg(theme); d = ImageDraw.Draw(img)
    _wordmark(d, theme)
    ink = WHITE if theme == "navy" else NAVY
    d.text((M-10, 196), "“", font=f("display_b", 200), fill=TEAL)
    y = 360
    qf = f("quote", 70)
    for ln in wrap(d, quote, qf, S-2*M-20):
        d.text((M, y), ln, font=qf, fill=ink); y += 92
    d.line([M, y+30, M+110, y+30], fill=TEAL, width=8)
    tracked(d, (M, y+58), attribution.upper(), f("body_sb", 28), TEAL, tr=2)
    _footer(d, theme)
    img.save(out); return out

def email_mockup(subject, preview, button, out, sender="YourBrand", flow="ABANDONED CART · DAY 1"):
    """Product-style 'breather' tile: a sample recovery email on navy. Adds visual variety."""
    img = _bg("navy"); d = ImageDraw.Draw(img)
    _wordmark(d, "navy")
    # email card
    cx0, cy0, cx1, cy1 = M-10, 250, S-M+10, 820
    shadow = Image.new("RGBA", (S, S), (0,0,0,0))
    ImageDraw.Draw(shadow).rounded_rectangle([cx0+8, cy0+14, cx1+8, cy1+14], radius=28, fill=(0,0,0,90))
    img.paste(Image.new("RGB",(S,S),NAVY_DK), (0,0), shadow.filter(ImageFilter.GaussianBlur(14)))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([cx0, cy0, cx1, cy1], radius=28, fill=WHITE)
    # header row
    d.ellipse([cx0+40, cy0+44, cx0+96, cy0+100], fill=TEAL)
    d.text((cx0+58, cy0+56), sender[0].upper(), font=f("display_b", 34), fill=WHITE)
    d.text((cx0+118, cy0+50), sender, font=f("body_sb", 32), fill=NAVY)
    tracked(d, (cx0+118, cy0+92), flow, f("body_m", 20), SLATE, tr=1)
    d.line([cx0+40, cy0+136, cx1-40, cy0+136], fill=(228,224,217), width=2)
    # subject + preview
    d.text((cx0+40, cy0+166), subject, font=f("display_b", 46), fill=NAVY)
    yy = cy0+240
    for ln in wrap(d, preview, f("body", 32), cx1-cx0-80):
        d.text((cx0+40, yy), ln, font=f("body", 32), fill=SLATE); yy += 46
    # button
    _pill(d, (cx0+40, yy+30), button)
    # caption line under card
    cap = f("display_m", 34)
    d.text((M, 868), "Customers reply to these. That's how you know the copy works.",
           font=f("body", 34), fill=MUTEDLT)
    _footer(d, "navy")
    img.save(out); return out

def brand_tile(out, line="Recapture every dollar your store leaves on the table."):
    """Tagline 'breather' tile with a large teal envelope watermark."""
    img = _bg("navy"); d = ImageDraw.Draw(img)
    # big envelope watermark, low opacity
    mask = Image.new("L", (S, S), 0); wd = ImageDraw.Draw(mask)
    wd.rounded_rectangle([560, 560, 1060, 920], radius=24, outline=255, width=10)
    wd.line([560, 575, 810, 760], fill=255, width=10); wd.line([1060, 575, 810, 760], fill=255, width=10)
    mask = mask.point(lambda p: int(p*0.12))
    img.paste(Image.new("RGB", (S, S), TEAL), (0, 0), mask)
    d = ImageDraw.Draw(img)
    _wordmark(d, "navy")
    tracked(d, (M, 300), "RECAPTURLY", f("body_sb", 26), TEAL, tr=4)
    y = 360
    for ln in wrap(d, line, f("display_b", 92), S-2*M):
        d.text((M, y), ln, font=f("display_b", 92), fill=WHITE); y += 104
    _footer(d, "navy")
    img.save(out); return out

def carousel_slide(index, total, title, body, out, kind="body",
                   kicker="HOW TO RECOVER A CART", theme="navy", cta_label="Book your free audit"):
    img = _bg(theme); d = ImageDraw.Draw(img)
    _wordmark(d, theme)
    ink = WHITE if theme == "navy" else NAVY
    if kind == "cover":
        tracked(d, (M, 286), kicker, f("body_sb", 28), TEAL, tr=3)
        y = 344
        for ln in wrap(d, title, f("display_b", 104), S-2*M):
            d.text((M, y), ln, font=f("display_b", 104), fill=ink); y += 116
        d.text((M, y+22), body, font=f("body", 40), fill=MUTEDLT if theme=="navy" else SLATE)
        tracked(d, (M, S-M-118), "SWIPE", f("body_sb", 26), TEAL, tr=4)
        d.text((M+118, S-M-130), "→", font=f("display_b", 46), fill=TEAL)
    elif kind == "cta":
        tracked(d, (M, 300), "YOUR NEXT STEP", f("body_sb", 28), TEAL, tr=3)
        y = 360
        for ln in wrap(d, title, f("display_b", 82), S-2*M):
            d.text((M, y), ln, font=f("display_b", 82), fill=ink); y += 96
        y += 12
        for ln in wrap(d, body, f("body", 38), S-2*M):
            d.text((M, y), ln, font=f("body", 38), fill=MUTEDLT if theme=="navy" else SLATE); y += 52
        _pill(d, (M, y+30), cta_label)
    else:  # body
        tracked(d, (M, 270), kicker, f("body_sb", 26), TEAL, tr=3)
        d.text((M, 318), f"{index:02d}", font=f("display_b", 88), fill=GOLD)
        y = 440
        for ln in wrap(d, title, f("display_b", 72), S-2*M):
            d.text((M, y), ln, font=f("display_b", 72), fill=ink); y += 84
        y += 12
        for ln in wrap(d, body, f("body", 40), S-2*M):
            d.text((M, y), ln, font=f("body", 40), fill=MUTEDLT if theme=="navy" else SLATE); y += 56
    # progress dots
    dx = M
    for i in range(total):
        c = TEAL if i == index else (45,63,92) if theme=="navy" else (215,210,202)
        d.ellipse([dx, S-M+2, dx+15, S-M+17], fill=c); dx += 26
    tracked(d, (S-M-tw(d,"RECAPTURLY.COM",f("body_m",22),2), S-M+2),
            "RECAPTURLY.COM", f("body_m", 22), MUTEDLT if theme=="navy" else SLATE, tr=2)
    img.save(out); return out
