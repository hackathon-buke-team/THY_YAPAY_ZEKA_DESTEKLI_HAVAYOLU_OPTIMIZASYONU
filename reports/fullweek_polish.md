# Tam-Hafta Warm-Start Cilalaması — Koşu Raporu

**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu

*Üretim: 2026-07-13 21:25 · `python src/08_fullweek_polish.py 1800 0.3`*

Aşama-1 (güne-göre ayrıştırma) çözümü, haftanın tamamını kapsayan tek MIP'e
**MIP-start** (HiGHS `setSolution`) olarak verildi; branch-and-bound bu
incumbent'tan devam ederek günler-arası koordinasyonu küresel iyileştirdi.
Amaç ve kısıtlar 03 ile birebir aynıdır (yönteme ek — kurala dokunulmaz).

| | Değer |
|---|---|
| Günler | 7 (1–7) |
| Pencere (Wdev) | ±60 dk |
| İkili değişken | 100,552 |
| G ilk-gün-çapalı bağ | 2,643 (muafiyet: byday 1110, yeni 22) |
| Aşama-1 (byday) kayıtlı toplam | 3,390,287.4 |
| MIP-start SAF rekabetçilik | 3,389,422.3 |
| Cilalanmış SAF rekabetçilik | **3,405,039.1** (byday'e göre +14,751.6) |
| Baseline (mevcut tarife) | 3,251,527.2 |
| İyileşme (baseline'a göre) | **+153,511.9 (+4.72%)** |
| Toplam kaydırma (tekil olay bazında) | 20,620 uçuş-dk |
| **Global MIP-gap (cezalı amaç)** | **1.183%** |
| Çözüm süresi | 1809 s (sınır 1800 s) |
| A2 gece-aşan doğrulama | 1660 tur, yeni ihlal 0 |
| output/ güncellendi mi | EVET |

Not: Global MIP-gap, greedy gün-zincirinin veremediği **optimalite kanıtıdır**:
tam-hafta modelinin gerçek optimumu, raporlanan cezalı amacın en fazla gap kadar
üzerindedir. 'SAF rekabetçilik' resmi amaçtır ve cezasız ölçülür (docs §12).
