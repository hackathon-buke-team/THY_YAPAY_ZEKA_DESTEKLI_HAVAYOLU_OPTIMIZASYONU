# -*- coding: utf-8 -*-
"""Dokuman 2 — Ek B: iki konunun adim adim anlatimi."""

ITEMS = [
    ("h1", ("B", "Ek B — İki konunun adım adım anlatımı")),
    ("p", "Bu ek, dokümandaki iki sayının *nereden geldiğini* sıfırdan, hiçbir ön bilgi "
          "varsaymadan anlatır."),

    # ============================================================ B1
    ("h2", "B.1  \"823 uçuş olayı neden kımıldatılamıyor?\""),

    ("h3", "Önce: \"uçuş olayı\" ne demek?"),
    ("p", "Bir uçuş, IST'te ya **iner** ya **kalkar**. Bizim için karar birimi \"uçuş\" değil, "
          "**uçuşun IST'teki tek bir hareketidir**. Buna *olay* diyoruz. Bir olayın kimliği "
          "üç şeyden oluşur:"),
    ("bul", ["hangi uçuş numarası (örn. 88)",
             "hangi rol (IST'e **varış** mı, IST'ten **kalkış** mı)",
             "hangi gün (1–7)"]),
    ("p", "Modelde toplam **5.376 olay** var. Sorumuz şu: bunlardan 823'ünün saati neden "
          "değiştirilemiyor?"),

    ("h3", "Cevap: uçak fiziksel bir nesnedir ve bir yere gidip geri dönmek zorundadır"),
    ("img", ("g10_sabit_ucus.png",
             "Şekil B.1 — Rotasyon partneri bilinen bir uçuş oynatılabilir; bilinmeyen "
             "oynatılamaz.")),
    ("p", "Bir uçak IST'ten kalkar, bir yere gider, orada bir süre bekler ve **aynı uçak** "
          "geri döner. Bu turun süresi en az şu kadar olmalıdır:"),
    ("box", ("Dönüş varışı  −  Gidiş kalkışı   ≥   T_OB  +  τ  +  T_IB",
             "**T_OB** — gidiş bacağının uçuş süresi\n"
             "**τ (tau)** — hedef havalimanında yerde geçen minimum süre (45 dk: yolcu "
             "indirme/bindirme, yakıt, temizlik)\n"
             "**T_IB** — dönüş bacağının uçuş süresi\n\n"
             "Bu, modeldeki **A2 kısıtıdır**. Bunu sağlamayan bir tarife kâğıt üstünde "
             "vardır ama gerçekte uçurulamaz — uçak orada olmaz.")),

    ("h3", "Somut örnek — kımıldayabilen uçuş"),
    ("p", "`Flight Pairs.xlsx` dosyasında şu satırlar var:"),
    ("tbl", (["FlNo", "Orig", "Dest", "Pair"],
             [["88", "IST", "PEK", "88-89"],
              ["89", "PEK", "IST", "88-89"]],
             [2.6, 2.6, 2.6, 3.0], 9.0)),
    ("p", "Aynı `Pair` etiketi şunu söylüyor: **88 numaralı uçuşu yapan uçak, 89 numaralı "
          "uçuşla geri dönüyor.** Dolayısıyla 88'in kalkışını 20 dakika geciktirmek "
          "istediğimde, 89'un varışının hâlâ yetişip yetişmediğini **hesaplayabilirim**. "
          "Model bu kısıtı kurar, çözücü ona uyar. Bu uçuş **ayarlanabilir**."),

    ("h3", "Somut örnek — kımıldayamayan uçuş"),
    ("p", "Bağlantı tablosunda **112** numaralı bir TK uçuşu var (JFK → IST, gün 1'de 23:25'te "
          "iniyor). Ama `Flight Pairs.xlsx` dosyasında **112 numaralı uçuş hiç geçmiyor**. "
          "Yani elimizde şu bilgi yok:"),
    ("bul", ["Bu uçuşu hangi uçak yapıyor?",
             "O uçak IST'e indikten sonra hangi uçuşa gidiyor?",
             "Varışını 20 dakika geciktirirsem, o uçak bir sonraki uçuşuna yetişebilir mi?"]),
    ("box", ("Bilmediğimiz bir kısıtı bozma riski almıyoruz",
             "112'yi yine de kaydırabilirdik — puan biraz artardı. Ama sonuçta **fiziksel "
             "olarak uygulanamayan** bir tarife üretmiş olabilirdik ve bunu fark etmemizin "
             "hiçbir yolu olmazdı, çünkü kontrol edecek veri yok.\n\n"
             "Proje bunun yerine ihtiyatlı yolu seçiyor: *doğrulayamadığın şeye dokunma.* "
             "Bu uçuşlar mevcut saatlerinde bırakılıyor ve model onları sadece \"orada duran "
             "sabit uçuşlar\" olarak görüyor — IST kapasitesinde yer kaplıyorlar ama karar "
             "değişkeni olmuyorlar.", "ok")),

    ("h3", "Kaç tane, ve nereden 823 çıkıyor?"),
    ("tbl", (["Adım", "Sayı", "Açıklama"],
             [["Bağlantı tablosundaki TK uçuş numarası", "**952**", "Toplam farklı uçuş no"],
              ["Flight Pairs'te karşılığı olan", "776", "Rotasyon eşi biliniyor → ayarlanabilir"],
              ["Flight Pairs'te **olmayan**", "**176**", "Rotasyon eşi yok → sabit"],
              ["Bunların amaç evreninde görüneni", "172", "4'ü yalnız ρ'suz pazarlarda uçuyor"],
              ["Uçuş numarası başına ortalama olay", "4,78", "7 günün bir kısmında, tek rolde"],
              ["**Toplam sabit olay**", "**823**", "172 × 4,78 ≈ 823"],
              ["Toplam olay", "5.376", "Sabitlerin payı: **%15,3**"]],
             [7.0, 2.2, 7.8], 8.8)),

    ("h3", "Bunun kodda karşılığı"),
    ("code", ("02_data_prep.py", 288, 295, "listenin üretilmesi")),
    ("p", "`02_data_prep.py` bu 176 uçuş numarasını bulup "
          "`derived/tk_flights_without_partner.csv` dosyasına yazar."),
    ("code", ("03_model.py", 236, 247, "listenin uygulanması")),
    ("p", "`03_model.py` bu listeyi okur. **Satır 240** kararı verir: uçuş numarası listede "
          "varsa `adj = False`. **Satır 244** sonucu uygular: ayarlanamaz olayın aday "
          "listesi `cands = [cur]` olur — yani tek seçenek, mevcut saatin kendisi. Çözücü "
          "başka bir değer seçemez çünkü seçecek başka değer yoktur."),

    ("h3", "Bunun bedeli ne?"),
    ("p", "Dürüst cevap: **puan kaybı**. Bu 823 olay serbest bırakılsaydı model daha iyi bir "
          "sonuç bulurdu. Arama uzayı da 13⁸²³ = 10⁹¹⁷ kat büyürdü. Yani burada bilinçli bir "
          "takas var: *daha yüksek puan* yerine *uygulanabilirliği kanıtlanmış tarife*. "
          "Organizatör eksik rotasyon verisini sağlarsa bu 823 olay tek satır değişiklikle "
          "serbest bırakılabilir."),

    # ============================================================ B2
    ("h2", "B.2  Huni figürü (Şekil 2.1) tam olarak neyi gösteriyor?"),
    ("p", "Bu figür **tek bir hikâyeyi** anlatır: elimize gelen ham veri, adım adım "
          "süzülerek sonunda \"yolcuya satılabilir bağlantı\" listesine dönüşüyor. Her "
          "çubuk bir öncekinin **alt kümesidir** — yani her satır, üstündeki satırın "
          "içinden çıkar."),
    ("img", ("g2_veri_hunisi.png",
             "Şekil B.2 — Huninin düzeltilmiş hâli: üstteki şerit girdi dosyalarının "
             "dağılımını, alttaki çubuklar ise gerçek süzülmeyi gösteriyor.")),

    ("h3", "Üstteki şerit: 89.094 satır neyin toplamı?"),
    ("p", "Burada **dikkat edilmesi gereken bir ayrım** var. 89.094, dört Excel dosyasının "
          "satır toplamıdır ve bunların hepsi \"bağlantı\" değildir:"),
    ("tbl", (["Dosya", "Satır", "Bu satırlar ne?", "Huniye girer mi?"],
             [["`O&D Rakip Bağlantı Tablosu`", "**57.317**",
               "Her satır bir aktarmalı yolculuk seçeneği", "**EVET** — huninin girdisi"],
              ["`change_ranking_input.xlsx`", "22.140",
               "Ödül tablosu: (N rakip, b sıra, s sıra) → puan", "Hayır — **başvuru tablosu**"],
              ["`Yolcu Verisi_masked.xlsx`", "8.075",
               "Pazar → gelir ağırlığı ρ", "Hayır — **çarpan tablosu**"],
              ["`Flight Pairs.xlsx`", "1.562",
               "Uçuş no → rotasyon eşi", "Hayır — **kısıt verisi**"]],
             [4.6, 1.8, 6.0, 4.6], 8.4)),
    ("box", ("Yani 89.094 → 57.317 bir \"eleme\" DEĞİLDİR",
             "Diğer 31.777 satır atılmıyor — modelde sonuna kadar kullanılıyorlar; sadece "
             "*bağlantı adayı* değiller. Ödül tablosu puan hesabında, ρ tablosu amaç "
             "fonksiyonunda, Flight Pairs ise A2 rotasyon kısıtında iş görür. Figürün ilk "
             "şeridi bu yüzden **eleme oku değil, dağılım şeridi** olarak çizilmiştir.",
             "warn")),

    ("h3", "Çubuk 1 — 57.317: bağlantı tablosunun tamamı"),
    ("p", "Bu tablonun her satırı şu bilgiyi taşır: *\"Şu havayolu, şu günde, şu gelen uçuşla "
          "IST'e geliyor; şu giden uçuşla şu şehre devam ediyor.\"* Yani bir satır = **bir "
          "yolculuk seçeneği**. 57.317 satır, 88 farklı havayolunun 1.408 pazardaki 7 günlük "
          "tüm aktarma seçenekleridir."),

    ("h3", "Çubuk 2 — 7.850: bunun THY'ye ait olanı"),
    ("p", "`Cr1` sütunu \"TK\" olan satırlar. Kalan **49.467 satır rakiplerindir.** Onları "
          "**değiştiremeyiz** — rakip havayolunun tarifesine müdahale edemeyiz. Ama onlar "
          "kaybolmaz: her rakibin o pazardaki **en iyi yolculuk süresi** (T_comp) hesaplanır "
          "ve bizim kıyas ölçümüz olur. \"Rakip yendik mi?\" sorusu tam olarak bununla "
          "cevaplanır."),

    ("h3", "Çubuk 3 — 7.693: 157 özdeş kopya atıldı"),
    ("p", "Veride şöyle bir tuhaflık var: **aynı operasyon günü** (\"Gün 1\") farklı "
          "pazarlarda farklı takvim tarihlerine yazılmış. Bir satırda 4 Ağustos Pazartesi, "
          "başka satırda 11 Ağustos Pazartesi. İkisi de \"Gün 1\"dir ve aynı fiziksel uçuşu "
          "anlatır — sadece bir hafta kaymış görünür."),
    ("p", "`02_data_prep.py` bunları hizalar (kaymış olanları 7 gün geri çeker). Hizalama "
          "sonrası **157 satır**, başka bir satırın **birebir aynısı** hâline gelir: aynı "
          "pazar, aynı gün, aynı iki uçuş numarası, aynı iki saat."),
    ("box", ("Neden atmak zorundayız?",
             "Aynı ürünü iki kez saymak, aktarma ödülünü **iki kez** yazdırır. Bu hem mevcut "
             "tarifenin (baseline) puanını hem de optimize sonucun puanını şişirir — yani "
             "elde ettiğimiz \"iyileşme\" sahte olur. Dikkat: **yalnız tüm alanları özdeş** "
             "olanlar atılır; saati gerçekten farklı olan satırlar korunur, çünkü onlar "
             "gerçekten farklı uçuşlardır.", "info")),

    ("h3", "Çubuk 4 — 7.577: 116 bağlantı amaç evreninden çıktı"),
    ("p", "Amaç fonksiyonu şöyle: **ρ × (aktarma ödülü + sıralama ödülü)**. Buradaki ρ, "
          "pazarın gelir ağırlığıdır ve `Yolcu Verisi` dosyasından gelir. Ama bağlantı "
          "tablosundaki **48 pazarın** bu dosyada karşılığı yok — ρ'ları bilinmiyor."),
    ("p", "Üç seçenek vardı:"),
    ("tbl", (["Seçenek", "Ne olurdu?", "Karar"],
             [["ρ = 0 varsay", "O pazarları \"değersiz\" ilan etmek olurdu", "Reddedildi"],
              ["ρ = ortalama varsay", "**Veri uydurmak** olurdu", "Reddedildi"],
              ["Amaç evreninden çıkar",
               "Puanlamaya girmezler; ama uçuşları IST kapasitesinde sayılmaya devam eder",
               "**Seçildi**"]],
             [3.4, 8.6, 5.0], 8.6)),
    ("box", ("Kritik nokta: puanlamadan çıktılar, FİZİKTEN çıkmadılar",
             "Bu 48 pazarın uçakları hâlâ havada ve hâlâ IST pistini kullanıyor. Onları "
             "kapasite hesabından da çıkarsaydık, gerçekte olmayan bir boşluk yaratır ve "
             "model oraya uçuş yerleştirirdi. Kod bunu `extra_use` mekanizmasıyla önler: "
             "bu uçuşlar **karar değişkeni olmadan, sabit doluluk olarak** kova sayacına "
             "eklenir (79 kova etkileniyor).", "ok")),

    ("h3", "Çubuk 5 — 6.966: modelin sunmayı SEÇTİĞİ bağlantılar"),
    ("p", "Buraya kadar olan tüm daralmalar **veriyle** ilgiliydi. Bu son adım farklıdır: "
          "burası **modelin kararıdır** (bu yüzden çubuk yeşil). 7.577 adaydan 611'i "
          "sunulmadı. İki nedeni var:"),
    ("num", ["**Pencereye sokulamıyor.** Bağlantının boşluğu 60–300 dakika aralığına ancak "
             "±60 dakikalık kaydırmalarla girebilir. Bazı bağlantılarda gelen ve giden uçuş "
             "arasındaki mesafe o kadar büyük ki, iki uçuşu da sonuna kadar kaydırsanız bile "
             "pencereye giremiyor.",
             "**E1 yön dengesi için bilinçli olarak sunulmuyor.** Model, bir pazarın gidiş "
             "ve dönüş yönlerinin bağlantı sayılarını dengeli tutmak zorunda "
             "(|n_od − n_do| ≤ 0,20 × toplam). Bir yönde 20, ters yönde 8 bağlantı varsa, "
             "20'nin hepsini sunmak dengeyi bozar — model bilerek bir kısmını sunmaz."]),
    ("box", ("İkinci neden ilk bakışta garip gelir: \"neden kârlı bir şeyi sunmuyorsun?\"",
             "Çünkü tek yönü şişirip dönüşü ihmal eden bir tarife kâğıt üstünde puan kazanır "
             "ama **gerçekte satılabilir bir ürün değildir**. Yolcu gidiş-dönüş ister. "
             "E1 kısıtı bu gerçekliği modele sokar. (Bu ayrıntı `08_fullweek_polish.py`'de "
             "de kritiktir: warm-start'ta hangi bağlantıların sunulduğu **uygunluktan "
             "türetilemez**, byday'in gerçek kararından okunmalıdır.)", "info")),

    ("h3", "Huninin özeti — tek cümlede her satır"),
    ("tbl", (["Satır", "Sayı", "Tek cümlede"],
             [["Ham girdi", "89.094",
               "Dört Excel dosyasının toplam satırı (hepsi bağlantı değil)"],
              ["Bağlantı tablosu", "57.317", "Tüm havayollarının IST aktarma seçenekleri"],
              ["THY bağlantısı", "7.850", "Bunun bize ait olanı — geri kalanı rakip"],
              ["Tekilleştirilmiş", "7.693", "Aynı ürünü iki kez saymamak için 157 kopya atıldı"],
              ["Modele giren", "7.577", "Gelir ağırlığı bilinen pazarların bağlantıları"],
              ["Sunulan", "**6.966**",
               "Modelin, tüm kısıtları sağlayarak sunmayı seçtiği bağlantılar"]],
             [3.6, 2.0, 11.0], 8.8)),
    ("p", "Ve nihayetinde optimizasyonun ölçtüğü şey bu son satırdır: bu 6.966 bağlantının "
          "toplam yolculuk süreleri, rakiplerinkinden ne kadar iyi ve bu pazarlar THY için "
          "ne kadar değerli."),
]
