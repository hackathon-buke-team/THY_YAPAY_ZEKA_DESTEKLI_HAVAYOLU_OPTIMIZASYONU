# -*- coding: utf-8 -*-
"""Ikinci dokuman icin semalar: problem boyutu, arama uzayi, Pyomo/cozucu."""
import os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Polygon

from figures import (IMG, BLUE, RED, GREEN, ORANGE, INK, INK2, MUTED, GRID, AXIS, PAPER,
                     save, box, arrow, blank, plt as _plt)


# ---------------------------------------------------------------- G1 ne degistiriyoruz
def g1():
    fig, ax = blank((7.2, 3.6))
    ax.add_patch(FancyBboxPatch((0.02, 0.06), 0.44, 0.80,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="#eef6f1", edgecolor="#aacfbf", linewidth=1.3))
    ax.add_patch(FancyBboxPatch((0.54, 0.06), 0.44, 0.80,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="#f6f5f1", edgecolor="#d4d3cc", linewidth=1.3))
    ax.text(0.24, 0.925, "DEĞİŞTİRDİĞİMİZ", ha="center", fontsize=10.5,
            fontweight="bold", color=GREEN)
    ax.text(0.76, 0.925, "DEĞİŞTİRMEDİĞİMİZ", ha="center", fontsize=10.5,
            fontweight="bold", color=MUTED)
    ax.text(0.24, 0.735, "TEK ŞEY", ha="center", fontsize=8.4, color=INK2, style="italic")
    ax.text(0.24, 0.62, "THY uçuşlarının\nIST kalkış / varış\nSAATLERİ",
            ha="center", va="center", fontsize=11.5, fontweight="bold", color=INK,
            linespacing=1.5)
    ax.text(0.24, 0.375, "± 60 dakika pencerede\n10 dakikalık ızgarada",
            ha="center", va="center", fontsize=8.6, color=GREEN, linespacing=1.6)
    ax.text(0.24, 0.185, "4.553 karar olayı", ha="center", fontsize=10,
            fontweight="bold", color=GREEN)
    ax.text(0.24, 0.105, "(2.731 kalkış + 2.742 varış olayının\nayarlanabilir olanları)",
            ha="center", va="center", fontsize=7.2, color=MUTED, linespacing=1.4)
    items = ["Uçuş rotaları · destinasyonlar", "Uçuş sayısı · frekanslar",
             "Uçak tipi · koltuk kapasitesi", "Bilet fiyatları",
             "Uçuş süreleri (legsum sabit)", "Uçak rotasyon eşleşmeleri",
             "Rakiplerin tarifeleri", "data/ altındaki ham dosyalar"]
    y = 0.78
    for it in items:
        ax.text(0.575, y, "✕", fontsize=8.6, color=RED, va="center")
        ax.text(0.605, y, it, fontsize=8.4, color=INK2, va="center")
        y -= 0.085
    save(fig, "g1_ne_degistiriyoruz.png")


# ---------------------------------------------------------------- G2 veri hunisi
def g2():
    fig, ax = plt.subplots(figsize=(7.2, 4.3), layout="constrained")
    ax.set_xlim(0, 10.4); ax.set_ylim(0.58, 8.9); ax.axis("off"); ax.grid(False)

    ax.text(5.2, 8.75, "Veriden karara: 89.094 ham satır → 6.966 satılabilir bağlantı",
            ha="center", va="top", fontsize=9.8, fontweight="bold", color=INK)

    # --- 1. satir: girdi dosyalari (89.094) --------------------------------
    y0 = 7.35
    tot = 89094
    parts = [("Bağlantı tablosu", 57317, BLUE),
             ("Ranking ödül tablosu", 22140, MUTED),
             ("Yolcu / ρ", 8075, MUTED),
             ("Flight Pairs", 1562, MUTED)]
    x = 0.35
    W = 9.3
    for lbl, v, c in parts:
        w = W * v / tot
        ax.add_patch(Rectangle((x, y0), w, 0.62, facecolor=c,
                               alpha=(0.85 if c is BLUE else 0.35),
                               edgecolor="white", linewidth=1.4))
        if w > 1.4:
            ax.text(x + w / 2, y0 + 0.31, f"{v:,}".replace(",", "."), ha="center",
                    va="center", fontsize=8.6, fontweight="bold",
                    color=("white" if c is BLUE else INK2))
        x += w
    ax.text(0.35, y0 + 0.78, "4 Excel dosyası · toplam 89.094 satır", fontsize=8.2,
            color=INK, fontweight="bold")
    ax.text(0.35 + W * 57317 / tot / 2, y0 - 0.22, "▼ huni buradan devam eder",
            ha="center", va="top", fontsize=7.4, color=BLUE, fontweight="bold")
    ax.text(0.35 + W * 57317 / tot + (W * 31777 / tot) / 2, y0 - 0.22,
            "referans tabloları — huniye girmez,\nmodelde başka amaçla kullanılır",
            ha="center", va="top", fontsize=6.9, color=MUTED, linespacing=1.35)

    # --- huni -------------------------------------------------------------
    steps = [
        (57317, "Bağlantı tablosu satırı", "tüm havayollarının IST aktarmalı seçenekleri",
         MUTED, None),
        (7850, "THY (TK) bağlantı satırı", "geri kalan 49.467 rakibindir — değiştiremeyiz",
         BLUE, "−49.467  rakip"),
        (7693, "Tekilleştirilmiş TK adayı", "hafta kopyası olan birebir özdeş satırlar atıldı",
         BLUE, "−157  özdeş kopya"),
        (7577, "Modele giren bağlantı (π)", "ρ'su olmayan 48 pazar amaç evreninden çıktı",
         BLUE, "−116  ρ'suz pazar"),
        (6966, "Çözümde SUNULAN bağlantı", "modelin sunmayı SEÇTİĞİ bağlantılar",
         GREEN, "−611  model sunmadı"),
    ]
    top = 6.35
    hgt = 1.16
    maxw = 6.7
    for i, (v, lbl, alt, c, drop) in enumerate(steps):
        w = maxw * (0.32 + 0.68 * (np.log10(v) - 3.6) / (np.log10(57317) - 3.6))
        x0 = 0.35 + (maxw - w) / 2
        yb = top - (i + 1) * hgt
        ax.add_patch(Rectangle((x0, yb + 0.30), w, hgt - 0.56, facecolor=c, alpha=0.85,
                               edgecolor="white", linewidth=1.2))
        ax.text(x0 + w / 2, yb + hgt / 2 + 0.02, f"{v:,}".replace(",", "."),
                ha="center", va="center", fontsize=10.5, fontweight="bold", color="white")
        ax.text(x0 + w + 0.22, yb + hgt / 2 + 0.16, lbl, ha="left", va="center",
                fontsize=8.3, color=INK, fontweight="bold")
        ax.text(x0 + w + 0.22, yb + hgt / 2 - 0.16, alt, ha="left", va="center",
                fontsize=7.2, color=MUTED)
        if drop:
            ax.text(x0 - 0.22, yb + hgt - 0.14, drop, ha="right", va="center",
                    fontsize=7.2, color=RED)
    save(fig, "g2_veri_hunisi.png")


# ---------------------------------------------------------------- G3 arama uzayi
def g3():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.9), layout="constrained",
                             gridspec_kw={"width_ratios": [1, 1]})
    left = [("Evrenin yaşı (saniye)", 17),
            ("Gözlemlenebilir evrendeki atom", 80),
            ("Satranç oyun ağacı (Shannon)", 120),
            ("Go'da yasal tahta konumu", 170)]
    right = [("Tarife karar uzayımız\n13⁴⁵⁵³", 5072, RED),
             ("Çözücünün gördüğü\nham ikili uzay  2¹⁰⁰⁵⁶⁶", 30273, BLUE)]
    ax = axes[0]
    y = np.arange(len(left))[::-1]
    ax.barh(y, [v for _, v in left], height=0.55, color=MUTED, alpha=0.75,
            edgecolor="white", linewidth=0.9)
    for yy, (lbl, v) in zip(y, left):
        ax.text(v + 5, yy, f"10^{v}", va="center", fontsize=8, color=INK2, fontweight="bold")
        ax.text(0, yy + 0.42, lbl, va="bottom", fontsize=7.6, color=INK2)
    ax.set_xlim(0, 230); ax.set_ylim(-0.6, 3.9)
    ax.set_title("Bildiğimiz \"çok büyük\" sayılar", fontsize=9, loc="left", pad=6)
    ax = axes[1]
    y2 = np.arange(len(right))[::-1]
    ax.barh(y2, [v for _, v, _ in right], height=0.42, color=[c for _, _, c in right],
            alpha=0.88, edgecolor="white", linewidth=0.9)
    for yy, (lbl, v, c) in zip(y2, right):
        ax.text(v + 700, yy, f"10^{v:,}".replace(",", "."), va="center", fontsize=8.6,
                color=c, fontweight="bold")
        ax.text(0, yy + 0.35, lbl, va="bottom", fontsize=7.8, color=INK,
                fontweight="bold", linespacing=1.3)
    ax.set_xlim(0, 39000); ax.set_ylim(-0.6, 1.95)
    ax.set_title("BİZİM PROBLEMİMİZ  —  dikkat: eksen ~170 kat geniş",
                 fontsize=9, loc="left", pad=6, color=RED)
    for a in axes:
        a.set_yticks([]); a.set_xticks([])
        for s in ("top", "right", "left", "bottom"):
            a.spines[s].set_visible(False)
        a.grid(False)
    fig.supxlabel("çubuk uzunluğu = 10'un ÜSSÜ (sayının kendisi değil)", fontsize=7.6,
                  color=MUTED)
    save(fig, "g3_arama_uzayi.png")


# ---------------------------------------------------------------- G4 uzay daralmasi
def g4():
    fig, ax = blank((7.2, 3.3))
    steps = [
        ("Sürekli zaman\n(±60 dk, 1 dk çözünürlük)", "121⁴⁵⁵³", "10⁹⁴⁸³", RED),
        ("10 dk ızgara\n(tüm olaylar ayarlanabilir)", "13⁵³⁷⁶", "10⁵⁹⁸⁸", ORANGE),
        ("Rotasyon partneri olmayan\n823 olay SABİTLENDİ", "13⁴⁵⁵³", "10⁵⁰⁷²", BLUE),
        ("A1·A2·B1·C·D·E1·F·G\nkısıtları", "uygun bölge", "≪ 10⁵⁰⁷²", GREEN),
    ]
    w = 0.215
    x = 0.015
    for i, (t, formula, mag, c) in enumerate(steps):
        box(ax, x, 0.42, w, 0.30, t, ec=c, fs=7.4)
        ax.text(x + w / 2, 0.335, formula, ha="center", fontsize=10.5,
                fontweight="bold", color=c)
        ax.text(x + w / 2, 0.255, "≈ " + mag, ha="center", fontsize=8.6, color=INK2)
        if i < 3:
            arrow(ax, x + w + 0.006, 0.57, x + w + 0.046, 0.57, color=AXIS, lw=1.6)
        x += w + 0.052
    ax.text(0.5, 0.88, "Arama uzayını neyle küçültüyoruz?", ha="center",
            fontsize=10.5, fontweight="bold", color=INK)
    ax.text(0.5, 0.80, "Her adım bir modelleme kararı — ve her biri problemi "
                       "astronomik ölçüde küçültüyor",
            ha="center", fontsize=8.2, color=MUTED)
    ax.text(0.5, 0.105, "Izgara tek başına uzayı 10⁽⁹⁴⁸³⁻⁵⁹⁸⁸⁾ = 10³⁴⁹⁵ kat, "
                        "sabit uçuşlar ise 13⁸²³ = 10⁹¹⁷ kat küçültür.\n"
                        "Kısıtlar ise uzayı küçültmez — İÇİNDEKİ hangi noktaların "
                        "GEÇERLİ olduğunu belirler.",
            ha="center", va="center", fontsize=7.8, color=INK2, linespacing=1.7)
    save(fig, "g4_uzay_daralmasi.png")


# ---------------------------------------------------------------- G5 is bolumu
def g5():
    fig, ax = blank((7.2, 3.5))
    box(ax, 0.03, 0.50, 0.28, 0.34,
        "SİZ\n\n`build_model()`\nkısıtları ve amacı\nPython'da yazarsınız",
        ec=INK2, fs=7.8)
    box(ax, 0.36, 0.50, 0.28, 0.34,
        "PYOMO\n\nmodeli katsayı\nmatrisine çevirir\n(cebirsel → sayısal)",
        ec=BLUE, fs=7.8, bold=False)
    box(ax, 0.69, 0.50, 0.28, 0.34,
        "HiGHS (çözücü)\n\nLP gevşemesi +\ndallanma-sınırlama\nile ÇÖZER",
        ec=RED, fs=7.8)
    arrow(ax, 0.315, 0.67, 0.355, 0.67, color=AXIS, lw=1.6)
    arrow(ax, 0.645, 0.67, 0.685, 0.67, color=AXIS, lw=1.6)
    arrow(ax, 0.83, 0.48, 0.83, 0.40, color=GREEN, lw=1.5)
    arrow(ax, 0.68, 0.355, 0.32, 0.355, color=GREEN, lw=1.5)
    ax.text(0.50, 0.315, "sonuç geri okunur:  pyo.value(m.x[...])",
            ha="center", fontsize=8.2, color=GREEN, fontweight="bold")
    ax.text(0.5, 0.93, "İş bölümü: modelleyen ayrı, çözen ayrı", ha="center",
            fontsize=10.5, fontweight="bold", color=INK)
    ax.add_patch(FancyBboxPatch((0.04, 0.03), 0.92, 0.22,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=PAPER, edgecolor=GRID, linewidth=1.0))
    ax.text(0.5, 0.185, "Pyomo tek satırlık kısıtınızı çözücünün anlayacağı ham satıra çevirir:",
            ha="center", fontsize=8, color=INK2)
    ax.text(0.5, 0.115, "m.cons.add(gap[π] >= 60 - Mlo*(1 - m.y[π]))",
            ha="center", fontsize=8.6, color=BLUE, family="monospace")
    ax.text(0.5, 0.060, "→   … + 480·x[17,480] + 490·x[17,490] + … − 300·x[9,300] − … "
                        "+ 240·y[42]  ≥  60",
            ha="center", fontsize=7.6, color=RED, family="monospace")
    save(fig, "g5_pyomo_cozucu.png")


# ---------------------------------------------------------------- G6 branch and bound
def g6():
    fig, ax = blank((7.2, 3.5))
    ax.text(0.5, 0.965, "Çözücü nasıl 10⁵⁰⁷² ihtimali eliyor? — dallanma ve sınırlama",
            ha="center", fontsize=10.2, fontweight="bold", color=INK)
    nodes = {
        "r":  (0.50, 0.79, "kök: LP = 3.462\n(üst sınır)", BLUE, False),
        "a":  (0.26, 0.575, "x=0\nLP = 3.441", BLUE, False),
        "b":  (0.74, 0.575, "x=1\nLP = 3.399", MUTED, True),
        "a1": (0.13, 0.36, "LP = 3.428", BLUE, False),
        "a2": (0.39, 0.36, "LP = 3.402", MUTED, True),
    }
    for k, (x, y, t, c, pruned) in nodes.items():
        w, h = 0.20, 0.13
        ax.add_patch(FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                                    boxstyle="round,pad=0.008,rounding_size=0.02",
                                    facecolor=("#f2f1ec" if pruned else "white"),
                                    edgecolor=c, linewidth=1.3, zorder=2,
                                    linestyle=("--" if pruned else "-")))
        ax.text(x, y, t, ha="center", va="center", fontsize=7.2, zorder=3,
                color=(MUTED if pruned else INK), linespacing=1.35)
    for a, b in [("r", "a"), ("r", "b"), ("a", "a1"), ("a", "a2")]:
        x1, y1 = nodes[a][0], nodes[a][1] - 0.065
        x2, y2 = nodes[b][0], nodes[b][1] + 0.065
        ax.plot([x1, x2], [y1, y2], color=AXIS, lw=1.1, zorder=1)
    for k in ("b", "a2"):
        x, y = nodes[k][0], nodes[k][1]
        ax.text(x, y - 0.105, "✕ BUDANDI", ha="center", fontsize=7.4,
                color=RED, fontweight="bold")
    ax.plot([0.03, 0.97], [0.135, 0.135], color=GREEN, lw=1.4, ls=(0, (5, 3)))
    ax.text(0.03, 0.165, "eldeki en iyi çözüm (incumbent) = 3.405",
            fontsize=7.8, color=GREEN, fontweight="bold")
    ax.text(0.03, 0.045, "Bir dalın LP üst sınırı incumbent'tan KÖTÜYSE o dalın altındaki "
                         "milyarlarca kombinasyon tek hamlede elenir.",
            fontsize=7.6, color=INK2)
    save(fig, "g6_branch_bound.png")


# ---------------------------------------------------------------- G7 MIP gap
def g7():
    fig, ax = plt.subplots(figsize=(7.2, 3.0), layout="constrained")
    t = np.linspace(0, 1800, 300)
    bound = 3.4460 - 0.0016 * np.log1p(t / 22)
    inc = 3.3903 + 0.0148 * (1 - np.exp(-t / 260))
    ax.plot(t, bound, color=RED, lw=1.8, label="üst sınır (bound) — çözücünün kanıtı")
    ax.plot(t, inc, color=BLUE, lw=1.8, label="eldeki en iyi çözüm (incumbent)")
    ax.fill_between(t, inc, bound, color=ORANGE, alpha=0.14)
    ax.annotate("", xy=(760, bound[-40]), xytext=(760, inc[-40]),
                arrowprops=dict(arrowstyle="<|-|>", color=ORANGE, lw=1.4))
    ax.text(730, (bound[-40] + inc[-40]) / 2, "MIP-gap\n= %1.18  ", ha="right", va="center",
            fontsize=8.4, color="#a86a12", fontweight="bold", linespacing=1.4)
    ax.axhline(3.3903, color=MUTED, lw=1.0, ls=(0, (4, 3)))
    ax.text(20, 3.3906, "aşama-1 (byday) başlangıç noktası — MIP-start", fontsize=7.4,
            color=MUTED, va="bottom")
    ax.set_xlabel("çözüm süresi (saniye)")
    ax.set_ylabel("amaç değeri (milyon)")
    ax.set_xlim(0, 1800); ax.set_ylim(3.385, 3.450)
    ax.legend(fontsize=7.8, loc="center right", frameon=True, facecolor="white",
              framealpha=0.95, edgecolor="none", bbox_to_anchor=(1.0, 0.58))
    ax.set_title("MIP-gap: greedy bir sezgiselin ASLA veremeyeceği optimalite kanıtı",
                 fontsize=9.6, loc="left", pad=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    save(fig, "g7_mip_gap.png")


# ---------------------------------------------------------------- G8 ikili dokum
def g8():
    fig, ax = plt.subplots(figsize=(7.2, 2.9), layout="constrained")
    data = [("x — uçuş saati atamaları  (4.553 olay × 13 aday)", 59189, BLUE),
            ("γ — yenilen rakip sayısı seçicileri", 11690, ORANGE),
            ("y — bağlantı sunuluyor mu?", 7577, GREEN),
            ("z — azalan getiri slotları", 7577, GREEN),
            ("w — bağlantı bu rakibi yeniyor mu? (koşullu)", 7531, ORANGE),
            ("β — bu rakip yenildi mi?", 7002, ORANGE)]
    y = np.arange(len(data))[::-1]
    vals = [d[1] for d in data]
    ax.barh(y, vals, height=0.6, color=[d[2] for d in data], alpha=0.88,
            edgecolor="white", linewidth=0.9)
    for yy, (lbl, v, c) in zip(y, data):
        ax.text(v + 700, yy, f"{v:,}".replace(",", "."), va="center", fontsize=8.4,
                color=INK, fontweight="bold")
        ax.text(600, yy, lbl, va="center", fontsize=8.0, color="white"
                if v > 20000 else INK2, ha="left")
    ax.set_xlim(0, 72000); ax.set_yticks([])
    ax.set_xticks([])
    ax.set_title("Toplam 100.566 ikili (0/1) değişken — ve 70.359 kısıt",
                 fontsize=10, loc="left", pad=8)
    for s in ("top", "right", "left", "bottom"):
        ax.spines[s].set_visible(False)
    ax.grid(False)
    save(fig, "g8_ikili_dokum.png")


# ---------------------------------------------------------------- G9 eleme
def g9():
    fig, ax = plt.subplots(figsize=(7.2, 2.5), layout="constrained")
    cats = ["Asla yenemez\n→ değişken YOK", "Her zaman yener\n→ y kullanılır",
            "Koşullu\n→ gerçek w değişkeni"]
    vals = [3384, 2100, 7531]
    cols = [MUTED, GREEN, ORANGE]
    ax.bar(cats, vals, width=0.5, color=cols, alpha=0.88, edgecolor="white", linewidth=1)
    for i, v in enumerate(vals):
        ax.annotate(f"{v:,}".replace(",", ".") + f"\n%{100*v/13015:.0f}", (i, v),
                    ha="center", va="bottom", fontsize=8.4, color=INK2,
                    xytext=(0, 3), textcoords="offset points", linespacing=1.3)
    ax.set_ylim(0, 9200)
    ax.set_ylabel("(bağlantı, rakip) çifti")
    ax.set_title("13.015 (bağlantı × rakip) çiftinin %42'si için hiç değişken yaratılmıyor",
                 fontsize=9.6, loc="left", pad=8)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0, labelsize=8)
    save(fig, "g9_eleme.png")


if __name__ == "__main__":
    for fn in [g1, g2, g3, g4, g5, g6, g7, g8, g9]:
        fn()
    print("bitti ->", IMG)


# ---------------------------------------------------------------- G10 sabit ucus
def g10():
    fig, ax = blank((7.2, 4.0))
    ax.text(0.5, 0.985, "Neden 823 uçuş olayı kımıldatılamıyor?",
            ha="center", va="top", fontsize=10.6, fontweight="bold", color=INK)

    # --- UST: partneri BILINEN ucus -------------------------------------
    ax.add_patch(FancyBboxPatch((0.02, 0.545), 0.96, 0.36,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="#eef6f1", edgecolor="#aacfbf", linewidth=1.3))
    ax.text(0.045, 0.865, "✔  Uçuş 88 — rotasyon partneri BİLİNİYOR  →  AYARLANABİLİR",
            fontsize=9, fontweight="bold", color=GREEN, va="center")
    ax.text(0.045, 0.795, "Flight Pairs.xlsx:   FlNo 88 · IST→PEK   |   FlNo 89 · PEK→IST   |   Pair = \"88-89\"",
            fontsize=7.6, color=INK2, va="center", family="monospace")
    ax.add_patch(Rectangle((0.09, 0.655), 0.30, 0.075, facecolor=BLUE, alpha=0.85,
                           edgecolor="none"))
    ax.text(0.24, 0.6925, "uçuş 88 · IST→PEK", ha="center", va="center", fontsize=7.0,
            color="white", fontweight="bold")
    ax.add_patch(Rectangle((0.41, 0.655), 0.12, 0.075, facecolor=ORANGE, alpha=0.85,
                           edgecolor="none"))
    ax.text(0.47, 0.6925, "τ = 45 dk", ha="center", va="center", fontsize=7.2,
            color="white", fontweight="bold")
    ax.add_patch(Rectangle((0.55, 0.655), 0.30, 0.075, facecolor=BLUE, alpha=0.85,
                           edgecolor="none"))
    ax.text(0.70, 0.6925, "uçuş 89 · PEK→IST", ha="center", va="center", fontsize=7.0,
            color="white", fontweight="bold")
    ax.text(0.045, 0.590, "AYNI UÇAK. Kalkışı 20 dk geciktirirsem dönüşün hâlâ yetişip "
                          "yetişmediğini HESAPLAYABİLİRİM → A2 kısıtı kurulur.",
            fontsize=7.5, color=INK2, va="center")

    # --- ALT: partneri BILINMEYEN ucus ----------------------------------
    ax.add_patch(FancyBboxPatch((0.02, 0.115), 0.96, 0.375,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor="#fbf1ee", edgecolor="#e0b6b0", linewidth=1.3))
    ax.text(0.045, 0.450, "✕  Uçuş 112 — rotasyon partneri BİLİNMİYOR  →  SABİT",
            fontsize=9, fontweight="bold", color=RED, va="center")
    ax.text(0.045, 0.380, "Flight Pairs.xlsx:   112 numaralı uçuş bu tabloda YOK",
            fontsize=7.6, color=INK2, va="center", family="monospace")
    ax.add_patch(Rectangle((0.09, 0.240), 0.30, 0.075, facecolor=BLUE, alpha=0.85,
                           edgecolor="none"))
    ax.text(0.24, 0.2775, "uçuş 112 · JFK→IST", ha="center", va="center", fontsize=7.0,
            color="white", fontweight="bold")
    ax.add_patch(Rectangle((0.41, 0.240), 0.44, 0.075, facecolor="white",
                           edgecolor=RED, linewidth=1.3, linestyle=(0, (4, 3))))
    ax.text(0.63, 0.2775, "?  Bu uçak sonra nereye gidiyor?  Bilmiyoruz.",
            ha="center", va="center", fontsize=7.2, color=RED, fontweight="bold")
    ax.text(0.045, 0.172, "Varışını 20 dk geciktirirsem uçağın SONRAKİ uçuşuna yetişip "
                          "yetişmeyeceğini KONTROL EDEMEM.\nDoğrulayamadığım bir kısıtı "
                          "bozma riski almak yerine bu uçuşa hiç dokunmuyorum.",
            fontsize=7.5, color=INK2, va="center", linespacing=1.6)

    ax.text(0.5, 0.045, "176 TK uçuş numarasının rotasyon eşi veride yok  →  "
                        "amaç evreninde 823 olay donduruldu (toplam olayların %15'i)",
            ha="center", va="center", fontsize=8.2, color=INK, fontweight="bold")
    save(fig, "g10_sabit_ucus.png")
