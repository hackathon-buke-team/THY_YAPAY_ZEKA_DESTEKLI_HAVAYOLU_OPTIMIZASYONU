# -*- coding: utf-8 -*-
"""Kalan iddialar: F kova asimlari (docs 16/20 dogru mu?), E1 baseline ihlali, yok edilen baglantilar."""
import pandas as pd, numpy as np, os
R = r'C:\Users\darkb\Desktop\Buke_cozum'
D, O = os.path.join(R, 'derived'), os.path.join(R, 'output')
def hdr(t): print('\n' + '=' * 92 + '\n' + t + '\n' + '=' * 92)

L, U, DELTA = 60, 300, 10
tk = pd.read_csv(os.path.join(D, 'tk_connections.csv'), parse_dates=['ist_arr', 'ist_dep'])
mk = pd.read_csv(os.path.join(D, 'markets.csv'))
nopart = set(pd.read_csv(os.path.join(D, 'tk_flights_without_partner.csv')).iloc[:, 0])

hdr('IDDIA A: docs/teknik rapor "mevcut tarifede kova asimlari kalkis <=16, varis <=20" diyor')
# TUM TK ucuslari, benzersiz (flno, gun, rol, snap-saat) olayi bazinda
t0 = min(tk.ist_arr.min(), tk.ist_dep.min()).normalize()
snap = lambda s: np.round(((s - t0).dt.total_seconds() / 60) / DELTA).astype(int) * DELTA
arr = pd.DataFrame({'flno': tk.FlNo1, 'day': tk.day, 'role': 'arr', 't': snap(tk.ist_arr)})
dep = pd.DataFrame({'flno': tk.FlNo2, 'day': tk.day, 'role': 'dep', 't': snap(tk.ist_dep)})
ev = pd.concat([arr, dep]).drop_duplicates(['flno', 'role', 't'])
print(f'benzersiz olay (flno, rol, snap-saat): {len(ev)}   [veri hazirlama logu: 5474]')
for role, cap, adi in [('dep', 10, 'KALKIS'), ('arr', 15, 'VARIS')]:
    sub = ev[ev.role == role]
    cnt = sub.groupby('t').size()
    print(f'\n{adi} (cap={cap}) — TUM TK ucuslari, mevcut tarife:')
    print(f'   dolu kova: {len(cnt)} | MAKS doluluk: {cnt.max()} | cap asan kova: {(cnt > cap).sum()}')
    print(f'   en dolu 5 kova: {cnt.nlargest(5).to_dict()}')
    # sabit ucuslar
    fx = sub[sub.flno.isin(nopart)]
    cf = fx.groupby('t').size()
    print(f'   SABIT (partnersiz) ucuslarin maks doluluğu: {cf.max() if len(cf) else 0}  '
          f'(docs iddiasi: kalkis<=4, varis<=5)')

hdr('IDDIA B: mevcut tarife (baseline) E1 yon dengesini ihlal ediyor mu?')
tk['in_win'] = tk.gap_min.between(L, U)
uni = set(mk[(mk.has_tk) & (~mk.excluded_no_rho)].market)
b = tk[tk.market.isin(uni)].groupby(['market', 'day']).in_win.sum().astype(int)
bd = b.to_dict()
ALPHA = 0.20
chk = bad = 0; seen = set()
worst = []
for (m_, d_), n_od in bd.items():
    o, dd = m_.split('-'); rk = (f'{dd}-{o}', d_)
    if rk in bd and ((m_, d_), rk) not in seen and (rk, (m_, d_)) not in seen:
        seen.add(((m_, d_), rk)); chk += 1
        n_do = bd[rk]
        if abs(n_od - n_do) > ALPHA * (n_od + n_do) + 1e-9:
            bad += 1; worst.append((m_, rk[0], d_, n_od, n_do))
print(f'kontrol edilen yon-cifti: {chk} | E1 IHLAL eden: {bad}  ({100*bad/chk:.1f}%)')
print('ornekler (pazar, ters, gun, n_od, n_do):', worst[:8])
print('\nKARSILASTIRMA: optimize cozumde dogrulayici 2001 yon-ciftinde 0 ihlal buldu.')

hdr('IDDIA C: baseline"da sunulan ama cozumde SUNULMAYAN baglanti sayisi')
sel = pd.read_csv(os.path.join(O, 'selected_connections.csv'))
sel_key = set(zip(sel.gun, sel.pazar, sel.gelen_ucus, sel.giden_ucus))
base_off = tk[tk.market.isin(uni) & tk.in_win]
base_key = set(zip(base_off.day, base_off.market, base_off.FlNo1, base_off.FlNo2))
lost = base_key - sel_key
gained = sel_key - base_key
print(f'baseline"da sunulan (model evreni)   : {len(base_key)}')
print(f'cozumde sunulan                     : {len(sel_key)}')
print(f'KAYBEDILEN (baseline"da var, cozumde yok): {len(lost)}')
print(f'KAZANILAN (cozumde var, baseline"da yok): {len(gained)}')
print(f'NET                                 : {len(gained) - len(lost):+d}')
# kaybedilenlerin rho agirligi
rho = mk.set_index('market').rho.to_dict()
lost_rho = sum(rho.get(k[1], 0) for k in lost)
gain_rho = sum(rho.get(k[1], 0) for k in gained)
print(f'\nkaybedilenlerin toplam rho: {lost_rho:,.0f} | kazanilanlarin: {gain_rho:,.0f}')

hdr('IDDIA D: N=1 pazarlarda siralama odulu olu mu? (W(1,1,1)=0)')
mres = pd.read_csv(os.path.join(O, 'market_results.csv'))
print('N_rakip=0 pazar-gun:', (mres.N_rakip == 0).sum())
print('N_rakip=1 pazar-gun:', (mres.N_rakip == 1).sum())
print('N<=1 toplam        :', (mres.N_rakip <= 1).sum(), f'= %{100*(mres.N_rakip<=1).mean():.1f} of {len(mres)}')
print('siralama_odul == 0 olan pazar-gun:', (mres.siralama_odul == 0).sum())
print('N=1 olup siralama_odul != 0:', ((mres.N_rakip == 1) & (mres.siralama_odul != 0)).sum())
print('\n-> siralama terimi FIILEN aktif pazar-gun:', (mres.siralama_odul != 0).sum())

hdr('IDDIA E: aktarma odulu pazar-gun basina 2.0"da doyuyor; baseline tavanin ne kadarinda?')
maxpg = 2.0
print(f'aktarma odulu teorik tavan (pazar-gun basina): {maxpg}  [sum (1/2)^(j-1) -> 2]')
print(f'cozumde ortalama aktarma_odul: {mres.aktarma_odul.mean():.3f}  (tavanin %{100*mres.aktarma_odul.mean()/maxpg:.1f}"i)')
# baseline aktarma odulu
bcnt = tk[tk.market.isin(uni)].groupby(['market','day']).in_win.sum().astype(int)
brew = bcnt.map(lambda n: sum(0.5**(j-1) for j in range(1, n+1)))
print(f'baseline ortalama aktarma odulu: {brew.mean():.3f}  (tavanin %{100*brew.mean()/maxpg:.1f}"i)')
print(f'-> aktarma teriminde kalan bas alan: %{100*(maxpg-mres.aktarma_odul.mean())/maxpg:.1f}')
