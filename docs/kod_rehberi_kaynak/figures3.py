# -*- coding: utf-8 -*-
"""Ucuncu dokuman icin semalar: katki haritasi, one-hot, big-M, warm-start kazanci."""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle

from figures import (IMG, BLUE, RED, GREEN, ORANGE, INK, INK2, MUTED, GRID, AXIS, PAPER,
                     save, box, arrow, blank)


# ---------------------------------------------------------------- H1 katki haritasi
def h1():
    fig, ax = blank((7.2, 4.0))
    ax.text(0.5, 0.985, "Brief'ten sonuca: hangi adım kimin işi?",
            ha="center", va="top", fontsize=10.6, fontweight="bold", color=INK)

    rows = [
        (0.775, "Brief — düz yazıyla iş problemi", MUTED, "ORGANİZATÖR", MUTED),
        (0.585, "MATEMATİKSEL FORMÜLASYON\ndeğişkenler · kısıtlar · amaç · big-M",
         GREEN, "BİZ", GREEN),
        (0.395, "ÇÖZÜM STRATEJİSİ\nayrıştırma · warm-start · koruma sınırları",
         GREEN, "BİZ", GREEN),
        (0.235, "Çözme (dallanma-sınırlama)", RED, "HiGHS", RED),
        (0.095, "BAĞIMSIZ DOĞRULAMA\nçift kayıt · 12 kontrol · kalite kapısı",
         GREEN, "BİZ", GREEN),
    ]
    for y, txt, c, who, wc in rows:
        h = 0.135 if "\n" in txt else 0.10
        ax.add_patch(FancyBboxPatch((0.20, y), 0.60, h,
                                    boxstyle="round,pad=0.010,rounding_size=0.02",
                                    facecolor=("#eef6f1" if c is GREEN else "white"),
                                    edgecolor=c, linewidth=1.6))
        ax.text(0.50, y + h / 2, txt, ha="center", va="center", fontsize=8.2,
                color=INK, linespacing=1.4,
                fontweight=("bold" if c is GREEN else "normal"))
        ax.text(0.175, y + h / 2, who, ha="right", va="center", fontsize=8.6,
                color=wc, fontweight="bold")
    for y0, y1 in [(0.775, 0.720), (0.585, 0.530), (0.395, 0.350), (0.235, 0.235)]:
        arrow(ax, 0.50, y0 - 0.002, 0.50, y1, color=AXIS, lw=1.4)
    ax.text(0.845, 0.60, "5 adımın\n4'ü bizim", ha="center", va="center", fontsize=9,
            color=GREEN, fontweight="bold", linespacing=1.5)
    save(fig, "h1_katki_haritasi.png")


# ---------------------------------------------------------------- H2 one-hot
def h2():
    fig, ax = blank((7.2, 3.5))
    ax.text(0.5, 0.985, "Bir uçuşun saatini bilgisayara nasıl anlatırsınız?",
            ha="center", va="top", fontsize=10.4, fontweight="bold", color=INK)

    # SOL: surekli degisken
    ax.add_patch(FancyBboxPatch((0.02, 0.30), 0.45, 0.58,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="#fbf1ee", edgecolor="#e0b6b0", linewidth=1.3))
    ax.text(0.245, 0.835, "YOL 1 — sürekli değişken", ha="center", fontsize=9,
            fontweight="bold", color=RED)
    ax.text(0.245, 0.755, "θ = 510   (tek sayı, 08:30)", ha="center", fontsize=8.6,
            family="monospace", color=INK)
    ax.text(0.045, 0.665, "Sezgisel görünür AMA:", fontsize=8, color=INK, va="top")
    for i, t in enumerate(["|θ − cur| mutlak değeri doğrusal değil",
                           "→ ek değişken + big-M gerekir",
                           "F kapasitesi \"hangi kovada?\" sorusunu",
                           "   soramaz — ek gösterge gerekir"]):
        ax.text(0.055, 0.605 - i * 0.062, ("• " if i in (0, 2) else "   ") + t,
                fontsize=7.6, color=INK2, va="top")

    # SAG: one-hot
    ax.add_patch(FancyBboxPatch((0.53, 0.30), 0.45, 0.58,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="#eef6f1", edgecolor="#aacfbf", linewidth=1.3))
    ax.text(0.755, 0.835, "YOL 2 — tek-sıcak (one-hot)  ✔ SEÇTİĞİMİZ", ha="center",
            fontsize=9, fontweight="bold", color=GREEN)
    vals = [-30, -20, -10, 0, 10, 20, 30]
    x0 = 0.575
    w = 0.049
    for i, v in enumerate(vals):
        on = (v == 20)
        ax.add_patch(Rectangle((x0 + i * (w + 0.006), 0.700), w, 0.055,
                               facecolor=(GREEN if on else "white"),
                               edgecolor=(GREEN if on else AXIS), linewidth=1.1))
        ax.text(x0 + i * (w + 0.006) + w / 2, 0.7275, "1" if on else "0", ha="center",
                va="center", fontsize=7.4, fontweight="bold",
                color=("white" if on else MUTED))
        ax.text(x0 + i * (w + 0.006) + w / 2, 0.686, f"{v:+d}", ha="center", va="top",
                fontsize=6.2, color=MUTED)
    ax.text(0.755, 0.640, "13 kutucuktan 7'si gösterildi · tam biri 1  →  Σ x[e,v] = 1  (A1)",
            ha="center", fontsize=7.6, color=INK)
    for i, t in enumerate(["Saat = Σ v · x[e,v]  →  doğrusal",
                           "Ceza = Σ |v−cur| · x[e,v]  →  doğrusal,",
                           "           EK DEĞİŞKEN ve BIG-M YOK",
                           "Kova = x[e,v]'nin kendisi  →  F doğrudan yazılır"]):
        pre = "   " if i == 2 else "• "
        ax.text(0.555, 0.585 - i * 0.058, pre + t, fontsize=7.4, color=INK2, va="top")

    ax.add_patch(FancyBboxPatch((0.06, 0.03), 0.88, 0.20,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=PAPER, edgecolor=GRID, linewidth=1.0))
    ax.text(0.5, 0.165, "Neden \"tek-sıcak\"? Çünkü 13 lambadan tam biri yanar.",
            ha="center", fontsize=8.4, color=INK, fontweight="bold")
    ax.text(0.5, 0.085, "Bu tercih sayesinde tarife-değişim cezası hiçbir ek değişken ve "
                        "big-M gerektirmeden yazılabildi.\nSürekli değişken seçseydik model "
                        "hem daha büyük hem daha zor çözülür olacaktı.",
            ha="center", va="center", fontsize=7.6, color=INK2, linespacing=1.6)
    save(fig, "h2_onehot.png")


# ---------------------------------------------------------------- H3 big-M
def h3():
    fig, ax = plt.subplots(figsize=(7.2, 3.6), layout="constrained")
    ax.set_xlim(-120, 620); ax.set_ylim(0, 10); ax.axis("off"); ax.grid(False)
    ax.text(250, 9.75, "big-M: \"eger-ise\" kuralini dogrusal hale getirme numarasi".replace(
        "eger-ise", "eğer-ise").replace("dogrusal", "doğrusal").replace(
        "kuralini", "kuralını").replace("numarasi", "numarası"),
        ha="center", va="top", fontsize=10, fontweight="bold", color=INK)
    ax.text(250, 8.95, "İstenen mantık:  y = 1  ise  boşluk ≥ 60 dakika   ·   "
                       "kısıt:  boşluk ≥ 60 − Mlo·(1−y)",
            ha="center", va="top", fontsize=8.4, color=INK2)

    # --- y = 1 ---------------------------------------------------------
    ax.text(-115, 7.90, "y = 1   (bağlantı sunuluyor)", fontsize=8.8, color=GREEN,
            fontweight="bold", va="center")
    ax.add_patch(Rectangle((60, 6.05), 240, 0.9, facecolor=GREEN, alpha=0.20,
                           edgecolor="none"))
    ax.plot([60, 60], [5.95, 7.05], color=GREEN, lw=2.0)
    ax.text(60, 7.18, "60", ha="center", fontsize=7.6, color=GREEN, fontweight="bold")
    ax.text(180, 6.50, "geçerli bölge  [60, 300]", ha="center", va="center", fontsize=7.6,
            color=GREEN)
    ax.text(-115, 5.40, "boşluk ≥ 60 − Mlo·(1−1) = 60 − 0 = 60      →  kısıt DEVREDE",
            fontsize=7.8, color=INK2, family="monospace", va="center")

    # --- y = 0 ---------------------------------------------------------
    ax.text(-115, 4.35, "y = 0   (bağlantı sunulmuyor)", fontsize=8.8, color=MUTED,
            fontweight="bold", va="center")
    ax.add_patch(Rectangle((-110, 2.85), 710, 0.9, facecolor=MUTED, alpha=0.14,
                           edgecolor="none"))
    ax.plot([-110, -110], [2.75, 3.85], color=MUTED, lw=1.8, ls=(0, (3, 2)))
    ax.text(-104, 3.30, "60 − Mlo", ha="left", va="center", fontsize=7.2, color=MUTED)
    ax.text(290, 3.30, "her değer serbest — kısıt hiçbir şeyi engellemiyor",
            ha="center", va="center", fontsize=7.6, color=MUTED)
    ax.text(-115, 2.20, "boşluk ≥ 60 − Mlo·(1−0) = çok küçük bir sayı  →  kısıt ETKİSİZ",
            fontsize=7.8, color=INK2, family="monospace", va="center")

    # --- eksen ---------------------------------------------------------
    ax.annotate("", xy=(600, 1.25), xytext=(-115, 1.25),
                arrowprops=dict(arrowstyle="-|>", color=AXIS, lw=1.2))
    for v in range(0, 601, 100):
        ax.plot([v, v], [1.20, 1.40], color=AXIS, lw=0.9)
        ax.text(v, 0.90, str(v), ha="center", fontsize=6.8, color=MUTED)
    ax.text(600, 0.30, "boşluk (dk)", fontsize=7.4, color=MUTED, ha="right")
    ax.text(-115, 0.30, "Mlo = max(0, 60 − ulaşılabilir en küçük boşluk) — mümkün olan "
                        "EN KÜÇÜK M seçilir; büyük M çözücüyü yavaşlatır.",
            fontsize=7.4, color=INK, va="center")
    save(fig, "h3_bigm.png")


# ---------------------------------------------------------------- H4 warm-start kazanci
def h4():
    fig, ax = plt.subplots(figsize=(7.2, 2.8), layout="constrained")
    labels = ["Mevcut tarife\n(baseline)", "Aşama-1\nbyday", "Aşama-2\ntam-hafta cilalama"]
    vals = [3251527, 3390287, 3405039]
    cols = [MUTED, BLUE, GREEN]
    b = ax.bar(labels, vals, width=0.5, color=cols, alpha=0.9, edgecolor="white",
               linewidth=1.2)
    for r, v in zip(b, vals):
        ax.annotate(f"{v:,.0f}".replace(",", "."), (r.get_x() + r.get_width() / 2, v),
                    ha="center", va="bottom", fontsize=9, fontweight="bold", color=INK,
                    xytext=(0, 3), textcoords="offset points")
    ax.annotate("", xy=(1, 3390287), xytext=(0, 3251527),
                arrowprops=dict(arrowstyle="-|>", color=BLUE, lw=1.3,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(0.5, 3332000, "+138.760\n(%+4,27)", ha="center", fontsize=7.8, color=BLUE,
            fontweight="bold", linespacing=1.3)
    ax.annotate("", xy=(2, 3405039), xytext=(1, 3390287),
                arrowprops=dict(arrowstyle="-|>", color=GREEN, lw=1.3,
                                connectionstyle="arc3,rad=-0.25"))
    ax.text(1.5, 3372000, "+14.752\nwarm-start kazancı", ha="center", fontsize=7.8,
            color=GREEN, fontweight="bold", linespacing=1.3)
    ax.set_ylim(3200000, 3440000)
    ax.set_ylabel("gelir-ağırlıklı rekabetçilik")
    ax.set_title("İki aşamalı çözümün katkısı — toplam %+4,72", fontsize=9.6, loc="left",
                 pad=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0, labelsize=8)
    save(fig, "h4_warmstart_kazanc.png")


if __name__ == "__main__":
    for fn in [h1, h2, h3, h4]:
        fn()
    print("bitti ->", IMG)
