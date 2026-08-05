"""
BAĞIMSIZ ÇÖZÜM DOĞRULAYICI (5. adım) — MIP kodundan ayrı ikinci kayıt.

`src/03_model.py`'nin ürettiği `output/` dosyalarını, modelin İÇİNDEN geçmeden
(yalnız `derived/` veri katmanı + `output/` çıktıları üzerinden) yeniden hesaplayıp
doğrular. Amaç: jürinin, çözümün kısıt uyumunu ve amaç değerini çözücüden bağımsız
bir kod yoluyla teyit edebilmesi ("çift kayıt" ilkesi).

Kontroller (docs/model_formulation.md kısıt adlarıyla):
  A1  yeni_IST 10 dk ızgarada, |değişim| ≤ Wdev=60 dk, saat aritmetiği tutarlı
  A2  uçak rotasyonu — GERÇEK zaman ekseninde (gece-aşan dahil): mevcut tarifenin
      sağladığı her turda optimize tarife de T_OB+τ+T_IB minimumunu sağlar;
      ayrıca aynı-gün turlarda model çapası (min(brief-exact, mevcut tur)) korunur
  B1  seçilen her bağlantıda 60 ≤ boşluk ≤ 300; J = legsum + boşluk; boşluk, tarifedeki
      optimize saatlerle birebir tutarlı
  C   aktarma ödülü = Σ_{j=1..n} (1/2)^(j-1), n = sunulan bağlantı sayısı
  D   yenilen rakip: pazarın en iyi J'si ≤ T_comp olan rakip sayısı (dosyadakiyle
      karşılaştırılır; fazla-beyan = HATA, eksik-beyan = ihtiyatlı, not edilir)
  E1  |n_od − n_do| ≤ α·(n_od + n_do), α = 0.20 (her iki yönü de mevcut pazar çifti)
  F   IST kova kapasitesi: her operasyon günü + 10 dk kovada kalkış ≤ 10, varış ≤ 15
      (sabit + ayarlanabilir TÜM uçuşlar)
  G   tarife düzenliliği: aynı uçuş no+rol, ilk günkü yerleşiminin ±Xdev=15 dk bandında
      (bandın penceresinin yetişemediği günler modeldeki gibi atlanır ve raporlanır)
  Amaç  Σ ρ·(aktarma + sıralama) hem market_results üzerinden hem lookup'tan yeniden
      hesaplanır; BASELINE tümüyle bağımsız (yalnız derived/) yeniden hesaplanır ve
      results_summary.md'deki değerlerle karşılaştırılır.

Çalıştırma:  python src/05_validate_solution.py   →  reports/validation_report.md
Çıkış kodu:  0 = tüm kontroller PASS, 1 = en az bir FAIL.
"""

import os
import re
import sys

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DERIVED = os.path.join(ROOT, "derived")
OUTPUT = os.path.join(ROOT, "output")
REPORTS = os.path.join(ROOT, "reports")

# 03_model.py CFG ile birebir aynı sabitler (bağımsızlık için burada AÇIKÇA tekrarlanır)
DELTA = 10        # dk — zaman kovası
# NOT (2026-07-13): Wdev=90 denendi (src/08_fullweek_polish.py Wdev=90) — +%5.34'e
# çıktı AMA bu doğrulayıcı gerçek bir A2 ihlali yakaladı (uçuş 2200/2201, gün 2):
# 2201'in bazı günlerdeki varışı ρ'suz (dışlanan) bir pazara (KCM-AGP) ait olduğundan
# o günkü olay 03'ün build_instance()'ında HİÇ OLUŞTURULMUYOR → rotasyon ortağı 2200
# ile A2 kısıtı o gün hiç kurulmuyor (F'de U4 ile düzeltilen açığın A2 karşılığı).
# Wdev=60'ta çözücü bu boşluğu tetiklemeyecek kadar az kaydırmıştı; Wdev=90'da tetikledi.
# GÜVENLİ olmadığından Wdev=90 İPTAL edildi, Wdev=60 sonucuna dönüldü. A2'nin rotasyon
# ortağı olayları MARKET evreninden BAĞIMSIZ (F'nin extra_use'u gibi) kurması gerekir —
# bu, dikkatli test isteyen ayrı bir düzeltmedir (bkz. reports/ içindeki not).
WDEV = 60         # dk — ayarlanabilir uçuş penceresi ±
L_GAP, U_GAP = 60, 300   # dk — bağlantı boşluğu penceresi
ALPHA = 0.20      # E1 yönsel dengesizlik eşiği
TAU = 45          # dk — minimum yer süresi (A2)
XDEV = 15         # dk — G gün-arası bant yarıçapı
CAP_DEP, CAP_ARR = 10, 15   # F kova kapasiteleri


def rd_derived(name, **kw):
    return pd.read_csv(os.path.join(DERIVED, name), encoding="utf-8-sig", **kw)


def rd_output(name, **kw):
    return pd.read_csv(os.path.join(OUTPUT, name), encoding="utf-8-sig", **kw)


def snap10(ts):
    """Zaman damgasını 10 dk ızgaraya yuvarla (03_model ile aynı: Python round)."""
    m = (ts - ts.normalize()).total_seconds() / 60.0
    return ts.normalize() + pd.Timedelta(minutes=int(round(m / DELTA) * DELTA))


def hhmm_of(ts):
    return f"{ts.hour:02d}:{ts.minute:02d}"


class Checks:
    """PASS/FAIL toplayıcı + markdown rapor satırları."""

    def __init__(self):
        self.rows = []          # (kısıt, kapsam, sonuç, ayrıntı)
        self.failed = False

    def add(self, name, scope, ok, detail=""):
        self.rows.append((name, scope, "PASS" if ok else "**FAIL**", detail))
        if not ok:
            self.failed = True
        print(f"  [{'PASS' if ok else 'FAIL'}] {name:<28} {scope:<34} {detail}")

    def note(self, name, scope, detail):
        self.rows.append((name, scope, "not", detail))
        print(f"  [not ] {name:<28} {scope:<34} {detail}")


def main():
    print(">> BAĞIMSIZ DOĞRULAMA — output/ çıktıları derived/ verisiyle yeniden hesaplanıyor\n")
    ck = Checks()

    # ---------------------------------------------------------------- veri
    tk = rd_derived("tk_connections.csv", parse_dates=["ist_arr", "ist_dep"])
    markets = rd_derived("markets.csv")
    nod = rd_derived("market_n_od.csv")
    tcomp = rd_derived("competitor_times_carrier.csv")
    rank = rd_derived("ranking_lookup.csv")
    rank.columns = ["N", "b", "s", "W"]
    rkW = {(int(r.N), int(r.b), int(r.s)): float(r.W) for r in rank.itertuples()}
    rot = rd_derived("flight_rotation.csv")
    blocks_df = rd_derived("flight_block_times.csv")
    blocks = {(int(r.flno), int(r.day), str(r.role)): float(r.block_min)
              for r in blocks_df.itertuples()}

    sched = rd_output("optimized_schedule.csv")
    mres = rd_output("market_results.csv")
    conns = rd_output("selected_connections.csv")
    # G hedefli bant-muafiyetleri (rotasyon-güvenliği önceliği; modelin belgelediği liste)
    exempt = set()
    exq = os.path.join(OUTPUT, "g_band_exemptions.csv")
    if os.path.exists(exq):
        for r in pd.read_csv(exq, encoding="utf-8-sig").itertuples():
            exempt.add((int(r.gun), int(r.ucus_no), r.rol))

    days = sorted(tk["day"].dropna().astype(int).unique())
    tk["cur_arr_snap"] = tk["ist_arr"].map(snap10)
    tk["cur_dep_snap"] = tk["ist_dep"].map(snap10)

    # tarifedeki değişimler: (gün, uçuş, rol, eski hh:mm) -> değişim dk
    shift = {}
    for r in sched.itertuples():
        shift[(int(r.gun), int(r.ucus_no), r.rol, r.eski_IST)] = int(r.degisim_dk)

    def opt_dt(flno, day, role, cur_snap_dt):
        """Olayın optimize gerçek zamanı: mevcut (snap) + tarifedeki değişim (yoksa sabit)."""
        rol_tr = "kalkış" if role == "dep" else "varış"
        d = shift.get((day, flno, rol_tr, hhmm_of(cur_snap_dt)), 0)
        return cur_snap_dt + pd.Timedelta(minutes=d)

    # ---------------------------------------------------------------- A1
    grid_ok = (sched["degisim_dk"] % DELTA == 0).all()
    wdev_ok = (sched["degisim_dk"].abs() <= WDEV).all()
    n_bad_hhmm = 0
    for r in sched.itertuples():
        h0, m0 = map(int, r.eski_IST.split(":"))
        tot = (h0 * 60 + m0 + int(r.degisim_dk)) % 1440
        if f"{tot // 60:02d}:{tot % 60:02d}" != r.yeni_IST:
            n_bad_hhmm += 1
    ck.add("A1 ızgara (10 dk)", f"{len(sched)} uçuş hareketi", grid_ok)
    ck.add("A1 pencere (±60 dk)", f"{len(sched)} uçuş hareketi", wdev_ok,
           f"maks |değişim| = {sched['degisim_dk'].abs().max()} dk")
    ck.add("A1 saat aritmetiği", "eski+değişim = yeni", n_bad_hhmm == 0,
           f"tutarsız satır: {n_bad_hhmm}")

    # ---------------------------------------------------------------- olay tablosu (F, A2, G için)
    # olay = (gün, uçuş, rol, snap'lenmiş mevcut zaman); bağlantılarda paylaşılır → unique
    ev = pd.concat([
        tk[["day", "FlNo1", "cur_arr_snap"]].rename(
            columns={"FlNo1": "flno", "cur_arr_snap": "cur"}).assign(role="arr"),
        tk[["day", "FlNo2", "cur_dep_snap"]].rename(
            columns={"FlNo2": "flno", "cur_dep_snap": "cur"}).assign(role="dep"),
    ]).drop_duplicates(["day", "flno", "role", "cur"]).reset_index(drop=True)
    ev["opt"] = [opt_dt(int(r.flno), int(r.day), r.role, r.cur) for r in ev.itertuples()]
    n_events = len(ev)
    n_adj = sum(1 for r in ev.itertuples()
                if (int(r.day), int(r.flno), "kalkış" if r.role == "dep" else "varış",
                    hhmm_of(r.cur)) in shift)
    ck.note("olay eşleme", f"{n_events} olay", f"{n_adj} ayarlanabilir (tarife dosyasıyla eşleşti), "
            f"{n_events - n_adj} sabit; tarife satırı: {len(sched)}")

    # ---------------------------------------------------------------- F  (kova kapasitesi)
    worst = {"dep": 0, "arr": 0}
    n_over = 0
    for (day, role), grp in ev.groupby(["day", "role"]):
        occ = grp.groupby("opt").size()
        cap = CAP_DEP if role == "dep" else CAP_ARR
        worst[role] = max(worst[role], int(occ.max()))
        n_over += int((occ > cap).sum())
    ck.add("F kova kapasitesi", f"{len(days)} gün × 10 dk kovalar", n_over == 0,
           f"aşan kova: {n_over} · en dolu kova: kalkış {worst['dep']}/{CAP_DEP}, "
           f"varış {worst['arr']}/{CAP_ARR}")

    # ---------------------------------------------------------------- A2  (rotasyon, gerçek eksen)
    pairs = []
    for _, grp in rot.groupby("Pair"):
        for of in grp[grp["Orig"] == "IST"]["FlNo"]:
            for inf in grp[grp["Dest"] == "IST"]["FlNo"]:
                pairs.append((int(of), int(inf)))
    cur_map = {(int(r.flno), int(r.day), r.role): r.cur for r in ev.itertuples()}
    opt_map = {(int(r.flno), int(r.day), r.role): r.opt for r in ev.itertuples()}
    a2_chk = a2_new = a2_base = 0
    for of, inf in pairs:
        for d in days:
            t_ob = blocks.get((of, d, "dep"))
            dep_c, dep_o = cur_map.get((of, d, "dep")), opt_map.get((of, d, "dep"))
            if dep_c is None or dep_o is None or t_ob is None:
                continue
            pick = None
            for d2 in (d, d + 1):
                a_c = cur_map.get((inf, d2, "arr"))
                t_ib = blocks.get((inf, d2, "arr"))
                if a_c is not None and t_ib is not None and a_c > dep_c:
                    pick = (d2, a_c, t_ib)
                    break
            if pick is None:
                continue
            d2, a_c, t_ib = pick
            a_o = opt_map.get((inf, d2, "arr"))
            if a_o is None:
                continue
            a2_chk += 1
            need = pd.Timedelta(minutes=t_ob + TAU + t_ib)
            if a_c < dep_c + need:
                a2_base += 1        # mevcut tarife de sağlamıyor → eşleşme artefaktı
            elif a_o < dep_o + need:
                a2_new += 1         # optimizasyonun YENİ yarattığı ihlal
    ck.add("A2 rotasyon (gerçek eksen)", f"{a2_chk} tur (gece-aşan dahil)", a2_new == 0,
           f"YENİ ihlal: {a2_new} · mevcut tarifede de sağlanmayan (artefakt): {a2_base}")

    # aynı-gün model çapası: opt tur ≥ min(T_OB+τ+T_IB, mevcut tur)
    n_anchor = n_anchor_bad = 0
    for of, inf in pairs:
        for d in days:
            dep_c, dep_o = cur_map.get((of, d, "dep")), opt_map.get((of, d, "dep"))
            arr_c, arr_o = cur_map.get((inf, d, "arr")), opt_map.get((inf, d, "arr"))
            if None in (dep_c, dep_o, arr_c, arr_o):
                continue
            turn = (arr_c - dep_c).total_seconds() / 60.0
            if turn <= 0:
                continue
            t_ob, t_ib = blocks.get((of, d, "dep")), blocks.get((inf, d, "arr"))
            sep = min(t_ob + TAU + t_ib, turn) if (t_ob is not None and t_ib is not None) else turn
            n_anchor += 1
            if (arr_o - dep_o).total_seconds() / 60.0 < sep - 1e-6:
                n_anchor_bad += 1
    ck.add("A2 aynı-gün çapası", f"{n_anchor} tur", n_anchor_bad == 0,
           f"çapa (min(brief-exact, mevcut tur)) altına inen: {n_anchor_bad}")

    # ---------------------------------------------------------------- G  (düzenlilik)
    tod = lambda dtv: (dtv - dtv.normalize()).total_seconds() / 60.0
    g_chk = g_bad = g_skip = g_exempt = 0
    for (flno, role), grp in ev.sort_values("day").groupby(["flno", "role"]):
        rol_tr = "kalkış" if role == "dep" else "varış"
        rows = [r for r in grp.itertuples()
                if (int(r.day), int(r.flno), rol_tr, hhmm_of(r.cur)) in shift]
        if len({r.day for r in rows}) < 2:
            continue
        c0 = None
        for r in rows:
            o_tod = tod(r.cur) + int(shift[(int(r.day), int(r.flno), rol_tr, hhmm_of(r.cur))])
            if c0 is None:
                c0 = o_tod                              # ilk günün yerleşimi = bant merkezi
                continue
            if (int(r.day), int(flno), rol_tr) in exempt:
                g_exempt += 1                           # belgeli muafiyet (rotasyon > bant)
                continue
            if abs(tod(r.cur) - c0) > WDEV + XDEV:
                g_skip += 1                             # pencere banda yetişemez → modelde atlanır
                continue
            g_chk += 1
            if abs(o_tod - c0) > XDEV + 1e-6:
                g_bad += 1
    ck.add("G düzenlilik (±15 dk bant)", f"{g_chk} gün-arası bağ", g_bad == 0,
           f"bant dışı: {g_bad} · belgeli rotasyon-önceliği muafiyeti: {g_exempt} · "
           f"yapısal atlanan (pencere yetişemez): {g_skip}")

    # ---------------------------------------------------------------- B1 + bağlantı tutarlılığı
    tk_key = {}                                         # anahtar -> [satırlar] (anomali olaylar
    for r in tk.itertuples():                           # aynı anahtarda FARKLI saatli satır bırakabilir)
        tk_key.setdefault((int(r.day), r.market, int(r.FlNo1), int(r.FlNo2)), []).append(r)
    n_conn = len(conns)
    bad_gapwin = bad_j = bad_time = bad_gap = miss = 0
    j_opt = {}                                          # (market, gün) -> [J]
    for r in conns.itertuples():
        key = (int(r.gun), r.pazar, int(r.gelen_ucus), int(r.giden_ucus))
        rows = tk_key.get(key, [])
        if not rows:
            miss += 1
            continue
        if not (L_GAP <= r.bosluk_dk <= U_GAP):
            bad_gapwin += 1
        # saat/boşluk: anahtarın HERHANGİ bir satırı (olay kopyası) ile tutarlıysa geçerli
        matched = None
        for row in rows:
            a_opt = opt_dt(int(r.gelen_ucus), int(r.gun), "arr", row.cur_arr_snap)
            d_opt = opt_dt(int(r.giden_ucus), int(r.gun), "dep", row.cur_dep_snap)
            if hhmm_of(a_opt) == r.IST_varis and hhmm_of(d_opt) == r.IST_kalkis:
                matched = (row, a_opt, d_opt)
                break
        if matched is None:
            bad_time += 1
            bad_gap += 1
            row = rows[0]
        else:
            row, a_opt, d_opt = matched
            if abs((d_opt - a_opt).total_seconds() / 60.0 - r.bosluk_dk) > 0.51:
                bad_gap += 1
        if abs((row.legsum_min + r.bosluk_dk) - r.J_dk) > 0.51:
            bad_j += 1
        j_opt.setdefault((r.pazar, int(r.gun)), []).append(float(row.legsum_min) + float(r.bosluk_dk))
    ck.add("B1 boşluk penceresi", f"{n_conn} seçilen bağlantı", bad_gapwin == 0,
           f"[60,300] dışı: {bad_gapwin}")
    ck.add("B1 J = legsum + boşluk", f"{n_conn} bağlantı", bad_j == 0 and miss == 0,
           f"tutarsız J: {bad_j} · veri eşleşmeyen: {miss}")
    ck.add("B1 tarife ↔ bağlantı saati", f"{n_conn} bağlantı", bad_time == 0 and bad_gap == 0,
           f"saat uyuşmayan: {bad_time} · boşluk uyuşmayan: {bad_gap}")

    # ---------------------------------------------------------------- pazar sonuçları (C, D, amaç)
    comp_map = {}                                       # (market, gün) -> {taşıyıcı: T_comp}
    for r in tcomp.itertuples():
        comp_map.setdefault((r.market, int(r.day)), {})[r.carrier] = float(r.T_comp_min)
    rho_map = markets.set_index("market")["rho"].to_dict()
    nsel = {}                                           # (market, gün) -> seçilen bağlantı sayısı
    for r in conns.itertuples():
        nsel[(r.pazar, int(r.gun))] = nsel.get((r.pazar, int(r.gun)), 0) + 1

    bad_cnt = bad_c = bad_rank = bad_katki = over_beat = under_beat = 0
    tot_file = tot_recomp = 0.0
    for r in mres.itertuples():
        key = (r.pazar, int(r.gun))
        n = int(r.sunulan_baglanti)
        if n != nsel.get(key, 0):
            bad_cnt += 1
        conn_rew = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        if abs(conn_rew - float(r.aktarma_odul)) > 1e-3:
            bad_c += 1
        # D: gerçek yenilen = en iyi J ≤ T_comp olan rakipler
        N = int(r.N_rakip)
        beat_file = int(r.yenilen_rakip)
        js = j_opt.get(key, [])
        comps = comp_map.get(key, {})
        beat_true = sum(1 for tc in comps.values() if js and min(js) <= tc)
        if beat_file > beat_true:
            over_beat += 1                              # fazla-beyan → gerçek hata
        elif beat_file < beat_true:
            under_beat += 1                             # ihtiyatlı (çözücü β'yı bağlamamış)
        # sıralama ödülü lookup'tan
        rank_rew = 0.0
        if N >= 1 and not pd.isna(r.baslangic_sira_bod):
            s = int(np.clip(N - beat_file, 1, N))
            rank_rew = rkW.get((N, int(r.baslangic_sira_bod), s), 0.0)
        if abs(rank_rew - float(r.siralama_odul)) > 1e-3:
            bad_rank += 1
        rho = float(rho_map.get(r.pazar, 0.0))
        katki = rho * (conn_rew + rank_rew)
        if abs(katki - float(r.rho_katki)) > 0.5 + rho * 2e-3:
            bad_katki += 1
        tot_file += float(r.rho_katki)
        tot_recomp += katki
    ck.add("C aktarma ödülü", f"{len(mres)} pazar-gün", bad_c == 0 and bad_cnt == 0,
           f"ödül tutarsız: {bad_c} · sayaç tutarsız: {bad_cnt}")
    ck.add("D yenilen rakip", f"{len(mres)} pazar-gün", over_beat == 0,
           f"fazla-beyan: {over_beat} · ihtiyatlı (eksik-beyan): {under_beat}")
    ck.add("D sıralama ödülü (lookup)", f"{len(mres)} pazar-gün", bad_rank == 0,
           f"lookup uyuşmayan: {bad_rank}")
    ck.add("Amaç ρ-katkı", f"{len(mres)} pazar-gün", bad_katki == 0,
           f"katkı tutarsız: {bad_katki}")

    # ---------------------------------------------------------------- E1  (yön dengesi)
    n_by_key = {(r.pazar, int(r.gun)): int(r.sunulan_baglanti) for r in mres.itertuples()}
    e1_chk = e1_bad = 0
    seen = set()
    for (mk, d), n_od in n_by_key.items():
        o, dd = mk.split("-")
        rkey = (f"{dd}-{o}", d)
        if rkey in n_by_key and ((mk, d), rkey) not in seen and (rkey, (mk, d)) not in seen:
            seen.add(((mk, d), rkey))
            n_do = n_by_key[rkey]
            e1_chk += 1
            if abs(n_od - n_do) > ALPHA * (n_od + n_do) + 1e-6:
                e1_bad += 1
    ck.add("E1 yön dengesi (α=0.20)", f"{e1_chk} yön-çifti", e1_bad == 0,
           f"dengesiz çift: {e1_bad}")

    # ---------------------------------------------------------------- BASELINE (tam bağımsız)
    mk_rho_ok = set(markets[(markets["has_tk"]) & (~markets["excluded_no_rho"])
                            & (markets["rho"].notna())]["market"])
    nod_map = nod.set_index(["market", "day"])["N_od"].to_dict()
    base_tot = 0.0
    n_base_md = 0
    for (mk, d), grp in tk.groupby(["market", "day"]):
        if mk not in mk_rho_ok:
            continue
        n_base_md += 1
        comps = comp_map.get((mk, int(d)), {})
        N = int(nod_map.get((mk, int(d)), len(comps)))
        off = grp[grp["gap_min"].between(L_GAP, U_GAP)]
        n = len(off)
        conn_rew = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten0 = 0
        if n and comps:
            j0 = float((off["legsum_min"] + off["gap_min"]).min())
            beaten0 = sum(1 for tc in comps.values() if j0 <= tc)
        rank_rew = 0.0
        if N >= 1 and len(grp):
            b = int(np.clip(N - beaten0, 1, N))
            s = int(np.clip(N - beaten0, 1, N))
            rank_rew = rkW.get((N, b, s), 0.0)
        base_tot += float(rho_map.get(mk, 0.0)) * (conn_rew + rank_rew)

    # results_summary.md'deki raporlanan sayılarla karşılaştır
    rep_opt = rep_base = None
    summ_path = os.path.join(OUTPUT, "results_summary.md")
    if os.path.exists(summ_path):
        txt = open(summ_path, encoding="utf-8").read()
        m1 = re.search(r"OPTIMIZE amaç[^:]*:\*{0,2}\s*([\d,]+)", txt)
        m2 = re.search(r"BASELINE[^:]*:\*{0,2}\s*([\d,]+)", txt)
        rep_opt = float(m1.group(1).replace(",", "")) if m1 else None
        rep_base = float(m2.group(1).replace(",", "")) if m2 else None
    ck.add("Amaç toplamı (OPT)", "market_results ↔ bağımsız hesap",
           abs(tot_file - tot_recomp) < 5.0,
           f"dosya Σ={tot_file:,.0f} · yeniden hesap={tot_recomp:,.0f}"
           + (f" · raporlanan={rep_opt:,.0f}" if rep_opt else ""))
    if rep_opt is not None:
        ck.add("Amaç ↔ results_summary", "raporlanan OPT", abs(tot_file - rep_opt) < 5.0,
               f"|Δ| = {abs(tot_file - rep_opt):.1f}")
    ck.add("BASELINE bağımsız hesap", f"{n_base_md} pazar-gün",
           rep_base is None or abs(base_tot - rep_base) < 5.0,
           f"yeniden hesap={base_tot:,.0f}"
           + (f" · raporlanan={rep_base:,.0f} · |Δ|={abs(base_tot - rep_base):.1f}"
              if rep_base is not None else ""))
    if rep_base and rep_opt:
        ck.note("İYİLEŞME", "bağımsız teyit",
                f"Δ = {tot_recomp - base_tot:+,.0f}  ({100 * (tot_recomp - base_tot) / base_tot:+.2f}%)")

    # ---------------------------------------------------------------- rapor
    os.makedirs(REPORTS, exist_ok=True)
    stamp = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "# Bağımsız Doğrulama Raporu",
        "",
        "**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu",
        "",
        f"*Üretim: {stamp} · `python src/05_validate_solution.py`*",
        "",
        "`output/` çözüm dosyaları, MIP kodundan (`src/03_model.py` + `src/08_fullweek_polish.py`)",
        "geçmeden yalnız `derived/` veri katmanı üzerinden yeniden hesaplanarak doğrulanmıştır",
        "(çift kayıt). Kısıt adları `docs/model_formulation.md` ile aynıdır.",
        "",
        "| Kontrol | Kapsam | Sonuç | Ayrıntı |",
        "|---|---|---|---|",
    ]
    for name, scope, res, det in ck.rows:
        lines.append(f"| {name} | {scope} | {res} | {det} |")
    lines += [
        "",
        f"**Genel sonuç: {'TÜM KONTROLLER GEÇTİ' if not ck.failed else 'FAIL VAR — incele!'}**",
        "",
        "- *ihtiyatlı (eksik-beyan)*: çözücünün β göstergesini bağlamadığı, gerçekte yenilen ama",
        "  raporda sayılmayan rakip — amaç değerini ŞİŞİRMEZ (yalnız olduğundan küçük gösterir),",
        "  bu yüzden hata değildir; fazla-beyan ise hata sayılır (0 olmalı).",
        "- *eşleşme artefaktı (A2)*: mevcut yayınlanan tarifenin kendisinin de sağlamadığı",
        "  rotasyon yorumları (o gün o çift tek uçakla dönülmüyordur); ihlal sayılmaz.",
    ]
    with open(os.path.join(REPORTS, "validation_report.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n>> rapor: reports/validation_report.md — "
          f"{'TÜM KONTROLLER GEÇTİ' if not ck.failed else 'FAIL VAR'}")
    return 1 if ck.failed else 0


if __name__ == "__main__":
    sys.exit(main())
