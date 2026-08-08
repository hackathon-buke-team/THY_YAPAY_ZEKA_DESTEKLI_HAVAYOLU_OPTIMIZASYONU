# -*- coding: utf-8 -*-
"""Kod rehberi DOCX'i icin aciklayici semalar (matplotlib -> PNG)."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "img")
os.makedirs(IMG, exist_ok=True)

BLUE, RED, GREEN, ORANGE = "#2a78d6", "#e34948", "#2e8b6f", "#d98b2b"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS, PAPER = "#e1e0d9", "#c3c2b7", "#f6f5f1"

plt.rcParams.update({
    "figure.dpi": 220, "savefig.dpi": 220, "figure.facecolor": "white",
    "axes.facecolor": "white", "font.family": "DejaVu Sans",
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
    "axes.axisbelow": True, "font.size": 8.5,
})


def save(fig, name):
    p = os.path.join(IMG, name)
    fig.savefig(p, bbox_inches="tight", pad_inches=0.06)
    plt.close(fig)
    print("[ok]", name)


def box(ax, x, y, w, h, text, fc="white", ec=BLUE, tc=INK, fs=8, lw=1.4, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=fc, edgecolor=ec, linewidth=lw, zorder=2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=fs, color=tc,
            zorder=3, fontweight=("bold" if bold else "normal"), linespacing=1.35)


def arrow(ax, x1, y1, x2, y2, color=AXIS, lw=1.3, style="-|>", ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=style, mutation_scale=11,
                                 color=color, linewidth=lw, linestyle=ls,
                                 shrinkA=1, shrinkB=1, zorder=1))


def blank(figsize):
    fig, ax = plt.subplots(figsize=figsize, layout="constrained")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off"); ax.grid(False)
    return fig, ax


# ---------------------------------------------------------------- 1) boru hatti
def f01():
    fig, ax = blank((7.2, 3.5))
    steps = [
        ("01\nVeri sağlık\nkontrolü", BLUE), ("02\nVeri\nhazırlama", BLUE),
        ("03\nMIP modeli\n(byday)", RED), ("08\nTam-hafta\ncilalama", RED),
        ("05\nBağımsız\ndoğrulama", GREEN), ("06\nRapor\nfigürleri", ORANGE),
        ("04\nDOCX / PDF\nüretimi", ORANGE),
    ]
    n = len(steps)
    w, h, gap = 0.118, 0.30, 0.0245
    x = 0.008
    for i, (t, c) in enumerate(steps):
        box(ax, x, 0.42, w, h, t, ec=c, fs=7.6, bold=True, fc="white")
        if i < n - 1:
            arrow(ax, x + w + 0.002, 0.57, x + w + gap - 0.002, 0.57, color=AXIS, lw=1.6)
        x += w + gap
    ax.text(0.5, 0.90, "run_all.py — tek komutla uçtan uca koşu", ha="center",
            fontsize=9.5, color=INK, fontweight="bold")
    ax.add_patch(Rectangle((0.0, 0.38), 1.0, 0.40, facecolor="none",
                           edgecolor=GRID, linewidth=1.0, linestyle=(0, (4, 3))))
    notes = [(0.066, "girdi:\ndata/"), (0.185, "çıktı:\nderived/"), (0.305, "çıktı:\noutput/"),
             (0.447, "output/\nyeniden"), (0.588, "reports/\nvalidation"),
             (0.729, "docs/\nfigures"), (0.870, "docs/ · reports/\n.docx + .pdf")]
    for xx, t in notes:
        ax.text(xx, 0.30, t, ha="center", va="top", fontsize=6.9, color=MUTED, linespacing=1.3)
    ax.text(0.5, 0.075, "Bir adım hata verirse akış AÇIK hata ile durur — doğrulanmamış çözüm teslim edilmez.",
            ha="center", fontsize=7.6, color=INK2, style="italic")
    save(fig, "f01_pipeline.png")


# ---------------------------------------------------------------- 2) veri katmanlari
def f02():
    fig, ax = blank((7.2, 3.4))
    cols = [
        (0.02, "data/  (SALT-OKUNUR)", BLUE,
         ["O&D Rakip Bağlantı Tablosu_updated.xlsx", "Yolcu Verisi_masked.xlsx",
          "change_ranking_input.xlsx", "Flight Pairs.xlsx"]),
        (0.35, "derived/  (türetilmiş)", GREEN,
         ["tk_connections.csv", "competitor_itineraries.csv", "competitor_times_carrier.csv",
          "market_n_od.csv", "markets.csv", "ranking_lookup.csv", "flight_rotation.csv",
          "flight_block_times.csv", "transform_log.md"]),
        (0.68, "output/  (teslim)", RED,
         ["optimized_schedule.csv", "market_results.csv", "selected_connections.csv",
          "g_band_exemptions.csv", "results_summary.md", "sweep_results.csv"]),
    ]
    for x, title, c, items in cols:
        box(ax, x, 0.80, 0.285, 0.12, title, ec=c, fc="white", fs=8.4, bold=True)
        y = 0.725
        for it in items:
            ax.text(x + 0.015, y, "· " + it, fontsize=7.0, color=INK2, va="top")
            y -= 0.056
        top = 0.755
        h = 0.056 * len(items) + 0.03
        ax.add_patch(Rectangle((x, top - h), 0.285, h, facecolor=PAPER, edgecolor=GRID,
                               linewidth=0.9, zorder=0))
    arrow(ax, 0.308, 0.86, 0.345, 0.86, color=AXIS, lw=1.6)
    arrow(ax, 0.638, 0.86, 0.675, 0.86, color=AXIS, lw=1.6)
    ax.text(0.185, 0.955, "02_data_prep.py", ha="center", fontsize=7.4, color=MUTED)
    ax.text(0.515, 0.955, "03 + 08 (MIP)", ha="center", fontsize=7.4, color=MUTED)
    ax.text(0.845, 0.955, "05 doğrular · 06 çizer", ha="center", fontsize=7.4, color=MUTED)
    ax.text(0.02, 0.075, "Altın kural: yarışmanın orijinal Excel dosyalarına ASLA yazılmaz; "
                         "her dönüşüm derived/transform_log.md içine kaydedilir.",
            fontsize=7.6, color=INK2, style="italic")
    save(fig, "f02_veri_katmanlari.png")


# ---------------------------------------------------------------- 3) baglanti anatomisi
def f03():
    fig, ax = plt.subplots(figsize=(7.2, 2.9), layout="constrained")
    ax.set_xlim(-30, 620); ax.set_ylim(0, 10); ax.axis("off"); ax.grid(False)
    ax.annotate("", xy=(615, 2.2), xytext=(-25, 2.2),
                arrowprops=dict(arrowstyle="-|>", color=AXIS, lw=1.2))
    ax.text(608, 1.35, "zaman (dk)", fontsize=7.5, color=MUTED, ha="right")
    # bacaklar
    ax.add_patch(Rectangle((0, 4.6), 150, 1.0, facecolor=BLUE, alpha=0.85, edgecolor="none"))
    ax.text(75, 5.1, "1. bacak  (FlNo1: o → IST)\nElapsedTime1 = E1", ha="center", va="center",
            color="white", fontsize=7.4, fontweight="bold", linespacing=1.3)
    ax.add_patch(Rectangle((330, 4.6), 250, 1.0, facecolor=BLUE, alpha=0.85, edgecolor="none"))
    ax.text(455, 5.1, "2. bacak  (FlNo2: IST → d)\nElapsedTime2 = E2", ha="center", va="center",
            color="white", fontsize=7.4, fontweight="bold", linespacing=1.3)
    # bosluk
    ax.add_patch(Rectangle((150, 4.6), 180, 1.0, facecolor=PAPER, edgecolor=AXIS,
                           linewidth=1.0, hatch="///"))
    ax.text(240, 5.1, "BOŞLUK (gap)\nIST'te bekleme", ha="center", va="center",
            fontsize=7.4, color=INK, linespacing=1.3)
    for xx, lb in [(150, "IST varış\nθ_arr"), (330, "IST kalkış\nθ_dep")]:
        ax.plot([xx, xx], [2.2, 6.1], color=RED, lw=1.2, ls=(0, (3, 2)))
        ax.plot([xx], [2.2], marker="o", color=RED, ms=4.5)
        ax.text(xx, 6.4, lb, ha="center", fontsize=7.3, color=RED, linespacing=1.3)
    # pencere
    ax.annotate("", xy=(330, 3.25), xytext=(150, 3.25),
                arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=1.1))
    ax.text(240, 3.45, "boşluk = θ_dep − θ_arr   →  ℓ=60 dk ≤ boşluk ≤ u=300 dk  ⟺  y_π = 1",
            ha="center", fontsize=7.6, color=INK)
    # J
    ax.annotate("", xy=(580, 0.85), xytext=(0, 0.85),
                arrowprops=dict(arrowstyle="<|-|>", color=BLUE, lw=1.2))
    ax.text(290, 0.25, "J  =  E1  +  boşluk  +  E2      (toplam yolculuk süresi, Gate-to-Gate)",
            ha="center", fontsize=7.8, color=BLUE, fontweight="bold")
    ax.text(290, 8.6, "Bir bağlantı (itinerary) π — modelin temel ürünü",
            ha="center", fontsize=9.2, color=INK, fontweight="bold")
    ax.text(290, 7.7, "legsum = E1 + E2 sabittir (uçuş süreleri); model YALNIZCA IST saatlerini "
                      "oynatarak boşluğu ve dolayısıyla J'yi değiştirir.",
            ha="center", fontsize=7.5, color=MUTED)
    save(fig, "f03_baglanti_anatomisi.png")


# ---------------------------------------------------------------- 4) de-wrap
def f04():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5), layout="constrained")
    for ax, (title, jw, gapv, note, col) in zip(axes, [
        ("Sorun: Excel 'time' alanı 24 saatte sarar", 380, 520,
         "Gate-to-Gate = 06:20 görünüyor\nama boşluğun kendisi 520 dk!\nJ < boşluk → FİZİKSEL İMKÂNSIZ", RED),
        ("Çözüm: +24 sa de-wrap (yalnız imkânsız satırda)", 1820, 520,
         "J = 380 + 1440 = 1820 dk\nartık J > boşluk → tutarlı\n(dewrap_k = 1 olarak kaydedilir)", GREEN)]):
        ax.set_xlim(0, 2000); ax.set_ylim(0, 3); ax.axis("off"); ax.grid(False)
        ax.add_patch(Rectangle((0, 1.75), gapv, 0.5, facecolor=PAPER, edgecolor=AXIS,
                               hatch="///", linewidth=1.0))
        ax.text(gapv / 2, 2.0, f"boşluk {gapv} dk", ha="center", va="center", fontsize=7.2)
        ax.add_patch(Rectangle((0, 1.0), jw, 0.5, facecolor=col, alpha=0.85, edgecolor="none"))
        ax.text(min(jw, 1900) / 2, 1.25, f"J = {jw} dk", ha="center", va="center",
                fontsize=7.2, color="white", fontweight="bold")
        ax.set_title(title, fontsize=8.3, loc="left", color=INK)
        ax.text(0, 0.35, note, fontsize=7.1, color=INK2, va="top", linespacing=1.45)
    save(fig, "f04_dewrap.png")


# ---------------------------------------------------------------- 5) izgara / aday kovalar
def f05():
    fig, ax = plt.subplots(figsize=(7.2, 2.5), layout="constrained")
    ax.set_xlim(-75, 75); ax.set_ylim(0, 3.4); ax.grid(False)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.set_yticks([])
    vals = list(range(-60, 70, 10))
    for v in vals:
        chosen = (v == 20)
        ax.add_patch(Rectangle((v - 4.2, 1.0), 8.4, 0.75,
                               facecolor=(BLUE if chosen else "white"),
                               edgecolor=(BLUE if chosen else AXIS), linewidth=1.2))
        ax.text(v, 1.375, "1" if chosen else "0", ha="center", va="center", fontsize=7.4,
                color=("white" if chosen else MUTED), fontweight="bold")
    ax.plot([0, 0], [0.55, 2.35], color=RED, lw=1.3, ls=(0, (3, 2)))
    ax.text(0, 2.45, "mevcut saat (cur)", ha="center", fontsize=7.4, color=RED)
    ax.annotate("", xy=(60, 2.05), xytext=(-60, 2.05),
                arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=1.1))
    ax.text(0, 2.15, "pencere:  ± Wdev = 60 dk", ha="center", fontsize=7.6, color=INK)
    ax.annotate("", xy=(24.2, 0.80), xytext=(15.8, 0.80),
                arrowprops=dict(arrowstyle="<|-|>", color=MUTED, lw=0.9))
    ax.text(20, 0.52, "Δ = 10 dk", ha="center", fontsize=7.0, color=MUTED)
    ax.text(20, 2.72, "seçilen kova → θ = cur + 20 dk", ha="center", fontsize=7.5, color=BLUE,
            fontweight="bold")
    ax.set_xlabel("mevcut saate göre kayma (dk)", fontsize=7.6)
    ax.set_xticks(vals)
    ax.tick_params(length=0, labelsize=7)
    ax.set_title("(A1) Her uçuş olayı için 13 aday kova — tam biri seçilir:  Σ_v x[e,v] = 1",
                 fontsize=8.6, loc="left", pad=8)
    save(fig, "f05_izgara_aday.png")


# ---------------------------------------------------------------- 6) azalan getiri
def f06():
    fig, ax = plt.subplots(figsize=(7.2, 2.5), layout="constrained")
    js = list(range(1, 9))
    w = [0.5 ** (j - 1) for j in js]
    cum = [sum(w[:i + 1]) for i in range(len(w))]
    ax.bar(js, w, width=0.55, color=BLUE, edgecolor="white", linewidth=0.8, label="j. bağlantının ödülü  (½)^(j−1)")
    ax.plot(js, cum, color=RED, lw=1.4, marker="o", ms=3.5, label="kümülatif ödül (→ 2'ye yakınsar)")
    for j, v in zip(js, w):
        ax.annotate(f"{v:g}", (j, v), ha="center", va="bottom", fontsize=7, color=INK2,
                    xytext=(0, 2), textcoords="offset points")
    ax.set_xticks(js)
    ax.set_xlabel("bir O–D pazarında sunulan kaçıncı bağlantı")
    ax.set_ylabel("ödül")
    ax.set_title("(C) Azalan getiri: 1. bağlantı çok değerli, 5.'si neredeyse değersiz",
                 fontsize=8.6, loc="left", pad=8)
    ax.legend(frameon=False, fontsize=7.2, loc="center right")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    save(fig, "f06_azalan_getiri.png")


# ---------------------------------------------------------------- 7) rakip yenme + siralama
def f07():
    fig, ax = plt.subplots(figsize=(7.2, 2.8), layout="constrained")
    names = ["Rakip A", "Rakip B", "Rakip C", "Rakip D", "Rakip E"]
    tcomp = [520, 480, 455, 410, 360]
    y = list(range(len(names)))[::-1]
    ax.barh(y, tcomp, height=0.52, color=MUTED, alpha=0.35, edgecolor="none")
    for yy, t, nm in zip(y, tcomp, names):
        ax.text(t + 8, yy, f"T_comp = {t} dk", va="center", fontsize=7.1, color=INK2)
        ax.text(-12, yy, nm, va="center", ha="right", fontsize=7.4, color=INK)
    J = 445
    ax.add_patch(Rectangle((-130, 2.62), 770, 1.76, facecolor=GREEN, alpha=0.09, edgecolor="none"))
    ax.axvline(J, color=BLUE, lw=1.8)
    ax.text(J - 10, 5.05, f"TK'nın en iyi J = {J} dk  ", color=BLUE, fontsize=8,
            fontweight="bold", va="center", ha="right")
    ax.text(J + 10, 5.05, "  J ≤ T_comp → bu iki rakip YENİLDİ  (beaten = 2)", fontsize=7.8,
            color=GREEN, ha="left", va="center", fontweight="bold")
    ax.set_xlim(-130, 640); ax.set_ylim(-0.8, 5.5)
    ax.set_yticks([])
    ax.set_xlabel("yolculuk süresi (dk) — küçük olan kazanır")
    ax.set_title("(D) Rakip yenme ve sıralama:  s = N − yenilen = 5 − 2 = 3.  "
                 "Ödül = Wʳ(N=5, b_od, s=3)", fontsize=8.6, loc="left", pad=8)
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="y", visible=False)
    ax.tick_params(length=0)
    save(fig, "f07_rakip_siralama.png")


# ---------------------------------------------------------------- 8) E1 yon dengesi
def f08():
    fig, ax = blank((7.2, 2.3))
    box(ax, 0.06, 0.45, 0.30, 0.34, "IST → LHR\nsunulan bağlantı  n_od = 12", ec=BLUE, fs=8)
    box(ax, 0.64, 0.45, 0.30, 0.34, "LHR → IST\nsunulan bağlantı  n_do = 9", ec=BLUE, fs=8)
    arrow(ax, 0.37, 0.62, 0.63, 0.62, color=AXIS, lw=1.2, style="<|-|>")
    ax.text(0.50, 0.86, "|n_od − n_do|  ≤  α · (n_od + n_do),   α = 0.20",
            ha="center", fontsize=9, color=INK, fontweight="bold")
    ax.text(0.50, 0.66, "|12 − 9| = 3   ≤   0.20 · 21 = 4.2   ✓", ha="center",
            fontsize=8.2, color=GREEN)
    ax.text(0.50, 0.20, "Neden? Tek yönü şişirip dönüşü ihmal eden bir tarife, kâğıt üstünde puan\n"
                        "kazanır ama gerçekte satılabilir bir ürün değildir (gidiş-dönüş talep eder).",
            ha="center", fontsize=7.6, color=INK2, linespacing=1.5)
    save(fig, "f08_e1_denge.png")


# ---------------------------------------------------------------- 9) F kova kapasitesi
def f09():
    fig, axes = plt.subplots(1, 2, figsize=(7.2, 2.5), layout="constrained")
    buckets = ["07:00", "07:10", "07:20", "07:30", "07:40", "07:50"]
    before_fix = [3, 4, 3, 2, 4, 3]
    before_adj = [4, 9, 5, 1, 3, 2]
    after_adj = [4, 6, 6, 4, 4, 4]
    for ax, adj, ttl in [(axes[0], before_adj, "Mevcut tarife: 07:10 kovası taşıyor"),
                         (axes[1], after_adj, "Optimize: pencerede yayılarak sığıyor")]:
        ax.bar(buckets, before_fix, width=0.6, color=MUTED, alpha=0.45,
               edgecolor="white", linewidth=0.8, label="sabit uçuşlar")
        ax.bar(buckets, adj, width=0.6, bottom=before_fix, color=BLUE,
               edgecolor="white", linewidth=0.8, label="ayarlanabilir uçuşlar")
        ax.axhline(10, color=RED, lw=1.4, ls=(0, (4, 2)))
        ax.text(5.45, 10.35, "cap_dep = 10", color=RED, fontsize=7.2, ha="right")
        ax.set_ylim(0, 15)
        ax.set_title(ttl, fontsize=8.1, loc="left", pad=6)
        ax.tick_params(length=0, labelsize=7)
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        ax.grid(axis="x", visible=False)
    axes[0].set_ylabel("kovadaki IST kalkışı")
    axes[0].legend(frameon=False, fontsize=7, loc="upper right")
    save(fig, "f09_f_kapasite.png")


# ---------------------------------------------------------------- 10) G bandi
def f10():
    fig, ax = plt.subplots(figsize=(7.2, 2.5), layout="constrained")
    days = [1, 2, 3, 4, 5, 6, 7]
    cur = [510, 520, 505, 540, 500, 515, 530]
    opt = [512, 512, 512, 522, 502, 512, 512]
    c0 = 512
    ax.add_patch(Rectangle((0.4, c0 - 15), 7.2, 30, facecolor=GREEN, alpha=0.12, edgecolor="none"))
    ax.axhline(c0, color=GREEN, lw=1.3)
    ax.text(7.62, c0, "  c₀ (1. günün\n  yerleşimi)", color=GREEN, fontsize=7, va="center",
            linespacing=1.4)
    ax.text(7.62, c0 + 15, "  +Xdev", color=GREEN, fontsize=6.8, va="center")
    ax.text(7.62, c0 - 15, "  −Xdev", color=GREEN, fontsize=6.8, va="center")
    ax.plot(days, cur, "o--", color=MUTED, ms=5, lw=1.1, label="mevcut tarife (dağınık)")
    ax.plot(days, opt, "o-", color=BLUE, ms=5.5, lw=1.6, label="optimize (±15 dk bandında)")
    ax.set_xticks(days)
    ax.set_xlim(0.4, 9.2)
    ax.set_xlabel("operasyon günü")
    ax.set_ylabel("IST saati (gece yarısından dk)")
    ax.set_title("(G) Tarife düzenliliği: aynı uçuş numarası her gün ±Xdev = 15 dk bandında",
                 fontsize=8.6, loc="left", pad=8)
    ax.legend(frameon=False, fontsize=7.2, loc="lower left")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    save(fig, "f10_g_bant.png")


# ---------------------------------------------------------------- 11) A2 rotasyon
def f11():
    fig, ax = plt.subplots(figsize=(7.2, 2.6), layout="constrained")
    ax.set_xlim(-40, 700); ax.set_ylim(0, 6); ax.axis("off"); ax.grid(False)
    ax.annotate("", xy=(690, 1.2), xytext=(-35, 1.2),
                arrowprops=dict(arrowstyle="-|>", color=AXIS, lw=1.2))
    ax.add_patch(Rectangle((0, 3.0), 230, 0.85, facecolor=BLUE, alpha=0.85, edgecolor="none"))
    ax.text(115, 3.42, "T_OB — gidiş bacağı\n(IST → o, FlNo_out)", ha="center", va="center",
            color="white", fontsize=7.2, fontweight="bold", linespacing=1.3)
    ax.add_patch(Rectangle((230, 3.0), 90, 0.85, facecolor=ORANGE, alpha=0.85, edgecolor="none"))
    ax.text(275, 3.42, "τ = 45 dk\nyer süresi", ha="center", va="center", color="white",
            fontsize=7.0, fontweight="bold", linespacing=1.3)
    ax.add_patch(Rectangle((320, 3.0), 240, 0.85, facecolor=BLUE, alpha=0.85, edgecolor="none"))
    ax.text(440, 3.42, "T_IB — dönüş bacağı\n(o → IST, FlNo_in)", ha="center", va="center",
            color="white", fontsize=7.2, fontweight="bold", linespacing=1.3)
    for xx, lb, col in [(0, "θ_out\nIST kalkış", RED), (560, "θ_in\nIST varış", RED)]:
        ax.plot([xx, xx], [1.2, 4.2], color=col, lw=1.2, ls=(0, (3, 2)))
        ax.plot([xx], [1.2], marker="o", color=col, ms=4.5)
        ax.text(xx, 4.45, lb, ha="center", fontsize=7.2, color=col, linespacing=1.3)
    ax.annotate("", xy=(560, 2.1), xytext=(0, 2.1),
                arrowprops=dict(arrowstyle="<|-|>", color=INK2, lw=1.1))
    ax.text(280, 2.28, "θ_in − θ_out  ≥  T_OB + τ + T_IB", ha="center", fontsize=8.4,
            color=INK, fontweight="bold")
    ax.text(280, 0.45, "Aynı uçak gidip döner: dönüş varışı, gidiş kalkışından en az bu kadar sonra olmalı.\n"
                       "Model bu kısıtı sağlamazsa 'çözüm' fiziksel olarak uçurulamaz.",
            ha="center", fontsize=7.4, color=INK2, linespacing=1.5)
    ax.text(280, 5.45, "(A2) Uçak rotasyonu — brief §4.1'in tam karşılığı", ha="center",
            fontsize=9.2, color=INK, fontweight="bold")
    save(fig, "f11_a2_rotasyon.png")


# ---------------------------------------------------------------- 12) iki asamali cozum
def f12():
    fig, ax = blank((7.2, 3.5))
    box(ax, 0.02, 0.55, 0.28, 0.30,
        "AŞAMA 1 — 03_model.py byday\n\n7 günü AYRI AYRI çöz\n(her gün küçük ve hızlı MIP)\n"
        "G düzenliliği günden güne\nbant ile zincirlenir",
        ec=BLUE, fs=7.3, bold=False)
    box(ax, 0.36, 0.55, 0.28, 0.30,
        "AŞAMA 2 — 08_fullweek_polish.py\n\nTÜM haftayı kapsayan TEK MIP\naşama-1 çözümü MIP-start\n"
        "(incumbent) olarak verilir",
        ec=RED, fs=7.3)
    box(ax, 0.70, 0.55, 0.28, 0.30,
        "SONUÇ\n\nKüresel iyileştirme\n+ GLOBAL MIP-gap\n(optimalite kanıtı)",
        ec=GREEN, fs=7.3)
    arrow(ax, 0.305, 0.70, 0.355, 0.70, color=AXIS, lw=1.6)
    arrow(ax, 0.645, 0.70, 0.695, 0.70, color=AXIS, lw=1.6)
    ax.text(0.5, 0.95, "Neden iki aşama?", ha="center", fontsize=10, fontweight="bold", color=INK)
    ax.text(0.5, 0.455,
            "Monolitik 7-gün MIP'inde ~102.000 ikili değişken var; HiGHS makul sürede tek bir\n"
            "uygun çözüm (incumbent) bile bulamıyor.  Güne-göre ayrıştırma hızlı ve garanti bir\n"
            "çözüm üretir ama 'greedy zincir' olduğu için küresel optimalite iddia edemez.\n"
            "Warm-start bu ikisini birleştirir: hızlı çözüm → tam modele başlangıç noktası.",
            ha="center", va="top", fontsize=7.7, color=INK2, linespacing=1.7)
    ax.add_patch(FancyBboxPatch((0.10, 0.03), 0.80, 0.16,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=PAPER, edgecolor=GRID, linewidth=1.0))
    ax.text(0.5, 0.11, "BARİYER: cilalanmış çözüm byday'in kayıtlı toplamını geçmiyorsa VEYA yeni bir A2\n"
                       "ihlali yaratıyorsa output/ dosyalarına DOKUNULMAZ — iyi çözüm asla ezilmez.",
            ha="center", va="center", fontsize=7.5, color=INK, linespacing=1.6)
    save(fig, "f12_byday_warmstart.png")


# ---------------------------------------------------------------- 13) cift kayit
def f13():
    fig, ax = blank((7.2, 3.4))
    ax.text(0.5, 0.985, "Çift kayıt ilkesi: çözümü üreten kod ile doğrulayan kod AYRIDIR",
            ha="center", va="top", fontsize=9.6, fontweight="bold", color=INK)
    box(ax, 0.04, 0.63, 0.26, 0.20, "derived/\n(veri katmanı)", ec=MUTED, fs=8)
    box(ax, 0.37, 0.775, 0.26, 0.15, "03 + 08\nMIP çözücü", ec=RED, fs=8, bold=True)
    box(ax, 0.70, 0.63, 0.26, 0.20, "output/\n(çözüm dosyaları)", ec=RED, fs=8)
    box(ax, 0.34, 0.36, 0.32, 0.15, "05_validate_solution.py\nBAĞIMSIZ HESAP",
        ec=GREEN, fs=8.4, bold=True)
    arrow(ax, 0.305, 0.78, 0.365, 0.83, color=AXIS)
    arrow(ax, 0.635, 0.83, 0.695, 0.78, color=AXIS)
    arrow(ax, 0.15, 0.615, 0.35, 0.515, color=GREEN, lw=1.4)
    arrow(ax, 0.85, 0.615, 0.65, 0.515, color=GREEN, lw=1.4)
    ax.text(0.5, 0.295, "A1 · A2 · B1 · C · D · E1 · F · G  +  amaç  +  baseline  →  PASS / FAIL",
            ha="center", fontsize=8.2, color=GREEN, fontweight="bold")
    ax.text(0.5, 0.215, "Tek bir FAIL → çıkış kodu 1 → run_all.py koşuyu durdurur.",
            ha="center", fontsize=7.8, color=INK2, style="italic")
    ax.add_patch(FancyBboxPatch((0.06, 0.02), 0.88, 0.135,
                                boxstyle="round,pad=0.012,rounding_size=0.02",
                                facecolor=PAPER, edgecolor=GRID, linewidth=1.0))
    ax.text(0.5, 0.088, "05, modelin içinden HİÇ geçmez; sabitleri (Wdev, τ, Xdev, cap) kendi "
                        "dosyasında yeniden tanımlar.\nBöylece modeldeki bir hata, doğrulamada "
                        "aynı hatayla örtülemez.",
            ha="center", va="center", fontsize=7.6, color=INK2, linespacing=1.6)
    save(fig, "f13_cift_kayit.png")


if __name__ == "__main__":
    for fn in [f01, f02, f03, f04, f05, f06, f07, f08, f09, f10, f11, f12, f13]:
        fn()
    print("bitti ->", IMG)
