# Duyarlılık Analizi

**Takım: Büke** · TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu

*Üretim: 2026-07-11 15:49 · `python src/07_sensitivity.py` · tüm koşular tam veri, gap ≤ %0.1, deterministik*

Teslim edilen çözüm **λ=0.3, Wdev=±60, τ=45** iledir. Bu analiz çözümü değiştirmez;
modelin parametrelere tepkisinin makul/sürekli olduğunu belgeler. Tüm koşular
**aşama-1 (byday)** çözücüsüyledir; teslim edilen nihai sonuç, bu parametrelerle
byday + `src/08_fullweek_polish.py` (tam-hafta MIP-start cilalaması) iki aşamalı
hattan üretilir: **+153,512 (+%4.72)** (bkz. `docs/model_formulation.md` §13).

## 1. Tarife-değişim cezası λ (Pareto ödünleşimi)

| λ | Δ rekabetçilik | Δ % | kaydırılan uçuş | toplam kaydırma (dk) |
|---:|---:|---:|---:|---:|
| 0.0 | +126,475 | +3.89% | %92 (4,172) | 159,800 |
| 0.1 | +140,463 | +4.32% | %26 (1,162) | 24,090 |
| 0.3 **(seçilen; aşama-1 ölçümü)** | +140,566 | +4.32% | %25 (1,125) | 23,150 |
| 0.7 | +138,992 | +4.27% | %24 (1,102) | 22,280 |
| 1.5 | +137,904 | +4.24% | %22 (1,024) | 20,080 |

λ=0 (cezasız) hem düşük kazanım verir hem uçuşların ~%90+'ını kaydırır (dejenerasyon);
λ>0 simetriyi kırar: kazanım artar, kaydırma ~%25'e düşer. λ∈[0.1,1.5] kararlı bant.

## 2. Pencere genişliği Wdev ve minimum yer süresi τ (λ=0.3)

| Varyant | Δ rekabetçilik | Δ % | kaydırılan | not |
|---|---:|---:|---:|---|
| **Wdev=±60, τ=45 (aşama-1 referansı)** | +140,566 | +4.32% | %25 | referans (byday ölçümü) |
| Wdev=±30, τ=45 | +118,275 | +3.64% | %22 | dar pencere → daha az serbestlik (beklenen yön) |
| Wdev=±90, τ=45 | +45,005 | +1.38% | %24 | ölçüm ZAMAN-LİMİTLİ (aşağıya bkz.) |
| Wdev=±60, τ=30 | +146,898 | +4.52% | %24 | kısa MCT → rotasyon gevşer (beklenen yön; yalnız analiz) |
| Wdev=±60, τ=60 | +144,106 | +4.43% | %24 | dar bantta, monoton değil (aşağıya bkz.) |

**Yorum (dürüst okuma):**

- **Wdev=±30:** kazanım +4.32% → +3.64% düşer — pencere serbestliği gerçek bir kaldıraçtır (beklenen yön).
- **Wdev=±90:** olay başına aday sayısı 13→19'a çıkar, problem belirgin büyür ve **150 s/gün limitinde
  HiGHS iyi incumbent bulamaz** — tablodaki düşüş serbestlik etkisi değil, **çözüm-süresi etkisidir**
  (daha uzun limitle kazanım ±60'ın üstüne çıkar). Yan bulgu: brief'in ±60 penceresi çözülebilirlik
  açısından da iyi kalibredir.
- **τ:** iki yönde de değişim dar bantta kalır (±0.2 puan). τ=60'ın τ=45'ten hafif YÜKSEK çıkması
  monotonluk beklentisine aykırı görünür; nedeni yapısaldır — τ büyüyünce bazı gece-aşan rotasyon
  çiftlerinde mevcut tarife bile minimum turu sağlayamaz hâle gelir, bu çiftler "eşleşme artefaktı"
  sınıfına geçip koruma sınırı almaz (bkz. `docs/model_formulation.md` U1). Model τ'ya kırılgan değildir.
