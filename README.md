# THY Tarife Optimizasyonu — Rakip Odaklı Ağ Optimizasyonu / Teknofest 4.lüğü

**Takım: Büke** · **TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu** · Pyomo + HiGHS (açık-kaynak), tümüyle Python.

---

## Problem ve amaç (sade anlatım)

THY, İstanbul'u (IST) bir **aktarma merkezi** olarak kullanır. Birçok yolcu direkt uçamaz; örneğin
**Venedik → IST → Cidde** şeklinde aktarma yapar. Bu yolcu için önemli olan **toplam yolculuk
süresidir** (gelen uçuş + IST'te bekleme + giden uçuş). Aynı yolcuyu **rakip havayolları** da başka
merkezler üzerinden taşımak ister.

THY'nin elindeki kaldıraç **IST'teki uçuş saatleridir.** Bunları öyle ayarlamalıyız ki:

- **İyi aktarma bağlantıları** oluşsun — IST'teki bekleme 60–300 dk arasında (ne kaçıracak kadar
  kısa, ne sıkıcı kadar uzun);
- THY'nin toplam süresi **rakibinkini geçsin** → o pazarda THY'nin rekabet sıralaması iyileşsin.

Her O–D pazarının önemi **gelir potansiyeli ρ** ile ölçülür. **Amaç:** tüm pazarlarda *gelir-ağırlıklı*
"iyi bağlantı sunma + rakip yenme" toplam faydasını **en büyük** yapacak uçuş saatlerini bulmak — tüm
operasyonel kurallara (uçak rotasyonu, hub kapasitesi, tarife düzenliliği, yön dengesi) uyarak.

## Ne yaptık? (özet)

1. İş problemini **matematiksel bir MIP modeline** çevirdik (karar = ayarlanabilir uçuşların IST saati).
2. **Çalışan kod** yazdık (Python + Pyomo + HiGHS) ve çözdürdük.
3. Gerçek veriyi temiz/belgeli işledik; **7 günün tamamına** ölçekledik (tek-parça problem soğuk
   başlangıçla çözülemiyordu → güne göre ayrıştırdık). Hafta-kopyası kayıtları kanonik haftaya
   indirgedik → aynı fiziksel uçuşa **tek tutarlı karar**, aynı bağlantıya **çift ödül sayımı yok**.
4. **Yenilik 1:** doğrusal bir **tarife-değişim cezası** ekledik → çözüm hem gerçekçi (uçuşların %92'si
   yerine %23'ü oynar) hem de daha iyi oldu (dejenerasyonu kırdı: +%3.89 → +%4.32, aşama-1).
5. **Yenilik 2:** güne-göre çözümü **tam-hafta MIP'ine MIP-start** olarak verip küresel cilaladık
   (`src/08_fullweek_polish.py`): +%4.32 → **+%4.72** ve **kanıtlı global gap %1.18**.
6. **Bağımsız doğrulayıcı** yazdık (çift kayıt ilkesi): çözüm, MIP kodundan geçmeden yalnız veri
   katmanından yeniden hesaplanıp denetlenir — **tüm kontroller PASS** (`reports/validation_report.md`).
7. **Sonuç: mevcut tarifeden +%4.72 daha rekabetçi — tüm kısıtlara tam uyumla**
   (G-gevşetme 0 gün, rotasyonda yeni ihlal 0; güncellenmiş ElapsedTime'lı veri, brief-exact A2).

## Sonuç

| | Değer |
|---|---|
| **İYİLEŞME** | **+153 512 (+%4.72)** gelir-ağırlıklı rekabetçilik faydası |
| OPTIMIZE amaç | 3 405 039 · BASELINE (mevcut tarife) 3 251 527 |
| Tarife değişikliği | 4 554 uçuş hareketinden yalnız **1 067'si (%23)** kaydırıldı (ort. 19 dk) |
| Çözüm | 2 aşama: güne-göre ayrıştırma (~1.5 dk, gün-içi gap ≤ %0.1) + tam-hafta MIP-start cilalama (≤30 dk) → **kanıtlı global gap %1.18** |
| Kısıt uyumu | **G-gevşetilen gün: 0** · A2 rotasyon (gerçek eksen, gece-aşan dahil): **yeni ihlal 0** (1 709 tur) · **bağımsız doğrulayıcı: tüm kontroller PASS** |

## Değerlendirme kriterleriyle eşleme

| Kriter | Ağırlık | Bu teslimde |
|---|---|---|
| 1. Model doğruluğu & kapsam | %30 | A–G kısıtlarının tamamı doğrusal MIP olarak kuruldu ve sıkı doğrusallaştırıldı; A2 rotasyonu **brief-exact** (T_OB+τ+T_IB, bacak blokları güncel veriden; gece-aşan turlar yapısal garantili + doğrulanmış), F kapasitesi (gerçek 10/15, **tüm TK uçuşlarıyla**) ve sıralama tabanı brief tanımına uyumludur. E2 ve B2, sert biçimde uygulandığında infeasible/çözülemez olduğu **sayısal olarak kanıtlanarak** gevşetilmiştir (`docs/model_formulation.md` §10). |
| 2. Çözüm kalitesi | %25 | Mevcut tarifeye göre **+%4.72** gelir-ağırlıklı iyileşme (**kanıtlı global MIP-gap %1.18**); **tüm kısıtlara tam uyumlu** çözüm (G-gevşetme 0, rotasyonda yeni ihlal 0) — üstelik **bağımsız doğrulayıcıyla teyitli** (tüm kontroller PASS; amaç ve baseline bağımsız hesapla birebir). Kod, jürinin gizli test örneği için veriden bağımsız (genel) tasarlanmıştır. |
| 3. Performans & ölçeklenebilirlik | %15 | Yön-yerel büyük-M, kapsamlı ön-işleme ve güne-göre ayrıştırma ile 7 günün tamamı ~1.5 dakikada çözülür (gün-içi gap ≤ %0.1); tam-hafta MIP-start cilalaması (≤30 dk) küresel optimalite kanıtı ekler (global gap %1.18). |
| 4. Kod kalitesi & tekrar-üretilebilirlik | %15 | Modüler yapı; **`python run_all.py` tek komutla uçtan uca** (doğrulayıcı FAIL verirse durur); deterministik ayarlar (HiGHS `threads=1, random_seed=0`; aşama-1 byte-byte aynı çıktı; süre-sınırlı aşama-2 için not: aşağıda "Çalıştırma"). |
| 5. Teknik rapor & dokümantasyon | %10 | `reports/technical_report.md` (~6 sayfa, **figürlü**) + tam matematiksel model dokümanı + bağımsız doğrulama ve duyarlılık raporları. |
| 6. Yenilikçilik & ileri yöntemler | %5 | Büyük-M'siz tarife-değişim ceza-regülarizasyonu; **tam-hafta MIP-start cilalaması** (global optimalite kanıtı); hafta-normalizasyonu (veri tutarlılığı); **çift-kayıt bağımsız doğrulama**; λ/pencere/τ duyarlılık analizi. |

### Gizli test verisine genelleme ve sağlamlık

Çözüm kalitesi jüriye kapalı bir gizli test örneği üzerinde ölçülür; bu nedenle kod, belirli bir veri
kümesine bağlı kalmayacak biçimde tasarlanmıştır:

- **Hiçbir parametre sabitlenmemiştir (hardcode yok):** operasyon günleri, pazarlar, rakipler ve uçuşlar
  tümüyle **veriden türetilir** (gün sayısı 7'ye sabitlenmez).
- **Şema doğrulaması:** girdi Excel dosyalarında beklenen sütun yoksa, kriptik `KeyError` yerine **açık
  ve okunabilir bir hata** verilir.
- **Hata izolasyonu:** tek bir günün/çözümün hatası yakalanıp atlanır; koşu bütünüyle çökmez ve kısmi de
  olsa feasible çıktı üretilir.
- **Determinizm:** HiGHS `threads=1, random_seed=0` ile çağrılır; aynı girdi **byte-byte aynı** çıktıyı
  verir.
- **Bağımsız doğrulama koşuya gömülü:** `run_all.py`, çözümden sonra `05_validate_solution.py`'yi
  çalıştırır; herhangi bir kısıt/amaç kontrolü FAIL verirse koşu durur — gizli veride de geçersiz
  çıktı teslim edilmez.

## Klasör Yapısı

```
THY_Tarife_Optimizasyonu/
├── data/            Yarışmanın orijinal girdi dosyalarının KOPYASI (yalnız okunur)
│                      • O&D Rakip Bağlantı Tablosu_updated.xlsx · Yolcu Verisi_masked.xlsx
│                      • change_ranking_input.xlsx · Flight Pairs.xlsx
├── src/             • 01_data_health_check.py   veri sağlık kontrolü
│                    • 02_data_prep.py           "altın" veri katmanı (minimal+belgeli)
│                    • 03_model.py               MIP modeli (Pyomo + HiGHS) — ana çözücü
│                    • 04_export_docs.py         .md → .docx → .pdf teslim biçimleri
│                    • 05_validate_solution.py   BAĞIMSIZ çözüm doğrulayıcı (çift kayıt)
│                    • 06_make_figures.py        rapor figürleri (PNG)
│                    • 07_sensitivity.py         λ / pencere / τ duyarlılık taraması
│                    • 08_fullweek_polish.py     tam-hafta MIP-start cilalaması (aşama-2)
├── derived/         02_data_prep.py'nin ürettiği temiz veri (model girdisi) + transform_log.md
├── docs/            • model_formulation.md / .docx / .pdf   matematiksel model (teslim #1)
│                    • figures/                              rapor figürleri
├── reports/         • technical_report.md / .docx / .pdf    teknik rapor ~6 sayfa (teslim #4)
│                    • validation_report.md                  bağımsız doğrulama raporu
│                    • fullweek_polish.md                    tam-hafta cilalama koşu raporu
│                    • sensitivity_analysis.md               duyarlılık analizi
│                    • data_health_report.md                 veri sağlık raporu
├── output/          • optimized_schedule.csv          ayarlanan IST saatleri
│                    • market_results.csv              O–D/gün: yenilen rakip + ödüller
│                    • selected_connections.csv        seçilen her bağlantı
│                    • g_band_exemptions.csv           G bandı belgeli muafiyetleri (şeffaflık)
│                    • sweep_results.csv               λ-taraması ham sonuçları
│                    • results_summary.md / .docx / .pdf     sonuç özeti + toplam amaç
├── run_all.py       TEK KOMUTLA uçtan uca koşu (aşağıya bakın)
├── requirements.txt
└── README.md
```

> `references/` (organizatörün Brief/sunum PDF'leri) yereldedir ama telifli 3. taraf materyali
> olduğundan depoya **dahil edilmez** (`.gitignore`). `data/`+`derived/` proje çalışsın diye dahildir.

## Kurulum

```bash
python -m venv .venv && .venv\Scripts\activate     # Windows (opsiyonel)
pip install -r requirements.txt
```

Doğrulanmış ortam: Python 3.13, Windows 11. Çözücü HiGHS tek-iş parçacıklıdır → **deterministik**.

## Çalıştırma (proje kökünden)

**Tek komutla uçtan uca** (veri sağlığı → hazırlama → model → **tam-hafta cilalama** → **bağımsız
doğrulama** → figürler → docx/pdf):

```bash
python run_all.py                      # ~35–40 dk (30 dk'sı tam-hafta cilalama); doğrulayıcı FAIL verirse durur
python run_all.py --with-sensitivity   # + λ/pencere/τ duyarlılık taraması (~15–30 dk ek)
```

> **Determinizm notu:** HiGHS her yerde `threads=1, random_seed=0` ile çağrılır. Aşama-1 (güne-göre,
> gap-sonlandırmalı) aynı girdiyle **byte-byte aynı** çıktıyı verir (doğrulandı). Aşama-2 cilalama
> süre-sınırlı (1800 s) olduğundan farklı donanımda kesme noktası — dolayısıyla incumbent — teoride
> değişebilir; her koşu **kendi çıktısını bağımsız doğrulayıcıdan geçirir** ve 08 yalnız kanıtlı
> iyileşme varsa `output/`u günceller (aksi hâlde deterministik aşama-1 çıktısı geçerli kalır).

Adımlar tek tek de koşulabilir:

```bash
python src/01_data_health_check.py     # -> reports/data_health_report.md
python src/02_data_prep.py             # -> derived/*.csv  (model girdisi)
python src/03_model.py                 # küçük alt-örnek (TÜM kısıtlar, elle doğrulanır)
python src/03_model.py byday           # TAM VERİ — güne göre ayrıştır (varsayılan λ ile)
python src/03_model.py byday 0         # cezasız varyant (uçuşların ~%92'si kayar)
python src/03_model.py sweep           # λ ödünleşim taraması — Pareto tablo (docs §12)
python src/08_fullweek_polish.py 1800  # tam-hafta MIP-start cilalaması (aşama-2, docs §13)
python src/05_validate_solution.py     # BAĞIMSIZ doğrulama -> reports/validation_report.md
python src/06_make_figures.py          # rapor figürleri -> docs/figures/*.png
python src/07_sensitivity.py           # duyarlılık -> reports/sensitivity_analysis.md
python src/04_export_docs.py           # teslim dokümanları: .md -> .docx -> .pdf (Word ile)
```

## Teslimler (Brief eşlemesi)

| # | Teslim | Dosya |
|---|---|---|
| 1 | Matematiksel model dokümanı (PDF) | `docs/model_formulation.pdf` (+ `.md` / `.docx`) |
| 2 | Çalışan kod (Python + Pyomo) | `src/01–08_*.py` + `run_all.py` |
| 3 | Çıktı dosyası (bağlantı, IST, yenilen rakip, amaç) | `output/*.csv` + `results_summary.md` |
| 4 | Teknik rapor (~6 sayfa, PDF) | `reports/technical_report.pdf` (+ `.md` / `.docx`) |
| 5 | README | bu dosya |
| + | Bağımsız doğrulama raporu (destekleyici kanıt) | `reports/validation_report.md` |
| + | Tam-hafta cilalama koşu raporu (destekleyici kanıt) | `reports/fullweek_polish.md` |
| + | Duyarlılık analizi (destekleyici kanıt) | `reports/sensitivity_analysis.md` |

> **Biçimler:** `python src/04_export_docs.py` tüm `.md` kaynaklarından `.docx` (pandoc) ve `.pdf`
> (yüklü Microsoft Word üzerinden, otomatik) üretir.

## Model özeti

- **Çözüm stratejisi (2 aşama):** güne-göre ayrıştırma (λ=0.3, ~1.5 dk) + tam-hafta MIP-start
  cilalaması (≤1800 s, global gap %1.18) — docs §11–§13.
- **Karar:** ayarlanabilir uçuşların IST saatleri (10 dk kova, mevcut ± 60 dk pencere).
- **Amaç:** Σ ρ_od·(azalan-getiri bağlantı ödülü + sıralama ödülü) − λ·(toplam kaydırma).
- **Kısıtlar:** A (zaman + rotasyon — brief-exact min tur T_OB+τ+T_IB, bacak blokları güncel veriden;
  gece-aşan turlar statik slack-bölüşümüyle yapısal garantili), B (bağlantı uygunluğu), C (azalan
  getiri/monoton slot), D (rakip yenme+sıralama), E1 (yönsel sayı dengesi), F (hub kova kapasitesi —
  brief'in gerçek 10/15'i), G (gün-arası düzenlilik).
- **Sıkılık:** yön-yerel büyük-M; ön-işleme ile yenme/uygunluk elemesi; ceza ve argmin terimleri
  **büyük-M'siz** (docs §3/§12).

## Bilinen sınırlar ve açık noktalar

- **E2** (yön bazında en iyi süre dengesi) tam-ölçekte kapalı: min-seçimi büyük-M'i çözücüyü kilitliyor;
  küçük-ölçekte açık ve doğrulanmış (gerçek 10/15 F altında da çözülemez — kanıtlı).
- **B2** ("uygun olan tüm bağlantılar zorunlu sunulur") varsayılan kapalı: zorlanırsa tek günler bile
  infeasible (E1 yön dengesiyle çatışma — gün 1/2 saniyeler içinde, gerçek F altında doğrulandı).
  Etki küçük: amaç sunmayı ödüllendirdiğinden pencereye erişebilir adayların **%90+'ı zaten sunuluyor**
  (aşama-1 çözümünde ölçüldü: 6 877/7 577 = %90.8; nihai çözümde 6 966 bağlantı sunulu); sunulmayanların
  da çoğu paylaşılan uçuş saatlerinin başka pazarlarda pencere-dışı kalmasından — bilinçli bastırılan
  yalnız ~%3.5.
- **b_od taban sıralaması** artık baseline ile **iç-tutarlı** (mevcut tarife her pazarda lookup
  köşegenine = "değişim yok" nötr referansına oturur);
  yalnız kesin türetim kuralının organizatör tanımı teyit bekliyor (docs §9). Hub kapasitesi brief'in
  gerçek 10/15'ini uygular.
- Bunların ayrıntılı gerekçesi `docs/model_formulation.md` §10–§12 ve `reports/technical_report.md`'de.

## Veri ele alma — "Minimal + Belgeli"

- Orijinal Excel'lere **asla** dokunulmaz; hiçbir değer uydurulmaz.
- **Hafta normalizasyonu + tekilleştirme:** aynı operasyon gününün farklı takvim-haftası kopyaları tek
  kanonik haftaya çekilir (boşluk/J değişmez) ve birebir özdeşleşen aday satırları tekilleştirilir —
  aynı fiziksel uçuşa iki farklı saat atanması ve aynı bağlantıya çift ödül sayımı önlenir
  (`derived/transform_log.md`).
- Yolculuk süresi J, güncellenmiş verinin bacak süresi sütunlarından (`ElapsedTime1/2`) **kesin**
  hesaplanır (`J = E1 + boşluk + E2`); Gate-to-Gate'in 24sa sarma belirsizliği yoktur (tüm satırlar
  mod-24sa çapraz doğrulanır). ElapsedTime'sız eski şema gelirse kod, fiziksel imkânsız satırlara
  (J < boşluk) +24sa uygulayan minimal de-wrap'e otomatik döner.
- Belirsizlik nötr/ihtiyatlı: ρ eksik pazar → dışla; rotasyon partneri yok → sabit kabul.
- Tüm dönüşümler `derived/transform_log.md`'de; `src/02_data_prep.py` `CFG` ile geri alınabilir.

## Final sunumu materyalleri

Finale hazırlık için üretilen ek dokümanlar (`docs/` ve `preaudit/`). **Okuma sırası aşağıdaki gibidir:**

| # | Dosya | Sayfa | İçerik |
|---|---|---|---|
| 1 | `docs/Buke_ON_BILGI_DERSI.docx` / `.pdf` | 12 | **Ön koşul.** Hiçbir ön bilgi varsaymayan konu anlatımı: bir havayolu nasıl çalışır (hub ekonomisi, dalga yapısı, rotasyon, tarife planlama süreci, terimler) → optimizasyon nedir (**elle çözülen LP/tamsayı/branch-and-bound/big-M örnekleriyle**) → projenin sembol sözlüğü ve karıştırılan kavramlar → yarışma bağlamı, okuma haritası, takım rol dağılımı. |
| 2 | `docs/Buke_ANLAMA_ve_ANLATMA_Kilavuzu.docx` / `.pdf` | 34 | Projeyi sıfırdan anlatan kılavuz: veri → model → **kod satır satır (11 gerçek blok)** → karar günlüğü (**neden HiGHS, neden Gurobi değil**, neden Pyomo, neden MIP) → **projenin hikâyesi: karşılaşılan 10 problem** → sunum senaryosu → 23 soruluk öz-test. |
| 3 | `docs/Buke_JURI_SORU_BANKASI.docx` / `.pdf` | 21 | **59 zorlayıcı jüri sorusu**, sekiz mercekte gruplu (model, çözüm kalitesi, ön-denetim, veri, operasyon, yazılım, ileri seviye, tuzak). Her soru için: neden zor, hazır cevap, dayanak dosyası. |
| 4 | `docs/Buke_FINAL_Sunum_Hazirlik_Dosyasi.docx` / `.pdf` | 61 | Referans dosyası: tam matematiksel model, doğrusallaştırma kararları, sonuçların tam sayısal dökümü, doğrulama, duyarlılık, zayıflıklar ve **§13.11 ÖN-DENETİM bulguları**. |
| 5 | `docs/Buke_GELISTIRME_YOL_HARITASI.docx` / `.pdf` | 29 | **«Bu çözüme ne eklenebilir?»** — 81 somut geliştirme, çoğu matematiksel formülasyonuyla: hızlı kazanımlar, model genişletmeleri (soft-E2, kalite ağırlığı, tail sürekliliği), çözüm yöntemleri (indicator constraints, LNS, Benders), stokastik/robust uzantılar, rekabet dinamikleri, talep-gelir modellemesi, **yapay zekâ entegrasyonu**, ürünleşme, test. Öncelik matrisi + 4 fazlı yol haritası. |
| + | `preaudit/` | — | Final öncesi **öz-denetim betikleri**. Çözümü, üreten koddan bağımsız olarak yeniden ölçer (baseline, kapasite, rotasyon kapsamı, ürün kalitesi, rakip yenme marjları). |

> Öz-denetimin en önemli iki bulgusu şeffaflık adına burada da belirtilir:
> **(1)** Baseline bağlantı boşluklarını ham dakika hassasiyetiyle, model ise 10 dk ızgarada
> değerlendirdiğinden, raporlanan +%4,72'lik kazancın 21.597 puanı (%14,1) ayrıklaştırmadan
> gelir; ızgara-tutarlı karşılaştırmada iyileşme **+%4,03**'tür.
> **(2)** Rotasyon eşleri uçuş bazlı filtrelendiği için 512 Pair'in 291'i kullanılabilir
> gidiş-dönüş çifti üretir; 221 uçuşta A2 kısıtı kurulamamaktadır (kaydırılan hareketlerin
> %23,2'si). Kök neden: `Flight Pairs.xlsx` W26 (Kış 2026) sezonuna, tarife verisi ise
> Ağustos 2025'e aittir.
