# Bağımsız Doğrulama Raporu

**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu

*Üretim: 2026-07-16 15:51 · `python src/05_validate_solution.py`*

`output/` çözüm dosyaları, MIP kodundan (`src/03_model.py` + `src/08_fullweek_polish.py`)
geçmeden yalnız `derived/` veri katmanı üzerinden yeniden hesaplanarak doğrulanmıştır
(çift kayıt). Kısıt adları `docs/model_formulation.md` ile aynıdır.

| Kontrol | Kapsam | Sonuç | Ayrıntı |
|---|---|---|---|
| A1 ızgara (10 dk) | 4554 uçuş hareketi | PASS |  |
| A1 pencere (±60 dk) | 4554 uçuş hareketi | PASS | maks |değişim| = 60 dk |
| A1 saat aritmetiği | eski+değişim = yeni | PASS | tutarsız satır: 0 |
| olay eşleme | 5473 olay | not | 4554 ayarlanabilir (tarife dosyasıyla eşleşti), 919 sabit; tarife satırı: 4554 |
| F kova kapasitesi | 7 gün × 10 dk kovalar | PASS | aşan kova: 0 · en dolu kova: kalkış 10/10, varış 15/15 |
| A2 rotasyon (gerçek eksen) | 1709 tur (gece-aşan dahil) | PASS | YENİ ihlal: 0 · mevcut tarifede de sağlanmayan (artefakt): 358 |
| A2 aynı-gün çapası | 915 tur | PASS | çapa (min(brief-exact, mevcut tur)) altına inen: 0 |
| G düzenlilik (±15 dk bant) | 2644 gün-arası bağ | PASS | bant dışı: 0 · belgeli rotasyon-önceliği muafiyeti: 1131 · yapısal atlanan (pencere yetişemez): 0 |
| B1 boşluk penceresi | 6966 seçilen bağlantı | PASS | [60,300] dışı: 0 |
| B1 J = legsum + boşluk | 6966 bağlantı | PASS | tutarsız J: 0 · veri eşleşmeyen: 0 |
| B1 tarife ↔ bağlantı saati | 6966 bağlantı | PASS | saat uyuşmayan: 0 · boşluk uyuşmayan: 0 |
| C aktarma ödülü | 4660 pazar-gün | PASS | ödül tutarsız: 0 · sayaç tutarsız: 0 |
| D yenilen rakip | 4660 pazar-gün | PASS | fazla-beyan: 0 · ihtiyatlı (eksik-beyan): 1199 |
| D sıralama ödülü (lookup) | 4660 pazar-gün | PASS | lookup uyuşmayan: 0 |
| Amaç ρ-katkı | 4660 pazar-gün | PASS | katkı tutarsız: 0 |
| E1 yön dengesi (α=0.20) | 2001 yön-çifti | PASS | dengesiz çift: 0 |
| Amaç toplamı (OPT) | market_results ↔ bağımsız hesap | PASS | dosya Σ=3,405,039 · yeniden hesap=3,405,039 · raporlanan=3,405,039 |
| Amaç ↔ results_summary | raporlanan OPT | PASS | |Δ| = 0.4 |
| BASELINE bağımsız hesap | 4660 pazar-gün | PASS | yeniden hesap=3,251,527 · raporlanan=3,251,527 · |Δ|=0.2 |
| İYİLEŞME | bağımsız teyit | not | Δ = +153,512  (+4.72%) |

**Genel sonuç: TÜM KONTROLLER GEÇTİ**

- *ihtiyatlı (eksik-beyan)*: çözücünün β göstergesini bağlamadığı, gerçekte yenilen ama
  raporda sayılmayan rakip — amaç değerini ŞİŞİRMEZ (yalnız olduğundan küçük gösterir),
  bu yüzden hata değildir; fazla-beyan ise hata sayılır (0 olmalı).
- *eşleşme artefaktı (A2)*: mevcut yayınlanan tarifenin kendisinin de sağlamadığı
  rotasyon yorumları (o gün o çift tek uçakla dönülmüyordur); ihlal sayılmaz.
