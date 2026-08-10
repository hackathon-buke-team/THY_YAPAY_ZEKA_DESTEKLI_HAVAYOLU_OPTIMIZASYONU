# -*- coding: utf-8 -*-
"""
ÖN-DENETİM 08 — Kapalı/kısmi kısıtların SAYISAL kanıtı  (E2, B2, G)

Jüri sorularının üçü şu an iddia düzeyinde savunuluyor:
  · "E2'yi neden kurmadınız?"      -> farkın ne kadarı FİZİK, ne kadarı SEÇİM?
  · "B2'yi de mi kapattınız?"      -> nihai çözümde zorunlu-sunum fiilen ne kadar sağlanıyor?
  · "G'de %42,8 muafiyet fazla."   -> muafiyetlerin kaçı FİİLEN kullanıldı?

Bu betik üçünü de sıfırdan, `src/` kodundan hiçbir şey import etmeden ölçer;
yalnız `derived/` (veri katmanı) + `output/` (çözüm) dosyalarını okur.

Çalıştırma:  python preaudit/08_kapali_kisit_kanitlari.py     (proje kökünden)
Üretir:      output/audit_e2_ayristirma.csv
             output/audit_b2_sunulmayan.csv
             output/audit_g_muafiyet_kullanimi.csv
"""

import os
import sys

import numpy as np
import pandas as pd

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DER = os.path.join(ROOT, "derived")
OUT = os.path.join(ROOT, "output")

# Brief §2.2 / §2.4 parametreleri (yarisma-belgeleri/TEKNOFEST_Yarismasi Brief.pdf)
L, U = 60, 300      # bağlantı boşluğu alt/üst sınırı  [Brief §2.2, s.4]
GAMMA = 30          # E2 en iyi yolculuk süresi fark eşiği [Brief §2.4 + §4.5, s.4/6]
XDEV = 15           # G gün-arası maks. sapma [Brief §2.4 + §4.7, s.4/6]


def hdr(t):
    print("\n" + "=" * 78 + f"\n{t}\n" + "=" * 78)


def tod(s):
    """'HH:MM' -> gün-içi dakika."""
    h, m = str(s).split(":")
    return int(h) * 60 + int(m)


def circ(a, b):
    """İki gün-içi dakika arasındaki dairesel (gece sarmasına dayanıklı) fark."""
    d = abs(a - b) % 1440
    return min(d, 1440 - d)


def rev(mkt):
    o, d = mkt.split("-")
    return f"{d}-{o}"


# ----------------------------------------------------------------- veriyi oku
conn = pd.read_csv(os.path.join(DER, "tk_connections.csv"),
                   parse_dates=["ist_arr", "ist_dep"])
mkts = pd.read_csv(os.path.join(DER, "markets.csv"))
sel = pd.read_csv(os.path.join(OUT, "selected_connections.csv"))
sch = pd.read_csv(os.path.join(OUT, "optimized_schedule.csv"))
exm = pd.read_csv(os.path.join(OUT, "g_band_exemptions.csv"))
mres = pd.read_csv(os.path.join(OUT, "market_results.csv"))

rho = dict(zip(mkts.market, mkts.rho))
universe = set(zip(mres.gun, mres.pazar))          # modelin amaç evreni (pazar-gün)

print(f"okundu: aday bağlantı {len(conn)} · sunulan {len(sel)} · tarife satırı {len(sch)} "
      f"· G muafiyeti {len(exm)} · amaç evreni {len(universe)} pazar-gün")

# roller ('kalkış' / 'varış') — kodlamadan bağımsız tanı
roles = list(sch.rol.unique())
R_DEP = next(r for r in roles if str(r).lower().startswith("k"))
R_ARR = next(r for r in roles if str(r).lower().startswith("v"))


# =============================================================================
# ÖLÇÜM 1 — E2: GÖZLENEN fark ve blok-süresi / boşluk ayrıştırması
# =============================================================================
hdr("ÖLÇÜM 1 — E2 GÖZLENEN FARK:  |Jmin_od − Jmin_do| nereden geliyor?")

sel = sel.copy()
sel["legsum"] = sel.J_dk - sel.bosluk_dk
best = sel.loc[sel.groupby(["gun", "pazar"]).J_dk.idxmin()][
    ["gun", "pazar", "J_dk", "bosluk_dk", "legsum"]
].rename(columns={"J_dk": "Jmin", "bosluk_dk": "gap_at_min", "legsum": "legsum_at_min"})

bm = {(r.gun, r.pazar): r for r in best.itertuples()}

rows = []
for (g, mkt), a in bm.items():
    rm = rev(mkt)
    if mkt > rm:                        # her yön-çiftini bir kez say
        continue
    b = bm.get((g, rm))
    if b is None:                       # ters yön PASİF -> E2 zaten bağlayıcı değil (Brief §4.5)
        continue
    rows.append(dict(
        gun=g, yon_A=mkt, yon_B=rm,
        Jmin_A=a.Jmin, Jmin_B=b.Jmin,
        fark=abs(a.Jmin - b.Jmin),
        d_legsum=abs(a.legsum_at_min - b.legsum_at_min),
        d_gap=abs(a.gap_at_min - b.gap_at_min),
        rho=max(rho.get(mkt, 0) or 0, rho.get(rm, 0) or 0),
    ))
e2 = pd.DataFrame(rows)

n_pair = len(e2)
viol = e2[e2.fark > GAMMA]
print(f"her iki yönü AKTİF yön-çifti (E2 bağlayıcı olurdu): {n_pair}")
print(f"|Jmin_A − Jmin_B| > Γ={GAMMA} dk olan  : {len(viol)}  (%{100*len(viol)/max(n_pair,1):.1f})")
print(f"  fark dağılımı (dk): medyan {viol.fark.median():.0f} · ort {viol.fark.mean():.0f} "
      f"· p90 {viol.fark.quantile(.9):.0f} · maks {viol.fark.max():.0f}")

# Boşluk ∈ [60,300] olduğundan |Δboşluk| ≤ U−L = 240 dk ile SINIRLIDIR.
# Farkın 240 dk'yı aşan kısmı TANIM GEREĞİ blok süresinden gelir.
sadece_blok = viol[viol.d_legsum > GAMMA]
print(f"\n  · yalnız BLOK SÜRESİ farkı bile Γ'yı aşan çift : {len(sadece_blok)} "
      f"(%{100*len(sadece_blok)/max(len(viol),1):.1f} of ihlaller)")
print(f"  · |Δblok| medyan {viol.d_legsum.median():.0f} dk · maks {viol.d_legsum.max():.0f} dk")
print(f"  · |Δboşluk| medyan {viol.d_gap.median():.0f} dk · maks {viol.d_gap.max():.0f} dk "
      f"(yapısal tavan {U-L} dk)")


# =============================================================================
# ÖLÇÜM 2 — E2: YAPISAL alt sınır.  Hangi çift HİÇBİR tarifeyle sağlanamaz?
# =============================================================================
hdr("ÖLÇÜM 2 — E2 YAPISAL SINIR:  fizik mi, bizim seçimimiz mi?")
print(f"""
Yöntem (gevşetme -> bulunan 'imkânsız' KANITLIDIR):
  Bir yönün en iyi yolculuk süresi Jmin, aday bağlantılar üzerinden
      Jmin = min_π (legsum_π + boşluk_π),   boşluk_π ∈ [{L},{U}]   [Brief §2.2]
  olduğundan ERİŞİLEBİLİR aralık en geniş hâliyle
      R = [ min legsum + {L} ,  min legsum + {U} ]   (genişlik {U-L} dk)
  İki yönün aralıkları Γ={GAMMA} dk yakınlığa getirilemiyorsa E2 hiçbir tarifeyle sağlanamaz:
      |Δ min legsum| > {U-L} + {GAMMA} = {U-L+GAMMA} dk   ->  YAPISAL OLARAK İMKÂNSIZ
  Her iki yön de EN İYİ ürününde (boşluk={L}) iken sağlanabilmesi için ise
      |Δ min legsum| ≤ {GAMMA} dk   ->  BEDELSİZ
  Aradaki bölge: sağlanabilir, ama iyi yön (|Δ min legsum| − {GAMMA}) dk BOZULARAK.
  'min legsum' saf blok süresidir — içinde SIFIR karar vardır (Brief §2.2, T^IB + T^OB).
""")

mlg = conn.groupby(["market", "day"]).legsum_min.min().to_dict()

rows = []
for r in e2.itertuples():
    a = mlg.get((r.yon_A, r.gun))
    b = mlg.get((r.yon_B, r.gun))
    if a is None or b is None:
        continue
    dl = abs(a - b)
    if dl > (U - L) + GAMMA:
        kat, bedel = "A_imkansiz", np.nan
    elif dl > GAMMA:
        kat, bedel = "B_bedelli", dl - GAMMA      # iyi yönün zorunlu bozulması (dk)
    else:
        kat, bedel = "C_bedelsiz", 0.0
    rows.append(dict(gun=r.gun, yon_A=r.yon_A, yon_B=r.yon_B, rho=r.rho,
                     gozlenen_fark=r.fark, min_legsum_A=a, min_legsum_B=b,
                     d_min_legsum=dl, kategori=kat, zorunlu_bozulma_dk=bedel))
st = pd.DataFrame(rows)

tot = len(st)
for k, ad in [("A_imkansiz", "A · YAPISAL OLARAK İMKÂNSIZ (hiçbir tarife sağlayamaz)"),
              ("B_bedelli", "B · ancak İYİ YÖNÜ BOZARAK sağlanabilir"),
              ("C_bedelsiz", "C · bedelsiz sağlanabilir (kötü yönü iyileştirerek)")]:
    s = st[st.kategori == k]
    pay = 100 * len(s) / max(tot, 1)
    rpay = 100 * s.rho.sum() / max(st.rho.sum(), 1)
    print(f"  {ad:<58} {len(s):>5}  (%{pay:>4.1f} çift · %{rpay:>4.1f} ρ)")

B = st[st.kategori == "B_bedelli"]
print(f"\n  Kategori B'nin bedeli: toplam {B.zorunlu_bozulma_dk.sum():,.0f} dk ürün bozulması "
      f"(medyan {B.zorunlu_bozulma_dk.median():.0f} dk/çift, maks {B.zorunlu_bozulma_dk.max():.0f} dk)")
AB = st[st.kategori.isin(["A_imkansiz", "B_bedelli"])]
print(f"  A+B (sert E2 uygulanamaz VEYA bedelli)          : {len(AB)} çift = "
      f"%{100*len(AB)/max(tot,1):.1f} · ρ payı %{100*AB.rho.sum()/max(st.rho.sum(),1):.1f}")
print(f"  En büyük blok asimetrisi: {st.d_min_legsum.max():,.0f} dk "
      f"({st.loc[st.d_min_legsum.idxmax(), 'yon_A']} ↔ {st.loc[st.d_min_legsum.idxmax(), 'yon_B']})")

st.sort_values("d_min_legsum", ascending=False).to_csv(
    os.path.join(OUT, "audit_e2_ayristirma.csv"), index=False, encoding="utf-8-sig")


# =============================================================================
# ÖLÇÜM 3 — B2: NİHAİ çözümde zorunlu-sunum (Brief §2.3) fiilen ne kadar sağlanıyor?
# =============================================================================
hdr("ÖLÇÜM 3 — B2 (zorunlu sunum):  nihai çözümdeki gerçek uyum")
print("""Brief §2.3 (s.4): "aktarma süresi uygun olan tüm uçuşlar seçilmek zorundadır".
Test: her aday bağlantının NİHAİ tarifedeki boşluğu, çözümün KENDİ ızgara
      saatlerinden yeniden kurulur:  yeni_boşluk = (yeni_kalkış − yeni_varış) mod 1440.
Ham dakika kullanmak ±5/±10 dk ızgara artefaktı üretirdi — bu yüzden taban da
ızgaraya oturtulur (snap = round(dk/10)·10, src/03_model.py ile birebir).""")

# çözümün ızgara saatleri: (gün, uçuş, rol, eski_kova) -> yeni_kova
t0 = min(conn.ist_arr.min(), conn.ist_dep.min()).normalize()


def am(ts):
    return (ts - t0).dt.total_seconds() / 60.0


def snap(s):
    return (np.round(s / 10.0) * 10).astype(int)


c = conn.drop_duplicates(["market", "day", "FlNo1", "FlNo2"]).copy()
c["arr0"] = snap(am(c.ist_arr)) % 1440
c["dep0"] = snap(am(c.ist_dep)) % 1440

# eski_IST üzerinden birebir eşleme (aynı uçuş-gün'de 2 farklı olay olan U7 anomalileri dâhil)
move = {(r.gun, r.ucus_no, r.rol, tod(r.eski_IST)): tod(r.yeni_IST) for r in sch.itertuples()}
c["arr1"] = [move.get((r.day, r.FlNo1, R_ARR, r.arr0), r.arr0) for r in c.itertuples()]
c["dep1"] = [move.get((r.day, r.FlNo2, R_DEP, r.dep0), r.dep0) for r in c.itertuples()]
c["yeni_bosluk"] = (c.dep1 - c.arr1) % 1440
c["d_arr"] = (c.arr1 - c.arr0 + 720) % 1440 - 720
c["d_dep"] = (c.dep1 - c.dep0 + 720) % 1440 - 720
c["uygun"] = c.yeni_bosluk.between(L, U)
c["evrende"] = [(r.day, r.market) in universe for r in c.itertuples()]

sel_key = set(zip(sel.gun, sel.pazar, sel.gelen_ucus, sel.giden_ucus))
c["sunuldu"] = [(r.day, r.market, r.FlNo1, r.FlNo2) in sel_key for r in c.itertuples()]

# --- ÖNCE: kendi yeniden-kurulumumuzu çözümün kendi boşluk değeriyle doğrula ---
chk = sel.merge(c, left_on=["gun", "pazar", "gelen_ucus", "giden_ucus"],
                right_on=["day", "market", "FlNo1", "FlNo2"], how="left")
ok = int((chk.bosluk_dk == chk.yeni_bosluk).sum())
print(f"\n  [öz-denetim] yeniden kurulan boşluk == çözümün boşluğu: {ok:,}/{len(chk):,}"
      f"  {'✓' if ok == len(chk) else '✗ (aşağıdaki sayılar güvenilmez)'}")

ev = c[c.evrende]
uy = ev[ev.uygun]
ihl = uy[~uy.sunuldu]
print(f"\n  amaç evrenindeki aday bağlantı           : {len(ev):,}")
print(f"  nihai tarifede boşluğu [60,300] olan     : {len(uy):,}")
print(f"  bunlardan SUNULAN                        : {int(uy.sunuldu.sum()):,}  "
      f"-> B2 uyumu = %{100*uy.sunuldu.mean():.2f}")
print(f"  bunlardan sunulmayan (B2 ihlali)         : {len(ihl):,}  "
      f"(%{100*(1-uy.sunuldu.mean()):.2f})")
ihl_rho = sum(rho.get(m, 0) or 0 for m in ihl.market)
uy_rho = sum(rho.get(m, 0) or 0 for m in uy.market)
print(f"  ihlallerin ρ payı                        : %{100*ihl_rho/max(uy_rho,1):.2f}")
tersi = uy[uy.sunuldu].shape[0], int(ev[~ev.uygun].sunuldu.sum())
print(f"  ters yönde hata (uygun DEĞİL ama sunulan): {tersi[1]}   <- 0 olmalı (B1 kontrolü)")

# --- ÖLÇÜM 3b: bu ihlaller BİZİM tercihimiz mi, yoksa E1 mi zorluyor? ---------
ALPHA = 0.20        # E1 yönsel dengesizlik eşiği [Brief §2.4 + §4.5]
print(f"""
  ---- 3b: Sunulmayan {len(ihl)} bağlantı, bir TERCİH mi yoksa E1 ZORLAMASI mı? ----
  Tarife bu noktada SABİT: bu bağlantıları sunmak hiçbir uçuşu kımıldatmaz ve
  amacı ARTIRIR. Model yine de sunmadıysa, tek engel E1'dir. Test: her birini
  tek tek eklediğimizde  |n_od − n_do| ≤ α·(n_od + n_do)  hâlâ sağlanıyor mu?""")

ncnt = sel.groupby(["gun", "pazar"]).size().to_dict()


def e1_ok(a, b):
    return abs(a - b) <= ALPHA * (a + b) + 1e-9


bloklu = serbest = 0
for r in ihl.itertuples():
    a = ncnt.get((r.day, r.market), 0)
    b = ncnt.get((r.day, rev(r.market)), 0)
    if e1_ok(a + 1, b):
        serbest += 1
    else:
        bloklu += 1
print(f"  · eklendiğinde E1'i İHLAL eden (=zorunlu bastırma) : {bloklu:>4} "
      f"(%{100*bloklu/max(len(ihl),1):.1f})")
print(f"  · eklenebilir olduğu hâlde sunulmayan (=bizim açığımız): {serbest:>4} "
      f"(%{100*serbest/max(len(ihl),1):.1f})")

# E1 ne kadar bağlayıcı? (tek bağlantı eklemeye bile yer var mı)
prs = set()
for (g, m) in ncnt:
    rm = rev(m)
    if m < rm and (g, rm) in ncnt:
        prs.add((g, m, rm))
tight = sum(1 for (g, m, rm) in prs
            if not e1_ok(ncnt[(g, m)] + 1, ncnt[(g, rm)])
            and not e1_ok(ncnt[(g, m)], ncnt[(g, rm)] + 1))
print(f"  · E1'in TAM BAĞLI olduğu yön-çifti (iki yöne de +1 imkânsız): "
      f"{tight}/{len(prs)} (%{100*tight/max(len(prs),1):.1f})")

ihl[["day", "market", "FlNo1", "FlNo2", "gap_min", "d_arr", "d_dep", "yeni_bosluk"]] \
    .assign(rho=[rho.get(m, np.nan) for m in ihl.market],
            n_od=[ncnt.get((r.day, r.market), 0) for r in ihl.itertuples()],
            n_do=[ncnt.get((r.day, rev(r.market)), 0) for r in ihl.itertuples()]) \
    .sort_values("rho", ascending=False) \
    .to_csv(os.path.join(OUT, "audit_b2_sunulmayan.csv"), index=False, encoding="utf-8-sig")


# =============================================================================
# ÖLÇÜM 4 — G: 1131 muafiyetin kaçı FİİLEN kullanıldı?
# =============================================================================
hdr("ÖLÇÜM 4 — G muafiyetleri:  kâğıt üstünde mi, fiilen mi kullanıldı?")
print(f"""Muafiyet = o (gün, uçuş, rol) için ±{XDEV} dk bandı KURULMADI demektir.
Ama kurulmaması, uçuşun bandı AŞTIĞI anlamına gelmez. Test: nihai tarifede
her uçuş-rol grubunun ilk günü çapa alınır, diğer günlerin sapması ölçülür.""")

s2 = sch.copy()
s2["tod"] = s2.yeni_IST.map(tod)
s2["tod0"] = s2.eski_IST.map(tod)          # MEVCUT (yayınlanmış) tarifedeki saat
ex_keys = set(zip(exm.gun, exm.ucus_no, exm.rol))
s2["muaf"] = [(r.gun, r.ucus_no, r.rol) in ex_keys for r in s2.itertuples()]

links = []
for (f, rl), grp in s2.groupby(["ucus_no", "rol"]):
    grp = grp.sort_values("gun")
    if len(grp) < 2:
        continue
    a_new, a_old = grp.iloc[0].tod, grp.iloc[0].tod0
    for r in grp.iloc[1:].itertuples():
        links.append(dict(ucus_no=f, rol=rl, gun=r.gun,
                          sapma=circ(r.tod, a_new),        # BİZİM tarifemizde
                          sapma_mevcut=circ(r.tod0, a_old),  # MEVCUT tarifede
                          muaf=r.muaf))
lk = pd.DataFrame(links)

print(f"\n  toplam gün-arası bağ                     : {len(lk):,}")
print(f"  muafiyetli bağ                           : {int(lk.muaf.sum()):,} "
      f"(%{100*lk.muaf.mean():.1f})")
print(f"    [mutabakat] doğrulayıcının 'denetlenen' bağ sayısı = muaf OLMAYAN = "
      f"{len(lk)-int(lk.muaf.sum()):,}; muafiyet oranı bunun üzerinden değil, "
      f"TOPLAM {len(lk):,} bağ üzerinden okunmalıdır.")
mf = lk[lk.muaf]
kullanilmayan = mf[mf.sapma <= XDEV]
print(f"  · muaf AMA yine de ±{XDEV} dk bandında     : {len(kullanilmayan):,} "
      f"(%{100*len(kullanilmayan)/max(len(mf),1):.1f}) <- MUAFİYET FİİLEN KULLANILMADI")
gercek = mf[mf.sapma > XDEV]
print(f"  · muafiyeti GERÇEKTEN kullanan bağ        : {len(gercek):,} "
      f"(tüm bağların %{100*len(gercek)/max(len(lk),1):.1f}'i)")
if len(gercek):
    print(f"    sapma: medyan {gercek.sapma.median():.0f} dk · p90 {gercek.sapma.quantile(.9):.0f} dk "
          f"· maks {gercek.sapma.max():.0f} dk")
nm = lk[~lk.muaf]
print(f"  muaf OLMAYAN bağlarda bant dışı          : {int((nm.sapma > XDEV).sum())}  <- 0 olmalı")
print(f"\n  => G'nin FİİLEN sağlandığı bağ oranı     : "
      f"%{100*(len(lk)-len(gercek))/max(len(lk),1):.1f}  ({len(lk)-len(gercek):,}/{len(lk):,})")

# --- bu 105 sapmayı BİZ mi yarattık, girdide zaten var mıydı? -----------------
print(f"\n  Bant dışı kalan {len(gercek)} bağın kaynağı (MEVCUT tarifeyle kıyas):")
miras = gercek[gercek.sapma_mevcut > XDEV]
yeni_ihl = gercek[gercek.sapma_mevcut <= XDEV]
print(f"    · MEVCUT tarifede de zaten bant dışıydı (miras) : {len(miras):>4} "
      f"(%{100*len(miras)/max(len(gercek),1):.1f})")
print(f"    · MEVCUT'ta bantta olup BİZİM bozduğumuz        : {len(yeni_ihl):>4} "
      f"(%{100*len(yeni_ihl)/max(len(gercek),1):.1f})")
kotu = gercek[gercek.sapma > gercek.sapma_mevcut]
print(f"    · mevcuda göre KÖTÜLEŞEN bağ                    : {len(kotu):>4}"
      + (f"  (medyan +{(kotu.sapma-kotu.sapma_mevcut).median():.0f} dk, "
         f"maks +{(kotu.sapma-kotu.sapma_mevcut).max():.0f} dk)" if len(kotu) else ""))
print(f"    · mevcuda göre İYİLEŞEN bağ                     : "
      f"{int((gercek.sapma < gercek.sapma_mevcut).sum()):>4}")
print(f"\n  Tüm {len(lk):,} bağda toplam yayılım: mevcut tarife "
      f"{lk.sapma_mevcut.sum():,.0f} dk -> bizim tarife {lk.sapma.sum():,.0f} dk")
print(f"  MEVCUT tarifenin kendisi {int((lk.sapma_mevcut > XDEV).sum())} bağda "
      f"±{XDEV} dk bandını ihlal ediyor (bizde {int((lk.sapma > XDEV).sum())}).")

lk.sort_values("sapma", ascending=False).to_csv(
    os.path.join(OUT, "audit_g_muafiyet_kullanimi.csv"), index=False, encoding="utf-8-sig")

hdr("BİTTİ — üretilen dosyalar")
for f in ["audit_e2_ayristirma.csv", "audit_b2_sunulmayan.csv", "audit_g_muafiyet_kullanimi.csv"]:
    print(f"  output/{f}")
