# THY Tarife Optimizasyonu — Sonuç Özeti

**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu

*Üretim: 2026-07-13 21:25 · `python src/03_model.py byday` → `python src/08_fullweek_polish.py 1800 0.3`*

## Tam veri sonucu (güne göre ayrıştırma + tam-hafta cilalaması)

- **Çözülen gün:** 7/7  (G-gevşetilen 0)
- **Tarife-değişim cezası (λ):** 0.3 amaç-puanı / uçuş-dk (açık)
- **Ayarlanabilir uçuş hareketi:** 4554 (kaydırılan 1067, %23; toplam 20,640 uçuş-dk, ort. 19 dk)
- **OPTIMIZE amaç (saf rekabetçilik):** 3,405,039
- **BASELINE (mevcut tarife):** 3,251,527
- **İYİLEŞME:** +153,512  (**+4.72%** gelir-ağırlıklı rekabetçilik faydası)

## Gün kırılımı

| Gün | Pazar-gün | Aday bağlantı | OPT | Baseline | Δ | gap | Kaydırılan | Kaydırma-dk | G-gevş. |
|----|----|----|----|----|----|----|----|----|----|
| 1 | 670 | 1077 | 488,005 | 465,686 | +22,318 | 1.18% | 166 | 3,170 | — |
| 2 | 655 | 1062 | 465,912 | 443,873 | +22,038 | 1.18% | 161 | 3,270 | — |
| 3 | 658 | 1079 | 490,860 | 470,624 | +20,237 | 1.18% | 140 | 2,790 | — |
| 4 | 661 | 1081 | 482,902 | 459,225 | +23,677 | 1.18% | 155 | 3,110 | — |
| 5 | 667 | 1076 | 495,630 | 472,018 | +23,612 | 1.18% | 139 | 2,610 | — |
| 6 | 672 | 1094 | 486,872 | 467,761 | +19,111 | 1.18% | 153 | 2,810 | — |
| 7 | 677 | 1108 | 494,858 | 472,339 | +22,519 | 1.18% | 153 | 2,880 | — |

*Gün tablosundaki `gap` sütunu tam-hafta modelinin GLOBAL (cezalı) MIP-gap'idir
(aşama-1'in gün-içi gap'i ≤ %0.1 idi).*

## Notlar (bkz. `docs/model_formulation.md` §10–§13)

- **Tarife-değişim cezası (P, docs §12):** amaca −λ·Σ|θ−cur| eklenir (tam doğrusal: A1 sayesinde Σ_v|v−cur|·x). λ=0.3. Amaç değişimi cezalandırmadığında çözücü uçuşları keyfî kaydırıyordu (bedava/dejenere kaydırma); λ bunları geri çeker.
- 'OPTIMIZE amaç' ve 'İYİLEŞME' SAF rekabetçiliktir (cezasız ölçülür); λ yalnızca hangi kaydırmaların yapılacağını süzer.
- Kısıtlar: A1,A2,B1,C,D,E1,F,G gün-içinde tam uygulanır; G günler-arası saat-içi
  bantla zincirlenir (çatışan günde gevşetilir). Rotasyon-güvenliği önceliğiyle bandı bırakılan (gün,uçuş,rol): 1132 — `output/g_band_exemptions.csv`.
- A2 rotasyonu brief-exact minimum turla (T_OB+τ+T_IB, bacak blokları veriden) kurulur; gece-aşan turlar statik slack-bölüşümüyle korunur — 08'in gece-aşan denetimi: 1660 tur, YENİ ihlal 0 (mevcut tarifede de görünen eşleşme-artefaktları hariç). Bağımsız doğrulayıcı ayrıca gerçek zaman ekseninde 1709 turu denetler (yeni ihlal 0; `reports/validation_report.md`).
- E2 (Jmin zaman dengesi) tam-ölçekte kapalı (büyük-M min-seçimi HiGHS'i kilitliyor);
  küçük örnekte açık ve doğrulanmış.
- F kova kapasitesi brief'in gerçek 10/15'ini uygular (sabit uçuşlar baz cap'i hiç
  aşmadığından rezidüel cap ≥0; ayarlanabilirler pencerede yayılarak sığar).
  Modellenmeyen (ρ'suz → amaç dışı) pazarların uçuşları da kovalarda SABİT doluluk
  olarak sayılır (fiziksel kapasite tüm TK uçuşlarıyla korunur).
- `eski_IST`/`yeni_IST` 10 dk ızgaraya yuvarlanmış saat-içi değerlerdir.

## Çıktı dosyaları (teslim #3)

- `optimized_schedule.csv` — ayarlanan IST saatleri (uçuş × eski→yeni).
- `market_results.csv` — O–D/gün: sunulan bağlantı, **yenilen rakip**, sıralama, ρ-katkı.
- `selected_connections.csv` — seçilen her bağlantı (gelen/giden uçuş, boşluk, J, yendiği rakip).
- Toplam amaç değeri (saf rekabetçilik): **3,405,039** (baseline 3,251,527, Δ +153,512).

## Tam-hafta warm-start cilalaması (08)

Bu sonuç, güne-göre ayrıştırma (aşama-1) çözümünün HAFTANIN TAMAMINI
kapsayan tek MIP'e MIP-start olarak verilip HiGHS ile iyileştirilmesiyle
üretildi (`python src/08_fullweek_polish.py`, ≤1800s):

- Aşama-1 (byday) SAF rekabetçilik : 3,390,287.4
- Tam-hafta cilalanmış             : 3,405,039.1  (+14,751.6)
- Global MIP-gap (cezalı amaç)     : 1.18%
- G düzenliliği doğrulayıcı-birebir 'ilk-gün çapalı ±Xdev' kısıtlarıyla
  tam modelde kuruldu (2643 bağ; belgeli muafiyet: 1132, bkz. `output/g_band_exemptions.csv`).
