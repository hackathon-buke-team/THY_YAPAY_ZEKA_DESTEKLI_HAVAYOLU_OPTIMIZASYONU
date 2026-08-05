"""
TEKNOFEST Havayolu Optimizasyonu — MIP Modeli (3. adım) · Pyomo + HiGHS

Bu betik `docs/model_formulation.md` formülasyonunun TAM implementasyonudur.
Küçük alt-örnekte tüm kısıtlarla elle doğrulanır; tam veride (`full` profili) ölçeklenir.

Uygulanan kısıtlar (hepsi CFG ile açılır/kapanır):
  A1  Tekil zaman atama (10 dk ızgarada, pencere ±Wdev)              [docs §5-A]
  A2  Uçak rotasyonu — min tur = T_OB + τ + T_IB (brief-exact) (*)   [docs §5-A2]
  B1  Bağlantı uygunluk göstergesi  ℓ ≤ boşluk ≤ u  ⟺  y_π          [docs §5-B]
  B2  Uygun bağlantı zorunlu sunulur — VARSAYILAN KAPALI (*)         [docs §5-B2]
  C   Azalan-getiri / monoton slot ödülü (aktarma sayısı)            [docs §5-C]
  D   Rakip yenme (w, β) + sıralama ödülü (γ)                        [docs §5-D]
  E1  Yönsel SAYI dengesi                                            [docs §5-E1]
  E2  En iyi yolculuk süresi (Jmin) dengesi — tam-ölçekte KAPALI (*) [docs §5-E2]
  F   IST hub kova kapasitesi — brief'in gerçek 10/15 rezidüel cap'i  [docs §5-F]
  G   Tarife düzenliliği — SAAT-İÇİ referans-bant c_f (*)            [docs §5-G]
  P   Tarife-değişim cezası — λ·Σ|θ−cur| (tam doğrusal, ops.)        [docs §12]
  Amaç:  Σ ρ·(aktarma ödülü + sıralama ödülü) − λ·(toplam kaydırma)  [docs §4/§12]

Uygulama/ölçekleme kararları (*) — bkz. docs §10 (uygulama notları):
  (A2) Güncel veri bacak bloklarını (ElapsedTime1/2) verir → brief-exact T_OB+τ+T_IB kurulur;
       mevcut tur brief minimumunun altında görünen çiftler gece-aşan rotasyondur → mevcut tur
       çapası korunur (sep = min(exact, cur)); bloklar yoksa (eski şema) mevcut tur çapası.
  (B2) B2×E1 ÇATIŞMASI: B2 her uygun bağlantıyı zorlar; asimetrik pazarlarda E1 dengesiyle
       infeasible (bisection ile doğrulandı). Amaç zaten sunmayı ödüllendirir → B2 kapalı.
  (E2) Jmin min-seçimi büyük-M'i HiGHS'te incumbent buldurmuyor (tanı: çekirdek+E2 tek başına
       çözülemez). Küçük-ölçekte açık/doğrulanmış; `full` profilinde kapalı.
  (F)  Brief'in gerçek 10/15'i UYGULANIR: mevcut tarifedeki kova aşımları yalnız ayarlanabilir
       uçuşların kümelenmesinden; SABİT uçuşlar baz cap'i hiç aşmaz (kalkış ≤4, varış ≤5) → rezidüel
       cap ≥0, ayarlanabilirler pencerede yayılarak sığar. 7/7 gün feasible (warm-start gerekmez).
  (G)  Düzenlilik SAAT-İÇİ; grup-başına ortak bant c_f (yayılım ≤ Xdev); pencerede
       düzenlenemeyenler atlanır/raporlanır.

NOT (docs §9): sıralama ödülünde b_od, baseline 'son sırası' (s = N − yenilen, [1,N]) ile
BİREBİR aynı tabandan hesaplanır → mevcut tarife her pazarda lookup köşegenine (b==s = 'değişim
yok' nötr referansı, değeri 1/(N−1)) oturur (sıralama bir İYİLEŞTİRME ödülü). Kesin türetim
konvansiyonu organizatör teyidine tabi; model iç-tutarlı.

Çalıştırma:  python src/03_model.py            (küçük alt-örnek, tüm kısıtlar)
             python src/03_model.py full       (tam veri tek-MIP denemesi, E2 kapalı)
             python src/03_model.py byday [λ]  (güne-göre ayrıştırma + çıktı; ops. ceza λ)
             python src/03_model.py sweep      (λ ödünleşim taraması — Pareto tablo)
"""

import os
import sys
import datetime as dt
import numpy as np
import pandas as pd
import pyomo.environ as pyo

# Windows konsolu (cp1254) π/Δ gibi karakterleri basamıyor -> UTF-8'e geç
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# --------------------------------------------------------------------------- yollar
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DERIVED = os.path.join(ROOT, "derived")

# --------------------------------------------------------------------------- yapılandırma
CFG = {
    # --- alt-örnek seçimi -------------------------------------------------
    "days": [1],            # hangi operasyon günleri
    "markets": None,        # açık pazar listesi (None ise ρ'ya göre otomatik seçim)
    "top_k_markets": 6,     # ρ'ya göre en yüksek kaç (yön) pazar
    "require_competitors": True,  # yalnız ≥1 rakibi olan pazarları seç (sıralama terimini sınamak için)
    "prefer_improvable": True,    # baseline'da pencere-dışı (iyileştirilebilir) bağlantısı olan pazarları öne al
    "add_reverse": True,    # seçilen pazarların ters yönünü de ekle (E1 için)
    # --- zaman ızgarası ve pencere ---------------------------------------
    "delta_min": 10,        # Δ kova genişliği (dk)
    "wdev_min": 60,         # ayarlanabilir uçuş için ± pencere (dk)  [docs D3]
    "L_min": 60, "U_min": 300,    # bağlantı boşluğu [ℓ,u] (dk)
    # --- amaç / kısıt anahtarları ----------------------------------------
    "ranking": True,        # sıralama ödülü terimi (geçici b_od kuralı, docs §9)
    "shift_penalty": 0.0,   # (P) tarife-değişim cezası λ: amaç-puanı / uçuş-dk (0 = kapalı)
    "alpha": 0.20,          # E1 yönsel dengesizlik eşiği
    "tau_min": 45,          # τ — minimum yer süresi (dk, brief §2.4; A2 rotasyonunda)
    "gamma_min": 30,        # Γ — E2 en iyi yolculuk süresi fark eşiği (dk)
    "xdev_min": 15,         # G — aynı uçuşun günler arası maks. IST sapması (dk, docs §5-G)
    "E1_balance": True,     # (E1) yönsel SAYI dengesi
    "E2_balance": True,     # (E2) en iyi yolculuk süresi dengesi (Jmin)
    # (B2) VARSAYILAN KAPALI: B2 her uygun bağlantıyı sunmaya zorlar; tam veride asimetrik
    # pazarlarda (bir yön çok, ters yön az bağlantı) E1 dengesiyle ÇATIŞIR → infeasible.
    # Amaç zaten sunmayı ödüllendirdiğinden B2 olmadan da model dengeyi sunum SEÇEREK
    # sağlar (doc §5-B2 notu: azaltılmış modelde B2 gevşetilebilir). Bisection ile doğrulandı.
    "B2_force_offer": False,
    "A2_rotation": True,    # (A2) uçak rotasyonu: min tur = T_OB+τ+T_IB (bloklar varsa; yoksa mevcut tur)
    "A2_overnight_guard": True,  # (A2×) gece-aşan turlara statik slack-bölüşümü sınırı (byday)
    "G_regularity": True,   # (G) aynı uçuş no'nun günler arası IST tutarlılığı
    "F_capacity": True,     # (F) IST hub kova kapasitesi
    "cap_dep": 10,          # kova başına maks. (ayarlanabilir+sabit) kalkış  [docs §2]
    "cap_arr": 15,          # kova başına maks. varış
    # --- çözücü ----------------------------------------------------------
    "solver": "appsi_highs",
    "time_limit": None,     # saniye (None = sınırsız); tam veride önerilir
    "mip_gap": None,        # bağıl MIP boşluğu (None = çözücü varsayılanı)
    "warmstart": False,     # appsi Highs MIP-start'ı kullanmıyor (yalnız LP bazı) — etkisiz
}

# Hazır profiller: CFG.update(PRESETS["full"]) ile tüm veriye geç.
PRESETS = {
    "full": {                       # TÜM gün/pazar — ölçekleme koşusu
        "days": None,               # None = veride mevcut TÜM günler (hardcode etme; gizli veri uyumu)
        "markets": None, "top_k_markets": None,
        "require_competitors": False, "prefer_improvable": False,
        # E2 (Jmin zaman dengesi) tam-ölçekte KAPALI: min-seçimi büyük-M'i HiGHS'te
        # incumbent bulunamaz kılıyor (tanı: çekirdek+E2 tek başına çözülemiyor; A2/G/F/E1
        # hepsi hızlı). Küçük-ölçekte E2 açık ve doğrulanmış kalır. Bkz. docs §10.
        "E2_balance": False,
        "time_limit": 600, "mip_gap": 0.01,
    },
}


# =========================================================================== veri
def all_operation_days():
    """Veride mevcut TÜM operasyon günleri. Gün listesini HARDCODE etmemek için (gizli
    test verisi farklı sayıda/etikette güne sahip olabilir) tk_connections.csv'den okunur."""
    df = pd.read_csv(os.path.join(DERIVED, "tk_connections.csv"),
                     encoding="utf-8-sig", usecols=["day"])
    return sorted(int(d) for d in df["day"].dropna().unique())


def load_data():
    rd = lambda f, **k: pd.read_csv(os.path.join(DERIVED, f), encoding="utf-8-sig", **k)
    markets = rd("markets.csv")
    nod = rd("market_n_od.csv")
    tk = rd("tk_connections.csv", parse_dates=["ist_arr", "ist_dep"])
    tcomp = rd("competitor_times_carrier.csv")
    rank = rd("ranking_lookup.csv")
    if rank.shape[1] != 4:                       # beklenen şema: N, ilk-rank, son-rank, ağırlık
        raise ValueError(f"ranking_lookup.csv 4 sütun bekler, {rank.shape[1]} bulundu "
                         f"({list(rank.columns)}) — sıralama ödülü tablosu şeması beklenenden farklı.")
    rank.columns = ["N", "b", "s", "W"]          # konumsal sabitleme (Rakip Sayısı/İlk/Son/Weight)
    nopart = rd("tk_flights_without_partner.csv")["flno_no_rotation_partner"].tolist()
    rot = rd("flight_rotation.csv")              # FlNo, Orig, Dest, Pair
    # bacak blok süreleri (güncel şema; A2 için brief-exact minimum tur) — yoksa None
    blk_path = os.path.join(DERIVED, "flight_block_times.csv")
    blocks = None
    if os.path.exists(blk_path):
        bdf = pd.read_csv(blk_path, encoding="utf-8-sig")
        blocks = {(int(r.flno), int(r.day), str(r.role)): float(r.block_min)
                  for r in bdf.itertuples()}
    return markets, nod, tk, tcomp, rank, set(nopart), rot, blocks


def rotation_pairs(rot):
    """Flight Pairs'ten (IST→o giden, o→IST gelen) uçak rotasyon eşleri.
    Aynı 'Pair' iki uçuş no'yu gruplar; Orig=IST olan giden (dep), Dest=IST olan gelen (arr)."""
    pairs = []
    for _, grp in rot.groupby("Pair"):
        outs = grp[grp["Orig"] == "IST"]["FlNo"].tolist()   # IST→o (kalkış)
        ins = grp[grp["Dest"] == "IST"]["FlNo"].tolist()    # o→IST (varış)
        for of in outs:
            for inf in ins:
                pairs.append((int(of), int(inf)))
    return pairs


def select_markets(markets, nod, tk, days):
    """ρ'ya göre alt-örnek pazarları seç (has_tk, ρ tanımlı, seçilen günlerde bağlantısı olan)."""
    d = tk[tk["day"].isin(days)]
    mk_with_conn = set(d["market"])
    if CFG["markets"]:                      # açık liste verildiyse onu kullan
        chosen = [m for m in CFG["markets"] if m in mk_with_conn]
        if CFG["add_reverse"]:
            for m in list(chosen):
                o, dd = m.split("-")
                rev = f"{dd}-{o}"
                if rev in mk_with_conn and rev not in chosen:
                    chosen.append(rev)
        return chosen
    cand = markets[(markets["has_tk"]) & (~markets["excluded_no_rho"])
                   & (markets["rho"].notna()) & (markets["market"].isin(mk_with_conn))].copy()
    if CFG["require_competitors"]:
        nd = nod[nod["day"].isin(days)].groupby("market")["N_od"].max()
        has_comp = set(nd[nd >= 1].index)
        cand = cand[cand["market"].isin(has_comp)]
    if CFG["prefer_improvable"]:
        # baseline'da ≥1 bağlantısı pencere dışı (gap ∉ [L,U]) olan pazarları öne al
        gg = d.copy()
        gg["out"] = ~gg["gap_min"].between(CFG["L_min"], CFG["U_min"])
        improvable = set(gg.groupby("market")["out"].any().pipe(lambda s: s[s].index))
        cand["_imp"] = cand["market"].isin(improvable)
        cand = cand.sort_values(["_imp", "rho"], ascending=[False, False])
    else:
        cand = cand.sort_values("rho", ascending=False)
    chosen = list(cand["market"] if CFG["top_k_markets"] is None
                  else cand["market"].head(CFG["top_k_markets"]))
    if CFG["add_reverse"]:
        rho_map = markets.set_index("market")["rho"]
        for m in list(chosen):
            o, dd = m.split("-")
            rev = f"{dd}-{o}"
            if rev in mk_with_conn and rev not in chosen and not pd.isna(rho_map.get(rev, np.nan)):
                chosen.append(rev)
    return chosen


# =========================================================================== örnek/önişleme
class Instance:
    """Modelin tükettiği önişlenmiş alt-örnek."""
    pass


def build_instance():
    markets, nod, tk, tcomp, rank, fixed_flnos, rot, blocks = load_data()
    days = CFG["days"]
    chosen = select_markets(markets, nod, tk, days)

    rho_map = markets.set_index("market")["rho"].to_dict()
    nod_map = nod.set_index(["market", "day"])["N_od"].to_dict()
    delta = CFG["delta_min"]
    wd = CFG["wdev_min"]

    # zaman referansı: tüm zaman damgalarının en küçüğü (mutlak dakika için)
    sub = tk[tk["market"].isin(chosen) & tk["day"].isin(days)].copy()
    if sub.empty:                                     # ValueError → run_byday yakalayıp günü atlar
        raise ValueError("Seçilen alt-örnekte bağlantı yok — CFG'yi gevşetin.")
    t0 = min(sub["ist_arr"].min(), sub["ist_dep"].min()).normalize()

    def abs_min(ts):
        return (ts - t0).total_seconds() / 60.0

    def snap(m):
        return int(round(m / delta) * delta)

    # --- olaylar (instances): her IST kalkış/varış olayı tek bir karar zamanı ----
    # anahtar = (flno, rol, snap(mevcut))  — aynı uçak/olay birden çok bağlantıda paylaşılır.
    events = {}        # key -> dict(id, flno, role, cur, day, adjustable, cands)

    def get_event(flno, role, cur_abs, day):
        cur = snap(cur_abs)
        key = (int(flno), role, cur)
        if key not in events:
            adj = int(flno) not in fixed_flnos          # rotasyon partneri yoksa SABIT (docs D6)
            if adj:
                cands = [cur + k * delta for k in range(-(wd // delta), wd // delta + 1)]
            else:
                cands = [cur]
            events[key] = dict(id=len(events), flno=int(flno), role=role,
                               cur=cur, day=int(day), adjustable=adj, cands=cands)
        return events[key]["id"]

    # --- bağlantılar (π) ---------------------------------------------------
    conns = []         # her biri: dict(market, day, arr_eid, dep_eid, legsum, gap_cur)
    for _, r in sub.iterrows():
        arr_eid = get_event(r["FlNo1"], "arr", abs_min(r["ist_arr"]), r["day"])
        dep_eid = get_event(r["FlNo2"], "dep", abs_min(r["ist_dep"]), r["day"])
        conns.append(dict(market=r["market"], day=int(r["day"]),
                          arr_eid=arr_eid, dep_eid=dep_eid,
                          legsum=float(r["legsum_min"]),
                          gap_cur=float(r["gap_min"])))

    ev_by_id = {e["id"]: e for e in events.values()}

    # --- (F için) modellenmeyen uçuşların kova kullanımı --------------------
    # Amaç evrenine girmeyen pazarların (ör. ρ tanımsız → dışlanan) uçuşları da IST
    # kovalarını FİZİKSEL olarak doldurur. Karar değişkeni olmazlar ama F kapasitesinde
    # sabit kullanım olarak sayılırlar (instance olayıyla çakışan uçuş zaten sayılıdır).
    rest = tk[tk["day"].isin(days) & ~tk["market"].isin(set(chosen))]
    rest_keys = set()
    for r in rest.itertuples():
        rest_keys.add((int(r.FlNo1), "arr", snap(abs_min(r.ist_arr))))
        rest_keys.add((int(r.FlNo2), "dep", snap(abs_min(r.ist_dep))))
    extra_use = {}
    for (flno, role, cur) in rest_keys - set(events.keys()):
        extra_use[(role, cur)] = extra_use.get((role, cur), 0) + 1

    # --- (A2 evren-eksiği) rotasyon ortaklarının TAM evrendeki fiziksel saatleri -----
    # U4'ün F'de düzelttiği "amaç evreni eksikliği" A2 için de geçerlidir: bir rotasyon
    # ortağının bağlantısı amaç evreninde (chosen) değilse (ör. ρ tanımsız pazar) o günkü
    # olay HİÇ modellenmez → A2 kısıtı o gün için hiç kurulamaz (build_model bunu ANKOR
    # olarak kullanır; bkz. docs §10-U9). full_role_time TÜM (chosen ∪ dışlanan) günler/
    # pazarlar için gerçek snap'lenmiş saatleri tutar — extra_use'un A2 karşılığıdır.
    full_all = tk[tk["day"].isin(days)]
    full_role_time = {}
    for r in full_all.itertuples():
        full_role_time[(int(r.FlNo1), "arr", int(r.day))] = snap(abs_min(r.ist_arr))
        full_role_time[(int(r.FlNo2), "dep", int(r.day))] = snap(abs_min(r.ist_dep))

    # --- pazar-gün grupları (md) ------------------------------------------
    md = {}            # (market,day) -> dict(rho, N, comps{carrier:Tcomp}, conns[idx], b_od)
    for pi, c in enumerate(conns):
        key = (c["market"], c["day"])
        if key not in md:
            comps = tcomp[(tcomp["market"] == c["market"]) & (tcomp["day"] == c["day"])]
            comp_map = dict(zip(comps["carrier"], comps["T_comp_min"]))
            md[key] = dict(rho=float(rho_map.get(c["market"], 0.0)),
                           N=int(nod_map.get(key, len(comp_map))),
                           comps=comp_map, conns=[], b_od=None)
        md[key]["conns"].append(pi)

    # --- b_od (taban sıralama, docs §9): baseline 'son sıra' (s) ile BİREBİR tutarlı ----
    # Sıralama ödülü bir İYİLEŞTİRME ödülüdür (brief §2.4): lookup köşegeni b==s = 'değişim yok'
    # nötr referansı (değeri 1/(N−1)). Dolayısıyla mevcut tarife (baseline) HER pazarda buna oturmalı ⇒
    # b_od, baseline'da s=clip(N−beaten,1,N) ile AYNI tabandan hesaplanır: pencere-içi
    # ([L,U]) sunulan bağlantıların en iyi J'si üzerinden yenilen rakip sayısından türetilir.
    # (Eski kural faster+1 idi; s=N−beaten konvansiyonuna göre 1 kayıyor ve baseline'ı
    #  pazarların ~%29'unda köşegen-dışına itiyordu → mevcut tarifeye hak edilmemiş ödül.)
    Lc, Uc = CFG["L_min"], CFG["U_min"]
    for key, g in md.items():
        if g["N"] >= 1 and g["conns"]:
            offered0 = [pi for pi in g["conns"] if Lc <= conns[pi]["gap_cur"] <= Uc]
            if offered0 and g["comps"]:
                j_best0 = min(conns[pi]["legsum"] + conns[pi]["gap_cur"] for pi in offered0)
                beaten0 = sum(1 for tc in g["comps"].values() if j_best0 <= tc)
            else:
                beaten0 = 0
            g["b_od"] = int(np.clip(g["N"] - beaten0, 1, g["N"]))

    # --- yardımcı indeksler (A2 rotasyon, G düzenlilik için) --------------
    ev_by_flno_role = {}                 # (flno, role) -> [eid]
    for e in events.values():
        ev_by_flno_role.setdefault((e["flno"], e["role"]), []).append(e["id"])

    inst = Instance()
    inst.events, inst.ev_by_id, inst.conns, inst.md = events, ev_by_id, conns, md
    inst.extra_use = extra_use           # (rol, kova) -> modellenmeyen sabit uçuş sayısı (F)
    inst.rank = rank
    inst.L, inst.U = CFG["L_min"], CFG["U_min"]
    inst.t0, inst.delta = t0, delta
    inst.ev_by_flno_role = ev_by_flno_role
    inst.rot_pairs = rotation_pairs(rot)
    inst.blocks = blocks                 # (flno, day, role) -> blok dk | None (eski şema)
    inst.full_role_time = full_role_time  # (flno, role, day) -> snap dk (A2 evren-eksiği ankoru)
    return inst


# =========================================================================== model
def rank_weight_table(rank_df):
    return {(int(r.N), int(r.b), int(r.s)): float(r.W) for r in rank_df.itertuples()}


def rank_reward(rkW, N, b_od, beaten):
    """Sıralama ödülü: yenilen sayısı 'beaten' iken Wʳ(N, b_od, s), s = clamp(N−beaten, 1, N).
    docs §4/§9 (GEÇİCİ kural). N<1 veya b_od yoksa 0 (rakip yok → sıralama terimi tanımsız)."""
    if N < 1 or b_od is None:
        return 0.0
    s = int(np.clip(N - beaten, 1, N))
    return rkW.get((N, b_od, s), 0.0)


def theta_expr(model, inst, eid):
    """Olay eid'nin IST zamanı (dk): ayarlanabilirse Σ val·x, sabitse sabit."""
    e = inst.ev_by_id[eid]
    if e["adjustable"]:
        return sum(v * model.x[eid, v] for v in e["cands"])
    return float(e["cands"][0])


def build_model(inst):
    m = pyo.ConcreteModel()
    L, U = inst.L, inst.U

    # --- değişkenler: x[eid,val] (yalnız ayarlanabilir olaylar) -------------
    x_index = [(e["id"], v) for e in inst.ev_by_id.values() if e["adjustable"] for v in e["cands"]]
    m.x = pyo.Var(x_index, domain=pyo.Binary)

    # y_π : bağlantı sunuluyor (uygun) mu
    P = list(range(len(inst.conns)))
    m.y = pyo.Var(P, domain=pyo.Binary)
    if CFG["B2_force_offer"]:
        m.s = pyo.Var(P, domain=pyo.Binary)     # B2 ayrık "çok kısa / çok uzun" seçici

    m.cons = pyo.ConstraintList()

    # --- (A1) her ayarlanabilir olay tam bir kovaya atanır -----------------
    for e in inst.ev_by_id.values():
        if e["adjustable"]:
            m.cons.add(sum(m.x[e["id"], v] for v in e["cands"]) == 1)

    # --- gap_π ifadesi ve büyük-M aralıkları -------------------------------
    gap = {}
    for pi, c in enumerate(inst.conns):
        gap[pi] = theta_expr(m, inst, c["dep_eid"]) - theta_expr(m, inst, c["arr_eid"])
        ea, ed = inst.ev_by_id[c["arr_eid"]], inst.ev_by_id[c["dep_eid"]]
        gmin = min(ed["cands"]) - max(ea["cands"])       # ulaşılabilir en küçük boşluk
        gmax = max(ed["cands"]) - min(ea["cands"])       # ulaşılabilir en büyük boşluk
        c["gmin"], c["gmax"] = gmin, gmax

        # --- (B1) y=1 ⟹ ℓ ≤ gap ≤ u  (yön-yerel sıkı M) ------------------
        Mlo = max(0, L - gmin)
        Mhi = max(0, gmax - U)
        m.cons.add(gap[pi] >= L - Mlo * (1 - m.y[pi]))
        m.cons.add(gap[pi] <= U + Mhi * (1 - m.y[pi]))
        # uygun aralık hiç yakalanamıyorsa y=0 sabitlenir
        if gmax < L or gmin > U:
            m.cons.add(m.y[pi] == 0)
        # --- (B2) uygun ⟹ y=1  (zorunlu sunum; ayrık alt/üst seçimi s_π) ---
        elif CFG["B2_force_offer"]:
            d2 = inst.delta
            Mb = max(d2, gmax - (L - d2), (U + d2) - gmin)
            # y=0,s=0 ⟹ gap ≤ ℓ−Δ (çok kısa) ;  y=0,s=1 ⟹ gap ≥ u+Δ (çok uzun)
            m.cons.add(gap[pi] <= (L - d2) + Mb * (m.y[pi] + m.s[pi]))
            m.cons.add(gap[pi] >= (U + d2) - Mb * (m.y[pi] + (1 - m.s[pi])))

    # --- (C) azalan-getiri / monoton slotlar -------------------------------
    # z[md_id, j] : md grubunda j. slot dolu mu
    md_keys = list(inst.md.keys())
    md_id = {k: i for i, k in enumerate(md_keys)}
    z_index, Wc = [], {}
    for k, g in inst.md.items():
        M = len(g["conns"])
        for j in range(1, M + 1):
            z_index.append((md_id[k], j))
            Wc[(md_id[k], j)] = 0.5 ** (j - 1)          # W^c_j = (1/2)^{j-1}
    m.z = pyo.Var(z_index, domain=pyo.Binary)
    for k, g in inst.md.items():
        i = md_id[k]
        M = len(g["conns"])
        m.cons.add(sum(m.y[pi] for pi in g["conns"]) == sum(m.z[i, j] for j in range(1, M + 1)))
        for j in range(1, M):
            m.cons.add(m.z[i, j] >= m.z[i, j + 1])      # monoton doldurma

    # --- (D) rakip yenme + sıralama ----------------------------------------
    # w[(pi,carrier)] yalnız "koşullu" durumda yaratılır; "hep yener" → y, "asla" → yok.
    w = {}                       # (pi, carrier) -> Var  (koşullu)
    beat_eq_y = {}               # (pi, carrier) -> True  (offered ⟹ beats; w := y)
    m.w = pyo.Var(pyo.Any, domain=pyo.Binary, dense=False)   # seyrek binary havuzu
    for k, g in inst.md.items():
        for pi in g["conns"]:
            c = inst.conns[pi]
            for carrier, Tc in g["comps"].items():
                G = Tc - c["legsum"]                    # izinli maks. boşluk (yenmek için)
                lo = max(L, c["gmin"])                  # sunulurken ulaşılabilir en küçük boşluk
                if G < lo:
                    continue                            # asla yenemez → w ≡ 0
                elif G >= U:
                    beat_eq_y[(pi, carrier)] = True     # sunulduğunda hep yener → w = y
                else:
                    wv = m.w[("w", pi, carrier)]        # koşullu
                    w[(pi, carrier)] = wv
                    Mw = max(1.0, c["gmax"] - G)
                    m.cons.add(wv <= m.y[pi])
                    m.cons.add(gap[pi] <= G + Mw * (1 - wv))

    # β[(md_id,carrier)] : rakip yenildi mi  (yenen ≥1 sunulu bağlantı varsa)
    beta = {}
    for k, g in inst.md.items():
        i = md_id[k]
        for carrier in g["comps"]:
            terms = []
            for pi in g["conns"]:
                if (pi, carrier) in beat_eq_y:
                    terms.append(m.y[pi])
                elif (pi, carrier) in w:
                    terms.append(w[(pi, carrier)])
            if not terms:
                continue
            bv = m.w[("beta", i, carrier)]
            beta[(i, carrier)] = bv
            m.cons.add(bv <= sum(terms))                # β ≤ Σ w  (ödül β'yı yukarı iter)

    # γ[(md_id,bcount)] : yenilen rakip sayısı seçici (Σγ=1, Σ b·γ = Σβ)
    # NOT: doküman §4'te Σγ=1 KOŞULSUZ — yenilebilir rakip olmasa da beaten=0 için
    # taban ödülü Wʳ(N,b_od,N) kazanılır. Bu yüzden N≥1 olan her pazar için γ kurulur.
    obj_terms = []
    rkW = rank_weight_table(inst.rank)
    if CFG["ranking"]:
        for k, g in inst.md.items():
            i = md_id[k]
            N, b_od = g["N"], g["b_od"]
            if N < 1 or b_od is None:
                continue
            betas = [beta[(i, ca)] for ca in g["comps"] if (i, ca) in beta]
            gam = {bn: m.w[("gam", i, bn)] for bn in range(0, N + 1)}
            m.cons.add(sum(gam.values()) == 1)
            m.cons.add(sum(bn * gam[bn] for bn in gam) == (sum(betas) if betas else 0))
            for bn, gv in gam.items():
                obj_terms.append(g["rho"] * rank_reward(rkW, N, b_od, bn) * gv)

    # --- (E1) yönsel SAYI dengesi (opsiyonel) ------------------------------
    if CFG["E1_balance"]:
        a = CFG["alpha"]
        seen = set()
        for k, g in inst.md.items():
            (mk, day) = k
            o, dd = mk.split("-")
            rk = (f"{dd}-{o}", day)
            if rk in inst.md and (rk, k) not in seen:
                seen.add((k, rk))
                n_od = sum(m.y[pi] for pi in g["conns"])
                n_do = sum(m.y[pi] for pi in inst.md[rk]["conns"])
                m.cons.add(n_od - n_do <= a * (n_od + n_do))
                m.cons.add(n_do - n_od <= a * (n_od + n_do))

    # --- (A2) uçak rotasyonu: min tur = T_OB + τ + T_IB (brief §4.1) ---------
    # Güncel veri bacak bloklarını verir → brief-exact minimum kurulur. Mevcut tur
    # brief minimumunun ALTINDAYSA (gece-aşan rotasyonun aynı-gün izdüşümü; fiziksel
    # tur gün h → h+1'e yayılır) mevcut tur çapası korunur: sep = min(exact, cur).
    # Böylece (i) gerçek aynı-gün turlar asla brief minimumunun altına sıkışmaz,
    # (ii) gece-aşan çiftlerde mevcut desen korunur (gün-bağlaşımı yaratılmaz;
    # fiziksel h→h+1 kısıtı çözüm-sonrası ayrıca doğrulanır). Bloklar yoksa (eski
    # şema) ihtiyatlı geri-dönüş: sep = mevcut turnaround.
    m._n_a2 = 0
    m._n_a2_exact = 0
    if CFG["A2_rotation"]:
        tau = CFG["tau_min"]
        for out_f, in_f in inst.rot_pairs:
            for oe in inst.ev_by_flno_role.get((out_f, "dep"), []):
                for ie in inst.ev_by_flno_role.get((in_f, "arr"), []):
                    ed, ea = inst.ev_by_id[oe], inst.ev_by_id[ie]
                    if ed["day"] != ea["day"]:
                        continue                        # aynı operasyon günü rotasyonu
                    turn = ea["cur"] - ed["cur"]        # mevcut turnaround (dk)
                    if turn <= 0:
                        continue
                    sep = turn
                    if inst.blocks is not None:
                        t_ob = inst.blocks.get((out_f, ed["day"], "dep"))
                        t_ib = inst.blocks.get((in_f, ea["day"], "arr"))
                        if t_ob is not None and t_ib is not None:
                            exact = t_ob + tau + t_ib
                            if exact <= turn:           # gerçek aynı-gün tur
                                sep = exact
                                m._n_a2_exact += 1
                    m.cons.add(theta_expr(m, inst, ie) - theta_expr(m, inst, oe) >= sep)
                    m._n_a2 += 1

        # --- (A2×evren) rotasyon ortağının amaç-evreni-dışı günleri (docs §10-U9) ---
        # Üstteki döngü YALNIZ HER İKİ tarafın da modellendiği (gün,pazar-evreni-içi)
        # günleri kapsar. Bir tarafın bağlantısı amaç evreninde değilse (ör. ρ tanımsız
        # pazar → o günkü olay hiç kurulmaz, D5) o gün için kısıt HİÇ oluşmazdı — F'de
        # (U4) düzeltilen "amaç evreni eksikliği" açığının A2 karşılığı (bağımsız
        # doğrulayıcı 05'in yakaladığı gerçek ihlal). Bu blok, üstteki döngünün
        # ATLADIĞI her (pair,gün) için modellenmeyen tarafı full_role_time'daki SABİT
        # gerçek saatiyle ANKORLAYARAK kısıtı ekler (05'in sep=min(exact,turn) formülüyle
        # birebir). Her iki taraf da modelsizse (fiziksel arşiv verisi, karar dışı)
        # atlanır — o zaten sabit veridir, kısıt uygulanamaz/gereksizdir.
        m._n_a2_anchor = 0
        frt = getattr(inst, "full_role_time", None)
        if frt:
            for out_f, in_f in inst.rot_pairs:
                modeled_days = {inst.ev_by_id[oe]["day"]
                                for oe in inst.ev_by_flno_role.get((out_f, "dep"), [])
                                for ie in inst.ev_by_flno_role.get((in_f, "arr"), [])
                                if inst.ev_by_id[oe]["day"] == inst.ev_by_id[ie]["day"]}
                all_days = {d for (f, r, d) in frt if f in (out_f, in_f)}
                for d in all_days - modeled_days:
                    dep_full = frt.get((out_f, "dep", d))
                    arr_full = frt.get((in_f, "arr", d))
                    if dep_full is None or arr_full is None:
                        continue
                    turn = arr_full - dep_full
                    if turn <= 0:
                        continue
                    sep = turn
                    t_ob = inst.blocks.get((out_f, d, "dep")) if inst.blocks else None
                    t_ib = inst.blocks.get((in_f, d, "arr")) if inst.blocks else None
                    if t_ob is not None and t_ib is not None:
                        sep = min(t_ob + tau + t_ib, turn)
                    oe = next((e for e in inst.ev_by_flno_role.get((out_f, "dep"), [])
                              if inst.ev_by_id[e]["day"] == d), None)
                    ie = next((e for e in inst.ev_by_flno_role.get((in_f, "arr"), [])
                              if inst.ev_by_id[e]["day"] == d), None)
                    if oe is None and ie is None:
                        continue                        # her iki taraf da sabit veri → gereksiz
                    dep_expr = theta_expr(m, inst, oe) if oe is not None else dep_full
                    arr_expr = theta_expr(m, inst, ie) if ie is not None else arr_full
                    m.cons.add(arr_expr - dep_expr >= sep)
                    m._n_a2_anchor += 1

    # --- (A2×) gece-aşan rotasyon koruması (byday, bkz. run_byday) ----------
    # Fiziksel tur gün h→h+1'e yayılan çiftlerde gün-ayrıştırması turu bozmasın:
    # mevcut tarifedeki pay (slack) statik ikiye bölünür —
    #  rotcap : bugünün kalkışı en çok slack/2 GEÇ kayabilir (tavan),
    #  rotlock: bugünün dönüş varışı en çok slack/2 ERKEN kayabilir (taban)
    # → θ_in − θ_out ≥ T_OB+τ+T_IB yapısal garanti; gün-bağlaşımı doğmaz.
    # Değerler GERÇEK zaman (datetime) verilir; bu örneğin eksenine çevrilir.
    m._n_rot_chain = 0
    for attr, role, sense in [("rotlock", "arr", "lo"), ("rotcap", "dep", "hi")]:
        bounds = getattr(inst, attr, None) or {}
        for (flno, day), val_dt in bounds.items():
            val = (val_dt - inst.t0).total_seconds() / 60.0
            for eid in inst.ev_by_flno_role.get((flno, role), []):
                e = inst.ev_by_id[eid]
                if e["day"] != day or not e["adjustable"]:
                    continue
                if sense == "lo":
                    m.cons.add(theta_expr(m, inst, eid) >= val)
                else:
                    m.cons.add(theta_expr(m, inst, eid) <= val)
                m._n_rot_chain += 1

    # --- (G) tarife düzenliliği: aynı uçuş no günler arası ≤ Xdev -----------
    # Wdev↔G gerilimi: pencere ±Wdev her olayı KENDİ mevcut saatine bağlar; iki günün
    # mevcut saatleri 2·Wdev+Xdev'den fazla farklıysa ortak düzenli saat penceredе YOK.
    # Bu yüzden G yalnız pencerenin izin verdiği çiftlere uygulanır; gerisi "pencere
    # içinde düzenlenemez" olarak atlanır (belgeli — Wdev/Xdev büyütülerek genişletilebilir).
    # NOT: θ MUTLAK dakika (t0'dan) → günler arası ~1440·gün fark içerir. Düzenlilik
    # SAAT-İÇİ (time-of-day) tutarlılıktır; her olaydan kendi günü-gece-yarısı ofseti
    # çıkarılır: θ' = θ − ⌊cur/1440⌋·1440.  "En fazla Xdev sapar" → grup-başına ortak
    # bant c_f: tüm günlerin saat-içi zamanı [c_f, c_f+Xdev] içinde (yayılım ≤ Xdev).
    # Pencerede ortak bant olamayan gruplar (saat-içi yayılım > 2·Wdev+Xdev) atlanır.
    m._n_g = 0
    m._n_g_skip = 0
    if CFG["G_regularity"]:
        Xd = CFG["xdev_min"]
        reach = 2 * CFG["wdev_min"] + Xd
        offset = lambda e: (inst.ev_by_id[e]["cur"] // 1440) * 1440
        tod = lambda e: inst.ev_by_id[e]["cur"] - offset(e)        # mevcut saat-içi (dk)
        reg_groups = []                                  # (gkey, [eids]) düzenlenebilir gruplar
        for fr, eids in inst.ev_by_flno_role.items():
            adj = [e for e in eids if inst.ev_by_id[e]["adjustable"]
                   and len({inst.ev_by_id[x]["day"] for x in eids}) >= 1]
            # günler arası (her gün bir olay; gün-içi anomali tekrarları dahil edilir)
            days = {inst.ev_by_id[e]["day"] for e in adj}
            if len(adj) < 2 or len(days) < 2:
                continue
            tods = [tod(e) for e in adj]
            if max(tods) - min(tods) > reach:
                m._n_g_skip += 1                         # pencerede ortak bant yok
                continue
            reg_groups.append((fr, adj))
        if reg_groups:
            m.creg = pyo.Var(range(len(reg_groups)), domain=pyo.Reals)
            for gi, (fr, adj) in enumerate(reg_groups):
                for e in adj:
                    th = theta_expr(m, inst, e) - offset(e)
                    m.cons.add(m.creg[gi] <= th)
                    m.cons.add(th <= m.creg[gi] + Xd)
                    m._n_g += 1
        # --- gün-arası G kuplajı (decomposition): önceki günlerden gelen bant ----
        # inst.gband[(flno,role)] = yerleşmiş saat-içi merkez. Bu günün aynı uçuşu o
        # merkezin ±Xdev'inde tutulur (pencere ulaşamıyorsa atlanır → kayıt edilir).
        gband = getattr(inst, "gband", None)
        if gband:
            for e in inst.ev_by_id.values():
                if not e["adjustable"]:
                    continue
                key = (e["flno"], e["role"])
                c0 = gband.get(key)
                if c0 is None:
                    continue
                etod = e["cur"] - (e["cur"] // 1440) * 1440
                if abs(etod - c0) > CFG["wdev_min"] + Xd:
                    m._n_g_skip += 1                      # bu günün penceresi banda ulaşamıyor
                    continue
                th = theta_expr(m, inst, e["id"]) - (e["cur"] // 1440) * 1440
                m.cons.add(th >= c0 - Xd)
                m.cons.add(th <= c0 + Xd)
                m._n_g += 1

    # --- (E2) en iyi yolculuk süresi (Jmin) dengesi ------------------------
    if CFG["E2_balance"]:
        ids = list(md_id.values())
        m.Jmin = pyo.Var(ids, domain=pyo.Reals)
        m.act = pyo.Var(ids, domain=pyo.Binary)
        m.u = pyo.Var(P, domain=pyo.Binary)            # Jmin'i veren bağlantı seçici
        for k, g in inst.md.items():
            i, cs = md_id[k], g["conns"]
            Mexpr = len(cs)
            n_md = sum(m.y[pi] for pi in cs)
            m.cons.add(m.act[i] <= n_md)
            m.cons.add(n_md <= Mexpr * m.act[i])
            Jlo = min(inst.conns[pi]["legsum"] + inst.conns[pi]["gmin"] for pi in cs)
            Jhi = max(inst.conns[pi]["legsum"] + inst.conns[pi]["gmax"] for pi in cs)
            g["_Jlo"], g["_Jhi"] = Jlo, Jhi
            MJ = max(1.0, Jhi - Jlo)
            for pi in cs:
                Jpi = inst.conns[pi]["legsum"] + gap[pi]
                m.cons.add(m.Jmin[i] <= Jpi + MJ * (1 - m.y[pi]))     # ≤ her sunulu J
                m.cons.add(m.Jmin[i] >= Jpi - MJ * (1 - m.u[pi]))     # ≥ seçilen J
                m.cons.add(m.u[pi] <= m.y[pi])
            m.cons.add(sum(m.u[pi] for pi in cs) == m.act[i])         # tam 1 seçili (aktifse)
        Gam = CFG["gamma_min"]
        seen = set()
        for k, g in inst.md.items():
            (mk, day) = k
            o, dd = mk.split("-")
            rk = (f"{dd}-{o}", day)
            if rk in inst.md and (rk, k) not in seen and (k, rk) not in seen:
                seen.add((k, rk))
                i, j = md_id[k], md_id[rk]
                gr = inst.md[rk]
                ME = max(1.0, max(g["_Jhi"], gr["_Jhi"]) - min(g["_Jlo"], gr["_Jlo"]))
                relax = ME * (2 - m.act[i] - m.act[j])
                m.cons.add(m.Jmin[i] - m.Jmin[j] <= Gam + relax)
                m.cons.add(m.Jmin[j] - m.Jmin[i] <= Gam + relax)

    # --- (F) IST hub kova kapasitesi --------------------------------------
    # Her grid kovası t (mutlak dk; her t tek bir (gün, saat-içi)) için ayarlanabilir
    # atamalar + o kovadaki sabit uçuşlar ≤ brief baz kapasitesi (kalkış 10 / varış 15).
    # VERİ BULGUSU (doğrulandı): mevcut tarifedeki kova aşımları TAMAMEN ayarlanabilir
    # uçuşların mevcut saatlerinde kümelenmesinden gelir; SABİT (kımıldamayan) uçuşlar
    # hiçbir kovada baz cap'i aşmaz (kalkış max 4≤10, varış max 5≤15). Dolayısıyla baz
    # 10/15 brief'e sadık biçimde UYGULANABİLİR: ayarlanabilir uçuşlar ±Wdev penceresinde
    # yayılarak rezidüel kapasiteye sığar (gün başına ort. ~4–5/kova, ~120 kova). Mevcut
    # tarife artık warm-start için uygun değil, ama appsi-Highs MIP-start kullanmadığından
    # bu maliyetsiz; F gerçek bir kısıt olur (önceki max(baz,mevcut) F'i fiilen bağlamıyordu).
    m._n_f = 0
    m._n_f_overflow = 0                                  # kımıldatılamayanların tek başına aştığı kova
    if CFG["F_capacity"]:
        extra_use = getattr(inst, "extra_use", {})       # modellenmeyen uçuşların sabit kullanımı
        for role, base in [("dep", CFG["cap_dep"]), ("arr", CFG["cap_arr"])]:
            terms, cur_use = {}, {}
            for e in inst.ev_by_id.values():
                if e["role"] != role:
                    continue
                cur_use[e["cur"]] = cur_use.get(e["cur"], 0) + 1     # kova kümesi için
                if e["adjustable"]:
                    for v in e["cands"]:
                        terms.setdefault(v, []).append((e["id"], v))
            fixed = {}                                   # kova -> sabit uçuş sayısı
            for e in inst.ev_by_id.values():
                if e["role"] == role and not e["adjustable"]:
                    fixed[e["cur"]] = fixed.get(e["cur"], 0) + 1
            for (ro, v), n in extra_use.items():         # modellenmeyen pazarların uçuşları da
                if ro == role:                           # IST kovalarını fiziksel olarak doldurur
                    fixed[v] = fixed.get(v, 0) + n
            for v in set(terms) | set(cur_use) | set(fixed):
                tv = [m.x[eid, vv] for eid, vv in terms.get(v, [])]
                fc = fixed.get(v, 0)
                cap = base                               # brief §4.6: gerçek rezidüel cap (10/15)
                if fc > cap:                             # kımıldatılamayanlar tek başına aşıyor →
                    m._n_f_overflow += 1                 # ayarlanabilir hiç giremez (veri-taşması raporlanır)
                    cap = fc
                if len(tv) + fc > cap:                   # ancak bağlayabilirse ekle
                    m.cons.add(sum(tv) + fc <= cap)
                    m._n_f += 1

    # --- amaç: Σ ρ·(aktarma ödülü + sıralama ödülü) − λ·(toplam kaydırma) ----
    for k, g in inst.md.items():
        i = md_id[k]
        M = len(g["conns"])
        for j in range(1, M + 1):
            obj_terms.append(g["rho"] * Wc[(i, j)] * m.z[i, j])
    comp_expr = sum(obj_terms)                       # SAF rekabetçilik faydası (cezasız)
    # (P) tarife-değişim cezası: A1 her olayda Σ_v x[eid,v]=1 olduğundan, kaydırmanın
    # mutlak değeri |θ−cur| = Σ_v |v−cur|·x[eid,v] — TAM DOĞRUSAL (ek değişken / big-M YOK).
    # λ = amaç-puanı / uçuş-dk. Yalnız ayarlanabilir olaylar cezalandırılır (sabitler kımıldamaz).
    lam = CFG["shift_penalty"]
    shift_terms = []
    for e in inst.ev_by_id.values():
        if e["adjustable"]:
            for v in e["cands"]:
                dv = abs(v - e["cur"])
                if dv:
                    shift_terms.append(dv * m.x[e["id"], v])
    m._shift_expr = sum(shift_terms) if shift_terms else 0.0
    m._comp_expr = comp_expr
    m.OBJ = pyo.Objective(expr=(comp_expr - lam * m._shift_expr) if lam > 0 else comp_expr,
                          sense=pyo.maximize)

    m._md_id = md_id
    m._gap = gap
    m._w = w
    m._beat_eq_y = beat_eq_y
    m._beta = beta
    return m


def set_warmstart(inst, m):
    """Mevcut tarifeyi (x=mevcut saat) TAM tutarlı uygun çözüm olarak değişkenlere yaz.
    Büyük-M MIP'te HiGHS'in incumbent bulamaması sorununu çözer (baseline'dan iyileştirir)."""
    md_id, L, U = m._md_id, inst.L, inst.U
    cur = {e["id"]: e["cur"] for e in inst.ev_by_id.values()}
    sv = lambda var, val: var.set_value(val, skip_validation=True)
    for e in inst.ev_by_id.values():                  # x = mevcut kova
        if e["adjustable"]:
            for v in e["cands"]:
                sv(m.x[e["id"], v], 1 if v == e["cur"] else 0)
    yv, Jc = {}, {}
    for pi, c in enumerate(inst.conns):               # y, J (mevcut snapped boşluk)
        g = cur[c["dep_eid"]] - cur[c["arr_eid"]]
        yv[pi] = 1 if (L <= g <= U) else 0
        Jc[pi] = c["legsum"] + g
        sv(m.y[pi], yv[pi])
    for k, g in inst.md.items():                      # z (monoton doldurma)
        i, M = md_id[k], len(g["conns"])
        n = sum(yv[pi] for pi in g["conns"])
        for j in range(1, M + 1):
            sv(m.z[i, j], 1 if j <= n else 0)
    for k, g in inst.md.items():                      # w, β, γ
        i = md_id[k]
        beaten = {}
        for ca, Tc in g["comps"].items():
            bt = 0
            for pi in g["conns"]:
                if yv[pi] != 1:
                    continue
                if (pi, ca) in m._beat_eq_y:
                    bt = 1
                elif (pi, ca) in m._w:
                    beats = (cur[inst.conns[pi]["dep_eid"]] - cur[inst.conns[pi]["arr_eid"]]) \
                        <= (Tc - inst.conns[pi]["legsum"])
                    sv(m._w[(pi, ca)], 1 if beats else 0)
                    bt = bt or int(beats)
            if (i, ca) in m._beta:
                sv(m._beta[(i, ca)], bt)
            beaten[ca] = bt
        if CFG["ranking"] and g["N"] >= 1 and g["b_od"] is not None:
            nb = sum(beaten.values())
            for bn in range(0, g["N"] + 1):
                sv(m.w[("gam", i, bn)], 1 if bn == nb else 0)
    if CFG["E2_balance"]:                             # act, u, Jmin
        for k, g in inst.md.items():
            i, cs = md_id[k], g["conns"]
            offered = [pi for pi in cs if yv[pi] == 1]
            sv(m.act[i], 1 if offered else 0)
            amin = min(offered, key=lambda pi: Jc[pi]) if offered else None
            for pi in cs:
                sv(m.u[pi], 1 if pi == amin else 0)
            sv(m.Jmin[i], min((Jc[pi] for pi in offered), default=g["_Jlo"]))


# =========================================================================== baseline & rapor
def current_baseline(inst):
    """Mevcut tarifenin (optimizasyon yok) amaç değeri — dürüst karşılaştırma için."""
    rkW = rank_weight_table(inst.rank)
    total = 0.0
    for k, g in inst.md.items():
        offered = [pi for pi in g["conns"]
                   if inst.L <= inst.conns[pi]["gap_cur"] <= inst.U]
        n = len(offered)
        conn_rew = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten = 0
        if CFG["ranking"] and offered and g["comps"]:
            j_best = min(inst.conns[pi]["legsum"] + inst.conns[pi]["gap_cur"] for pi in offered)
            beaten = sum(1 for tc in g["comps"].values() if j_best <= tc)
        rank_rew = rank_reward(rkW, g["N"], g["b_od"], beaten) if CFG["ranking"] else 0.0
        total += g["rho"] * (conn_rew + rank_rew)
    return total


def report(inst, m, detail=12):
    """Pazar-gün kırılımı. Çok pazar varsa yalnız en yüksek katkılı `detail` tanesi
    ayrıntılı yazılır; toplam her zaman tüm pazarlar üzerinden hesaplanır."""
    rkW = rank_weight_table(inst.rank)
    md_id = m._md_id
    rows = []                                            # (val, k, g, n, beaten, gaps)
    total = 0.0
    for k, g in inst.md.items():
        i = md_id[k]
        offered = [pi for pi in g["conns"] if pyo.value(m.y[pi]) > 0.5]
        n = len(offered)
        conn_rew = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        gaps = [(pi, pyo.value(m._gap[pi]),
                 inst.conns[pi]["legsum"] + pyo.value(m._gap[pi])) for pi in offered]
        beaten = sum(1 for ca in g["comps"]
                     if (i, ca) in m._beta and pyo.value(m._beta[(i, ca)]) > 0.5)
        rank_rew = rank_reward(rkW, g["N"], g["b_od"], beaten) if CFG["ranking"] else 0.0
        val = g["rho"] * (conn_rew + rank_rew)
        total += val
        rows.append((val, k, g, n, beaten, conn_rew, rank_rew, gaps))

    rows.sort(key=lambda r: -r[0])
    print("\n" + "=" * 78)
    print(f"SONUÇ — pazar/gün kırılımı (en yüksek katkılı {min(detail, len(rows))}/{len(rows)})")
    print("=" * 78)
    for val, k, g, n, beaten, conn_rew, rank_rew, gaps in rows[:detail]:
        print(f"\n{k[0]} (gün {k[1]})  ρ={g['rho']:.0f}  N_rakip={g['N']}  b_od={g['b_od']}")
        print(f"   sunulan bağlantı: {n}/{len(g['conns'])}  | yenilen rakip: {beaten}/{g['N']}")
        for pi, gv, j in gaps[:6]:
            c = inst.conns[pi]
            print(f"     π#{pi}: boşluk {c['gap_cur']:.0f}→{gv:.0f} dk  J={j:.0f} dk"
                  f"  (legsum={c['legsum']:.0f})")
        if len(gaps) > 6:
            print(f"     … (+{len(gaps) - 6} bağlantı daha)")
        print(f"   ödül: aktarma={conn_rew:.3f}  sıralama={rank_rew:+.3f}"
              f"  → ρ·toplam={val:.1f}")
    sh = shift_value(m)
    print("\n" + "-" * 78)
    print(f"SAF rekabetçilik (raporlanan)     : {total:.2f}")
    print(f"Toplam kaydırma                   : {sh:.0f} uçuş-dk  (λ={CFG['shift_penalty']})")
    print(f"Pyomo amaç (rekabet − λ·kaydırma) : {pyo.value(m.OBJ):.2f}")
    print(f"Mevcut tarife (baseline)          : {current_baseline(inst):.2f}")
    print("-" * 78)
    return total


# =========================================================================== main
def main():
    if len(sys.argv) > 1 and sys.argv[1] in PRESETS:
        CFG.update(PRESETS[sys.argv[1]])
        if CFG["days"] is None:                          # gün listesini veriden türet (hardcode YOK)
            CFG["days"] = all_operation_days()
        print(f">> profil: {sys.argv[1]}  (gün {CFG['days']}, "
              f"süre sınırı {CFG['time_limit']}s, gap {CFG['mip_gap']})")
    print(">> örnek kuruluyor …")
    inst = build_instance()
    n_adj = sum(1 for e in inst.ev_by_id.values() if e["adjustable"])
    print(f"   pazar-gün: {len(inst.md)} | bağlantı(π): {len(inst.conns)} | "
          f"olay: {len(inst.events)} (ayarlanabilir {n_adj}) | "
          f"pencere ±{CFG['wdev_min']}dk / Δ{CFG['delta_min']}dk")

    print(">> model kuruluyor …")
    m = build_model(inst)
    on = [n for n, f in [("A1", True), ("A2", CFG["A2_rotation"]), ("B1", True),
                         ("B2", CFG["B2_force_offer"]), ("C", True), ("D", CFG["ranking"]),
                         ("E1", CFG["E1_balance"]), ("E2", CFG["E2_balance"]),
                         ("F", CFG["F_capacity"]), ("G", CFG["G_regularity"])] if f]
    nbin = sum(1 for v in m.component_data_objects(pyo.Var) if v.is_binary())
    print(f"   aktif kısıtlar: {'+'.join(on)}  | A2 bağ:{m._n_a2} (brief-exact {m._n_a2_exact}, "
          f"evren-ankoru {getattr(m, '_n_a2_anchor', 0)}) "
          f"G bağ:{m._n_g}(atlanan {m._n_g_skip}) F bağ:{m._n_f} | ikili değişken: {nbin}")

    if CFG["warmstart"]:
        set_warmstart(inst, m)
        print(f"   warm start: mevcut tarife (obj={pyo.value(m.OBJ):.1f})")

    print(f">> çözülüyor ({CFG['solver']}) …")
    res = solve_model(m)
    print(f"   durum: {res['tc']}" + (f"  | MIP boşluğu: {res['gap']:.3%}"
          if res.get("gap") is not None else "") + f"  | süre: {res['t']:.1f}s")
    if not res["ok"]:
        print("   [!] Uygun çözüm yüklenemedi (infeasible / zaman aşımı).")
        return
    report(inst, m)


def solve_model(m):
    """appsi Highs ile çöz; zaman/gap sınırları + dürüst durum raporu."""
    import time
    from pyomo.contrib.appsi.solvers import Highs
    opt = Highs()
    opts = {"threads": 1, "random_seed": 0}    # determinizm (makineler arası tekrar-üretim)
    opts.update(CFG.get("highs_extra_options") or {})      # ops. ek HiGHS ayarları (08 kullanır)
    opt.highs_options = opts
    if CFG["time_limit"] is not None:
        opt.config.time_limit = CFG["time_limit"]
    if CFG["mip_gap"] is not None:
        opt.config.mip_gap = CFG["mip_gap"]
    opt.config.load_solution = False
    if CFG["warmstart"] and opt.warm_start_capable():
        opt.config.warmstart = True
    t0 = time.time()
    res = opt.solve(m)
    dt_ = time.time() - t0
    tc = res.termination_condition
    from pyomo.contrib.appsi.base import TerminationCondition as TC
    ok = tc in (TC.optimal, TC.maxTimeLimit, TC.maxIterations) and \
        res.best_feasible_objective is not None
    gap = None
    try:
        bf, bp = res.best_feasible_objective, res.best_objective_bound
        if bf not in (None, 0) and bp is not None:
            gap = abs(bp - bf) / max(1e-9, abs(bf))
    except Exception:
        pass
    if ok:
        res.solution_loader.load_vars()
    return {"ok": ok, "tc": tc, "gap": gap, "t": dt_}


def shift_value(m):
    """Çözümdeki toplam tarife kaydırması (uçuş-dk). Ceza kapalıyken (ifade float 0)."""
    e = getattr(m, "_shift_expr", 0.0)
    return 0.0 if isinstance(e, (int, float)) else float(pyo.value(e))


def solution_total(inst, m):
    """Çözümün ρ-ağırlıklı SAF rekabetçilik toplamı (cezasız, raporlamadan)."""
    rkW = rank_weight_table(inst.rank)
    md_id = m._md_id
    total = 0.0
    for k, g in inst.md.items():
        i = md_id[k]
        n = sum(1 for pi in g["conns"] if pyo.value(m.y[pi]) > 0.5)
        conn = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten = sum(1 for ca in g["comps"]
                     if (i, ca) in m._beta and pyo.value(m._beta[(i, ca)]) > 0.5)
        rr = rank_reward(rkW, g["N"], g["b_od"], beaten) if CFG["ranking"] else 0.0
        total += g["rho"] * (conn + rr)
    return total


# Varsayılan tarife-değişim cezası. λ-taraması (docs §12) λ∈[0.1,1.5] aralığında düz bir plato
# gösterdi (rekabetçilik ~+%4.2–4.3, kaydırma ~%22–26); λ=0.3 platonun knee'si (cezasız λ=0
# dejenerasyon uçurumunun hemen üstü: en yüksek kazanım + düşük kaydırma).
DEFAULT_LAMBDA = 0.3


def compute_overnight_guards(days):
    """(A2×) gece-aşan rotasyon koruması: STATİK slack-bölüşümü sınırları.
    Mevcut tarifede fiziksel turu gün h→h+1'e yayılan (aynı-gün dönüşü olmayan,
    gün h+1 dönüşü brief minimumunu T_OB+τ+T_IB SAĞLAYAN) çiftlerde mevcut pay:
      slack = (dönüş_varış − kalkış) − minimum_tur ≥ 0.
    Pay ikiye bölünür: kalkış en çok slack/2 GEÇ, dönüş en çok slack/2 ERKEN
    kayabilir → θ_in − θ_out ≥ minimum tur YAPISAL olarak garanti (ihlal imkânsız),
    gün-bağlaşımı ve G-bandı çatışması hiç doğmaz (sınırlar statik/deterministik).
    Mevcutta bile sağlanmayan çiftler eşleşme-yorumu artefaktıdır (o gün tek uçak
    dönmüyor) → sınır konmaz (çözüm-sonrası raporda 'taban' olarak görünür).
    Döner: (rotcap_by_day, rotfloor_by_day) — gün -> {(flno,gün): tavan/taban (dt)}."""
    _, _, tk_g, _, _, fixed_g, rot_g, blocks_g = load_data()
    rp_g = rotation_pairs(rot_g)
    cur_arr_g = {(int(r.FlNo1), int(r.day)): r.ist_arr for r in tk_g.itertuples()}
    cur_dep_g = {(int(r.FlNo2), int(r.day)): r.ist_dep for r in tk_g.itertuples()}
    tau_g = CFG["tau_min"]
    rotcap_by_day, rotfloor_by_day = {}, {}              # (flno,gün) -> tavan/taban (dt)
    if blocks_g and CFG["A2_overnight_guard"]:
        for of, inf in rp_g:
            for d in days:
                dep_c = cur_dep_g.get((of, d))
                if dep_c is None:
                    continue
                a_same = cur_arr_g.get((inf, d))
                if a_same is not None and a_same > dep_c:
                    continue                             # aynı-gün dönüş → model-içi A2 kapsar
                a_next = cur_arr_g.get((inf, d + 1))
                t_ob = blocks_g.get((of, d, "dep"))
                t_ib = blocks_g.get((inf, d + 1, "arr"))
                if a_next is None or a_next <= dep_c or t_ob is None or t_ib is None:
                    continue
                exact = t_ob + tau_g + t_ib
                slack = (a_next - dep_c).total_seconds() / 60.0 - exact
                if slack < 0:
                    continue                             # mevcut bile sağlamıyor → artefakt
                if slack >= 2 * CFG["wdev_min"]:
                    continue                             # pencere ihlale yetişemez → sınır gereksiz
                cap_dt = dep_c + pd.Timedelta(minutes=slack / 2)     # kalkış geç-kayma tavanı
                flr_dt = a_next - pd.Timedelta(minutes=slack / 2)    # dönüş erken-kayma tabanı
                caps = rotcap_by_day.setdefault(d, {})
                kc = (of, d)
                caps[kc] = min(caps.get(kc, cap_dt), cap_dt)
                floors = rotfloor_by_day.setdefault(d + 1, {})
                kf = (inf, d + 1)
                floors[kf] = max(floors.get(kf, flr_dt), flr_dt)
    return rotcap_by_day, rotfloor_by_day


def run_byday(lam=0.0, gap=0.02, time_limit=150, write=True, verbose=True):
    """TÜM veriyi GÜNE GÖRE ayrıştırarak çöz (çekirdek). Günleri bağlayan tek kısıt G;
    her gün ayrı (küçük, hızlı) çözülür, G önceki günlerden gelen saat-içi bantla
    zincirlenir. Monolitik 7-gün MIP (102k ikili) HiGHS'te incumbent bulamadığından gerekli.
    lam>0 ise amaca λ·(toplam kaydırma) cezası girer; istatistik sözlüğü döner."""
    CFG.update(PRESETS["full"])
    CFG["shift_penalty"] = lam
    CFG["time_limit"], CFG["mip_gap"] = time_limit, gap
    if CFG["days"] is None:                               # gün listesini veriden türet (hardcode YOK)
        CFG["days"] = all_operation_days()
    days = CFG["days"]
    if verbose:
        print(f">> GÜNE-GÖRE ayrıştırma  (λ={lam} obj/uçuş-dk, gap≤{gap:.2%}, "
              f"gün-başına ≤{time_limit}s, günler {days})")
    band = {}                                            # (flno,role) -> yerleşmiş saat-içi
    g_opt = g_base = 0.0
    g_shift = 0
    ok_days = relaxed_days = 0
    n_band_dropped = 0                                   # hedefli G-gevşetmede bırakılan bant
    band_exempt_rows = []                                # (gün, uçuş, rol): bandı bırakılan olaylar
    sched_rows, day_stats = [], []                       # çıktı tarifesi + özet
    market_rows, conn_rows = [], []                      # O–D/gün + seçilen-bağlantı (teslim #3)
    final_dt = {}                                        # (flno,gün,rol) -> optimize GERÇEK zaman
    cur_dt = {}                                          # (flno,gün,rol) -> MEVCUT gerçek zaman
    blocks_ref = rot_pairs_ref = None                    # A2 gece-aşan doğrulaması için

    # (A2×) gece-aşan rotasyon koruması — statik sınırlar (bkz. compute_overnight_guards)
    rotcap_by_day, rotfloor_by_day = compute_overnight_guards(days)
    hhmm = lambda t: f"{(t % 1440) // 60:02d}:{(t % 1440) % 60:02d}"
    for d in days:
        CFG["days"] = [d]
        try:
            inst = build_instance()
            inst.gband = band
            inst.rotcap = rotcap_by_day.get(d, {})
            inst.rotlock = rotfloor_by_day.get(d, {})
            m = build_model(inst)
            res = solve_model(m)
            relaxed = False
            if not res["ok"]:                            # bant kuplajı aşırı-kısıtladı →
                # 1. aşama (HEDEFLİ): yalnız rotasyon-korumalı uçuşların bandını bırak
                guarded = {f for (f, _d) in list(inst.rotcap) + list(inst.rotlock)}
                if guarded and inst.gband:
                    dropped = [k for k in band if k[0] in guarded]
                    inst.gband = {k: v for k, v in band.items() if k[0] not in guarded}
                    m = build_model(inst)
                    res = solve_model(m)
                    n_band_dropped += len(dropped)
                    if res["ok"]:                        # muafiyet fiilen kullanıldı → belgele
                        for (fl, ro) in dropped:         # (rotasyon güvenliği > G bandı önceliği)
                            band_exempt_rows.append(dict(
                                gun=d, ucus_no=fl,
                                rol=("kalkış" if ro == "dep" else "varış")))
                if not res["ok"]:                        # 2. aşama: o gün G'yi tam gevşet
                    inst.gband = {}
                    m = build_model(inst)
                    res = solve_model(m)
                    relaxed = True
        except Exception as ex:                          # gizli veride tek gün hatası TÜM koşuyu çökertmesin
            if verbose:
                print(f"   gün {d}: ATLANDI (hata: {type(ex).__name__}: {ex})")
            continue
        if not res["ok"]:
            if verbose:
                print(f"   gün {d}: ÇÖZÜLEMEDİ ({res['tc']}, {res['t']:.0f}s)")
            continue
        relaxed_days += int(relaxed)
        opt = solution_total(inst, m)
        base = current_baseline(inst)
        g_opt += opt
        g_base += base
        ok_days += 1
        # tüm olayların optimize IST zamanı (sabitler yerinde durur)
        new_time = {e["id"]: (round(sum(v * pyo.value(m.x[e["id"], v]) for v in e["cands"]))
                              if e["adjustable"] else e["cur"]) for e in inst.ev_by_id.values()}
        for e in inst.ev_by_id.values():                 # gece-aşan A2 doğrulaması için gerçek zaman
            final_dt[(e["flno"], d, e["role"])] = inst.t0 + pd.Timedelta(minutes=new_time[e["id"]])
            cur_dt[(e["flno"], d, e["role"])] = inst.t0 + pd.Timedelta(minutes=e["cur"])
        if blocks_ref is None:
            blocks_ref, rot_pairs_ref = inst.blocks, inst.rot_pairs
        n_moved = 0
        day_shift = 0
        for e in inst.ev_by_id.values():                 # bantları kaydet + tarife satırı
            if not e["adjustable"]:
                continue
            new_abs = new_time[e["id"]]
            band.setdefault((e["flno"], e["role"]), new_abs - (e["cur"] // 1440) * 1440)
            delta = new_abs - e["cur"]
            n_moved += int(delta != 0)
            day_shift += abs(delta)
            sched_rows.append(dict(
                gun=d, ucus_no=e["flno"],
                rol=("kalkış" if e["role"] == "dep" else "varış"),
                eski_IST=hhmm(e["cur"]), yeni_IST=hhmm(new_abs),
                degisim_dk=delta, G_gevsetildi=int(relaxed)))
        g_shift += day_shift
        if write:                                        # teslim #3: O–D/gün + seçilen bağlantı
            collect_market_outputs(inst, m, d, new_time, hhmm, market_rows, conn_rows)
        gp = f"{res['gap']:.2%}" if res.get("gap") is not None else "?"
        tag = " [G-gevşetildi]" if relaxed else ""
        day_stats.append(dict(gun=d, pazar_gun=len(inst.md), baglanti=len(inst.conns),
                              OPT=round(opt), baseline=round(base), delta=round(opt - base),
                              gap=gp, ucus_kaydirilan=n_moved, kaydirma_dk=day_shift,
                              G_gevsetildi=int(relaxed)))
        if verbose:
            print(f"   gün {d}: md={len(inst.md):3d} bağ={len(inst.conns):4d} | "
                  f"OPT={opt:>9.0f} baz={base:>9.0f} Δ={opt - base:>+8.0f} | gap={gp:>6} "
                  f"kaydırılan={n_moved} ({day_shift:,}dk) ({res['t']:.0f}s){tag}")
    dpct = 100 * (g_opt - g_base) / g_base if g_base else 0
    moved = sum(1 for r in sched_rows if r["degisim_dk"] != 0)
    nfl = len(sched_rows)
    # --- A2 fiziksel rotasyon doğrulaması (gece-aşan turlar dahil) ----------
    # Model-içi A2 aynı-gün kurulur (byday gün-bağlaşımı yaratamaz); burada her IST
    # kalkışının MEVCUT tarifedeki dönüş örneği (aynı-gün veya ertesi gün — uçağın
    # gerçek eşleşmesi) sabitlenir ve optimize saatlerde brief minimumuna
    # (T_OB+τ+T_IB) uyduğu GERÇEK zaman ekseninde doğrulanır. Mevcut tarifenin
    # kendisinin sağlamadığı eşleşmeler artefakttır (o gün o çift tek uçakla
    # dönülmüyordur) → 'taban' olarak ayrıca raporlanır, ihlal sayılmaz.
    a2x_chk = a2x_viol = a2x_base = 0
    if blocks_ref is not None and rot_pairs_ref:
        tau = CFG["tau_min"]
        for out_f, in_f in rot_pairs_ref:
            for d in days:
                t_ob = blocks_ref.get((out_f, d, "dep"))
                dep_c = cur_dt.get((out_f, d, "dep"))
                dep_o = final_dt.get((out_f, d, "dep"))
                if dep_c is None or dep_o is None or t_ob is None:
                    continue
                # dönüş örneğini MEVCUT tarife belirler (ilk cur-varış > cur-kalkış)
                pick = None
                for d2 in (d, d + 1):
                    a_c = cur_dt.get((in_f, d2, "arr"))
                    tb = blocks_ref.get((in_f, d2, "arr"))
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
                if a_c < dep_c + need:                   # mevcut bile sağlamıyor → artefakt
                    a2x_base += 1
                elif a_o < dep_o + need:                 # optimizasyonun YENİ yarattığı ihlal
                    a2x_viol += 1
    stats = dict(lam=lam, opt=g_opt, base=g_base, dpct=dpct, shift=g_shift,
                 moved=moved, nflights=nfl, movedpct=100 * moved / max(1, nfl),
                 ok_days=ok_days, n_days=len(days), relaxed_days=relaxed_days,
                 a2x_chk=a2x_chk, a2x_viol=a2x_viol, a2x_base=a2x_base,
                 band_exempt=len(band_exempt_rows))
    if verbose:
        print("=" * 70)
        print(f"TAM VERİ ({ok_days}/{len(days)} gün, G-gevşetilen {relaxed_days}) — "
              f"GÜNE-GÖRE AYRIŞTIRMA  (λ={lam})")
        print(f"  OPTIMIZE toplam : {g_opt:>12,.0f}")
        print(f"  BASELINE toplam : {g_base:>12,.0f}")
        print(f"  İYİLEŞME (Δ)    : {g_opt - g_base:>+12,.0f}   ({dpct:+.2f}%)")
        print(f"  Tarife kaydırma : {moved:>5}/{nfl} uçuş hareketi (%{stats['movedpct']:.0f}), "
              f"toplam {g_shift:,} uçuş-dk")
        if a2x_chk:
            print(f"  A2 rotasyon doğrulaması (gece-aşan dahil, gerçek zaman ekseni): "
                  f"{a2x_chk} tur kontrol, YENİ ihlal: {a2x_viol} "
                  f"(mevcut tarifede de aynı yorumda görünen: {a2x_base} — eşleşme artefaktı)")
        if band_exempt_rows:
            print(f"  G hedefli bant-muafiyeti (rotasyon güvenliği önceliği): "
                  f"{len(band_exempt_rows)} (gün,uçuş,rol) — output/g_band_exemptions.csv")
        print("=" * 70)
    if write:
        write_outputs(sched_rows, day_stats, stats, market_rows, conn_rows, band_exempt_rows)
    return stats


def collect_market_outputs(inst, m, day, new_time, hhmm, market_rows, conn_rows):
    """O–D/gün özeti (yenilen rakip, sıralama, ödüller) ve seçilen her bağlantı satırını
    biriktirir (teslim #3: 'seçilen bağlantılar' + 'O–D bazında yenilen rakipler')."""
    rkW = rank_weight_table(inst.rank)
    md_id = m._md_id
    for k, g in inst.md.items():
        i = md_id[k]
        offered = [pi for pi in g["conns"] if pyo.value(m.y[pi]) > 0.5]
        n = len(offered)
        conn_rew = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten_cas = [ca for ca in g["comps"]
                      if (i, ca) in m._beta and pyo.value(m._beta[(i, ca)]) > 0.5]
        beaten = len(beaten_cas)
        rank_rew = rank_reward(rkW, g["N"], g["b_od"], beaten) if CFG["ranking"] else 0.0
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
                IST_varis=hhmm(new_time[c["arr_eid"]]), IST_kalkis=hhmm(new_time[c["dep_eid"]]),
                bosluk_dk=round(gv), J_dk=round(J), yendigi_rakip=len(beats)))


def main_byday(lam=None):
    """Varsayılan (DEFAULT_LAMBDA) cezayla tam veri koşusu + çıktı yazımı.
    gap=0.1%: kalibre edildi — 0.5% raporlanan (saf) amaçta ~0.5 puan bırakıyor;
    0.01% ise cezalı amacı sıkarken saf rekabetçiliği DÜŞÜRÜyor (ceza-ödün etkisi)."""
    lam = DEFAULT_LAMBDA if lam is None else lam
    run_byday(lam=lam, gap=(0.001 if lam > 0 else 0.02), time_limit=150, write=True)


def main_sweep(lams=None, gap=0.001, time_limit=150):
    """λ-TARAMASI: rekabetçilik-kazanımı ⟷ tarife-değişimi ödünleşim (Pareto) tablosu.
    Cezasız (λ=0) referansa göre korunan kazanım yüzdesini ve %kaydırılan'ı verir."""
    lams = lams if lams is not None else [0.0, 0.1, 0.3, 0.7, 1.5]
    print(f">> λ-TARAMASI  (gap≤{gap:.2%}, ≤{time_limit}s/gün)  — ödünleşim: "
          f"rekabetçilik vs tarife-değişimi\n")
    rows = []
    for lam in lams:
        s = run_byday(lam=lam, gap=gap, time_limit=time_limit, write=False, verbose=False)
        rows.append(s)
        print(f"   λ={lam:<5}: Δ={s['opt'] - s['base']:>+9,.0f} ({s['dpct']:+.2f}%)  | "
              f"kaydırılan %{s['movedpct']:>3.0f} ({s['moved']}/{s['nflights']})  | "
              f"{s['shift']:>8,} uçuş-dk  [G-gevş {s['relaxed_days']}]")
    base_gain = (rows[0]["opt"] - rows[0]["base"]) if rows else 0.0
    print("\n" + "=" * 72)
    print(f"{'λ':>6} | {'Δ rekabet':>12} | {'korunan':>8} | {'kaydırılan':>11} | {'uçuş-dk':>10}")
    print("-" * 72)
    for s in rows:
        gain = s["opt"] - s["base"]
        keep = 100 * gain / base_gain if base_gain else 0.0
        print(f"{s['lam']:>6} | {gain:>+12,.0f} | {keep:>6.0f}%  | {s['movedpct']:>9.0f}%  | "
              f"{s['shift']:>10,}")
    print("=" * 72)
    print("Not: 'korunan' = λ=0 kazanımının yüzdesi. Knee = yüksek korunan + düşük kaydırma.")
    return rows


def write_outputs(sched_rows, day_stats, stats, market_rows=None, conn_rows=None,
                  band_exempt_rows=None):
    """Teslim #3 çıktıları: tarife (optimized_schedule.csv), O–D/gün sonuçları
    (market_results.csv), seçilen bağlantılar (selected_connections.csv) + özet (.md)."""
    out = os.path.join(ROOT, "output")
    os.makedirs(out, exist_ok=True)
    sched = pd.DataFrame(sched_rows).sort_values(["gun", "ucus_no", "rol"])
    sched.to_csv(os.path.join(out, "optimized_schedule.csv"), index=False, encoding="utf-8-sig")
    if market_rows:                                      # O–D/gün: yenilen rakip + ödüller
        pd.DataFrame(market_rows).sort_values(["gun", "rho_katki"], ascending=[True, False]) \
          .to_csv(os.path.join(out, "market_results.csv"), index=False, encoding="utf-8-sig")
    if conn_rows:                                        # seçilen (sunulan) her bağlantı
        pd.DataFrame(conn_rows).sort_values(["gun", "pazar"]) \
          .to_csv(os.path.join(out, "selected_connections.csv"), index=False, encoding="utf-8-sig")
    # G hedefli bant-muafiyetleri (şeffaflık: doğrulayıcı bu listeyi okur; boşsa da yazılır)
    pd.DataFrame(band_exempt_rows or [], columns=["gun", "ucus_no", "rol"]) \
      .to_csv(os.path.join(out, "g_band_exemptions.csv"), index=False, encoding="utf-8-sig")
    g_opt, g_base, dpct = stats["opt"], stats["base"], stats["dpct"]
    moved, nfl, lam = stats["moved"], stats["nflights"], stats["lam"]
    avg_shift = stats["shift"] / max(1, moved)
    pen_line = (f"- **Tarife-değişim cezası (λ):** {lam} amaç-puanı / uçuş-dk "
                f"({'açık' if lam > 0 else 'KAPALI — referans'})")
    L = ["# THY Tarife Optimizasyonu — Sonuç Özeti", "",
         "**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu", "",
         f"*Üretim: {dt.datetime.now():%Y-%m-%d %H:%M} · `python src/03_model.py byday`*", "",
         "## Tam veri sonucu (güne göre ayrıştırma)", "",
         f"- **Çözülen gün:** {stats['ok_days']}/{stats['n_days']}  "
         f"(G-gevşetilen {stats['relaxed_days']})",
         pen_line,
         f"- **Ayarlanabilir uçuş hareketi:** {nfl} (kaydırılan {moved}, "
         f"%{stats['movedpct']:.0f}; toplam {stats['shift']:,} uçuş-dk, ort. {avg_shift:.0f} dk)",
         f"- **OPTIMIZE amaç (saf rekabetçilik):** {g_opt:,.0f}",
         f"- **BASELINE (mevcut tarife):** {g_base:,.0f}",
         f"- **İYİLEŞME:** {g_opt-g_base:+,.0f}  (**{dpct:+.2f}%** gelir-ağırlıklı rekabetçilik faydası)",
         "", "## Gün kırılımı", "",
         "| Gün | Pazar-gün | Aday bağlantı | OPT | Baseline | Δ | gap | Kaydırılan | Kaydırma-dk | G-gevş. |",
         "|----|----|----|----|----|----|----|----|----|----|"]
    for s in day_stats:
        L.append(f"| {s['gun']} | {s['pazar_gun']} | {s['baglanti']} | {s['OPT']:,} | "
                 f"{s['baseline']:,} | {s['delta']:+,} | {s['gap']} | {s['ucus_kaydirilan']} | "
                 f"{s.get('kaydirma_dk', 0):,} | {'evet' if s['G_gevsetildi'] else '—'} |")
    L += ["", "## Notlar (bkz. `docs/model_formulation.md` §10–§12)", "",
          f"- **Tarife-değişim cezası (P, docs §12):** amaca −λ·Σ|θ−cur| eklenir (tam doğrusal: "
          f"A1 sayesinde Σ_v|v−cur|·x). λ={lam}. Amaç değişimi cezalandırmadığında çözücü "
          "uçuşları keyfî kaydırıyordu (bedava/dejenere kaydırma); λ bunları geri çeker.",
          "- 'OPTIMIZE amaç' ve 'İYİLEŞME' SAF rekabetçiliktir (cezasız ölçülür); λ yalnızca "
          "hangi kaydırmaların yapılacağını süzer.",
          "- Kısıtlar: A1,A2,B1,C,D,E1,F,G gün-içinde tam uygulanır; G günler-arası saat-içi",
          "  bantla zincirlenir (çatışan günde gevşetilir)."
          + (f" Rotasyon-güvenliği önceliğiyle bandı bırakılan (gün,uçuş,rol): "
             f"{stats.get('band_exempt', 0)} — `output/g_band_exemptions.csv`."
             if stats.get("band_exempt") else ""),
          "- A2 rotasyonu brief-exact minimum turla (T_OB+τ+T_IB, bacak blokları veriden) kurulur;"
          " gece-aşan turlar statik slack-bölüşümüyle korunur"
          + (f" — doğrulama: {stats.get('a2x_chk', 0)} tur, YENİ ihlal {stats.get('a2x_viol', 0)}"
             f" (mevcut tarifede de görünen {stats.get('a2x_base', 0)} eşleşme-artefaktı hariç)."
             if stats.get("a2x_chk") else "."),
          "- E2 (Jmin zaman dengesi) tam-ölçekte kapalı (büyük-M min-seçimi HiGHS'i kilitliyor);",
          "  küçük örnekte açık ve doğrulanmış.",
          "- F kova kapasitesi brief'in gerçek 10/15'ini uygular (sabit uçuşlar baz cap'i hiç",
          "  aşmadığından rezidüel cap ≥0; ayarlanabilirler pencerede yayılarak sığar).",
          "  Modellenmeyen (ρ'suz → amaç dışı) pazarların uçuşları da kovalarda SABİT doluluk",
          "  olarak sayılır (fiziksel kapasite tüm TK uçuşlarıyla korunur).",
          "- `eski_IST`/`yeni_IST` 10 dk ızgaraya yuvarlanmış saat-içi değerlerdir.",
          "", "## Çıktı dosyaları (teslim #3)", "",
          "- `optimized_schedule.csv` — ayarlanan IST saatleri (uçuş × eski→yeni).",
          "- `market_results.csv` — O–D/gün: sunulan bağlantı, **yenilen rakip**, sıralama, ρ-katkı.",
          "- `selected_connections.csv` — seçilen her bağlantı (gelen/giden uçuş, boşluk, J, yendiği rakip).",
          "- Toplam amaç değeri (saf rekabetçilik): "
          f"**{g_opt:,.0f}** (baseline {g_base:,.0f}, Δ {g_opt-g_base:+,.0f})."]
    with open(os.path.join(out, "results_summary.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(L) + "\n")
    extra = ""
    if market_rows:
        extra = (f", output/market_results.csv ({len(market_rows)} O–D/gün), "
                 f"output/selected_connections.csv ({len(conn_rows)} bağlantı)")
    print(f">> çıktı yazıldı: output/optimized_schedule.csv ({len(sched)} satır){extra}, "
          f"output/results_summary.md")


if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else ""
    if arg == "byday":                                   # tam veri + çıktı; ops. λ: byday 0.3
        main_byday(float(sys.argv[2]) if len(sys.argv) > 2 else None)
    elif arg == "sweep":                                 # λ ödünleşim taraması (Pareto tablo)
        main_sweep()
    else:
        main()
