"""
TEKNOFEST Havayolu Optimizasyonu — Veri Hazırlama (2. adım)

POLİTİKA: "Minimal + belgeli"
  * Orijinal Excel dosyalarına ASLA dokunulmaz (sadece okunur).
  * Hiçbir değer uydurulmaz.
  * J (Gate-to-Gate) yalnızca FİZİKSEL OLARAK İMKÂNSIZ satırlarda (J < boşluk) +24sa düzeltilir.
  * Belirsiz durumlarda nötr/ihtiyatlı varsayım + açık işaret.
  * Her dönüşüm derived/transform_log.md içine yazılır; ham haliyle de izlenebilir.

Çalıştırma:  python src/02_data_prep.py   (proje kökünden)
Girdi:       data/      (yarışmanın orijinal dosyalarının kopyası — değiştirilmez)
Çıktı:       derived/   (yeni dosyalar)
"""

import os
import datetime as dt
import warnings

import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# proje kökü = bu dosyanın bulunduğu src/ klasörünün üstü
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
DERIVED = os.path.join(ROOT, "derived")
os.makedirs(DERIVED, exist_ok=True)

def _find_conn_file():
    """Bağlantı tablosunu bul: güncellenmiş sürüm (ElapsedTime'lı) öncelikli."""
    candidates = ["O&D Rakip Bağlantı Tablosu_updated.xlsx",
                  "O&D Rakip Bağlantı Tablosu.xlsx"]
    for name in candidates:
        p = os.path.join(DATA, name)
        if os.path.exists(p):
            return p
    import glob as _glob
    hits = sorted(_glob.glob(os.path.join(DATA, "O&D*.xlsx")))
    if hits:
        return hits[0]
    raise FileNotFoundError(f"data/ altında O&D bağlantı tablosu bulunamadı: {candidates}")

F_CONN = _find_conn_file()
F_PAX = os.path.join(DATA, "Yolcu Verisi_masked.xlsx")
F_RANK = os.path.join(DATA, "change_ranking_input.xlsx")
F_PAIR = os.path.join(DATA, "Flight Pairs.xlsx")

# ----------------------------- yapılandırma (hepsi belgeli, değiştirilebilir)
CFG = {
    "L_min": 60, "U_min": 300,        # bağlantı penceresi
    "tau_min": 45,                    # minimum yer süresi
    "dewrap": "minimal",              # "minimal" (yalnız J<boşluk) | "off"
    "n_od_def": "carrier",            # "carrier" (veri 17<=40) | "itinerary"
    "missing_rho": "exclude",         # eksik gelir ağırlığı olan pazarı dışla
}

LOG = []
def log(*a):
    line = " ".join(str(x) for x in a)
    print(line); LOG.append(line)

def tmin(v):
    """time-of-day -> dakika (saat:dk:sn)."""
    if isinstance(v, dt.time):
        return v.hour * 60 + v.minute + v.second / 60.0
    return np.nan


def dur_min(v):
    """Süre -> dakika. Excel'in süreyi temsil edebileceği tüm biçimleri kabul eder:
    time-of-day, 1899-12-30 epoch'lu datetime (24sa+ süreler gün kısmında taşınır),
    'dd.mm.yyyy HH:MM:SS' / 'HH:MM[:SS]' metni, timedelta, gün-kesri sayısı."""
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return np.nan
    if isinstance(v, dt.datetime):
        return (v - dt.datetime(1899, 12, 30)).total_seconds() / 60.0
    if isinstance(v, dt.time):
        return v.hour * 60 + v.minute + v.second / 60.0
    if isinstance(v, (pd.Timedelta, dt.timedelta)):
        return v.total_seconds() / 60.0
    if isinstance(v, (int, float)):
        return float(v) * 1440.0  # Excel serisi: 1.0 = 1 gün
    if isinstance(v, str):
        s = v.strip()
        if not s:
            return np.nan
        if "." in s.split(" ")[0] and " " in s:  # '30.12.1899 06:19:00'
            d = dt.datetime.strptime(s, "%d.%m.%Y %H:%M:%S")
            return (d - dt.datetime(1899, 12, 30)).total_seconds() / 60.0
        parts = s.split(":")
        if len(parts) in (2, 3) and all(p.strip().isdigit() for p in parts):
            h, m = int(parts[0]), int(parts[1])
            sec = int(parts[2]) if len(parts) == 3 else 0
            return h * 60 + m + sec / 60.0
    return np.nan


def main():
    log("# TEKNOFEST Veri Hazırlama — dönüşüm logu")
    log("Üretim:", dt.datetime.now().strftime("%Y-%m-%d %H:%M"), "| Politika: minimal+belgeli")
    log("Yapılandırma:", CFG)

    conn = pd.read_excel(F_CONN, sheet_name=0)
    pax = pd.read_excel(F_PAX, sheet_name=0)
    rank = pd.read_excel(F_RANK, sheet_name=0)
    pair = pd.read_excel(F_PAIR, sheet_name=0)
    log(f"\nOkundu (salt-okunur): bağlantı={conn.shape} [{os.path.basename(F_CONN)}], "
        f"yolcu={pax.shape}, ranking={rank.shape}, pair={pair.shape}")

    # === şema doğrulaması (gizli veride sütun farklıysa kriptik KeyError yerine net hata) ===
    def need(df, cols, name):
        miss = [c for c in cols if c not in df.columns]
        if miss:
            raise ValueError(f"[ŞEMA] '{name}' beklenen sütun(lar) eksik: {miss}\n"
                             f"        mevcut sütunlar: {list(df.columns)}")
    need(conn, ["Dep1", "Arr2", "Cr1", "Dep Time", "Arr Time", "Gate-to-Gate Uçuş Süresi",
                "O&D", "Gün", "FlNo1", "FlNo2", "Carrier Name"], "O&D Rakip Bağlantı Tablosu")
    need(pax, ["Orig Airport Code", "Dest Airport Code", "OD importance factor"], "Yolcu Verisi")
    need(pair, ["FlNo", "Pair", "Orig", "Dest"], "Flight Pairs")

    # === ortak türetmeler (uydurma yok; tarih/saatten kesin hesap) ============
    conn = conn.copy()
    conn["o"] = conn["Dep1"].astype(str)
    conn["d"] = conn["Arr2"].astype(str)
    conn["is_tk"] = conn["Cr1"].eq("TK")
    conn["gap_min"] = (conn["Dep Time"] - conn["Arr Time"]).dt.total_seconds() / 60.0
    conn["J_wrap_min"] = conn["Gate-to-Gate Uçuş Süresi"].map(dur_min)

    # === J hesabı ============================================================
    # Güncellenmiş veri (ElapsedTime1/2 sütunlu): J = E1 + boşluk + E2 KESİN olarak
    # hesaplanır — Gate-to-Gate'in 24 saatte sarma (wrap) belirsizliği tamamen kalkar.
    # Eski şema (ElapsedTime yok): J yalnız Gate-to-Gate'ten gelir; fiziksel imkânsız
    # (J < boşluk) satırlara minimal +24sa de-wrap uygulanır.
    has_elapsed = {"ElapsedTime1", "ElapsedTime2"}.issubset(conn.columns)
    if has_elapsed:
        conn["E1_min"] = conn["ElapsedTime1"].map(dur_min)
        conn["E2_min"] = conn["ElapsedTime2"].map(dur_min)
        n_bad = int(conn["E1_min"].isna().sum()) + int(conn["E2_min"].isna().sum())
        if n_bad:
            raise ValueError(f"[ŞEMA] ElapsedTime1/2 çözümlenemeyen hücre: {n_bad} "
                             f"(örnek: {conn.loc[conn['E1_min'].isna(), 'ElapsedTime1'].head(3).tolist()})")
        conn["legsum_min"] = conn["E1_min"] + conn["E2_min"]
        conn["J_min"] = conn["legsum_min"] + conn["gap_min"]
        conn["dewrap_k"] = np.round((conn["J_min"] - conn["J_wrap_min"]) / 1440.0).astype(int)

        # doğrulama: kesin J, sarılı Gate-to-Gate ile mod-24sa tutarlı olmalı
        mod_off = ((conn["J_min"] - conn["J_wrap_min"]) % 1440.0)
        inconsistent = ~(np.isclose(mod_off, 0, atol=1.01) | np.isclose(mod_off, 1440, atol=1.01))
        log(f"\n[J KESİN] ElapsedTime1/2 mevcut -> J = E1 + boşluk + E2 (wrap belirsizliği YOK)")
        log(f"  Gate-to-Gate ile mod-24sa tutarsız satır: {int(inconsistent.sum())} (0 beklenir)")
        log(f"  24 saati aşan gerçek yolculuk: {int((conn['J_min'] >= 1440).sum())} satır"
            f" (eski şemada bunlar sarılı görünüyordu)")
        # eski minimal de-wrap sezgiseli neyi kaçırırdı? (belgeleme amaçlı)
        imposs = conn["J_wrap_min"] < conn["gap_min"]
        k_old = np.where(imposs, np.maximum(np.ceil((conn["gap_min"] - conn["J_wrap_min"]) / 1440.0), 1), 0)
        j_old = conn["J_wrap_min"] + 1440 * k_old
        missed = ~np.isclose(j_old, conn["J_min"], atol=1.01)
        log(f"  Eski minimal de-wrap'in yanlış hesaplayacağı satır: {int(missed.sum())}"
            f" (TK: {int((conn['is_tk'] & missed).sum())}, rakip: {int((~conn['is_tk'] & missed).sum())})")
    else:
        # === J de-wrap (YALNIZ fiziksel imkânsız: J_wrap < boşluk) — eski şema ===
        impossible = conn["J_wrap_min"] < conn["gap_min"]
        if CFG["dewrap"] == "minimal":
            k = np.ceil((conn["gap_min"] - conn["J_wrap_min"]) / 1440.0)
            k = np.where(impossible, np.maximum(k, 1), 0).astype(int)
        else:
            k = np.zeros(len(conn), dtype=int)
        conn["dewrap_k"] = k
        conn["J_min"] = conn["J_wrap_min"] + 1440 * conn["dewrap_k"]
        conn["legsum_min"] = conn["J_min"] - conn["gap_min"]

        n_fixed = int((conn["dewrap_k"] > 0).sum())
        log(f"\n[J de-wrap] ElapsedTime sütunları YOK (eski şema) -> minimal sezgisel.")
        log(f"  Fiziksel imkânsız (J<boşluk) satır: {int(impossible.sum())}  -> +24sa uygulanan: {n_fixed}")
        log(f"  TK düzeltilen: {int((conn['is_tk'] & (conn['dewrap_k']>0)).sum())}"
            f" | Rakip düzeltilen: {int((~conn['is_tk'] & (conn['dewrap_k']>0)).sum())}")
        suspicious = (~impossible) & (conn["J_wrap_min"] >= 1380)
        log(f"  [AÇIK İŞARET] 23s+ görünen ve gizli wrap riski taşıyan (DOKUNULMADI): {int(suspicious.sum())}"
            f"  -> teknik raporda belirtilecek.")

    # === TK bağlantı adayları =================================================
    tk = conn[conn["is_tk"]].copy()
    tk_out = tk[["o", "d", "O&D", "Gün", "FlNo1", "Arr Time", "FlNo2", "Dep Time",
                 "gap_min", "legsum_min", "J_min", "J_wrap_min", "dewrap_k"]].rename(
        columns={"O&D": "market", "Gün": "day", "Arr Time": "ist_arr", "Dep Time": "ist_dep"})

    # === hafta normalizasyonu =================================================
    # Veride AYNI operasyon günü (Gün=d) farklı pazarlarda FARKLI takvim haftalarına
    # yazılabiliyor (ör. gün 1 kimi satırda 4 Ağu, kiminde 11 Ağu Pazartesi). Aynı uçuş
    # no'nun aynı gündeki hafta-kopyaları modelde AYRI karar olaylarına dönüşür ve
    # tutarsız kaydırma alabilir (aynı fiziksel uçuşa iki farklı saat). Düzeltme:
    # satırın İKİ zaman damgası BİRLİKTE 7k gün geri çekilir (kalkış tarihi o günün
    # kanonik = en erken tarihine oturur) — boşluk ve J değişmez, kopyalar birleşir.
    # Gizli veri güvencesi: 7'nin katı olmayan fark görülürse satır DOKUNULMADAN bırakılır.
    ev_key = lambda df: set(zip(df["FlNo1"], df["day"], df["ist_arr"])) \
                      | set(zip(df["FlNo2"], df["day"], df["ist_dep"]))
    n_ev_before = len(ev_key(tk_out))
    dep_date = tk_out["ist_dep"].dt.normalize()
    canon = dep_date.groupby(tk_out["day"]).transform("min")
    k_days = (dep_date - canon).dt.days
    weekly = (k_days % 7 == 0)
    shift_d = np.where(weekly, k_days, 0)
    tk_out["ist_arr"] = tk_out["ist_arr"] - pd.to_timedelta(shift_d, unit="D")
    tk_out["ist_dep"] = tk_out["ist_dep"] - pd.to_timedelta(shift_d, unit="D")
    n_ev_after = len(ev_key(tk_out))
    log(f"\n[Hafta normalizasyonu] geri çekilen satır: {int((shift_d > 0).sum())} "
        f"(7'nin katı olmayan, dokunulmayan: {int((~weekly).sum())})")
    log(f"  Tekil (uçuş,gün,zaman) olay: {n_ev_before} -> {n_ev_after} "
        f"(birleşen hafta-kopyası: {n_ev_before - n_ev_after}; boşluk/J değişmedi)")

    # === aday tekilleştirme ===================================================
    # Hafta-kopyaları birleşince AYNI fiziksel bağlantı (pazar, gün, uçuş çifti, saatler)
    # birebir özdeş iki satır olarak kalabiliyor. İki kopyayı iki ayrı aday saymak, aynı
    # ürüne çift aktarma ödülü yazdırır (hem baseline hem optimize tarafını şişirir).
    # Yalnız TÜM alanları özdeş satırlar atılır; saatleri gerçekten farklı olan (veri
    # anomalisi) satırlar korunur — model onları ayrı olaylar olarak ele alır.
    n0 = len(tk_out)
    tk_out = tk_out.drop_duplicates(
        ["market", "day", "FlNo1", "FlNo2", "ist_arr", "ist_dep"]).reset_index(drop=True)
    log(f"  Birebir özdeş aday satırı tekilleştirildi: {n0 - len(tk_out)} "
        f"({n0} -> {len(tk_out)} aday)")

    tk_out["gap_in_window"] = tk_out["gap_min"].between(CFG["L_min"], CFG["U_min"])
    log(f"\n[TK bağlantı] {len(tk_out)} aday | pencere içi: {int(tk_out['gap_in_window'].sum())}"
        f" ({100*tk_out['gap_in_window'].mean():.1f}%)")

    # === TK bacak blok süreleri (A2 rotasyonu için; yalnız güncel şemada) =====
    # Brief §4.1: dönüş IST varışı, gidiş IST kalkışından en az (T_OB + τ + T_IB)
    # sonra olmalı. ElapsedTime'lı veri T_IB (FlNo1: o→IST) ve T_OB (FlNo2: IST→d)
    # süresini uçuş-örneği düzeyinde verir. Aynı (FlNo,gün) için birden çok değer
    # görülürse İHTİYATLI olan (en büyük blok) alınır — tur asla brief minimumunun
    # altına sıkıştırılamaz.
    blocks = None
    if has_elapsed:
        ib = (tk.groupby(["FlNo1", "Gün"], as_index=False)["E1_min"].max()
                .rename(columns={"FlNo1": "flno", "Gün": "day", "E1_min": "block_min"}))
        ib["role"] = "arr"
        obt = (tk.groupby(["FlNo2", "Gün"], as_index=False)["E2_min"].max()
                 .rename(columns={"FlNo2": "flno", "Gün": "day", "E2_min": "block_min"}))
        obt["role"] = "dep"
        n_multi = int((tk.groupby(["FlNo1", "Gün"])["E1_min"].nunique() > 1).sum()) \
                + int((tk.groupby(["FlNo2", "Gün"])["E2_min"].nunique() > 1).sum())
        blocks = pd.concat([ib, obt], ignore_index=True)[["flno", "day", "role", "block_min"]]
        log(f"\n[Blok süreleri] TK bacak blokları (A2 için): {len(blocks)} (FlNo,gün,rol) kaydı"
            f" | çok-değerli grup (max alındı): {n_multi}")

    # === Rakip itineraryleri + (carrier bazlı) T_comp =========================
    comp = conn[~conn["is_tk"]].copy()
    comp_cols = ["o", "d", "O&D", "Gün", "Cr1", "Carrier Name", "J_min", "dewrap_k"]
    if "ML2" in comp.columns:   # güncel veri: M=Mainline, L=Low-cost (bilgi amaçlı taşınır;
        comp_cols.append("ML2")  # brief'in sıralama tanımı taşıyıcı tipi ayrımı yapmaz)
        log(f"\n[ML2] Taşıyıcı tipi sütunu mevcut: {comp['ML2'].value_counts().to_dict()}"
            f" (M=Mainline, L=Low-cost; ranking'e etkisiz, bilgi amaçlı taşındı)")
    comp_it = comp[comp_cols].rename(
        columns={"O&D": "market", "Gün": "day", "Cr1": "carrier"})
    tcomp_carrier = (comp_it.groupby(["market", "day", "carrier"], as_index=False)["J_min"]
                     .min().rename(columns={"J_min": "T_comp_min"}))
    if CFG["n_od_def"] == "carrier":
        n_od = tcomp_carrier.groupby(["market", "day"], as_index=False)["carrier"].nunique() \
                            .rename(columns={"carrier": "N_od"})
    else:
        n_od = comp_it.groupby(["market", "day"], as_index=False).size().rename(columns={"size": "N_od"})
    log(f"\n[Rakip] {len(comp_it)} itinerary | taşıyıcı-bazlı T_comp satırı: {len(tcomp_carrier)}")
    log(f"  N_od ({CFG['n_od_def']}) aralığı: {int(n_od['N_od'].min())}–{int(n_od['N_od'].max())}"
        f" | ranking lookup max N=40 -> kapsam {'TAM' if n_od['N_od'].max()<=40 else 'EKSİK'}")

    # === Pazar tablosu: ρ (gelir ağırlığı) + N_od ============================
    pax = pax.copy()
    pax["market"] = pax["Orig Airport Code"].astype(str) + "-" + pax["Dest Airport Code"].astype(str)
    pax = pax.drop_duplicates("market")
    rho = pax.set_index("market")["OD importance factor"]

    markets = pd.DataFrame({"market": sorted(conn["O&D"].unique())})
    markets["o"] = markets["market"].str.split("-").str[0]
    markets["d"] = markets["market"].str.split("-").str[1]
    markets["rho"] = markets["market"].map(rho)
    markets["has_tk"] = markets["market"].isin(set(tk_out["market"]))
    markets["has_comp"] = markets["market"].isin(set(comp_it["market"]))
    n_missing_rho = int(markets["rho"].isna().sum())
    markets["excluded_no_rho"] = markets["rho"].isna() if CFG["missing_rho"] == "exclude" else False
    log(f"\n[Pazar] {len(markets)} yönlü pazar | ρ eksik: {n_missing_rho}"
        f" -> politika='{CFG['missing_rho']}' (dışlanan: {int(markets['excluded_no_rho'].sum())})")
    log(f"  TK olan: {int(markets['has_tk'].sum())} | sadece-rakip: {int((~markets['has_tk']).sum())}")

    # === Rotasyon (Flight Pairs) — eksik partner = ayarlanamaz işareti =========
    pair = pair.copy()
    tk_flnos = set(tk["FlNo1"]).union(set(tk["FlNo2"]))
    pair_flnos = set(pair["FlNo"])
    no_partner = sorted(tk_flnos - pair_flnos)
    rot = pair[pair["FlNo"].isin(tk_flnos)].copy()
    log(f"\n[Rotasyon] TK uçuş no: {len(tk_flnos)} | Flight Pairs'te eşi olan: {len(tk_flnos & pair_flnos)}")
    log(f"  Partnersiz TK uçuş no: {len(no_partner)} -> politika: 'ayarlanamaz/sabit' kabul (kısıt eklenmez)")

    # === yaz (derived/) =======================================================
    tk_out.to_csv(os.path.join(DERIVED, "tk_connections.csv"), index=False, encoding="utf-8-sig")
    comp_it.to_csv(os.path.join(DERIVED, "competitor_itineraries.csv"), index=False, encoding="utf-8-sig")
    tcomp_carrier.to_csv(os.path.join(DERIVED, "competitor_times_carrier.csv"), index=False, encoding="utf-8-sig")
    n_od.to_csv(os.path.join(DERIVED, "market_n_od.csv"), index=False, encoding="utf-8-sig")
    markets.to_csv(os.path.join(DERIVED, "markets.csv"), index=False, encoding="utf-8-sig")
    rank.to_csv(os.path.join(DERIVED, "ranking_lookup.csv"), index=False, encoding="utf-8-sig")
    rot.to_csv(os.path.join(DERIVED, "flight_rotation.csv"), index=False, encoding="utf-8-sig")
    if blocks is not None:
        blocks.to_csv(os.path.join(DERIVED, "flight_block_times.csv"), index=False, encoding="utf-8-sig")
    pd.DataFrame({"flno_no_rotation_partner": no_partner}).to_csv(
        os.path.join(DERIVED, "tk_flights_without_partner.csv"), index=False, encoding="utf-8-sig")

    with open(os.path.join(DERIVED, "transform_log.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(LOG) + "\n")

    log("\n[OK] derived/ altına yazıldı:")
    for fn in sorted(os.listdir(DERIVED)):
        p = os.path.join(DERIVED, fn)
        log(f"   {fn:38s} {os.path.getsize(p)//1024:>5d} KB")
    log("\nKAYNAK DOSYALAR DEĞİŞMEDİ. Tüm dönüşümler bu logda.")


if __name__ == "__main__":
    main()
