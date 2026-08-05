# Matematiksel Model — Tarife Planlamalarında Rakip Odaklı Ağ Optimizasyonu

**Takım: Büke** · **TEKNOFEST · Yapay Zeka Destekli Havayolu Optimizasyonu**
IST hub aktarma ağı · Karışık Tamsayılı Programlama (MIP)

> Bu, teslim edilen **Matematiksel Model Dokümanı**'dır. Kümeler, parametreler, karar değişkenleri,
> amaç fonksiyonu ve A–H kısıt gruplarının doğrusal (MIP) formülasyonunu içerir; tasarım kararları ve
> doğrusallaştırma seçimleri gerekçeleriyle birlikte verilmiştir. Çözüm hattı iki aşamalıdır:
> güne-göre ayrıştırma (§11–§12) + tam-hafta MIP-start cilalaması (§13); nihai sonuç §13'tedir.

---

## 0. Tasarım Kararları ve Gerekçeleri

Veri incelemesinden (bkz. `reports/data_health_report.md`) doğan ve formülasyonu şekillendiren kararlar:

| # | Karar | Gerekçe |
|---|---|---|
| D1 | **Zaman 10 dk'lık kovalara ayrıklaştırılır** (Δ = 10 dk). Ayarlanabilir her uçuşun IST olayı (kalkış/varış) bir kovaya atanır. | Hub kapasitesi kısıtı (F) zaten 10 dk kova ister. Ayrıklaştırma; (i) bağlantı penceresini [L,U] tam tamsayı yapar, (ii) katı eşitsizlik (ε) sorununu giderir, (iii) büyük-M değerlerini sıkılaştırır. |
| D2 | **Yolculuk süresi J = legsum + boşluk** olarak ayrıştırılır; `legsum` (bacak blok toplamı) her bağlantı için sabit veridir. | Güncellenmiş veride (`_updated.xlsx`) bacak süreleri `ElapsedTime1/2` sütunlarıyla verilir: `legsum = E1 + E2` **doğrudan veriden**, `J = E1 + boşluk + E2` **kesin** hesaplanır (Gate-to-Gate'in 24sa sarma belirsizliği yoktur; tüm satırlarda mod-24sa çapraz doğrulandı). Eski şemada (ElapsedTime yoksa) `legsum = J_mevcut − boşluk_mevcut` + minimal de-wrap kullanılır (bkz. `derived/transform_log.md`). Bloklar uçuş süreleridir, değişmez; yalnız IST saatleri (dolayısıyla boşluk) karardır. |
| D3 | **Ayarlanabilir uçuşlara pencere** tanımlanır: mevcut saat ± `Wdev`. Standart'ta sınır yok; tıkızlık için tanımlanır (brief md.2.3 buna izin verir). | Kova atama değişkenlerinin sayısını sınırlar; aksi halde 144 kova × uçuş patlar. `Wdev` ölçeklenebilirlik ayar parametresidir. |
| D4 | **Rakip sayısı N_od taşıyıcı bazlıdır** (itinerary değil). | Veride taşıyıcı bazlı N ∈ [1,17] ≤ 40 (ranking lookup tam kapsar); itinerary bazlı 73 pazarda 40'ı aşar (lookup dışı). Belgeli, `CFG` ile değiştirilebilir. |
| D5 | **Ön-işleme** ile uygun olmayan bağlantı/rakip eşleşmeleri ve kapasitesiz kovalar baştan elenir. | Brief md.7 önerisi; büyük-M ihtiyacını ve model boyutunu büyük ölçüde düşürür (bkz. §8). |
| D6 | ρ değeri olmayan 48 pazar amaçtan dışlanır; rotasyon partneri olmayan 176 TK uçuşu sabit kabul edilir. | "Minimal + belgeli" politikası: değer uydurmak yerine ihtiyatlı dışlama. |

Notasyon: kalın küçük harfler kümeler değil; kümeler kaligrafik (𝒮, ℳ…), parametreler düz, karar
değişkenleri Latin/Yunan. Tüm zamanlar kova indeksidir (1 kova = 10 dk).

---

## 1. Kümeler

| Sembol | Tanım |
|---|---|
| 𝒮 | Dış istasyonlar (outstation), o, d ∈ 𝒮. Hub = IST (sabit). |
| ℋ | Operasyon günleri, h ∈ {1,…,7}. |
| ℳ | Yönlü O–D pazarları (o,d), o≠d. TK bağlantısı olan **ve** ρ tanımlı pazarlar (dışlamalar sonrası). |
| ℛ | Uçuş örnekleri r = (f,h): uçuş no f'nin h günündeki gerçekleşmesi. |
| ℛⁱⁿ ⊂ ℛ | **Gelen** bacak örnekleri (o → IST). Karar: IST **varış** kovası. |
| ℛᵒᵘᵗ ⊂ ℛ | **Giden** bacak örnekleri (IST → d). Karar: IST **kalkış** kovası. |
| ℛᵛᵃʳ ⊂ ℛ | Ayarlanabilir örnekler (saat karar). ℛᶠⁱˣ = ℛ∖ℛᵛᵃʳ sabit. |
| Π | Aday TK aktarma bağlantıları π = (r₁,r₂), r₁∈ℛⁱⁿ (o→IST), r₂∈ℛᵒᵘᵗ (IST→d), aynı gün. Ön-işleme sonrası. |
| Π_{od,h} ⊂ Π | (o,d) pazarı, gün h için aday bağlantılar. |
| 𝒦_{od,h} | (o,d), h için rakip taşıyıcılar kümesi (T_comp türetilir). |
| 𝒯_r | Örnek r için izinli kova kümesi (pencere). Sabit r için tekil. |
| 𝒥_{od,h} = {1,…,M_{od,h}} | Azalan-getiri "slot" indeksleri; M_{od,h}=|Π_{od,h}|. |
| 𝒫 | Rotasyon çiftleri (rᵒᵘᵗ, rⁱⁿ): aynı uçak IST→o→IST (Flight Pairs'ten). |

---

## 2. Parametreler

| Sembol | Tanım | Değer/Kaynak |
|---|---|---|
| Δ | Kova genişliği | 10 dk |
| ℓ, u | Bağlantı boşluğu alt/üst sınırı (kova) | L=60, U=300 dk → ℓ=6, u=30 |
| τ_o | Minimum yer süresi | 45 dk |
| Tᴵᴮ_r, Tᴼᴮ_r | Gelen/giden bacak blok süreleri (rotasyon için) | veriden türetilir |
| legsum_π | π için sabit bacak blok toplamı (kova) | = (J_π − boşluk_π) / Δ, `derived/tk_connections.csv` |
| ρ_od | O–D gelir/önem ağırlığı | `markets.csv` (1–1000) |
| Tᶜᵒᵐᵖ_{od,h,k} | Rakip k'nin yolculuk süresi (kova) | `competitor_times_carrier.csv` |
| N_od,h | Rakip sayısı (taşıyıcı bazlı) | `market_n_od.csv` |
| b_od | Taban (başlangıç) sıralama | veriden/ranking taban |
| Wᶜ_j | Azalan-getiri ağırlığı, slot j | (½)^{j−1}, W₁=1 |
| Wʳ(N,b,s) | Sıralama ödülü (N, ilk rank b, son rank s) | `ranking_lookup.csv` |
| Capᵈᵉᵖ_t, Capᵃʳʳ_t | Kova t artık kalkış/varış kapasitesi | 10 / 15 − (sabit uçuş kullanımı) |
| Xdev | Gün-içi maks. saat sapması (kova) | 15 dk |
| α | Yönsel dengesizlik eşiği | 0.20 |
| Γ | En iyi-süre fark eşiği (kova) | 30 dk |
| lb_r, ub_r | Örnek r için kova penceresi alt/üst | mevcut ± Wdev (D3) |
| M_• | Büyük-M sabitleri | en sıkı değer (§7) |

Türetilmiş ön-işleme sabiti: **G_{πk} = Tᶜᵒᵐᵖ_{od,h,k} − legsum_π** (π'nin k'yi yenmesi için
izin verilen maksimum boşluk). §8'de bunun büyük-M elemesi için kullanımı.

---

## 3. Karar Değişkenleri

| Değişken | Tip | Tanım |
|---|---|---|
| x_{r,t} | ikili | Örnek r, kova t'ye atandı (∀ r∈ℛᵛᵃʳ, t∈𝒯_r). Sabit r için sabit. |
| θ_r | tamsayı (türev) | r'nin IST kova zamanı: θ_r = Σ_t t·x_{r,t}. |
| g_π | tamsayı ≥0 (türev) | π'nin bağlantı boşluğu (kova): g_π = θ_{r₂} − θ_{r₁}. |
| y_π | ikili | π pazara **sunuluyor** (uygun) mu? |
| z_{od,h,j} | ikili | (o,d,h) için j. slot dolu mu (monoton). |
| w_{π,k} | ikili | π bağlantısı rakip k'yi yeniyor mu (sunulu & J_π ≤ Tᶜᵒᵐᵖ). |
| β_{od,h,k} | ikili | (o,d,h)'de rakip k yenildi mi. |
| γ_{od,h,b} | ikili | (o,d,h)'de yenilen rakip sayısı = b seçici (Σγ=1). |
| Jmin_{od,h} | sürekli/tamsayı | yönün en iyi (min) sunulu yolculuk süresi (E2). |
| act_{od,h} | ikili | (o,d,h) yönü aktif mi (≥1 sunulu bağlantı). |

---

## 4. Amaç Fonksiyonu

Gelir ağırlıklı toplam rekabetçilik faydasını enbüyükle:

```
max  Σ_{(o,d)∈ℳ} ρ_od · Σ_{h∈ℋ} [  Σ_{j∈𝒥_{od,h}} Wᶜ_j · z_{od,h,j}            (bağlantı-sayısı ödülü)
                                  + Σ_{b=0}^{N_od,h} Wʳ(N_od,h, b_od, N_od,h−b) · γ_{od,h,b} ]   (sıralama ödülü)
```

İkinci terim: yenilen rakip sayısı b seçilir (γ), son sıralama s = N_od−b, ödül lookup'tan okunur.

> **Operasyonel kesinti uzantısı (P, §12).** Yukarıdaki amaca isteğe bağlı bir tarife-değişim
> cezası eklenir: `− λ · Σ_{r∈ℛᵛᵃʳ} |θ_r − cur_r|`. Bu, mevcut tarifeden gereksiz sapmaları
> cezalandırır; aynı zamanda "bedava kaydırma" dejenerasyonunu kırarak çözücüyü iyileştirir
> (bkz. §12). λ=0 iken saf rekabetçilik geri elde edilir.

---

## 5. Kısıtlar

### (A) Zaman Atama, Pencere ve Uçak Rotasyonu

**A1 — Tekil atama:** her ayarlanabilir örnek tam bir kovaya atanır.
```
Σ_{t∈𝒯_r} x_{r,t} = 1            ∀ r ∈ ℛᵛᵃʳ
θ_r = Σ_{t∈𝒯_r} t · x_{r,t}      ∀ r ∈ ℛᵛᵃʳ ;   θ_r = sabit   ∀ r ∈ ℛᶠⁱˣ
```
Pencere lb_r ≤ t ≤ ub_r, 𝒯_r tanımı içine gömülür (D3).

**A2 — Rotasyon:** aynı uçak IST→o (gidiş rᵒᵘᵗ) ... o→IST (dönüş rⁱⁿ) görevini yapar; dönüşün IST varışı,
gidişin IST kalkışından en az (Tᴼᴮ_o + τ_o + Tᴵᴮ_o) sonra olmalı:
```
θ_{rⁱⁿ} − θ_{rᵒᵘᵗ} ≥ ⌈(Tᴼᴮ_o + τ_o + Tᴵᴮ_o)/Δ⌉        ∀ (rᵒᵘᵗ, rⁱⁿ) ∈ 𝒫
```
Bacak blokları güncellenmiş verinin `ElapsedTime1/2` sütunlarından okunur (τ=45 dk, brief §2.4);
kısıt aynı-gün turlarda birebir kurulur. Fiziksel turu **gün h→h+1'e yayılan** (gece-aşan) çiftlerde
güne-göre ayrıştırma gün-bağlaşımı kuramaz; bunun yerine mevcut tarifedeki pay (slack) statik ikiye
bölünür — kalkış en çok slack/2 geç, ertesi günün dönüşü en çok slack/2 erken kayabilir → minimum tur
**yapısal olarak garanti** edilir ve çözüm üzerinde gerçek zaman ekseninde ayrıca doğrulanır (bkz. §10-U1).

### (B) Bağlantı Uygunluğu ve Tutarlı Bağlama

Boşluk tanımı ve "**boşluk ∈ [ℓ,u] ⟺ y_π = 1**" çift yönlü göstergesi. g_π = θ_{r₂} − θ_{r₁}.

**B1 — y=1 ⟹ uygun** (sunulan bağlantı pencere içinde):
```
g_π ≥ ℓ − M_g·(1 − y_π)
g_π ≤ u + M_g·(1 − y_π)
```
**B2 — uygun ⟹ y=1** (uygun olan zorunlu sunulur; ayrık "alt/üst" seçimi için s_π∈{0,1}):
```
g_π ≤ (ℓ−1) + M_g·(y_π + s_π)
g_π ≥ (u+1) − M_g·(y_π + (1 − s_π))
```
y=0 iken s_π=0 ise g≤ℓ−1 (çok kısa), s_π=1 ise g≥u+1 (çok uzun) zorlanır; y=1 iken iki kısıt da gevşer.
M_g = (ub−lb) menzili kadar sıkı seçilir (§7). Δ ayrıklığı sayesinde ε=1 kova kullanılır (katı eşitsizlik sorunu yok).

> Not: Pratikte azaltılmış model, B2'yi ön-işleme + objektif yönüyle hafifletebilir; ancak yönsel
> denge (E) bağlayıcıyken "zorunlu sunum" gerekli olduğundan B2 korunur.

### (C) Bağlantı Seçimi ve Azalan Getiri (Monoton Slotlar)

```
Σ_{π∈Π_{od,h}} y_π = Σ_{j∈𝒥_{od,h}} z_{od,h,j}        (sunulan sayı = dolu slot)
z_{od,h,j} ≥ z_{od,h,j+1}                              ∀ j  (monoton doldurma)
```
Wᶜ_j azalan olduğundan enbüyükleme slotları küçük j'den doldurur; monotonluk LP gevşetmesini sıkılaştırır.

### (D) Rakip Yenme ve Sıralama

π'nin k'yi yenmesi: sunulu **ve** J_π = legsum_π + g_π ≤ Tᶜᵒᵐᵖ ⟺ g_π ≤ G_{πk}. Ön-işleme (§8) üç durum:
- G_{πk} < ℓ : asla yenemez → w_{π,k} ≡ 0 (değişken yaratılmaz).
- G_{πk} ≥ u : sunulduğunda hep yener → **w_{π,k} = y_π** (büyük-M yok).
- ℓ ≤ G_{πk} < u : koşullu:
```
w_{π,k} ≤ y_π
g_π ≤ G_{πk} + M_g·(1 − w_{π,k})           (w=1 ⟹ boşluk yeterince kısa)
```
**β — rakip yenildi mi** (yenen en az bir sunulu bağlantı varsa):
```
β_{od,h,k} ≤ Σ_{π∈Π_{od,h}} w_{π,k}        ∀ k ∈ 𝒦_{od,h}
```
(β ödülü artırdığından enbüyükleme β'yı mümkünken 1 yapar; üst sınır yeterli.)

**Sıralama bağlama** — yenilen sayı ve ödül seçimi:
```
Σ_{b} γ_{od,h,b} = 1
Σ_{b} b · γ_{od,h,b} = Σ_{k∈𝒦_{od,h}} β_{od,h,k}        (b = yenilen rakip sayısı)
```
γ üzerinden amaçtaki Wʳ(N,b_od,N−b) doğru ödülü seçer.

### (E) Yönsel Denge Kısıtları

n_od,h := Σ_{π∈Π_{od,h}} y_π (yönün sunulan bağlantı sayısı). act_{od,h}=1 ⟺ n_od,h ≥ 1:
```
act_{od,h} ≤ n_od,h ≤ M_{od,h}·act_{od,h}
```

**E1 — sayı dengesi** (bağıl dengesizlik ≤ α; iki yön boşsa kendiliğinden sağlanır):
```
 n_od,h − n_do,h ≤ α·(n_od,h + n_do,h)
 n_do,h − n_od,h ≤ α·(n_od,h + n_do,h)
```

**E2 — en iyi yolculuk süresi dengesi** (yalnız her iki yön aktifken bağlayıcı, koşullu):
Jmin_{od,h} = min sunulu J. MIP'te min, alt sınır + seçimle modellenir:
```
Jmin_{od,h} ≤ (legsum_π + g_π) + M_J·(1 − y_π)        ∀ π∈Π_{od,h}    (sunulanların altına iner)
Jmin_{od,h} = Σ_{π} (legsum_π+g_π)·σ_π ,  Σ_π σ_π = act_{od,h},  σ_π ≤ y_π   (gerçek min'i seçen σ)
```
Koşullu fark kısıtı (M_E ile, yalnız iki yön aktifken):
```
 Jmin_{od,h} − Jmin_{do,h} ≤ Γ + M_E·(2 − act_{od,h} − act_{do,h})
 Jmin_{do,h} − Jmin_{od,h} ≤ Γ + M_E·(2 − act_{od,h} − act_{do,h})
```

### (F) IST Hub Kapasitesi

Her kova t için ayarlanabilir kalkış/varış sayısı artık kapasiteyi aşamaz:
```
Σ_{r∈ℛᵒᵘᵗ∩ℛᵛᵃʳ} x_{r,t} ≤ Capᵈᵉᵖ_t        ∀ t   (kalkış)
Σ_{r∈ℛⁱⁿ∩ℛᵛᵃʳ}  x_{r,t} ≤ Capᵃʳʳ_t        ∀ t   (varış)
```
Capᵈᵉᵖ_t, Capᵃʳʳ_t = baz kapasite (10/15) − sabit uçuşların t'de kullandığı slotlar. Cap=0 kovalar 𝒯_r'den elenir (D5).

### (G) Tarife Düzenliliği (Gün-İçi Tutarlılık)

Aynı uçuş no f'nin farklı günlerdeki IST kova zamanları en fazla Xdev sapar. Referans güne (ya da
ardışık çiftlere) bağlanır:
```
| θ_{(f,h)} − θ_{(f,h')} | ≤ ⌈Xdev/Δ⌉        ∀ aynı f, ∀ h,h' (örn. ardışık)
```
(Mutlak değer iki doğrusal eşitsizliğe açılır.)

### (H) Slot Pencereleri — *opsiyonel / netleştirilecek*

Sunum slaytında geçen ancak brief'in A–G listesinde **olmayan** ek kısıt: düzenlenmiş (slot-koordineli)
havalimanlarında varış pencereleri. Veride bu havalimanları/pencere bilgisi açıkça verilmediğinden,
bu kısıt **şimdilik dahil edilmez**; organizatör teyidine ve veri varlığına bağlı olarak, etkilenen
varışların 𝒯_r penceresi daraltılarak kolayca eklenebilir.

---

## 6. Geçerlilik / Çözülebilirlik Notları

- Tüm "min/koşullu" kısıtlar (E2) ve gösterge bağlamaları (B,D) doğru tarafta gevşetilir; pasif
  yönler dengeyi yapay olarak ihlal etmez (brief md.7).
- Sabit–sabit bağlantılarda g_π, J_π, w_{π,k} **veri** olarak hesaplanır; değişken yaratılmaz (D5).
- Amaç bileşenlerine ayrılabilir (bağlantı ödülü vs. sıralama ödülü) — küçük örnekte elle doğrulama
  için (brief md.7) raporlanır.

## 7. Büyük-M Sıkılaştırma

| M | Kullanım | Sıkı değer |
|---|---|---|
| M_g | B1/B2/D boşluk göstergeleri | (ub_max − lb_min) − ℓ veya u − (•) menzili; pencere genişliğiyle sınırlı |
| M_J | E2 Jmin alt sınırı | max_π(legsum_π+u) − min_π(legsum_π+ℓ) pazar-içi menzil |
| M_E | E2 koşullu fark | maks. olası |Jmin farkı| (pazar-içi) |

İlke: her M, ilgili değişkenin **pazar/örnek-yerel** menzilinden hesaplanır (global değil) — LP
gevşetmesini bozmamak için (brief md.7).

## 8. Ön-İşleme (model boyutu ↓, M ihtiyacı ↓)

1. **Bağlantı adayı filtresi:** boşluğu hiçbir pencere konumunda [ℓ,u]'ya giremeyecek (r₁,r₂)
   çiftleri Π'ye alınmaz.
2. **Yenme elemesi:** G_{πk} eşiğine göre w_{π,k} üç duruma ayrılır (§5-D); büyük-M yalnız orta
   durumda kurulur. Çoğu (π,k) ya sabit (y_π) ya da yok.
3. **Kapasite elemesi:** Capᵈᵉᵖ_t = 0 veya Capᵃʳʳ_t = 0 kovalar 𝒯_r'den çıkarılır.
4. **Pazar elemesi:** ρ tanımsız (48) pazar ℳ dışı; TK bağlantısı olmayan pazarda karar yok.
5. **Pencere daraltma (D3):** Wdev ayarıyla kova sayısı/uçuş düşürülür — ölçeklenebilirlik kolu.

## 9. Açık Sorular (organizatör teyidi önerilir)

- **N_od tanımı**: taşıyıcı bazlı varsayıldı (D4); itinerary bazlıysa lookup N>40 için genişletilmeli.
- **b_od taban sıralama**: artık baseline'ın 'son sırası' (s) ile **birebir aynı tabandan** hesaplanır
  ⇒ mevcut tarife HER pazarda lookup köşegenine (b==s = 'değişim yok' nötr referansı; köşegen değeri
  N'e göre 1/(N−1)) oturur (sıralama ödülü bir *iyileştirme* ödülü olduğundan doğru olan budur; brief §2.4). Önceki `faster+1` kuralı `s=N−beaten`
  konvansiyonuyla 1 kayıyor, baseline'ı pazarların ~%29'unda köşegen-dışına itip mevcut tarifeye
  hak edilmemiş ödül veriyordu — **düzeltildi**. Yalnız kesin türetim *konvansiyonunun* (0- mu 1-indeksli
  mi) organizatör tanımı teyit bekliyor; model artık hangi konvansiyon seçilirse seçilsin **iç-tutarlı**.
- **Kısıt H**: dahil mi; ilgili havalimanı/pencere verisi sağlanacak mı.
- ~~**Gizli wrap (195 satır)**: 24h+ olup boşluğu aşmayan uzun-menzil J'ler minimal politikada düzeltilmedi.~~
  **ÇÖZÜLDÜ (güncellenmiş veri):** organizatörün `_updated.xlsx` dosyası bacak sürelerini (`ElapsedTime1/2`)
  içerir; J artık kesin hesaplanır. Eski minimal de-wrap'in yanlış bıraktığı **154 satır** (29 TK, 125 rakip;
  hepsi tam +24sa eksik — EZE-PEK, BOG-PEK, VCE-SYD gibi ultra-uzun yolculuklar) düzeltilmiş oldu; veride
  24 saati gerçekten aşan **495** itinerary vardır.

---

## 10. Uygulama Notları (`src/03_model.py`)

Formülasyon küçük alt-örnekte (F hariç) uygulandı ve elle doğrulandı. Uygulama sırasında, veri
gerçekleriyle (bkz. `derived/transform_log.md`) doğan ve formülasyonu **netleştiren/sıkılaştıran**
kararlar:

| # | Karar | Gerekçe |
|---|---|---|
| U1 | **A2 rotasyon — BRIEF-EXACT minimum tur.** θ_{rⁱⁿ} − θ_{rᵒᵘᵗ} ≥ min(Tᴼᴮ+τ+Tᴵᴮ, mevcut tur); τ=45 dk (brief §2.4). | Güncellenmiş veri bacak bloklarını (`ElapsedTime1/2` → `derived/flight_block_times.csv`) verir → §5-A2 formülü artık **birebir** kurulur. Mevcut tur brief minimumunun ALTINDA görünen çiftler (141/948) **gece-aşan rotasyonun aynı-gün izdüşümüdür** (fiziksel tur gün h→h+1); bunlarda mevcut tur çapası korunur (gün-bağlaşımı yaratılmaz) ve fiziksel h→h+1 kısıtı çözüm üzerinde **gerçek zaman ekseninde ayrıca doğrulanır** (byday çıktısında rapor edilir). Bloklar yoksa (eski şema) ihtiyatlı geri-dönüş: min tur = mevcut tur. Eşler `Flight Pairs`'ten. |
| U2 | **E2 Jmin — doğrusal büyük-M min-seçimi.** §5-E2'deki `Jmin = Σ(legsum+g)·σ` **bilineerdir** (g·σ). Yerine: Jmin ≤ J_π+M_J(1−y_π); Jmin ≥ J_π−M_J(1−u_π); Σu_π=act; u_π≤y_π. | u_π argmin'i seçmeye zorlanır (J_sel ≥ min_sunulu ve Jmin ≤ min_sunulu ⇒ eşitlik). Tamamen doğrusal, McCormick gerekmez. M_J pazar-yerel J menzili. |
| U3 | **G düzenliliği SAAT-İÇİ + referans-bant.** θ mutlak dakika olduğundan günler arası ~1440 fark taşır; her olaydan gün-ofseti çıkarılır (θ' = θ − ⌊cur/1440⌋·1440). "En fazla Xdev sapar" için grup-başına ortak **c_f**: tüm günler [c_f, c_f+Xdev] ⇒ yayılım ≤ Xdev (ardışık-zincir yerine; zincir uçlarda (n−1)·Xdev'e kadar sapardı). | Veride aynı uçuş günler-arası neredeyse sabit (387 kalkıştan 356'sı tam aynı saat). **Wdev↔G gerilimi**: pencere ±Wdev her olayı kendi mevcut saatine bağlar; saat-içi yayılımı > 2·Wdev+Xdev olan gruplar pencerede düzenlenemez → atlanır ve raporlanır (Wdev/Xdev büyütülerek genişletilebilir). |
| U4 | **F (hub kapasite) — brief'in GERÇEK 10/15'i, TÜM TK uçuşlarıyla.** | Veri bulgusu (doğrulandı): mevcut tarifedeki kova aşımları (kalkış ≤16, varış ≤20) **tamamen ayarlanabilir** uçuşların mevcut saatlerinde kümelenmesinden gelir; **SABİT (kımıldamayan) uçuşlar hiçbir kovada baz cap'i aşmaz** (kalkış max 4 ≤ 10, varış max 5 ≤ 15). Dolayısıyla rezidüel kapasite (10/15 − sabit) her kovada ≥ 0 ve brief'e sadık **10/15 uygulanabilir**: ayarlanabilir uçuşlar ±Wdev penceresinde yayılarak sığar (gün başına ort. ~4–5/kova, ~120 kova). Mevcut tarife artık warm-start için uygun değil ama appsi-Highs MIP-start kullanmadığından **maliyetsiz** (aşama-2 §13'ün MIP-start'ı mevcut tarifeden değil, feasible byday ÇÖZÜMÜNDEN alınır — gözlem geçerli kalır); tüm 7 gün bu gerçek cap altında feasible kaldı. (Önceki sürüm `cap=max(baz,mevcut)` kullanıp F'i fiilen bağlamaz hale getiriyordu — düzeltildi.) **Ek düzeltme (bağımsız doğrulayıcının bulgusu):** amaç evrenine girmeyen pazarların (ρ tanımsız → dışlanan) uçuşları da IST kovalarını fiziksel olarak doldurur; bunlar F'de **sabit doluluk** olarak sayılır. Kımıldatılamayanların tek başına aştığı kova olursa kısıt `cap=max(baz, sabit)` ile korunur ve taşma raporlanır (bu veride 0). |
| U5 | **B2 (zorunlu sunum) — VARSAYILAN KAPALI (sayısal kanıtla).** | **B2 × E1 çatışması**: B2 her uygun bağlantıyı sunmaya zorlar; asimetrik pazarlarda (bir yön çok, ters yön az) E1 `|n_od−n_do| ≤ α(n_od+n_do)` ile çelişir. **Doğrudan kanıt (gerçek 10/15 F altında yeniden alındı):** `B2_force_offer=True` ile tek günler bile çözülemez (gün 1: 8 s'de **infeasible**, gün 2: 10 s'de **infeasible**, gün 3: 60 s'de incumbent yok). **Etki küçük:** amaç sunmayı ödüllendirdiğinden model B2 olmadan da, pencereye erişebilir adayların **%90.8'ini (6877/7577; aşama-1/byday çözümünde ölçüldü — nihai çözümde 6 966 bağlantı sunulu) zaten sunar**; sunulmayanların çoğu paylaşılan uçuş saatlerinin başka pazarlarda pencere-dışı kalmasındandır, bilinçli bastırılan **~%3.5'tir**. Yani B2 fiilen büyük ölçüde sağlanır, sert uygulamak ise infeasible yapar. |
| U6 | **E2 (Jmin zaman dengesi) — TAM-ÖLÇEKTE KAPALI (iki bağımsız kanıtla).** | **(a) Çözücü:** E2'nin min-seçimi büyük-M'i LP gevşetmesini zayıflatır; HiGHS **incumbent bulamaz**. Bu *boyut* sorunu DEĞİL: güne-göre ayrıştırmada tek gün (~18k ikili, E2 açık) dahi 150 s'de incumbent bulamaz (E2 kapalı aynı gün saniyeler içinde çözülür). **(b) Veri:** E2-kapalı optimal çözümde, her iki yönü aktif yön-çiftlerinin **%76'sı (1500/1972)** \|Jmin_od−Jmin_do\| > Γ(=30 dk) koşulunu ihlal eder, **465 dk'ya** varan farklarla. Yani Γ=30 dk bu veride yapısal olarak ulaşılamaz — E2'yi *sert* uygulamak ya infeasible yapar ya rekabetçilik kazanımını (nihai +%4.72) çökertir. Küçük-ölçekte E2 açık/doğrulanmış kalır; `full`/`byday`'de kanıtlı olarak gevşetilir. (Soft-E2 ya da ticari çözücü ileri adımdır.) |
| U7 | **Hafta normalizasyonu + aday tekilleştirme (veri katmanı).** | Veride aynı operasyon günü (Gün=d) farklı pazarlarda **farklı takvim haftalarına** yazılıyor (gün 1 hem 4 Ağu hem 11 Ağu Pazartesi). Aynı uçuş no'nun hafta-kopyaları modelde **ayrı karar olayları** olur ve aynı fiziksel uçuşa iki farklı saat atanabilirdi (çıktıda gözlendi: bir kopya −50 dk, öteki 0). Düzeltme (`02_data_prep`): her satırın iki zaman damgası birlikte 7k gün geri çekilir (boşluk/J **değişmez**), kopyalar tek olaya birleşir (5 604→5 474 olay); ardından birebir özdeşleşen aday satırları tekilleştirilir (7 850→7 693) — aksi hâlde aynı fiziksel bağlantı iki aday sayılıp **aynı ürüne çift aktarma ödülü** yazdırırdı (baseline ve optimize tarafını birlikte şişirir). Saatleri gerçekten farklı olan 3 anomali olay korunur. Gizli veri güvencesi: 7'nin katı olmayan tarih farkı görülürse satıra dokunulmaz. |
| U8 | **Bağımsız çözüm doğrulayıcı (çift kayıt).** | `src/05_validate_solution.py`, `output/` çözümünü MIP kodundan geçmeden yalnız `derived/` veri katmanı üzerinden yeniden hesaplar: A1 (ızgara/pencere), A2 (gerçek zaman ekseni, gece-aşan dahil + aynı-gün çapası), B1 (pencere + J + saat tutarlılığı), C/D (ödüller lookup'tan), E1, F (10/15, **tüm** TK uçuşlarıyla), G (bant + belgeli muafiyetler) ve amaç/baseline toplamları. Rapor: `reports/validation_report.md`. U4'teki F evren açığını ve U7'deki kopya-olay tutarsızlığını bu doğrulayıcı yakaladı. |
| U9 | **A2 evren-ankoru (F'nin U4 açığının A2 karşılığı).** | Bir rotasyon ortağının bağlantısı amaç evreninde değilse (ör. ρ tanımsız pazar, D5) o günkü olay hiç modellenmez ve A2 kısıtı o gün için hiç kurulamazdı — **bağımsız doğrulayıcı (U8) gerçek bir ihlal yakaladı** (uçuş 2200/2201, gün 2: KCM-AGP pazarı dışlandığından 2201'in o günkü varışı modelsiz kaldı, rotasyon ortağı 2200'ün kalkışı kısıtsız kayarak minimum turu 20 dk altına indirdi). Düzeltme: `build_instance()` artık **TÜM** (chosen ∪ dışlanan) pazar/günler için gerçek saatleri (`full_role_time`) tutar; `build_model()` üstteki A2 döngüsünün atladığı her (rotasyon-çifti, gün) için modellenmeyen tarafı bu SABİT gerçek saatiyle **ankorlayarak** kısıtı ekler (05'in `sep=min(exact,turn)` formülüyle birebir). Etki küçük ve beklenen yönde: byday +%4.32→**+%4.27** (haksız kazanılan ~5 bin puanlık payı geri aldı), tüm 7 gün feasible kaldı, bağımsız doğrulayıcı A2'de **0/0 ihlal**. |

**Doğrulama (küçük örnek):** Model HiGHS ile *optimal* çözülür; raporlanan amaç = çözücü amacı
(14 384.38, iç tutarlı). Optimize amaç baseline'ı (10 876.70) belirgin geçer (**+%32**). A2
(brief-exact minimum tur) ve G (saat-içi yayılım ≤ Xdev) çözüm üzerinde ihlalsiz doğrulandı; tam
veride ayrıca gece-aşan rotasyonlar gerçek zaman ekseninde denetlenir (1 709 tur, **yeni ihlal 0**;
mevcut tarifede de görülen 358 eşleşme-artefaktı hariç). Ayrıca
b_od düzeltmesi (§9) sonrası baseline'ın sıralama terimi tüm (N≥1, sunulan) pazar-günlerde
lookup köşegenine (nötr) oturur — birebir doğrulandı; sıralama ödülü lookup'tan birebir okunur.
Tam-veri çözümü ayrıca **bağımsız doğrulayıcıyla** (U8) uçtan uca denetlenir: **tüm kontroller PASS**
(18 kontrol + 2 bilgi notu; `reports/validation_report.md`).

---

## 11. Tam Veriye Ölçekleme (`byday` profili)

**Sorun:** Tüm veri tek MIP olarak (4660 pazar-gün, 7693 bağlantı, ~100k ikili) HiGHS'te *soğuk
başlangıçla* 600s'de **incumbent bile bulunamıyor** (büyük-M MIP; sezgisel yöntemler uygun tamsayı
noktası bulamıyor). appsi Highs warm-start'ı yalnız LP bazı için kullanıyor, MIP-start vermiyor.
(Bu engel aşama-2'de aşılır: §13'te byday çözümü, highspy `setSolution` ile tam-hafta modele
MIP-start olarak verilir.)

**Çözüm — güne göre ayrıştırma.** Günleri bağlayan **tek** kısıt G'dir (E1/E2/A2/F hepsi gün-içi).
Her gün ayrı çözülür (≈670 pazar-gün, ~17k ikili ⇒ 3–10s, çoğu *optimal*); G, önceki günlerin
yerleşmiş **saat-içi bandı** ile zincirlenir (o günün aynı uçuşu band ±Xdev'de tutulur). Bir gün
bant kuplajıyla aşırı-kısıtlanıp infeasible olursa, o gün için **G gevşetilip** bantsız çözülür
(greedy propagasyonun katılığına karşı sağlam geri-düşüş).

**Sonuç (7 gün, tüm pazarlar; güncellenmiş ElapsedTime'lı + hafta-normalize veri) — cezasız (λ=0) ayrıştırma:**

| | Toplam | Not |
|---|---|---|
| OPTIMIZE | **3 378 002** | 7/7 gün çözüldü; hepsi G-bantlı (gevşetme 0) |
| BASELINE (mevcut tarife) | 3 251 527 | |
| **İYİLEŞME** | **+126 475 (+%3.89)** | gelir-ağırlıklı rekabetçilik faydası |

Gün-içi kısıtlar (A1, A2, B1, C, D, E1, F, G-bant) her günde tam uygulanır; E2 tam-ölçekte kapalı (U6).

> **Uyarı (→ §12–§13):** Bu cezasız çözüm uçuşların **~%92'sini** kaydırır (operasyonel olarak
> gerçekçi değil) ve dejenerasyon nedeniyle çözücü gerçek optimumun altında kalır (+%3.89).
> §12'deki **tarife-değişim cezası** hem bu kaydırmayı **~%25'e** indirir hem rekabetçiliği
> **+%4.32'ye** (aşama-1 ölçümü) yükseltir; §13'teki tam-hafta cilalaması nihai sonucu **+%4.72'ye**
> taşır. Nihai/önerilen sonuç **§13**'tedir.

---

## 12. Tarife-Değişim Cezası (Operasyonel Kesinti) — `byday [λ]` / `sweep`

**Motivasyon.** §4 amacı yalnız rekabetçiliği ödüllendirir; bir uçuşu mevcut saatinde tutmakla
kaydırmak amaç açısından **eşdeğerdir**. Bu yüzden cezasız çözüm, hiçbir fayda üretmeyen "bedava"
kaydırmaları keyfî yapar (uçuşların ~%92'si, ort. ~38 dk). Gerçek hayatta her saat değişikliği
operasyonel maliyettir (slot, ekip, bağlantı dalgası). Bunu içselleştirmek için amaca doğrusal bir
**tarife-değişim cezası** eklenir.

**Formülasyon (tam doğrusal — ek değişken / büyük-M YOK).** A1 her ayarlanabilir olayda
`Σ_{t∈𝒯_r} x_{r,t} = 1` zorladığından, mutlak kaydırma doğrudan x'in doğrusal birleşimidir:

```
|θ_r − cur_r| = Σ_{t∈𝒯_r} |t − cur_r| · x_{r,t}            (cur_r = mevcut kova; |t−cur_r| SABİT)

max   Σ_{(o,d)} ρ_od·(…§4…)   −   λ · Σ_{r∈ℛᵛᵃʳ} Σ_{t∈𝒯_r} |t − cur_r| · x_{r,t}
```

λ = **amaç-puanı / uçuş-dk**. Yalnız ayarlanabilir olaylar cezalanır (sabitler kımıldamaz). Mutlak
değer için yardımcı değişken/ikinci big-M gerekmez — bu, A1'in tekil-atama yapısının doğrudan
sonucudur. "OPTIMIZE amaç"/"İYİLEŞME" daima **cezasız** (saf rekabetçilik) ölçülür; λ yalnız *hangi*
kaydırmaların yapılacağını süzer, ödülü şişirmez.

**λ-taraması (Pareto ödünleşimi, `python src/03_model.py sweep`).** gap≤%0.1, gün-başına ≤150s.
*Tablodaki tüm değerler aşama-1 (byday) ölçümüdür; nihai teslim sonucu §13'teki cilalama sonrasıdır:*

| λ | Δ rekabetçilik | mevcut tarifeye göre | kaydırılan uçuş | toplam kaydırma | G-gevş. |
|---:|---:|---:|---:|---:|---:|
| 0.0 | +126 475 | +%3.89 | **%92** | 159 800 dk | 0 |
| 0.1 | +140 463 | +%4.32 | %26 | 24 090 dk | 0 |
| **0.3** | **+140 566** | **+%4.32** | %25 | 23 150 dk | 0 |
| 0.7 | +138 992 | +%4.27 | %24 | 22 280 dk | 0 |
| 1.5 | +137 904 | +%4.24 | %22 | 20 080 dk | 0 |

*(Tarama, U9 evren-ankoru düzeltmesi öncesi koşudandır; U9 sonrası byday λ=0.3 = 3 390 287
(+138 760, +%4.27). Satırlar arası **sıralama ve knee sonucu değişmez**; nihai teslim değeri §13'te.)*

**İki yönlü kazanç.** λ>0, kaydırmayı düşürdüğü gibi **rekabetçiliği de artırır**: λ=0 +%3.89
verirken λ=0.3 **+%4.32**'ye çıkar — kaydırma %92'den %25'e düşerken. Sebep dejenerasyondur:
cezasız modelde binlerce eşit-amaçlı "bedava kaydırma" çözümü LP gevşetmesini gevşetir ve HiGHS iyi
tamsayı çözümü bulamaz; ceza bu simetriyi kırar (her olay için tek bir "minimum sapma" yönü),
gevşetmeyi sıkar ve çözücüyü daha iyi optimuma taşır. λ∈[0.1, 1.5] sonuçlarının dar bir bantta
kümelenmesi (kararlılık), bunların gerçek optimuma yakınlığını gösterir. (Not: dejenerasyonun bir
bölümü U7 hafta-normalizasyonu ile veri katmanında da çözüldüğünden cezasız taban eski verideki
+%2.39'dan +%3.89'a yükseldi; iki-yönlü kazanç bulgusu geçerliliğini korur ve cezanın asıl değeri
kaydırmayı ~1/7'ye indirmesidir.)

**MIP-gap kalibrasyonu.** %0.5 gap, raporlanan (saf) amaçta ~0.5 puan bırakır; %0.01 gap ise cezalı
amacı sıkarken saf rekabetçiliği *düşürür* (çözücü kaydırma maliyetini kısmak için saf ödülden feragat
eder — ceza-ödün etkisi) → **%0.1** seçildi.

**Seçim (aşama-1 ölçümüyle).** Plato geniş (λ∈[0.1,1.5]); **λ=0.3** hem en yüksek kazanımı verir hem
λ=0.1'den daha az kaydırır → **knee** olarak seçildi. λ=0.3 ile güncel (U9 sonrası) aşama-1/byday
sonucu: OPTIMIZE 3 390 287 · İYİLEŞME **+138 760 (+%4.27)**. Bu, nihai teslim değeri **değildir** —
nihai sonuç, bu çözümün §13'teki tam-hafta cilalamasından geçmiş hâlidir (**3 405 039, +%4.72**).

**G'de iki aşamalı geri-düşüş — ŞEFFAF raporlanır.** Bir gün bant kuplajıyla infeasible olursa önce
**yalnız rotasyon-korumalı uçuşların** bandı bırakılır (rotasyon güvenliği > gün-arası düzenlilik
önceliği; kısıtlar çatıştığında hangi kuralın kazandığı bilinçli bir tasarım kararıdır), yetmezse o
günün bandı tümüyle gevşetilir. Bandı bırakılan her (gün, uçuş, rol) `output/g_band_exemptions.csv`'ye
yazılır ve bağımsız doğrulayıcı bu listeyi **belgeli muafiyet** olarak ayrıca denetler; muafiyet
dışındaki tüm gün-arası bağlar ±Xdev bandında doğrulanır. Ceza her günü mevcut tarifeye
çapaladığından muaf uçuşlar da mevcuda yakın kalır (gün-arası düzenlilik örtük korunur).

---

## 13. Aşama-2: Tam-Hafta MIP-Start Cilalaması (`src/08_fullweek_polish.py`) — NİHAİ SONUÇ

**Motivasyon.** Güne-göre ayrıştırma (§11–§12) hızlıdır ama iki yapısal sınırı vardır: *(i)* G'yi
greedy zincirle kurduğundan günler-arası koordinasyonu tam göremez; *(ii)* gün-bazlı gap'ler toplam
için **küresel optimalite kanıtı** vermez. Aşama-2 ikisini de giderir.

**Yöntem (modele ek — kurala dokunulmaz).** Haftanın tamamı **tek MIP** olarak kurulur; amaç ve tüm
kısıtlar (λ=0.3 cezası dahil) §4–§5/§12 ile **birebir aynıdır** (100 552 ikili değişken). Tek fark
G'nin kuruluş biçimidir: gün-arası bağlar, bağımsız doğrulayıcının denetlediği biçimle birebir aynı
**"ilk-gün çapalı ±Xdev"** kısıtları olarak tam modelde kurulur (2 643 bağ; aşama-1'in belgeli
muafiyetleri korunur — byday 1 110 + cilalamada 22 yeni = 1 132, `output/g_band_exemptions.csv`).
Aşama-1 çözümü highspy `setSolution` ile **MIP-start** verilir; HiGHS (threads=1, seed=0) ≤1800 s
branch-and-bound ile bu incumbent'ı iyileştirir.

**Güvence (çift bariyer).** 08, `output/`u yalnız *(i)* kayıtlı aşama-1 toplamına göre **kanıtlı
iyileşme** varsa ve *(ii)* gece-aşan A2 denetimi temizse (1 660 tur, yeni ihlal 0) yeniden yazar;
aksi hâlde deterministik aşama-1 çıktısı geçerli kalır (uçtan-uca koşu durdurulmaz).

**Nihai sonuç (7 gün, tüm pazarlar; güncellenmiş ElapsedTime'lı veri):**

| | Değer |
|---|---:|
| Aşama-1 (byday λ=0.3) SAF rekabetçilik | 3 390 287 |
| **Cilalanmış NİHAİ amaç (saf rekabetçilik)** | **3 405 039** (+14 752) |
| BASELINE (mevcut tarife) | 3 251 527 |
| **İYİLEŞME** | **+153 512 (+%4.72)** |
| Kaydırılan uçuş hareketi | 1 067 / 4 554 (%23) · 20 640 uçuş-dk (ort. 19 dk) |
| **Global MIP-gap (cezalı amaç)** | **%1.18** — küresel optimalite kanıtı |
| Çözüm süresi | 1 809 s (sınır 1 800 s) + aşama-1 ~1.5 dk |
| Kısıt uyumu | G-gevşetilen gün 0 · A2 gerçek eksen 1 709 tur, **yeni ihlal 0** · bağımsız doğrulayıcı **tüm kontroller PASS** |

Koşu raporu: `reports/fullweek_polish.md`; bağımsız doğrulama: `reports/validation_report.md`.

*İleri adımlar (isteğe bağlı):* E2/tam-G için ticari çözücü, λ'nın pazar-bazlı (ρ-ölçekli)
genelleştirilmesi, kaydırmayı uçuş-bazlı operasyonel maliyetle ağırlıklandırma, daha uzun
cilalama bütçesiyle gap'in daraltılması.
