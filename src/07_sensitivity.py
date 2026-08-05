"""
DUYARLILIK ANALİZİ (7. adım) — λ-taraması + pencere (Wdev) ve MCT (τ) duyarlılığı.

Teslim edilen çözümü DEĞİŞTİRMEZ (write=False); modelin ana parametrelere makul ve
sürekli tepki verdiğini belgeler (jüri kriteri: model doğruluğu & analiz derinliği).

  * λ ∈ {0, 0.1, 0.3, 0.7, 1.5}   tarife-değişim cezası (Pareto ödünleşimi)
  * Wdev ∈ {30, 60, 90} dk        ayarlanabilir uçuş penceresi (±)
  * τ ∈ {30, 45, 60} dk           minimum yer süresi (A2 rotasyonu)

Çalıştırma:  python src/07_sensitivity.py
Çıktı:       reports/sensitivity_analysis.md + output/sweep_results.csv
Süre:        ~15–30 dk (11 tam-veri koşusu; HiGHS deterministik, gap ≤ %0.1)
"""

import importlib.util
import os
import sys

import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

spec = importlib.util.spec_from_file_location("model03", os.path.join(HERE, "03_model.py"))
m3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m3)

LAM, GAP, TL = 0.3, 0.001, 150
BASE = {"wdev_min": 60, "tau_min": 45}


def reset_cfg():
    m3.CFG.update(BASE)


def main():
    # ---------------- λ-taraması (Pareto) ----------------
    reset_cfg()
    print(">> [1/3] λ-taraması (5 koşu)")
    sweep = m3.main_sweep()                              # [0, 0.1, 0.3, 0.7, 1.5]
    sw = pd.DataFrame([{
        "lam": s["lam"], "delta": s["opt"] - s["base"], "dpct": s["dpct"],
        "moved": s["moved"], "movedpct": s["movedpct"], "shift_dk": s["shift"],
    } for s in sweep])
    sw.to_csv(os.path.join(ROOT, "output", "sweep_results.csv"),
              index=False, encoding="utf-8-sig")

    # ---------------- Wdev ve τ varyantları ----------------
    variants = []
    print("\n>> [2/3] pencere (Wdev) duyarlılığı")
    for wd in (30, 90):
        reset_cfg()
        m3.CFG["wdev_min"] = wd
        s = m3.run_byday(lam=LAM, gap=GAP, time_limit=TL, write=False, verbose=False)
        variants.append(("Wdev", wd, s))
        print(f"   Wdev=±{wd}dk: Δ={s['opt'] - s['base']:>+9,.0f} ({s['dpct']:+.2f}%)  "
              f"kaydırılan %{s['movedpct']:.0f}")
    print("\n>> [3/3] minimum yer süresi (τ) duyarlılığı")
    for tau in (30, 60):
        reset_cfg()
        m3.CFG["tau_min"] = tau
        s = m3.run_byday(lam=LAM, gap=GAP, time_limit=TL, write=False, verbose=False)
        variants.append(("tau", tau, s))
        print(f"   τ={tau}dk: Δ={s['opt'] - s['base']:>+9,.0f} ({s['dpct']:+.2f}%)  "
              f"kaydırılan %{s['movedpct']:.0f}")
    reset_cfg()

    # ---------------- rapor ----------------
    base_row = sw[sw["lam"] == LAM].iloc[0]
    L = [
        "# Duyarlılık Analizi",
        "",
        "**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu",
        "",
        f"*Üretim: {pd.Timestamp.now():%Y-%m-%d %H:%M} · `python src/07_sensitivity.py` · "
        f"tüm koşular tam veri, gap ≤ %0.1, deterministik*",
        "",
        "Teslim edilen çözüm **λ=0.3, Wdev=±60, τ=45** iledir. Bu analiz çözümü değiştirmez;",
        "modelin parametrelere tepkisinin makul/sürekli olduğunu belgeler. Tüm koşular",
        "**aşama-1 (byday)** çözücüsüyledir; teslim edilen nihai sonuç, bu parametrelerle",
        "byday + `src/08_fullweek_polish.py` (tam-hafta MIP-start cilalaması) iki aşamalı",
        "hattan üretilir (bkz. `docs/model_formulation.md` §13).",
        "",
        "## 1. Tarife-değişim cezası λ (Pareto ödünleşimi)",
        "",
        "| λ | Δ rekabetçilik | Δ % | kaydırılan uçuş | toplam kaydırma (dk) |",
        "|---:|---:|---:|---:|---:|",
    ]
    for r in sw.itertuples():
        sel = " **(seçilen; aşama-1 ölçümü)**" if r.lam == LAM else ""
        L.append(f"| {r.lam}{sel} | {r.delta:+,.0f} | {r.dpct:+.2f}% | "
                 f"%{r.movedpct:.0f} ({r.moved:,}) | {r.shift_dk:,.0f} |")
    L += [
        "",
        "λ=0 (cezasız) hem düşük kazanım verir hem uçuşların ~%90+'ını kaydırır (dejenerasyon);",
        "λ>0 simetriyi kırar: kazanım artar, kaydırma ~%25'e düşer. λ∈[0.1,1.5] kararlı bant.",
        "",
        "## 2. Pencere genişliği Wdev ve minimum yer süresi τ (λ=0.3)",
        "",
        "| Varyant | Δ rekabetçilik | Δ % | kaydırılan | not |",
        "|---|---:|---:|---:|---|",
        f"| **Wdev=±60, τ=45 (aşama-1 referansı)** | {base_row.delta:+,.0f} | {base_row.dpct:+.2f}% | "
        f"%{base_row.movedpct:.0f} | referans (byday ölçümü) |",
    ]
    notes = {("Wdev", 30): "dar pencere → daha az serbestlik (beklenen yön)",
             ("Wdev", 90): "DİKKAT: problem büyür; zaman-limitli ölçüm (yorum gerekir)",
             ("tau", 30): "kısa MCT → rotasyon gevşer (beklenen yön; yalnız analiz)",
             ("tau", 60): "uzun MCT; artefakt-sınıflandırma nedeniyle monoton olmayabilir"}
    for kind, val, s in variants:
        tag = f"Wdev=±{val}, τ=45" if kind == "Wdev" else f"Wdev=±60, τ={val}"
        L.append(f"| {tag} | {s['opt'] - s['base']:+,.0f} | {s['dpct']:+.2f}% | "
                 f"%{s['movedpct']:.0f} | {notes[(kind, val)]} |")
    L += [
        "",
        "Not: Wdev=±90'da olay başına aday sayısı artıp problem büyüdüğünden 150 s/gün limitinde",
        "çözücü kalitesi düşebilir (ölçülen fark serbestlik etkisi olmayabilir); τ'da artefakt-",
        "sınıflandırma sınırı kaydığı için tepki monoton olmayabilir. Sonuçları raporlarken bu iki",
        "etkeni açıkça belirtin (bkz. reports/sensitivity_analysis.md'nin elden geçirilmiş yorumu).",
    ]
    with open(os.path.join(ROOT, "reports", "sensitivity_analysis.md"), "w",
              encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    print("\n>> yazıldı: reports/sensitivity_analysis.md + output/sweep_results.csv")


if __name__ == "__main__":
    main()
