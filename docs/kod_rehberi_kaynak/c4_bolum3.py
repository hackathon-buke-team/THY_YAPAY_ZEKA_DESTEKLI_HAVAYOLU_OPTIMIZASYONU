# -*- coding: utf-8 -*-
"""ALGORITMA — SIFIRDAN ANLATIM · Bolum 8-12 + Ek A
(cozum hatti · MIP gap kaniti · dogrulama · sonuclar · juri sorulari)
"""

F3 = "03_model.py"
F8 = "08_fullweek_polish.py"
F5 = "05_validate_solution.py"

ITEMS = [
    # =================================================================== 8
    ("h1", ("8", "Çözüm hattı — modeli kurmak yetmiyor, çözebilmek de gerek")),
    ("p", "Modeli kurduk: 100 binin üzerinde ikili değişken. Şimdi kötü haber: **bu modeli "
          "olduğu gibi çözücüye verdiğimizde çözemiyor.** İyi haber: bunu aşmanın yolunu "
          "bulduk ve bu, projenin en özgün mühendislik katkılarından biri."),

    ("h2", "8.1  Önce sorun: monolitik model çözülemiyor"),
    ("p", "Tüm haftayı tek MIP olarak kurup HiGHS'e soğuk başlangıçla verdiğimizde, 600 "
          "saniyede **tek bir uygun çözüm bile** bulunamıyor. Dikkat: \"kötü çözüm buluyor\" "
          "değil — *hiç* çözüm bulamıyor. Büyük-M'li geniş bir MIP'te çözücünün sezgiselleri "
          "geçerli bir tamsayı noktası yakalayamıyor."),
    ("p", "Burada durup pes edebilir ya da sezgisele (genetik algoritma vb.) kaçabilirdik. "
          "İkisini de yapmadık."),

    ("h2", "8.2  Aşama 1 — güne göre ayrıştırma"),
    ("p", "Kritik gözlem şu: **günleri birbirine bağlayan tek kısıt G'dir** (aynı uçuşun "
          "günler arası tutarlılığı). A2, B1, C, D, E1, F — hepsi gün içinde kalır. Öyleyse "
          "her günü ayrı çözebiliriz:"),
    ("bul", ["Her gün ≈ 670 pazar-gün, ~17 bin ikili → **3–10 saniyede** çözülüyor, çoğu "
             "*kanıtlanmış optimal*.",
             "G kısıtı, önceki günlerin yerleşmiş saat bandıyla **zincirlenir**: o günün "
             "aynı uçuşu, bandın ±15 dk'sında tutulur.",
             "Bir gün bant yüzünden çözümsüz kalırsa **iki aşamalı geri düşüş** devreye "
             "girer: önce yalnız rotasyon-korumalı uçuşların bandı bırakılır, yetmezse o "
             "günün bandı tümüyle gevşetilir. Bırakılan her bant "
             "`output/g_band_exemptions.csv`'ye yazılır — gizlenmez, belgelenir.",
             "**7 gün toplam ~1,5 dakika**, gün içi gap ≤ %0,1."]),
    ("p", "Bu aşamanın zayıflığı da açık ve bunu kendimiz söylüyoruz: greedy bir zincir "
          "olduğu için günler arası koordinasyonu tam göremez, ve **gün gün gap'ler toplam "
          "için küresel bir optimalite kanıtı vermez**. İkisini de aşama 2 çözüyor."),

    ("h2", "8.3  Aşama 2 — tam hafta, sıcak başlangıçla"),
    ("img", ("f12_byday_warmstart.png",
             "Şekil 8.1 — İki aşamalı hat: gün gün çöz, sonra tüm haftayı tek modelde "
             "o çözümden başlayarak cilala.")),
    ("p", "Fikir şu: çözücü sıfırdan bir çözüm bulamıyorsa, **ona bir çözüm verelim**. "
          "Aşama-1'in ürettiği tarife, tüm kısıtları sağlayan geçerli bir noktadır. Bunu "
          "tam-hafta modeline **MIP-start** (sıcak başlangıç) olarak veriyoruz; HiGHS "
          "buradan başlayıp dallanma-sınırlama ile **iyileştiriyor**."),
    ("p", "Teknik olarak: modelin **tüm** ikili değişkenlerine aşama-1 değerleri yazılır, "
          "sonra Pyomo bunu HiGHS'in `setSolution` çağrısına çevirir. \"Tüm\" kelimesi "
          "kritik — dokunulmayan bir değişken 0 kabul edilir ve başlangıç noktası tutarsız "
          "olup reddedilir."),
    ("box", ("İnce bir ayrıntı: \"E1 onarımı\"",
             "Sıcak başlangıç noktası E1 denge kısıtını **ihlal ederse HiGHS onu tümden "
             "reddeder** ve tüm cilalama boşa gider. Birleşik olayların dondurulması bazı "
             "bağlantıları pencere dışına düşürdüğü için bu risk gerçek. Kod bunu, dengesizlik "
             "giderilene dek büyük yönden bağlantı geri çekerek **deterministik** biçimde "
             "onarır. Bedeli ölçülü ve raporlanıyor: başlangıç noktası aşama-1'den 865 puan "
             "düşük başlıyor — ve cilalama bunu fazlasıyla geri kazanıyor.", "info")),
    ("p", "Kazanç iki yönlü oldu:"),
    ("tbl", (["", "Değer"],
             [["Aşama-1 (byday) saf rekabetçilik", "3.390.287"],
              ["**Aşama-2 cilalanmış**", "**3.405.039**   (+14.752)"],
              ["**Ve** küresel MIP-gap", "**%1,18** — aşama-1'in veremediği kanıt"],
              ["Çözüm süresi", "1.809 s (sınır 1.800 s) + aşama-1 ~1,5 dk"]],
             [8.0, 9.0], 8.8)),

    ("h2", "8.4  Çift bariyer — çıktıyı bozmama güvencesi"),
    ("p", "Aşama-2, `output/` dosyalarını yalnız **iki koşul birden** sağlanırsa yeniden "
          "yazar:"),
    ("num", ["Saf rekabetçilik, aşama-1'in **kayıtlı** toplamını gerçekten aşmalı "
             "(sıcak başlangıç noktasını değil — bu ayrım E1 onarımı yüzünden önemli).",
             "Gece-aşan A2 rotasyon denetimi temiz olmalı: **yeni ihlal 0**."]),
    ("p", "Aksi hâlde aşama-1 çıktısı olduğu gibi kalır ve neden yazdırılır. Yani cilalama "
          "adımı, kötü bir sonuçla iyi bir sonucu ezemez. Bu, teslim güvenliği açısından "
          "bilinçli bir tasarım."),

    # =================================================================== 9
    ("h1", ("9", "MIP gap — \"%1,18 kesin mi?\" sorusunun tam cevabı")),
    ("p", "Şimdi asıl sorunuza geldik. Cevap: **evet, kesin** — ama neyin kesin olduğunu "
          "tam olarak tanımlamak gerekiyor, çünkü jüri buradan soru sorarsa yüzeysel bir "
          "cevap sizi zora sokar. Bu bölüm dört adımda ilerliyor: sayı nereden geliyor, "
          "kodun neresinde okunuyor, neyi garanti ediyor, neyi etmiyor."),

    ("h2", "9.1  Sayı nereden geliyor — matematiksel kaynak"),
    ("p", "Bölüm 3.3 ve 3.5'te temeli kurmuştuk; şimdi birleştiriyoruz. Çözücü iki sayı "
          "tutuyordu:"),
    ("tbl", (["Sayı", "Bizim koşumuzda", "Neden bu bir sınır?"],
             [["**incumbent**  (alt sınır)", "Bulduğumuz gerçek tarifenin cezalı amaç değeri",
               "Elimizde **fiilen duruyor**. Tüm kısıtları sağlayan, uygulanabilir bir "
               "tarife. Optimum bundan küçük **olamaz**, çünkü bu zaten geçerli bir çözüm."],
              ["**bound**  (üst sınır)",
               "Dallanma ağacındaki tüm açık dalların LP gevşetmelerinin en iyisi",
               "LP gevşetmesi gerçek problemden **daha serbesttir**; cevabı asla daha kötü "
               "olamaz. Optimum bundan büyük **olamaz**."]],
             [3.8, 5.4, 7.8], 8.4)),
    ("p", "Gerçek optimum bu ikisinin arasında sıkışmış durumda. Aradaki mesafeyi "
          "incumbent'a oranlarsak MIP gap çıkar:"),
    ("eq", "**gap  =  | bound − incumbent |  /  | incumbent |   =   %1,18**"),
    ("img", ("g7_mip_gap.png",
             "Şekil 9.1 — İki sınırın yakınsaması (şematik gösterim; başlangıç noktası, "
             "nihai değer ve %1,18'lik gap gerçek koşudan, aradaki eğriler temsilîdir).")),
    ("box", ("Kilit cümle",
             "Bu sayı **bizim iddiamız değil**. Bizim ürettiğimiz bir tahmin, bir istatistik "
             "ya da bir benzetim sonucu değil. Çözücünün dallanma-sınırlama sürecinde "
             "**matematiksel olarak türettiği** bir sınırdır. LP gevşetmesinin gerçek "
             "optimumdan kötü olamayacağı, doğrusal programlama teorisinin temel bir "
             "sonucudur — tartışmaya açık bir yanı yok.", "ok")),

    ("h2", "9.2  Kodun neresinde okunuyor — kanıtın kendisi"),
    ("p", "Jüri \"bu sayıyı nasıl elde ettiniz\" derse gösterebileceğiniz yer tam olarak "
          "burası. Yedi satır:"),
    ("code", (F3, 939, 945, "MIP gap'in okunduğu YER — tüm raporlardaki %1,18 buradan çıkar")),
    ("p", "Satır satır:"),
    ("bul", ["`res.best_feasible_objective` → HiGHS'in bulduğu **incumbent** (en iyi gerçek "
             "çözümün amaç değeri).",
             "`res.best_objective_bound` → HiGHS'in **dual sınırı**, yani dallanma-sınırlama "
             "sürecinin ürettiği üst sınır.",
             "Üçüncü satır ikisinin farkını incumbent'a bölüyor — Bölüm 9.1'deki formülün "
             "birebir kendisi.",
             "Bu iki değeri biz hesaplamıyoruz; **çözücüden okuyoruz**. Kodun yaptığı tek "
             "şey bölme işlemi."]),
    ("p", "Bu değer sonra dört yere birden yazılır: konsola, `reports/fullweek_polish.md` "
          "tablosuna, `output/results_summary.md`'ye ve gün kırılım tablosuna. Yani "
          "raporlarda gördüğünüz %1,18'lerin hepsinin tek bir kaynağı var."),
    ("p", "Koşunun ürettiği tam değer **%1,183**'tür (`reports/fullweek_polish.md`, "
          "\"Global MIP-gap (cezalı amaç)\" satırı)."),
    ("h3", "Tekrar üretilebilirlik"),
    ("p", "Çözücü deterministik ayarlarla çağrılıyor: `threads = 1`, `random_seed = 0`. "
          "Yani aynı makinede aynı komut aynı sonucu verir. Bu, \"şansa bağlı bir koşu\" "
          "olmadığının da kanıtı:"),
    ("code", (F3, 917, 931, "çözücü çağrısı — determinizm ve sınırlar")),

    ("h2", "9.3  Bu tam olarak NEYİ garanti eder?"),
    ("p", "Net konuşalım. Garanti şudur:"),
    ("box", ("Garanti",
             "*\"Kurduğumuz modelin — tüm kısıtlarıyla — matematiksel optimumu, teslim "
             "ettiğimiz çözümün en fazla %1,18 üzerindedir. Daha iyi bir tarife var olsa "
             "bile, bizimkinden en fazla bu kadar iyi olabilir.\"*", "ok")),
    ("p", "Bunun pratik anlamı büyük. Teslim ettiğimiz çözüm **+%4,72** rekabetçilik "
          "iyileşmesi sağlıyor. Kalan tüm arama uzayında saklanabilecek en büyük ek kazanç "
          "%1,18 mertebesinde. Yani \"acaba çok daha iyi bir çözüm mü kaçırdık?\" sorusunun "
          "cevabı kesin bir **hayır**."),

    ("h2", "9.4  Ve neyi garanti ETMEZ? — bunu siz söyleyin"),
    ("p", "Bir jüri üyesi bu ayrımı yapabilir. Siz önce söylerseniz, hem dürüstlük hem "
          "hâkimiyet göstermiş olursunuz. Üç sınır:"),
    ("num", ["**Modelin optimumu, gerçek dünyanın optimumu değildir.** Gap, *bizim "
             "formüle ettiğimiz problemin* optimumuna olan uzaklıktır. Model gerçeği ne kadar "
             "iyi temsil ediyorsa o kadar anlamlıdır. Bu yüzden modelleme kararlarımızın her "
             "birini ayrıca belgeledik — ve bu yüzden bağımsız doğrulayıcı (Bölüm 10) var.",
             "**Gap, cezalı amaç üzerindedir.** Çözücünün optimize ettiği fonksiyon "
             "\"rekabetçilik − λ·kaydırma\". Raporladığımız +%4,72 ise cezasız (saf) "
             "rekabetçiliktir. İkisi farklı ölçekler; gap'i doğrudan \"+%4,72'nin %1,18'i\" "
             "diye çevirmek yanlış olur. Tüm raporlarımızda bu, \"global MIP-gap (**cezalı "
             "amaç**)\" diye etiketli.",
             "**E2 kısıtı kapalı olan modelin optimumudur.** E2 açık bir model kurulsaydı "
             "fizibıl bölge daralır, optimum farklı olurdu. Bu da açıkça belgeli (Bölüm 6)."]),
    ("p", "Bu üç sınırı bilmek gap'i zayıflatmaz — tam tersine, ne söylediğinizi bildiğinizi "
          "gösterir."),

    ("h2", "9.5  Neden bu, sezgisel yöntemlere karşı en güçlü kozunuz"),
    ("p", "Bu bölümün özeti ve muhtemelen sunumun en vurucu cümlesi:"),
    ("box", ("Jüriye söylenecek cümle",
             "\"Sezgisel bir yöntem — genetik algoritma, tabu arama, tavlama benzetimi — "
             "size bir çözüm verir, ama o çözümün ne kadar iyi olduğunu **asla** söyleyemez. "
             "Optimumun %2 altında da olabilirsiniz, %40 altında da; bilmenin bir yolu "
             "yoktur. MIP ise size bir üst sınır verir. Biz %1,18 diyoruz — yani **ne "
             "bulduğumuzu değil, ne kadar iyi bulduğumuzu da biliyoruz.**\"", "ok")),
    ("p", "Ve bunu somutlaştıran bir ayrıntı daha var: aşama-1'in (greedy gün zinciri) "
          "kendisi bir sezgiseldir ve tam da bu yüzden küresel bir kanıt veremiyordu. "
          "Aşama-2'yi eklememizin sebebi yalnız +14.752 puanlık iyileşme değil, "
          "**kanıtın kendisiydi**."),

    # =================================================================== 10
    ("h1", ("10", "Bağımsız doğrulama — \"peki ya kodunuzda hata varsa?\"")),
    ("p", "Optimizasyon projelerinin en büyük riski şudur: modelde bir hata varsa, çözücü "
          "o hatayı **sömürerek** yüksek ama gerçek olmayan bir skor üretir. Kendi kodunuzla "
          "kendi kodunuzu kontrol edemezsiniz. Bu yüzden ikinci bir kayıt tuttuk."),

    ("h2", "10.1  Çift kayıt ilkesi"),
    ("p", "`05_validate_solution.py`, çözümü **modelden hiç geçmeden** yeniden hesaplar:"),
    ("bul", ["**Pyomo'yu hiç import etmez.** Model kodu bu betikte yüklenmez bile.",
             "Tüm sabitleri (10 dk ızgara, ±60 dk pencere, 60–300 dk boşluk, α=0,20, "
             "τ=45, ±15 dk bant, 10/15 kapasite) **açıkça yeniden yazar**. Model bir sabiti "
             "değiştirir de doğrulayıcı güncellenmezse, doğrulama FAIL verir — istenen "
             "davranış budur.",
             "Optimize saatleri modelin değişkenlerinden değil, **çıktı dosyasındaki "
             "kaydırma miktarlarından** yeniden türetir.",
             "Amaç değerini ve baseline'ı sıfırdan, yalnız `derived/` veri katmanından "
             "hesaplar."]),
    ("img", ("f13_cift_kayit.png",
             "Şekil 10.1 — İki bağımsız hesap yolu. Buluşurlarsa sonuç güvenilirdir.")),

    ("h2", "10.2  Sonuç: tüm kontroller PASS"),
    ("tbl", (["Kontrol", "Kapsam", "Sonuç"],
             [["A1 ızgara / pencere / saat aritmetiği", "4.554 uçuş hareketi", "**PASS**"],
              ["F kova kapasitesi", "7 gün × 10 dk kovalar",
               "**PASS** — aşan kova 0; en dolu kova kalkış 10/10, varış 15/15"],
              ["A2 rotasyon (gerçek zaman ekseni)", "1.709 tur (gece-aşan dahil)",
               "**PASS** — yeni ihlal **0**"],
              ["G düzenlilik (±15 dk bant)", "2.644 gün-arası bağ",
               "**PASS** — bant dışı 0"],
              ["B1 boşluk / J / saat tutarlılığı", "6.966 seçilen bağlantı", "**PASS**"],
              ["C aktarma ödülü, D yenilen rakip + sıralama", "4.660 pazar-gün", "**PASS**"],
              ["E1 yön dengesi (α = 0,20)", "2.001 yön-çifti", "**PASS** — dengesiz 0"],
              ["Amaç toplamı (bağımsız yeniden hesap)", "3.405.039 ↔ 3.405.039", "**PASS**"],
              ["Baseline (bağımsız yeniden hesap)", "3.251.527 ↔ 3.251.527", "**PASS**"]],
             [6.4, 5.2, 5.4], 8.4)),
    ("p", "En güçlü satır sondan ikincisi: dosyadaki amaç toplamı ile sıfırdan yapılan "
          "yeniden hesap **birebir** tutuyor. Yani raporladığımız 3.405.039 puanın her "
          "kuruşu bağımsız olarak yeniden üretilebiliyor."),

    ("h2", "10.3  Doğrulayıcı gerçekten işe yaradı mı? — evet, üç kez"),
    ("p", "Bu bir vitrin süsü değil. Gerçek hatalar yakaladı ve hepsi düzeltildi:"),
    ("num", ["**Kapasite evreni açığı.** Amaç fonksiyonuna girmeyen (ρ'suz, dışlanan) "
             "pazarların uçuşları da IST kovalarını fiziksel olarak dolduruyor, ama model "
             "onları saymıyordu. Doğrulayıcı yakaladı; artık o uçuşlar da sabit doluluk "
             "olarak sayılıyor.",
             "**Rotasyon evreni açığı.** Bir rotasyon ortağının bağlantısı amaç evreninde "
             "değilse, o günkü olay hiç modellenmiyordu ve A2 kısıtı kurulamıyordu. "
             "Doğrulayıcı **gerçek bir ihlal** yakaladı (uçuş 2200/2201, gün 2): rotasyon "
             "ortağının kalkışı kısıtsız kayıp minimum turu 20 dakika altına indirmişti. "
             "Düzeltme sonrası skor bilinçli olarak **düştü** (+%4,32 → +%4,27) — haksız "
             "kazanılan payı geri verdik.",
             "**Kopya olay tutarsızlığı.** Hafta normalizasyonu ihtiyacını (Bölüm 2.4) da "
             "bu doğrulayıcı ortaya çıkardı."]),
    ("box", ("Jüriye söylenecek cümle",
             "\"Doğrulayıcımız üç gerçek hata yakaladı ve bunlardan biri skorumuzu "
             "**düşürdü**. Bunu saklamak yerine belgeledik, çünkü amacımız yüksek bir sayı "
             "değil, **doğru** bir sayı üretmek.\"", "ok")),
    ("p", "Bir dürüstlük ayrıntısı daha: doğrulayıcı, çözücünün bazı \"rakip yenildi\" "
          "göstergelerini bağlamadığını da tespit ediyor (1.199 adet). Bunlar gerçekte "
          "yenilen ama raporda sayılmayan rakipler — yani **raporladığımız skor, gerçek "
          "skorun bir alt sınırıdır**. Bu yönde hata, skoru şişirmez; tersi olsaydı hata "
          "sayılırdı ve o sayaç sıfırdır."),

    # =================================================================== 11
    ("h1", ("11", "Sonuçlar")),
    ("h2", "11.1  Ana sonuç"),
    ("tbl", (["Ölçüt", "Değer"],
             [["Baseline (mevcut yayınlanan tarife)", "3.251.527"],
              ["Aşama-1 (güne göre ayrıştırma)", "3.390.287"],
              ["**Aşama-2 (tam hafta cilalama) — NİHAİ**", "**3.405.039**   (+14.752)"],
              ["**İYİLEŞME**", "**+153.512   (+%4,72)** gelir-ağırlıklı rekabetçilik"],
              ["**Küresel MIP-gap**", "**%1,18** — optimalite kanıtı"],
              ["Kaydırılan uçuş hareketi", "1.067 / 4.554  (**%23**) — 3.487'si yerinde kaldı"],
              ["Toplam kaydırma", "20.640 uçuş-dk · ortalama **19 dakika**"],
              ["Sunulan bağlantı", "6.966 / 7.577 aday"],
              ["Çözülen gün", "7 / 7 (G gevşetilen: 0)"],
              ["Bağımsız doğrulama", "Tüm kontroller **PASS** · A2 yeni ihlal: 0"]],
             [7.0, 10.0], 8.8)),
    ("p", "Bu tablodaki en güçlü satır ikili: **%4,72 kazanç, %23 kaydırma.** Yani "
          "uçuşların dörtte üçüne hiç dokunmadan, dokunduklarımızı da ortalama 19 dakika "
          "oynatarak elde edilmiş bir kazanç. Operasyonel olarak uygulanabilir bir öneri."),

    ("h2", "11.2  Gün kırılımı"),
    ("tbl", (["Gün", "Pazar-gün", "OPT", "Baseline", "Δ", "Kaydırılan"],
             [["1", "670", "488.005", "465.686", "+22.318", "166"],
              ["2", "655", "465.912", "443.873", "+22.038", "161"],
              ["3", "658", "490.860", "470.624", "+20.237", "140"],
              ["4", "661", "482.902", "459.225", "+23.677", "155"],
              ["5", "667", "495.630", "472.018", "+23.612", "139"],
              ["6", "672", "486.872", "467.761", "+19.111", "153"],
              ["7", "677", "494.858", "472.339", "+22.519", "153"]],
             [1.6, 2.6, 3.2, 3.2, 3.0, 3.4], 8.4)),
    ("p", "Kazanç yedi güne dengeli dağılmış — tek bir günü sömürüp ortalamayı yükselten bir "
          "çözüm değil. Bu da sonucun sağlamlığının bir göstergesi."),

    ("h2", "11.3  Duyarlılık — sonuç ne kadar sağlam?"),
    ("tbl", (["Varyant", "Kazanç", "Yorum"],
             [["**Referans** (±60 dk, τ=45)", "+%4,32", "aşama-1 ölçümü"],
              ["Pencere ±30 dk", "+%3,64",
               "Pencere serbestliği gerçek bir kaldıraç — beklenen yön"],
              ["Pencere ±90 dk", "+%1,38",
               "**Düşüş serbestlikten değil, süre limitinden**: aday sayısı 13→19'a çıkıyor, "
               "150 s'de çözücü iyi çözüm bulamıyor. Ayrıca bu ayarda doğrulayıcı bir A2 "
               "açığı yakaladığı için güvenli bulunmadı ve **iptal edildi**."],
              ["τ = 30 dk", "+%4,52", "Kısa yer süresi → rotasyon gevşer, kazanç artar"],
              ["τ = 60 dk", "+%4,43", "Dar bantta; monoton değil (gerekçesi raporda)"]],
             [4.0, 2.4, 10.6], 8.4)),
    ("p", "Duyarlılık analizinin en dürüst kısmı üçüncü satır: sonucun düşmesinin sebebini "
          "\"model kötüleşti\" diye değil, **\"ölçüm zaman-limitliydi\"** diye açıkladık ve "
          "o varyantı benimsemedik."),

    # =================================================================== 12
    ("h1", ("12", "Jüri soru bankası — bu dokümandaki konular için")),
    ("p", "Aşağıdaki sorular tam olarak bu dokümanın kapsadığı alanlardan. Cevapları "
          "ezberlemeyin; mantığını anlayın, kendi cümlelerinizle söyleyin."),

    ("qa", (1, "MIP gap %1,18 diyorsunuz. Bu sayıyı siz mi hesapladınız?")),
    ("p", "\"Hayır, çözücü hesaplıyor; biz yalnız okuyoruz. HiGHS dallanma-sınırlama "
          "sırasında iki sayı tutar: elindeki en iyi gerçek çözüm (incumbent) ve LP "
          "gevşetmelerinden gelen üst sınır (bound). Kodumuzun 941. satırı bu iki değeri "
          "çözücünün sonuç nesnesinden okuyor, 943. satır farkı incumbent'a bölüyor. Yani "
          "tek yaptığımız bir bölme işlemi — sınırın kendisi çözücünün matematiksel "
          "çıktısı.\""),

    ("qa", (2, "Peki bu sınırın geçerli olduğunu nereden biliyoruz?")),
    ("p", "\"Doğrusal programlamanın temel bir sonucu: bir MIP'in LP gevşetmesi, tamsayı "
          "kısıtı kaldırıldığı için daha geniş bir fizibıl bölgeye sahiptir. Enbüyüklemede "
          "daha geniş bölgenin en iyisi, dar bölgenin en iyisinden küçük olamaz. Dolayısıyla "
          "her düğümdeki LP değeri o dalın üst sınırıdır; hepsinin en büyüğü de global üst "
          "sınırdır. Bu bir varsayım değil, teorem.\""),

    ("qa", (3, "Gap hangi amaç fonksiyonu üzerinde? Raporladığınız %4,72 üzerinde mi?")),
    ("p", "\"Hayır, ve bunu raporlarımızda açıkça etiketledik. Gap, çözücünün optimize "
          "ettiği **cezalı** amaç üzerinde: rekabetçilik eksi λ çarpı toplam kaydırma. "
          "Raporladığımız +%4,72 ise **cezasız** saf rekabetçilik — çünkü yarışmanın ölçütü "
          "o. Ceza terimi bizim eklediğimiz operasyonel gerçekçilik katmanı; ödülü şişirmiyor, "
          "yalnız hangi kaydırmaların yapılacağını süzüyor.\""),

    ("qa", (4, "Neden sezgisel bir yöntem (genetik algoritma) kullanmadınız?")),
    ("p", "\"Çünkü sezgisel yöntemler çözümün kalitesi hakkında hiçbir garanti veremez. Bir "
          "genetik algoritma size bir tarife verir ama optimumun %2 mi %40 mı altında "
          "olduğunuzu söyleyemez. MIP ise bir üst sınır üretir. Bizim için ölçülebilir "
          "güven, biraz daha yüksek olabilecek ama kanıtsız bir skordan daha değerliydi. "
          "Nitekim aşama-1'imiz greedy bir sezgiseldir ve tam da bu yüzden yetmedi: "
          "aşama-2'yi eklememizin sebeplerinden biri kanıtın kendisiydi.\""),

    ("qa", (5, "E2 kısıtını kapatmışsınız. Bu kuralı ihlal etmek değil mi?")),
    ("p", "\"E2 formüle edildi, kodda kurulu ve küçük ölçekte doğrulandı — yapamadığımız bir "
          "şey değil. Tam ölçekte kapatmamızın iki ölçülmüş sebebi var. Birincisi: E2'nin "
          "min-seçimi büyük-M'i LP gevşetmesini o kadar zayıflatıyor ki çözücü **hiç uygun "
          "çözüm bulamıyor**; bu bir boyut sorunu da değil — tek gün bile çözülemiyor, aynı "
          "gün E2 kapalıyken saniyeler sürüyor. İkincisi: E2-kapalı optimal çözümde yön "
          "çiftlerinin **%76'sı** 30 dakikalık eşiği zaten ihlal ediyor, en büyük fark 465 "
          "dakika. Çünkü bu farkın çoğu bacak uçuş sürelerinden geliyor ve onlar sabit veri — "
          "hiçbir tarife düzenlemesiyle kapatılamaz. Kapatma kararı model dokümanında, teknik "
          "raporda ve çıktı özetinde açıkça yazılı.\""),

    ("qa", (6, "Kaç ikili değişkeniniz var? Belgelerde iki farklı sayı görüyorum.")),
    ("p", "\"Teslim ettiğimiz tam-hafta modelinde **100.552**. 100.566 ise aynı modelin "
          "monolitik varyantı — orada bir olay, gün-görünümü kopyası olduğu için aşama-1 "
          "değerine sabitleniyor ve 12 zaman ataması ile 2 yenme göstergesi düşüyor. İkisi de "
          "doğru; farkı yeniden sayarak doğruladık ve dökümü Ek A'da veriyoruz.\""),

    ("qa", (7, "Modelinizde bir hata olmadığını nereden biliyorsunuz?")),
    ("p", "\"Bilmiyoruz — bu yüzden ikinci bir kayıt tuttuk. `05_validate_solution.py` "
          "çözümü model kodundan hiç geçmeden, Pyomo'yu import bile etmeden, yalnız veri "
          "katmanından yeniden hesaplıyor. Tüm sabitleri bağımsız olarak yeniden yazıyor. "
          "Ve gerçekten işe yaradı: üç gerçek hata yakaladı, bunlardan biri skorumuzu "
          "%4,32'den %4,27'ye **düşürdü**. Haksız kazanılmış puanı geri verdik.\""),

    ("qa", (8, "Sonuç çözücünün rastgeleliğine bağlı mı? Tekrar üretilebilir mi?")),
    ("p", "\"Tam tekrar üretilebilir. Çözücüyü `threads=1` ve `random_seed=0` ile "
          "çağırıyoruz; paralel iş parçacığı yok, sabit tohum var. Aynı komut aynı makinede "
          "aynı sonucu verir. Gün listesi bile veriden okunuyor, koda gömülü değil — gizli "
          "test verisi farklı gün etiketleriyle gelirse kod çalışmaya devam eder.\""),

    ("qa", (9, "Neden ±60 dakika? Neden 10 dakikalık ızgara?")),
    ("p", "\"10 dakika, brief'in hub kapasite kısıtının zaten tanımlı olduğu kova "
          "genişliği — aynı ızgarayı kullanmak kısıtı doğal kılıyor. ±60 dakika ise bizim "
          "kararımız: brief sınır koymuyor ama sınırsız bırakmak hem modeli patlatır hem "
          "operasyonel olarak anlamsız olur. Duyarlılık analizinde ±30 ve ±90 da denendi; "
          "±30 kazancı düşürüyor, ±90 ise problem büyüdüğü için verilen sürede iyi çözüm "
          "bulunamıyor ve ayrıca doğrulayıcı orada bir açık yakaladığı için benimsemedik.\""),

    ("qa", (10, "Ceza terimi eklemek kazancı artırmış. Bu nasıl olabilir?")),
    ("p", "\"Dejenerasyon. Cezasız modelde binlerce farklı tarife tamamen aynı amaç değerini "
          "veriyor — çünkü fayda üretmeyen bir kaydırma bedava. Bu simetri LP gevşetmesini "
          "gevşetiyor ve çözücü iyi bir tamsayı çözümü bulamıyor. Ceza her olay için tek bir "
          "'minimum sapma' yönü tanımlayıp simetriyi kırıyor, gevşetmeyi sıkıyor. Sonuç: "
          "kaydırma %92'den %25'e inerken kazanç %3,89'dan %4,32'ye çıktı. λ'yı 0,1 ile 1,5 "
          "arasında taradık; sonuçların dar bir bantta kümelenmesi de gerçek optimuma "
          "yakınlığın işareti.\""),

    # =================================================================== EK A
    ("h1", ("A", "Ek A — Sayı künyesi ve yeniden sayım kanıtı")),
    ("h2", "A.1  Girdiden çözüme tek tabloda"),
    ("tbl", (["Kategori", "Ölçüt", "Değer"],
             [["**Girdi**", "Ham Excel satırı (4 dosya)", "89.094"],
              ["", "Bağlantı tablosu satırı", "57.317  (TK 7.850 · rakip 49.467)"],
              ["", "Operasyon günü", "7  *(veriden okunur, koda gömülü değil)*"],
              ["", "Yönlü O–D pazarı", "1.408  (ρ'suz olduğu için dışlanan: 48)"],
              ["", "TK uçuş numarası", "952  (eşli 776 · partnersiz 176)"],
              ["**Türetilmiş**", "TK bağlantı adayı", "7.693"],
              ["**Model**", "Pazar-gün grubu", "4.660"],
              ["", "Aday bağlantı (π)", "7.577"],
              ["", "Uçuş olayı", "5.376  (ayarlanabilir 4.553 · sabit 823)"],
              ["", "**İkili değişken (teslim modeli)**", "**100.552**"],
              ["", "İkili değişken (monolitik varyant)", "100.566"],
              ["**Çözüm**", "Baseline", "3.251.527"],
              ["", "**Nihai amaç (saf rekabetçilik)**", "**3.405.039**"],
              ["", "**İyileşme**", "**+153.512  (+%4,72)**"],
              ["", "**Global MIP-gap (cezalı amaç)**", "**%1,183**"],
              ["", "Çözüm süresi", "1.809 s + aşama-1 ~1,5 dk"]],
             [3.4, 6.6, 7.0], 8.4)),

    ("h2", "A.2  İkili değişken sayımı — iki modelin karşılaştırması"),
    ("p", "Aşağıdaki sayılar, her iki modeli yeniden kurup Pyomo üzerinden **tek tek "
          "sayarak** üretildi (çözüm yapılmadan, hiçbir çıktı dosyasına dokunulmadan). "
          "Belgelerdeki iki farklı toplamın kaynağı budur:"),
    ("tbl", (["Değişken ailesi", "Teslim modeli  (08)", "Monolitik varyant  (03 full)", "Fark"],
             [["`x` — zaman ataması", "**59.177**", "59.189", "−12"],
              ["`γ` — yenilen sayı seçici", "11.690", "11.690", "—"],
              ["`y` — bağlantı sunumu", "7.577", "7.577", "—"],
              ["`z` — azalan getiri slotu", "7.577", "7.577", "—"],
              ["`w` — koşullu yenme", "**7.529**", "7.531", "−2"],
              ["`β` — rakip yenildi mi", "7.002", "7.002", "—"],
              ["**TOPLAM**", "**100.552**", "**100.566**", "**−14**"],
              ["Kısıt sayısı", "67.877", "70.359", ""],
              ["G bağı", "2.643 (ilk-gün çapalı)", "4.503 (ortak bant)", ""],
              ["A2 bağı · F bağı", "874 · 1.395", "874 · 1.395", ""]],
             [4.6, 4.0, 4.4, 2.0], 8.4)),
    ("p", "**Farkın açıklaması:** Teslim modelinde bir olay, aynı fiziksel zaman damgasının "
          "birden çok operasyon gününde kayıtlı olması nedeniyle (gün-görünümü kopyası) "
          "aşama-1 değerine sabitlenir. O olayın 13 aday saati 1'e iner (−12 `x`) ve ona bağlı "
          "iki koşullu yenme göstergesi gereksizleşir (−2 `w`). Kısıt sayısındaki fark ise "
          "G'nin iki modelde farklı kurulmasından gelir: teslim modeli, bağımsız doğrulayıcıyla "
          "birebir aynı \"ilk-gün çapalı\" biçimi kullanır."),
    ("box", ("Belgelerdeki tutarsızlığın giderilmesi",
             "`reports/fullweek_polish.md`, teknik rapor ve model dokümanı **100.552** diyor "
             "(teslim modeli — doğru). Kod Rehberi ve sunum figürü **100.566** diyor "
             "(monolitik varyant — o da doğru, ama teslim edilen model değil). Sunumda tek "
             "bir sayı kullanacaksanız **100.552**'yi tercih edin ve sorulursa yukarıdaki "
             "farkı açıklayın.", "warn")),

    ("h2", "A.3  Nereye bakmalı — dosya haritası"),
    ("tbl", (["Aradığınız şey", "Dosya"],
             [["Matematiksel formülasyon (kümeler, kısıtlar, amaç)",
               "`docs/model_formulation.md`"],
              ["Formülasyon gerekçeleri, varsayımlar, ölçekleme",
               "`reports/technical_report.md`"],
              ["Kodun blok blok anlatımı", "`docs/Buke_KOD_REHBERI.docx`"],
              ["**MIP gap koşu raporu**", "`reports/fullweek_polish.md`"],
              ["**Bağımsız doğrulama sonuçları**", "`reports/validation_report.md`"],
              ["Duyarlılık analizi", "`reports/sensitivity_analysis.md`"],
              ["Veri sağlık teşhisi", "`reports/data_health_report.md`"],
              ["Nihai tarife çıktısı", "`output/optimized_schedule.csv`"],
              ["Pazar bazında sonuçlar", "`output/market_results.csv`"],
              ["Modelin kendisi", "`src/03_model.py`  (kısıtlar 372–748, çözücü 917–948)"],
              ["Tam hafta cilalama", "`src/08_fullweek_polish.py`"],
              ["Bağımsız doğrulayıcı", "`src/05_validate_solution.py`"]],
             [8.0, 9.0], 8.6)),

    ("h2", "A.4  Belgelerde fark ettiğimiz küçük tutarsızlıklar"),
    ("p", "Sunum öncesi bilmenizde fayda var; jüri kodu okursa karşılarına çıkabilir:"),
    ("bul", ["**İkili değişken sayısı** (100.552 / 100.566) — A.2'de açıklandı. Gerçek bir "
             "çelişki değil, iki farklı model.",
             "**`03_model.py` satır 101'deki yorum** \"appsi Highs MIP-start'ı kullanmıyor — "
             "etkisiz\" diyor. Bu yorum **eskimiş**: kurulu Pyomo sürümünde sıcak başlangıç "
             "gerçekten HiGHS'e aktarılıyor ve aşama-2 tam da buna dayanıyor. Kod doğru "
             "çalışıyor, yalnız yorum güncellenmemiş. Sorulursa: *\"O yorum eski bir Pyomo "
             "sürümünden kalma; aşama-2'nin sıcak başlangıcı fiilen çalışıyor ve kazancı "
             "raporda ölçülü.\"*",
             "**Olay sayısı** kaynağa göre 5.376 (model evreni) veya 5.473 (doğrulayıcı "
             "evreni) görünebilir. Fark beklenen: doğrulayıcı, amaç fonksiyonuna girmeyen "
             "pazarların uçuşlarını da sayar — çünkü onlar da hub kapasitesini fiziksel "
             "olarak dolduruyor.",
             "**MIP gap figürü** (Şekil 9.1) şematiktir: başlangıç değeri, nihai değer ve "
             "%1,18'lik boşluk gerçek koşudan, aradaki yakınsama eğrileri temsilîdir. "
             "Sorulursa bunu peşinen söyleyin."]),
    ("box", ("Son söz",
             "Bu projenin jüri karşısındaki en güçlü yanı yüksek bir skor değil — **her "
             "sayının nereden geldiğini gösterebiliyor olmanız**. Kaç değişken var, neden o "
             "kadar; hangi kısıt neden kapalı, hangi ölçümle; skor ne kadar iyi, hangi "
             "kanıtla; ve kod hata yaparsa bunu kim yakalıyor. Sunumda bu dört soruya "
             "rahatça cevap verebiliyorsanız, teknik derinlik zaten görünür olur.", "ok")),
]
