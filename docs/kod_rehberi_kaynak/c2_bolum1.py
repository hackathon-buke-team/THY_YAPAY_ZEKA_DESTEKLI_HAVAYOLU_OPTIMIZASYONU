# -*- coding: utf-8 -*-
"""Dokuman 2 — Bolum 1-3: ne degistiriyoruz, kac veri var, kac ihtimal var."""

ITEMS = [
    # ================================================================= 1
    ("h1", ("1", "Bizden tam olarak ne isteniyor?")),

    ("p", "Bu sorunun cevabı şaşırtıcı derecede dardır ve projeyi anlamanın anahtarı budur: "
          "**değiştirdiğimiz tek bir şey var.**"),
    ("img", ("g1_ne_degistiriyoruz.png",
             "Şekil 1.1 — Karar alanı ile veri alanının ayrımı. Sağ sütundaki hiçbir şeye "
             "dokunulmaz; hepsi girdi kabul edilir.")),

    ("h2", "1.1  Değiştirdiğimiz: THY uçuşlarının IST saatleri"),
    ("p", "Bir uçuşun THY tarifesindeki iki \"IST olayı\" vardır:"),
    ("bul", ["**Varış olayı** — o uçuş IST'e kaçta iniyor? (`Arr Time`, kodda rol = `arr`)",
             "**Kalkış olayı** — o uçuş IST'ten kaçta kalkıyor? (`Dep Time`, rol = `dep`)"]),
    ("p", "Modelin oynattığı **tek** şey bu saatlerdir. İki sınırla:"),
    ("tbl", (["Sınır", "Değer", "Anlamı"],
             [["Pencere (Wdev)", "±60 dk",
               "Bir uçuş kendi mevcut saatinden en fazla 1 saat öne/arkaya çekilebilir"],
              ["Izgara (Δ)", "10 dk",
               "Kaydırma yalnız 10'un katı olabilir → olay başına 13 seçenek"]],
             [3.2, 2.2, 11.6], 8.8)),

    ("h2", "1.2  Değiştirmediğimiz: her şey"),
    ("p", "Aşağıdakiler **girdi**dir, karar değil. Hiçbiri modelin çıktısında farklı bir "
          "değer alamaz:"),
    ("tbl", (["Dokunulmayan", "Neden karar değil?"],
             [["Uçuş rotaları, destinasyonlar",
               "Ağ tasarımı bu problemin kapsamı dışında; brief tarife saatlerini soruyor"],
              ["Uçuş sayısı, frekanslar",
               "Yeni uçuş eklemek/çıkarmak filo ve slot kararıdır"],
              ["Uçak tipi, koltuk kapasitesi", "Amaç fonksiyonunda yer almıyor"],
              ["Bilet fiyatları", "Rekabetçilik burada **süre** üzerinden ölçülüyor, fiyat üzerinden değil"],
              ["Uçuş süreleri (`legsum`)",
               "Fiziksel gerçek — `ElapsedTime1 + ElapsedTime2`, veriden gelir ve sabittir"],
              ["Uçak rotasyon eşleşmeleri",
               "`Flight Pairs.xlsx`'ten okunur; hangi uçağın hangi turu yaptığı verilmiştir"],
              ["Rakiplerin tarifeleri",
               "49.467 rakip itinerary'si sabit referanstır — onları kıyas için kullanırız"],
              ["`data/` altındaki dört Excel", "Salt-okunur; proje politikası gereği asla yazılmaz"]],
             [5.4, 11.6], 8.6)),
    ("box", ("Bu darlık bir kısıtlama değil, bir güç",
             "Karar alanı dar olduğu için **her iyileşme doğrudan tarife saatlerine "
             "atfedilebilir**. \"Sonuç %4,72 arttı\" dediğinizde bunun kaynağı belirsiz "
             "değildir: 1.067 uçuş hareketinin ortalama 19 dakika kaydırılması. Uçuş eklemek "
             "ya da fiyat oynatmak gibi başka kaldıraçlar karışmadığı için kazanç temiz ve "
             "savunulabilirdir.", "ok")),

    ("h2", "1.3  Peki neyi maksimize ediyoruz?"),
    ("p", "Amaç fonksiyonu iki ödülün gelir-ağırlıklı toplamıdır:"),
    ("box", ("Amaç  =  Σ_pazar  ρ · ( aktarma ödülü + sıralama ödülü )  −  λ · Σ|kaydırma|",
             "**ρ (rho)** — pazarın gelir/önem ağırlığı (3 ile 1.000 arası). Büyük pazarda "
             "kazanılan puan daha değerlidir.\n"
             "**Aktarma ödülü** — o pazarda sunulan her geçerli bağlantı için azalan getirili "
             "puan: 1, ½, ¼, …\n"
             "**Sıralama ödülü** — kaç rakibi geçtiğinize göre `change_ranking_input.xlsx` "
             "tablosundan okunan puan.\n"
             "**λ · kaydırma** — gereksiz tarife değişimini engelleyen ceza (λ = 0,3).")),
    ("p", "Raporlanan tüm sonuçlar **cezasız (saf) rekabetçilik** üzerindendir; λ yalnızca "
          "hangi kaydırmaların yapılacağını süzer, puanı ölçmez."),

    # ================================================================= 2
    ("h1", ("2", "Elimizde kaç adet veri var?")),

    ("p", "Sayılara girmeden önce genel resim: dört Excel dosyasındaki 89.094 satır, "
          "adım adım süzülerek 6.966 satılabilir bağlantıya dönüşüyor."),
    ("img", ("g2_veri_hunisi.png",
             "Şekil 2.1 — 89.094 ham satırdan 6.966 satılabilir bağlantıya. Her daralma bir "
             "modelleme kararıdır.")),
    ("box", ("Figürü okurken dikkat",
             "Üstteki şerit **eleme değil, dağılım** gösterir: 89.094 ham satırın 57.317'si "
             "bağlantı tablosudur ve huniye o girer. Kalan 31.777 satır (ödül tablosu, ρ "
             "tablosu, rotasyon eşleri) atılmaz — modelde başka amaçlarla sonuna kadar "
             "kullanılır. Alttaki çubuklar ise gerçek süzülmedir; her çubuk bir üstündekinin "
             "alt kümesidir. **Her adımın ayrıntılı anlatımı için bkz. Ek B.**", "info")),

    ("h2", "2.1  Ham girdi — 4 Excel dosyası, 89.094 satır"),
    ("tbl", (["Dosya", "Satır", "Sütun", "İçerik"],
             [["`O&D Rakip Bağlantı Tablosu_updated.xlsx`", "**57.317**", "17",
               "Tüm havayollarının IST aktarmalı bağlantıları"],
              ["`change_ranking_input.xlsx`", "**22.140**", "4",
               "(rakip sayısı, ilk sıra, son sıra) → ödül ağırlığı"],
              ["`Yolcu Verisi_masked.xlsx`", "**8.075**", "3",
               "O–D pazarı → gelir/önem katsayısı ρ"],
              ["`Flight Pairs.xlsx`", "**1.562**", "4",
               "Uçuş no → uçak rotasyon eşi (Pair)"],
              ["**TOPLAM**", "**89.094**", "—", "—"]],
             [6.4, 2.2, 1.6, 6.8], 8.6)),

    ("h2", "2.2  Bağlantı tablosunun içi"),
    ("tbl", (["Ölçüt", "Değer"],
             [["Toplam satır (itinerary)", "57.317"],
              ["Bunun **THY (TK)** olanı", "**7.850**"],
              ["Rakip olanı", "49.467"],
              ["Farklı taşıyıcı sayısı", "88 (TK dâhil) — rakip 87"],
              ["Operasyon günü", "**7** (1–7); takvim aralığı 3–11 Ağustos 2025"],
              ["Benzersiz yönlü O–D pazarı", "**1.408**"],
              ["Benzersiz (pazar, gün) anahtarı", "8.864"],
              ["TK bağlantısı **olan** pazar", "805"],
              ["Yalnız rakibin olduğu pazar", "603"],
              ["Yalnız TK'nın olduğu pazar (rakipsiz)", "266"],
              ["Benzersiz TK uçuş numarası", "**952** (480 gelen + 498 giden)"],
              ["Mevcut tarifede [60,300] penceresinde olan TK bağlantısı",
               "6.986 / 7.850 (**%89,0**)"],
              ["Penceresi çok uzun olan (> 300 dk)", "864"],
              ["Penceresi çok kısa olan (< 60 dk)", "0"]],
             [8.6, 8.4], 8.8)),
    ("box", ("\"%89'u zaten uygun\" — o hâlde iyileştirme nereden geliyor?",
             "Uygun olmak yeterli değil; **rakipten hızlı** olmak gerekiyor. Bir bağlantı "
             "pencerede olabilir ama toplam yolculuk süresi (J) rakibinkinden uzunsa sıralama "
             "puanı getirmez. Optimizasyon iki şeyi birden yapar: pencere dışındaki 864 "
             "bağlantının bir kısmını içeri çeker **ve** zaten uygun olanların boşluğunu "
             "kısaltarak J'yi düşürüp rakip geçer.", "info")),

    ("h2", "2.3  Diğer üç tablonun içi"),
    ("tbl", (["Tablo", "Ölçüt", "Değer"],
             [["Yolcu Verisi", "Benzersiz O–D", "8.066 (8 tekrarlı satır ayıklandı)"],
              ["", "ρ aralığı", "**3 – 1.000**"],
              ["", "Bağlantı tablosunda olup ρ'su **olmayan** pazar", "**48** → amaç evreninden dışlandı"],
              ["Ranking lookup", "Satır", "22.140"],
              ["", "Desteklediği maks. rakip sayısı N", "**40**"],
              ["", "Ağırlık aralığı", "−0,9744 … +1,6321"],
              ["", "Sıralamanın kötüleştiği satır", "10.660 (tablo cezayı da tanımlıyor)"],
              ["Flight Pairs", "Satır / benzersiz uçuş no", "1.562 / 1.381"],
              ["", "Benzersiz Pair (rotasyon grubu)", "708"],
              ["", "TK uçuş no'su olup **partneri olmayan**", "**176** → bu uçuşlar sabit kabul edildi"]],
             [3.2, 7.4, 6.4], 8.4)),
    ("p", "Rakip sayısı N için **taşıyıcı bazlı** sayım seçildi. Gerekçe veriden geldi: "
          "itinerary bazlı sayımda 73 pazar-gün 40'ı aşıyor (ödül tablosunun dışına çıkıyor), "
          "taşıyıcı bazlı sayımda ise en yüksek değer **17** — tablo tam kapsıyor. Ortalama "
          "N = 3,45."),

    ("h2", "2.4  Türetilmiş veri katmanı — `derived/`, 118.177 satır"),
    ("tbl", (["Dosya", "Satır", "İçerik"],
             [["`competitor_itineraries.csv`", "49.467", "Rakiplerin tüm bağlantı seçenekleri"],
              ["`competitor_times_carrier.csv`", "23.975", "(pazar, gün, taşıyıcı) → en iyi J"],
              ["`ranking_lookup.csv`", "22.140", "Sıralama ödül tablosu"],
              ["`tk_connections.csv`", "**7.693**", "TK bağlantı adayları (tekilleştirilmiş)"],
              ["`market_n_od.csv`", "6.953", "(pazar, gün) → rakip taşıyıcı sayısı"],
              ["`flight_block_times.csv`", "5.471", "(uçuş, gün, rol) → bacak blok süresi"],
              ["`markets.csv`", "1.408", "Pazar + ρ + kapsam bayrakları"],
              ["`flight_rotation.csv`", "894", "TK uçuşlarının rotasyon eşleri"],
              ["`tk_flights_without_partner.csv`", "176", "Sabit kabul edilen uçuş numaraları"],
              ["**TOPLAM**", "**118.177**", "—"]],
             [6.0, 2.2, 8.8], 8.6)),
    ("p", "7.850 TK satırı neden 7.693 oldu? Hafta normalizasyonundan sonra **birebir özdeş** "
          "kalan 157 kopya satır atıldı. İkisini iki ayrı aday saymak, aynı ürüne çifte "
          "aktarma ödülü yazdırırdı."),

    ("h2", "2.5  Çıktı — `output/`, 17.317 satır"),
    ("tbl", (["Dosya", "Satır", "İçerik"],
             [["`selected_connections.csv`", "**6.966**", "Çözümde sunulan her bağlantı"],
              ["`market_results.csv`", "**4.660**", "Her (pazar, gün) için sonuç ve ödül dökümü"],
              ["`optimized_schedule.csv`", "**4.554**", "Her ayarlanabilir uçuş olayı: eski → yeni saat"],
              ["`g_band_exemptions.csv`", "1.132", "Belgeli G düzenlilik muafiyetleri"],
              ["`sweep_results.csv`", "5", "λ taraması sonuçları"]],
             [6.0, 2.2, 8.8], 8.8)),

    # ================================================================= 3
    ("h1", ("3", "Kaç ihtimal var?")),

    ("h2", "3.1  Hesabın kendisi"),
    ("p", "Modelde **5.376 uçuş olayı** var. Bunların **823**'ü sabit (rotasyon partneri "
          "bilinmiyor → kımıldatılmıyor), **4.553**'ü ayarlanabilir. Her ayarlanabilir olayın "
          "13 seçeneği var ve seçimler birbirinden bağımsız yapılabilir:"),
    ("box", ("Tarife karar uzayı  =  13 ^ 4.553  ≈  10 ^ 5.072",
             "Yani 1'in arkasına **beş bin yetmiş iki** sıfır. Bu sayı yazıya dökülemez; "
             "10⁵⁰⁷² ifadesinin kendisi bile ancak üstel gösterimle anlatılabilir.")),
    ("img", ("g3_arama_uzayi.png",
             "Şekil 3.1 — Karşılaştırma. Sol paneldeki \"devasa\" sayılar, sağ panelin "
             "yanında çubuk olarak bile görünmez.")),
    ("p", "Sağ paneldeki iki çubuk iki **ayrı** sorunun cevabıdır — hangisinin \"kaç ihtimal "
          "var?\" sorusunu yanıtladığını bölüm 3.4'te netleştiriyoruz. Önce bu sayının "
          "nereden geldiğine ve ne kadar büyük olduğuna bakalım."),

    ("h2", "3.2  13'ün 4.553'üncü kuvveti niye? — çarpım kuralı"),
    ("p", "Sayı büyük olduğu için sihirli görünüyor ama hesabı ilkokul matematiği. Her "
          "ayarlanabilir olay için 13 seçenek var ve **her olay için ayrı ayrı** seçim "
          "yapılıyor. Küçükten başlayalım:"),
    ("tbl", (["Kaç uçuş olayı?", "Kaç farklı tarife?", "Hesap"],
             [["1", "13", "13"],
              ["2", "169", "13 × 13"],
              ["3", "2.197", "13 × 13 × 13"],
              ["5", "371.293", "13⁵"],
              ["10", "137.858.491.849  (≈138 milyar)", "13¹⁰"],
              ["50", "≈ 10⁵⁶", "13⁵⁰"],
              ["**4.553**", "**≈ 10⁵·⁰⁷²**", "**13⁴⁵⁵³**"]],
             [3.6, 7.4, 6.0], 8.8)),
    ("box", ("Neden toplama değil çarpma?",
             "Çünkü seçimler **birbirinden bağımsız** yapılıyor. İlk uçuş için 13 seçeneğin "
             "*her biri* için, ikinci uçuşun 13 seçeneği de ayrı ayrı denenebilir → "
             "13 × 13. Üçüncü uçuş eklendiğinde bu 169'un her biri için yine 13 seçenek "
             "doğar → 2.197. Her yeni uçuş, olasılık sayısını **13 katına çıkarır**.")),
    ("p", "Peki uçuşlar birbirinden bağımsızsa neden her birini tek tek en iyilemiyoruz? "
          "İşte problemin asıl zorluğu burada: uçuşların **saat seçimi** bağımsız, ama "
          "**sonuçları** bağımsız değil."),
    ("bul", ["Bir gelen uçuşu kaydırınca ona bağlı onlarca bağlantının boşluğu değişir",
             "Aynı 10 dk kovasına giren uçuş sayısı değişir (**F** kapasitesi)",
             "Uçağın dönüş turu etkilenir (**A2** rotasyonu)",
             "O uçuşun diğer günlerdeki saatiyle uyumu bozulabilir (**G** düzenliliği)",
             "Pazarın ters yönüyle bağlantı dengesi bozulabilir (**E1**)"]),
    ("box", ("Tüm zorluk bu bağlaşıklıktan doğuyor",
             "Uçuşlar gerçekten birbirinden bağımsız olsaydı her birini ayrı ayrı en "
             "iyilerdik: 4.553 × 13 = **59.189 deneme**, saniyeler sürerdi. Ama bir uçuşu "
             "oynatmak diğerlerinin puanını da değiştirdiği için hepsini **aynı anda** "
             "değerlendirmek zorundayız — kombinasyon sayısı işte o zaman patlıyor.",
             "warn")),

    ("h2", "3.3  10⁵·⁰⁷² ne kadar büyük?"),
    ("bul", ["Bu sayı yazıldığında **5.072 basamaklıdır** — normal punto ile yaklaşık iki "
             "sayfa dolusu rakam.",
             "Gözlemlenebilir evrendeki **atom sayısı** 10⁸⁰'dir. Bizim uzayımız bunun "
             "10⁴·⁹⁹² katıdır.",
             "Saniyede **bir milyar** kombinasyon deneyen bir bilgisayar, **Büyük "
             "Patlama'dan beri** çalışsaydı ancak 4,4 × 10²⁶ kombinasyon denerdi — yani "
             "işin 10⁻⁵·⁰⁴⁵'i kadarını. Pratikte **sıfır**."]),
    ("p", "Bu yüzden \"hepsini dene\" yaklaşımı bir seçenek değil. Ne bugün, ne de "
          "gelecekte herhangi bir bilgisayarla."),

    ("h2", "3.4  İkinci çubuk ne? Hangisi \"gerçek cevap\"?"),
    ("p", "Şekil 3.1'deki mavi çubuk kırmızıdan çok daha uzun. Bu, \"asıl problem o\" "
          "anlamına **gelmiyor**. İki çubuk iki ayrı sorunun cevabı:"),
    ("tbl", (["", "① 13⁴⁵⁵³ ≈ 10⁵·⁰⁷²", "② 2¹⁰⁰·⁵⁶⁶ ≈ 10³⁰·²⁷³"],
             [["Hangi soruyu yanıtlar?",
               "**Kaç farklı TARİFE üretilebilir?**",
               "Çözücünün formel arama kutusu ne kadar büyük?"],
              ["Neyi sayar?", "Yalnız uçuş saati seçimlerini (`x`)",
               "**Tüm** ikili değişkenleri (`x`, `y`, `z`, `w`, `β`, `γ`)"],
              ["Her nokta gerçek bir tarife mi?", "**Evet** — her biri farklı bir tarife",
               "Hayır — çoğu geçersiz veya `x`'ten zaten türetilmiş"],
              ["\"Kaç ihtimal var?\" sorusunun cevabı", "**BU**", "Bu değil"]],
             [4.2, 6.4, 6.4], 8.6)),
    ("box", ("Neden ikisi birden var?",
             "Model, \"bu bağlantı sunuluyor mu?\" (`y`), \"bu rakip yenildi mi?\" (`β`) gibi "
             "soruları da ikili değişkenle temsil eder — çünkü ödül mantığı ancak böyle "
             "**doğrusal** yazılabilir. Ama bu değişkenler serbest değildir: kısıtlar onları "
             "büyük ölçüde `x`'e kilitler. Saatleri seçtiğinizde hangi bağlantının uygun "
             "olduğu, hangi rakibin yenildiği zaten belli olur.", "info")),
    ("p", "Yani ② sayısı çözücünün *çalışma alanının* boyutudur, gerçekten farklı "
          "çözümlerin sayısı değil. **\"Kaç ihtimal var?\" diye sorulduğunda verilecek "
          "cevap ①'dir: 13⁴⁵⁵³.**"),
    ("box", ("\"Bunu bir for döngüsüyle çözemez miydik?\"",
             "Hayır. Saniyede bir milyar kombinasyon deneyen bir bilgisayar bile 10⁵·⁰⁷² "
             "ihtimali bitiremez — Büyük Patlama'dan beri çalışsa işin 10⁻⁵·⁰⁴⁵'ini yapmış "
             "olurdu. Açgözlü (greedy) bir sezgisel yazabilirsiniz ve bir cevap alırsınız; "
             "ama o cevabın en iyiye ne kadar yakın olduğunu **asla** söyleyemezsiniz. "
             "MIP çözücünün verdiği %1,18'lik gap tam olarak bu eksiği kapatır.", "warn")),
    ("p", "Peki çözücü kaç noktayı gerçekten inceliyor? Milyarlar değil — dallanma ağacında "
          "**birkaç bin ile birkaç yüz bin arası düğüm**. 10⁵·⁰⁷²'nin yanında bu, "
          "hayal edilemeyecek kadar küçük bir oran. Nasıl başardığını Bölüm 5'te göreceğiz."),

    ("h2", "3.5  İhtimalleri neyle değiştiriyoruz?"),
    ("img", ("g4_uzay_daralmasi.png",
             "Şekil 3.2 — Her modelleme kararı arama uzayını astronomik ölçüde küçültüyor.")),
    ("p", "Dört kaldıraç var ve üçü doğrudan sizin elinizde:"),
    ("tbl", (["Kaldıraç", "Ne yapar?", "Uzaya etkisi", "Kodda"],
             [["**Izgara (Δ = 10 dk)**",
               "Sürekli zamanı 13 ayrık kovaya indirger",
               "121⁴⁵⁵³ → 13⁴⁵⁵³ · yani 10³⁴⁹⁵ kat küçültür",
               "`CFG[\"delta_min\"]`"],
              ["**Pencere (Wdev = ±60)**",
               "Her uçuşu kendi saatine bağlar",
               "Sınırsız olsa aday sayısı 144'e çıkardı",
               "`CFG[\"wdev_min\"]`"],
              ["**Sabit uçuşlar**",
               "823 olayın seçeneğini 1'e indirir",
               "13⁸²³ = 10⁹¹⁷ kat küçültür",
               "`tk_flights_without_partner.csv`"],
              ["**Kısıtlar (A1–G)**",
               "Uzayı küçültmez — içindeki hangi noktaların **geçerli** olduğunu belirler",
               "Uygun bölge, uzayın çok küçük bir alt kümesi",
               "`build_model()`"]],
             [3.4, 5.4, 5.0, 3.2], 8.2)),
    ("box", ("Kritik ayrım: uzayı küçültmek ≠ kısıt koymak",
             "**Izgara ve pencere** arama uzayının *büyüklüğünü* değiştirir — daha az nokta "
             "vardır.\n"
             "**Kısıtlar** ise uzayın büyüklüğüne dokunmaz; hangi noktaların **uygun** "
             "olduğunu söyler. Aslında kısıtlar çözücünün işini *kolaylaştırır*: uygun bölge "
             "daraldıkça budanabilecek dal sayısı artar.", "info")),

    ("h2", "3.6  Model, işe başlamadan önce de eliyor"),
    ("p", "Çözücüye gitmeden, model kurulurken bile ciddi bir eleme yapılır. En belirgin "
          "örnek rakip yenme değişkenleridir. Teorik olarak her (bağlantı × rakip) çifti için "
          "bir değişken gerekir — toplam **13.015** çift. Ama kod üç duruma ayırır:"),
    ("img", ("g9_eleme.png",
             "Şekil 3.3 — Çiftlerin %42'si için hiç değişken yaratılmıyor.")),
    ("tbl", (["Durum", "Koşul", "Sayı", "Ne yapılır?"],
             [["Asla yenemez", "İzin verilen boşluk, ulaşılabilir en küçüğün altında",
               "**3.384** (%26)", "Değişken **yaratılmaz**"],
              ["Her zaman yener", "Pencere içindeki her boşlukta rakip geçilir",
               "**2.100** (%16)", "`w` yerine doğrudan `y` kullanılır"],
              ["Koşullu", "Boşluğa bağlı — bazen yener, bazen yenmez",
               "**7.531** (%58)", "Gerçek `w` değişkeni + 2 kısıt"]],
             [2.8, 6.4, 2.6, 5.2], 8.4)),
    ("p", "Benzer elemeler her yerde var: F kapasite kısıtı yalnız **bağlayıcı olabilecek** "
          "kovalara eklenir (1.395 kısıt), G düzenliliği penceresi yetişmeyen 4 grup için "
          "atlanır. Bunlar kozmetik değil — büyük MIP'lerde çözülebilirlik ile "
          "çözülemezlik arasındaki fark tam olarak bu tür ayıklamalardır."),
]
