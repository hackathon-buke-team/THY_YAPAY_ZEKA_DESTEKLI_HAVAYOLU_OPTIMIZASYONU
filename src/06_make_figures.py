"""
RAPOR GÖRSELLERİ (6. adım) — output/ çıktılarından teknik rapor figürleri (PNG).

  fig1_gunluk_iyilesme.png    gün-bazlı Δ amaç (OPT − baseline) çubukları
  fig2_kaydirma_dagilimi.png  kaydırılan uçuşların dakika dağılımı (histogram)
  fig3_lambda_pareto.png      λ ödünleşimi: kaydırma ↔ rekabetçilik kazanımı
                              (output/sweep_results.csv varsa; yoksa atlanır)
  fig4_siralama_iyilesme.png  pazar-günlerde sıralama değişimi (b_od − son sıra)

Çalıştırma:  python src/06_make_figures.py   →  docs/figures/*.png
Stil: tek/iki renk (doğrulanmış palet), çekinik ızgara, doğrudan etiket; başlıklar Türkçe.
"""

import os
import re
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "output")
FIGDIR = os.path.join(ROOT, "docs", "figures")
os.makedirs(FIGDIR, exist_ok=True)

# doğrulanmış referans palet (aydınlık yüzey) — tek hue: mavi; kutupluluk: mavi/kırmızı
BLUE, RED = "#2a78d6", "#e34948"
INK, INK2, MUTED = "#0b0b0b", "#52514e", "#898781"
GRID, AXIS = "#e1e0d9", "#c3c2b7"

plt.rcParams.update({
    "figure.dpi": 200, "savefig.dpi": 200, "figure.facecolor": "white",
    "axes.facecolor": "white", "font.family": "DejaVu Sans",
    "axes.edgecolor": AXIS, "axes.labelcolor": INK2, "axes.titlecolor": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "text.color": INK,
    "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.7,
    "axes.axisbelow": True, "font.size": 9,
})

tr = lambda v: f"{v:,.0f}".replace(",", ".")     # 123456 -> '123.456'


def style(ax, ygrid_only=True):
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    if ygrid_only:
        ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)


def fig1_daily():
    """Gün-bazlı iyileşme: results_summary.md gün tablosundan (kendi ürettiğimiz format)."""
    txt = open(os.path.join(OUT, "results_summary.md"), encoding="utf-8").read()
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*[\d.,]+\s*\|\s*[\d.,]+\s*\|\s*([\d.,]+)\s*\|"
                      r"\s*([\d.,]+)\s*\|\s*([+\-][\d.,]+)\s*\|", txt, re.M)
    if not rows:
        print("[atla] fig1: results_summary.md gün tablosu bulunamadı")
        return
    days = [int(r[0]) for r in rows]
    delta = [float(r[3].replace(",", "")) for r in rows]
    fig, ax = plt.subplots(figsize=(6.4, 2.9), layout="constrained")
    ax.bar(days, delta, width=0.62, color=BLUE, edgecolor="white", linewidth=0.8)
    for d, v in zip(days, delta):
        ax.annotate(f"+{tr(v)}", (d, v), ha="center", va="bottom", fontsize=8, color=INK2,
                    xytext=(0, 2), textcoords="offset points")
    ax.set_title("Günlük rekabetçilik iyileşmesi (OPT − mevcut tarife)", loc="left", pad=10)
    ax.set_xlabel("Operasyon günü")
    ax.set_ylabel("Δ amaç (gelir-ağırlıklı)")
    ax.set_xticks(days)
    ax.set_ylim(0, max(delta) * 1.18)
    style(ax)
    fig.savefig(os.path.join(FIGDIR, "fig1_gunluk_iyilesme.png"))
    plt.close(fig)
    print("[ok] fig1_gunluk_iyilesme.png")


def fig2_shift_hist():
    sched = pd.read_csv(os.path.join(OUT, "optimized_schedule.csv"), encoding="utf-8-sig")
    moved = sched.loc[sched["degisim_dk"] != 0, "degisim_dk"]
    n_all = len(sched)
    fig, ax = plt.subplots(figsize=(6.4, 2.9), layout="constrained")
    bins = [b - 5 for b in range(-60, 80, 10)]
    ax.hist(moved, bins=bins, color=BLUE, edgecolor="white", linewidth=0.8)
    ax.axvline(0, color=AXIS, linewidth=1)
    ax.set_title("Kaydırılan uçuş hareketlerinin dakika dağılımı", loc="left", pad=26)
    ax.set_xlabel("Saat değişimi (dk; − erken, + geç)")
    ax.set_ylabel("Uçuş hareketi")
    ax.set_xticks(range(-60, 70, 20))
    txt = (f"{tr(len(moved))} hareket kaydırıldı (%{100 * len(moved) / n_all:.0f}); "
           f"{tr(n_all - len(moved))} tanesi (%{100 * (n_all - len(moved)) / n_all:.0f}) yerinde kaldı · "
           f"ort. |kayma| {moved.abs().mean():.0f} dk")
    ax.text(0, 1.03, txt, transform=ax.transAxes, fontsize=8, color=MUTED, va="bottom")
    style(ax)
    fig.savefig(os.path.join(FIGDIR, "fig2_kaydirma_dagilimi.png"))
    plt.close(fig)
    print("[ok] fig2_kaydirma_dagilimi.png")


def fig3_pareto():
    p = os.path.join(OUT, "sweep_results.csv")
    if not os.path.exists(p):
        print("[atla] fig3: output/sweep_results.csv yok (once: python src/07_sensitivity.py)")
        return
    sw = pd.read_csv(p, encoding="utf-8-sig").sort_values("lam")
    fig, ax = plt.subplots(figsize=(6.4, 3.1), layout="constrained")
    ax.plot(sw["shift_dk"] / 1000, sw["delta"] / 1000, color=AXIS, linewidth=1.2, zorder=1)
    sel = sw["lam"] == 0.3
    ax.scatter(sw.loc[~sel, "shift_dk"] / 1000, sw.loc[~sel, "delta"] / 1000,
               s=42, facecolor="white", edgecolor=BLUE, linewidth=1.6, zorder=2)
    ax.scatter(sw.loc[sel, "shift_dk"] / 1000, sw.loc[sel, "delta"] / 1000,
               s=64, color=BLUE, zorder=3)
    offs = {0.0: (-8, 8, "right"), 0.1: (8, 8, "left"), 0.3: (10, -3, "left"),
            0.7: (-10, -4, "right"), 1.5: (8, -14, "left")}
    for r in sw.itertuples():
        chosen = r.lam == 0.3
        dx, dy, ha = offs.get(float(r.lam), (8, 6, "left"))
        ax.annotate(("λ=" + (f"{r.lam:g}" if not chosen else "0.3 (seçilen)")),
                    (r.shift_dk / 1000, r.delta / 1000),
                    xytext=(dx, dy), textcoords="offset points", ha=ha,
                    fontsize=8, color=(INK if chosen else INK2),
                    fontweight=("bold" if chosen else "normal"))
    ax.margins(y=0.12)
    ax.set_title("Tarife-değişim cezası λ: kaydırma ↔ kazanım ödünleşimi", loc="left", pad=10)
    ax.set_xlabel("Toplam kaydırma (bin uçuş-dk)")
    ax.set_ylabel("Δ rekabetçilik (bin)")
    style(ax, ygrid_only=False)
    fig.savefig(os.path.join(FIGDIR, "fig3_lambda_pareto.png"))
    plt.close(fig)
    print("[ok] fig3_lambda_pareto.png")


def fig4_rank():
    mr = pd.read_csv(os.path.join(OUT, "market_results.csv"), encoding="utf-8-sig")
    mr = mr[(mr["N_rakip"] >= 1) & mr["baslangic_sira_bod"].notna() & mr["son_sira"].notna()]
    dr = (mr["baslangic_sira_bod"] - mr["son_sira"]).astype(int)   # + = sıralama yükseldi
    counts = dr.value_counts().sort_index()
    colors = [RED if k < 0 else (AXIS if k == 0 else BLUE) for k in counts.index]
    fig, ax = plt.subplots(figsize=(6.4, 2.9), layout="constrained")
    ax.bar(counts.index, counts.values, width=0.62, color=colors,
           edgecolor="white", linewidth=0.8)
    for k, v in counts.items():
        ax.annotate(tr(v), (k, v), ha="center", va="bottom", fontsize=8, color=INK2,
                    xytext=(0, 2), textcoords="offset points")
    n_up = int((dr > 0).sum())
    ax.set_title("Pazar-günlerde sıralama değişimi (başlangıç b − son sıra)", loc="left", pad=26)
    ax.text(0, 1.03, f"{tr(n_up)} pazar-günde sıralama yükseldi (mavi); "
            f"{tr(int((dr == 0).sum()))} değişmedi (gri); {tr(int((dr < 0).sum()))} geriledi (kırmızı)",
            transform=ax.transAxes, fontsize=8, color=MUTED, va="bottom")
    ax.set_xlabel("Sıralama değişimi (basamak; + = iyileşme)")
    ax.set_ylabel("Pazar-gün")
    ax.set_xticks(range(int(counts.index.min()), int(counts.index.max()) + 1))
    ax.set_ylim(0, counts.max() * 1.15)
    style(ax)
    fig.savefig(os.path.join(FIGDIR, "fig4_siralama_iyilesme.png"))
    plt.close(fig)
    print("[ok] fig4_siralama_iyilesme.png")


if __name__ == "__main__":
    fig1_daily()
    fig2_shift_hist()
    fig3_pareto()
    fig4_rank()
    print(f">> figürler: {os.path.relpath(FIGDIR, ROOT)}/")
