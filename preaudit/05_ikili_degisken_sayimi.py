# -*- coding: utf-8 -*-
"""
İKİLİ DEĞİŞKEN SAYIMI — belgelerdeki 100.552 / 100.566 farkının kanıtı.

Her iki modeli de KURAR ve ikili değişkenleri aile aile SAYAR. Model ÇÖZÜLMEZ,
hiçbir çıktı dosyasına DOKUNULMAZ — bu betik salt okuma/doğrulama amaçlıdır.

  (a) 03_model.py `full`        : monolitik tam-hafta varyantı        -> 100.566
  (b) 08_fullweek_polish.py     : NİHAİ TESLİM modeli (cilalama)      -> 100.552

Fark (14) tamamen açıklanabilir: (b)'de bir olay "gün-görünümü kopyası" olduğu için
aşama-1 değerine sabitlenir (pin_merged_events) -> 13 aday saat 1'e iner (-12 x) ve
o olaya bağlı iki koşullu yenme göstergesi gereksizleşir (-2 w).

Çalıştırma:  python preaudit/05_ikili_degisken_sayimi.py
Not: (b) için `output/optimized_schedule.csv` (aşama-1 çıktısı) mevcut olmalıdır.
"""
import os
import sys
import importlib.util
from collections import Counter

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "src")

import pyomo.environ as pyo


def load(name, mod_name):
    spec = importlib.util.spec_from_file_location(mod_name, os.path.join(SRC, name))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)          # __name__ != "__main__" -> main() çalışmaz
    return mod


def say(m):
    """Modeldeki ikili değişkenleri Pyomo bileşen adına göre sayar."""
    cnt, total = Counter(), 0
    for v in m.component_data_objects(pyo.Var):
        if v.is_binary():
            total += 1
            cnt[v.parent_component().local_name] += 1
    return cnt, total


def yaz(baslik, cnt, total, m, ekstra=""):
    print(f"\n{'=' * 62}\n{baslik}\n{'=' * 62}")
    for k, n in sorted(cnt.items(), key=lambda kv: -kv[1]):
        print(f"   {k:<8} {n:>9,}")
    print(f"   {'TOPLAM':<8} {total:>9,}")
    print(f"   kısıt (m.cons) : {sum(1 for _ in m.cons.values()):,}")
    print(f"   A2 bağ: {m._n_a2} · F bağ: {m._n_f}{ekstra}")
    # m.w seyrek havuzunun mantıksal alt-türleri (w / beta / gam)
    if hasattr(m, "w"):
        sub = Counter(idx[0] for idx in m.w)
        if sub:
            print("   m.w havuzu     :", ", ".join(f"{k}={v:,}" for k, v in sorted(sub.items())))


def main():
    # ---------------------------------------------------------------- (a) monolitik
    M3 = load("03_model.py", "model03")
    CFG = M3.CFG
    CFG.update(M3.PRESETS["full"])
    CFG["days"] = M3.all_operation_days()
    CFG["shift_penalty"] = M3.DEFAULT_LAMBDA

    print(">> (a) monolitik tam-hafta örneği kuruluyor …")
    inst_a = M3.build_instance()
    print(f"   pazar-gün: {len(inst_a.md)} · bağlantı: {len(inst_a.conns)} · "
          f"olay: {len(inst_a.ev_by_id)} "
          f"(ayarlanabilir {sum(1 for e in inst_a.ev_by_id.values() if e['adjustable'])})")
    m_a = M3.build_model(inst_a)
    cnt_a, tot_a = say(m_a)
    yaz("(a) 03_model.py `full` — MONOLİTİK VARYANT", cnt_a, tot_a, m_a,
        f" · G bağ: {m_a._n_g} (atlanan {m_a._n_g_skip})")

    # ---------------------------------------------------------------- (b) teslim modeli
    if not os.path.exists(os.path.join(ROOT, "output", "optimized_schedule.csv")):
        print("\n[!] output/optimized_schedule.csv yok — (b) atlanıyor. "
              "Önce `python src/03_model.py byday 0.3` koşun.")
        return 0

    P8 = load("08_fullweek_polish.py", "polish08")
    lam = P8.M3.DEFAULT_LAMBDA
    print("\n>> (b) tam-hafta cilalama modeli kuruluyor …")
    shift, offered, byday_exempt, _ = P8.load_phase1(lam)
    C8 = P8.CFG
    C8.update(P8.M3.PRESETS["full"])
    C8["days"] = P8.M3.all_operation_days()
    C8["shift_penalty"] = lam
    C8["G_regularity"] = False            # G'yi 08 kendisi (ilk-gün çapalı) kurar

    days = C8["days"]
    inst_b = P8.M3.build_instance()
    caps, floors = P8.M3.compute_overnight_guards(days)
    inst_b.rotcap = {k: v for d in caps for k, v in caps[d].items()}
    inst_b.rotlock = {k: v for d in floors for k, v in floors[d].items()}
    n_pin = P8.pin_merged_events(inst_b, days, shift)
    tstar, missing = P8.warm_times(inst_b, shift)
    if missing:
        print(f"[!] {len(missing)} olay tarife dosyasında yok — byday çıktısı bayat.")
        return 1
    m_b = P8.M3.build_model(inst_b)
    n_star, _ = P8.add_star_G(inst_b, m_b, tstar, byday_exempt)
    cnt_b, tot_b = say(m_b)
    yaz("(b) 08_fullweek_polish.py — NİHAİ TESLİM MODELİ", cnt_b, tot_b, m_b,
        f" · G ilk-gün-çapalı bağ: {n_star}")
    print(f"   gün-görünümü kopyası olduğu için sabitlenen olay: {n_pin}")

    # ---------------------------------------------------------------- karşılaştırma
    print(f"\n{'=' * 62}\nKARŞILAŞTIRMA\n{'=' * 62}")
    print(f"   {'aile':<8} {'(b) teslim':>12} {'(a) monolitik':>15} {'fark':>8}")
    for k in sorted(set(cnt_a) | set(cnt_b), key=lambda k: -cnt_b.get(k, 0)):
        a, b = cnt_a.get(k, 0), cnt_b.get(k, 0)
        print(f"   {k:<8} {b:>12,} {a:>15,} {b - a:>+8,}")
    print(f"   {'TOPLAM':<8} {tot_b:>12,} {tot_a:>15,} {tot_b - tot_a:>+8,}")
    print("\n   Raporlanan değerler: reports/fullweek_polish.md -> 100.552 (teslim modeli)")
    print("                        docs/Buke_KOD_REHBERI      -> 100.566 (monolitik varyant)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
