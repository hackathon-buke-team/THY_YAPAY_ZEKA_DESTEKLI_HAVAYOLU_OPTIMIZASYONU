# -*- coding: utf-8 -*-
"""IDDIA 6'nin BUYUKLUGUNU ol: baseline ham gap yerine SNAP gap ile hesaplansa ne olurdu?
   IDDIA 2'nin ETKISINI ol: A2 kisiti kurulamayan 221 ucus gercekten kaydi mi?"""
import pandas as pd, numpy as np, os
R = r'C:\Users\darkb\Desktop\Buke_cozum'
D, O = os.path.join(R, 'derived'), os.path.join(R, 'output')
def hdr(t): print('\n' + '=' * 92 + '\n' + t + '\n' + '=' * 92)

L, U, DELTA = 60, 300, 10
tk = pd.read_csv(os.path.join(D, 'tk_connections.csv'), parse_dates=['ist_arr', 'ist_dep'])
mk = pd.read_csv(os.path.join(D, 'markets.csv'))
nod = pd.read_csv(os.path.join(D, 'market_n_od.csv'))
tc = pd.read_csv(os.path.join(D, 'competitor_times_carrier.csv'))
rank = pd.read_csv(os.path.join(D, 'ranking_lookup.csv'))
rank.columns = ['N', 'b', 's', 'W']
rkW = {(int(r.N), int(r.b), int(r.s)): float(r.W) for r in rank.itertuples()}
rho = mk.set_index('market').rho.to_dict()
nmap = nod.set_index(['market', 'day']).N_od.to_dict()

# model evreni: TK'li ve rho'lu pazarlar
uni = set(mk[(mk.has_tk) & (~mk.excluded_no_rho)].market)
sub = tk[tk.market.isin(uni)].copy()
print(f'model evreni aday: {len(sub)}  (beklenen 7577: {len(sub)==7577})')

t0 = min(sub.ist_arr.min(), sub.ist_dep.min()).normalize()
absmin = lambda ts: (ts - t0).dt.total_seconds() / 60.0
snap = lambda m: np.round(m / DELTA) * DELTA
sub['arr_abs'] = absmin(sub.ist_arr); sub['dep_abs'] = absmin(sub.ist_dep)
sub['gap_snap'] = snap(sub.dep_abs) - snap(sub.arr_abs)
sub['gap_raw'] = sub.gap_min
sub['J_raw'] = sub.legsum_min + sub.gap_raw
sub['J_snap'] = sub.legsum_min + sub.gap_snap

comp = {}
for r in tc.itertuples():
    comp.setdefault((r.market, r.day), {})[r.carrier] = r.T_comp_min

def baseline(gapcol, Jcol):
    """current_baseline() replikasi: b_od ayni tabandan turetilir -> siralama terimi kosegende."""
    tot = conn_term = rank_term = 0.0
    n_off = 0
    for (m_, d_), g in sub.groupby(['market', 'day']):
        rh = float(rho.get(m_, 0.0))
        N = int(nmap.get((m_, d_), len(comp.get((m_, d_), {}))))
        offered = g[(g[gapcol] >= L) & (g[gapcol] <= U)]
        n = len(offered); n_off += n
        cr = sum(0.5 ** (j - 1) for j in range(1, n + 1))
        beaten = 0
        cmap = comp.get((m_, d_), {})
        if n and cmap:
            jb = offered[Jcol].min()
            beaten = sum(1 for t in cmap.values() if jb <= t)
        rr = 0.0
        if N >= 1:
            b_od = int(np.clip(N - beaten, 1, N))          # b_od baseline'dan turetilir
            s = int(np.clip(N - beaten, 1, N))
            rr = rkW.get((N, b_od, s), 0.0)                # = kosegen
        tot += rh * (cr + rr); conn_term += rh * cr; rank_term += rh * rr
    return tot, conn_term, rank_term, n_off

hdr('IDDIA 6 OLCUMU: baseline HAM gap vs SNAP gap')
t_raw = baseline('gap_raw', 'J_raw')
t_snp = baseline('gap_snap', 'J_snap')
print(f'HAM  gap ile baseline : toplam={t_raw[0]:>12,.0f}  (aktarma={t_raw[1]:>11,.0f}  siralama={t_raw[2]:>10,.0f})  sunulan={t_raw[3]}')
print(f'SNAP gap ile baseline : toplam={t_snp[0]:>12,.0f}  (aktarma={t_snp[1]:>11,.0f}  siralama={t_snp[2]:>10,.0f})  sunulan={t_snp[3]}')
print(f'\nFARK (snap - ham)     : {t_snp[0]-t_raw[0]:>+12,.0f}   ({100*(t_snp[0]-t_raw[0])/t_raw[0]:+.3f}%)')
print(f'raporlanan baseline    : 3,251,527   (ham ile uyum: {abs(t_raw[0]-3251527)<2000})')

OPT = 3405039.0
print(f'\n--- IYILESME KARSILASTIRMASI ---')
print(f'raporlanan  : OPT {OPT:,.0f} - baseline(ham)  {t_raw[0]:,.0f} = {OPT-t_raw[0]:>+11,.0f}  ({100*(OPT-t_raw[0])/t_raw[0]:+.2f}%)')
print(f'IZGARA-TUTARLI: OPT {OPT:,.0f} - baseline(snap) {t_snp[0]:,.0f} = {OPT-t_snp[0]:>+11,.0f}  ({100*(OPT-t_snp[0])/t_snp[0]:+.2f}%)')
print(f'\n-> yuvarlama artefaktinin iyilesmeye katkisi: {t_snp[0]-t_raw[0]:,.0f} puan '
      f'= toplam kazancin %{100*(t_snp[0]-t_raw[0])/(OPT-t_raw[0]):.1f}"i')

hdr('IDDIA 2 OLCUMU: A2 kisiti kurulamayan (yarim Pair) ucuslar kaydi mi?')
rot = pd.read_csv(os.path.join(D, 'flight_rotation.csv'))
half_fl = set()
for p_, g in rot.groupby('Pair'):
    if not ((g.Orig == 'IST').any() and (g.Dest == 'IST').any()):
        half_fl |= set(g.FlNo)
print(f'yarim Pair"lerdeki ucus no: {len(half_fl)}')
s = pd.read_csv(os.path.join(O, 'optimized_schedule.csv'))
ins = s[s.ucus_no.isin(half_fl)]
print(f'bunlardan tarife dosyasinda gorunen hareket: {len(ins)}  ({ins.ucus_no.nunique()} benzersiz ucus)')
mv = ins[ins.degisim_dk != 0]
print(f'GERCEKTEN KAYDIRILAN: {len(mv)} hareket ({mv.ucus_no.nunique()} ucus) | '
      f'toplam {mv.degisim_dk.abs().sum()} dk | maks {mv.degisim_dk.abs().max() if len(mv) else 0} dk')
print(f'\nkarsilastirma: TUM kaydirilan hareket 1067 -> bunlarin %{100*len(mv)/1067:.1f}"i A2-korumasiz ucuslar')
# 05 dogrulayici bu ucuslari denetliyor mu? 05 rot_pairs kullaniyor -> ayni yarim pair sorunu
print('\nNOT: bagimsiz dogrulayici (05) da ayni flight_rotation.csv"yi kullanir -> ayni ucuslar')
print('     onun denetiminde de A2 kapsamina GIRMEZ (1709 tur disinda kalirlar).')

hdr('EK: G bandi 20 dk yayilan 48 grup — hangi ucuslar?')
exempt = pd.read_csv(os.path.join(O, 'g_band_exemptions.csv'))
ex = set(zip(exempt.gun, exempt.ucus_no, exempt.rol))
s['muaf'] = [(r.gun, r.ucus_no, r.rol) in ex for r in s.itertuples()]
tod = lambda x: int(x[:2]) * 60 + int(x[3:])
s['tod'] = s.yeni_IST.map(tod)
sp = s[~s.muaf].groupby(['ucus_no', 'rol']).tod.agg(['min', 'max', 'count'])
sp['y'] = sp['max'] - sp['min']; sp = sp[(sp['count'] > 1) & (sp.y > 15)]
print(f'muaf olmayan, yayilim>15 dk grup: {len(sp)} | yayilim degerleri: {sorted(sp.y.unique())}')
print('ornekler:'); print(sp.head(10).to_string())
