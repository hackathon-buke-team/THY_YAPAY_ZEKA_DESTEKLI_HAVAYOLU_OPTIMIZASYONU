# -*- coding: utf-8 -*-
"""Dokuman 3 — Bolum 5: Terimler, konu anlatimi tarzinda."""

ITEMS = [
    ("h1", ("5", "Terimler — sıfırdan konu anlatımı")),
    ("p", "Bu bölüm bir sözlük değil, bir **ders**. Her terim üç adımda anlatılıyor: "
          "*nedir* → *neden gerekli* → *bu projede nerede*. Hiçbir ön bilgi varsayılmıyor."),

    # ============================================================ A
    ("h2", "5.1  Optimizasyonun temel kavramları"),

    ("h3", "Optimizasyon"),
    ("p", "**Nedir?** Bir amacı en iyi hâle getirecek kararları bulmak. Günlük hayattan "
          "örnek: markete gideceksiniz, 500 lira paranız var, alışveriş listeniz uzun ve "
          "bazı ürünler indirimde. \"Bütçeyi aşmadan en çok ihtiyacımı karşılayan sepeti "
          "kur\" demek bir optimizasyon problemidir."),
    ("p", "**Üç bileşeni vardır ve her optimizasyon probleminde bu üçü aranır:**"),
    ("tbl", (["Bileşen", "Markette", "Bizim projede"],
             [["**Karar değişkenleri**", "Hangi üründen kaç tane alacağım?",
               "Her uçuş olayının IST saati"],
              ["**Kısıtlar**", "Bütçe 500 lira; süt en fazla 2 litre",
               "Uçak rotasyonu, hub kapasitesi, bağlantı penceresi, düzenlilik, yön dengesi"],
              ["**Amaç fonksiyonu**", "Toplam faydayı en büyük yap",
               "Gelir-ağırlıklı rekabetçilik puanını en büyük yap"]],
             [4.0, 6.0, 7.0], 8.6)),

    ("h3", "Karar değişkeni"),
    ("p", "**Nedir?** Değerine *bizim* karar verdiğimiz büyüklük. Veriden gelmez, hesaplanmaz "
          "— seçilir."),
    ("p", "**Neden önemli?** Bir problemi modellerken en kritik soru şudur: *neyin değerini "
          "seçiyorum?* Yanlış seçerseniz model ya çözülemez ya da anlamsız sonuç verir."),
    ("box", ("Bu projedeki karar değişkeni",
             "`x[olay, saat]` — \"şu uçuş olayı, şu saate atandı mı?\" (evet/hayır)\n\n"
             "Dikkat: karar değişkenimiz **bağlantı** değil, **olay**. Bu bilinçli bir "
             "tercih; nedeni Bölüm 2.1'de anlatıldı: bir uçuş 20 farklı bağlantıda geçiyor, "
             "bağlantı başına karar verseydik aynı uçağa 20 farklı saat atanabilirdi.")),

    ("h3", "İkili (binary) değişken"),
    ("p", "**Nedir?** Yalnızca **0** veya **1** değeri alabilen karar değişkeni. Bir "
          "evet/hayır sorusunun matematiksel karşılığıdır."),
    ("p", "**Neden 0/1?** Çünkü gerçek hayattaki kararların çoğu böyle: *bu uçuş bu saate mi "
          "atandı?* (evet/hayır), *bu bağlantıyı sunuyor muyuz?* (evet/hayır), *bu rakibi "
          "yendik mi?* (evet/hayır). Bunlara \"yarım\" cevap veremezsiniz."),
    ("tbl", (["Değişken", "Sorduğu soru", "Kaç tane var?"],
             [["`x[olay, saat]`", "Bu uçuş olayı bu saate mi atandı?", "**59.189**"],
              ["`y[π]`", "Bu bağlantı sunuluyor mu?", "7.577"],
              ["`z[pazar, slot]`", "Bu pazarın kaçıncı ödül slotu dolu?", "7.577"],
              ["`w[π, rakip]`", "Bu bağlantı bu rakibi yeniyor mu?", "7.531"],
              ["`β[pazar, rakip]`", "Bu rakip yenildi mi?", "7.002"],
              ["`γ[pazar, sayı]`", "Bu pazarda tam kaç rakip yenildi?", "11.690"],
              ["**TOPLAM**", "", "**100.566**"]],
             [3.6, 8.0, 5.4], 8.6)),
    ("box", ("\"Tamsayı\" neden problemi zorlaştırıyor?",
             "Değişkenler kesirli olabilseydi (0,63 gibi) problem **çok hızlı** çözülürdü — "
             "buna doğrusal programlama denir ve saniyeler sürer. Ama \"uçuşun %63'ünü "
             "08:30'a ata\" anlamsızdır. Tamsayı şartı gerçekçiliği getirir, karşılığında "
             "zorluğu da getirir. \"Karışık Tamsayılı\" ifadesindeki zorluk tam olarak "
             "budur.", "warn")),

    ("h3", "Kısıt (constraint)"),
    ("p", "**Nedir?** Çözümün uyması **zorunlu** olan kural. Kısıt ihlal edilirse çözüm "
          "geçersizdir — puanı ne olursa olsun."),
    ("p", "**Ödülle farkı:** Amaç fonksiyonu \"bunu yaparsan puan kazanırsın\" der; kısıt "
          "\"bunu yapamazsın\" der. Amaç bir **tercih**, kısıt bir **yasaktır**."),
    ("tbl", (["Kısıt", "Türkçesi", "Kaç kısıt"],
             [["**A1**", "Her uçuş olayına tam bir saat ata", "4.553"],
              ["**A2**", "Dönüş varışı ≥ gidiş kalkışı + uçuş + yer + uçuş", "892"],
              ["**B1**", "Bir bağlantı ancak boşluğu 60–300 dk ise sunulabilir", "15.154"],
              ["**C**", "Ödül slotları baştan doldurulmalı (monotonluk)", "7.577"],
              ["**D**", "Rakip yenme ve sıralama göstergelerinin tutarlılığı", "~30.000"],
              ["**E1**", "Gidiş ve dönüş yönleri dengeli olmalı (±%20)", "~8.500"],
              ["**F**", "Her 10 dk kovada kalkış ≤ 10, varış ≤ 15", "1.395"],
              ["**G**", "Aynı uçuş her gün ±15 dk bandında kalmalı", "4.503"]],
             [1.8, 10.0, 5.2], 8.6)),

    ("h3", "Amaç fonksiyonu"),
    ("p", "**Nedir?** \"İyi\"yi tanımlayan formül. Çözücü bu sayıyı en büyük (veya en küçük) "
          "yapmaya çalışır."),
    ("box", ("Amaç  =  Σ_pazar ρ · (aktarma ödülü + sıralama ödülü)  −  λ · Σ|kaydırma|",
             "**ρ (rho)** — pazarın gelir/önem ağırlığı, 3 ile 1.000 arası. Büyük pazarda "
             "kazanılan puan daha değerli.\n"
             "**Aktarma ödülü** — sunulan her geçerli bağlantı için azalan getirili puan: "
             "1, ½, ¼, ⅛ …\n"
             "**Sıralama ödülü** — kaç rakip geçtiğinize göre lookup tablosundan okunan puan.\n"
             "**λ · kaydırma** — gereksiz tarife değişimini engelleyen ceza.")),

    ("h3", "Uygun (feasible) ve uygun olmayan (infeasible)"),
    ("p", "**Uygun çözüm:** tüm kısıtları sağlayan herhangi bir çözüm. İyi olması gerekmez, "
          "sadece kuralları çiğnememesi yeter."),
    ("p", "**Infeasible:** hiçbir çözümün tüm kısıtları aynı anda sağlayamaması. Bu bir hata "
          "değil, bir **bilgidir**: kısıtlarınız birbiriyle çelişiyor demektir."),
    ("box", ("Bu projede gerçekten yaşandı",
             "Kısıt **B2** (\"uygun olan her bağlantıyı sunmak zorundasın\") ile **E1** "
             "(\"gidiş-dönüş dengeli olmalı\") çatıştı. Asimetrik pazarlarda — bir yönde çok, "
             "ters yönde az bağlantı olan pazarlarda — ikisi aynı anda sağlanamıyor ve model "
             "**infeasible** oluyordu.\n\n"
             "Çözüm: B2 kapatıldı. Zaten amaç fonksiyonu sunmayı ödüllendirdiği için model "
             "kârlı bağlantıları kendiliğinden sunuyor. Bu, kodda `bisection` yöntemiyle "
             "doğrulanmış bir karar (`03_model.py:86–89`).", "warn")),

    # ============================================================ B
    ("h2", "5.2  Modelleme teknikleri — asıl zanaat"),

    ("h3", "Doğrusallık — neden bu kadar takıntılıyız?"),
    ("p", "**Doğrusal ifade nedir?** Değişkenlerin yalnızca sabitlerle çarpılıp toplandığı "
          "ifade. `3x + 5y − 2z` doğrusaldır. `x·y` (iki değişkenin çarpımı), `x²`, `|x|`, "
          "`min(x,y)`, `eğer x>3 ise…` doğrusal **değildir**."),
    ("p", "**Neden önemli?** Çünkü MIP çözücüleri **yalnızca doğrusal** ifadeleri "
          "çözebilir. Doğrusal olmayan bir şey yazmak istiyorsanız, onu doğrusal parçalardan "
          "yeniden inşa etmeniz gerekir. Modelleme zanaatının büyük kısmı budur."),
    ("tbl", (["İstediğimiz (doğrusal değil)", "Nasıl doğrusallaştırdık?", "Kısıt"],
             [["\"Eğer sunuluyorsa boşluk 60–300 olsun\"", "big-M numarası", "B1"],
              ["\"1. bağlantı 1 puan, 2. bağlantı ½ puan…\"",
               "monoton `z` slot dizisi", "C"],
              ["\"Lookup tablosundan puan oku\"", "`γ` seçici değişkenleri", "D"],
              ["\"|θ − mevcut saat| kadar ceza\"",
               "one-hot sayesinde `Σ|v−cur|·x` — **hiç numara gerekmedi**", "P"],
              ["\"En kısa J'yi seç\"", "`u` seçici + iki yönlü big-M", "E2"]],
             [5.6, 8.0, 1.6], 8.6)),

    ("h3", "Tek-sıcak (one-hot) kodlama"),
    ("p", "**Nedir?** Bir seçimi tek bir sayıyla değil, **her seçenek için bir evet/hayır "
          "lambası** ile ifade etmek. Tam bir lamba yanar, gerisi söner."),
    ("img", ("h2_onehot.png", "Şekil 5.1 — Aynı bilgiyi iki farklı şekilde ifade etmek.")),
    ("p", "Bir uçuşun saatini iki şekilde yazabilirdik:"),
    ("num", ["**Sürekli değişken:** `θ = 510` (yani 08:30). Tek sayı, sezgisel görünür.",
             "**Tek-sıcak:** 13 tane 0/1 değişkeni; hangi kova seçildiyse o 1, diğerleri 0."]),
    ("p", "İkincisini seçtik. Nedeni tek kelimeyle: **ceza fonksiyonu.**"),
    ("box", ("Kritik kazanç",
             "Tarife-değişim cezası `|θ − mevcut saat|` mutlak değeri gerektirir. Mutlak "
             "değer doğrusal değildir; normalde ek değişken ve big-M ister.\n\n"
             "Ama A1 kısıtı sayesinde her olayda **tam bir** `x` değişkeni 1'dir. O zaman:\n\n"
             "**|θ − cur| = Σ_v |v − cur| · x[olay, v]**\n\n"
             "Buradaki `|v − cur|` değerleri **sabittir** (aday saatler önceden belli). "
             "Yani ifade tamamen doğrusal — **sıfır ek değişken, sıfır big-M.**", "ok")),
    ("p", "İkinci kazanç: **F kapasitesi**. \"Bu kovada kaç uçuş var?\" sorusu, one-hot ile "
          "doğrudan `Σ x[olay, kova] ≤ 10` olarak yazılır. Sürekli değişkenle bu soruyu "
          "sormak için ayrıca gösterge değişkenleri kurmak gerekirdi."),

    ("h3", "big-M"),
    ("p", "**Nedir?** \"Eğer şu koşul geçerliyse şu kural işlesin\" mantığını doğrusal hale "
          "getiren bir numara. Adı, kullanılan büyük sabitten (M) gelir."),
    ("img", ("h3_bigm.png", "Şekil 5.2 — Aynı eşitsizlik, y'nin değerine göre devreye "
                            "giriyor veya etkisizleşiyor.")),
    ("p", "**Somut örnek.** İstediğimiz kural: *bir bağlantı sunuluyorsa (y=1) boşluğu en az "
          "60 dakika olmalı.* Bunu doğrudan yazamayız. Bunun yerine şunu yazarız:"),
    ("box", ("boşluk  ≥  60 − Mlo · (1 − y)",
             "**y = 1 ise:** sağ taraf `60 − Mlo·0 = 60` olur → kural **devreye girer**.\n"
             "**y = 0 ise:** sağ taraf `60 − Mlo` olur. Mlo yeterince büyük seçilirse bu "
             "sayı, boşluğun alabileceği en küçük değerden bile küçüktür → kural "
             "**otomatik sağlanır, yani etkisizleşir**.")),
    ("p", "**Peki M ne kadar büyük olmalı?** İşte asıl mesele bu."),
    ("tbl", (["M çok küçükse", "M çok büyükse", "Doğrusu"],
             [["Kural y=0 iken bile bağlar → **model yanlış olur**",
               "Model **doğru** ama çözücü çok yavaşlar — doğrusal gevşeme zayıflar, "
               "hiçbir dal budanamaz",
               "Kuralı etkisizleştirecek **en küçük** M"]],
             [5.0, 6.4, 5.2], 8.6)),
    ("box", ("Bizim yaptığımız",
             "Genel bir \"büyük sayı\" (mesela 99999) kullanmak yerine, **her bağlantı "
             "için ayrı ayrı** hesapladık:\n\n"
             "`Mlo = max(0, 60 − o bağlantının ulaşabileceği en küçük boşluk)`\n"
             "`Mhi = max(0, o bağlantının ulaşabileceği en büyük boşluk − 300)`\n\n"
             "Aday saatler sınırlı olduğu için bu aralıklar önceden bilinebiliyor. Sonuç: "
             "mümkün olan en sıkı M değerleri → çözücü çok daha hızlı ilerliyor "
             "(`03_model.py:382–390`).", "ok")),

    ("h3", "Seyrek (sparse) değişken üretimi"),
    ("p", "**Nedir?** İhtiyaç duyulmayan değişkeni **hiç yaratmamak**. Kulağa basit gelir "
          "ama büyük modellerde çözülebilirlik ile çözülemezlik arasındaki fark budur."),
    ("p", "Örnek: teorik olarak her (bağlantı × rakip) çifti için bir \"yendi mi?\" "
          "değişkeni gerekir — 13.015 çift. Kod üç duruma ayırıyor:"),
    ("tbl", (["Durum", "Sayı", "Ne yapılıyor?"],
             [["**Asla yenemez** — izin verilen boşluk, ulaşılabilir en küçüğün altında",
               "3.384 (%26)", "Değişken **hiç yaratılmıyor**"],
              ["**Her zaman yener** — pencere içindeki her boşlukta rakip geçiliyor",
               "2.100 (%16)", "`w` yerine doğrudan `y` kullanılıyor"],
              ["**Koşullu** — boşluğa bağlı", "7.531 (%58)", "Gerçek `w` değişkeni + 2 kısıt"]],
             [7.6, 2.4, 6.6], 8.6)),
    ("p", "Yani çiftlerin **%42'si için hiç değişken yaratılmıyor.** Benzer eleme F "
          "kısıtında da var: kapasite kısıtı yalnız **bağlayıcı olabilecek** kovalara "
          "ekleniyor (1.395 kısıt)."),

    # ============================================================ C
    ("h2", "5.3  Çözücü nasıl çalışıyor?"),

    ("h3", "Doğrusal gevşeme (LP relaxation)"),
    ("p", "**Nedir?** Çözücünün ilk hamlesi şaşırtıcıdır: problemi **kolaylaştırır**. "
          "`x ∈ {0,1}` şartını gevşetip `0 ≤ x ≤ 1` yapar. Artık x kesirli olabilir."),
    ("p", "**Neden işe yarıyor?** Gevşetilmiş problem çok hızlı çözülür ve verdiği sonuç, "
          "gerçek problemin sonucundan **daha iyi ya da eşittir** (daha az kısıt var). Yani "
          "bir **üst sınır** verir: *\"gerçek cevap bundan yüksek olamaz.\"*"),
    ("box", ("Bir benzetme",
             "Bir sınavda \"tam not 100\" bilgisi, kimsenin 100'ün üstünde alamayacağını "
             "söyler. Gevşeme de öyle: gerçek optimumun tavanını verir. Bu tavan olmadan "
             "hiçbir dal budanamaz.")),

    ("h3", "Dallanma ve sınırlama (branch and bound)"),
    ("p", "**Nedir?** MIP çözücülerinin ana algoritması. Adım adım:"),
    ("img", ("g6_branch_bound.png", "Şekil 5.3 — Bir dalın üst sınırı elimizdekinden "
                                    "kötüyse, o dal komple budanır.")),
    ("num", ["Gevşeme çözülür. `x = 0,63` gibi kesirli bir değer çıkarsa problem ikiye "
             "**dallanır**: bir dalda `x = 0`, diğerinde `x = 1`.",
             "Her dalda gevşeme yeniden çözülür ve o dalın **üst sınırı** bulunur.",
             "Elde bir uygun çözüm (**incumbent**) varsa değeri bilinir — örneğin 3.405.000.",
             "Bir dalın üst sınırı 3.399.000 ise, o dalın altında 3.405.000'i geçen bir "
             "çözüm **olamaz** → dal komple **budanır**.",
             "Böylece 10⁵·⁰⁷² ihtimalin ezici çoğunluğu **hiç ziyaret edilmeden** elenir."]),

    ("h3", "Incumbent (eldeki en iyi çözüm)"),
    ("p", "**Nedir?** Şu ana kadar bulunmuş, tüm kısıtları sağlayan en iyi çözüm. Türkçede "
          "\"mevcut en iyi\" diyebiliriz."),
    ("p", "**Neden kritik?** Budama ancak elde bir karşılaştırma noktası varken çalışır. "
          "Incumbent yoksa hiçbir dal budanamaz ve çözücü ağaçta boğulur."),
    ("box", ("Bu projedeki en büyük teknik sorun tam da buydu",
             "Tam-hafta modelinde (~100.566 ikili) HiGHS makul sürede **tek bir incumbent "
             "bile bulamıyordu**. Çözüm bulunamayınca budama yok, budama yoksa ilerleme yok.\n\n"
             "İşte `08_fullweek_polish.py` bu yüzden var: byday'in bulduğu çözümü hazır bir "
             "incumbent olarak çözücünün eline veriyoruz.", "warn")),

    ("h3", "Üst sınır (bound) ve MIP-gap"),
    ("p", "**Üst sınır:** çözücünün kanıtladığı tavan — \"gerçek optimum bundan yüksek "
          "olamaz\"."),
    ("p", "**MIP-gap:** eldeki en iyi çözüm ile bu tavan arasındaki bağıl fark."),
    ("box", ("gap = |üst sınır − eldeki en iyi| / |eldeki en iyi|",
             "Bizim teslim koşumuzda **%1,18**. Türkçesi:\n\n"
             "*\"Bulduğum çözüm, teorik olarak mümkün olan en iyinin en fazla %1,18 "
             "altında.\"*")),
    ("img", ("g7_mip_gap.png", "Şekil 5.4 — İki sınır birbirine yaklaşır; aradaki fark "
                               "gap'tir.")),
    ("box", ("Neden bu, projenin en değerli çıktısı?",
             "Elle yazılmış hiçbir açgözlü algoritma bu cümleyi kuramaz. Greedy bir yöntem "
             "size bir tarife verir — ama o tarifenin optimale yakın mı yoksa çok mu uzak "
             "olduğu konusunda **hiçbir bilgi** vermez. Gap, \"iyi bir çözüm buldum\" ile "
             "\"bulduğum çözümün ne kadar iyi olduğunu kanıtlayabiliyorum\" arasındaki "
             "farktır.", "ok")),

    ("h3", "Kesme düzlemleri (cutting planes)"),
    ("p", "**Nedir?** Çözücünün kendi ürettiği ek eşitsizlikler. Kesirli çözümü dışarıda "
          "bırakırlar ama hiçbir geçerli tamsayı çözümü kesmezler. Sonuç: gevşeme sıkılaşır, "
          "üst sınır düşer, budama hızlanır."),
    ("p", "Bunlar sizin yazmadığınız kısıtlardır — çözücü otomatik türetir."),

    ("h3", "Sezgisel (heuristic)"),
    ("p", "**Nedir?** \"En iyi\"yi garanti etmeyen ama hızlıca **iyi** bir çözüm bulan "
          "yöntem. Çözücüler bunları incumbent'ı erken bulmak için kullanır (RINS, local "
          "branching, feasibility pump)."),
    ("p", "Bu projede sezgisel bütçesi bilinçli olarak artırıldı: `mip_heuristic_effort` "
          "varsayılan 0,05 iken **0,3** yapıldı. Gerekçe: warm-start'lı büyük MIP'te "
          "iyileştirmeler çoğunlukla incumbent çevresinde çalışan sezgisellerden gelir "
          "(`08_fullweek_polish.py:412–414`)."),

    ("h3", "Determinizm"),
    ("p", "**Nedir?** Aynı girdiyle her zaman aynı çıktıyı üretme özelliği."),
    ("p", "**Neden zor?** Çok çekirdekli MIP çözümü doğası gereği deterministik değildir: "
          "iş parçacıkları düğümleri farklı sırayla işler, farklı çözümler dönebilir."),
    ("box", ("Bizim tercihimiz",
             "`{\"threads\": 1, \"random_seed\": 0}` — tek iş parçacığı, sabit tohum. "
             "Bu **hızdan feragat** demektir. Ama yarışma teslimi için \"jüri kendi "
             "makinesinde koşturunca aynı sayıyı görmeli\" kısıtı hız kaygısının önüne "
             "kondu (`03_model.py:922`).", "ok")),

    # ============================================================ D
    ("h2", "5.4  Çözüm stratejisi terimleri"),

    ("h3", "Warm-start (MIP-start)"),
    ("p", "**Nedir?** Çözücüye sıfırdan başlamak yerine *\"işte elimde çalışan bir çözüm, "
          "buradan devam et\"* demek."),
    ("p", "**Nasıl çalışır?** Elinizdeki çözümün **tüm** değişken değerlerini çözücüye "
          "yazarsınız. Çözücü bunu incumbent kabul eder ve o noktadan **iyileştirmeye** "
          "başlar; ayrıca üst sınırı daraltarak gap üretir."),
    ("tbl", (["", "Warm-start'sız", "Warm-start'lı"],
             [["Başlangıç", "Sıfırdan çözüm arar", "Elde 3.390.287 puanlık çözüm var"],
              ["Bu modelde sonuç", "**Hiç incumbent bulamıyor**",
               "İlk saniyeden itibaren budama yapabiliyor"],
              ["Elde edilen", "—", "**+14.752** puan ve **%1,18** global gap"]],
             [3.4, 6.4, 7.2], 8.6)),
    ("box", ("Kritik ayrıntı — başlangıç noktası KUSURSUZ olmalı",
             "HiGHS, verilen başlangıç noktasını uygunluk açısından denetler. **Tek bir "
             "kısıt ihlali** varsa noktayı tümüyle reddeder ve sıfırdan başlar — yani "
             "warm-start'ın tüm anlamı kaybolur.\n\n"
             "Bu yüzden `08_fullweek_polish.py`'de `y` değişkenleri \"uygunluktan\" değil, "
             "byday'in **gerçek sunum listesinden** okunuyor. byday, E1 dengesi için bazı "
             "uygun bağlantıları bilinçli sunmuyor; hepsini y=1 yapmak E1'i ihlal eden bir "
             "başlangıç üretirdi. Ayrıca bir **E1 onarım** döngüsü de var.", "warn")),

    ("h3", "Matheuristik"),
    ("p", "**Nedir?** Kesin yöntem (matematiksel programlama) ile sezgiseli birleştiren "
          "melez yaklaşım. Bizimki *fix-and-optimize / warm-start* ailesine girer:"),
    ("num", ["**Sezgisel adım:** haftayı günlere böl, her günü ayrı çöz (hızlı, garantili "
             "çözüm — ama küresel optimallik iddiası yok).",
             "**Kesin adım:** bu çözümü tam-hafta modeline başlangıç ver, çözücü küresel "
             "olarak iyileştirsin ve gap'i kanıtlasın."]),

    ("h3", "Ayrıştırma (decomposition)"),
    ("p", "**Nedir?** Çözülemeyecek kadar büyük bir problemi çözülebilir parçalara bölmek."),
    ("p", "Bizde bölme ekseni **gün**: 7 günü ayrı ayrı çözüyoruz. Ama günleri birbirine "
          "bağlayan iki şey var ve ikisi de ayrıca ele alınıyor:"),
    ("bul", ["**G düzenliliği** — aynı uçuş her gün benzer saatte olmalı. Çözüm: önceki "
             "günlerde yerleşen saat bir \"bant\" olarak sonraki güne aktarılıyor (zincirleme).",
             "**A2 gece-aşan rotasyon** — gün h'nin kalkışı ile gün h+1'in dönüşü aynı "
             "modelde değil. Çözüm: `compute_overnight_guards` ile statik slack bölüşümü."]),

    ("h3", "Açgözlü (greedy) yöntem"),
    ("p", "**Nedir?** Her adımda o an en iyi görünen kararı alan, geri dönüp düzeltmeyen "
          "yöntem. Hızlıdır, ama küresel en iyiyi bulacağının garantisi yoktur."),
    ("p", "byday ayrıştırması bir greedy zincirdir: 3. günde alınan bir karar 6. gün için "
          "daha iyi bir seçeneği kapatmış olabilir ve geri alma imkânı yoktur. **Aşama-2 "
          "tam olarak bunu telafi ediyor.**"),

    ("h3", "Dejenerasyon ve λ cezası"),
    ("p", "**Dejenerasyon nedir?** Birden fazla çözümün **tamamen aynı** amaç değerini "
          "vermesi. Çözücü aralarından rastgele birini seçer."),
    ("box", ("Bu neden bir sorun?",
             "λ = 0 iken (ceza yok) çözücü, amaç değerini **hiç değiştirmeyen** kaydırmaları "
             "da yapıyordu — çünkü yapmamak için bir nedeni yok. Sonuç: uçuşların "
             "**~%90'ı** boşuna kaydırılıyordu.\n\n"
             "Havayolu için bu, sıfır kazanç karşılığı devasa bir operasyonel maliyettir: "
             "yer hizmetleri, mürettebat planı, yolcu bilgilendirme, sistem güncellemeleri.",
             "warn")),
    ("p", "**λ cezası** bu simetriyi kırar: amaçtan `λ · toplam kaydırma` düşülür. Artık bir "
          "kaydırmanın hayatta kalması için **gerçek kazanç** getirmesi gerekir. Sonuç: "
          "uçuşların %90'ı yerine yalnız **%23'ü** kaydırıldı, kazanç ise arttı."),
    ("p", "λ = 0,3 değeri tahminle değil **taramayla** seçildi: λ ∈ [0,1 – 1,5] aralığında "
          "kazanç düz bir plato çiziyor; 0,3 bu platonun dizi (*knee*) noktası."),

    ("h3", "Pareto ödünleşimi ve \"knee\" noktası"),
    ("p", "**Pareto ödünleşimi:** iki iyi şeyin aynı anda en üst düzeye çıkarılamaması. "
          "Burada: *daha çok kazanç* ↔ *daha az tarife değişikliği*."),
    ("p", "**Knee (diz) noktası:** eğrinin kırıldığı yer — bir birim daha kazanç için ödemeniz "
          "gereken bedelin hızla arttığı nokta. Rasyonel seçim genellikle buradadır."),

    ("h3", "Duyarlılık analizi"),
    ("p", "**Nedir?** Parametreleri oynatıp modelin tepkisine bakmak. Amaç sonucu "
          "iyileştirmek değil, sonucun **ne kadar sağlam** olduğunu göstermek."),
    ("p", "Beklenen davranış: **sürekli ve yönü açıklanabilir** tepki. Küçük bir parametre "
          "değişikliğinde sonuç sıçrıyorsa modelde ya kırılganlık ya hata vardır. "
          "`07_sensitivity.py` üç parametrede 11 koşu yapıyor (λ, Wdev, τ) ve **teslim "
          "edilen çözüme dokunmuyor**."),

    # ============================================================ E
    ("h2", "5.5  Problem ve havacılık terimleri"),
    ("tbl", (["Terim", "Nedir?", "Bu projede"],
             [["**O–D pazarı**", "Origin–Destination: yönlü kalkış–varış çifti",
               "1.408 yönlü pazar. Örn. `AGP-KCM` ile `KCM-AGP` **farklı** pazarlardır"],
              ["**Itinerary / bağlantı**", "Bir aktarmalı yolculuk seçeneği",
               "TK'nınki 7.850 satır, rakiplerinki 49.467 satır"],
              ["**Hub / aktarma merkezi**", "Yolcuların uçuş değiştirdiği merkez havalimanı",
               "İstanbul (IST)"],
              ["**Bacak (leg)**", "Tek bir uçuş — aktarmanın yarısı",
               "1. bacak: kalkış→IST · 2. bacak: IST→varış"],
              ["**Boşluk (gap)**", "IST'te bekleme süresi",
               "Brief'in penceresi: 60–300 dakika"],
              ["**J**", "Toplam yolculuk süresi = 1. bacak + boşluk + 2. bacak",
               "Rakiple kıyaslanan **tek** büyüklük. En uzunu 35 saat"],
              ["**legsum**", "İki bacağın uçuş süreleri toplamı",
               "**Sabittir** — model değiştiremez; yalnız boşluk değişir"],
              ["**ρ (rho)**", "Pazarın gelir/önem ağırlığı",
               "3 – 1.000 arası. Amaç fonksiyonundaki çarpan"],
              ["**N_od**", "Pazardaki rakip sayısı",
               "**Taşıyıcı bazlı** sayılıyor (en fazla 17, ödül tablosu 40'a kadar destekliyor)"],
              ["**T_comp**", "Bir rakip taşıyıcının o pazardaki en iyi J değeri",
               "`J ≤ T_comp` ise o rakibi yendik demektir"],
              ["**b_od**", "Pazarın başlangıç sırası",
               "Mevcut tarifeye göre hesaplanır; sıralama ödülü b'den s'ye geçişin ödülüdür"],
              ["**s (son sıra)**", "clip(N − yenilen, 1, N)",
               "Küçük s = daha iyi sıralama"],
              ["**τ (tau) / MCT**", "Minimum yer süresi — uçağın varış havalimanında "
               "geçirmesi gereken en az süre", "45 dakika"],
              ["**Blok süresi**", "Bir bacağın uçuş süresi (T_OB gidiş, T_IB dönüş)",
               "`ElapsedTime1/2`'den türetiliyor; A2 kısıtının girdisi"],
              ["**Rotasyon**", "Aynı uçağın yaptığı gidiş–dönüş turu",
               "`Flight Pairs.xlsx`'ten okunuyor; 330 çift"],
              ["**Kova (bucket) / slot**", "10 dakikalık zaman dilimi",
               "Hem zaman ızgarası hem F kapasitesinin sayım birimi"],
              ["**Baseline**", "Mevcut tarifenin (hiç dokunulmamış) amaç değeri",
               "3.251.527 — tüm iyileşme buna göre ölçülüyor"]],
             [3.2, 6.0, 7.8], 8.2)),

    # ============================================================ F
    ("h2", "5.6  Kalite ve doğrulama terimleri"),

    ("h3", "Çift kayıt (double-entry)"),
    ("p", "**Nereden geliyor?** Muhasebeden. Her işlem iki kez, iki farklı yere kaydedilir; "
          "ikisi tutmuyorsa hata vardır."),
    ("p", "**Bizde:** çözümü üreten kod (`03` + `08`) ile doğrulayan kod (`05`) **ayrıdır**. "
          "05 ne Pyomo import ediyor ne de modele dokunuyor; sabitleri kendi dosyasında "
          "yeniden yazıyor. Böylece modeldeki bir hata, doğrulamada aynı hatayla örtülemiyor."),
    ("img", ("f13_cift_kayit.png", "Şekil 5.5 — Üreten kod ile doğrulayan kod ayrıdır.")),

    ("h3", "Fazla-beyan / eksik-beyan asimetrisi"),
    ("tbl", (["", "Ne demek?", "Nasıl işleniyor?"],
             [["**Fazla-beyan**", "Dosyada yazandan az rakip gerçekten yenilmiş → amaç "
               "değeri **şişirilmiş**", "**HATA** — doğrulama FAIL verir"],
              ["**Eksik-beyan**", "Gerçekte yenilmiş ama çözücü göstergeyi bağlamamış → "
               "amaç değeri olduğundan küçük görünüyor", "**NOT** — hata değil, ihtiyatlılık"]],
             [3.0, 8.2, 5.8], 8.6)),
    ("p", "Bu asimetri bilinçlidir: **kendi lehimize olan sapmalar hata sayılıyor, "
          "aleyhimize olanlar sayılmıyor.** Ölçüm kendine karşı kurulmuş."),

    ("h3", "Eşleşme artefaktı (A2)"),
    ("p", "**Nedir?** Rotasyon eşleşmesinin, mevcut yayınlanan tarifenin kendisinin de "
          "sağlamadığı bir tur öngörmesi. Yani o gün o çift muhtemelen tek uçakla "
          "dönülmüyor — veri yorumunun sınırı."),
    ("p", "Kod bunu **ihlal saymıyor** ama **sayıyor ve raporluyor**. Gerçek hata olan "
          "\"YENİ ihlal\" (mevcut sağlıyordu, optimizasyon bozdu) ayrı sayılıyor ve **0** "
          "olmak zorunda."),

    ("h3", "Kalite kapısı"),
    ("p", "**Nedir?** Boru hattının içine gömülmüş, geçilemezse akışı durduran kontrol."),
    ("p", "Bizde: `05_validate_solution.py` bir tane bile FAIL bulursa **çıkış kodu 1** "
          "döndürüyor; `run_all.py` bunu görüp koşuyu durduruyor. Yani `output/` klasöründe "
          "bir sonuç varsa ve uçtan uca koşu başarıyla bittiyse, o sonuç **kesinlikle** 12 "
          "kontrolden geçmiştir. Doğrulanmamış bir çözüm için figür bile üretilmez."),
]
