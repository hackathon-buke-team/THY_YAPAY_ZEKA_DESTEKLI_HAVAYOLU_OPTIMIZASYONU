# -*- coding: utf-8 -*-
"""Sunum slayt 4 için çözüm hattı şeması (docs/figures/fig11_cozum_hatti.png).

Neden ikiye böldüğümüzü ve her adımın ne kadar sürdüğünü tek bakışta anlatır.
Çalıştırma:  python src/11_cozum_hatti_figuru.py
"""

import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "docs", "figures", "fig11_cozum_hatti.png")

INK, GREY = "#1C122F", "#6E6A78"
BLUE, NAVY, PLUM, RED = "#0035D7", "#1C1C51", "#9E55A0", "#B03A48"

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})

# (başlık, alt satırlar, kenar rengi, dolgu, başlık rengi) — satırlar ≤ 30 karakter
PANELS = [
    ("Önce tek model",
     ["Haftanın tamamı tek seferde,",
      "100 binden fazla değişken.",
      "",
      "10 dakika bekledik,",
      "hiçbir sonuç çıkmadı."],
     RED, "#FBF1F2", RED),
    ("1. Günleri ayırdık",
     ["Günleri bağlayan tek kural,",
      "uçuşun günler arası saat",
      "farkı. Yedi günü ayrı çözdük.",
      "",
      "Süre: 1,5 dakika"],
     BLUE, "#EEF2FD", BLUE),
    ("2. Haftayı birleştirdik",
     ["Tek model, ama sıfırdan",
      "değil: 1. adımın sonucundan",
      "başlattık.",
      "",
      "30 dakika, optimuma %1,18"],
     NAVY, "#EEEEF5", NAVY),
    ("3. Bağımsız denetim",
     ["05_validate_solution.py",
      "Modeli hiç kullanmadan ham",
      "veriden yeniden hesaplar.",
      "",
      "18 kontrol, hepsi geçti."],
     PLUM, "#F6EFF7", PLUM),
]

FIGW, FIGH = 12.63, 3.25
fig, ax = plt.subplots(figsize=(FIGW, FIGH), dpi=200)
ax.set_xlim(0, 100)
ax.set_ylim(0, 100)
ax.axis("off")

# Dikey ölçek: y birimi = FIGH/100 inç. Yazı boyutları punto (mutlak) olduğundan,
# yazıya bağlı tüm dikey ofsetler k ile ölçeklenir — figür boyu değişince kaymasın.
k = 3.25 / FIGH
PW, GAP, X0, PY, PH = 22.3, 3.0, 0.4, 16.0, 66.0

for i, (title, lines, edge, fill, tcol) in enumerate(PANELS):
    x = X0 + i * (PW + GAP)
    ax.add_patch(FancyBboxPatch(
        (x, PY), PW, PH, boxstyle="round,pad=0,rounding_size=2.0",
        linewidth=1.1, edgecolor=edge, facecolor=fill, mutation_aspect=0.35))
    ax.plot([x + 1.2, x + 1.2], [PY + 3.5, PY + PH - 3.5], color=edge, lw=3,
            solid_capstyle="round")
    ax.text(x + 2.7, PY + PH - 8 * k, title, fontsize=10.5, fontweight="bold",
            color=tcol, va="top")
    for j, ln in enumerate(lines):
        if not ln:
            continue
        mono = ln.endswith(".py")
        ax.text(x + 2.7, PY + PH - (21 + j * 8.6) * k, ln, fontsize=8.4,
                color=INK if mono else GREY, va="top",
                family="DejaVu Sans Mono" if mono else "DejaVu Sans",
                fontweight="bold" if mono else "normal")

    if i < len(PANELS) - 1:
        ax0 = x + PW + 0.5
        ax.add_patch(FancyArrowPatch(
            (ax0, PY + PH / 2), (ax0 + GAP - 1.0, PY + PH / 2),
            arrowstyle="-|>", mutation_scale=13, linewidth=1.3, color="#B9B6C2"))

ax.text(0.4, 6, "Her şey tek komutla çalışır: python run_all.py, uçtan uca yaklaşık 40 dakika. "
                "Denetimde bir kontrol bile geçmezse çalışma kendini durdurur.",
        fontsize=9.3, color=GREY, va="center")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
fig.savefig(OUT, bbox_inches="tight", pad_inches=0.05, facecolor="white")
print(f"yazildi: {os.path.relpath(OUT, ROOT)}")
