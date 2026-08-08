# -*- coding: utf-8 -*-
"""Dokuman 3 — Bolum 6: Juri soru bankasi."""

ITEMS = [
    ("h1", ("6", "Jüri Soru Bankası — 45 soru, açıklamalı cevap")),
    ("p", "Sorular altı gruba ayrıldı. Her cevap **kısa bir özet cümleyle** başlıyor; "
          "ardından gerekçe ve sayısal dayanak geliyor. Sunumda önce özet cümleyi söyleyin, "
          "jüri derinleşmek isterse gerisini anlatın."),

    # ==================================================== A
    ("h2", "A · Problem anlayışı"),

    ("qa", (1, "Problemi kendi cümlelerinizle anlatır mısınız?")),
    ("p", "THY'nin yolcularının büyük kısmı doğrudan uçmuyor: bir uçuşla İstanbul'a geliyor, "
          "bekliyor, ikinci uçuşla gideceği şehre gidiyor. Yolcu için önemli olan **kapıdan "
          "kapıya toplam süre**. Aynı yolcuyu rakipler kendi merkezleri üzerinden taşımak "
          "istiyor — kim daha hızlıysa tercih ediliyor."),
    ("p", "Bizim elimizdeki tek kaldıraç **İstanbul'daki iniş ve kalkış saatleri**. Bu "
          "saatleri, tüm operasyonel kuralları koruyarak, gelir-ağırlıklı rekabetçilik "
          "puanını en yükseğe çıkaracak şekilde yeniden düzenledik."),

    ("qa", (2, "Neden sadece saatleri değiştiriyorsunuz? Uçuş ekleseniz daha çok "
               "kazanmaz mıydınız?")),
    ("p", "Kazanırdık — ama o başka bir problem. Uçuş eklemek filo, mürettebat, slot ve "
          "yatırım kararıdır; brief bize tarife saatlerini soruyor. Ayrıca **dar karar "
          "alanı bir avantaj**: elde ettiğimiz %4,72'lik kazancın kaynağı belirsiz değil — "
          "1.067 uçuş hareketinin ortalama 19 dakika kaydırılması. Uçuş eklemek ya da fiyat "
          "oynatmak gibi başka kaldıraçlar karışmadığı için kazanç temiz ve savunulabilir."),

    ("qa", (3, "±60 dakikalık pencere ve 10 dakikalık ızgara nereden geldi?")),
    ("p", "İkisi de bizim modelleme tercihimiz — brief bir sınır koymuyor."),
    ("bul", ["**±60 dakika:** sınırsız bırakılsaydı model bir uçuşu sabahtan akşama "
             "taşıyabilirdi. Kâğıtta iyi, gerçekte uygulanamaz. Pencere \"iyileştirme yap "
             "ama tarifeyi tanınmaz hâle getirme\" demenin sayısal karşılığı.",
             "**10 dakika:** havayolu tarifeleri zaten 5–10 dakikalık dilimlerde yayınlanır. "
             "Ayrıca hub kapasitesi de 10 dakikalık kovalarda sayılıyor — ikisinin aynı "
             "birim olması kısıtların birbirine çevrilebilmesini sağlıyor.",
             "Duyarlılık analizinde her ikisi de sınandı (`07_sensitivity.py`); Wdev=30 ve "
             "Wdev=90 varyantları raporlandı."]),

    ("qa", (4, "Bağlantı penceresi neden 60–300 dakika?")),
    ("p", "Bu brief'ten geliyor, bizim seçimimiz değil. Mantığı: 60 dakikadan kısa bir "
          "aktarmaya yolcu yetişemez (bagaj, pasaport, kapı değişimi); 300 dakikadan uzun "
          "bekleme ise satılabilir bir ürün değildir — yolcu başka havayolunu tercih eder."),

    ("qa", (5, "Amaç fonksiyonunuzu açıklar mısınız?")),
    ("box", ("Amaç = Σ_pazar  ρ · (aktarma ödülü + sıralama ödülü)  −  λ · Σ|kaydırma|",
             "**ρ** — pazarın gelir ağırlığı (3–1.000). Büyük pazardaki kazanç daha değerli.\n"
             "**Aktarma ödülü** — sunulan her geçerli bağlantı için azalan getirili puan "
             "(1, ½, ¼ …). Gerçek hayatta ilk aktarma seçeneği çok değerlidir, beşincisi "
             "neredeyse hiç.\n"
             "**Sıralama ödülü** — kaç rakip geçtiğimize göre organizatörün verdiği lookup "
             "tablosundan okunur.\n"
             "**λ · kaydırma** — gereksiz tarife değişimini engelleyen ceza (λ = 0,3).")),
    ("p", "Önemli not: raporladığımız tüm sonuçlar **cezasız (saf) rekabetçilik** "
          "üzerindendir. λ yalnızca hangi kaydırmaların yapılacağını süzer; puanı ölçmez."),

    # ==================================================== B
    ("h2", "B · Model ve formülasyon"),

    ("qa", (6, "Neden MIP? Neden makine öğrenmesi kullanmadınız?")),
    ("p", "Çünkü bu bir **tahmin** problemi değil, bir **karar** problemi. Makine öğrenmesi "
          "geçmişten öğrenip gelecek tahmin eder; burada tahmin edilecek bir şey yok — "
          "kısıtlar altında en iyi kararı arıyoruz."),
    ("tbl", (["", "Sinir ağı olsaydı", "MIP ile"],
             [["Kısıtlar", "Garanti edilemez — ihlal edebilir", "**Matematiksel olarak garanti**"],
              ["\"En iyi mi?\"", "Cevaplanamaz", "**%1,18 gap ile kanıtlanır**"],
              ["Açıklanabilirlik", "Kara kutu", "Her kısıt ve terim tek tek okunabilir"],
              ["Veri ihtiyacı", "Binlerce etiketli örnek", "Yok — kurallar yeterli"]],
             [3.0, 6.4, 7.6], 8.6)),

    ("qa", (7, "Kaç değişken ve kaç kısıt var?")),
    ("p", "**100.566 ikili değişken, 70.359 kısıt.** Dökümü: `x` (uçuş saati atamaları) "
          "59.189 · `γ` (yenilen rakip sayısı seçicileri) 11.690 · `y` (bağlantı sunuluyor "
          "mu) 7.577 · `z` (ödül slotları) 7.577 · `w` (rakip yeniliyor mu) 7.531 · `β` "
          "(rakip yenildi mi) 7.002."),

    ("qa", (8, "Karar değişkeniniz tam olarak ne? Neden bağlantı bazlı değil?")),
    ("p", "Karar birimimiz **olay**: `(uçuş numarası, rol, gün)`. Rol = IST'e varış veya "
          "IST'ten kalkış."),
    ("box", ("Neden bağlantı bazlı değil — bu kritik bir tasarım kararı",
             "Bir uçuş **20 farklı bağlantıda** yer alabilir: IST'e gelen bir uçak, oradan "
             "kalkan 20 uçuşla 20 bağlantı oluşturur. Bağlantı başına karar verseydik aynı "
             "uçağa 20 farklı varış saati atanabilirdi — fiziksel olarak imkânsız bir "
             "tarife.\n\n"
             "Olay soyutlaması bu tutarsızlığı **yapısal olarak imkânsız** kılıyor: aynı "
             "anahtar → aynı karar.", "ok")),

    ("qa", (9, "Azalan getiri ödülü neden (½)^(j−1)?")),
    ("p", "Gerçek hayatta bir pazarda **ilk** aktarma seçeneği çok değerlidir; ikincisi "
          "biraz daha az; beşincisi neredeyse hiç. Yolcu zaten bir tane seçecek."),
    ("p", "Geometrik dizi seçilmesinin iki nedeni var: (i) hızlı ama pürüzsüz azalıyor, "
          "(ii) toplamı 2'ye yakınsıyor — yani tek bir pazarın puanı sınırsız büyüyemiyor, "
          "model tek pazara odaklanıp diğerlerini ihmal edemiyor."),
    ("img", ("f06_azalan_getiri.png", "Şekil 6.1 — Ödül dizisi ve kümülatif toplam.")),

    ("qa", (10, "big-M nedir? M değerlerini nasıl seçtiniz?")),
    ("p", "big-M, *\"eğer şu koşul geçerliyse şu kural işlesin\"* mantığını doğrusal hale "
          "getiren bir tekniktir. Örnek: \"bağlantı sunuluyorsa (y=1) boşluk ≥ 60\" kuralını "
          "`boşluk ≥ 60 − Mlo·(1−y)` olarak yazarız. y=1 iken kural devreye girer, y=0 iken "
          "sağ taraf çok küçülür ve kural etkisizleşir."),
    ("box", ("M seçimi neden kritik?",
             "**Çok küçük M:** kural y=0 iken bile bağlar → model **yanlış** olur.\n"
             "**Çok büyük M:** model doğru ama doğrusal gevşeme zayıflar, hiçbir dal "
             "budanamaz, çözücü ağaçta kaybolur.\n\n"
             "Biz genel bir sabit yerine **her bağlantı için ayrı ayrı** hesapladık: "
             "`Mlo = max(0, 60 − o bağlantının ulaşabileceği en küçük boşluk)`. Aday saatler "
             "sınırlı olduğu için bu aralık önceden bilinebiliyor — sonuç mümkün olan en "
             "sıkı M.", "ok")),

    ("qa", (11, "Neden tek-sıcak (one-hot) kodlama? Sürekli bir saat değişkeni daha basit "
                "olmaz mıydı?")),
    ("p", "Görünüşte evet, pratikte hayır. Tek-sıcak kodlama iki büyük kazanç sağladı:"),
    ("num", ["**Tarife-değişim cezası tam doğrusal oldu.** `|θ − mevcut saat|` mutlak değeri "
             "normalde ek değişken ve big-M ister. Ama her olayda tam bir `x` = 1 olduğu "
             "için `|θ−cur| = Σ|v−cur|·x[olay,v]` yazılabiliyor — katsayılar sabit, "
             "**sıfır ek değişken, sıfır big-M**.",
             "**F kapasitesi doğrudan yazılabildi.** \"Bu kovada kaç uçuş var?\" sorusu "
             "`Σ x[olay, kova] ≤ 10` oluyor. Sürekli değişkenle bu soruyu sormak için ayrıca "
             "gösterge değişkenleri kurmak gerekirdi."]),

    ("qa", (12, "B2 kısıtını neden kapattınız? Model eksik kalmıyor mu?")),
    ("p", "B2 \"uygun olan her bağlantıyı sunmak zorundasın\" der. Açık olduğunda **E1 yön "
          "dengesiyle çatışıyor**: bir yönde çok, ters yönde az bağlantı olan asimetrik "
          "pazarlarda ikisi aynı anda sağlanamıyor ve model **infeasible** oluyor — yani "
          "hiç çözüm alamıyoruz."),
    ("p", "Model eksik kalmıyor çünkü **amaç fonksiyonu zaten sunmayı ödüllendiriyor** "
          "(aktarma ödülü). Model kârlı olan her bağlantıyı kendiliğinden sunuyor. B2 açık "
          "olsaydı hiçbir sonucumuz olmazdı."),

    ("qa", (13, "E2 kısıtını tam ölçekte kapattınız — bu modeli zayıflatmıyor mu?")),
    ("p", "E2, gidiş ve dönüş yönlerinin en iyi yolculuk sürelerinin 30 dakikadan fazla "
          "ayrılmamasını ister. **Küçük alt-örnekte açık ve doğrulanmış** durumda; yalnız "
          "tam ölçekte kapalı."),
    ("p", "Gerekçe ölçülmüş: E2'nin \"minimum seçimi\" yapısı bağlantı başına iki big-M "
          "kısıtı ve bir ek ikili değişken getiriyor; doğrusal gevşemesi o kadar zayıflıyor "
          "ki HiGHS tam veride **tek bir uygun çözüm bile** bulamıyor. Tanı yöntemi kodda "
          "yazılı: çekirdek + yalnız E2 çözülemiyor, çekirdek + A2/G/F/E1 hepsi hızlı."),
    ("p", "En önemlisi: bu karar **gizlenmedi**. `output/results_summary.md`'nin notlar "
          "bölümünde açıkça ilan ediliyor."),

    ("qa", (14, "A2 uçak rotasyon kısıtını nasıl kurdunuz?")),
    ("p", "Temel kural: **dönüş varışı ≥ gidiş kalkışı + T_OB + τ + T_IB** (gidiş uçuş "
          "süresi + 45 dk yer süresi + dönüş uçuş süresi). Aynı uçak gidip döneceği için "
          "fiziksel zorunluluk."),
    ("p", "İncelik `sep` değerinin nasıl seçildiğinde: `sep = min(brief-exact, mevcut tur)`. "
          "Bu iki riski aynı anda kapatıyor — gerçek aynı-gün turlar asla brief minimumunun "
          "altına sıkışmıyor, gece-aşan çiftlerde ise mevcut desen bozulmuyor."),
    ("img", ("f11_a2_rotasyon.png", "Şekil 6.2 — Minimum tur süresi.")),

    ("qa", (15, "Gün ayrıştırması yaptınız — gece-aşan turlar nasıl korunuyor?")),
    ("p", "Bu, projenin en zarif teknik parçası. Gün h'nin kalkışı ile gün h+1'in dönüşü "
          "farklı MIP'lerde çözülüyor, yani model bu ikisini bağlayamaz."),
    ("p", "Çözüm: mevcut tarifedeki boşluk payı (slack) **statik olarak ikiye bölünüyor** ve "
          "iki tek-taraflı sınır konuyor — bugünün kalkışı en fazla `slack/2` geç kayabilir, "
          "bugünün dönüş varışı en fazla `slack/2` erken kayabilir. İkisi birlikte minimum "
          "tur eşitsizliğini **yapısal olarak** garanti ediyor: iki gün birbirini hiç "
          "görmese bile ihlal matematiksel olarak imkânsız."),

    ("qa", (16, "Hub kapasitesi 10/15 nereden geliyor? Gerçekten bağlayıcı mı?")),
    ("p", "Brief'ten: her 10 dakikalık kovada en fazla 10 kalkış, 15 varış."),
    ("box", ("Kritik veri bulgusu",
             "Mevcut tarifedeki kova aşımlarının **tamamı** ayarlanabilir uçuşların "
             "kümelenmesinden geliyor; **sabit uçuşlar hiçbir kovada baz kapasiteyi "
             "aşmıyor** (kalkışta en fazla 4 ≤ 10, varışta 5 ≤ 15).\n\n"
             "Bu bulgu sayesinde brief'in **gerçek** 10/15 değerini uygulayabildik. Aksi "
             "hâlde `max(baz, mevcut)` gibi gevşetilmiş bir kapasite kullanmak gerekirdi ki "
             "bu F'yi fiilen etkisiz bir kısıta çevirirdi.", "ok")),
    ("p", "Ayrıca modellenmeyen (ρ'suz) pazarların uçuşları da kovalarda **sabit doluluk** "
          "olarak sayılıyor — fiziksel kapasite tüm TK uçuşlarıyla korunuyor."),

    ("qa", (17, "Tarife düzenliliği (G) neden gerekli?")),
    ("p", "Yolcu \"her gün 08:30 uçuşu\" bekler. Aynı uçuş numarası bir gün 07:00, ertesi "
          "gün 09:00 kalkarsa tarife satılabilirliğini kaybeder; ayrıca mürettebat ve yer "
          "hizmetleri planlaması bozulur. G, aynı uçuşun saat-içi zamanını günler arası "
          "±15 dakikalık bir bantta tutuyor."),

    ("qa", (18, "E1 yön dengesi neden var? Kârlı yönü şişirmek daha iyi olmaz mı?")),
    ("p", "Kâğıtta daha iyi olur, gerçekte olmaz. Yolcu **gidiş-dönüş** ister; tek yönü "
          "şişirip dönüşü ihmal eden bir tarife satılabilir bir ürün değildir. E1, "
          "`|n_od − n_do| ≤ 0,20 × (n_od + n_do)` ile bu gerçekliği modele sokuyor."),
    ("p", "Bedeli var: model 611 uygun bağlantıyı sunmuyor, bunun bir kısmı E1 yüzünden. "
          "Bilinçli bir ticari tercih."),

    ("qa", (19, "Modelin en zayıf yanı ne?")),
    ("p", "Dürüst cevap: **E2'nin tam ölçekte kapalı olması.** Yönler arası süre dengesi "
          "şu an denetlenmiyor; yalnız bağlantı **sayısı** dengesi (E1) uygulanıyor. Küçük "
          "örnekte E2 açık ve doğrulanmış ama tam veride çözülebilirlik engeli var."),
    ("p", "İkinci zayıflık: **823 uçuş olayı donduruldu** çünkü rotasyon partnerleri veride "
          "yok. Bu bilgi sağlanırsa daha iyi bir sonuç elde edilebilir."),

    ("qa", (20, "Neden 823 uçuşu kımıldatmadınız?")),
    ("p", "176 TK uçuş numarasının `Flight Pairs.xlsx`'te karşılığı yok. Yani o uçuşu hangi "
          "uçağın yaptığını, o uçağın sonra nereye gittiğini bilmiyoruz."),
    ("p", "Kaydırabilirdik — puan artardı. Ama fiziksel olarak uygulanamayan bir tarife "
          "üretmiş olabilirdik ve **bunu kontrol edecek veri yok**. Projenin kuralı: "
          "*doğrulayamadığın şeye dokunma.*"),

    ("qa", (21, "Kısıtlardan hangisi en çok bağlıyor?")),
    ("p", "Kısıt sayısına göre **B1** (15.154) ve **G** (4.503) en kalabalık olanlar. Ama "
          "gerçekte en çok bağlayan **E1**: 611 uygun bağlantının sunulmamasının başlıca "
          "nedeni yön dengesi. **F** ise mevcut tarifedeki kümelenmeyi dağıtmaya zorluyor."),

    ("qa", (22, "Ödül tablosunun (ranking lookup) mantığını anladınız mı?")),
    ("p", "Evet ve iç tutarlılığını da doğruladık: her N için tam N×N satır var, `İlk Rank > "
          "Rakip Sayısı` olan tutarsız satır yok, sıralamanın kötüleştiği durumlar (10.660 "
          "satır) tabloda tanımlı — yani tablo cezayı da içeriyor."),
    ("p", "Kritik yorum kararımız: sıralama ödülü bir **iyileştirme** ödülü. Tablonun "
          "köşegeni (b == s) \"değişim yok\" nötr referansı. Bu yüzden `b_od`'yi `s` ile "
          "**birebir aynı tabandan** hesapladık; aksi hâlde mevcut tarife hiçbir şey "
          "yapmadan ödül kazanırdı."),

    # ==================================================== C
    ("h2", "C · Çözüm ve çözücü"),

    ("qa", (23, "Neden HiGHS? Gurobi daha hızlı değil mi?")),
    ("p", "Gurobi daha hızlı, doğru. Ama HiGHS'i seçmemizin nedeni hız değil "
          "**doğrulanabilirlik**: HiGHS açık kaynak ve lisans gerektirmiyor. Jüri "
          "`pip install -r requirements.txt` deyip kodu kendi makinesinde koşturabilir. "
          "Gurobi olsaydı lisans anahtarı gerekirdi ve sonuç bağımsız olarak doğrulanamazdı."),
    ("p", "Ayrıca Pyomo kullandığımız için çözücü değiştirmek **tek satır**: "
          "`CFG[\"solver\"]`. Model kodunun hiçbir satırı değişmiyor."),

    ("qa", (24, "`threads = 1` performansı düşürmüyor mu?")),
    ("p", "Evet, düşürüyor — ve bu bilinçli. Çok çekirdekli MIP çözümü **deterministik "
          "değildir**: iş parçacıkları düğümleri farklı sırayla işler, aynı girdiyle farklı "
          "çözümler dönebilir. Yarışma teslimi için \"jüri koştuğunda aynı sayıyı görmeli\" "
          "kısıtını hız kaygısının önüne koyduk (`threads=1`, `random_seed=0`)."),

    ("qa", (25, "Neden haftayı tek seferde çözmediniz?")),
    ("p", "Denedik, olmadı. Tam-hafta modelinde ~100.566 ikili değişken var ve HiGHS makul "
          "sürede **tek bir uygun çözüm bile** bulamıyor. Çözüm bulunamayınca budama yok, "
          "budama yoksa ilerleme yok."),
    ("p", "Çözümümüz iki aşamalı: (1) haftayı günlere böl, her günü ayrı çöz — hızlı ve "
          "garantili; (2) bu çözümü tam-hafta modeline başlangıç noktası ver, çözücü küresel "
          "olarak iyileştirsin."),

    ("qa", (26, "Warm-start nedir, ne kazandırdı?")),
    ("p", "Çözücüye sıfırdan başlamak yerine *\"işte elimde çalışan bir çözüm, buradan "
          "devam et\"* demek. Çözücü onu incumbent kabul edip iyileştirmeye başlıyor."),
    ("tbl", (["", "Değer"],
             [["Aşama-1 (byday)", "3.390.287"],
              ["Aşama-2 (tam-hafta cilalama)", "**3.405.039**"],
              ["Warm-start kazancı", "**+14.752**"],
              ["Ayrıca elde edilen", "**%1,18 global MIP-gap** — optimalite kanıtı"]],
             [7.0, 10.0], 8.8)),
    ("img", ("h4_warmstart_kazanc.png", "Şekil 6.3 — İki aşamalı çözümün katkısı.")),

    ("qa", (27, "MIP-gap %1,18 tam olarak ne anlama geliyor?")),
    ("p", "*\"Bulduğum çözüm, teorik olarak mümkün olan en iyinin en fazla %1,18 altında.\"* "
          "Çözücü hem bir çözüm buluyor hem de bir **üst sınır** kanıtlıyor; gap ikisi "
          "arasındaki bağıl fark."),
    ("box", ("Neden bu, projenin en değerli çıktısı?",
             "Elle yazılmış hiçbir açgözlü algoritma bu cümleyi kuramaz. Greedy bir yöntem "
             "size bir tarife verir ama o tarifenin optimale yakın mı çok mu uzak olduğu "
             "konusunda hiçbir bilgi vermez. Gap, *\"iyi bir çözüm buldum\"* ile "
             "*\"bulduğum çözümün ne kadar iyi olduğunu kanıtlayabiliyorum\"* arasındaki "
             "farktır.", "ok")),

    ("qa", (28, "Daha uzun süre verseniz daha iyi sonuç çıkar mı?")),
    ("p", "Muhtemelen biraz — gap %1,18 olduğu için teorik tavan yaklaşık %1,2 daha "
          "yukarıda. Ama iyileşme giderek yavaşlar (grafikteki yakınsama). Teslim koşusu "
          "1.800 saniye ile sınırlandı; bu, tekrar-üretilebilirlik ve makul koşu süresi "
          "arasındaki denge noktası."),

    ("qa", (29, "Sonuç başka bir makinede aynı çıkar mı?")),
    ("p", "Evet, tasarım gereği: tek iş parçacığı, sabit rasgele tohum, sabit MIP-gap ve "
          "süre sınırları, veriden türetilen (hardcode edilmeyen) gün listesi."),
    ("p", "Tek değişken, süre sınırına takılan koşuların makine hızına bağlı olması — bu "
          "yüzden gap ve süre sınırları raporlarda **açıkça** yazılıyor."),

    ("qa", (30, "Çözücü kaç ihtimali gerçekten inceliyor?")),
    ("p", "Karar uzayı 13⁴⁵⁵³ ≈ 10⁵·⁰⁷². Çözücü bunların hepsini değil, dallanma ağacında "
          "**birkaç bin ile birkaç yüz bin arası düğümü** inceliyor. Geri kalanı doğrusal "
          "gevşeme + budama ile **hiç ziyaret edilmeden** eleniyor."),

    # ==================================================== D
    ("h2", "D · Veri"),

    ("qa", (31, "Veriyi temizlediniz mi? Ne yaptınız?")),
    ("p", "Temizlemedik — **düzelttik**. Politikamız dört ilkeye dayanıyor: orijinale "
          "dokunma, değer uydurma, yalnız fiziksel olarak imkânsız olanı düzelt, her "
          "dönüşümü logla. Yaptığımız her işlem `derived/transform_log.md` içinde."),
    ("bul", ["Excel'in altı farklı süre biçimini tek çeviriciyle dakikaya normalize ettik",
             "24 saat sarmasını çözüp J'yi **kesin** hesapladık (mod-24 çapraz doğrulaması: "
             "57.317 satırda 0 tutarsızlık)",
             "Hafta kaymasını hizaladık (132 satır geri çekildi, 130 kopya olay birleşti)",
             "Birebir özdeş 157 satırı tekilleştirdik",
             "Bacak blok sürelerini çıkardık (5.471 kayıt; çok-değerli 173 grupta ihtiyatlı "
             "olan alındı)",
             "Rakip sürelerini taşıyıcı bazında özetledik (49.467 → 23.975)"]),
    ("p", "**Yapmadıklarımız:** aykırı değer atmadık, eksik değer doldurmadık, "
          "normalizasyon/ölçekleme yapmadık, rakip verisine müdahale etmedik, orijinal "
          "Excel'lere hiç yazmadık."),

    ("qa", (32, "24 saat sarması nedir? Nasıl fark ettiniz?")),
    ("p", "`Gate-to-Gate Uçuş Süresi` sütunu bir **saat hücresi** olarak kaydedilmiş. Saat "
          "hücresi 00:00–23:59 arasıdır; 24 saati aşan bir süreyi gösteremez ve başa sarar. "
          "28 saatlik bir yolculuk \"04:00\" görünür."),
    ("p", "Fark etme yöntemi: sütunun aldığı **en büyük değer 1.435 dakika (23:55)** — "
          "57.317 satırda tek istisna yok. Böyle bir tavan doğal olamaz."),
    ("box", ("Gerçek örnek — EZE→PEK (Buenos Aires → Pekin), TK 16 + 88",
             "Excel diyor: **04:40**. Gerçek: 1. bacak 17 saat + bekleme 2,5 saat + 2. bacak "
             "9 saat = **28,7 saat**. Fark tam 24 saat.\n\n"
             "Bu değeri kullansaydık model \"Buenos Aires'ten Pekin'e 4 saat 40 dakikada "
             "gidiyoruz, herkesi yendik\" derdi.", "warn")),

    ("qa", (33, "ElapsedTime sütunlarına neden güveniyorsunuz?")),
    ("p", "Üç ayrı gerekçeyle:"),
    ("num", ["**Yapısal:** bu sütunlar `'30.12.1899 06:19:00'` biçiminde **metin** olarak "
             "saklanmış — Excel'in 1899 epoch kodlaması. Tarih kısmı 24 saat üstünü "
             "taşıyabildiği için biçimin **tavanı yok**.",
             "**Fiziksel:** tek bir uçuş bacağı zaten 24 saati aşmaz (en uzunu 23 sa 45 dk, "
             "ortanca 2,6 saat). Aşan şey **toplam yolculuk**, ve o zaten farklı bir sütunda.",
             "**Çapraz doğrulama:** `(E1 + bekleme + E2)` ile `Gate-to-Gate` arasındaki fark "
             "tam olarak 24 saatin katı olmalı. **57.317 satırda 0 tutarsızlık.** İki "
             "bağımsız kaynak birbirini tutuyor."]),

    ("qa", (34, "24 saati aşan satırları attınız mı?")),
    ("p", "Hayır, **tek satır bile atılmadı**. 495 uzun yolculuğun (61 THY + 434 rakip) "
          "hepsi doğru J değeriyle modele girdi. Çözümde 61 sunulan bağlantının J'si 24 "
          "saati aşıyor ve bunlar toplam 64 rakip yeniyor — bu galibiyetler gerçek."),

    ("qa", (35, "Eksik veriyi nasıl ele aldınız?")),
    ("p", "İki tür eksik vardı:"),
    ("tbl", (["Eksik", "Kaç", "Politikamız", "Neden"],
             [["ρ (gelir ağırlığı) olmayan pazar", "48",
               "Amaç evreninden **dışla** — ama uçuşları kapasitede saymaya devam et",
               "0 saymak \"değersiz ilan etmek\", ortalama atamak **veri uydurmak** olurdu"],
              ["Rotasyon partneri olmayan uçuş", "176",
               "**Sabit** kabul et, hiç kaydırma",
               "Doğrulayamadığımız bir kısıtı bozma riski almıyoruz"]],
             [4.4, 1.4, 5.6, 5.6], 8.4)),

    ("qa", (36, "Gizli test verisi farklı gelirse kod çalışır mı?")),
    ("p", "Bunun için özel olarak hazırlandı:"),
    ("bul", ["Gün listesi veriden okunuyor, hardcode edilmiyor (`all_operation_days()`)",
             "Dosya adı farklıysa `glob` yedeğiyle aranıyor (`_find_conn_file()`)",
             "Beklenen sütun yoksa **anlaşılır** hata veriyor (`need()`), kriptik `KeyError` "
             "değil",
             "`ElapsedTime` sütunları yoksa eski şemaya (minimal de-wrap) otomatik düşüyor "
             "ve bunu loglara yazıyor",
             "`flight_block_times.csv` yoksa A2 ihtiyatlı moda geçiyor",
             "Tek bir günün çözümü hata verirse o gün atlanıyor, koşu devam ediyor"]),

    # ==================================================== E
    ("h2", "E · Doğrulama ve güvenilirlik"),

    ("qa", (37, "Sonucunuzun doğru olduğunu nasıl biliyoruz?")),
    ("p", "Üç bağımsız kanıtla:"),
    ("num", ["**Bağımsız doğrulayıcı.** `05_validate_solution.py` modelin kodundan tamamen "
             "ayrı — Pyomo import etmiyor, sabitleri kendi dosyasında yeniden yazıyor, "
             "baseline'ı sıfırdan hesaplıyor. 12 kontrolün hepsi PASS.",
             "**Global MIP-gap %1,18.** Çözücü, çözümün optimale ne kadar yakın olduğunu "
             "matematiksel olarak kanıtlıyor.",
             "**Kalite kapısı.** Doğrulayıcı bir tane bile FAIL bulursa çıkış kodu 1 "
             "döndürüyor ve `run_all.py` koşuyu durduruyor. Yani `output/` klasöründe bir "
             "sonuç varsa, o sonuç kesinlikle 12 kontrolden geçmiştir."]),
    ("img", ("f13_cift_kayit.png", "Şekil 6.4 — Çift kayıt: üreten kod ile doğrulayan kod "
                                   "ayrıdır.")),

    ("qa", (38, "Doğrulayıcı gerçekten bir hata yakaladı mı?")),
    ("p", "Evet — ve bu, sunumdaki en önemli hikâyemiz."),
    ("num", ["Pencereyi ±90 dakikaya çıkardık, sonuç **%5,34**'e yükseldi. Cazip bir rakam.",
             "Doğrulayıcı **gerçek bir A2 rotasyon ihlali** yakaladı (uçuş 2200/2201, gün 2).",
             "Kök nedeni bulduk: rotasyon ortağının o günkü olayı ρ'suz bir pazara ait "
             "olduğu için modelde hiç oluşturulmuyordu → A2 kısıtı o gün hiç kurulmuyordu.",
             "**Yüksek rakamı iptal ettik**, ±60'a döndük ve kök nedeni "
             "(`full_role_time` evren-ankoru ile) kalıcı olarak düzelttik."]),
    ("p", "Bu not `05_validate_solution.py`'nin 52–60. satırlarında hâlâ duruyor — silmedik, "
          "çünkü kararın gerekçesi kodun bir parçası."),

    ("qa", (39, "G muafiyetleri bir açık kapı değil mi?")),
    ("p", "Olabilirdi — ama muafiyet listesi **diske yazılıyor** "
          "(`output/g_band_exemptions.csv`, 1.132 kayıt), raporlarda sayısıyla anılıyor ve "
          "doğrulayıcı onu okuyup ayrıca sayıyor."),
    ("p", "Alternatif — muafiyetleri hiç bildirmemek — G'nin nerede uygulanmadığını "
          "**bilinemez** kılardı. Şeffaf gevşetme, gizli gevşetmeden iyidir."),

    ("qa", (40, "\"Artefakt\" dediğiniz A2 ihlalleri gerçek ihlal olabilir mi?")),
    ("p", "Artefakt olarak sayılan turlar, **mevcut yayınlanan tarifenin kendisinin de "
          "sağlamadığı** turlardır — yani o gün o çift zaten tek uçakla dönülmüyor. "
          "Optimizasyon onları yaratmadı, devraldı."),
    ("p", "Kod ikisini asla karıştırmıyor: `a2x_base` (artefakt) ve `a2x_viol` (YENİ ihlal) "
          "ayrı sayılıyor ve **ikisi de** raporlanıyor. YENİ ihlal sayısı 0 olmak zorunda — "
          "ve 0. Ayrıca bu, 08'de bir yeniden yazma bariyeri: yeni ihlal doğarsa çıktı "
          "dosyalarına dokunulmuyor."),

    ("qa", (41, "Baseline'ı nasıl hesapladınız? Kendi lehinize olabilir mi?")),
    ("p", "Baseline **iki kez, iki bağımsız kodla** hesaplanıyor: `03_model.py`'de "
          "`current_baseline()` ve `05_validate_solution.py`'de sıfırdan. İkisi "
          "uyuşmuyorsa doğrulama FAIL veriyor."),
    ("p", "Ayrıca `b_od` tanımını özellikle baseline'ı **şişirmeyecek** şekilde kurduk: "
          "mevcut tarife ödül tablosunun köşegenine (nötr referans) oturuyor. Eski kural "
          "kullanılsaydı baseline pazarların ~%29'unda hak etmediği ödülü alır ve "
          "iyileşmemiz **olduğundan büyük** görünürdü. Yani hatayı kendi aleyhimize "
          "düzelttik."),

    ("qa", (42, "Fazla-beyan ve eksik-beyan neden farklı muamele görüyor?")),
    ("p", "**Fazla-beyan** (dosyada yazandan az rakip gerçekten yenilmiş) amaç değerini "
          "şişirir → gerçek hata, FAIL. **Eksik-beyan** (gerçekte yenilmiş ama gösterge "
          "bağlanmamış) amaç değerini olduğundan küçük gösterir → hata değil, ihtiyatlılık, "
          "sadece not edilir."),
    ("p", "Bu asimetri bilinçli: **kendi lehimize olan sapmalar hata sayılıyor, aleyhimize "
          "olanlar sayılmıyor.** Ölçüm kendine karşı kurulmuş."),

    # ==================================================== F
    ("h2", "F · Sonuç, özgünlük ve eleştiri"),

    ("qa", (43, "%4,72 anlamlı bir kazanç mı?")),
    ("p", "Evet, üç nedenle:"),
    ("bul", ["**Gelir-ağırlıklı.** Bu bir uçuş sayısı yüzdesi değil; her pazarın gelir "
             "potansiyeliyle çarpılmış bir rekabetçilik ölçüsü. Büyük pazarlardaki "
             "iyileşme daha ağır basıyor.",
             "**Çok düşük maliyetle elde edildi.** Uçuşların yalnız %23'ü, ortalama 19 "
             "dakika kaydırıldı. %77'si hiç kımıldamadı. Yeni uçak, yeni sefer, ek yatırım "
             "gerekmiyor.",
             "**Kanıtlı.** Global gap %1,18 — yani mümkün olan en iyi bile bizden en fazla "
             "%1,2 daha iyi. Masada bırakılan çok az şey var."]),
    ("p", "Somut sonuçlar: 660 pazar-günde sıralama yükseldi, 4.914 rakip yenildi, 6.966 "
          "bağlantı sunuldu."),

    ("qa", (44, "Çözücüyü kullandınız — sizin katkınız ne?")),
    ("p", "Çözücü, sorduğunuz sorunun cevabını verir. **Bütün maharet doğru soruyu "
          "sormaktır.** Yanlış formüle etseydik çözücü bize yanlış sorunun kusursuz optimal "
          "cevabını verirdi — ve bunu fark etmenin hiçbir yolu olmazdı."),
    ("img", ("h1_katki_haritasi.png", "Şekil 6.5 — Beş adımın dördü bizim tasarımımız.")),
    ("p", "Katkımız beş başlıkta: **formülasyon kararları** (olay soyutlaması, one-hot "
          "kodlama, sıkı big-M, üç yollu değişken elemesi, b_od türetimi), **çözüm "
          "stratejisi** (iki aşamalı matheuristik, gece-aşan koruma, G zincirlemesi), "
          "**veri mühendisliği** (kesin J, hafta normalizasyonu, evren-eksiği düzeltmeleri), "
          "**bağımsız doğrulama** ve **dürüst raporlama**."),
    ("p", "En güçlü kanıt Bölüm 3'teki \"yapmasaydık ne olurdu\" tablosu: her satır ölçülmüş "
          "bir tasarım kararı ve hiçbiri çözücüden gelmiyor."),

    ("qa", (45, "Bu teknikler standart değil mi? Neyi siz buldunuz?")),
    ("p", "Dürüst cevap: **teknikler standart, uygulaması bize ait.** Big-M, one-hot "
          "kodlama, azalan getiri, warm-start — hepsi bilinen yöneylem araştırması "
          "araçları. HiGHS'in algoritması ve Pyomo da bizim değil."),
    ("p", "Bizim kattığımız, bu araçların **bu probleme nasıl uygulanacağına** dair tasarım "
          "kararları: karar biriminin ne olacağı, hangi değişkenin hiç yaratılmayacağı, "
          "M'lerin nasıl sıkılaştırılacağı, çözülemeyen modelin nasıl ikiye bölüneceği, "
          "gün ayrıştırmasının gece-aşan turları nasıl bozmayacağı ve sonucun nasıl "
          "bağımsız doğrulanacağı."),
    ("box", ("Kapanış cümlesi",
             "*\"Biz bir yapay zekâ modeli eğitmedik — bu bir tahmin değil, karar problemi. "
             "Yaptığımız şey brief'teki iş problemini 100.566 ikili değişkenli bir "
             "matematiksel modele çevirmekti; karar biriminden ödül yapısına, big-M "
             "sıkılığından kısıt formülasyonuna kadar her tasarım kararı bize ait. Çözücü "
             "bu modeli çözen motor — ama sorduğumuz soru yanlış olsaydı bize yanlış sorunun "
             "kusursuz cevabını verirdi. Doğru sorduğumuzun kanıtı üç yerde: modelden "
             "tamamen bağımsız yazdığımız doğrulayıcı 12 kontrolün hepsini geçiyor, çözücü "
             "%1,18'lik global optimalite boşluğunu kanıtlıyor, ve daha yüksek sonuç veren "
             "bir denememizi kendi doğrulayıcımız ihlal yakaladığı için iptal ettik.\"*",
             "ok")),
]
