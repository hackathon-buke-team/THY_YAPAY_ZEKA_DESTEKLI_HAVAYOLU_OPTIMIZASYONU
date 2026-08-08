# -*- coding: utf-8 -*-
"""Dokuman 2 — Bolum 4-8: Pyomo, cozucu, appsi, model boyutu, sonuc."""

F3 = "03_model.py"
F8 = "08_fullweek_polish.py"

ITEMS = [
    # ================================================================= 4
    ("h1", ("4", "Pyomo nedir, ne işe yarar?")),

    ("p", "Optimizasyonda iki tamamen farklı iş vardır ve bunları karıştırmamak gerekir:"),
    ("img", ("g5_pyomo_cozucu.png",
             "Şekil 4.1 — İş bölümü. Siz problemi tarif edersiniz, Pyomo tercüme eder, "
             "çözücü çözer.")),
    ("tbl", (["", "Modelleme (Pyomo)", "Çözme (HiGHS)"],
             [["Soru", "Problem **nedir**?", "Problem **nasıl** çözülür?"],
              ["Ürün", "Değişkenler, kısıtlar, amaç", "Optimal değerler + optimalite kanıtı"],
              ["Dil", "Python", "C++ (siz görmezsiniz)"],
              ["Sizin projede", "`03_model.py` · `build_model()`", "`highspy` paketi"],
              ["Benzetme", "SQL sorgusu", "Veritabanı motoru"]],
             [2.6, 7.2, 7.2], 8.8)),

    ("h2", "4.1  Pyomo'nun üç işi"),

    ("h3", "1) Modeli Python'da ifade etmenizi sağlar"),
    ("code", (F3, 360, 375, "değişkenler ve A1 kısıtı")),
    ("p", "`pyo.Var`, `pyo.ConstraintList`, `pyo.Objective` — bunlar Pyomo'nun sunduğu "
          "yapılardır. Onlarla yazdığınız şey Python kodu gibi görünür ama aslında bir "
          "**matematiksel model tarifidir**."),

    ("h3", "2) Bunu çözücünün anlayacağı forma çevirir"),
    ("p", "Çözücü Python bilmez. Sadece sayılardan oluşan bir katsayı matrisi görür. Tek "
          "satırlık bir B1 kısıtınız:"),
    ("code", (F3, 386, 390, "B1 — Pyomo'da nasıl görünüyor")),
    ("p", "`gap[pi]` aslında `theta_expr(dep) − theta_expr(arr)` yani iki toplamın farkıdır. "
          "Pyomo bunu açar, düzleştirir ve çözücüye şuna benzer **tek bir satır** olarak "
          "verir:"),
    ("box", ("… + 480·x[17,480] + 490·x[17,490] + … − 300·x[9,300] − 310·x[9,310] − … "
             "+ 240·y[42]  ≥  60",
             "Bu çeviriyi elle yapmak zorunda kalsaydınız `03_model.py` 1.357 satır değil, on "
             "binlerce satır olurdu — ve her kısıt değişikliğinde matris indekslerini elle "
             "güncellemek gerekirdi.")),

    ("h3", "3) Sonucu geri okur"),
    ("code", (F3, 1100, 1101, "çözümün gerçek saatlere çevrilmesi")),
    ("p", "Çözücü isimsiz bir sayı dizisi döndürür; Pyomo onu tekrar `m.x[eid, v]` gibi "
          "anlamlı isimlere bağlar. `pyo.value()` bu değeri okur."),

    ("h2", "4.2  Pyomo tam olarak ne DEĞİLDİR"),
    ("bul", ["**Bir çözücü değildir.** Tek başına hiçbir şey çözemez; mutlaka arkasına bir "
             "çözücü takmanız gerekir.",
             "**Bir algoritma değildir.** Dallanma-sınırlama, kesme düzlemleri, sezgiseller — "
             "hiçbiri Pyomo'da yoktur.",
             "**Bir hızlandırıcı değildir.** Aynı modeli daha iyi *ifade etmenizi* sağlar; "
             "modelin kendisi kötüyse (gevşek big-M gibi) Pyomo bunu düzeltmez."]),

    # ================================================================= 5
    ("h1", ("5", "Çözücü nedir, nasıl çalışır?")),

    ("p", "Çözücü (solver), matematiksel bir modeli alıp optimal çözümü bulan motordur. "
          "Kaba kuvvet kullanmaz — dört tekniği birlikte çalıştırır."),

    ("h2", "5.1  Doğrusal gevşeme (LP relaxation)"),
    ("p", "İlk adım şaşırtıcıdır: çözücü problemi **kolaylaştırır**. `x ∈ {0,1}` şartını "
          "gevşetip `0 ≤ x ≤ 1` yapar. Bu yeni problem artık bir doğrusal programdır ve "
          "simpleks/iç-nokta yöntemleriyle **çok hızlı** çözülür."),
    ("box", ("Neden işe yarıyor?",
             "Gevşetilmiş problemin optimumu, gerçek problemin optimumundan **daha iyi ya da "
             "eşittir** — çünkü daha az kısıt vardır. Yani size bir **üst sınır** verir: "
             "\"gerçek cevap bundan daha yüksek olamaz.\" Bu sınır, ilerideki budamaların "
             "temelidir.")),

    ("h2", "5.2  Dallanma ve sınırlama (branch & bound)"),
    ("img", ("g6_branch_bound.png",
             "Şekil 5.1 — Bir dalın üst sınırı eldeki en iyi çözümden kötüyse, o dalın "
             "altındaki tüm kombinasyonlar tek hamlede elenir.")),
    ("p", "Gevşemede `x = 0,63` gibi kesirli bir değer çıkarsa çözücü ikiye dallanır: "
          "`x = 0` ve `x = 1`. Her dalda gevşeme yeniden çözülür. Sihir burada:"),
    ("num", ["Elde bir **uygun çözüm** (incumbent) varsa, değeri bilinir. Örneğin 3.405.000.",
             "Bir dalın LP üst sınırı 3.399.000 çıkarsa, o dalın altında 3.405.000'i geçen "
             "bir çözüm **olamaz**.",
             "O dal komple budanır — altındaki milyarlarca kombinasyon hiç incelenmeden elenir.",
             "Böylece 10⁵⁰⁷² ihtimalin ezici çoğunluğu **hiç ziyaret edilmeden** dışlanır."]),

    ("h2", "5.3  Kesme düzlemleri (cutting planes)"),
    ("p", "Çözücü, kesirli çözümü dışarıda bırakan ama hiçbir geçerli tamsayı çözümü kesmeyen "
          "ek eşitsizlikler türetir. Gevşeme sıkılaşır, üst sınır düşer, budama hızlanır. "
          "Bunlar modelde yazmadığınız, çözücünün kendi ürettiği kısıtlardır."),

    ("h2", "5.4  Sezgiseller (heuristics)"),
    ("p", "İyi bir incumbent'ı **erken** bulmak kritiktir — çünkü budama ancak elde bir "
          "karşılaştırma noktası varken çalışır. Çözücüler bunun için RINS, local branching, "
          "feasibility pump gibi yöntemler kullanır. Sizin kodunuz bunu bilinçli ayarlıyor:"),
    ("code", (F8, 412, 414, "sezgisel bütçesinin artırılması")),
    ("p", "Varsayılan 0,05'ten 0,3'e çıkarılmış. Gerekçe kodda yazılı: warm-start'lı büyük "
          "MIP'te iyileştirmeler çoğunlukla incumbent çevresinde çalışan sezgisellerden gelir."),

    ("h2", "5.5  MIP-gap — çözücünün asıl armağanı"),
    ("img", ("g7_mip_gap.png",
             "Şekil 5.2 — Alt (incumbent) ve üst (bound) sınır birbirine yaklaşır; aradaki "
             "fark gap'tir. Grafik şematiktir; nihai değerler gerçek koşudandır.")),
    ("code", (F3, 939, 945, "gap'in hesaplanması")),
    ("p", "**Gap = |üst sınır − eldeki en iyi| / |eldeki en iyi|.** Sizin teslim koşunuzda "
          "bu değer **%1,18**'dir ve şu anlama gelir:"),
    ("box", ("\"Bulduğum çözüm, teorik en iyinin en fazla %1,18 altında.\"",
             "Bu cümle, elle yazılmış hiçbir açgözlü algoritmanın kuramayacağı cümledir. "
             "Greedy bir sezgisel size bir tarife verir — ama o tarifenin optimale yakın mı "
             "yoksa çok uzak mı olduğu konusunda **hiçbir bilgi** vermez. "
             "`08_fullweek_polish.py`'nin tüm varlık sebebi bu kanıtı üretebilmektir.", "ok")),

    # ================================================================= 6
    ("h1", ("6", "Hangi çözücü, neden?")),

    ("h2", "6.1  Dört seçenek"),
    ("tbl", (["Çözücü", "Tür", "Hız sınıfı", "Lisans", "Not"],
             [["**Gurobi**", "Ticari", "En hızlı sınıf", "Ücretli (akademik ücretsiz var)",
               "Endüstri standardı; kurumsal lisans pahalı"],
              ["**CPLEX** (IBM)", "Ticari", "Gurobi'ye yakın", "Ücretli",
               "Uzun geçmişli, olgun"],
              ["**HiGHS**", "Açık kaynak", "Ticarilere en yakın açık seçenek",
               "**Yok** — `pip install highspy`", "Aktif geliştirilen modern çözücü"],
              ["**CBC**", "Açık kaynak", "Belirgin biçimde yavaş", "Yok",
               "Eski nesil; büyük MIP'lerde zorlanır"]],
             [2.4, 2.0, 3.6, 4.4, 4.6], 8.4)),

    ("h2", "6.2  Neden HiGHS seçildi?"),
    ("num", ["**Lisans engeli yok.** Jüri `pip install -r requirements.txt` deyip kodu kendi "
             "makinesinde koşturabilir. Gurobi olsaydı lisans anahtarı gerekirdi ve sonuç "
             "bağımsız olarak doğrulanamazdı.",
             "**Determinizm destekliyor.** Tek iş parçacığı ve sabit tohum ile aynı girdi her "
             "makinede aynı sonucu verir.",
             "**Yeterince hızlı.** 100 binlik ikili değişkenli modeli warm-start ile 1.800 "
             "saniyede %1,18 gap'e getiriyor.",
             "**Pyomo ile birinci sınıf desteği var** (`appsi_highs` arayüzü)."]),
    ("code", (F3, 917, 931, "çözücünün kurulumu")),
    ("box", ("`threads: 1` performansı düşürmüyor mu?",
             "Evet, düşürüyor. Ama çok çekirdekli MIP çözümü **deterministik değildir** — "
             "iş parçacıkları düğümleri farklı sırayla işler ve aynı girdiyle farklı "
             "çözümler dönebilir. Yarışma teslimi için \"jüri koştuğunda aynı sayıyı "
             "görmeli\" kısıtı, hız kaygısının önüne konmuştur.", "warn")),

    ("h2", "6.3  Bu ayrımın somut faydası"),
    ("p", "Çözücüyü değiştirmek için model kodunda **tek satır** yeterlidir:"),
    ("code", (F3, 97, 99, "çözücü seçimi tek anahtarda")),
    ("p", "Kısıtlar, amaç fonksiyonu, `build_model()`'in 400 satırı — hiçbiri değişmez. "
          "Model doğrudan HiGHS'in C++ API'sine yazılmış olsaydı, çözücü değiştirmek projeyi "
          "baştan yazmak demek olurdu."),

    # ================================================================= 7
    ("h1", ("7", "`appsi` katmanı — ve 08 neden buna bağımlı")),

    ("p", "Kodunuzda düz `SolverFactory(\"highs\")` yok; şu var:"),
    ("code", (F3, 919, 924, "appsi arayüzü")),
    ("p", "**appsi** = *Auto-Persistent Pyomo Solver Interface*. Klasik arayüzden farkı: "
          "her çözümde diske bir `.lp`/`.mps` dosyası yazıp çözücüyü ayrı süreç olarak "
          "başlatmak yerine, **modeli çözücünün belleğinde canlı tutar** ve doğrudan C++ "
          "API'sini çağırır."),
    ("tbl", (["", "Klasik (dosya tabanlı)", "appsi (kalıcı)"],
             [["Model aktarımı", "Her çözümde `.lp` dosyası yaz/oku", "Bellekte, doğrudan API"],
              ["100 bin değişkenli modelde", "Ciddi ek maliyet", "Neredeyse sıfır"],
              ["MIP-start (warm start)", "Genellikle desteklenmez / kısıtlı",
               "**`Highs.setSolution()`** olarak geçer"],
              ["Ardışık çözümler", "Her seferinde sıfırdan", "Model korunur, sadece değişen kısım"]],
             [3.6, 6.6, 6.8], 8.6)),
    ("box", ("08_fullweek_polish.py'nin tüm yöntemi buna bağlı",
             "`CFG[\"warmstart\"] = True` ayarı, appsi katmanında HiGHS'in `setSolution()` "
             "çağrısına dönüşür. Yani \"aşama-1 çözümünü tam-hafta modeline başlangıç noktası "
             "olarak ver\" fikri **ancak bu arayüzle mümkündür**. Dosya tabanlı bir arayüzde "
             "MIP-start'ı bu şekilde geçiremezdiniz — ve o zaman ne %+14.752'lik ek iyileşme "
             "ne de %1,18'lik global gap elde edilebilirdi.", "ok")),
    ("p", "Nitekim `03_model.py`'deki şu yorum da buradan geliyor: *\"appsi Highs MIP-start'ı "
          "kullanmıyor (yalnız LP bazı) — etkisiz.\"* 03 için etkisizdir çünkü 03 warm-start'ı "
          "kapalı koşar; 08'de `config.warmstart = True` ile gerçekten devreye girer."),

    # ================================================================= 8
    ("h1", ("8", "Modelin gerçek boyutu")),

    ("h2", "8.1  Örnek (instance) büyüklüğü"),
    ("tbl", (["Ölçüt", "Değer", "Açıklama"],
             [["Operasyon günü", "**7**", "Veriden okunur, hardcode değil"],
              ["Pazar-gün grubu", "**4.660**", "Amaç fonksiyonunun toplandığı birim"],
              ["Bağlantı (π)", "**7.577**", "Modele giren TK bağlantı adayı"],
              ["Uçuş olayı", "**5.376**", "Karar birimi (uçuş no × rol × saat)"],
              ["— ayarlanabilir", "**4.553**", "Her birinin 13 seçeneği var"],
              ["— sabit", "823", "Rotasyon partneri yok → kımıldamaz"],
              ["Rotasyon çifti", "330", "A2 kısıtının kurulduğu (gidiş, dönüş) ikilisi"],
              ["Modellenmeyen kova kullanımı", "79", "ρ'suz pazarların F'deki sabit dolulukları"]],
             [5.4, 2.4, 9.2], 8.6)),

    ("h2", "8.2  100.566 ikili değişken — dökümü"),
    ("img", ("g8_ikili_dokum.png",
             "Şekil 8.1 — Değişkenlerin %59'u uçuş saati atamaları; gerisi ödül mantığını "
             "doğrusallaştıran yardımcı göstergeler.")),
    ("tbl", (["Değişken", "Sayı", "Ne sorar?"],
             [["`x[olay, saat]`", "**59.189**",
               "Bu uçuş olayı bu saate mi atandı? (4.553 × 13)"],
              ["`γ[pazar, sayı]`", "**11.690**",
               "Bu pazarda tam olarak kaç rakip yenildi? (seçici)"],
              ["`y[π]`", "**7.577**", "Bu bağlantı sunuluyor mu?"],
              ["`z[pazar, slot]`", "**7.577**", "Azalan getiri slotu dolu mu?"],
              ["`w[π, rakip]`", "**7.531**", "Bu bağlantı bu rakibi yeniyor mu? (koşullu olanlar)"],
              ["`β[pazar, rakip]`", "**7.002**", "Bu rakip yenildi mi?"],
              ["**TOPLAM**", "**100.566**", "—"]],
             [4.0, 2.4, 10.6], 8.6)),
    ("p", "Kısıt sayısı: **70.359**. Bunların kod tarafından ayrıca sayılan bazıları:"),
    ("tbl", (["Kısıt grubu", "Sayı", "Not"],
             [["**G** (düzenlilik)", "4.503", "4 grup pencerede ortak bant kuramadığı için atlandı"],
              ["**F** (kova kapasitesi)", "1.395", "Yalnız bağlayıcı olabilen kovalar"],
              ["**A2** (rotasyon)", "874 + 18", "874 aynı-gün + 18 evren-ankoru; 623'ü brief-exact"],
              ["**A1** (tekil atama)", "4.553", "Her ayarlanabilir olay için tam bir tane"],
              ["**B1** (pencere)", "15.154", "Her bağlantı için alt + üst sınır"]],
             [4.6, 2.6, 9.8], 8.6)),

    ("h2", "8.3  Ve sonuç"),
    ("tbl", (["Ölçüt", "Değer"],
             [["Çözülen gün", "7 / 7 (G gevşetilen: 0)"],
              ["Kaydırılan uçuş hareketi", "**1.067 / 4.554**  (%23) — 3.487'si yerinde kaldı"],
              ["Toplam kaydırma", "20.640 uçuş-dk · ortalama **19 dk**"],
              ["Sunulan bağlantı", "6.966 / 7.577 aday"],
              ["Yenilen rakip", "4.914 / 8.832"],
              ["Sıralaması yükselen pazar-gün", "660 · değişmeyen 2.174 · gerileyen 24"],
              ["BASELINE (mevcut tarife)", "3.251.527"],
              ["Aşama-1 (byday)", "3.390.287"],
              ["**Aşama-2 (tam-hafta cilalama)**", "**3.405.039**  (+14.752)"],
              ["**İYİLEŞME**", "**+153.512  (%+4,72)**"],
              ["**Global MIP-gap**", "**%1,18** — optimalite kanıtı"],
              ["Bağımsız doğrulama", "12 kontrolün tamamı PASS · A2 yeni ihlal: 0"]],
             [7.0, 10.0], 9.0)),
    ("box", ("Özetle",
             "89.094 satırlık ham veriden, 10⁵⁰⁷² büyüklüğünde bir karar uzayı doğdu. Pyomo "
             "bu uzayı 100.566 ikili değişken ve 70.359 kısıtla **tarif etti**; HiGHS "
             "dallanma-sınırlama ile **çözdü** ve çözümün optimale en fazla %1,18 uzak "
             "olduğunu **kanıtladı**. Sonuç: 1.067 uçuş hareketinin ortalama 19 dakika "
             "kaydırılmasıyla gelir-ağırlıklı rekabetçilikte %4,72 artış.", "ok")),

    # ================================================================= EK
    ("h1", ("A", "Ek A — Tek sayfalık sayı künyesi")),
    ("tbl", (["Kategori", "Ölçüt", "Değer"],
             [["**Girdi**", "Ham Excel satırı (4 dosya)", "89.094"],
              ["", "Bağlantı tablosu satırı", "57.317"],
              ["", "— THY (TK)", "7.850"],
              ["", "— rakip", "49.467"],
              ["", "Operasyon günü", "7"],
              ["", "Yönlü O–D pazarı", "1.408"],
              ["", "TK uçuş numarası", "952"],
              ["", "Farklı taşıyıcı", "88"],
              ["**Türetilmiş**", "`derived/` toplam satır", "118.177"],
              ["", "TK bağlantı adayı", "7.693"],
              ["", "ρ'su olmayan (dışlanan) pazar", "48"],
              ["", "Rotasyon partneri olmayan uçuş no", "176"],
              ["**Karar**", "Uçuş olayı (toplam)", "5.376"],
              ["", "— ayarlanabilir", "4.553"],
              ["", "— sabit", "823"],
              ["", "Olay başına seçenek", "13 (±60 dk / 10 dk)"],
              ["", "Tarife karar uzayı", "13⁴⁵⁵³ ≈ 10⁵·⁰⁷²"],
              ["**Model**", "İkili değişken", "100.566"],
              ["", "Kısıt", "70.359"],
              ["", "Ham ikili uzay", "2¹⁰⁰⁵⁶⁶ ≈ 10³⁰·²⁷³"],
              ["**Çözüm**", "Kaydırılan uçuş hareketi", "1.067 (%23)"],
              ["", "Ortalama kaydırma", "19 dk"],
              ["", "Sunulan bağlantı", "6.966"],
              ["", "Yenilen rakip", "4.914 / 8.832"],
              ["", "Baseline → Sonuç", "3.251.527 → 3.405.039"],
              ["", "İyileşme", "+153.512 (%+4,72)"],
              ["", "Global MIP-gap", "%1,18"],
              ["**Altyapı**", "Modelleme", "Pyomo 6.7+"],
              ["", "Çözücü", "HiGHS (`appsi_highs`, `highspy`)"],
              ["", "Determinizm", "threads=1, random_seed=0"],
              ["", "Süre sınırı", "aşama-1: 150 s/gün · aşama-2: 1.800 s"]],
             [3.2, 7.4, 6.4], 8.8)),
]
