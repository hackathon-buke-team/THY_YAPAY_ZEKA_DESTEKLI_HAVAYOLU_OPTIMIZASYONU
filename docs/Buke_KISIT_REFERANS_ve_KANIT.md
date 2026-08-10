# Kısıt Referans ve Kanıt Dosyası

**Takım: Büke** · TEKNOFEST — Yapay Zekâ Destekli Havayolu Optimizasyonu
*Tarife Planlamalarında Rakip Odaklı Ağ Optimizasyonu*

> **Bu doküman iki soruyu cevaplar:**
> **(1)** Yarışma bizden hangi kısıtları istiyor ve bunu **tam olarak nerede yazıyor**? Her kısıt,
> yarışma klasöründeki kaynak belgeye, bölüme, sayfaya ve **birebir alıntıya** bağlanmıştır.
> **(2)** Tam uygulamadığımız üç kural (**B2**, **E2**, **G**) için elimizde iddia değil **sayısal kanıt**
> var mı? Bu sürümle birlikte: evet. Kanıtlar `preaudit/08_kapali_kisit_kanitlari.py` ile
> sıfırdan, `src/` kodundan bağımsız olarak yeniden üretilebilir.

---

## 1. Yarışma klasöründeki kaynaklar — neyi kim bağlar?

`yarisma-belgeleri/` klasöründe **iki normatif metin** ve **beş veri dosyası** var:

| Dosya | Tür | Bağlayıcılık | Bu dokümandaki kısaltma |
|---|---|---|---|
| `TEKNOFEST_Yarismasi Brief.pdf` (7 sayfa) | **Yarışmacı Dokümanı** — Problem Tanımı, Kısıtlar ve Değerlendirme Kriterleri | **Birincil / asıl kaynak.** Kısıtların resmî tanımı burada. | **[B §x.y, s.N]** |
| `Teknofest_Yarisma_sunum.pdf` (11 slayt) | **Yarışma Kick-off** sunumu, 17 Haziran 2026 | İkincil. Brief'i özetler; **birkaç yerde brief'te olmayan ifade içerir** (bkz. §2). | **[S sl.N]** |
| `README_full_data_input_dosyalari.docx` | Veri paketi açıklaması | Veri şeması; kısıt tanımlamaz. | **[R]** |
| `Yolcu Verisi_masked.xlsx` | Veri | ρ_od gelir potansiyeli | |
| `O&D Rakip Bağlantı Tablosu_updated.xlsx` | Veri | TK + rakip bağlantıları, T^comp, N_od, b_od | |
| `change_ranking_input.xlsx` | Veri | Sıralama ödülü arama tablosu W^(r) | |
| `Flight Pairs.xlsx` | Veri | Uçak rotasyon çiftleri (A2) | |

Her ikisi de aynı hazırlayıcıya aittir (Doç. Dr. Mehmet Ertem, Yöneylem Araştırmaları Direktörlüğü,
17 Haziran 2026). **Çelişki hâlinde Brief esas alınmalıdır** — çünkü kendisini
*"Problem Tanımı, Kısıtlar ve Değerlendirme Kriterleri — Yarışmacı Dokümanı"* olarak tanımlar ve
kısıtları gereksinim düzeyinde tek tek yazar; sunum ise kick-off özetidir.

---

## 2. İki belge arasındaki **üç farklılık** (jüriye biz söylemeliyiz)

Bu farkları kendimiz tespit ettik; sunumda "brief'te olmayan kısıt uydurdunuz" ya da
"sunumdaki kısıtı atladınız" itirazının ikisini de baştan kapatır.

### Fark 1 — Kısıt grubu sayısı: **7'ye karşı 8**

* **Brief §4** yedi grup sayar: **A, B, C, D, E, F, G**. [B §4, s.5–6]
* **Sunum sl.7** başlığı: *"Dikkat Edilecek **8** Kısıt Grubu"* ve sekizinci kutu:
  > **H · Slot Pencereleri** — "Düzenlenmiş havalimanlarında varış pencereleri." [S sl.7]

**Kararımız:** H **dahil edilmedi.** Gerekçe: (i) Brief'in resmî kısıt listesinde yok;
(ii) hangi havalimanlarının slot-koordineli olduğu ve pencere saatleri **veri paketinde
verilmemiştir** ([R] dosya listesinde böyle bir alan yok). Model dokümanımızda bu, uydurulmuş bir
kısıt olarak değil, **açık bir eksiklik notu** olarak yazılıdır (`docs/model_formulation.md` §5-H).
Veri sağlanırsa uygulaması tek satırdır: etkilenen varışların 𝒯_r penceresi daraltılır.

### Fark 2 — C grubunda "bağlantı üst sınırı"

* **Sunum sl.7:** *"C · Seçim & Azalan Getiri — Monoton slotlar; **O–D başına bağlantı üst sınırı**."*
* **Brief §4.3** yalnızca monoton slotları ister; **üst sınırdan hiç söz etmez.** [B §4.3, s.5]

**Kararımız:** Üst sınır **konulmadı.** Zaten gereksizdir: azalan getiri ağırlığı (½)^(j−1)
olduğundan 10. bağlantının katkısı 1/512'dir — ödül kendiliğinden sönümlenir. Sert bir üst sınır
koymak, brief'te olmayan bir kısıtla çözüm uzayını daraltmak olurdu.

### Fark 3 — Kriter 3'ün tanımı

* **Brief §6:** *"Çözüm süresi; formülasyon sıkılığı (büyük-M kaçınma veya sıkılaştırma, gereksiz
  değişken/kısıttan kaçınma); daha büyük örneklere ölçeklenme."* [B §6, s.6]
* **Sunum sl.9:** *"Hesaplama Performansı **(Optimality gap)** %15"* [S sl.9]

**Kararımız:** İkisini de raporluyoruz — **küresel MIP-gap %1,18** (optimalite kanıtı) *ve* çözüm
süresi/formülasyon sıkılığı (ön-işleme, pazar-yerel büyük-M, ayrıştırma).

---

## 3. Kısıt–kaynak haritası: her kural nereden geliyor?

> Alıntılar **birebir**dir. "Bizde" sütunu, `docs/model_formulation.md` §5'teki karşılığını verir.

### A · Zaman Sınırları ve Uçak Rotasyonu — [B §4.1, s.5] · [S sl.7]

> **A-i** — *"Her ayarlanabilir uçuş örneğinin IST kalkış ve varış saati, verilen alt/üst sınırlar
> arasında kalmalıdır."*
>
> **A-ii** — *"Rotasyon: Aynı uçak IST → o → IST iki bacaklı bir görevi gerçekleştirir. Dönüş
> (inbound) IST varışı, gidişin (outbound) IST kalkışından en az (T^OB_o + τ_o + T^IB_o) kadar
> sonra olmalıdır."*

Pencere sınırı için brief serbestlik verir: *"Ayarlanabilir uçuşların IST kalkış ve varış saatleri
(**verilen alt/üst sınırlar içinde: Standard: herhangi bir sınır yok, gerekirse tanımlanabilir**)"*
[B §2.3, s.4]. Bu yetkiye dayanarak **±60 dk** pencere tanımladık (ölçeklenebilirlik kolu).

τ_o = **45 dk** kaynağı: *"Blok ve yer süreleri: T^IB_o, T^OB_o, minimum yer süresi τ_o **(45dk)**"*
[B §2.4, s.4].

**Bizde:** A1 + A2, tam. Doğrulama: 4 554 hareket ızgara+pencere PASS; **1 709 tur, yeni ihlal 0**
(gece-aşan turlar gerçek zaman ekseninde ayrıca denetlendi).

### B · Bağlantı Uygunluğu — [B §4.2, s.5] + **[B §2.3, s.4]** · [S sl.5, sl.7]

Bu grup **iki ayrı yerden** beslenir; ikincisi kolayca gözden kaçar:

> **B1 (§4.2)** — *"Bir bağlantı yalnızca IST'teki bağlantı boşluğu [L, U] aralığında ise
> sunulabilir."* ve *"Seçilen bir değişken bağlantı için, bağlantı boşluğu ilgili IST saatleri
> farkına eşit olmalı; seçilmeyen bağlantı için boşluk değişkeni serbest bırakılmamalıdır
> (tutarlı bağlama)."*
>
> **B2 (§2.3 — "Neye Karar Veriliyor?")** — *"Hangi aktarma bağlantılarının pazara 'sunulacağı'
> **(seçim: aktarma süresi uygun olan tüm uçuşlar seçilmek zorundadır)**."*

L=60, U=300 kaynağı: *"L ≤ bağlantı boşluğu ≤ U **(Standard süre: L=60 dk, U=300 dk)**"*
[B §2.2, s.4]; sunumda da aynı: *"Standard: 60–300 dk"* [S sl.5].

**Bizde:** B1 tam (6 966 bağlantının **tamamı** [60,300] içinde). **B2 sert kısıt olarak kurulmadı**
— nedeni ve kanıtı **§6**'da.

### C · Bağlantı Seçimi ve Azalan Getiri — [B §4.3 + §3.1, s.4–5] · [S sl.6, sl.7]

> *"Her O–D/gün için sunulan bağlantı sayısı, azalan-getiri 'slot' göstergeleriyle
> ilişkilendirilmelidir; slotlar monoton (sıralı) doldurulmalıdır."* [B §4.3]
>
> *"W^(c)_{od,h,1} ≥ W^(c)_{od,h,2} ≥ … ≥ W^(c)_{od,h,Mmax} ≥ 0"* [B §3.1]

Somut ağırlık kuralı: *"azalan getiri ağırlıkları W^(c)_od,h,j **(ilk bağlantı 1 puan, sonraki her
bağlantı bir önceki puanın yarısı)**"* [B §2.4, s.4]; sunum aynı [S sl.6].

**Bizde:** tam. `Σ y_π = Σ z_j`, `z_j ≥ z_{j+1}`. 4 660 pazar-gün PASS.

### D · Rakip Yenme ve Sıralama — [B §4.4 + §3.2, s.5] · [S sl.7]

> *"Bir bağlantı, toplam yolculuk süresi rakibin süresinden küçükse o rakibi 'yener': J_π ≤
> T^comp_odk."*
> *"Bir rakip, ancak onu **yenen en az bir bağlantı sunuluyorsa** 'yenilmiş' sayılır."*
> *"Güncellenen sıralama r_od,h, yenilen rakip sayısına bağlanmalı ve sıralama ödülü buna göre
> devreye girmelidir."*
>
> *"r_od,h = N_od,h − (yenilen rakip sayısı)"* [B §3.2]

Veri kaynağı: *"Her O–D, gün ve rakip k için rakip yolculuk süresi T^comp_odk, taban değer b_od,
toplam rakip sayısı N_od **(O&D Rakip Bağlantı Tablosu.xlsx dosyasından türetilmeli)**"* ve
*"sıralama-iyileştirme ödülü W^(r)_od,h **(önceden hesaplanmış, veri olarak verilir,
change_ranking_input.xlsx)**"* [B §2.4, s.4].

**Bizde:** tam. **Fazla-beyan 0** (hak etmediğimiz hiçbir yenme sayılmıyor).

### E · Yönsel Denge — [B §4.5, s.5–6] · [S sl.7]

> **E1** — *"Skor/bağlantı-sayısı dengesi: İki yöndeki sunulan bağlantı sayıları arasındaki bağıl
> dengesizlik α eşiğini aşmamalı. İki yön de boşsa kısıt kendiliğinden sağlanır."*
>
> **E2** — *"En iyi yolculuk süresi dengesi: Yalnızca her iki yönde de en az bir aktif bağlantı
> varken, iki yönün en iyi (minimum) yolculuk süreleri arasındaki fark Γ dakikayı aşmamalı.
> Yönlerden biri pasifse kısıt bağlayıcı olmamalıdır (koşullu aktivasyon)."*

α = **0.20**, Γ = **30 dk** kaynağı: *"yönsel dengesizlik eşiği α **(0.20)**; en iyi yolculuk süresi
fark eşiği Γ **(30 dk)**"* [B §2.4, s.4].

**Bizde:** **E1 tam ve sert** (2 001 yön-çifti, **0 ihlal**). **E2 tam ölçekte kurulmadı** —
nedeni ve kanıtı **§5**'te.

### F · IST Hub Kapasitesi — [B §4.6, s.6] · [S sl.7]

> *"Gün, 10 dakikalık zaman kovalarına (bucket) bölünür. Her ayarlanabilir kalkış/varış tam olarak
> bir kovaya atanmalı ve atandığı kovanın saat aralığıyla tutarlı olmalıdır."*
> *"Her kovadaki ayarlanabilir kalkış/varış sayısı, o kovadaki kalan (**rezidüel**) kapasiteyi
> aşamaz (sabit uçuşların kullandığı slotlar düşülür)."*

10/15 kaynağı: *"IST Hub kapasiteleri (10 dk'lık zaman aralıkları (kova) için **kalkış (10)/varış
(15)** slot kapasiteleri)"* [B §2.4, s.4].

**Bizde:** tam ve brief'in gerçek 10/15'iyle. **Aşan kova: 0**; en dolu kova kalkış 10/10, varış
15/15 → kısıt fiilen bağlayıcı. Amaç evrenine girmeyen pazarların uçuşları da sabit doluluk
sayılır.

### G · Tarife Düzenliliği — [B §4.7, s.6] · [S sl.7]

> *"Aynı uçuş numarasının farklı operasyon günlerindeki IST kalkış ve varış saatleri birbirinden
> en fazla X_dev dakika sapabilir."*

X_dev = **15 dk** kaynağı: *"maksimum gün-içi saat sapması X_dev **(15dk)**"* [B §2.4, s.4].

**Bizde:** belgeli muafiyetlerle sağlanıyor — ayrıntı ve kanıt **§7**'de.

### H · Slot Pencereleri — **yalnızca [S sl.7]**, brief'te yok

> *"H · Slot Pencereleri — Düzenlenmiş havalimanlarında varış pencereleri."*

**Bizde:** dahil edilmedi (bkz. §2, Fark 1).

---

## 4. Kısıt dışı, ama aynı ölçüde bağlayıcı kurallar

| # | Kural | Birebir alıntı | Kaynak |
|---|---|---|---|
| K1 | Tüm uçuşlar ayarlanabilir olmalı | *"Takımların öncelikli olarak bütün uçuşları ayarlanabilir olarak çözmeye çalışması beklenir. Çözümün elde edilememesi durumunda (computational complexity, memory limit vs. gibi sebeplerle) tüm uçuşların bir alt kümesi ayarlanabilir olarak tanımlanabilir. Daha çok ayarlanabilir uçuşun daha iyi sonuç verme potansiyeli gözden kaçmamalıdır!"* | [B §2.1, s.3] · [S sl.4: *"Standard: Hepsi ayarlanabilir"*] |
| K2 | Yalnızca IST saatleri karar | *"fiziksel olarak karar verilen büyüklükler şunlardır: Ayarlanabilir uçuşların IST kalkış ve varış saatleri…"* | [B §2.3, s.4] |
| K3 | Sabit bağlantılar **veri**dir | *"Süresi sabit seçilen bağlantılar için yolculuk süresi ve yenme göstergeleri sabittir — bunları değişken/kısıt olarak değil, veri olarak ele alın."* | [B §7, s.7] |
| K4 | **Pyomo zorunlu** | *"Python ve Pyomo kullanılmalı, **farklı kullanımlar diskaliye sebebidir**"* | [B §5, s.6] · [S sl.2, sl.8] |
| K5 | Model ↔ kod tutarlılığı | *"Diskalifiye / ağır puan kaybı: uygun olmayan (kısıt ihlali içeren) çözümler, çalışmayan kod veya **teslim edilen modelle kodun tutarsız olması**."* | [B §6, s.7] · [S sl.9] |
| K6 | Gizli test örneği | *"Çözüm kalitesi, jüriye açık olmayan bir **gizli test örneği** üzerinde değerlendirilir."* | [B §6, s.6] |
| K7 | Eşik kuralları | *"Kod çalışmıyor veya çıktı üretmiyorsa, Kriter 2 sıfır puan alır. Örnek testte uygun (feasible) çözüm üretemeyen takımlar Kriter 2'den puan alamaz."* | [B §6.1, s.7] |

> **K5 bizim için en kritik maddedir.** Model dokümanında E2 ve B2'nin formülleri yazılı, kodda
> `CFG` bayrağıyla kapalıdır. Bu bir *tutarsızlık* değil, **belgeli tasarım kararıdır**: her ikisi de
> `docs/model_formulation.md` §10-U5 / §10-U6'da gerekçesi ve sayısal kanıtıyla kayıtlıdır ve
> `CFG` bayrağı tek satırla açılabilir. Sunumda bu çerçeve bozulmamalıdır.

---

## 5. **E2** — "Farkın ne kadarı fizik, ne kadarı sizin seçiminiz?"

### 5.1 Sorunun tam hâli

Brief, iki yönün **en iyi** yolculuk sürelerinin 30 dk'dan fazla ayrılmamasını istiyor.
Yolculuk süresi tanım gereği [B §2.2, s.4]:

```
J_π = T^IB_o  +  bağlantı boşluğu  +  T^OB_d
      └────────┬────────┘            └───┬───┘
       BLOK SÜRELERİ (legsum)         KARARIMIZ
       — uçuş süreleri, veri;         — yalnız bu
         kararımız YOK                  [60,300] dk
```

Yani `Jmin` üzerindeki kontrolümüz **yalnızca boşluk kadardır** ve boşluk [60, 300] ile sınırlı
olduğundan bir yönün Jmin'ini en fazla **240 dk** oynatabiliriz.

### 5.2 Gözlenen tablo (nihai çözüm)

| Ölçü | Değer |
|---|---|
| Her iki yönü aktif yön-çifti (E2'nin bağlayıcı olacağı) | **1 989** |
| Bunlardan \|Jmin_od − Jmin_do\| > Γ=30 dk olan | **1 413 (%71,0)** |
| Fark dağılımı | medyan **75 dk** · ort. 91 · p90 165 · **maks 475 dk** |
| İhlallerin **yalnız blok süresi farkı bile** Γ'yı aşanı | **1 003 (%71,0)** |
| \|Δ blok süresi\| | medyan **60 dk** · maks **385 dk** |
| \|Δ boşluk\| | medyan 40 dk · maks 240 dk *(yapısal tavan)* |

> **Not — önceki rakamın güncellenmesi.** `model_formulation.md` §10-U6'daki "%76 (1500/1972)"
> ölçümü **aşama-1 (byday) çözümünden**dir. Nihai (cilalanmış) çözümde doğru rakam
> **%71,0 (1 413/1 989)**'dur. Yön açısından fark yok, ama sunumda **nihai rakamı** kullanmalıyız.

### 5.3 Yapısal ayrıştırma — kanıtlı sınıflandırma

**Yöntem.** Bir yönün erişebileceği en iyi yolculuk süresi aralığı, boşluğun [60,300] serbestliği
altında en geniş hâliyle

```
R_yön = [ min legsum + 60 ,  min legsum + 300 ]        (genişlik 240 dk)
```

`min legsum` **saf blok süresidir; içinde sıfır karar vardır.** İki yönün aralıkları Γ=30 dk
yakınlığa getirilemiyorsa E2 **hiçbir tarifeyle** sağlanamaz. Bu bir **gevşetmedir**: gerçek
tarife bu aralığın tamamına erişemez, dolayısıyla "imkânsız" dediğimiz her çift **gerçekten**
imkânsızdır (kanıt tek yönlüdür ve bizim aleyhimize ihtiyatlıdır).

| Kategori | Kriter | Çift | Pay | ρ payı |
|---|---|---:|---:|---:|
| **A · Yapısal olarak imkânsız** — hiçbir tarife E2'yi sağlayamaz | \|Δ min legsum\| > 270 dk | **10** | %0,5 | %0,5 |
| **B · Ancak iyi yönü BOZARAK sağlanabilir** | 30 < \|Δ min legsum\| ≤ 270 dk | **1 237** | **%62,2** | %61,7 |
| **C · Bedelsiz sağlanabilir** (kötü yönü iyileştirerek) | \|Δ min legsum\| ≤ 30 dk | 742 | %37,3 | %37,7 |

**Kategori B'nin faturası:** E2'yi sert uygulasaydık, iyi yöndeki ürünü toplam **46 695 dakika**
bozmak zorunda kalırdık (medyan **35 dk/çift**, maks 225 dk) — yani yolcuya *daha kötü* bir en iyi
seçenek sunarak "denge" satın alırdık.

**Sonuç cümlesi:** Aktif yön-çiftlerinin **%62,7'sinde** (ρ'nun %62,3'ü) sert E2 ya imkânsızdır ya
da **yalnızca ürünü bozarak** mümkündür. En büyük blok asimetrisi **385 dk** (CUN–VCE ↔ VCE–CUN);
bu iki yön arasındaki uçuş süresi farkı, boşluk serbestliğimizin (240 dk) tamamından büyüktür.

### 5.4 Bunun yanında: çözücü kanıtı

Veri tarafı tek başına yeterli değil; hesaplama tarafı da bağımsız olarak engelliyor:
E2'nin `Jmin = min(...)` seçimi büyük-M gerektirir, LP gevşetmesini bozar ve HiGHS **tek bir günde
bile (~18 bin ikili) 150 saniyede uygun tamsayı çözümü (incumbent) bulamaz**; aynı gün E2 kapalıyken
saniyeler içinde çözülür. Bu bir **boyut** değil, **yapı** sorunudur.

### 5.5 Doğru çözüm ve yol haritası

Kategori **C**'nin %37,3 olması önemli bir bilgidir: bu çiftlerde E2 **kötü yönü iyileştirerek**
sağlanabilir — ki bu amaç fonksiyonuyla **aynı yöndedir**. Dolayısıyla doğru adım E2'yi sert kısıt
yapmak değil, **amaca ceza terimi olarak eklemektir (Soft-E2)**:

```
max  … − μ · Σ_(o,d),h  max(0, |Jmin_od,h − Jmin_do,h| − Γ)
```

Böylece Kategori C'de model dengeyi bedelsiz yakalar, Kategori A/B'de ise infeasible olmak yerine
**ölçülebilir bir ceza öder**. Bu, yol haritamızın (`docs/Buke_GELISTIRME_YOL_HARITASI`) 1. maddesidir.

---

## 6. **B2** — "Zorunlu sunumu da mı kapattınız?"

### 6.1 Kural ve gerilim

Brief iki kuralı **aynı anda** istiyor:

* **B2** [B §2.3, s.4]: uygun olan **her** bağlantı sunulmak zorunda.
* **E1** [B §4.5, s.5]: iki yönün sunulan bağlantı sayıları `|n_od − n_do| ≤ 0,20·(n_od + n_do)`.

Asimetrik bir pazarda (bir yönde çok, ters yönde az uygun bağlantı) bu ikisi **matematiksel olarak
çelişir**. Doğrudan kanıt: `B2_force_offer=True` ile gün 1 → **8 s'de infeasible**, gün 2 → **10 s'de
infeasible**, gün 3 → 60 s'de incumbent yok.

### 6.2 Nihai çözümdeki gerçek uyum (yeni ölçüm)

Tarife bir kez belirlendikten sonra bir bağlantıyı "sunmak" **hiçbir uçuşu kımıldatmaz** ve amacı
**artırır**. Dolayısıyla sunulmayan her uygun bağlantı ya bizim açığımızdır ya da E1 zorlamasıdır.
Testi yaptık:

| Ölçü | Değer |
|---|---:|
| Amaç evrenindeki aday bağlantı | 7 575 |
| Nihai tarifede boşluğu [60,300] olan (= sunulması **zorunlu**) | 7 192 |
| Bunlardan sunulan | **6 966** |
| **B2 uyumu** | **%96,86** |
| Sunulmayan (B2 ihlali) | 226 (%3,14) · ρ payı %2,56 |
| *Ters yönde hata* (uygun olmadığı hâlde sunulan) | **0** ✓ |

> **Önceki rakamın güncellenmesi.** `model_formulation.md` §10-U5'teki **%90,8**, aşama-1 (byday)
> ölçümüdür. Nihai çözümde doğru rakam **%96,86**'dır.

### 6.3 Kritik kanıt: **226 ihlalin %100'ü E1 zorlamasıdır**

Sunulmayan 226 bağlantının her birini tek tek ekleyip E1'i yeniden kontrol ettik:

| Sonuç | Adet | Pay |
|---|---:|---:|
| Eklendiğinde **E1'i ihlal eden** (⇒ bastırma zorunlu) | **226** | **%100,0** |
| Eklenebilir olduğu hâlde sunulmayan (⇒ **bizim açığımız**) | **0** | **%0,0** |

Ayrıca **1 989 yön-çiftinin 1 378'inde (%69,3) E1 tam bağlıdır** — iki yöne de tek bir bağlantı
eklemeye yer yoktur.

**Sonuç cümlesi:** B2'yi biz kapatmadık; **E1 kapattı.** Sunulmayan tek bir bağlantı bile bizim
tercihimiz değil, brief'in kendi E1 kuralının matematiksel zorunluluğudur. İki kural çeliştiğinde
E1'i tercih ettik; çünkü E1 hem sert kısıt olarak brief'in §4 listesindedir, hem de **mevcut
yayınlanmış tarifenin 379/2 001 yön-çiftinde (%19) ihlal ettiği** gerçek bir operasyonel sorundur —
biz onu **sıfıra** indiriyoruz.

---

## 7. **G** — "%42,8 muafiyet fazla değil mi?"

### 7.1 Önce: **%42,8 rakamı yanlış paydayla hesaplanmış**

Bağımsız doğrulayıcı **denetlediği** bağ sayısını raporlar (2 644) ve muafiyetleri ayrıca listeler
(1 131). Önceki ön-denetim notu bu ikisini oranlayarak %42,8 demişti. Doğru payda **toplam gün-arası
bağ sayısıdır**:

```
toplam bağ = denetlenen 2 644  +  muaf 1 131  =  3 775
gerçek muafiyet oranı = 1 131 / 3 775 = %30,0        (%42,8 DEĞİL)
```

### 7.2 Muafiyetlerin **%90,7'si fiilen kullanılmadı**

Muafiyet, o bağ için ±15 dk bandının *kurulmaması* demektir — bandın *aşılması* demek değildir.
Nihai tarifede her uçuş-rol grubunun ilk gününü çapa alıp sapmaları ölçtük:

| Ölçü | Değer |
|---|---:|
| Toplam gün-arası bağ | 3 775 |
| Muafiyetli bağ | 1 131 (%30,0) |
| — muaf **ama yine de ±15 dk bandında** kalan | **1 026 (%90,7)** |
| — muafiyeti **gerçekten kullanan** | **105** (tüm bağların **%2,8**'i) |
| Muaf olmayan bağlarda bant dışı | **0** ✓ |
| **G'nin fiilen sağlandığı bağ oranı** | **%97,2 (3 670 / 3 775)** |

Sebebi yapısal: λ=0,3 tarife-değişim cezası her günü mevcut tarifeye çapaladığından, bandı
kaldırılmış uçuşlar da mevcut saatlerinin yakınında kalır. **Muafiyet bir kapı açar, model o
kapıdan geçmez.**

### 7.3 Kalan 105 sapmanın kaynağı — dürüst tablo

| Ölçü | Değer |
|---|---:|
| Bant dışı bağ (bizim tarife) | **105** |
| — mevcut yayınlanmış tarifede **de** bant dışıydı (**miras**) | 46 (%43,8) |
| — mevcut'ta bantta olup **bizim bozduğumuz** | **59 (%56,2)** |
| Mevcuda göre kötüleşen bağ | 68 (medyan **+30 dk**, maks +60 dk) |
| Mevcuda göre iyileşen bağ | 5 |
| **Mevcut tarifenin kendi ihlali** | **157 bağ** |
| **Bizim ihlalimiz** | **105 bağ** |

Örnek (miras): **uçuş 2841** — yayınlanmış tarifede 2., 3., 4., 7. günler 03:20, 5. gün **14:10**
varıyor. 640 dk'lık yayılım **girdi verisindedir**; biz o günü hiç kımıldatmadık (0 dk).
Aynısı uçuş 2014/2015 için de geçerlidir (180/170 dk yayılım, bizim değişimimiz 0–10 dk).

**Dürüstlük notu — bunu da söylemeliyiz:** bağ *sayısı* olarak mevcut tarifeden iyiyiz (105 < 157),
ama **toplam yayılım** 7 850 dk'dan 14 270 dk'ya çıkıyor. Yani ihlalleri seyreltiyoruz ama toplam
düzensizliği artırıyoruz. Sebebi, muaf uçuşların bandının kalkması ve rekabetçilik kazancının
oradan gelmesidir. İyileştirme yolu: G muafiyetini rotasyon-önceliği yerine **λ_G ceza terimiyle**
kurmak (Soft-G) — yol haritasında 2. madde.

### 7.4 Muafiyet neden var? — bilinçli öncelik kararı

Bir gün, bant kuplajı yüzünden infeasible olduğunda iki kısıt çatışır: **A2 (uçak rotasyonu)** ve
**G (tarife düzenliliği)**. Biz **A2'yi öncelikledik** — uçak fiziği, tarife estetiğinden önce
gelir. Muafiyet keyfî değil, kurallıdır: önce yalnız rotasyon-korumalı uçuşların bandı bırakılır,
yetmezse o günün bandı tümüyle gevşetilir; **her muafiyet tek tek** `output/g_band_exemptions.csv`'ye
yazılır ve bağımsız doğrulayıcı bu listeyi belgeli muafiyet olarak ayrıca denetler.

---

## 8. Diğer iki soru

### 8.1 "919 uçuş neden sabit? Brief hepsini ayarlanabilir istiyor." [B §2.1, s.3]

5 473 olayın 4 554'ü (**%83,2**) ayarlanabilirdir. Sabit tutulan 919 olayın gerekçesi brief'in
saydığı *"computational complexity, memory limit"* değil, **veri eksikliğidir**: bu uçuşların
`Flight Pairs.xlsx`'te rotasyon partneri yoktur, dolayısıyla A2 kısıtı kurulamaz. Doğrulayamadığımız
bir uçak turunu bozmamak için ihtiyatlı davrandık.

Bunun **daha zayıf** bir versiyonu da var ve jüriye biz söylemeliyiz: 512 Pair kaydının yalnız 291'i
kullanılabilir durumda; **221 uçuş A2 koruması olmadan** oynayabiliyor (100'ü fiilen oynatılmış).
Ayrıca `Flight Pairs.xlsx` sayfa adı **`W26 Flight Pair 20260227`** (Kış 2026) iken tarife verisi
**Ağustos 2025 (Yaz)** dönemidir — bu, [R] dosyasında organizatörün kendi verdiği dosya adıyla
(`W26 Flight Pair 20260227 (1).xlsx`) sabittir; bizim eşleştirme hatamız değildir.

### 8.2 "+%4,72 kazanç ne kadar gerçek?" — ızgara artefaktı

Model 10 dk ızgarada çalışır [B §4.6, s.6], baseline ise ham dakikadan hesaplanır. Bu fark
kazancın **%14,1'ini (21 597 puan)** oluşturur. **Izgara-tutarlı iyileşme +%4,03**'tür.
Bu farkı sunumda **sorulmadan önce** biz söylemeliyiz; ayrıca aynı ızgara etkisini bu dokümanın
B2 ölçümünde de nötrledik (§6.2'deki test, ham dakika yerine çözümün kendi ızgara saatlerini
kullanır; öz-denetim 6 966/6 966 ✓).

---

## 9. Uyum karnesi — tek tablo

| Kısıt | Kaynak | Parametre | Durum | Kanıt |
|---|---|---|---|---|
| **A1** pencere + ızgara | [B §4.1 + §2.3] | ±60 dk, 10 dk kova | ✅ TAM | 4 554 hareket PASS |
| **A2** rotasyon | [B §4.1] | T^OB + 45 dk + T^IB | ✅ TAM | 1 709 tur, yeni ihlal **0** |
| **B1** bağlantı penceresi | [B §4.2 + §2.2] | [60, 300] dk | ✅ TAM | 6 966 bağlantı, dışı **0** |
| **B2** zorunlu sunum | [B §2.3] | — | 🟡 **%96,86** | ihlallerin **%100'ü E1 zorlaması** |
| **C** azalan getiri | [B §4.3 + §3.1] | 1, ½, ¼ … monoton | ✅ TAM | 4 660 pazar-gün PASS |
| **D** yenme + sıralama | [B §4.4 + §3.2] | J ≤ T^comp | ✅ TAM | fazla-beyan **0** |
| **E1** sayı dengesi | [B §4.5] | α = 0,20 | ✅ TAM | 2 001 çift, **0 ihlal** |
| **E2** süre dengesi | [B §4.5] | Γ = 30 dk | ❌ KAPALI | %62,7 çiftte imkânsız/bedelli |
| **F** hub kapasitesi | [B §4.6] | 10 / 15 | ✅ TAM | aşan kova **0** |
| **G** düzenlilik | [B §4.7] | X_dev = 15 dk | 🟡 **%97,2** | 105/3 775 bağ; 46'sı miras |
| **H** slot pencereleri | **yalnız [S sl.7]** | — | ➖ Brief'te yok, veri yok | belgelendi |

**Karşılaştırma çapası:** aynı kurallar altında **mevcut yayınlanmış tarife** F'yi 96 kovada,
E1'i 379 yön-çiftinde, G'yi 157 bağda ihlal eder. Bizim çözümümüz sırasıyla **0 · 0 · 105**'tir.

---

## 10. Yeniden üretim

```bash
python preaudit/08_kapali_kisit_kanitlari.py      # §5, §6, §7'deki TÜM rakamlar
python preaudit/02_izgara_ve_rotasyon_olcumu.py   # §8.1 ve §8.2
python src/05_validate_solution.py                # bağımsız kısıt doğrulaması
```

Üretilen kanıt dosyaları:

| Dosya | İçerik |
|---|---|
| `output/audit_e2_ayristirma.csv` | 1 989 yön-çifti · gözlenen fark · min legsum · kategori · zorunlu bozulma |
| `output/audit_b2_sunulmayan.csv` | 226 sunulmayan bağlantı · ρ · n_od / n_do (E1 durumu) |
| `output/audit_g_muafiyet_kullanimi.csv` | 3 775 gün-arası bağ · bizim sapma · mevcut tarifedeki sapma · muaf mı |

Betik `src/` altındaki hiçbir modülü import etmez; yalnız `derived/` (veri katmanı) ve `output/`
(çözüm) dosyalarını okuyup sıfırdan hesaplar. Boşluk yeniden kurulumu, çözümün kendi değerleriyle
**6 966/6 966 birebir** doğrulanmıştır.

---

## 11. Jüri cevap kartları

**S: "E2'yi neden kurmadınız?"**
> "İki bağımsız nedenle. Veri tarafı: yolculuk süresi = blok süreleri + boşluk; blok süreleri veridir,
> kararımız yalnız boşluktur ve boşluk [60,300] ile sınırlı olduğundan bir yönün en iyi süresini en
> fazla 240 dk oynatabiliriz. Ölçtük: aktif yön-çiftlerinin **%62,7'sinde** Γ=30 dk ya hiçbir tarifeyle
> ulaşılamaz ya da **ancak iyi yöndeki ürünü bozarak** — toplam 46 695 dakikalık ürün bozulması
> pahasına. Çözücü tarafı: E2'nin min-seçimi tek günde bile HiGHS'in incumbent bulmasını engelliyor.
> Kısıtı sessizce atmadık: model dokümanında formülü duruyor, kapalı olduğu ve nedeni §10-U6'da
> yazılı, ve doğru çözümü — amaca ceza terimi olarak eklenen Soft-E2 — yol haritamızın 1. maddesi."

**S: "B2'yi de mi kapattınız?"**
> "Kapatan biz değiliz, **E1**. Nihai çözümde B2 uyumumuz **%96,86**. Sunulmayan 226 bağlantının
> her birini tek tek ekleyip test ettik: **%100'ü** eklendiği anda E1'in α=0,20 dengesini ihlal
> ediyor. Tarife o noktada sabit olduğu için sunmak bedavaydı ve amacı artıracaktı — model yine de
> sunmadıysa tek sebep E1'dir. Brief'in iki kuralı asimetrik pazarlarda matematiksel olarak
> çelişiyor; biz sert kısıt listesinde olan E1'i tercih ettik ve onu **0 ihlalle** sağlıyoruz."

**S: "G'de muafiyet oranınız çok yüksek."**
> "Önce bir düzeltme: doğru oran %42,8 değil **%30,0** — önceki rakam denetlenen bağ sayısını payda
> almış. Asıl cevap şu: muafiyetlerin **%90,7'si fiilen kullanılmadı**; uçuş bandı serbest olduğu
> hâlde ±15 dk içinde kaldı, çünkü λ=0,3 cezası onu mevcut saatine çapalıyor. Gerçekten bant dışına
> çıkan **105 bağ var, tüm bağların %2,8'i** — ve bunların **%43,8'i zaten yayınlanmış tarifede
> bant dışıydı**. Mevcut tarife 157 bağda ihlal ediyor, biz 105'te. Dürüst olmak gerekirse toplam
> yayılım 7 850'den 14 270 dakikaya çıkıyor; bunu da Soft-G ile çözmeyi yol haritasına yazdık."

**S: "Brief'te 7 kısıt var, sunumda 8. H'yi neden atladınız?"**
> "Farkı biz de tespit ettik. H yalnız kick-off sunumunun 7. slaydında var; brief'in §4 listesinde
> yok ve hangi havalimanının slot-koordineli olduğu **veri paketinde verilmemiş**. Uydurmak yerine
> model dokümanına açık eksiklik notu olarak yazdık. Pencere verisi gelirse uygulaması, ilgili
> varışların zaman kümesini daraltmaktan ibarettir."
