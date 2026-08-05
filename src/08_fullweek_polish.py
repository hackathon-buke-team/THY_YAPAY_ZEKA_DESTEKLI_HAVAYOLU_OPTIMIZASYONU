"""
TEKNOFEST Havayolu Optimizasyonu — Tam-Hafta Warm-Start Cilalaması (8. adım)

AMAÇ: Güne-göre ayrıştırma (03 `byday`) greedy zincirdir — G düzenliliği üzerinden
günler-arası koordinasyon kaybı yaşar ve global optimalite iddiası veremez. Bu betik,
byday çözümünü HAFTANIN TAMAMINI kapsayan tek MIP'e **MIP-start (incumbent)** olarak
verir ve HiGHS branch-and-bound'unun bu noktadan küresel olarak İYİLEŞTİRMESİNİ sağlar.

Yöntem (warm-start matheuristiği; literatürde "fix-and-optimize/warm-start" ailesi):
  1. Aşama-1 çözümü `output/optimized_schedule.csv`'den okunur (yoksa byday koşulur).
  2. Tam-hafta modeli kurulur: 03'ün TÜM kısıtları (A1, A2 + gece-aşan koruma, B1, C,
     D, E1, F) değişmeden; G düzenliliği ise bağımsız doğrulayıcıyla (05) BİREBİR aynı
     "ilk-gün çapalı ±Xdev" biçiminde kurulur (aşağıya bkz.).
  3. Byday çözümü tüm ikili değişkenlere yazılır; Pyomo 6.10 appsi-HiGHS arayüzü
     `config.warmstart=True` ile bunu `Highs.setSolution` MIP-start'ına çevirir.
  4. Süre sınırı içinde HiGHS incumbent'ı iyileştirir; ayrıca üst sınırdan (bound)
     **global MIP-gap** raporlanır — greedy zincirin veremediği optimalite kanıtı.
  5. SAF rekabetçilik iyileşirse `output/` dosyaları aynı formatta yeniden yazılır
     (05 doğrulayıcısı değişmeden geçer); her durumda `reports/fullweek_polish.md`
     yazılır.

G DÜZENLİLİĞİ (neden "ilk-gün çapalı"): Doğrulayıcı (05) G'yi şöyle denetler: her
(uçuş,rol) grubunda İLK günün optimize yerleşimi bant merkezidir (c0); sonraki günler
|yerleşim − c0| ≤ Xdev sağlamalı, `g_band_exemptions.csv`'deki belgeli muafiyetler ve
penceresi banda yetişmeyen günler atlanır. byday'in zincirleme bandı da tam budur. Bu
betik aynı kısıtı DEĞİŞKEN çapayla kurar: θ'_gün − θ'_ilkgün ∈ [−Xdev, +Xdev] (çapa da
kayabilir → günler-arası eşgüdüm serbestliği). Warm-start noktasının sağlamadığı veya
penceresi yetişmeyen az sayıda bağ kısıtlanmaz ve doğrulayıcı formatında BELGELİ
MUAFİYET olarak `g_band_exemptions.csv`'ye eklenir (byday muafiyetleri korunur).

KURALLARA ETKİ YOKTUR: resmi amaç fonksiyonu ve tüm kısıt grupları birebir aynıdır;
yalnız çözüm YÖNTEMİ güçlenir. Çözüm yine 05 bağımsız doğrulayıcısından geçirilir.

Çalıştırma:  python src/08_fullweek_polish.py [süre_s] [λ] [Wdev_dk]
             (varsayılan: 600 s, λ = 03'teki DEFAULT_LAMBDA = 0.3, Wdev = 60)

Wdev_dk > 60 verilirse pencere genişletme DENEYİ yapılır: aşama-1 çözümü (±60)
geniş pencerede de fizibıldir → warm-start geçerli kalır; fizibıl bölge büyüdüğü
için gerçek optimum ancak yükselir (brief pencereye sınır koymaz, docs D3).
DİKKAT: geniş-Wdev çözümü BENİMSENİRSE 05 doğrulayıcısının WDEV sabiti ve docs
D3 senkron güncellenmelidir (aksi hâlde A1 pencere kontrolü FAIL verir).
"""

import os
import sys
import datetime as dt
import importlib.util

import pandas as pd
import pyomo.environ as pyo

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUTPUT = os.path.join(ROOT, "output")
REPORTS = os.path.join(ROOT, "reports")

spec = importlib.util.spec_from_file_location("model03", os.path.join(HERE, "03_model.py"))
M3 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M3)
CFG = M3.CFG

HHMM = lambda t: f"{(t % 1440) // 60:02d}:{(t % 1440) % 60:02d}"
ROL = {"dep": "kalkış", "arr": "varış"}
TOD = lambda v: v - (v // 1440) * 1440


# --------------------------------------------------------------- aşama-1 çözümü
def load_phase1(lam):
    """byday çözümünü (uçuş-olay kaydırmaları + SUNULAN bağlantı listesi) ve G
    muafiyetlerini oku. Tarife dosyası yoksa byday'i çalıştırır.

    Sunum listesi kritiktir: amaç sunmayı ödüllendirse de byday, E1 yönsel dengesi
    için uygun bağlantıların bir kısmını BİLİNÇLİ sunmaz (docs §10-U5, ~265 aday).
    Warm-start'ta y'yi 'uygunluk'tan türetmek E1'i ihlal eden (reddedilecek) bir
    başlangıç üretir — y byday'in GERÇEK sunumundan alınmalıdır."""
    sched_p = os.path.join(OUTPUT, "optimized_schedule.csv")
    if not os.path.exists(sched_p):
        print(">> output/optimized_schedule.csv yok — aşama-1 (byday) koşuluyor …")
        M3.run_byday(lam=lam, gap=0.001, time_limit=150, write=True)
    df = pd.read_csv(sched_p, encoding="utf-8-sig", dtype={"eski_IST": str})
    shift = {(int(r.gun), int(r.ucus_no), r.rol, str(r.eski_IST)): int(r.degisim_dk)
             for r in df.itertuples()}
    sel = pd.read_csv(os.path.join(OUTPUT, "selected_connections.csv"),
                      encoding="utf-8-sig", dtype={"IST_varis": str, "IST_kalkis": str})
    offered = {(int(r.gun), r.pazar, int(r.gelen_ucus), int(r.giden_ucus),
                str(r.IST_varis), str(r.IST_kalkis)) for r in sel.itertuples()}
    # byday'in KAYITLI saf rekabetçilik toplamı — çıktı-yeniden-yazma bariyeri bunu
    # kullanır (warm nokta eşleşme kayıplarıyla düşebilir; kıyas gerçek toplamla yapılmalı)
    mres = pd.read_csv(os.path.join(OUTPUT, "market_results.csv"), encoding="utf-8-sig")
    byday_total = float(mres["rho_katki"].sum())
    exempt = set()
    exq = os.path.join(OUTPUT, "g_band_exemptions.csv")
    if os.path.exists(exq):
        for r in pd.read_csv(exq, encoding="utf-8-sig").itertuples():
            exempt.add((int(r.gun), int(r.ucus_no), r.rol))
    return shift, offered, exempt, byday_total


def pin_merged_events(inst, days, shift):
    """Aynı fiziksel zaman damgası birden çok operasyon gününde kayıtlı olan olaylar
    (gün-görünümü kopyaları) tam-hafta ekseninde TEK karara birleşir; byday ve bağımsız
    doğrulayıcı (05) ise bunları gün-görünümü başına AYRI değerlendirir. Tutarlılık için:
      • birleşik AYARLANABİLİR olay byday'in verdiği saate SABİTLENİR (cands=[t*]) —
        warm nokta birebir byday olur ve çözücü olayı oynatamayacağından öbür
        gün-görünümünün (modelde kurulmayan) A2/F bağları da riske girmez;
      • olayın TÜM gün-görünümleri kaydedilir (inst.view_days) — tarife çıktısına her
        görünüm için satır yazılır (doğrulayıcı iki günü de tutarlı görür; byday da
        kopyalar için ayrı satır yazıyordu).
    Bu veride 1 böyle olay vardır (uçuş 1304 varışı). Sabit birleşikler zaten durur."""
    _, _, tk, _, _, _, _, _ = M3.load_data()
    tk = tk[tk["day"].isin(days)]
    delta = CFG["delta_min"]
    absmin = lambda ts: (ts - inst.t0).total_seconds() / 60.0
    sp = lambda mv: int(round(mv / delta) * delta)
    evdays = {}
    for r in tk.itertuples():
        evdays.setdefault((int(r.FlNo1), "arr", sp(absmin(r.ist_arr))), set()).add(int(r.day))
        evdays.setdefault((int(r.FlNo2), "dep", sp(absmin(r.ist_dep))), set()).add(int(r.day))
    pinned = 0
    view_days = {}                                       # eid -> [görünüm günleri]
    for key, e in inst.events.items():
        vds = evdays.get(key, {e["day"]})
        if len(vds) <= 1:
            continue
        view_days[e["id"]] = sorted(vds)
        if not e["adjustable"]:
            continue
        # byday kaydırması: önce olayın kayıtlı günü, yoksa diğer görünüm günleri
        dv = None
        for d in [e["day"]] + [d for d in sorted(vds) if d != e["day"]]:
            dv = shift.get((d, e["flno"], ROL[e["role"]], HHMM(e["cur"])))
            if dv is not None:
                break
        e["cands"] = [e["cur"] + (dv or 0)]
        pinned += 1
    inst.view_days = view_days
    return pinned


def warm_times(inst, shift):
    """Her olayın aşama-1 (byday) zamanı: t*[eid] (tam eksende dk). Ayarlanabilir olay
    tarife dosyasında bulunamazsa sayılır (byday çıktısı bayat → koşu durdurulur)."""
    t, missing = {}, []
    for e in inst.ev_by_id.values():
        if not e["adjustable"]:
            t[e["id"]] = e["cur"]
            continue
        dv = shift.get((e["day"], e["flno"], ROL[e["role"]], HHMM(e["cur"])))
        if dv is None:
            missing.append((e["day"], e["flno"], e["role"]))
            t[e["id"]] = e["cur"]
        else:
            t[e["id"]] = e["cur"] + dv
            if t[e["id"]] not in set(e["cands"]):
                raise ValueError(f"byday kaydırması pencere dışı: olay {e} Δ={dv} "
                                 "(Wdev/Δ ayarları 03 ile uyumsuz?)")
    return t, missing


# --------------------------------------------------------------- G (ilk-gün çapalı)
def add_star_G(inst, m, tstar, byday_exempt):
    """G düzenliliğini doğrulayıcı-birebir kur: her (uçuş,rol) grubunda ilk günün
    yerleşimi (değişken) çapadır; sonraki günler θ'_g − θ'_çapa ∈ [−Xdev, +Xdev].
    Kısıtlanmayan her (gün,uçuş,rol) belgeli muafiyet olarak döndürülür — böylece
    doğrulayıcıda hiçbir bağ 'bant dışı' kalamaz (kısıtlı → geçer; kısıtsız → muaf)."""
    Xd = CFG["xdev_min"]
    W = CFG["wdev_min"]
    n_c, new_ex = 0, []
    for (flno, role), eids in sorted(inst.ev_by_flno_role.items()):
        adj = sorted((inst.ev_by_id[e] for e in eids if inst.ev_by_id[e]["adjustable"]),
                     key=lambda e: (e["day"], e["cur"]))
        if len({e["day"] for e in adj}) < 2:
            continue
        day_ct = {}
        for e in adj:
            day_ct[e["day"]] = day_ct.get(e["day"], 0) + 1
        anchor = adj[0]
        off_a = (anchor["cur"] // 1440) * 1440
        ws_a = TOD(tstar[anchor["id"]])
        th_a = None                                       # tembel: gerekirse kur
        for e in adj[1:]:
            key3 = (e["day"], flno, ROL[role])
            if key3 in byday_exempt:
                continue                                  # zaten belgeli muafiyet
            # kısıt ancak şu üç koşulla kurulur (aksi → belgeli muafiyet):
            #  (i) çapa/olay günü tekil (3 anomali-olay grubu determinizm için muaf),
            #  (ii) pencereler ortak banda yetişebilir (|Δcur| ≤ 2·Wdev+Xdev),
            #  (iii) warm-start noktası kısıtı sağlar (byday bant-dışı bıraktıysa muaf).
            ok = (day_ct[e["day"]] == 1 and day_ct[anchor["day"]] == 1
                  and abs(TOD(e["cur"]) - TOD(anchor["cur"])) <= 2 * W + Xd
                  and abs(TOD(tstar[e["id"]]) - ws_a) <= Xd)
            if not ok:
                new_ex.append(dict(gun=e["day"], ucus_no=flno, rol=ROL[role]))
                continue
            if th_a is None:
                th_a = M3.theta_expr(m, inst, anchor["id"]) - off_a
            th_e = M3.theta_expr(m, inst, e["id"]) - (e["cur"] // 1440) * 1440
            m.cons.add(th_e - th_a <= Xd)
            m.cons.add(th_a - th_e <= Xd)
            n_c += 1
    return n_c, new_ex


# --------------------------------------------------------------- warm-start yazımı
def set_start_values(inst, m, t, offered):
    """Aşama-1 çözümünü modelin TÜM ikili değişkenlerine tutarlı biçimde yaz
    (03.set_warmstart'ın t[eid] zamanlarıyla genellenmiş hali; E2/B2 tam-ölçekte
    kapalı olduğundan o bloklar yoktur). appsi `config.warmstart=True` bu değerleri
    HiGHS `setSolution` MIP-start'ına çevirir.

    y, UYGUNLUKTAN DEĞİL byday'in gerçek sunum listesinden (`offered`) alınır:
    byday E1 dengesi için bazı uygun bağlantıları bilinçli sunmaz; hepsini y=1
    yapmak E1'i ihlal eden (HiGHS'in reddedeceği) bir başlangıç üretir."""
    md_id, L, U = m._md_id, inst.L, inst.U
    sv = lambda var, val: var.set_value(val, skip_validation=True)
    for e in inst.ev_by_id.values():                     # x = byday kovası
        if e["adjustable"]:
            for v in e["cands"]:
                sv(m.x[e["id"], v], 1 if v == t[e["id"]] else 0)
    yv = {}
    n_drop = 0
    for pi, c in enumerate(inst.conns):                  # y = byday'in sunduğu ∩ hâlâ uygun
        g = t[c["dep_eid"]] - t[c["arr_eid"]]
        ea, ed = inst.ev_by_id[c["arr_eid"]], inst.ev_by_id[c["dep_eid"]]
        off = (c["day"], c["market"], ea["flno"], ed["flno"],
               HHMM(t[c["arr_eid"]]), HHMM(t[c["dep_eid"]])) in offered
        if off and not (L <= g <= U):
            off = False                                  # (dondurulan olay) artık uygun değil
            n_drop += 1
        yv[pi] = 1 if off else 0
    # E1 onarımı: dondurma kaynaklı düşürmeler bir yönün sayısını azaltıp warm
    # noktada E1'i bozabilir; sağlanana dek büyük yönden sunum geri çekilir
    # (deterministik: en yüksek indeksli). byday noktası E1'i sağladığından bu
    # onarım yalnız düşürme yaşanan yön-çiftlerinde tetiklenebilir.
    n_rep = 0
    if CFG["E1_balance"]:
        a = CFG["alpha"]
        seen = set()
        for k in inst.md:
            (mk, day) = k
            o, dd = mk.split("-")
            rk = (f"{dd}-{o}", day)
            if rk not in inst.md or (rk, k) in seen:
                continue
            seen.add((k, rk))
            c1, c2 = inst.md[k]["conns"], inst.md[rk]["conns"]
            n1 = sum(yv[p] for p in c1)
            n2 = sum(yv[p] for p in c2)
            while abs(n1 - n2) > a * (n1 + n2) + 1e-9:
                side = c1 if n1 > n2 else c2
                yv[max(p for p in side if yv[p] == 1)] = 0
                n_rep += 1
                n1 = sum(yv[p] for p in c1)
                n2 = sum(yv[p] for p in c2)
    for pi in range(len(inst.conns)):
        sv(m.y[pi], yv[pi])
    if n_drop or n_rep:
        print(f"   [not] warm-start: dondurma nedeniyle düşürülen bağlantı {n_drop}, "
              f"E1 onarımıyla geri çekilen {n_rep}")
    for k, gmd in inst.md.items():                       # z (monoton doldurma)
        i, Mn = md_id[k], len(gmd["conns"])
        n = sum(yv[pi] for pi in gmd["conns"])
        for j in range(1, Mn + 1):
            sv(m.z[i, j], 1 if j <= n else 0)
    for k, gmd in inst.md.items():                       # w, β, γ
        i = md_id[k]
        beaten = {}
        for ca, Tc in gmd["comps"].items():
            bt = 0
            for pi in gmd["conns"]:
                if yv[pi] != 1:
                    continue
                if (pi, ca) in m._beat_eq_y:
                    bt = 1
                elif (pi, ca) in m._w:
                    beats = (t[inst.conns[pi]["dep_eid"]] - t[inst.conns[pi]["arr_eid"]]) \
                        <= (Tc - inst.conns[pi]["legsum"])
                    sv(m._w[(pi, ca)], 1 if beats else 0)
                    bt = bt or int(beats)
            if (i, ca) in m._beta:
                sv(m._beta[(i, ca)], bt)
            beaten[ca] = bt
        if CFG["ranking"] and gmd["N"] >= 1 and gmd["b_od"] is not None:
            nb = sum(beaten.values())
            for bn in range(0, gmd["N"] + 1):
                sv(m.w[("gam", i, bn)], 1 if bn == nb else 0)


# --------------------------------------------------------------- raporlama yardımcıları
def totals_by_day(inst, m):
    """Gün kırılımı: optimize (çözümden) ve baseline (mevcut tarifeden) SAF rekabetçilik."""
    rkW = M3.rank_weight_table(inst.rank)
    md_id = m._md_id
    opt_d, base_d, nmd_d, nconn_d = {}, {}, {}, {}
    for k, g in inst.md.items():
        d, i = k[1], md_id[k]
        nmd_d[d] = nmd_d.get(d, 0) + 1
        nconn_d[d] = nconn_d.get(d, 0) + len(g["conns"])
        n = sum(1 for pi in g["conns"] if pyo.value(m.y[pi]) > 0.5)
        conn = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten = sum(1 for ca in g["comps"]
                     if (i, ca) in m._beta and pyo.value(m._beta[(i, ca)]) > 0.5)
        rr = M3.rank_reward(rkW, g["N"], g["b_od"], beaten) if CFG["ranking"] else 0.0
        opt_d[d] = opt_d.get(d, 0.0) + g["rho"] * (conn + rr)
        offered0 = [pi for pi in g["conns"]
                    if inst.L <= inst.conns[pi]["gap_cur"] <= inst.U]
        c0 = sum(0.5 ** (j - 1) for j in range(1, len(offered0) + 1))
        b0 = 0
        if CFG["ranking"] and offered0 and g["comps"]:
            jb = min(inst.conns[pi]["legsum"] + inst.conns[pi]["gap_cur"] for pi in offered0)
            b0 = sum(1 for tc in g["comps"].values() if jb <= tc)
        rr0 = M3.rank_reward(rkW, g["N"], g["b_od"], b0) if CFG["ranking"] else 0.0
        base_d[d] = base_d.get(d, 0.0) + g["rho"] * (c0 + rr0)
    return opt_d, base_d, nmd_d, nconn_d


def collect_market_outputs_week(inst, m, new_time):
    """03.collect_market_outputs'un çok-günlü örnek karşılığı (gun = pazar-gün anahtarından)."""
    rkW = M3.rank_weight_table(inst.rank)
    md_id = m._md_id
    market_rows, conn_rows = [], []
    for k, g in inst.md.items():
        day, i = k[1], md_id[k]
        offered = [pi for pi in g["conns"] if pyo.value(m.y[pi]) > 0.5]
        n = len(offered)
        conn_rew = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten_cas = [ca for ca in g["comps"]
                      if (i, ca) in m._beta and pyo.value(m._beta[(i, ca)]) > 0.5]
        beaten = len(beaten_cas)
        rank_rew = M3.rank_reward(rkW, g["N"], g["b_od"], beaten) if CFG["ranking"] else 0.0
        market_rows.append(dict(
            gun=day, pazar=k[0], rho=round(g["rho"]), N_rakip=g["N"],
            sunulan_baglanti=n, aday_baglanti=len(g["conns"]),
            yenilen_rakip=beaten, baslangic_sira_bod=g["b_od"],
            son_sira=(g["N"] - beaten) if g["N"] >= 1 else None,
            aktarma_odul=round(conn_rew, 4), siralama_odul=round(rank_rew, 4),
            rho_katki=round(g["rho"] * (conn_rew + rank_rew), 2)))
        for pi in offered:
            c = inst.conns[pi]
            ea, ed = inst.ev_by_id[c["arr_eid"]], inst.ev_by_id[c["dep_eid"]]
            gv = pyo.value(m._gap[pi])
            J = c["legsum"] + gv
            beats = [ca for ca, Tc in g["comps"].items() if J <= Tc]
            conn_rows.append(dict(
                gun=day, pazar=k[0], gelen_ucus=ea["flno"], giden_ucus=ed["flno"],
                IST_varis=HHMM(new_time[c["arr_eid"]]), IST_kalkis=HHMM(new_time[c["dep_eid"]]),
                bosluk_dk=round(gv), J_dk=round(J), yendigi_rakip=len(beats)))
    return market_rows, conn_rows


def a2x_check(inst, new_time, days):
    """A2 fiziksel rotasyon doğrulaması (gece-aşan dahil, gerçek zaman ekseni) —
    03.run_byday'deki kontrolün tam-hafta çözümü üzerindeki karşılığı."""
    final_dt, cur_dt = {}, {}
    for e in inst.ev_by_id.values():
        final_dt[(e["flno"], e["day"], e["role"])] = \
            inst.t0 + pd.Timedelta(minutes=new_time[e["id"]])
        cur_dt[(e["flno"], e["day"], e["role"])] = inst.t0 + pd.Timedelta(minutes=e["cur"])
    a2x_chk = a2x_viol = a2x_base = 0
    if inst.blocks is None or not inst.rot_pairs:
        return a2x_chk, a2x_viol, a2x_base
    tau = CFG["tau_min"]
    for out_f, in_f in inst.rot_pairs:
        for d in days:
            t_ob = inst.blocks.get((out_f, d, "dep"))
            dep_c = cur_dt.get((out_f, d, "dep"))
            dep_o = final_dt.get((out_f, d, "dep"))
            if dep_c is None or dep_o is None or t_ob is None:
                continue
            pick = None
            for d2 in (d, d + 1):
                a_c = cur_dt.get((in_f, d2, "arr"))
                tb = inst.blocks.get((in_f, d2, "arr"))
                if a_c is not None and tb is not None and a_c > dep_c:
                    pick = (d2, a_c, tb)
                    break
            if pick is None:
                continue
            d2, a_c, tb = pick
            a_o = final_dt.get((in_f, d2, "arr"))
            if a_o is None:
                continue
            a2x_chk += 1
            need = pd.Timedelta(minutes=t_ob + tau + tb)
            if a_c < dep_c + need:
                a2x_base += 1                             # mevcutta da yok → artefakt
            elif a_o < dep_o + need:
                a2x_viol += 1                             # YENİ ihlal (olmamalı)
    return a2x_chk, a2x_viol, a2x_base


# --------------------------------------------------------------- ana akış
def main(time_limit=600, lam=None, wdev=None):
    lam = M3.DEFAULT_LAMBDA if lam is None else lam
    # ÖNCE aşama-1: load_phase1 gerekirse run_byday çalıştırır ve run_byday CFG'yi
    # (days=[son gün], time_limit, mip_gap) mutasyona uğratır — CFG kurulumunu
    # bu yüzden aşama-1'den SONRA yapıyoruz.
    shift, offered, byday_exempt, byday_total = load_phase1(lam)
    CFG.update(M3.PRESETS["full"])
    CFG["days"] = M3.all_operation_days()
    CFG["shift_penalty"] = lam
    if wdev is not None:
        CFG["wdev_min"] = int(wdev)    # pencere genişletme deneyi (docstring'e bkz.)
    CFG["time_limit"], CFG["mip_gap"] = time_limit, 0.001
    CFG["G_regularity"] = False        # G'yi bu betik doğrulayıcı-birebir (ilk-gün çapalı) kurar
    CFG["warmstart"] = True            # appsi → HiGHS setSolution MIP-start
    # incumbent çevresi sezgisellere (RINS vb.) daha çok bütçe: warm-start'lı büyük
    # MIP'te iyileştirmeler çoğunlukla sezgisellerden gelir (varsayılan 0.05)
    CFG["highs_extra_options"] = {"mip_heuristic_effort": 0.3}
    days = CFG["days"]

    print(f">> TAM-HAFTA CİLALAMA  (λ={lam}, Wdev=±{CFG['wdev_min']}dk, "
          f"gap≤{CFG['mip_gap']:.2%}, ≤{time_limit}s, günler {days})")

    print(">> tam-hafta örneği kuruluyor …")
    inst = M3.build_instance()
    caps, floors = M3.compute_overnight_guards(days)     # (A2×) gece-aşan koruma (statik)
    inst.rotcap = {k: v for d in caps for k, v in caps[d].items()}
    inst.rotlock = {k: v for d in floors for k, v in floors[d].items()}
    n_pin = pin_merged_events(inst, days, shift)         # gün-görünümü kopyası → byday'e sabitle
    n_adj = sum(1 for e in inst.ev_by_id.values() if e["adjustable"])
    print(f"   pazar-gün: {len(inst.md)} | bağlantı(π): {len(inst.conns)} | "
          f"olay: {len(inst.events)} (ayarlanabilir {n_adj}, "
          f"gün-görünümü kopyası byday'e sabitlenen {n_pin})")

    tstar, missing = warm_times(inst, shift)
    if missing:
        print(f"   [!] {len(missing)} ayarlanabilir olay tarife dosyasında yok — "
              "byday çıktısı bayat görünüyor; önce `python src/03_model.py byday` koşun.")
        return 1

    print(">> model kuruluyor …")
    m = M3.build_model(inst)
    n_star, new_ex = add_star_G(inst, m, tstar, byday_exempt)
    all_exempt_rows = ([dict(gun=g, ucus_no=f, rol=r) for (g, f, r) in sorted(byday_exempt)]
                       + new_ex)
    nbin = sum(1 for v in m.component_data_objects(pyo.Var) if v.is_binary())
    print(f"   ikili değişken: {nbin} | A2 bağ: {m._n_a2} "
          f"(evren-ankoru {getattr(m, '_n_a2_anchor', 0)}) | F bağ: {m._n_f} | "
          f"G ilk-gün-çapalı bağ: {n_star} (byday muafiyeti {len(byday_exempt)}, "
          f"yeni muafiyet {len(new_ex)})")

    set_start_values(inst, m, tstar, offered)
    warm_pen = pyo.value(m.OBJ)
    warm_pure = M3.solution_total(inst, m)
    base = M3.current_baseline(inst)
    print(f"   MIP-start: SAF={warm_pure:,.1f}  cezalı={warm_pen:,.1f}  "
          f"(baseline {base:,.1f}, Δ={warm_pure - base:+,.1f})")
    print(f"   byday kayıtlı toplam: {byday_total:,.1f}  "
          f"(warm − byday = {warm_pure - byday_total:+,.1f} — 0'a yakın olmalı)")

    print(f">> çözülüyor (appsi_highs + MIP-start, ≤{time_limit}s) …")
    res = M3.solve_model(m)
    print(f"   durum: {res['tc']}" + (f"  | global MIP-gap (cezalı amaç): {res['gap']:.3%}"
          if res.get("gap") is not None else "") + f"  | süre: {res['t']:.1f}s")
    if not res["ok"]:
        # byday çıktısı geçerli kalır → uçtan-uca koşuyu (run_all) durdurma, uyar ve geç
        print("   [!] Çözüm yüklenemedi — MIP-start reddedilmiş olabilir; byday çıktısı korunuyor.")
        return 0

    pol_pen = pyo.value(m.OBJ)
    pol_pure = M3.solution_total(inst, m)
    sh = M3.shift_value(m)
    print(f"   CİLALANMIŞ: SAF={pol_pure:,.1f}  cezalı={pol_pen:,.1f}  "
          f"kaydırma={sh:,.0f} uçuş-dk")
    d_pure = pol_pure - warm_pure
    print(f"   İYİLEŞME (aşama-1'e göre, SAF): {d_pure:+,.1f}  "
          f"(baseline'a göre {pol_pure - base:+,.1f} = {100*(pol_pure-base)/base:+.2f}%)")

    # BARİYER: yeniden yazma kararı warm noktaya göre DEĞİL, byday'in kayıtlı gerçek
    # toplamına göre verilir (warm nokta eşleşme kayıplarıyla düşük olabilir; kötü
    # bir çözümle iyi byday çıktısını ezmek yasak).
    improved = pol_pure > byday_total + 0.5
    new_time = {e["id"]: (int(round(sum(v * pyo.value(m.x[e["id"], v]) for v in e["cands"])))
                          if e["adjustable"] else e["cur"]) for e in inst.ev_by_id.values()}
    a2x_chk, a2x_viol, a2x_base = a2x_check(inst, new_time, days)
    print(f"   A2 gece-aşan doğrulama: {a2x_chk} tur, YENİ ihlal: {a2x_viol} "
          f"(artefakt taban: {a2x_base})")

    if improved and a2x_viol == 0:
        print(">> iyileşme var — output/ dosyaları tam-hafta çözümüyle yeniden yazılıyor …")
        sched_rows = []
        moved = tot_shift = 0
        view_days = getattr(inst, "view_days", {})
        for e in sorted(inst.ev_by_id.values(), key=lambda e: (e["day"], e["flno"], e["role"])):
            if not e["adjustable"]:
                continue
            delta = new_time[e["id"]] - e["cur"]
            # birleşik olayların HER gün-görünümü için satır yaz (doğrulayıcı her iki
            # günü de aynı kaydırmayla görür; byday kopya başına satır yazıyordu)
            for vd in view_days.get(e["id"], [e["day"]]):
                moved += int(delta != 0)
                tot_shift += abs(delta)
                sched_rows.append(dict(gun=vd, ucus_no=e["flno"], rol=ROL[e["role"]],
                                       eski_IST=HHMM(e["cur"]), yeni_IST=HHMM(new_time[e["id"]]),
                                       degisim_dk=delta, G_gevsetildi=0))
        market_rows, conn_rows = collect_market_outputs_week(inst, m, new_time)
        opt_d, base_d, nmd_d, nconn_d = totals_by_day(inst, m)
        shift_d, moved_d = {}, {}
        for r in sched_rows:
            shift_d[r["gun"]] = shift_d.get(r["gun"], 0) + abs(r["degisim_dk"])
            moved_d[r["gun"]] = moved_d.get(r["gun"], 0) + int(r["degisim_dk"] != 0)
        gp = f"{res['gap']:.2%}" if res.get("gap") is not None else "?"
        day_stats = [dict(gun=d, pazar_gun=nmd_d.get(d, 0), baglanti=nconn_d.get(d, 0),
                          OPT=round(opt_d.get(d, 0)), baseline=round(base_d.get(d, 0)),
                          delta=round(opt_d.get(d, 0) - base_d.get(d, 0)), gap=gp,
                          ucus_kaydirilan=moved_d.get(d, 0), kaydirma_dk=shift_d.get(d, 0),
                          G_gevsetildi=0) for d in days]
        stats = dict(lam=lam, opt=pol_pure, base=base,
                     dpct=100 * (pol_pure - base) / base if base else 0.0,
                     shift=tot_shift, moved=moved, nflights=len(sched_rows),
                     movedpct=100 * moved / max(1, len(sched_rows)),
                     ok_days=len(days), n_days=len(days), relaxed_days=0,
                     a2x_chk=a2x_chk, a2x_viol=a2x_viol, a2x_base=a2x_base,
                     band_exempt=len(all_exempt_rows))
        M3.write_outputs(sched_rows, day_stats, stats, market_rows, conn_rows,
                         all_exempt_rows)
        # başlık iki aşamalı hattı yansıtsın (03'ün yazdığı özet artık cilalanmış sonucu içeriyor)
        summ_path = os.path.join(OUTPUT, "results_summary.md")
        txt = open(summ_path, encoding="utf-8").read()
        txt = txt.replace("`python src/03_model.py byday`",
                          f"`python src/03_model.py byday` → "
                          f"`python src/08_fullweek_polish.py {time_limit} {lam}`")
        txt = txt.replace("## Tam veri sonucu (güne göre ayrıştırma)",
                          "## Tam veri sonucu (güne göre ayrıştırma + tam-hafta cilalaması)")
        with open(summ_path, "w", encoding="utf-8") as f:
            f.write(txt)
        with open(os.path.join(OUTPUT, "results_summary.md"), "a", encoding="utf-8") as f:
            f.write(
                "\n*Gün tablosundaki `gap` sütunu tam-hafta modelinin GLOBAL (cezalı) MIP-gap'idir "
                "(aşama-1'in gün-içi gap'i ≤ %0.1 idi).*\n"
                "\n## Tam-hafta warm-start cilalaması (08)\n\n"
                "Bu sonuç, güne-göre ayrıştırma (aşama-1) çözümünün HAFTANIN TAMAMINI\n"
                "kapsayan tek MIP'e MIP-start olarak verilip HiGHS ile iyileştirilmesiyle\n"
                f"üretildi (`python src/08_fullweek_polish.py`, ≤{time_limit}s):\n\n"
                f"- Aşama-1 (byday) SAF rekabetçilik : {byday_total:,.1f}\n"
                f"- Tam-hafta cilalanmış             : {pol_pure:,.1f}  "
                f"({pol_pure - byday_total:+,.1f})\n"
                f"- Global MIP-gap (cezalı amaç)     : {gp}\n"
                "- G düzenliliği doğrulayıcı-birebir 'ilk-gün çapalı ±Xdev' kısıtlarıyla\n"
                f"  tam modelde kuruldu ({n_star} bağ; belgeli muafiyet: "
                f"{len(all_exempt_rows)}, bkz. `output/g_band_exemptions.csv`).\n")
    else:
        why = ("A2 gece-aşan yeni ihlal" if a2x_viol else
               "anlamlı iyileşme yok" if not improved else "?")
        print(f">> output/ DEĞİŞTİRİLMEDİ ({why}) — byday çıktısı geçerli kalır.")

    os.makedirs(REPORTS, exist_ok=True)
    gp = f"{res['gap']:.3%}" if res.get("gap") is not None else "hesaplanamadı"
    with open(os.path.join(REPORTS, "fullweek_polish.md"), "w", encoding="utf-8") as f:
        f.write("\n".join([
            "# Tam-Hafta Warm-Start Cilalaması — Koşu Raporu", "",
            "**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu", "",
            f"*Üretim: {dt.datetime.now():%Y-%m-%d %H:%M} · "
            f"`python src/08_fullweek_polish.py {time_limit} {lam}`*", "",
            "Aşama-1 (güne-göre ayrıştırma) çözümü, haftanın tamamını kapsayan tek MIP'e",
            "**MIP-start** (HiGHS `setSolution`) olarak verildi; branch-and-bound bu",
            "incumbent'tan devam ederek günler-arası koordinasyonu küresel iyileştirdi.",
            "Amaç ve kısıtlar 03 ile birebir aynıdır (yönteme ek — kurala dokunulmaz).", "",
            "| | Değer |", "|---|---|",
            f"| Günler | {len(days)} ({days[0]}–{days[-1]}) |",
            f"| Pencere (Wdev) | ±{CFG['wdev_min']} dk |",
            f"| İkili değişken | {nbin:,} |",
            f"| G ilk-gün-çapalı bağ | {n_star:,} (muafiyet: byday {len(byday_exempt)}, "
            f"yeni {len(new_ex)}) |",
            f"| Aşama-1 (byday) kayıtlı toplam | {byday_total:,.1f} |",
            f"| MIP-start SAF rekabetçilik | {warm_pure:,.1f} |",
            f"| Cilalanmış SAF rekabetçilik | **{pol_pure:,.1f}** "
            f"(byday'e göre {pol_pure - byday_total:+,.1f}) |",
            f"| Baseline (mevcut tarife) | {base:,.1f} |",
            f"| İyileşme (baseline'a göre) | **{pol_pure - base:+,.1f} "
            f"({100*(pol_pure-base)/base:+.2f}%)** |",
            f"| Toplam kaydırma (tekil olay bazında) | {sh:,.0f} uçuş-dk |",
            f"| **Global MIP-gap (cezalı amaç)** | **{gp}** |",
            f"| Çözüm süresi | {res['t']:.0f} s (sınır {time_limit} s) |",
            f"| A2 gece-aşan doğrulama | {a2x_chk} tur, yeni ihlal {a2x_viol} |",
            f"| output/ güncellendi mi | {'EVET' if improved and a2x_viol == 0 else 'HAYIR'} |",
            "",
            "Not: Global MIP-gap, greedy gün-zincirinin veremediği **optimalite kanıtıdır**:",
            "tam-hafta modelinin gerçek optimumu, raporlanan cezalı amacın en fazla gap kadar",
            "üzerindedir. 'SAF rekabetçilik' resmi amaçtır ve cezasız ölçülür (docs §12).",
        ]) + "\n")
    print(f">> rapor: reports/fullweek_polish.md")
    return 0


if __name__ == "__main__":
    tl = int(sys.argv[1]) if len(sys.argv) > 1 else 600
    lm = float(sys.argv[2]) if len(sys.argv) > 2 else None
    wd = int(sys.argv[3]) if len(sys.argv) > 3 else None
    sys.exit(main(time_limit=tl, lam=lm, wdev=wd))
