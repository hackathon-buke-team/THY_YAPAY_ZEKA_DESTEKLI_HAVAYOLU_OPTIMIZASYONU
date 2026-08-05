# -*- coding: utf-8 -*-
"""Ajan iddialarinin BAGIMSIZ dogrulanmasi. Her iddia icin: DOGRU / YANLIS / KISMEN."""
import pandas as pd, numpy as np, os, collections
R = r'C:\Users\darkb\Desktop\Buke_cozum'
D, O, DAT = os.path.join(R, 'derived'), os.path.join(R, 'output'), os.path.join(R, 'data')
def hdr(t): print('\n' + '=' * 92 + '\n' + t + '\n' + '=' * 92)

# ---------------------------------------------------------------- IDDIA 1: rho cakismasi
hdr('IDDIA 1: Yolcu Verisi"nde ayni O-D iki kez, CELISKILI rho ile geciyor')
pax = pd.read_excel(os.path.join(DAT, 'Yolcu Verisi_masked.xlsx'))
pax.columns = ['o', 'd', 'rho']
pax['market'] = pax.o.astype(str) + '-' + pax.d.astype(str)
dup = pax[pax.market.duplicated(keep=False)].sort_values('market')
print(f'tekrarli satir sayisi: {len(dup)} | benzersiz tekrarli pazar: {dup.market.nunique()}')
print(dup.to_string(index=False))
g = dup.groupby('market').rho.nunique()
print(f'\nCELISKILI (farkli rho) pazar sayisi: {(g > 1).sum()} / {len(g)}')
print('celiskili pazarlar ve degerleri:')
for m in g[g > 1].index:
    vals = pax[pax.market == m].rho.tolist()
    print(f'   {m}: {vals}   -> drop_duplicates(keep=first) ILK degeri alir: {vals[0]}')
mk = pd.read_csv(os.path.join(D, 'markets.csv'))
print('\nderived/markets.csv"te bu pazarlarin rho degeri:')
for m in g[g > 1].index:
    row = mk[mk.market == m]
    if len(row):
        print(f'   {m}: {row.rho.values[0]}')

# ---------------------------------------------------------------- IDDIA 2: rotasyon kapsami
hdr('IDDIA 2: 512 Pair"in yalniz bir kismi kullanilabilir (out,in) cifti uretiyor')
pair = pd.read_excel(os.path.join(DAT, 'Flight Pairs.xlsx'))
print('ham Flight Pairs:', pair.shape, list(pair.columns))
print('benzersiz Pair (ham):', pair.Pair.nunique())
full_ok = 0
for p_, gg in pair.groupby('Pair'):
    if (gg.Orig == 'IST').any() and (gg.Dest == 'IST').any():
        full_ok += 1
print(f'ham veride HEM IST-kalkis HEM IST-varis iceren Pair: {full_ok} / {pair.Pair.nunique()}')
rot = pd.read_csv(os.path.join(D, 'flight_rotation.csv'))
print(f'\nderived/flight_rotation.csv: {len(rot)} satir, {rot.Pair.nunique()} Pair')
usable = half = 0
for p_, gg in rot.groupby('Pair'):
    o_ = (gg.Orig == 'IST').any(); i_ = (gg.Dest == 'IST').any()
    if o_ and i_: usable += 1
    else: half += 1
print(f'filtre SONRASI kullanilabilir (out+in) Pair: {usable} | YARIM kalan Pair: {half}')
# yarim kalan pairlerdeki ucuslar without_partner listesinde mi?
nopart = set(pd.read_csv(os.path.join(D, 'tk_flights_without_partner.csv')).iloc[:, 0])
half_flnos = set()
for p_, gg in rot.groupby('Pair'):
    if not ((gg.Orig == 'IST').any() and (gg.Dest == 'IST').any()):
        half_flnos |= set(gg.FlNo)
print(f'yarim Pair"lerdeki ucus no: {len(half_flnos)} | bunlardan without_partner listesinde olan: {len(half_flnos & nopart)}')
print(f'  -> yani {len(half_flnos - nopart)} ucus "partneri var" gorunuyor ama A2 kisiti KURULAMIYOR')

# ---------------------------------------------------------------- IDDIA 3: G bandi 2*Xdev
hdr('IDDIA 3: G bandi capa etrafinda +-Xdev -> iki gun arasi 2*Xdev=30 dk"ya kadar fark')
s = pd.read_csv(os.path.join(O, 'optimized_schedule.csv'))
exempt = pd.read_csv(os.path.join(O, 'g_band_exemptions.csv'))
ex_keys = set(zip(exempt.gun, exempt.ucus_no, exempt.rol))
def tod(x):
    h_, m_ = map(int, x.split(':')); return h_ * 60 + m_
s['tod'] = s.yeni_IST.map(tod)
s['muaf'] = [ (r.gun, r.ucus_no, r.rol) in ex_keys for r in s.itertuples() ]
spread = s[~s.muaf].groupby(['ucus_no', 'rol']).tod.agg(['min', 'max', 'count'])
spread['yayilim'] = spread['max'] - spread['min']
spread = spread[spread['count'] > 1]
print(f'muaf OLMAYAN, >1 gunde gorunen ucus-rol grubu: {len(spread)}')
print('yayilim dagilimi (dk):')
print(spread.yayilim.value_counts().sort_index().to_string())
print(f'\n>15 dk yayilan grup: {(spread.yayilim > 15).sum()}  | maks yayilim: {spread.yayilim.max()} dk')
print(f'>30 dk yayilan grup: {(spread.yayilim > 30).sum()}')
# tum gruplar (muaf dahil)
sp2 = s.groupby(['ucus_no', 'rol']).tod.agg(['min', 'max', 'count'])
sp2['yayilim'] = sp2['max'] - sp2['min']; sp2 = sp2[sp2['count'] > 1]
print(f'\nTUM gruplar (muaf dahil): {len(sp2)} | >15 dk yayilan: {(sp2.yayilim > 15).sum()} | maks: {sp2.yayilim.max()} dk')

# ---------------------------------------------------------------- IDDIA 4: duplicate satirlar
hdr('IDDIA 4: Girdi dosyalarinda tam-satir duplicate"lar var')
conn = pd.read_excel(os.path.join(DAT, 'O&D Rakip Bağlantı Tablosu_updated.xlsx'))
print('conn:', conn.shape)
d1 = conn.duplicated().sum()
print(f'conn tam-satir duplicate: {d1}')
if d1:
    tkd = conn[conn.duplicated(keep=False) & (conn.Cr1 == 'TK')]
    print(f'  bunlarin TK olani (keep=False ile): {len(tkd)}')
print(f'Flight Pairs tam-satir duplicate: {pair.duplicated().sum()}')
print(f'pax bos hucre: {pax.isna().sum().sum()}  | detay: {pax.isna().sum().to_dict()}')

# ---------------------------------------------------------------- IDDIA 5: legsum negatif
hdr('IDDIA 5: Eski sema (J - gap) ile legsum negatif cikan satirlar')
c2 = conn.copy()
def tmin(v):
    import datetime as dt
    if isinstance(v, dt.time): return v.hour * 60 + v.minute
    return np.nan
c2['arr_m'] = pd.to_datetime(c2['Arr Time'])
c2['dep_m'] = pd.to_datetime(c2['Dep Time'])
c2['gap'] = (c2.dep_m - c2.arr_m).dt.total_seconds() / 60
def dur(v):
    import datetime as dt
    if isinstance(v, dt.time): return v.hour * 60 + v.minute + v.second / 60
    if isinstance(v, dt.datetime): return (v - dt.datetime(1899, 12, 30)).total_seconds() / 60
    if isinstance(v, (pd.Timedelta,)): return v.total_seconds() / 60
    if isinstance(v, (int, float)) and not pd.isna(v): return float(v) * 1440
    return np.nan
c2['J_raw'] = c2['Gate-to-Gate Uçuş Süresi'].map(dur)
c2['legsum_old'] = c2.J_raw - c2.gap
neg = c2[c2.legsum_old < 0]
print(f'legsum_old < 0 satir: {len(neg)} | TK olan: {(neg.Cr1 == "TK").sum()}')
print(f'  min legsum_old: {c2.legsum_old.min():.0f} dk')
print(f'ElapsedTime ile legsum: min {(c2.ElapsedTime1.map(dur) + c2.ElapsedTime2.map(dur)).min():.0f} dk (negatif olmamali)')

# ---------------------------------------------------------------- IDDIA 6: baseline snap farki
hdr('IDDIA 6: BASELINE ham gap_cur, MODEL snap edilmis saat kullaniyor -> sinirda yuvarlama artefakti')
tk = pd.read_csv(os.path.join(D, 'tk_connections.csv'), parse_dates=['ist_arr', 'ist_dep'])
def snap(m_, delta=10): return int(round(m_ / delta) * delta)
arr_m = tk.ist_arr.dt.hour * 60 + tk.ist_arr.dt.minute + tk.ist_arr.dt.day * 1440
dep_m = tk.ist_dep.dt.hour * 60 + tk.ist_dep.dt.minute + tk.ist_dep.dt.day * 1440
snap_gap = dep_m.map(snap) - arr_m.map(snap)
raw_gap = tk.gap_min
diff = (snap_gap - raw_gap)
print(f'ham gap ile snap gap farkli olan aday: {(diff != 0).sum()} / {len(tk)}')
in_raw = raw_gap.between(60, 300); in_snap = snap_gap.between(60, 300)
print(f'ham gap"a gore pencere ici : {in_raw.sum()}')
print(f'snap gap"a gore pencere ici: {in_snap.sum()}')
print(f'SINIR ARTEFAKTI (biri ici, oteki disi): {(in_raw != in_snap).sum()} aday')
if (in_raw != in_snap).sum():
    ex = tk[in_raw != in_snap].head(8)
    print(ex[['market', 'day', 'FlNo1', 'FlNo2', 'gap_min']].assign(snap_gap=snap_gap[in_raw != in_snap].head(8).values).to_string(index=False))

# ---------------------------------------------------------------- IDDIA 7: schedule sadece adjustable
hdr('IDDIA 7: optimized_schedule.csv yalniz AYARLANABILIR olaylari iceriyor')
print(f'optimized_schedule satir: {len(s)}')
print('dogrulama raporu: 4554 ayarlanabilir + 919 sabit = 5473 olay')
print(f'-> tarife dosyasinda sabit ucuslar YOK: {len(s) == 4554}')

# ---------------------------------------------------------------- IDDIA 8: snap banker rounding
hdr('IDDIA 8: snap() Python round() -> banker"s rounding, xx:x5 saatleri asagi ceker')
for t_ in [485, 475, 495, 465, 455]:
    print(f'   {t_//60:02d}:{t_%60:02d} ({t_} dk) -> round({t_}/10)*10 = {int(round(t_/10)*10)}  '
          f'[{int(round(t_/10)*10)//60:02d}:{int(round(t_/10)*10)%60:02d}]')
# veride kac ucus xx:x5"te?
c5 = (arr_m % 10 == 5).sum() + (dep_m % 10 == 5).sum()
print(f'\ntk_connections"da dakikasi 5 ile biten (10"a bolununce .5 kalan) zaman damgasi: {c5} / {2*len(tk)}')
