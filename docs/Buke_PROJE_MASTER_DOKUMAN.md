# Büke Takımı — Proje Master Dokümanı

**TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu**  
**Problem:** Tarife Planlamalarında Rakip Odaklı Ağ Optimizasyonu  
**Takım:** Büke  
**Çözüm yığını:** Python · Pyomo · HiGHS (açık kaynak)  
**Nihai sonuç:** mevcut tarifeye göre **+%4,72** gelir-ağırlıklı rekabetçilik iyileşmesi  
**Kanıt:** global MIP-gap **%1,18** · bağımsız doğrulayıcı **tüm kontroller PASS**

> Bu doküman, yarışma brief’i, takım çözümleri, matematiksel model, kod mimarisi, sonuçlar, eksikler ve final sunumu için gereken tüm anlatımı **tek yerde** toplar. Amacı hem jüriye hem takım içi hazırlığa hizmet etmektir: *ne istendi, ne yaptık, neden böyle yaptık, nerede eksik kaldık, sonuç ne.*

---

## İçindekiler

1. [Yarışma nedir? Bizden ne istendi?](#1-yarışma-nedir-bizden-ne-istendi)
2. [İş problemi — sade ve derin anlatım](#2-iş-problemi--sade-ve-derin-anlatım)
3. [Veri seti ve girdi dosyaları](#3-veri-seti-ve-girdi-dosyaları)
4. [Genel yaklaşımımız ve tasarım felsefesi](#4-genel-yaklaşımımız-ve-tasarım-felsefesi)
5. [Neden MIP? Neden Pyomo + HiGHS?](#5-neden-mip-neden-pyomo--highs)
6. [Matematiksel model özeti](#6-matematiksel-model-özeti)
7. [Kısıtlar A–G: ne istendi, biz ne yaptık](#7-kısıtlar-ag-ne-istendi-biz-ne-yaptık)
8. [Veri hazırlama: “Minimal + Belgeli”](#8-veri-hazırlama-minimal--belgeli)
9. [Çözüm stratejisi: iki aşamalı hat](#9-çözüm-stratejisi-iki-aşamalı-hat)
10. [Yenilik 1 — Tarife-değişim cezası (λ)](#10-yenilik-1--tarife-değişim-cezası-λ)
11. [Yenilik 2 — Tam-hafta MIP-start cilalaması](#11-yenilik-2--tam-hafta-mip-start-cilalaması)
12. [Bağımsız doğrulama (çift kayıt)](#12-bağımsız-doğrulama-çift-kayıt)
13. [Sayısal sonuçlar — tam döküm](#13-sayısal-sonuçlar--tam-döküm)
14. [Değerlendirme kriterleriyle eşleme](#14-değerlendirme-kriterleriyle-eşleme)
15. [Nelerde eksik kaldık / bilinen sınırlar](#15-nelerde-eksik-kaldık--bilinen-sınırlar)
16. [Ön-denetim (preaudit) bulguları — şeffaflık](#16-ön-denetim-preaudit-bulguları--şeffaflık)
17. [Kod mimarisi ve tekrar üretilebilirlik](#17-kod-mimarisi-ve-tekrar-üretilebilirlik)
18. [Duyarlılık analizi özeti](#18-duyarlılık-analizi-özeti)
19. [Karşılaşılan 10 kritik problem ve çözümleri](#19-karşılaşılan-10-kritik-problem-ve-çözümleri)
20. [Final sunumu için anlatı iskeleti](#20-final-sunumu-için-anlatı-iskeleti)
21. [Sık jüri sorularına hazır cevaplar](#21-sık-jüri-sorularına-hazır-cevaplar)
22. [Dosya haritası ve okuma sırası](#22-dosya-haritası-ve-okuma-sırası)
23. [Sonuç ve genel değerlendirme](#23-sonuç-ve-genel-değerlendirme)

---

## 1. Yarışma nedir? Bizden ne istendi?

### 1.1 Organizasyon bağlamı

Yarışma, **TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu** altında düzenlenmiştir. Hazırlayan: **Doç. Dr. Mehmet Ertem** (Yöneylem Araştırmaları Direktörlüğü). Brief tarihi: **17 Haziran 2026**. Problem başlığı:

> **Tarife Planlamalarında Rakip Odaklı Ağ Optimizasyonu**

Katılımcılara *çözümün tamamı* verilmez. Verilenler:

- çözülmesi beklenen **iş problemi**,
- optimize edilecek **amaç fonksiyonu**,
- uyulması gereken **operasyonel kısıtlar** (gereksinim düzeyinde),
- gerçekçi **örnek veri kümesi**.

Katılımcının geliştirmesi beklenenler:

1. İş problemini **matematiksel optimizasyon modeline** dönüştürmek  
2. Modeli bir **çözücü** (Gurobi, CPLEX, HiGHS, CBC vb.) ve **Pyomo** ile çalışır hale getirmek  
3. Veriyle **çözüm üretmek** ve çıktıyı belirtilen formatta sunmak  
4. Formülasyon, varsayımlar ve sonuçları açıklayan **teknik rapor** yazmak  

Kritik not (brief §1.1):

> Kısıtlar *ne sağlanmalı* düzeyinde tanımlanmıştır. Doğrusallaştırma (büyük-M, yardımcı ikili değişkenler, koşullu aktivasyon) **bilinçli olarak verilmemiştir**. Doğru ve sıkı formülasyon kurmak yarışmanın değerlendirilen **çekirdek becerisidir**.

### 1.2 Resmi teslim listesi (Brief §5)

| # | Teslim | Bizdeki karşılık |
|---|---|---|
| 1 | Matematiksel model dokümanı (PDF) | `docs/model_formulation.pdf` |
| 2 | Çalışan kod (Python + Pyomo) | `src/01–08_*.py` + `run_all.py` |
| 3 | Çıktı dosyası (bağlantı, IST saat, yenilen rakip, amaç) | `output/*.csv` + `results_summary.*` |
| 4 | Teknik rapor (~6 sayfa, PDF) | `reports/technical_report.pdf` |
| 5 | README (kurulum, tek komut, determinizm) | `README.md` |

### 1.3 Değerlendirme kriterleri (100 puan)

| Kriter | Ağırlık | Ne ölçer |
|---|---:|---|
| 1. Model doğruluğu ve kapsam | **%30** | Tüm gerekli kısıtların geçerli/uygulanabilir modellenmesi |
| 2. Çözüm kalitesi | **%25** | Uygunluk + amaç değeri (gizli test örneği üzerinde) |
| 3. Hesaplama performansı ve ölçeklenebilirlik | **%15** | Süre, formülasyon sıkılığı, büyük örneklere ölçek |
| 4. Kod kalitesi ve yeniden üretilebilirlik | **%15** | Uçtan uca çalışırlık, temizlik, determinizm |
| 5. Teknik rapor ve dokümantasyon | **%10** | Anlaşılırlık, varsayımlar, doğrusallaştırma gerekçeleri |
| 6. Yenilikçilik ve ileri yöntemler | **%5** | Ön-işleme, ayrıştırma, sıkılaştırma, ileri katkılar |

**Eşik / diskalifiye kuralları:**

- Kod çalışmıyor veya çıktı üretmiyorsa → Kriter 2 = **0**
- Uygun (feasible) çözüm yoksa → Kriter 2 puan alamaz
- Kısıt ihlalli çözüm → ağır puan kaybı / diskalifiye
- Python + Pyomo dışı yığın → diskalifiye sebebi
- Eşit puanda sıralama: önce Çözüm Kalitesi, sonra Performans

### 1.4 Takvim (kick-off sunumu)

| Aşama | Tarih |
|---|---|
| Kayıt & Soru-Cevap | 17 Haziran – 16 Temmuz 2026 |
| Veri paylaşımı | 17 Haziran 2026 |
| Teslim son tarihi | 16 Temmuz 2026, 17:00 |
| Sunum & Final | Ağustos – Eylül 2026 |

**Bizim konumumuz:** Finale kaldık. Bu doküman final sunumu ve jüri savunması içindir.

---

## 2. İş problemi — sade ve derin anlatım

### 2.1 Bir cümlelik özet

> THY’nin İstanbul (IST) hub’ındaki **ayarlanabilir uçuş saatlerini** öyle kaydır ki; yüksek gelirli O–D pazarlarında **daha çok ve daha rekabetçi aktarma bağlantısı** oluşsun — uçak rotasyonu, hub kapasitesi, yön dengesi ve tarife düzenliliği bozulmadan.

### 2.2 Hub ekonomisi (neden IST saatleri önemli?)

Birçok yolcu A şehrinden B şehrine **direkt** uçamaz. Tipik yol:

```
Venedik (VCE)  →  İstanbul (IST)  →  Cidde (JED)
     gelen bacak         aktarma          giden bacak
```

Yolcu için önemli olan **toplam yolculuk süresi J**:

```
J = (gelen bacak blok süresi) + (IST’te bekleme / boşluk) + (giden bacak blok süresi)
```

Aynı yolcuyu **rakip havayolları** da Frankfurt, Doha, Dubai gibi başka hub’lar üzerinden taşır. THY’nin rekabet kozu: IST’teki bağlantı boşluğunu 60–300 dk aralığında tutup **toplam J’yi rakibinkinden kısa** yapmak.

THY’nin elindeki kaldıraç: **IST kalkış/varış saatleri**. Blok süreleri (uçuş süreleri) sabittir; değişen şey boşluktur.

### 2.3 Ne “iyi bağlantı”dır?

Bir aktarma bağlantısı π = (gelen uçuş, giden uçuş) ancak şu aralıkta sunulabilir:

```
L ≤ bağlantı boşluğu ≤ U
Standard: L = 60 dk, U = 300 dk
```

- 60 dk’dan kısa → bagaj/yolcu yetişemez (Minimum Connection Time)
- 300 dk’dan uzun → yolcu için cazip değil (çok bekler)

### 2.4 Neye karar veriyoruz? (fiziksel karar)

Brief’in netleştirdiği fiziksel kararlar:

1. **Ayarlanabilir uçuşların IST kalkış/varış saatleri** (temel karar)
2. **Hangi aktarma bağlantılarının pazara sunulacağı** (dolaylı — saatlerden türetilir)
3. **Yenilen rakip sayısı ve güncellenen sıralama** (dolaylı — J karşılaştırmasından türetilir)

Bizim modelde temel karar değişkeni: her ayarlanabilir uçuş örneğinin IST olayının **10 dakikalık kova indeksi**.

### 2.5 Amaç neyi ölçer?

```
max  Σ_{o≠d}  ρ_od · ( bağlantı-sayısı ödülü  +  sıralama ödülü )
```

- **ρ_od**: O–D pazarının gelir potansiyeli (talep × fiyat benzeri önem). Yüksek ρ → daha çok optimizasyon eforu.
- **Bağlantı-sayısı ödülü (azalan getiri):** ilk sunulan bağlantı 1 puan, sonrakiler yarı yarıya: 1, ½, ¼, …
- **Sıralama ödülü:** rakibi toplam J’de geçmek → sıralama iyileşir → lookup tablosundan ödül.

Yani amaç “daha çok uçuş kaydır” değil; **gelir-ağırlıklı rekabetçilik faydasını** büyütmektir.

---

## 3. Veri seti ve girdi dosyaları

### 3.1 Yarışmanın verdiği dosyalar

Konum: `yarisma-belgeleri/TEKNOFEST_tarife_input_files/` (çalışan kopya: `data/`)

| Dosya | Rol |
|---|---|
| `O&D Rakip Bağlantı Tablosu_updated.xlsx` | TK + rakip itinerary’ler, süreler, boşluklar, ElapsedTime1/2 |
| `Yolcu Verisi_masked.xlsx` | O–D gelir potansiyeli ρ |
| `change_ranking_input.xlsx` | Sıralama ödülü lookup (N, b, s → Wʳ) |
| `Flight Pairs.xlsx` | Aynı uçağın gidiş–dönüş rotasyon eşleri |
| `TEKNOFEST_Yarismasi Brief.pdf` | Resmi problem tanımı |
| `Teknofest_Yarisma_sunum.pdf` | Kick-off sunumu |
| `README_full_data_input_dosyalari.docx` | Veri sözlüğü |

### 3.2 Ham veri ölçeği (transform log’dan)

| Büyüklük | Değer |
|---|---|
| Bağlantı tablosu satırı | 57 317 |
| Yolcu (ρ) satırı | 8 075 |
| Ranking lookup satırı | 22 140 |
| Flight pair satırı | 1 562 |
| Yönlü O–D pazar | 1 408 (ρ eksik 48 → dışlandı) |
| TK aday bağlantı (temizlik sonrası) | 7 693 |
| Operasyon günü | 7 |
| Ayarlanabilir uçuş hareketi (nihai) | 4 554 |
| Model ikili değişken (tam hafta) | ~100 552 |

### 3.3 Kritik veri gerçeği: güncellenmiş ElapsedTime

Organizatorün `_updated.xlsx` dosyası bacak sürelerini `ElapsedTime1/2` ile verir. Bu sayede:

```
J = E1 + boşluk + E2     (KESİN; 24 saat sarma belirsizliği yok)
```

Eski şemada Gate-to-Gate + de-wrap 154 satırı yanlış bırakıyordu (29 TK + 125 rakip; ultra-uzun hatlar: EZE–PEK, BOG–PEK, VCE–SYD vb.). Güncel veride 24 saati **gerçekten** aşan 495 itinerary vardır ve doğru işlenir.

### 3.4 Sezon uyumsuzluğu (önemli sınır)

- `Flight Pairs.xlsx` → **W26 (Kış 2026)** sezonuna ait
- Tarife / bağlantı verisi → **Ağustos 2025** civarı

Sonuç: 512 pair’den yalnızca 291’i kullanılabilir gidiş–dönüş üretir; **221 uçuşta A2 rotasyon kısıtı kurulamaz**. Bu veri sınırıdır, model hatası değildir — preaudit’te belgelenmiştir.

---

## 4. Genel yaklaşımımız ve tasarım felsefesi

### 4.1 Üç ilke

| İlke | Anlamı | Pratik yansıma |
|---|---|---|
| **Matematiksel doğruluk** | Brief’i “yaklaşık” değil birebir modelle | A–G kısıtları doğrusal MIP; A2 brief-exact |
| **Minimal + belgeli veri** | Değer uydurma; belirsizliği ihtiyatla ele al | ρ yok → dışla; partner yok → sabit; her dönüşüm log’da |
| **Kanıtlanabilirlik** | “İyiyiz” demek yetmez; ölç, doğrula, raporla | Bağımsız doğrulayıcı, gap kanıtı, duyarlılık, preaudit |

### 4.2 Çözüm hattı (uçtan uca)

```
data/*.xlsx
    │
    ▼
01_data_health_check.py     → reports/data_health_report.md
    │
    ▼
02_data_prep.py             → derived/*.csv + transform_log.md
    │
    ▼
03_model.py byday           → aşama-1 (güne göre, λ=0.3)  ~1.5 dk
    │
    ▼
08_fullweek_polish.py       → aşama-2 (tam hafta MIP-start) ≤30 dk
    │
    ▼
05_validate_solution.py     → validation_report.md  (FAIL → koşu DURUR)
    │
    ▼
06_make_figures.py          → docs/figures/*.png
07_sensitivity.py           → (opsiyonel) sensitivity_analysis.md
04_export_docs.py           → .md → .docx → .pdf
    │
    ▼
output/  +  reports/  +  docs/
```

Tek komut:

```bash
python run_all.py
```

### 4.3 Tasarım kararları (D1–D6) — neden böyle?

| # | Karar | Gerekçe |
|---|---|---|
| D1 | Zaman **10 dk kova** ayrıklaştırması | F zaten 10 dk ister; pencere tamsayı olur; ε sorunu biter; M sıkılaşır |
| D2 | J = legsum + boşluk; legsum sabit | Bloklar uçuş süresidir, değişmez; karar yalnız IST saati |
| D3 | Ayarlanabilir uçuşlara **±60 dk pencere (Wdev)** | Brief “sınır yok” der ama izin verir; aksi 144 kova × uçuş patlar |
| D4 | N_od **taşıyıcı bazlı** (itinerary değil) | Taşıyıcı N∈[1,17]≤40 → lookup tam kapsar; itinerary 73 pazarda 40’ı aşar |
| D5 | Ön-işleme ile eleme | Brief md.7 önerisi; model boyutu ve M ihtiyacı düşer |
| D6 | ρ yok → dışla; partner yok → sabit | Uydurma yok; ihtiyatlı dışlama |

---

## 5. Neden MIP? Neden Pyomo + HiGHS?

### 5.1 Neden Karışık Tamsayılı Programlama (MIP)?

Problem yapısı MIP’e birebir oturur:

- **Kesikli kararlar:** hangi kova, bağlantı sunuluyor mu (0/1), rakip yenildi mi (0/1)
- **Doğrusal ilişkiler:** saat farkı = boşluk; kapasite toplamı; denge eşitsizlikleri
- **Kanıt ihtiyacı:** sezgisel “iyi görünüyor” yetmez; jüri gap ve fizibilite ister
- **Kısıt sertliği:** rotasyon, kapasite, denge — ihlal diskalifiye

Sezgisel / meta-sezgisel (GA, SA, RL) tek başına:

- fizibilite garantisi vermez,
- global gap kanıtı üretmez,
- brief’in “doğru ve sıkı formülasyon” çekirdeğini karşılamaz.

**Bizim seçim:** saf MIP (sezgisel ana motor değil). Ölçek için *ayrıştırma + MIP-start* kullanıldı; bu da yine MIP çerçevesindedir.

### 5.2 Neden Pyomo?

- Brief **zorunlu** kılar (Python + Pyomo; aksi diskalifiye)
- Cebirsel model → kod okunabilirliği
- Çözücü bağımsız arayüz (HiGHS / Gurobi / CPLEX aynı model)

### 5.3 Neden HiGHS (Gurobi/CPLEX değil)?

| Ölçüt | HiGHS | Ticari (Gurobi/CPLEX) |
|---|---|---|
| Lisans | Açık kaynak, ücretsiz | Lisans gerekir |
| Tekrar üretilebilirlik | Her jüri makinesinde çalışır | Lisans yoksa koşmaz |
| Brief uyumu | Açıkça listelenmiş | Listelenmiş ama bağımlılık riski |
| Performans | Yeterli (bizde çalıştı) | Genelde daha hızlı |
| Determinizm | threads=1, seed=0 ile sağlandı | Benzer |

**Karar:** lisans riski ve jüri koşusu için **HiGHS**. Performans açığını *formülasyon sıkılığı + ayrıştırma + MIP-start* ile kapattık. E2 gibi zor kısıtlarda ticari çözücü ileri adımdır — bunu §15’te açıkça söylüyoruz.

### 5.4 Neden “yapay zekâ” yarışmasında klasik OR?

Yarışma adı “YZ destekli” olsa da brief’in çekirdeği **yöneylem araştırması / matematiksel optimizasyondur**. YZ burada:

- problem çerçevesi ve veri ürünü olarak,
- ileride talep tahmini / öğrenilmiş parametre (geliştirme yol haritasında),
- değil ana tarife motoru olarak konumlanır.

Jüriye net mesaj: **doğru araç doğru işe** — bu problemde kanıtlı optimuma en yakın yol MIP’tir.

---

## 6. Matematiksel model özeti

Tam formülasyon: `docs/model_formulation.md` / `.pdf`. Burada anlatısal özet.

### 6.1 Kümeler (seçme)

| Sembol | Anlam |
|---|---|
| 𝒮 | Dış istasyonlar |
| ℋ | Operasyon günleri (veriden; 7’ye hardcode yok) |
| ℳ | ρ tanımlı yönlü O–D pazarları |
| ℛ | Uçuş örnekleri r=(f,h) |
| ℛᵛᵃʳ / ℛᶠⁱˣ | Ayarlanabilir / sabit |
| Π | Aday aktarma bağlantıları |
| 𝒦_{od,h} | Rakip taşıyıcılar |
| 𝒫 | Rotasyon çiftleri |

### 6.2 Temel karar değişkenleri

| Değişken | Tip | Anlam |
|---|---|---|
| x_{r,t} | ikili | Örnek r, kova t’ye atandı |
| θ_r | tamsayı (türev) | IST kova zamanı |
| y_π | ikili | Bağlantı π sunuluyor mu |
| z_{od,h,j} | ikili | j. azalan-getiri slotu dolu mu |
| w_{π,k}, β_{od,h,k}, γ_{od,h,b} | ikili | Yenme ve sıralama seçicileri |

### 6.3 Amaç (özet)

```
max  Σ ρ_od · Σ_h [ Σ_j Wᶜ_j · z_{od,h,j}  +  Σ_b Wʳ(N,b_od,N−b)·γ_{od,h,b} ]
     − λ · Σ_r |θ_r − cur_r|
```

- Birinci satır: brief’in resmi rekabetçilik amacı  
- İkinci satır: bizim **operasyonel kesinti uzantımız** (λ=0.3)  
- Raporlanan OPTIMIZE / İYİLEŞME daima **cezasız** (saf rekabetçilik) ölçülür

### 6.4 Doğrusallaştırma vurguları (jüriye anlatılacak sıkılık)

1. **Yön-yerel büyük-M** — global gevşek M yok  
2. **Yenme ön-işleme üç durumu** — çoğu (π,k) için M hiç kurulmaz (`w=y` veya değişken yok)  
3. **Azalan getiri = monoton slot** — LP gevşetmesini sıkar  
4. **Ceza terimi büyük-M’siz** — A1 tekil atama sayesinde `\|θ−cur\|=Σ|t−cur|·x`  
5. **E2 min-seçimi McCormick’siz** (küçük ölçekte açık; tam ölçekte kapalı — §15)

---

## 7. Kısıtlar A–G: ne istendi, biz ne yaptık

### (A) Zaman atama ve uçak rotasyonu

| Brief | Bizim uygulama |
|---|---|
| Her ayarlanabilir olay alt/üst sınırda | ±60 dk pencere, 10 dk kova, Σ_t x=1 |
| Dönüş varışı ≥ gidiş kalkış + (T_OB+τ+T_IB) | **Brief-exact A2**; bloklar ElapsedTime’dan; τ=45 |
| — | Gece-aşan turlar: slack/2 statik bölüşüm + gerçek eksende doğrulama |

**Kanıt:** 1 709 tur, **yeni ihlal 0**.

### (B) Bağlantı uygunluğu

| Brief | Bizim uygulama |
|---|---|
| Boşluk [60,300] ise sunulabilir | B1: y=1 ⇒ g∈[ℓ,u] |
| Seçim ile boşluk tutarlı bağlansın | g = θ_out − θ_in türetilir |
| Uygun olanlar zorunlu sunulsun (B2 ruhu) | **B2 varsayılan KAPALI** — sert zorlanınca infeasible (E1 çatışması); amaç zaten %90+ sunuyor |

### (C) Azalan getiri / monoton slot

```
Σ y = Σ z
z_j ≥ z_{j+1}
Wᶜ_j = (1/2)^{j−1}
```

Tam uygulandı; bağımsız doğrulayıcıda C ödülü **PASS**.

### (D) Rakip yenme ve sıralama

```
J_π ≤ Tᶜᵒᵐᵖ  ⇒  rakip yenilebilir
β_k = 1  ⇒  en az bir yenen sunulu bağlantı
s = N − yenilen  →  Wʳ lookup
```

Ön-işleme: G_{πk}=Tᶜᵒᵐᵖ−legsum eşiğine göre üç durum (asla / hep / koşullu).

**b_od düzeltmesi:** taban sıralama baseline ile iç-tutarlı; mevcut tarife her pazarda lookup köşegenine (nötr) oturur. Eski `faster+1` kuralı baseline’a haksız ödül veriyordu — düzeltildi.

### (E) Yönsel denge

| Alt | Brief | Biz |
|---|---|---|
| E1 | \|n_od−n_do\| ≤ α(n_od+n_do), α=0.20 | **Açık, tam ölçek** — 2 001 çift, 0 ihlal |
| E2 | İki yön aktifken \|Jmin_od−Jmin_do\| ≤ Γ=30 dk | **Tam ölçekte KAPALI** (kanıtlı; §15) |

### (F) IST hub kapasitesi

- 10 dk kova  
- Kalkış cap **10**, varış cap **15** (brief gerçek değerleri)  
- Sabit uçuşlar düşülür; **tüm TK uçuşları** (amaç dışı ρ’suz pazarlar dahil) sabit doluluk sayılır  
- En dolu kova: kalkış 10/10, varış 15/15 — aşan kova **0**

### (G) Tarife düzenliliği

- Aynı uçuş no, günler arası en fazla **Xdev=15 dk** sapabilir  
- Saat-içi bant + ilk-gün çapası  
- Rotasyon güvenliği çatışırsa **belgeli muafiyet** (`g_band_exemptions.csv`)  
- G-gevşetilen gün: **0**  
- Doğrulayıcı: 2 644 bağ, bant dışı 0

### (H) Slot pencereleri

Sunumda var, brief A–G listesinde **yok**. Veride düzenlenmiş havalimanı penceresi yok → **dahil edilmedi**. Veri gelirse 𝒯_r daraltılarak eklenir.

---

## 8. Veri hazırlama: “Minimal + Belgeli”

### 8.1 Politika

- Orijinal Excel’lere **asla** yazılmaz  
- Değer **uydurulmaz**  
- Her dönüşüm `derived/transform_log.md`’de  
- CFG ile geri alınabilir (`02_data_prep.py`)

### 8.2 Yapılan dönüşümler

1. **J kesin hesabı** (ElapsedTime1/2)  
2. **Hafta normalizasyonu:** aynı operasyon gününün farklı takvim haftası kopyaları tek kanonik haftaya (5 604 → 5 474 olay)  
3. **Aday tekilleştirme:** özdeş satırlar (7 850 → 7 693) — aksi **çift ödül**  
4. **ρ eksik 48 pazar dışlama**  
5. **Partnersiz 176 TK uçuşu sabit**  
6. **N_od taşıyıcı bazlı**  
7. Pencere-dışı aday elemesi, kapasitesiz kova elemesi  

### 8.3 Bu adım neden kritik?

Bağımsız doğrulayıcı geliştirmede şunları yakaladı:

- F kapsam eksiği (amaç dışı uçuşlar kovayı dolduruyordu)  
- Hafta-kopyası tutarsız saat (aynı fiziksel uçuşa iki saat)  
- Çift ödül sayımı  

Üçü de veri/model katmanında düzeltildi. **“Çalışan kod” yetmez; denetlenebilir veri hattı şart.**

---

## 9. Çözüm stratejisi: iki aşamalı hat

### 9.1 Sorun

Tek parça 7-gün MIP (~100k ikili) HiGHS’te **soğuk başlangıçla 600 s’de incumbent bile bulamıyor**.

### 9.2 Aşama-1 — Güne göre ayrıştırma (`03_model.py byday`)

Gözlem: günleri bağlayan **tek** kısıt G’dir. E1/E2/A2/F gün-içidir.

```
Her gün h = 1..7:
  ayrı MIP (~17k ikili)
  G: önceki günlerin saat-içi bandı ± Xdev
  bant aşırı kısıtlarsa → hedefli muafiyet / gevşetme
```

- Süre: **~1,5 dk**  
- Gün-içi gap: **≤ %0,1**  
- G-gevşetilen gün: **0**  
- λ=0.3 ile aşama-1 saf rekabetçilik: **3 390 287** (+%4,27 baseline’a)

### 9.3 Aşama-2 — Tam-hafta cilalama (`08_fullweek_polish.py`)

```
Tam hafta tek MIP (100 552 ikili)
+ aşama-1 çözümü MIP-start (highspy setSolution)
+ G: doğrulayıcıyla birebir “ilk-gün çapalı ±Xdev”
+ ≤ 1800 s branch-and-bound
```

- Nihai amaç: **3 405 039**  
- Aşama-1’e göre ek: **+14 752**  
- Baseline’a göre: **+153 512 (+%4,72)**  
- **Global MIP-gap: %1,18**

### 9.4 Çift bariyer güvence

08, `output/`u yalnız şu iki koşulla günceller:

1. Aşama-1’e göre **kanıtlı iyileşme** var  
2. Gece-aşan A2 denetimi temiz  

Aksi hâlde deterministik aşama-1 çıktısı kalır. `run_all.py` doğrulayıcı FAIL verirse **durur**.

---

## 10. Yenilik 1 — Tarife-değişim cezası (λ)

### 10.1 Motivasyon

Brief amacı bir uçuşu yerinde tutmakla kaydırmak arasında **kayıtsızdır**. Cezasız çözüm:

- uçuşların **~%92’sini** kaydırır (ort. ~38 dk),
- operasyonel olarak gerçekçi değildir,
- binlerce eşit-amaçlı “bedava kaydırma” simetrisi LP gevşetmesini bozar → çözücü kötü incumbent bulur.

### 10.2 Formülasyon (ek değişken / büyük-M YOK)

```
|θ_r − cur_r| = Σ_t |t − cur_r| · x_{r,t}
max  (brief amacı)  −  λ · Σ_r |θ_r − cur_r|
```

λ birimi: **amaç-puanı / uçuş-dk**.

### 10.3 λ taraması (aşama-1 ölçümü)

| λ | Δ rekabetçilik | Kaydırılan uçuş | Toplam kaydırma |
|---:|---:|---:|---:|
| 0.0 | +%3,89 | %92 | 159 800 dk |
| 0.1 | +%4,32 | %26 | 24 090 dk |
| **0.3 (seçilen)** | **+%4,32** | **%25** | **23 150 dk** |
| 0.7 | +%4,27 | %24 | 22 280 dk |
| 1.5 | +%4,24 | %22 | 20 080 dk |

### 10.4 İki yönlü kazanç (jüri cümlesi)

> λ>0 yalnız kaydırmayı düşürmez; **dejenerasyonu kırarak rekabetçiliği de artırır** (+%3,89 → +%4,32) — üstelik kaydırma %92’den %25’e inerken.

λ=0.3 **knee** noktasıdır: en yüksek kazanım + daha az kaydırma.

Nihai çözümde (cilalama sonrası): kaydırma **%23**, ort. **19 dk**, 1 067 / 4 554 hareket.

---

## 11. Yenilik 2 — Tam-hafta MIP-start cilalaması

### 11.1 Neden gerekli?

Aşama-1 hızlıdır ama:

1. G’yi greedy zincirle kurar → günler-arası koordinasyon tam değil  
2. Gün-bazlı gap’ler **küresel optimalite kanıtı** vermez  

### 11.2 Ne kazandırdı?

| Metrik | Aşama-1 | Aşama-2 (nihai) |
|---|---:|---:|
| Saf rekabetçilik | 3 390 287 | **3 405 039** |
| Baseline’a Δ | +%4,27 | **+%4,72** |
| Global gap | yok | **%1,18** |

Bu, “biz iyi sezgisel yaptık” değil; **kanıtlı yakın-optimum** iddiasıdır.

---

## 12. Bağımsız doğrulama (çift kayıt)

### 12.1 Fikir

Çözümü üreten MIP koduna güvenmeden, yalnız `derived/` veri katmanından **yeniden hesapla**. Muhasebedeki çift kayıt gibi.

### 12.2 Kontroller (18 + bilgi notları) — hepsi PASS

| Kontrol | Kapsam | Sonuç |
|---|---|---|
| A1 ızgara / pencere / aritmetik | 4 554 hareket | PASS |
| F kova kapasitesi | 7 gün × kovalar | PASS (aşan 0) |
| A2 gerçek eksen | 1 709 tur | PASS (yeni ihlal 0) |
| A2 aynı-gün çapası | 915 tur | PASS |
| G bant | 2 644 bağ | PASS |
| B1 boşluk / J / saat | 6 966 bağlantı | PASS |
| C aktarma ödülü | 4 660 pazar-gün | PASS |
| D yenme / sıralama | 4 660 | PASS |
| E1 yön dengesi | 2 001 çift | PASS |
| Amaç OPT | 3 405 039 = yeniden hesap | PASS |
| BASELINE | 3 251 527 = yeniden hesap | PASS |

Dosya: `reports/validation_report.md`.

### 12.3 Jüriye mesaj

> Çıktılarımızı bizim çözücümüze güvenmeden tek komutla denetleyebilirsiniz:  
> `python src/05_validate_solution.py`

---

## 13. Sayısal sonuçlar — tam döküm

### 13.1 Nihai özet tablo

| | Değer |
|---|---|
| **OPTIMIZE (saf rekabetçilik)** | **3 405 039** |
| BASELINE (mevcut tarife) | 3 251 527 |
| **İYİLEŞME** | **+153 512 (+%4,72)** |
| Kaydırılan hareket | 1 067 / 4 554 (**%23**) |
| Toplam kaydırma | 20 640 uçuş-dk (ort. **19 dk**) |
| λ | 0.3 |
| Global MIP-gap | **%1,18** |
| G-gevşetilen gün | **0** |
| A2 yeni ihlal | **0** |
| Doğrulayıcı | **TÜM PASS** |
| Sunulan bağlantı | 6 966 |

### 13.2 Gün kırılımı

| Gün | Pazar-gün | Aday | OPT | Baseline | Δ | Kaydırılan | Kaydırma-dk |
|----:|----:|----:|----:|----:|----:|----:|----:|
| 1 | 670 | 1077 | 488 005 | 465 686 | +22 318 | 166 | 3 170 |
| 2 | 655 | 1062 | 465 912 | 443 873 | +22 038 | 161 | 3 270 |
| 3 | 658 | 1079 | 490 860 | 470 624 | +20 237 | 140 | 2 790 |
| 4 | 661 | 1081 | 482 902 | 459 225 | +23 677 | 155 | 3 110 |
| 5 | 667 | 1076 | 495 630 | 472 018 | +23 612 | 139 | 2 610 |
| 6 | 672 | 1094 | 486 872 | 467 761 | +19 111 | 153 | 2 810 |
| 7 | 677 | 1108 | 494 858 | 472 339 | +22 519 | 153 | 2 880 |

İyileşme yedi güne **dengeli** dağılır (+19k … +24k) — tek güne yığılma yok.

### 13.3 Çıktı dosyaları (teslim #3)

| Dosya | İçerik |
|---|---|
| `optimized_schedule.csv` | Uçuş × eski IST → yeni IST |
| `market_results.csv` | O–D/gün: sunulan, yenilen rakip, sıralama, ρ-katkı |
| `selected_connections.csv` | Her seçilen bağlantı (boşluk, J, yendiği rakip) |
| `g_band_exemptions.csv` | G muafiyetleri (şeffaflık) |
| `results_summary.md/.pdf` | Toplam amaç ve özet |

### 13.4 Figürler

`docs/figures/` altında:

1. `fig1_gunluk_iyilesme.png` — günlük Δ  
2. `fig2_kaydirma_dagilimi.png` — kaydırma dakika dağılımı  
3. `fig3_lambda_pareto.png` — λ Pareto  
4. `fig4_siralama_iyilesme.png` — sıralama iyileşmesi  

---

## 14. Değerlendirme kriterleriyle eşleme

| Kriter | Ağırlık | Bu teslimde ne var? | Kanıt dosyası |
|---|---:|---|---|
| 1. Model doğruluğu | %30 | A–G doğrusal MIP; A2 brief-exact; F gerçek 10/15 tüm TK; B2/E2 kanıtlı gevşetme | `model_formulation.md` §5, §10 |
| 2. Çözüm kalitesi | %25 | +%4,72; feasible; doğrulayıcı PASS; gizli teste genellenebilir kod | `results_summary`, `validation_report` |
| 3. Performans | %15 | ~1,5 dk aşama-1 + ≤30 dk cilalama; yön-yerel M; ön-işleme; gap %1,18 | `fullweek_polish.md` |
| 4. Kod kalitesi | %15 | Modüler; `run_all.py`; deterministik; şema doğrulama; hardcode yok | `README`, `src/` |
| 5. Rapor | %10 | Teknik rapor + model dokümanı + doğrulama + duyarlılık + bu master | `reports/`, `docs/` |
| 6. Yenilik | %5 | λ cezası (M’siz); tam-hafta MIP-start; hafta-norm; çift-kayıt doğrulama; duyarlılık | §10–§12, §18 |

### Gizli test sağlamlığı

- Gün sayısı / pazar / rakip **veriden türetilir** (7’ye sabit değil)  
- Eksik sütun → okunabilir hata  
- Tek gün hatası tüm koşuyu çökertmez  
- HiGHS `threads=1, random_seed=0`  
- Doğrulama koşuya gömülü  

---

## 15. Nelerde eksik kaldık / bilinen sınırlar

Şeffaflık finalde güçtür. Eksikleri **gizlemiyoruz**; kanıtla gerekçelendiriyoruz.

### 15.1 E2 (en iyi süre yön dengesi) — tam ölçekte kapalı

**İki bağımsız kanıt:**

1. **Çözücü:** E2’nin min-seçimi büyük-M’i LP’yi bozar; tek gün (~18k ikili) bile 150 s’de incumbent bulamaz. E2 kapalı aynı gün saniyelerde çözülür.  
2. **Veri:** E2-kapalı optimalde aktif yön-çiftlerinin **%76’sı (1500/1972)** Γ=30 dk’yı ihlal eder; farklar **465 dk’ya** varır. Γ=30 bu veride yapısal olarak ulaşılamaz.

**Sonuç:** Sert E2 ya infeasible yapar ya +%4,72’yi çökertir. Küçük örnekte E2 açık ve doğrulanmış. İleri adım: soft-E2 veya ticari çözücü.

### 15.2 B2 (zorunlu sunum) — varsayılan kapalı

B2 × E1 çatışması: asimetrik pazarlarda her uygun bağlantıyı sunmak yön dengesini bozar.

Kanıt (gerçek 10/15 F altında): B2 açıkken gün 1/2 **saniyelerde infeasible**.

Etki küçük: amaç sunmayı ödüllendirdiğinden pencereye erişebilir adayların **%90+’ı zaten sunuluyor** (aşama-1: 6 877/7 577 = %90,8; nihai: 6 966). Bilinçli bastırılan ~%3,5.

### 15.3 Rotasyon kapsamı (veri sezon uyumsuzluğu)

Flight Pairs W26, tarife Ağustos 2025 → 221 uçuşta A2 kurulamıyor; kaydırılan hareketlerin ~%23,2’si bu grupta. Kök neden veri, model değil.

### 15.4 G muafiyetleri

1 132 (gün, uçuş, rol) belgeli muafiyet — rotasyon güvenliği > gün-arası düzenlilik önceliği. Muafiyet dışı tüm bağlar ±15 dk’da. G tam-gün gevşetme: **0 gün**.

### 15.5 b_od konvansiyonu

Model baseline ile **iç-tutarlı**; 0/1-indeks kesin organizatör tanımı teyit bekliyor. Hangi konvansiyon seçilirse seçilsin iç tutarlılık korunur.

### 15.6 Kısıt H

Brief A–G’de yok; veri yok → modelde yok.

### 15.7 Izgara etkisi (preaudit dürüstlüğü)

Baseline boşlukları ham dakika, model 10 dk ızgara ile değerlendirir. Raporlanan +%4,72’nin bir kısmı ayrıklaştırmadan gelir:

- Izgara-tutarlı karşılaştırmada iyileşme yaklaşık **+%4,03**
- Kazancın ~%14,1’i (21 597 puan) ayrıklaştırma payı

Bunu gizliyoruz: finalde **açıkça söylüyoruz**. Yine de +%4 civarı gerçek iyileşme anlamlıdır.

---

## 16. Ön-denetim (preaudit) bulguları — şeffaflık

`preaudit/` altında çözüm, üreten koddan bağımsız yeniden ölçülür:

| Betik | Konu |
|---|---|
| `01_iddia_dogrulama.py` | Ana iddiaların sayısal teyidi |
| `02_izgara_ve_rotasyon_olcumu.py` | Izgara payı + rotasyon kapsamı |
| `03_kapasite_E1_baglanti_olcumu.py` | F, E1, bağlantı sunum oranları |
| `04_urun_kalitesi_ve_marjlar.py` | Ürün kalitesi, rakip yenme marjları |

**En önemli iki bulgu (README’de de yazılı):**

1. Izgara tutarlı iyileşme **+%4,03** (raporlanan +%4,72’nin ayrık payı ayrıştırılmış)  
2. A2 kapsamı pair sezon uyumsuzluğu nedeniyle tam değil (221 uçuş)

Bu, “kendi çözümümüzü de eleştiriyoruz” mesajıdır — jüri güveni için değerlidir.

---

## 17. Kod mimarisi ve tekrar üretilebilirlik

### 17.1 Modüller

| Dosya | Görev |
|---|---|
| `01_data_health_check.py` | Veri sağlık |
| `02_data_prep.py` | Altın veri katmanı |
| `03_model.py` | MIP (küçük / byday / sweep) |
| `04_export_docs.py` | md→docx→pdf |
| `05_validate_solution.py` | Bağımsız doğrulayıcı |
| `06_make_figures.py` | Figürler |
| `07_sensitivity.py` | λ / Wdev / τ taraması |
| `08_fullweek_polish.py` | Tam-hafta cilalama |
| `run_all.py` | Uçtan uca orkestrasyon |

### 17.2 Ortam

- Python 3.13 (doğrulanmış), Windows 11  
- `pip install -r requirements.txt`  
- pyomo, highspy, pandas, numpy, pypandoc  

### 17.3 Determinizm

- HiGHS: `threads=1`, `random_seed=0`  
- Aşama-1: aynı girdi → **byte-byte aynı** çıktı (doğrulandı)  
- Aşama-2: süre sınırlı (1800 s) → donanıma göre incumbent teoride değişebilir; her koşu doğrulayıcıdan geçer; iyileşme yoksa aşama-1 kalır  

### 17.4 Tek komut

```bash
python run_all.py                 # ~35–40 dk
python run_all.py --with-sensitivity
```

---

## 18. Duyarlılık analizi özeti

Dosya: `reports/sensitivity_analysis.md`. Teslim çözümü değiştirmez; parametre tepkisini belgeler.

### 18.1 λ

λ∈[0.1, 1.5] dar bantta kararlı; 0.3 knee.

### 18.2 Wdev ve τ (λ=0.3, aşama-1)

| Varyant | Δ % | Yorum |
|---|---:|---|
| Wdev=±60, τ=45 (referans) | +4,32 | teslim |
| Wdev=±30, τ=45 | +3,64 | dar pencere → beklenen düşüş |
| Wdev=±90, τ=45 | +1,38* | *süre limitli; serbestlik değil performans etkisi |
| Wdev=±60, τ=30 | +4,52 | gevşek MCT |
| Wdev=±60, τ=60 | +4,43 | dar bant; yapısal artefakt |

**Çıkarım:** ±60 hem brief kalibrasyonu hem çözülebilirlik açısından iyi. Model τ’ya kırılgan değil.

---

## 19. Karşılaşılan 10 kritik problem ve çözümleri

Final anlatısında “süreç olgunluğu”nu gösteren iskelet:

| # | Problem | Çözüm |
|---|---|---|
| 1 | 7-gün monolitik MIP çözülmüyor | Güne göre ayrıştırma |
| 2 | Ayrıştırma küresel gap vermiyor | Tam-hafta MIP-start cilalama |
| 3 | %92 anlamsız kaydırma | λ tarife-değişim cezası |
| 4 | Cezasız dejenerasyon (düşük amaç) | λ simetri kırıcı → daha iyi amaç |
| 5 | J 24sa sarma belirsizliği | ElapsedTime kesin J |
| 6 | Hafta kopyası / çift ödül | Normalizasyon + tekilleştirme |
| 7 | F evren açığı (ρ’suz uçuşlar) | Tüm TK sabit doluluk; doğrulayıcı yakaladı |
| 8 | A2 evren-ankoru ihlali | full_role_time ile sabit taraf ankoru |
| 9 | B2 × E1 infeasible | B2 kapalı; etki %3,5 |
| 10 | E2 çözücü + veri imkânsız | E2 kapalı; iki kanıt belgelendi |

Her satır bir “biz düşündük, ölçtük, düzelttik” hikâyesidir.

---

## 20. Final sunumu için anlatı iskeleti

### 20.1 Önerilen akış (10–12 dk)

1. **Hook (30 sn):** “IST saatlerini %23 uçuşta ortalama 19 dk kaydırarak, tüm operasyon kurallarına uyarak rekabetçiliği +%4,72 artırdık — global gap %1,18, bağımsız doğrulayıcı tam PASS.”  
2. **Problem (1 dk):** Hub, J, rakip, ρ.  
3. **Yaklaşım (1,5 dk):** MIP, neden HiGHS, iki aşama.  
4. **Model (2 dk):** Amaç + A–G tek slayt; sıkı doğrusallaştırma vurgusu.  
5. **Yenilikler (2 dk):** λ iki yönlü kazanç + tam-hafta gap kanıtı.  
6. **Sonuçlar (2 dk):** tablo, gün grafiği, kaydırma dağılımı.  
7. **Doğrulama & şeffaflık (1,5 dk):** çift kayıt; E2/B2/ızgara dürüstlüğü.  
8. **Kapanış (30 sn):** kriter eşlemesi + gizli teste genelleme.  

### 20.2 Söylenmemesi gerekenler

- “E2’yi unuttuk” → hayır: **kanıtla kapattık**  
- “Her şeyi optimal çözdük” → hayır: **gap %1,18**  
- “+%4,72 tamamen operasyonel” → ızgara payını da söyle  

### 20.3 Görsel öncelik

1. Günlük iyileşme (fig1)  
2. λ Pareto (fig3)  
3. Kaydırma dağılımı (fig2)  
4. Tek özet skor kartı (+%4,72 / %23 kaydırma / gap %1,18 / PASS)

---

## 21. Sık jüri sorularına hazır cevaplar

**S: Neden Gurobi kullanmadınız?**  
C: Brief açık kaynak çözücülere izin veriyor. HiGHS lisans riski olmadan jüride koşar. Performansı formülasyon + iki aşama ile yönettik; gap %1,18.

**S: E2 neden yok? Brief’te var.**  
C: İki kanıt: (1) açıkken incumbent yok; (2) veride %76 çift Γ’yı yapısal aşar. Sert uygulama infeasible veya kazanımı yok eder. Küçük ölçekte kurulu ve doğrulanmış. Soft-E2 yol haritasında.

**S: B2 zorunlu sunum?**  
C: E1 ile çatışıyor; açıkken günler infeasible. Amaç zaten %90+ sunuyor; bilinçli bastırma ~%3,5.

**S: Bu sezgisel mi?**  
C: Hayır. Ana model MIP. Ayrıştırma ve MIP-start ölçek tekniği; amaç/kısıt aynı. Global gap kanıtı var.

**S: +%4,72 abartılı mı?**  
C: Bağımsız doğrulayıcı OPT ve baseline’ı birebir teyit eder. Izgara-tutarlı bakışta ~+%4,03 — hâlâ anlamlı. Preaudit’te açıkladık.

**S: Gizli testte çalışır mı?**  
C: Hardcode yok; gün/pazar/rakip veriden; şema doğrulama; doğrulayıcı gömülü; deterministik ayarlar.

**S: Rotasyon gerçekten sağlam mı?**  
C: Brief-exact min tur; gece-aşan slack bölüşümü; 1 709 tur gerçek eksen; yeni ihlal 0. Pair sezon uyumsuzluğu nedeniyle 221 uçuşta kısıt kurulamaz — veri sınırı, şeffaf.

**S: En özgün katkınız?**  
C: (1) Büyük-M’siz tarife-değişim cezası ve iki yönlü kazanç bulgusu; (2) tam-hafta MIP-start ile küresel gap; (3) çift-kayıt bağımsız doğrulayıcı.

Daha geniş banka: `docs/Buke_JURI_SORU_BANKASI.pdf` (59 soru).

---

## 22. Dosya haritası ve okuma sırası

### 22.1 Proje kökü

```
Buke_cozum/
├── data/                 # yarışma girdileri (salt okunur kopya)
├── derived/              # temiz model girdisi + transform_log.md
├── src/                  # 01–08 + run_all.py
├── output/               # tarife, market, bağlantı, özet
├── reports/              # teknik, doğrulama, duyarlılık, cilalama
├── docs/                 # model + final hazırlık + bu master
├── preaudit/             # öz-denetim betikleri
├── yarisma-belgeleri/    # brief, sunum, orijinal input
├── requirements.txt
└── README.md
```

### 22.2 Final hazırlık okuma sırası (önceden üretilmiş)

| # | Dosya | İçerik |
|---|---|---|
| 1 | `Buke_ON_BILGI_DERSI` | Sıfırdan havayolu + optimizasyon dersi |
| 2 | `Buke_ANLAMA_ve_ANLATMA_Kilavuzu` | Proje anlatımı, kod blokları, 10 problem |
| 3 | `Buke_JURI_SORU_BANKASI` | 59 jüri sorusu |
| 4 | `Buke_FINAL_Sunum_Hazirlik_Dosyasi` | Tam sayısal referans |
| 5 | `Buke_GELISTIRME_YOL_HARITASI` | 81 geliştirme fikri |
| **+** | **`Buke_PROJE_MASTER_DOKUMAN` (bu dosya)** | **Tek parça bütünleşik anlatı** |

### 22.3 Resmi teslim çekirdeği

1. `docs/model_formulation.pdf`  
2. `src/` + `run_all.py`  
3. `output/*`  
4. `reports/technical_report.pdf`  
5. `README.md`  

---

## 23. Sonuç ve genel değerlendirme

### 23.1 Ne başardık?

1. Brief’teki iş problemini **sıkı, doğrusal bir MIP** olarak kurduk.  
2. Gerçek ölçekli veriyi **minimal+belgeli** işledik.  
3. HiGHS ile **7 günün tamamını** iki aşamada çözdük.  
4. Operasyonel gerçekçilik için **λ cezası** ekledik; kaydırmayı %92→%23 indirdik, amacı da iyileştirdik.  
5. Tam-hafta cilalama ile **+%4,72** ve **gap %1,18** kanıtı ürettik.  
6. Bağımsız doğrulayıcıyla **18 kontrol PASS** aldık.  
7. Eksikleri (E2, B2, ızgara payı, pair sezonu) **ölçüp belgeledik**.  
8. Tek komutla tekrar üretilebilir, gizli teste genellenebilir kod teslim ettik.  

### 23.2 Tek slaytlık final cümlesi

> **Büke çözümü:** Pyomo+HiGHS ile kurulan, brief-exact kısıtlı, tarife-değişim cezalı, iki aşamalı MIP hattı; mevcut tarifeye göre **+%4,72** gelir-ağırlıklı rekabetçilik; yalnızca **%23** uçuşta ortalama **19 dk** kaydırma; **global gap %1,18**; bağımsız doğrulayıcıda **tam uyum**.

### 23.3 Güçlü yanlar (özet)

- Model kapsamı ve sıkı doğrusallaştırma  
- Kanıtlı yakın-optimum (gap)  
- Operasyonel gerçekçilik (az kaydırma)  
- Çift kayıt doğrulama kültürü  
- Şeffaf sınırlar ve preaudit  
- Tekrar üretilebilir mühendislik  

### 23.4 Geliştirme ufku (kısa)

Ayrıntı: `Buke_GELISTIRME_YOL_HARITASI`. Öne çıkanlar:

- Soft-E2  
- Indicator constraints / daha sıkı formülasyon  
- Ticari çözücü veya daha uzun cilalama ile gap ↓  
- ρ-ölçekli / uçuş-bazlı λ  
- Tail sürekliliği, stokastik talep  
- Öğrenilmiş parametreler (YZ entegrasyonu)  

### 23.5 Kapanış

Bu proje, “bir tarife skoru üretmek”ten ibaret değildir. **Gerçek bir havayolu ağ tasarım kararını**, yarışma brief’inin sert kısıtları altında, açık kaynak araçlarla, denetlenebilir ve anlatılabilir biçimde çözme denemesidir.

Finale kalan bir çözümün hakkı: sayıyı ezberlemek değil — **neden bu sayı** sorusunu her katmanda cevaplayabilmektir. Bu master doküman o cevabın bütünleşik metnidir.

---

*Takım Büke · TEKNOFEST Yapay Zeka Destekli Havayolu Optimizasyonu · Master Doküman*  
*Kaynaklar: Brief, kick-off sunumu, model_formulation, technical_report, results_summary, validation_report, fullweek_polish, sensitivity_analysis, transform_log, README, preaudit.*
