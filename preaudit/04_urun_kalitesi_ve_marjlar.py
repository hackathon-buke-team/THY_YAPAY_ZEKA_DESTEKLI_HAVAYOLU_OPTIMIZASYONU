# -*- coding: utf-8 -*-
"""Havacilik merceginin sayisal iddialari: yeni baglantilarin kalitesi, MCT sinir riski,
   rakip yenme marjlari, G muafiyet orani."""
import pandas as pd, numpy as np, os
R = r'C:\Users\darkb\Desktop\Buke_cozum'
D, O = os.path.join(R, 'derived'), os.path.join(R, 'output')
def hdr(t): print('\n' + '=' * 92 + '\n' + t + '\n' + '=' * 92)
L, U = 60, 300

tk = pd.read_csv(os.path.join(D, 'tk_connections.csv'))
mk = pd.read_csv(os.path.join(D, 'markets.csv'))
sel = pd.read_csv(os.path.join(O, 'selected_connections.csv'))
uni = set(mk[(mk.has_tk) & (~mk.excluded_no_rho)].market)
tk['in_win'] = tk.gap_min.between(L, U)

sel_key = set(zip(sel.gun, sel.pazar, sel.gelen_ucus, sel.giden_ucus))
bo = tk[tk.market.isin(uni) & tk.in_win]
base_key = set(zip(bo.day, bo.market, bo.FlNo1, bo.FlNo2))
gained = sel_key - base_key
lost = base_key - sel_key

hdr('IDDIA S3: yeni kazanilan baglantilarin KALITESI (bekleme suresi)')
sel['key'] = list(zip(sel.gun, sel.pazar, sel.gelen_ucus, sel.giden_ucus))
gnew = sel[sel.key.isin(gained)]
print(f'kazanilan baglanti: {len(gnew)}')
print(f'bekleme (bosluk) istatistigi: {gnew.bosluk_dk.describe().round(1).to_dict()}')
print('\nbanda gore dagilim:')
bins = [59, 90, 120, 150, 180, 210, 240, 270, 300]
print(pd.cut(gnew.bosluk_dk, bins).value_counts().sort_index().to_string())
print(f'\n270-300 dk bandinda: {gnew.bosluk_dk.between(270,300).sum()} '
      f'(%{100*gnew.bosluk_dk.between(270,300).mean():.1f})')
print(f'TAM 300 dk        : {(gnew.bosluk_dk==300).sum()}')
print(f'medyan            : {gnew.bosluk_dk.median()} dk')
print('\n-- karsilastirma: TUM sunulan baglantilar --')
print(f'270-300 bandinda: {sel.bosluk_dk.between(270,300).sum()} (%{100*sel.bosluk_dk.between(270,300).mean():.1f}) | medyan {sel.bosluk_dk.median()}')
print('\n-- kaybedilen baglantilarin (baseline) beklemesi --')
bo2 = bo.copy(); bo2['key'] = list(zip(bo2.day, bo2.market, bo2.FlNo1, bo2.FlNo2))
glost = bo2[bo2.key.isin(lost)]
print(f'kaybedilen: {len(glost)} | bekleme: {glost.gap_min.describe().round(1).to_dict()}')
print(f'  bunlarin 60-120 dk (IYI urun) olani: {glost.gap_min.between(60,120).sum()} '
      f'(%{100*glost.gap_min.between(60,120).mean():.1f})')
print(f'  270-300 dk olani: {glost.gap_min.between(270,300).sum()}')

hdr('IDDIA S4: MCT sinirinda (60 dk) yigilma riski')
print(f'TAM 60 dk bekleyen sunulan baglanti: {(sel.bosluk_dk==60).sum()} (%{100*(sel.bosluk_dk==60).mean():.1f})')
print(f'<=70 dk: {(sel.bosluk_dk<=70).sum()} (%{100*(sel.bosluk_dk<=70).mean():.1f})')
print(f'<=90 dk: {(sel.bosluk_dk<=90).sum()} (%{100*(sel.bosluk_dk<=90).mean():.1f})')
print('\n-- baseline karsilastirmasi --')
print(f'baseline TAM 60 dk: {(bo.gap_min==60).sum()} (%{100*(bo.gap_min==60).mean():.1f})')
print(f'baseline <=70 dk  : {(bo.gap_min<=70).sum()} (%{100*(bo.gap_min<=70).mean():.1f})')

hdr('IDDIA S12: rakip yenme MARJLARI — cozum ne kadar kirilgan?')
tc = pd.read_csv(os.path.join(D, 'competitor_times_carrier.csv'))
comp = {}
for r in tc.itertuples():
    comp.setdefault((r.market, r.day), {})[r.carrier] = r.T_comp_min
# her sunulan baglanti icin: hangi rakipleri hangi marjla yeniyor
marg = []
for r in sel.itertuples():
    cm = comp.get((r.pazar, int(r.gun)), {})
    for ca, t in cm.items():
        if r.J_dk <= t:
            marg.append(t - r.J_dk)
marg = np.array(marg)
print(f'toplam (baglanti, yenilen rakip) cifti: {len(marg)}')
print(f'marj (dk): min {marg.min():.0f} | medyan {np.median(marg):.0f} | ort {marg.mean():.0f} | maks {marg.max():.0f}')
for th in [10, 20, 30, 60]:
    print(f'   marj < {th:3d} dk: {(marg<th).sum():5d}  (%{100*(marg<th).mean():.1f})')
print('\n-> rakipler tarifesini 30 dk oynatirsa kaybedilebilecek galibiyet orani: '
      f'%{100*(marg<30).mean():.1f}')

hdr('IDDIA S15: G muafiyet orani')
ex = pd.read_csv(os.path.join(O, 'g_band_exemptions.csv'))
print(f'muafiyet kaydi: {len(ex)}')
print(f'dogrulayicinin denetledigi gun-arasi bag: 2644')
print(f'muafiyet / toplam bag: {1131}/2644 = %{100*1131/2644:.1f}')
print(f'  -> "belgeli muafiyet 1131" dogrulama raporundan; 1132 = byday 1110 + cilalama 22')

hdr('EK: kaydirilan hareketlerin gece bandi ve uzun menzil dagilimi')
s = pd.read_csv(os.path.join(O, 'optimized_schedule.csv'))
mv = s[s.degisim_dk != 0].copy()
mv['saat'] = mv.yeni_IST.str.slice(0, 2).astype(int)
night = mv[(mv.saat >= 0) & (mv.saat < 6)]
print(f'kaydirilan hareket: {len(mv)} | 00:00-06:00 bandinda: {len(night)} (%{100*len(night)/len(mv):.1f})')
bt = pd.read_csv(os.path.join(D, 'flight_block_times.csv'))
longh = set(bt[bt.block_min > 360].flno)
print(f'uzun menzil (blok>6sa) ucus no: {len(longh)}')
print(f'kaydirilan hareketlerden uzun menzil olan: {mv.ucus_no.isin(longh).sum()} '
      f'(%{100*mv.ucus_no.isin(longh).mean():.1f})')
print(f'  bunlardan >30 dk kayan: {mv[mv.ucus_no.isin(longh) & (mv.degisim_dk.abs()>30)].shape[0]}')
