# -*- coding: utf-8 -*-
"""Bolum 3 — 03_model.py (cekirdek)."""

F = "03_model.py"

ITEMS = [
    ("h1", ("3", "03_model.py — MIP Modeli (projenin çekirdeği)")),

    ("box", ("Bu dosya ne yapar?",
             "`derived/` katmanını okur, onu bir **Karışık Tamsayılı Programlama (MIP)** "
             "modeline çevirir, HiGHS çözücüsüyle çözer ve sonucu `output/` altına yazar. "
             "1357 satırın tamamı tek bir soruya hizmet eder: *hangi uçuşun IST saati kaç "
             "dakika kaydırılırsa, tüm kısıtlar korunarak gelir-ağırlıklı rekabetçilik en "
             "yükseğe çıkar?*")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`derived/` — 8 CSV"],
              ["Çıktı", "`output/optimized_schedule.csv`, `market_results.csv`, "
                        "`selected_connections.csv`, `g_band_exemptions.csv`, "
                        "`results_summary.md`"],
              ["Çalıştırma", "`python src/03_model.py byday` (tam veri, teslim modu)"],
              ["Diğer modlar", "`(argümansız)` küçük alt-örnek · `full` tek-MIP denemesi · "
                               "`sweep` λ taraması"],
              ["Bağımlılık", "`pandas`, `numpy`, `pyomo`, `highspy`"],
              ["Süre", "byday ≈ 5–10 dk (gün başına ≤ 150 s)"]],
             [3.0, 14.0], 8.8)),
    ("p", "Bu bölüm uzundur çünkü dosya uzundur. Kolay takip için sırayı şöyle kuruyoruz: "
          "önce **ayarlar**, sonra **veriyi modele hazırlama**, sonra **kısıt kısıt model "
          "kurma**, sonra **çözme**, en sonda **haftayı güne bölerek koşturma ve çıktı "
          "yazma**."),

    # =====================================================================
    ("h2", "3.1  Docstring — modelin özeti ve alınan ölçekleme kararları"),
    ("code", (F, 1, 20, "uygulanan kısıtların listesi")),
    ("p", "İlk 20 satır, `docs/model_formulation.md` ile birebir eşleşen bir **kısıt "
          "envanteridir**. Yıldızlı (*) olanlar tam ölçekte özel muamele görür — nedenleri "
          "hemen altında yazılıdır:"),
    ("code", (F, 21, 44, "ölçekleme kararları ve çalıştırma modları")),
    ("p", "Bu 24 satır bir yazılım dokümantasyonundan çok bir **mühendislik günlüğüdür**. "
          "Her karar, denendiği ve neden o şekilde bırakıldığıyla birlikte yazılmış:"),
    ("tbl", (["Karar", "Ne yapıldı?", "Gerekçe"],
             [["**A2**", "Bloklar varsa brief-exact minimum tur; yoksa mevcut tur çapası",
               "Gece-aşan turlarda mevcut desen korunur, gün-bağlaşımı yaratılmaz"],
              ["**B2**", "Varsayılan **kapalı**",
               "B2 her uygun bağlantıyı zorlar; asimetrik pazarlarda E1 dengesiyle "
               "**infeasible** olur (bisection ile doğrulandı). Amaç zaten sunmayı ödüllendirir"],
              ["**E2**", "Tam ölçekte **kapalı**",
               "Jmin min-seçimi büyük-M'i HiGHS'te incumbent buldurmuyor; küçük ölçekte açık "
               "ve doğrulanmış"],
              ["**F**", "Brief'in gerçek 10/15 kapasitesi **uygulanır**",
               "Veri bulgusu: sabit uçuşlar baz kapasiteyi hiç aşmıyor → rezidüel kapasite ≥ 0"],
              ["**G**", "Saat-içi, grup başına ortak bant",
               "Pencerede ortak bant kurulamayanlar atlanır ve raporlanır"]],
             [1.7, 5.6, 9.7], 8.4)),
    ("box", ("Bu neden değerli?",
             "Bir jüri \"neden E2'yi kapattınız?\" diye sorduğunda cevap kodun içinde, "
             "tanı yöntemiyle birlikte yazılıdır: *\"çekirdek + E2 tek başına çözülemiyor; "
             "A2/G/F/E1 hepsi hızlı\"*. Bu, kararın keyfî değil **ölçülmüş** olduğunu "
             "gösterir.", "ok")),

    # =====================================================================
    ("h2", "3.2  Ayarlar: CFG ve PRESETS"),
    ("code", (F, 46, 62, "import'lar ve konsol kodlaması")),
    ("p", "`sys.stdout.reconfigure(encoding=\"utf-8\")` küçük ama gerekli: Windows konsolu "
          "varsayılan olarak cp1254 kullanır ve `π`, `Δ`, `≤` gibi karakterlerde çöker. "
          "`try/except` içine alınmıştır çünkü bazı ortamlarda bu metot yoktur — kod o "
          "durumda da çalışmaya devam eder."),
    ("code", (F, 65, 102, "merkezî yapılandırma sözlüğü")),
    ("p", "CFG dört gruba ayrılmıştır. En önemli anahtarlar:"),
    ("tbl", (["Anahtar", "Varsayılan", "Ne yapar?"],
             [["`delta_min`", "10", "Zaman ızgarasının adımı Δ. Saatler 10 dakikanın katı olur"],
              ["`wdev_min`", "60", "Bir uçuş mevcut saatinden en fazla ±60 dk kaydırılabilir"],
              ["`L_min` / `U_min`", "60 / 300", "Bağlantı boşluğu penceresi"],
              ["`shift_penalty`", "0.0", "λ — tarife-değişim cezası (byday'de 0.3 verilir)"],
              ["`alpha`", "0.20", "E1 yönsel dengesizlik toleransı"],
              ["`tau_min`", "45", "τ — minimum yer süresi (A2)"],
              ["`xdev_min`", "15", "G — günler arası maksimum saat sapması"],
              ["`cap_dep` / `cap_arr`", "10 / 15", "F — kova başına kalkış/varış kapasitesi"],
              ["`B2_force_offer`", "False", "B2 kapalı (E1 ile çatışıyor)"],
              ["`E2_balance`", "True", "Küçük örnekte açık; `full` profilinde kapatılır"],
              ["`solver`", "`appsi_highs`", "Pyomo'nun HiGHS arayüzü"],
              ["`time_limit` / `mip_gap`", "None / None", "Profil bunları doldurur"]],
             [4.0, 2.6, 10.4], 8.4)),
    ("code", (F, 104, 116, "\"full\" profili")),
    ("p", "PRESETS, CFG'yi tek satırda topluca değiştirir: `CFG.update(PRESETS[\"full\"])`. "
          "Dikkat edilecek nokta **`\"days\": None`**'dur:"),
    ("box", ("Gün listesi neden hardcode edilmiyor?",
             "Gizli test verisi 7 gün yerine 5 veya 10 gün içerebilir. `days=None` demek "
             "\"veride ne varsa onu kullan\" demektir; gerçek liste `all_operation_days()` "
             "ile `tk_connections.csv`'den okunur. Aynı ilke `markets`, `top_k_markets` için "
             "de geçerlidir — `None` = sınırlama yok.", "info")),

    # =====================================================================
    ("h2", "3.3  Veriyi okumak"),
    ("code", (F, 120, 125, "operasyon günlerini veriden türet")),
    ("code", (F, 128, 148, "load_data — sekiz CSV'yi tek çağrıda")),
    ("p", "Dikkat çekici üç ayrıntı:"),
    ("bul", ["**135–138:** Sıralama tablosunun sütun adları farklı gelebilir diye "
             "**konumsal** sabitleme yapılır (`rank.columns = [\"N\",\"b\",\"s\",\"W\"]`), ama "
             "önce sütun **sayısı** doğrulanır. Şema beklenenden farklıysa anlaşılır hata verir.",
             "**144–147:** `flight_block_times.csv` **isteğe bağlıdır**. Yoksa `blocks = None` "
             "döner ve A2 kısıtı ihtiyatlı moda (mevcut tur çapası) geçer. Eski şemayla "
             "uyumluluk böyle korunur.",
             "**139:** Rotasyon partneri olmayan uçuşlar `set` olarak döner — üyelik testi "
             "O(1) olsun diye."]),
    ("code", (F, 151, 161, "rotation_pairs — hangi gidiş hangi dönüşle eşleşir?")),
    ("p", "`Flight Pairs` tablosunda aynı `Pair` etiketini taşıyan uçuşlar **aynı uçağı** "
          "paylaşır. Fonksiyon bunları `Orig == \"IST\"` (giden) ve `Dest == \"IST\"` (gelen) "
          "olarak ayırır ve tüm (giden, gelen) kombinasyonlarını üretir. Çıktı, A2 kısıtının "
          "kurulacağı çift listesidir."),
    ("code", (F, 164, 201, "select_markets — alt-örnek seçimi")),
    ("p", "Bu fonksiyon esasen **geliştirme/hata ayıklama** içindir: tüm veriyle çalışmadan "
          "önce küçük ve anlamlı bir alt-örnekte tüm kısıtları elle doğrulamak için. Tam "
          "veri koşusunda (`full` profili) filtrelerin hepsi kapalıdır ve fonksiyon "
          "pratik olarak \"hepsini seç\" der. Yine de mantığı öğreticidir:"),
    ("num", ["Aday havuzu: TK bağlantısı olan + ρ'su tanımlı + seçilen günlerde bağlantısı "
             "bulunan pazarlar (177–178).",
             "`require_competitors` — rakibi olmayan pazarlarda sıralama terimi tanımsızdır; "
             "test için bunlar elenir (179–182).",
             "`prefer_improvable` — baseline'da **pencere dışı** en az bir bağlantısı olan "
             "pazarları öne alır; yani \"iyileştirilebilir\" olanları (183–189).",
             "`add_reverse` — seçilen her pazarın **ters yönü** de eklenir. E1 dengesi bir "
             "yön-çifti kısıtı olduğu için, tek yönü seçmek E1'i test edilemez kılar (194–200)."]),

    # =====================================================================
    ("h2", "3.4  `Instance` ve `build_instance()` — veriden model nesnelerine"),
    ("code", (F, 205, 207, "boş veri kabı sınıfı")),
    ("p", "Projedeki iki sınıftan biri. Gövdesi `pass`'tır çünkü görevi davranış değil, "
          "**taşımaktır**: `build_instance()` ona 12'den fazla alan atar ve `build_model()` "
          "bu tek nesneyi alır. Alternatif — 12 parametreli bir fonksiyon imzası — hem "
          "okunmaz hem hataya açık olurdu."),
    ("code", (F, 210, 231, "zaman referansı, mutlak dakika ve ızgaraya oturtma")),
    ("p", "Üç kavram burada doğar ve dosyanın sonuna kadar yaşar:"),
    ("tbl", (["Kavram", "Kod", "Anlamı"],
             [["`t0`", "satır 224",
               "Tüm zaman damgalarının en küçüğünün gece yarısı. **Zaman ekseninin sıfır "
               "noktası.**"],
              ["`abs_min(ts)`", "226–227",
               "Bir zaman damgasını `t0`'dan itibaren geçen **mutlak dakikaya** çevirir. "
               "Gün 3'ün 08:00'i ≈ 2×1440 + 480"],
              ["`snap(m)`", "229–230",
               "Dakikayı en yakın 10'un katına yuvarlar. Izgaranın tanımı budur"]],
             [2.6, 2.0, 12.4], 8.6)),
    ("box", ("Neden mutlak dakika?",
             "Gerçek `datetime` nesneleriyle doğrusal kısıt yazılamaz. Her şeyi tek bir "
             "sayı eksenine (dakika) taşıyarak `θ_dep − θ_arr ≥ 60` gibi kısıtlar doğrudan "
             "yazılabilir hâle gelir. Sonuçta bu sayılar `t0 + Timedelta(minutes=...)` ile "
             "gerçek saate geri çevrilir.", "info")),
    ("code", (F, 232, 247, "olaylar (events) — modelin karar birimleri")),
    ("p", "Bu 16 satır modelin **atomudur**. Anlamak için üç soruyu ayırmak gerekir:"),
    ("h3", "Olay nedir?"),
    ("p", "Bir **olay**, \"şu uçuş numarasının, şu roldeki (varış/kalkış), şu andaki IST "
          "hareketi\"dir. Anahtarı `(flno, role, snap(cur))` üçlüsüdür."),
    ("h3", "Neden bağlantı başına değil, olay başına karar veriyoruz?"),
    ("p", "Çünkü **bir uçuş birden fazla bağlantıda yer alır**. IST'e gelen bir uçuş, oradan "
          "kalkan 20 farklı uçuşla 20 bağlantı oluşturabilir. Eğer her bağlantı için ayrı "
          "saat kararı verilseydi, aynı uçağa 20 farklı varış saati atanabilirdi. Olay "
          "sözlüğü (`events`) bunu yapısal olarak imkânsız kılar: **aynı anahtar → aynı "
          "karar.** Bu, modelin doğruluğunu garanti eden en önemli tasarım kararıdır."),
    ("h3", "Aday saatler nasıl üretiliyor?"),
    ("bul", ["Uçuşun rotasyon partneri yoksa (`flno in fixed_flnos`) **ayarlanamaz**: "
             "`cands = [cur]`, tek seçenek, hiç kımıldamaz.",
             "Ayarlanabilirse `cands` = mevcut saatten ±60 dk aralığında 10'ar dakikalık tüm "
             "değerler → **13 aday** (−60, −50, …, 0, …, +50, +60)."]),
    ("img", ("f05_izgara_aday.png",
             "Şekil 3.1 — (A1) Bir olayın 13 aday kovası. Model tam birini seçer.")),
    ("code", (F, 249, 259, "bağlantılar (π) listesi")),
    ("p", "Her TK bağlantı satırı için varış ve kalkış olayları `get_event` ile alınır (varsa "
          "mevcut olan döner, yoksa yenisi yaratılır) ve bağlantı bu **iki olay kimliğiyle** "
          "tanımlanır. `legsum` sabittir; `gap_cur` mevcut tarifedeki boşluktur (baseline "
          "hesabı için)."),
    ("code", (F, 261, 272, "extra_use — modellenmeyen uçuşların fiziksel yükü")),
    ("box", ("Bu blok neden var? (\"amaç evreni eksikliği\")",
             "ρ'su olmayan pazarlar amaç fonksiyonundan **dışlanır** — ama o uçuşlar hâlâ "
             "havada! IST pistini ve kapılarını fiziksel olarak dolduruyorlar. Onları F "
             "kapasitesinde saymamak, gerçekte olmayan bir boşluk yaratıp modelin oraya uçuş "
             "yerleştirmesine izin verirdi. `extra_use`, bu uçuşları **karar değişkeni "
             "olmadan, sabit doluluk olarak** kova sayacına ekler.", "warn")),
    ("code", (F, 274, 284, "full_role_time — A2 için aynı açığın kapatılması")),
    ("p", "`extra_use` F kısıtındaki açığı kapatır; `full_role_time` **aynı açığı A2 için** "
          "kapatır. Bir rotasyon ortağının bağlantısı amaç evreninde değilse o günkü olay hiç "
          "kurulmaz ve A2 kısıtı o gün için hiç oluşmazdı. Bu sözlük, tüm günler ve tüm "
          "pazarlar için **gerçek fiziksel saatleri** tutar ve A2 bloğu bunları *çapa* "
          "(anchor) olarak kullanır."),
    ("box", ("Bu düzeltmenin hikâyesi",
             "Bu açığı **bağımsız doğrulayıcı (05) yakaladı**. Wdev=90 denenirken çözücü "
             "kaydırmayı artırınca gerçek bir A2 ihlali doğdu (uçuş 2200/2201, gün 2). "
             "05'in notu `05_validate_solution.py` satır 52–60'ta hâlâ duruyor. Çift kayıt "
             "ilkesinin işe yaradığının kanıtı.", "ok")),
    ("code", (F, 286, 296, "md — pazar-gün grupları")),
    ("p", "`md` sözlüğü `(pazar, gün)` anahtarıyla şunları toplar: ρ ağırlığı, rakip sayısı N, "
          "rakip taşıyıcıların T_comp değerleri ve bu gruba ait bağlantıların indeksleri. "
          "Ödül hesabı **grup düzeyinde** yapılır — çünkü hem azalan getiri (C) hem sıralama "
          "(D) pazar bazlıdır."),
    ("code", (F, 298, 314, "b_od — başlangıç sırasının hesabı")),
    ("p", "Sıralama ödülü bir **iyileştirme ödülüdür**: \"b. sıradan s. sıraya çıktın, işte "
          "ödülün.\" Dolayısıyla b_od, **mevcut tarifenin sırası** olmalıdır. Kod bunu tam "
          "olarak s ile aynı formülden türetir:"),
    ("num", ["Mevcut tarifede pencere içinde ([60,300]) olan bağlantılar bulunur (`offered0`).",
             "Bunların **en iyi J**'si hesaplanır (`j_best0`).",
             "Bu J'nin yendiği rakip sayısı sayılır (`beaten0`).",
             "`b_od = clip(N − beaten0, 1, N)` — s formülüyle **birebir aynı taban**."]),
    ("box", ("Neden bu kadar titiz davranılmış?",
             "Ödül tablosunun **köşegeni** (b == s) \"değişim yok\" nötr referansıdır. Eğer "
             "b_od farklı bir kuralla hesaplansaydı, mevcut tarife köşegenin dışına düşer ve "
             "**hiçbir şey yapmadan** sıralama ödülü kazanırdı — yani baseline şişer, "
             "iyileşme sahte görünürdü. Kodun yorumu eski kuralın (faster+1) pazarların "
             "~%29'unda tam bu hatayı yaptığını yazıyor.", "warn")),
    ("code", (F, 316, 331, "yardımcı indeksler ve Instance'ın doldurulması")),
    ("p", "`ev_by_flno_role` — `(uçuş no, rol) → [olay kimlikleri]` haritası. A2 ve G "
          "kısıtları bu haritayı kullanarak \"bu uçuşun tüm günlerdeki olayları\" sorgusunu "
          "O(1) yapar. Son 10 satır `Instance` nesnesini doldurur ve döndürür."),

    # =====================================================================
    ("h2", "3.5  Ödül ve zaman ifadeleri"),
    ("code", (F, 335, 345, "sıralama ödül tablosu ve sorgusu")),
    ("p", "`rank_weight_table` lookup CSV'sini `(N, b, s) → W` sözlüğüne çevirir; "
          "`rank_reward` ise \"N rakip varken b'den başlayıp, `beaten` rakip yenerek s'ye "
          "çıktım\" sorgusunun ödülünü döndürür. `s = clip(N − beaten, 1, N)` — daha çok "
          "rakip yenmek s'yi küçültür, küçük s daha iyi sıralamadır."),
    ("code", (F, 348, 354, "theta_expr — bir olayın saatinin cebirsel ifadesi")),
    ("p", "Modelin en çok çağrılan yardımcısı. Olay **ayarlanabilirse** θ = Σ (aday değeri × "
          "o adayın ikili değişkeni) — yani doğrusal bir ifade döner. **Sabitse** sadece bir "
          "sayı döner. Bu tek fonksiyon sayesinde kısıtlar \"sabit mi değişken mi\" ayrımı "
          "yapmadan yazılabilir:"),
    ("box", ("Neden Σ v·x[e,v] işe yarıyor?",
             "A1 kısıtı Σ_v x[e,v] = 1 olduğu için, ikili değişkenlerden **tam biri** 1'dir. "
             "O zaman Σ v·x[e,v] tam olarak seçilen adayın değerine eşittir. Sürekli bir saat "
             "değişkeni yerine bu \"tek-sıcak\" (one-hot) kodlama seçilmiştir — çünkü ileride "
             "**F kapasitesi** ve **P cezası** doğrudan bu değişkenler üzerinden, ek değişken "
             "ve big-M olmadan yazılabiliyor.", "ok")),

    # =====================================================================
    ("h2", "3.6  `build_model()` — değişkenler ve (A1)"),
    ("code", (F, 356, 375, "x, y ve A1 kısıtı")),
    ("tbl", (["Değişken", "İndeks", "Anlamı"],
             [["`x[eid, v]`", "ayarlanabilir olay × aday saat",
               "Bu olay `v` saatine atandı mı? (0/1)"],
              ["`y[pi]`", "her bağlantı", "Bu bağlantı **sunuluyor** (uygun) mu? (0/1)"],
              ["`s[pi]`", "her bağlantı (yalnız B2 açıksa)",
               "Uygun değilse \"çok kısa\" mı \"çok uzun\" mu? (0/1)"]],
             [3.4, 5.6, 8.0], 8.6)),
    ("p", "**Satır 372–375 = Kısıt A1**: her ayarlanabilir olay için `Σ_v x[eid,v] == 1`. "
          "Türkçesi: \"her uçuş hareketine tam bir saat ata.\" Üç satırlık bu kısıt, modelin "
          "tüm doğrusal yapısını mümkün kılar."),
    ("p", "`m.cons = pyo.ConstraintList()` — Pyomo'da adlandırılmış kısıt blokları yerine tek "
          "bir listeye ekleme yapılır. Kısıtlar farklı mantıklardan geldiği için bu daha "
          "pratiktir; kaç kısıt eklendiği ayrı sayaçlarla (`m._n_a2`, `m._n_g`, `m._n_f`) "
          "izlenir."),

    # =====================================================================
    ("h2", "3.7  (B1) Bağlantı uygunluğu ve big-M tekniği"),
    ("code", (F, 377, 400, "gap ifadesi, sıkı big-M ve B1/B2")),
    ("p", "Bu blok modelin **mantıksal kalbidir**. Adım adım:"),
    ("h3", "1) Boşluk ifadesi (380)"),
    ("p", "`gap[pi] = θ_kalkış − θ_varış`. İki `theta_expr` çağrısının farkı — doğrusal bir "
          "ifade."),
    ("h3", "2) Ulaşılabilir aralık (382–383)"),
    ("p", "Adaylar sınırlı olduğu için boşluk da sınırlıdır: en küçük boşluk = (en erken "
          "kalkış) − (en geç varış), en büyük boşluk = (en geç kalkış) − (en erken varış). "
          "Bu iki sayı `gmin` ve `gmax` olarak saklanır."),
    ("h3", "3) B1 kısıtı big-M ile (386–390)"),
    ("p", "İstenen mantık: **y_π = 1 ise 60 ≤ boşluk ≤ 300.** Bu bir \"eğer-ise\" ifadesidir "
          "ve doğrusal programlamada doğrudan yazılamaz. Big-M numarası şudur:"),
    ("box", ("gap ≥ L − Mlo·(1 − y)  nasıl çalışır?",
             "**y = 1 ise:** sağ taraf L − 0 = 60 olur → kısıt `boşluk ≥ 60` olarak devreye "
             "girer.\n"
             "**y = 0 ise:** sağ taraf 60 − Mlo olur. Mlo = max(0, L − gmin) seçildiği için "
             "bu değer, boşluğun alabileceği **en küçük değerden bile küçüktür** → kısıt "
             "otomatik sağlanır, yani **etkisizleşir**. Üst sınır için de simetrik olarak "
             "Mhi = max(0, gmax − U) kullanılır.", "info")),
    ("p", "**M'in küçük seçilmesi kritiktir.** Gereğinden büyük bir M, MIP'in *doğrusal "
          "gevşemesini* zayıflatır ve çözücü ağaçta kaybolur. Buradaki M'ler **yön-yerel** "
          "olarak, o bağlantının gerçekten ulaşabileceği aralıktan hesaplanır — mümkün olan "
          "en sıkı değerler."),
    ("h3", "4) Erken sabitleme (391–393)"),
    ("p", "Eğer `gmax < L` veya `gmin > U` ise bu bağlantı **hiçbir kaydırma kombinasyonuyla** "
          "uygun olamaz → `y[pi] == 0` doğrudan sabitlenir. Çözücünün araması gereken alan "
          "küçülür."),
    ("h3", "5) B2 (kapalı)"),
    ("p", "394–400 arası B2'yi kurar: \"uygunsa sunmak zorundasın\". `s[pi]` ayrık seçicisi "
          "y=0 durumunda boşluğun ya ℓ−Δ'nın altında ya u+Δ'nın üstünde olmasını zorlar. "
          "Varsayılan olarak kapalıdır çünkü E1 dengesiyle çatışıp modeli infeasible yapar."),

    # =====================================================================
    ("h2", "3.8  (C) Azalan getiri — neden 5. bağlantı değersizdir?"),
    ("img", ("f06_azalan_getiri.png",
             "Şekil 3.2 — Ödül dizisi (½)^(j−1). Toplam ödül 2'ye yakınsar.")),
    ("code", (F, 402, 418, "z değişkenleri ve monoton doldurma")),
    ("p", "Gerçek hayatta bir pazarda **ilk** aktarma seçeneği çok değerlidir; ikincisi biraz "
          "daha az; beşincisi neredeyse hiç. Model bunu şöyle kurar:"),
    ("num", ["Her pazar-gün grubu için `M` adet slot değişkeni `z[i,j]` tanımlanır (M = o "
             "gruptaki aday bağlantı sayısı).",
             "**Bağlama kısıtı (416):** `Σ y[pi] == Σ z[i,j]` — kaç bağlantı sunuluyorsa o "
             "kadar slot dolu olmalı.",
             "**Monotonluk (417–418):** `z[i,j] ≥ z[i,j+1]` — slotlar baştan doldurulmalı. "
             "Bu olmadan çözücü 1. slotu boş bırakıp 1 numaralı ödülü almadan 3. slotu "
             "doldurabilirdi.",
             "Ödül ağırlıkları `Wc[(i,j)] = 0.5^(j−1)` olarak önceden hesaplanır (411)."]),
    ("box", ("Neden ayrı z değişkenleri? y'ye doğrudan azalan ağırlık verilemez mi?",
             "Hayır — çünkü \"kaçıncı bağlantı\" olduğu, hangi bağlantıların seçildiğine "
             "bağlıdır ve önceden bilinemez. `z` dizisi \"kaç tane sunuldu\" sayısını "
             "**ödüle** çevirmenin doğrusal yoludur: n bağlantı sunulursa ilk n slot dolar ve "
             "toplam ödül tam olarak 1 + ½ + ¼ + … + (½)^(n−1) olur.", "ok")),

    # =====================================================================
    ("h2", "3.9  (D) Rakip yenme ve sıralama ödülü"),
    ("img", ("f07_rakip_siralama.png",
             "Şekil 3.3 — Yenilen rakip sayısı, sıralama ödülünün girdisidir.")),
    ("h3", "Adım 1 — w: \"bu bağlantı bu rakibi yeniyor mu?\""),
    ("code", (F, 420, 441, "koşullu w değişkenleri ve üç durum ayrımı")),
    ("p", "Yenmek demek J ≤ T_comp demektir. J = legsum + boşluk olduğundan bu, boşluk üzerine "
          "bir üst sınıra dönüşür: **boşluk ≤ G**, burada `G = T_comp − legsum`. Kod bu "
          "eşiği ulaşılabilir aralıkla karşılaştırıp **üç duruma** ayırır:"),
    ("tbl", (["Durum", "Koşul", "Ne yapılır?", "Kazanç"],
             [["Asla yenemez", "`G < lo`", "Değişken **yaratılmaz** (`continue`)",
               "Boş yere değişken üretilmez"],
              ["Hep yener", "`G ≥ U`", "`beat_eq_y` işaretlenir; w yerine doğrudan `y` "
                                       "kullanılır", "Bir değişken + iki kısıt tasarrufu"],
              ["Koşullu", "`lo ≤ G < U`", "Gerçek `w` değişkeni + iki kısıt kurulur",
               "Yalnız gerçekten gerekli olanlar"]],
             [2.8, 2.4, 7.4, 4.4], 8.4)),
    ("box", ("Bu ayrım neden bu kadar önemli?",
             "Tam veride binlerce (bağlantı × rakip) çifti vardır. Hepsine değişken açmak "
             "modeli gereksiz yere şişirir. Bu üç yollu ayrım, model boyutunu **büyük "
             "ölçüde** küçültür — büyük MIP'lerde çözülebilirlik ile çözülemezlik arasındaki "
             "fark tam olarak bu tür ayıklamalardır. `m.w = pyo.Var(pyo.Any, dense=False)` "
             "ise **seyrek** bir değişken havuzudur: yalnız istenen indeksler yaratılır.", "ok")),
    ("h3", "Adım 2 — β: \"bu rakip yenildi mi?\""),
    ("code", (F, 442, 457, "rakip düzeyinde toplama")),
    ("p", "Bir rakibi yenmek için **en az bir** sunulan bağlantının onu yenmesi yeterlidir. "
          "Kısıt `β ≤ Σ w` şeklindedir — yani hiçbir bağlantı yenmiyorsa β 0'a zorlanır. "
          "Ters yön (`β ≥ ...`) gerekmez çünkü **amaç fonksiyonu β'yı yukarı iter**: β "
          "büyüdükçe ödül artar, dolayısıyla çözücü onu mümkün olan en yükseğe çeker. "
          "Gereksiz kısıt yazmamak yine model boyutu kazancıdır."),
    ("h3", "Adım 3 — γ: yenilen sayısını ödüle çevirme"),
    ("code", (F, 459, 475, "seçici değişkenler ve amaç terimleri")),
    ("p", "Ödül tablosu ayrık bir fonksiyondur: \"2 rakip yendiysen şu kadar, 3 yendiysen bu "
          "kadar.\" Bunu doğrusal modele sokmanın standart yolu **seçici (indicator) "
          "değişken dizisidir**:"),
    ("bul", ["`γ[i,bn]` — \"bu pazarda tam olarak `bn` rakip yenildi\" göstergesi.",
             "`Σ γ == 1` (472) — tam bir değer seçilmeli. **Koşulsuzdur**: hiç rakip "
             "yenilmese bile bn = 0 seçilir ve taban ödülü kazanılır.",
             "`Σ bn·γ[bn] == Σ β` (473) — seçilen sayı, gerçekten yenilen rakip sayısına "
             "eşit olmalı. Bu iki kısıt γ'yı β'ya kilitler.",
             "Amaç terimi (474–475): her bn için `ρ × Wʳ(N, b_od, bn) × γ[bn]`. γ'lardan "
             "biri 1 olduğu için toplam tam olarak doğru ödüle eşittir."]),

    # =====================================================================
    ("h2", "3.10  (E1) Yönsel denge"),
    ("img", ("f08_e1_denge.png", "Şekil 3.4 — Gidiş ve dönüş yönleri arasında denge.")),
    ("code", (F, 477, 490, "yön-çifti başına iki kısıt")),
    ("p", "Her `(o-d, gün)` grubunun ters yönü `(d-o, gün)` aranır; ikisi de modeldeyse iki "
          "simetrik kısıt eklenir. `seen` kümesi aynı çiftin iki kez işlenmesini engeller."),
    ("p", "Mutlak değer `|n_od − n_do| ≤ α(n_od + n_do)` iki eşitsizlikle yazılır — bu, "
          "doğrusal programlamada mutlak değerin standart açılımıdır ve **hiç ek değişken "
          "gerektirmez**."),

    # =====================================================================
    ("h2", "3.11  (A2) Uçak rotasyonu — fiziksel gerçeklik kısıtı"),
    ("img", ("f11_a2_rotasyon.png", "Şekil 3.5 — Minimum tur süresi.")),
    ("code", (F, 492, 523, "aynı-gün rotasyon kısıtları")),
    ("p", "Her rotasyon çifti (giden uçuş, gelen uçuş) ve aynı operasyon günündeki her olay "
          "kombinasyonu için tek bir kısıt kurulur: **θ_gelen − θ_giden ≥ sep**. Asıl incelik "
          "`sep`'in nasıl seçildiğidir:"),
    ("tbl", (["Durum", "sep değeri", "Gerekçe"],
             [["Bloklar var, `exact ≤ turn`", "`exact = T_OB + τ + T_IB`",
               "Gerçek aynı-gün tur → brief'in tam minimumu uygulanır"],
              ["Bloklar var, `exact > turn`", "`turn` (mevcut tur)",
               "Bu bir **gece-aşan** rotasyondur; fiziksel tur gün h→h+1'e yayılır. Mevcut "
               "desen korunur, yapay gün-bağlaşımı yaratılmaz"],
              ["Bloklar yok (eski şema)", "`turn`",
               "İhtiyatlı geri-dönüş: en azından mevcut tur kadar boşluk korunur"]],
             [4.0, 4.0, 9.0], 8.4)),
    ("box", ("sep = min(exact, cur) formülünün mantığı",
             "İki riski aynı anda kapatır: (i) gerçek aynı-gün turlar **asla** brief "
             "minimumunun altına sıkıştırılamaz, (ii) gece-aşan çiftlerde model mevcut "
             "durumu bozmaz. Gece-aşan turların gerçek zaman eksenindeki doğruluğu ise "
             "çözüm **sonrasında** ayrıca doğrulanır (`run_byday` içinde ve 05'te).", "info")),
    ("code", (F, 525, 566, "A2 × evren-ankoru — modellenmeyen tarafın sabitlenmesi")),
    ("p", "Üstteki döngü yalnız **her iki tarafın da modellendiği** günleri kapsar. Bir taraf "
          "amaç evreni dışındaysa (ρ'su olmayan pazar) o gün için kısıt hiç kurulmazdı. Bu "
          "blok o boşluğu kapatır: modellenmeyen taraf `full_role_time`'daki **gerçek sabit "
          "saatiyle** ifadeye konur (563–564) ve kısıt yine eklenir."),
    ("p", "Her iki taraf da modelsizse atlanır — o zaten değiştiremeyeceğimiz arşiv "
          "verisidir, kısıt uygulamanın anlamı yoktur."),
    ("code", (F, 568, 588, "gece-aşan koruma sınırlarının modele bağlanması")),
    ("p", "`byday` modunda gün h'nin kalkışı ile gün h+1'in dönüşü **farklı MIP'lerde** "
          "çözülür — yani model bu ikisini birbirine bağlayamaz. Çözüm: mevcut tarifedeki "
          "boşluk payı (slack) statik olarak ikiye bölünür ve iki tek-taraflı sınır konur:"),
    ("bul", ["`rotcap` — bugünün kalkışı en fazla `slack/2` **geç** kayabilir (üst sınır).",
             "`rotlock` — bugünün dönüş varışı en fazla `slack/2` **erken** kayabilir "
             "(alt sınır)."]),
    ("p", "İkisi birlikte `θ_in − θ_out ≥ T_OB + τ + T_IB` eşitsizliğini **yapısal olarak** "
          "garanti eder — iki gün birbirini hiç görmese bile ihlal matematiksel olarak "
          "imkânsızdır. Sınırlar `compute_overnight_guards()` içinde hesaplanır (bkz. 3.17)."),

    # =====================================================================
    ("h2", "3.12  (G) Tarife düzenliliği"),
    ("img", ("f10_g_bant.png", "Şekil 3.6 — Aynı uçuş numarası her gün aynı bandın içinde.")),
    ("code", (F, 590, 627, "gün-içi grup bandı c_f")),
    ("p", "Yolcular \"her gün 08:30 uçuşu\" bekler. G kısıtı, aynı uçuş numarasının farklı "
          "günlerdeki saatlerinin birbirine yakın kalmasını sağlar. İki teknik ayrıntı "
          "kritiktir:"),
    ("h3", "1) Saat-içi (time-of-day) dönüşümü"),
    ("p", "θ **mutlak** dakikadır, yani gün 3'ün 08:00'i ile gün 1'in 08:00'i arasında "
          "2×1440 dakika fark vardır. Düzenlilik ise **saat** düzenliliğidir. Bu yüzden her "
          "olaydan kendi gününün gece yarısı ofseti çıkarılır: `θ' = θ − ⌊cur/1440⌋·1440` "
          "(605–606, 624)."),
    ("h3", "2) Ortak bant değişkeni `c_f`"),
    ("p", "\"En fazla Xdev sapar\" ifadesi, grup başına tek bir sürekli değişken `creg[gi]` "
          "ile kurulur: tüm günlerin saat-içi zamanı `[c_f, c_f + Xdev]` aralığında olmalı "
          "(625–626). Bant nerede olacağını **model seçer**; yalnız genişliği sabittir."),
    ("box", ("Wdev ↔ G gerilimi ve \"atlanan\" gruplar",
             "Her olay kendi mevcut saatinden ±60 dk uzaklaşabilir. İki günün mevcut saatleri "
             "arasındaki fark 2×60 + 15 = 135 dakikadan büyükse, pencerelerin kesişiminde "
             "ortak bir bant **yoktur**. Kod bu grupları sessizce zorlamaz; atlar ve "
             "`m._n_g_skip` sayacına ekler (616–618). Belgeli, savunulabilir bir sınırlama.",
             "warn")),
    ("code", (F, 628, 647, "günler-arası bant kuplajı (byday için)")),
    ("p", "`byday` modunda günler ayrı çözüldüğü için üstteki gün-içi bant yetmez. "
          "`inst.gband` sözlüğü **önceki günlerde yerleşmiş** merkezleri taşır; bu blok "
          "bugünün aynı uçuşunu o merkezin ±Xdev'inde tutar. Pencere merkeze yetişemiyorsa "
          "yine atlanır ve sayılır."),

    # =====================================================================
    ("h2", "3.13  (E2) En iyi yolculuk süresi dengesi — açık ama tam ölçekte kapalı"),
    ("code", (F, 649, 684, "Jmin min-seçimi ve yön karşılaştırması")),
    ("p", "E2, gidiş ve dönüş yönlerinin **en iyi yolculuk sürelerinin** birbirinden 30 "
          "dakikadan fazla ayrılmamasını ister. Zor kısmı \"minimum\" işlemini doğrusallaştırmaktır:"),
    ("num", ["`Jmin[i] ≤ J_π + MJ(1 − y_π)` — her sunulan bağlantıdan **küçük veya eşit** "
             "(bu tek başına Jmin'i −∞'a iter).",
             "`Jmin[i] ≥ J_π − MJ(1 − u_π)` — **seçilen** bağlantıdan büyük veya eşit.",
             "`Σ u_π == act[i]` — tam bir bağlantı \"minimumu veren\" olarak seçilmeli.",
             "`act[i]` — bu pazarda hiç bağlantı sunulmuyorsa Jmin tanımsızdır; `act` bunu "
             "yakalar ve karşılaştırma kısıtı `relax` terimiyle etkisizleşir (682)."]),
    ("box", ("Neden tam ölçekte kapatıldı?",
             "Bu yapı bağlantı başına **iki** big-M kısıtı ve bir ek ikili değişken (`u`) "
             "getirir. Tam veride HiGHS, doğrusal gevşemesi çok zayıf olan bu modelde makul "
             "sürede tek bir uygun çözüm (incumbent) bile bulamıyor. Tanı yöntemi kodda "
             "yazılı: çekirdek + yalnız E2 çözülemiyor, çekirdek + A2/G/F/E1 hepsi hızlı. "
             "Küçük alt-örnekte E2 açık ve doğrulanmış hâlde bırakılmıştır.", "warn")),

    # =====================================================================
    ("h2", "3.14  (F) IST hub kova kapasitesi"),
    ("img", ("f09_f_kapasite.png",
             "Şekil 3.7 — Kaydırma, taşan kovayı komşulara yayarak çözer.")),
    ("code", (F, 686, 725, "kova başına kapasite kısıtları")),
    ("p", "IST her 10 dakikalık dilimde sınırlı sayıda hareket kaldırabilir: en fazla 10 "
          "kalkış, 15 varış. Kod her rol için üç kaynağı toplar:"),
    ("num", ["**Ayarlanabilir olaylar** — `terms[v]` sözlüğü, o kovaya *atanabilecek* tüm "
             "`x[eid,v]` değişkenlerini toplar (706–708).",
             "**Sabit olaylar** — kımıldayamadıkları için mevcut kovalarına sabit sayı olarak "
             "eklenir (710–712).",
             "**Modellenmeyen uçuşlar** — `extra_use`'dan gelen fiziksel doluluk (713–715)."]),
    ("p", "Sonra her kova için `Σ x + sabit ≤ cap` kısıtı eklenir — ama **yalnız gerçekten "
          "bağlayıcı olabiliyorsa** (723). Toplam aday sayısı zaten kapasitenin altındaysa "
          "kısıt eklenmez; gereksiz kısıt = daha yavaş çözücü."),
    ("box", ("Kritik veri bulgusu (satır 689–695)",
             "Mevcut tarifedeki kova aşımlarının **tamamı** ayarlanabilir uçuşların "
             "kümelenmesinden geliyor; sabit uçuşlar hiçbir kovada baz kapasiteyi aşmıyor "
             "(kalkışta en fazla 4 ≤ 10, varışta 5 ≤ 15). Bu bulgu sayesinde brief'in "
             "**gerçek** 10/15 değeri uygulanabildi. Aksi hâlde `max(baz, mevcut)` gibi "
             "gevşetilmiş bir kapasite kullanmak gerekirdi ki bu, F'yi fiilen etkisiz bir "
             "kısıta çevirirdi.", "ok")),
    ("p", "718–722 arası bir emniyet valfidir: eğer sabit uçuşlar tek başına kapasiteyi "
          "aşıyorsa (veri taşması), kapasite o değere yükseltilir ve `_n_f_overflow` sayacı "
          "durumu raporlar — model infeasible olmaz ama sorun gizlenmez de."),

    # =====================================================================
    ("h2", "3.15  Amaç fonksiyonu ve (P) tarife-değişim cezası"),
    ("code", (F, 727, 748, "amacın kurulması")),
    ("p", "Amaç iki parçadan oluşur:"),
    ("box", ("Amaç = Σ ρ·(aktarma ödülü + sıralama ödülü) − λ·Σ|θ − cur|",
             "**Birinci parça (saf rekabetçilik):** pazar ağırlığı ρ ile çarpılmış, azalan "
             "getirili aktarma ödülü (C) ve sıralama ödülü (D). Resmî amaç budur ve "
             "raporlanan tüm sonuçlar bu değerdir.\n"
             "**İkinci parça (ceza):** yapılan toplam kaydırma, λ katsayısıyla amaçtan "
             "düşülür.", "info")),
    ("h3", "Cezanın \"tam doğrusal\" oluşu"),
    ("p", "Mutlak değer normalde ek değişken ve big-M gerektirir. Burada gerekmiyor — çünkü "
          "A1 sayesinde her olayda tam bir `x[eid,v]` = 1'dir. O hâlde:"),
    ("p", "**|θ − cur| = Σ_v |v − cur| · x[eid, v]**"),
    ("p", "Katsayılar (`dv = abs(v - e[\"cur\"])`) tamamen sabittir ve döngüde önceden "
          "hesaplanır (739–744). **Sıfır ek değişken, sıfır big-M.** Bu, one-hot kodlama "
          "tercihinin en zarif kazancıdır."),
    ("h3", "λ neden gerekli?"),
    ("box", ("Cezasız modelin \"dejenerasyon\" sorunu",
             "λ = 0 iken çözücü, amaç değerini **hiç değiştirmeyen** kaydırmaları da yapar — "
             "çünkü onları yapmamak için bir nedeni yoktur. Sonuç: uçuşların %90'ı boşuna "
             "kaydırılır. Havayolu için bu, sıfır kazanç karşılığı devasa bir operasyonel "
             "maliyettir. λ > 0 simetriyi kırar ve yalnız **gerçekten kazanç getiren** "
             "kaydırmalar hayatta kalır.", "warn")),
    ("code", (F, 749, 757, "modelin yanına iliştirilen referanslar")),
    ("p", "Fonksiyonun sonunda, model nesnesine alt çizgiyle başlayan beş referans "
          "iliştirilir: `_md_id` (pazar-gün → indeks), `_gap` (bağlantı → boşluk ifadesi), "
          "`_w` / `_beat_eq_y` / `_beta` (rakip yenme yapıları). Bunlar Pyomo bileşeni "
          "değildir, sadece **raporlama ve warm-start için gereken haritalardır** — çözümden "
          "sonra `report()`, `solution_total()` ve `set_warmstart()` bunlara ihtiyaç duyar. "
          "Alt çizgi öneki \"bu bir model bileşeni değil, yardımcı veri\" demektir."),
    ("code", (F, 973, 976, "λ = 0.3 seçiminin gerekçesi")),
    ("p", "λ değeri tahminle değil, **taramayla** seçilmiştir: λ ∈ [0.1, 1.5] aralığında "
          "rekabetçilik kazancı düz bir plato çizer (%4.2–4.3), kaydırma ise %22–26'da "
          "kalır. λ = 0.3 bu platonun **dizidir (knee)**: en yüksek kazanç, düşük kaydırma. "
          "Tarama `07_sensitivity.py` ile üretilir ve `output/sweep_results.csv`'de saklanır."),

    # =====================================================================
    ("h2", "3.16  `set_warmstart()` — mevcut tarifeyi başlangıç çözümü yapmak"),
    ("code", (F, 758, 809, "tüm ikili değişkenlere tutarlı değer yazma")),
    ("p", "Fonksiyon mevcut tarifeyi alır ve modelin **her** ikili değişkenine tutarlı bir "
          "değer yazar. Sıra önemlidir çünkü her adım bir öncekine dayanır:"),
    ("num", ["`x` — her olay mevcut kovasında (764–767).",
             "`y` — boşluk pencerede mi? (768–773)",
             "`z` — n bağlantı sunuluyorsa ilk n slot dolu (774–778).",
             "`w`, `β` — her rakip için mevcut saatlerle yenilip yenilmediği hesaplanır "
             "(779–796).",
             "`γ` — yenilen sayısına karşılık gelen tek gösterge 1 (797–800).",
             "`act`, `u`, `Jmin` — E2 açıksa min-seçici değişkenler (801–809)."]),
    ("p", "`skip_validation=True` kullanılır çünkü ara adımlarda değerler geçici olarak "
          "tutarsız görünebilir; Pyomo'nun doğrulaması burada gereksiz yavaşlık yaratır."),
    ("box", ("03'te bu fonksiyon fiilen kullanılmıyor — ama 08'de hayat kurtarıyor",
             "CFG'de `warmstart: False`'tur; yorumda \"appsi Highs MIP-start'ı kullanmıyor "
             "(yalnız LP bazı)\" yazar. Ancak `08_fullweek_polish.py` bu fikri "
             "genelleştirilmiş hâliyle (`set_start_values`) kullanır ve orada gerçekten "
             "HiGHS `setSolution` MIP-start'ına dönüşür. Yani bu fonksiyon, 08'in "
             "prototipidir.", "info")),

    # =====================================================================
    ("h2", "3.17  Baseline, rapor ve çözücü"),
    ("code", (F, 813, 828, "current_baseline — dürüst karşılaştırma tabanı")),
    ("p", "İyileşme iddiası ancak sağlam bir tabana göre anlamlıdır. Bu fonksiyon **hiçbir "
          "optimizasyon yapmadan**, mevcut tarifenin amaç değerini birebir aynı formüllerle "
          "hesaplar: pencere içindeki bağlantılar sayılır, azalan getiri ödülü toplanır, en "
          "iyi J'nin yendiği rakipler sayılır, sıralama ödülü lookup'tan alınır."),
    ("box", ("Neden ayrı bir fonksiyon?",
             "Baseline'ı \"modelden\" almak (örneğin x'leri mevcut saate sabitleyip çözmek) "
             "cazip görünür ama tehlikelidir: modeldeki bir hata baseline'a da bulaşır ve "
             "iyileşme oranı yanlış görünmez. Bağımsız hesap, hatanın **fark olarak** ortaya "
             "çıkmasını sağlar. 05 doğrulayıcısı da baseline'ı bir kez daha, tamamen "
             "sıfırdan hesaplar.", "ok")),
    ("code", (F, 831, 874, "report — pazar/gün kırılımı")),
    ("p", "En yüksek katkılı pazarları ayrıntılı, gerisini toplu yazar. Alt kısımdaki dört "
          "satır projenin **dürüstlük paneli**dir: saf rekabetçilik, toplam kaydırma, cezalı "
          "Pyomo amacı ve baseline yan yana basılır — hiçbiri diğerinin arkasına saklanmaz."),
    ("code", (F, 878, 915, "main — tek örneklik koşu ve tanı çıktısı")),
    ("p", "Argümansız (küçük alt-örnek) ve `full` modlarının akışı: profil uygula → örnek kur "
          "→ model kur → çöz → raporla. Konsola basılan iki tanı satırı geliştirme sırasında "
          "çok iş görür:"),
    ("bul", ["**888–890:** kaç pazar-gün, kaç bağlantı, kaç olay (kaçı ayarlanabilir), pencere "
             "ve ızgara ayarları.",
             "**899–901:** hangi kısıtlar **aktif**, A2 kaç bağ kurdu (kaçı brief-exact, kaçı "
             "evren-ankoru), G kaç bağ kurdu ve kaç grup atlandı, F kaç bağ kurdu, toplam kaç "
             "ikili değişken var. Bir kısıt beklenmedik şekilde 0 bağ kuruyorsa burada "
             "hemen görülür."]),
    ("code", (F, 917, 948, "solve_model — çözücü ayarları ve dürüst durum raporu")),
    ("bul", ["`threads: 1`, `random_seed: 0` — **determinizm**. Aynı girdi farklı makinede "
             "aynı sonucu verir; yarışma teslimi için bu şarttır.",
             "`load_solution = False` + elle `load_vars()` — çözüm ancak durum uygunsa "
             "yüklenir; zaman aşımında çöp değerlerle çalışılmaz.",
             "`ok` bayrağı (937–938): kabul edilen durumlar optimal / zaman-limiti / "
             "iterasyon-limiti **ve** ortada gerçek bir uygun çözüm olması.",
             "`gap` hesabı (940–945): |sınır − en iyi| / |en iyi| — çözümün optimale ne kadar "
             "yakın olduğunun kanıtı."]),
    ("code", (F, 951, 970, "shift_value ve solution_total")),
    ("p", "İki küçük ama sık kullanılan yardımcı: toplam kaydırmayı (uçuş-dakika) ve **cezasız** "
          "saf rekabetçilik toplamını döndürürler. Raporlanan tüm \"iyileşme\" rakamları "
          "`solution_total` üzerindendir — yani λ cezası sonucu **süzer** ama **ölçmez**."),

    # =====================================================================
    ("h2", "3.18  `compute_overnight_guards()` — gece-aşan turların statik koruması"),
    ("code", (F, 979, 1024, "slack'in ikiye bölünmesi")),
    ("p", "byday ayrıştırmasının tek yapısal zayıflığı, bir günün kalkışı ile ertesi günün "
          "dönüşünü aynı modelde görememesidir. Bu fonksiyon o boşluğu **çözüm öncesinde, "
          "deterministik olarak** kapatır:"),
    ("num", ["Her rotasyon çifti ve gün için mevcut kalkış saati bulunur.",
             "Aynı gün dönüş varsa atlanır — model-içi A2 zaten kapsıyor (1002–1004).",
             "Ertesi gün dönüş varsa mevcut pay hesaplanır: "
             "`slack = (dönüş − kalkış) − (T_OB + τ + T_IB)`.",
             "`slack < 0` ise bu bir **eşleşme artefaktıdır** (o gün o çift tek uçakla "
             "dönmüyor) → sınır konmaz (1012–1013).",
             "`slack ≥ 2·Wdev` ise pencere ihlale zaten yetişemez → sınır gereksiz (1014–1015).",
             "Aksi hâlde: kalkışa `+slack/2` tavan, dönüşe `−slack/2` taban konur."]),
    ("box", ("Neden \"statik\"?",
             "Sınırlar çözümden **bağımsız** hesaplanır ve sabittir. Böylece iki gün "
             "birbirini hiç görmese bile ihlal matematiksel olarak imkânsız hâle gelir; "
             "gün-bağlaşımı doğmaz, G bandıyla çatışma yaratmaz, çözüm tekrarlanabilir "
             "kalır.", "ok")),

    # =====================================================================
    ("h2", "3.19  `run_byday()` — haftayı güne bölerek çözmek"),
    ("img", ("f12_byday_warmstart.png", "Şekil 3.8 — İki aşamalı çözüm mimarisi.")),
    ("code", (F, 1027, 1054, "hazırlık: profil, günler, sayaçlar")),
    ("p", "Fonksiyonun docstring'i sorunu net koyar: *\"Monolitik 7-gün MIP (102k ikili) "
          "HiGHS'te incumbent bulamadığından gerekli.\"* Yani bu bir tercih değil, "
          "**zorunluluktur**. Günleri bağlayan tek kısıt G'dir ve o da bantla zincirlenir."),
    ("code", (F, 1056, 1088, "gün döngüsü ve iki aşamalı G gevşetmesi")),
    ("p", "Her gün için örnek kurulur, önceki günlerden gelen bant (`inst.gband`) ve rotasyon "
          "sınırları eklenir, model çözülür. Çözülemezse **kademeli** bir gevşetme uygulanır:"),
    ("tbl", (["Aşama", "Ne yapılır?", "Mantık"],
             [["1 — Hedefli", "Yalnız **rotasyon korumalı** uçuşların G bandı bırakılır",
               "Rotasyon güvenliği (fiziksel) > tarife düzenliliği (konfor). Bırakılan her "
               "bağ `band_exempt_rows`'a yazılır"],
              ["2 — Tam", "O gün için G tamamen gevşetilir",
               "Son çare; `relaxed` bayrağı raporda \"G-gevşetildi\" olarak görünür"]],
             [2.6, 6.2, 8.2], 8.4)),
    ("p", "**1085–1088:** Tüm blok `try/except` içindedir. Gizli veride tek bir günün hatası "
          "tüm koşuyu çökertmemeli; o gün atlanır, sebebi yazılır, diğerleri devam eder."),
    ("code", (F, 1089, 1134, "çözümün işlenmesi ve tarife satırlarının üretilmesi")),
    ("bul", ["**1100–1101:** Her olayın optimize saati `Σ v·x[e,v]` toplamından okunur ve "
             "yuvarlanır. Sabit olaylar mevcut saatlerinde kalır.",
             "**1113:** `band.setdefault(...)` — bir uçuşun bandı **ilk yerleştiği günde** "
             "belirlenir ve sonraki günler ona uyar. `setdefault` bunu tek satırda yapar.",
             "**1117–1121:** Tarife satırı: gün, uçuş no, rol, eski saat, yeni saat, değişim, "
             "G gevşetildi mi. `output/optimized_schedule.csv`'nin ham hâli.",
             "**1124:** Pazar/bağlantı çıktıları `collect_market_outputs` ile biriktirilir."]),
    ("code", (F, 1135, 1174, "A2 fiziksel rotasyon doğrulaması (gece-aşan dahil)")),
    ("p", "Model-içi A2 aynı-gün kurulur; bu blok çözümü **gerçek zaman ekseninde**, gece-aşan "
          "turlar dahil kontrol eder. Ayrım son derece dürüsttür:"),
    ("tbl", (["Sonuç", "Koşul", "Yorum"],
             [["**artefakt**", "Mevcut tarife de sağlamıyor (`a_c < dep_c + need`)",
               "O gün o çift tek uçakla dönülmüyor — eşleşme yorumunun sınırı. İhlal sayılmaz "
               "ama **sayılır ve raporlanır**"],
              ["**YENİ ihlal**", "Mevcut sağlıyor ama optimize bozuyor",
               "Gerçek hata. Bu sayı 0 olmalıdır"]],
             [2.6, 5.6, 8.8], 8.4)),
    ("code", (F, 1175, 1199, "istatistikler ve özet çıktısı")),
    ("p", "Özet paneli tek ekranda: kaç gün çözüldü, kaçında G gevşetildi, optimize toplam, "
          "baseline, iyileşme (mutlak ve yüzde), kaç uçuş kaydırıldı, toplam kaç uçuş-dakika, "
          "A2 doğrulama sonucu, bant muafiyeti sayısı."),

    # =====================================================================
    ("h2", "3.20  Çıktıların üretilmesi"),
    ("code", (F, 1202, 1232, "collect_market_outputs — teslim #3'ün iki dosyası")),
    ("p", "Her pazar-gün için bir özet satırı (`market_rows`) ve sunulan her bağlantı için "
          "bir ayrıntı satırı (`conn_rows`) üretir. Bu iki tablo, brief'in \"seçilen "
          "bağlantılar\" ve \"O–D bazında yenilen rakipler\" taleplerinin doğrudan "
          "karşılığıdır."),
    ("code", (F, 1235, 1240, "main_byday — teslim modu")),
    ("p", "`gap = 0.001` (%0.1) seçimi kalibre edilmiştir: %0.5 raporlanan amaçta ~0.5 puan "
          "bırakıyor, %0.01 ise cezalı amacı sıkarken **saf rekabetçiliği düşürüyor** — çünkü "
          "çözücü cezayı azaltmak için ödülden ödün veriyor. %0.1 dengeli noktadır."),
    ("code", (F, 1243, 1267, "main_sweep — λ Pareto taraması")),
    ("p", "Beş λ değeri için `write=False` ile koşar (teslim çıktılarına dokunmaz) ve "
          "\"korunan kazanım yüzdesi\" ile \"kaydırılan uçuş yüzdesini\" karşılaştıran bir "
          "tablo basar. Bu tablo, λ seçiminin gerekçesidir."),
    ("code", (F, 1270, 1347, "write_outputs — dört CSV ve sonuç özeti")),
    ("p", "Dört CSV yazılır ve `results_summary.md` markdown olarak üretilir. Dikkat çeken "
          "iki ayrıntı:"),
    ("bul", ["**1285–1286:** `g_band_exemptions.csv` **boş olsa bile** yazılır. Doğrulayıcı "
             "bu dosyayı okur; yokluğu ile boşluğu arasındaki farkı belirsiz bırakmamak için.",
             "**1311–1339:** Özet dosyasının \"Notlar\" bölümü, sonucun hangi varsayımlarla "
             "üretildiğini okuyucuya doğrudan söyler: E2 kapalı, F gerçek 10/15, G "
             "zincirleme, A2 gece-aşan koruma, λ'nın rolü. **Sonuçla birlikte sınırlarını da "
             "yayınlamak**, bu projenin tutarlı bir tavrıdır."]),
    ("code", (F, 1350, 1357, "komut satırı arayüzü")),
    ("p", "Üç mod: `byday` (isteğe bağlı λ ile), `sweep`, ve argümansız çağrıda küçük "
          "alt-örnek (`main()`). `full` argümanı `main()` içinde PRESETS ile yakalanır."),
]
