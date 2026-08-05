"""
TEKNOFEST Havayolu Optimizasyonu — Veri Sağlık Kontrolü (1. adım)

4 girdi Excel dosyasını okur, tutarlı bir veri katmanına bağlar ve
modellemeden önce bilmemiz gereken her şeyi bir 'sağlık raporu' olarak çıkarır.

Çalıştırma:  python src/01_data_health_check.py   (proje kökünden)
Girdi:       data/   (yarışmanın orijinal dosyalarının kopyası — değiştirilmez)
Çıktı:       reports/data_health_report.md
"""

import os
import datetime as dt
import warnings

import pandas as pd

warnings.filterwarnings("ignore")
pd.set_option("display.width", 200)
pd.set_option("display.max_columns", 60)

# proje kökü = bu dosyanın bulunduğu src/ klasörünün üstü
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
REPORT_DIR = os.path.join(ROOT, "reports")
os.makedirs(REPORT_DIR, exist_ok=True)

def _find_conn_file():
    """Bağlantı tablosunu bul: güncellenmiş sürüm (ElapsedTime'lı) öncelikli."""
    for name in ["O&D Rakip Bağlantı Tablosu_updated.xlsx",
                 "O&D Rakip Bağlantı Tablosu.xlsx"]:
        p = os.path.join(DATA, name)
        if os.path.exists(p):
            return p
    import glob as _glob
    hits = sorted(_glob.glob(os.path.join(DATA, "O&D*.xlsx")))
    if hits:
        return hits[0]
    raise FileNotFoundError("data/ altında O&D bağlantı tablosu bulunamadı")

F_CONN = _find_conn_file()
F_PAX = os.path.join(DATA, "Yolcu Verisi_masked.xlsx")
F_RANK = os.path.join(DATA, "change_ranking_input.xlsx")
F_PAIR = os.path.join(DATA, "Flight Pairs.xlsx")

L_MIN, U_MIN = 60, 300  # bağlantı penceresi (dk)

_buf = []
def out(*args):
    line = " ".join(str(a) for a in args)
    print(line)
    _buf.append(line)

def h1(t): out("\n" + "=" * 90); out(t); out("=" * 90)
def h2(t): out("\n" + "-" * 70); out(t); out("-" * 70)


def time_to_min(v):
    """time-of-day veya timedelta -> dakika."""
    if pd.isna(v):
        return None
    if isinstance(v, dt.time):
        return v.hour * 60 + v.minute + v.second / 60.0
    if isinstance(v, (pd.Timedelta, dt.timedelta)):
        return v.total_seconds() / 60.0
    return None


def main():
    h1("TEKNOFEST VERİ SAĞLIK RAPORU")
    out("Üretim tarihi:", dt.datetime.now().strftime("%Y-%m-%d %H:%M"))

    conn = pd.read_excel(F_CONN, sheet_name=0)
    pax = pd.read_excel(F_PAX, sheet_name=0)
    rank = pd.read_excel(F_RANK, sheet_name=0)
    pair = pd.read_excel(F_PAIR, sheet_name=0)

    # =================================================================
    h1(f"1) BAĞLANTI TABLOSU  ({os.path.basename(F_CONN)})")
    out("Boyut:", conn.shape)
    out("Kolonlar:", list(conn.columns))
    has_elapsed = {"ElapsedTime1", "ElapsedTime2"}.issubset(conn.columns)
    out("ElapsedTime1/2 (bacak süreleri) mevcut:", "EVET -> J kesin hesaplanabilir"
        if has_elapsed else "HAYIR -> Gate-to-Gate wrap riski (de-wrap sezgiseli gerekir)")
    if "ML2" in conn.columns:
        out("ML2 (taşıyıcı tipi, M=Mainline/L=Low-cost) dağılımı:",
            conn["ML2"].value_counts(dropna=False).to_dict())

    out("\nArr Time aralığı:", conn["Arr Time"].min(), "->", conn["Arr Time"].max())
    out("Dep Time aralığı:", conn["Dep Time"].min(), "->", conn["Dep Time"].max())
    out("Gün değerleri:", sorted(conn["Gün"].dropna().unique().tolist()))

    h2("Taşıyıcı dağılımı (Cr1)")
    vc = conn["Cr1"].value_counts()
    out("Toplam taşıyıcı:", vc.shape[0])
    out(vc.head(15).to_string())
    is_tk = conn["Cr1"] == "TK"
    out("\nTK satır:", int(is_tk.sum()), " | Rakip satır:", int((~is_tk).sum()))

    tk = conn[is_tk].copy()
    out("\nTK Arr1 (gelen bacağın varışı) benzersiz:", tk["Arr1"].unique().tolist()[:5])
    out("TK Dep2 (giden bacağın kalkışı) benzersiz:", tk["Dep2"].unique().tolist()[:5])

    conn["_od_from_cols"] = conn["Dep1"].astype(str) + "-" + conn["Arr2"].astype(str)
    mism = (conn["_od_from_cols"] != conn["O&D"]).sum()
    out("\nO&D kolonu, (Dep1-Arr2) ile uyuşmayan satır sayısı:", int(mism))

    out("\nBenzersiz O&D pazarı (yönlü):", conn["O&D"].nunique())
    out("Benzersiz (O&D, Gün) anahtarı:", conn.groupby(['O&D', 'Gün']).ngroups)

    tk_markets = set(tk["O&D"].unique())
    all_markets = set(conn["O&D"].unique())
    comp_markets = set(conn[~is_tk]["O&D"].unique())
    out("\nTK bağlantısı OLAN pazar sayısı:", len(tk_markets))
    out("TK bağlantısı OLMAYAN (sadece rakip) pazar sayısı:", len(all_markets - tk_markets))
    out("Rakip bağlantısı OLMAYAN (sadece TK) pazar sayısı:", len(all_markets - comp_markets))

    # =================================================================
    h1("2) TK BAĞLANTI GEÇERLİLİĞİ  (mevcut tarifede)")
    tk["gap_min"] = (tk["Dep Time"] - tk["Arr Time"]).dt.total_seconds() / 60.0
    tk["j_min"] = tk["Gate-to-Gate Uçuş Süresi"].map(time_to_min)
    tk["legsum_min"] = tk["j_min"] - tk["gap_min"]

    out("Bağlantı boşluğu (dk): min/medyan/max =",
        round(tk["gap_min"].min(), 1), "/",
        round(tk["gap_min"].median(), 1), "/",
        round(tk["gap_min"].max(), 1))
    in_window = tk["gap_min"].between(L_MIN, U_MIN)
    out(f"[{L_MIN},{U_MIN}] penceresinde olan TK bağlantısı:",
        int(in_window.sum()), f"/ {len(tk)}  ({100*in_window.mean():.1f}%)")
    out("Negatif boşluk (veri hatası?) sayısı:", int((tk["gap_min"] < 0).sum()))
    out("Boşluk < L (kısa) :", int((tk["gap_min"] < L_MIN).sum()),
        " | Boşluk > U (uzun):", int((tk["gap_min"] > U_MIN).sum()))

    out("\nGate-to-Gate (J) dakika: min/medyan/max =",
        round(tk["j_min"].min(), 1), "/",
        round(tk["j_min"].median(), 1), "/",
        round(tk["j_min"].max(), 1))
    out("J >= 24h (time formatında temsil edilemez!) sayısı:",
        int((tk["j_min"] >= 24 * 60 - 1).sum()),
        "  -> uzun itineraryler 'time' alanında kırpılmış olabilir, KONTROL ET")

    h2("Bacak blok süresi ayrıştırma fizibilitesi")
    g = tk.groupby(["FlNo1", "Gün"])["Arr Time"].nunique()
    out("Aynı (FlNo1,Gün) için farklı 'Arr Time' sayısı >1 olan grup:", int((g > 1).sum()),
        " (0 olmalı: bir gelen uçuşun tek IST varışı var)")
    g2 = tk.groupby(["FlNo2", "Gün"])["Dep Time"].nunique()
    out("Aynı (FlNo2,Gün) için farklı 'Dep Time' sayısı >1 olan grup:", int((g2 > 1).sum()),
        " (0 olmalı: bir giden uçuşun tek IST kalkışı var)")
    out("Benzersiz gelen TK uçuş örneği (FlNo1,Gün):", tk.groupby(["FlNo1", "Gün"]).ngroups)
    out("Benzersiz giden TK uçuş örneği (FlNo2,Gün):", tk.groupby(["FlNo2", "Gün"]).ngroups)

    # =================================================================
    h1("3) RAKİP SÜRELERİ ve RAKİP SAYISI (N_od)")
    comp = conn[~is_tk].copy()
    comp["j_min"] = comp["Gate-to-Gate Uçuş Süresi"].map(time_to_min)
    by_market = comp.groupby(["O&D", "Gün"])
    n_itin = by_market.size()
    n_carr = by_market["Cr1"].nunique()
    out("Rakip itinerary sayısı / (O&D,Gün): min/medyan/max =",
        int(n_itin.min()), "/", int(n_itin.median()), "/", int(n_itin.max()))
    out("Farklı rakip taşıyıcı / (O&D,Gün): min/medyan/max =",
        int(n_carr.min()), "/", int(n_carr.median()), "/", int(n_carr.max()))
    out("Rakip J (dk): min/medyan/max =",
        round(comp["j_min"].min(), 1), "/", round(comp["j_min"].median(), 1), "/", round(comp["j_min"].max(), 1))
    out("\nNOT: N_od (rakip sayısı) tanımı netleştirilmeli — farklı itinerary mi, farklı taşıyıcı mı?")
    out("Ranking lookup 'Rakip Sayısı' aralığı:", int(rank['Rakip Sayısı'].min()), "-", int(rank['Rakip Sayısı'].max()))
    out("Itinerary-bazlı rakip sayısı 40'ı aşan (O&D,Gün) sayısı:", int((n_itin > 40).sum()),
        " | taşıyıcı-bazlı 40'ı aşan:", int((n_carr > 40).sum()))

    # =================================================================
    h1("4) YOLCU VERİSİ / GELİR AĞIRLIĞI (ρ_od)")
    out("Boyut:", pax.shape, " | Kolonlar:", list(pax.columns))
    out("ρ (önem) aralığı:", int(pax["OD importance factor"].min()), "-", int(pax["OD importance factor"].max()))
    pax["_od"] = pax["Orig Airport Code"].astype(str) + "-" + pax["Dest Airport Code"].astype(str)
    dup = pax["_od"].duplicated().sum()
    out("Tekrarlı O-D satırı:", int(dup), " | Benzersiz O-D:", pax["_od"].nunique())
    pax_set = set(pax["_od"])
    missing_rho = [m for m in all_markets if m not in pax_set]
    out("Bağlantı tablosundaki pazar sayısı:", len(all_markets))
    out("ρ değeri OLMAYAN pazar sayısı:", len(missing_rho))
    if missing_rho:
        out("  Örnek eksikler:", missing_rho[:10])

    # =================================================================
    h1("5) RANKING ÖDÜL TABLOSU (change_ranking_input.xlsx)")
    out("Boyut:", rank.shape, " | Kolonlar:", list(rank.columns))
    out("Weight aralığı:", round(rank["Weight"].min(), 4), "-", round(rank["Weight"].max(), 4))
    cov = rank.groupby("Rakip Sayısı").size()
    out("\nN -> satır sayısı (ilk birkaç):")
    for n in sorted(rank["Rakip Sayısı"].unique())[:6]:
        out(f"  N={n}: {int(cov[n])} satır (beklenen N*N={n*n})")
    bad = (rank["Son Rank"] > rank["İlk Rank"]).sum()
    out("Son Rank > İlk Rank olan satır (sıralama kötüleşmesi):", int(bad))
    bad2 = (rank["İlk Rank"] > rank["Rakip Sayısı"]).sum()
    out("İlk Rank > Rakip Sayısı olan (tutarsız) satır:", int(bad2))

    # =================================================================
    h1("6) FLIGHT PAIRS / ROTASYON (Flight Pairs.xlsx)")
    out("Boyut:", pair.shape, " | Kolonlar:", list(pair.columns))
    out("Benzersiz Pair:", pair["Pair"].nunique(), " | Benzersiz FlNo:", pair["FlNo"].nunique())
    psize = pair.groupby("Pair").size()
    out("Pair başına uçuş sayısı dağılımı:", psize.value_counts().to_dict())
    out("IST'ten kalkan (Orig=IST) uçuş:", int((pair["Orig"] == "IST").sum()),
        " | IST'e gelen (Dest=IST):", int((pair["Dest"] == "IST").sum()))
    tk_flnos = set(tk["FlNo1"]).union(set(tk["FlNo2"]))
    pair_flnos = set(pair["FlNo"])
    out("\nBağlantı tablosundaki benzersiz TK uçuş no:", len(tk_flnos))
    out("Flight Pairs'teki uçuş no:", len(pair_flnos))
    out("TK uçuş no'su olup Flight Pairs'te OLMAYAN:", len(tk_flnos - pair_flnos))
    out("Flight Pairs'te olup bağlantı tablosunda kullanılmayan uçuş no:", len(pair_flnos - tk_flnos))

    # =================================================================
    h1("7) ÖZET / AÇIK SORULAR (modellemeden önce karara bağlanmalı)")
    out("- N_od tanımı: rakip = farklı itinerary mi, farklı taşıyıcı mı? (ranking ödülünü doğrudan etkiler)")
    out("- Gate-to-Gate 'time' formatı 24h'i aşan itineraryleri kırpıyor olabilir — uzun pazarları doğrula.")
    out("- T_IB / T_OB bacak blok sürelerini connection'dan ayrıştırma stratejisi (J - boşluk = sabit).")
    out("- Ayar pencereleri (Standard: sınır yok) — gün-içi düzenlilik (X_dev=15dk) ve hub kovaları (10dk) ile etkileşim.")
    out("- ρ eksik pazarlar için varsayım (0 mı, ortalama mı, ele mi?).")
    out("- Constraint H (slot pencereleri) sadece sunumda — dahil edilecek mi netleştir.")

    report_path = os.path.join(REPORT_DIR, "data_health_report.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("# TEKNOFEST Veri Sağlık Raporu\n\n```\n")
        f.write("\n".join(_buf))
        f.write("\n```\n")
    out("\n[OK] Rapor yazıldı:", report_path)


if __name__ == "__main__":
    main()
