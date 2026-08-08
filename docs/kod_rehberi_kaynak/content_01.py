# -*- coding: utf-8 -*-
"""Bolum 1 — 01_data_health_check.py"""

F = "01_data_health_check.py"

ITEMS = [
    ("h1", ("1", "01_data_health_check.py — Veri Sağlık Kontrolü")),

    ("box", ("Bu dosya ne yapar?",
             "Dört girdi Excel'ini okur ve **hiçbirini değiştirmeden** \"bu veriyle "
             "modelleme yapılabilir mi?\" sorusunu yanıtlar. Kaç satır var, hangi sütunlar "
             "eksik, saatler tutarlı mı, kaç bağlantı zaten uygun pencerede, hangi pazarların "
             "gelir ağırlığı yok — hepsini ekrana basar ve `reports/data_health_report.md` "
             "dosyasına yazar. **Tek bir karar üretmez; sadece teşhis koyar.**")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`data/` — 4 Excel dosyası (salt-okunur)"],
              ["Çıktı", "`reports/data_health_report.md`"],
              ["Çalıştırma", "`python src/01_data_health_check.py` (proje kökünden)"],
              ["Bağımlılık", "yalnız `pandas`"],
              ["Süre", "birkaç saniye"]],
             [3.0, 14.0], 9.0)),
    ("p", "Neden ilk adım bu? Çünkü **bir optimizasyon modelinin en tehlikeli hatası, sessiz "
          "veri hatasıdır.** Model çalışır, sayı üretir, ama üretilen sayı yanlış varsayıma "
          "dayanır. Bu dosya o varsayımları koşmadan önce açığa çıkarır."),

    ("h2", "1.1  Modül başlığı ve kurulum"),
    ("code", (F, 1, 20, "docstring + import'lar")),
    ("p", "Üstteki üç tırnaklı metin **modül docstring'idir**: dosyanın ne yaptığını, nasıl "
          "çalıştırıldığını, girdi ve çıktısını tek bakışta verir. Bu projedeki her dosya bu "
          "kalıbı izler — jüri veya yeni bir geliştirici dosyayı açtığında ilk 10 satırda "
          "bağlamı alır."),
    ("bul", ["`warnings.filterwarnings(\"ignore\")` — openpyxl'in Excel biçim uyarıları raporu "
             "kirletmesin diye susturulur. Rapor okunabilirliği önemlidir.",
             "`pd.set_option(\"display.width\", 200)` ve `max_columns 60` — pandas'ın geniş "
             "tabloları `...` ile kırpmasını engeller; sağlık raporunda tüm sütun adlarını "
             "görmek isteriz."]),

    ("h2", "1.2  Yol sabitleri — \"proje kökü neresi?\" problemi"),
    ("code", (F, 22, 27, "yolların dosyanın konumundan türetilmesi")),
    ("p", "Bu üç satır küçük görünür ama projenin **her yerden çalışabilmesini** sağlar:"),
    ("num", ["`__file__` bu dosyanın yolu; `os.path.abspath` onu mutlak yola çevirir.",
             "`os.path.dirname(...)` → `HERE` = `.../Buke_cozum/src`",
             "Bir kez daha `dirname` → `ROOT` = `.../Buke_cozum` (proje kökü)."]),
    ("box", ("Neden `os.getcwd()` kullanılmadı?",
             "Çünkü çalışma dizini, betiği nereden çağırdığınıza göre değişir. `__file__` "
             "tabanlı türetme ile betik **hangi klasörden çağrılırsa çağrılsın** doğru "
             "`data/` ve `reports/` klasörlerini bulur. `os.makedirs(REPORT_DIR, "
             "exist_ok=True)` da klasör yoksa oluşturur, varsa hata vermez.", "ok")),

    ("h2", "1.3  `_find_conn_file()` — hangi bağlantı tablosunu kullanacağız?"),
    ("code", (F, 29, 40, "dayanıklı dosya bulma")),
    ("p", "Yarışma sürecinde bağlantı tablosunun **iki sürümü** dolaştı: orijinal ve "
          "`_updated` (bacak sürelerini, yani `ElapsedTime1/2` sütunlarını içeren) sürüm. "
          "Güncellenmiş sürüm çok daha değerlidir — nedeni 2. bölümde açıklanacak — bu yüzden "
          "fonksiyon **öncelik sırasıyla** arar:"),
    ("num", ["Önce `..._updated.xlsx` var mı? Varsa onu döndür.",
             "Yoksa orijinal `O&D Rakip Bağlantı Tablosu.xlsx`'i dene.",
             "O da yoksa `glob` ile `O&D*.xlsx` kalıbına uyan **her şeyi** ara, "
             "alfabetik ilkini al.",
             "Hiçbiri yoksa `FileNotFoundError` fırlat — sessizce devam etme."]),
    ("box", ("Bu neden önemli?",
             "Gizli test verisi farklı bir dosya adıyla gelebilir. `glob` yedeği sayesinde "
             "kod, adı tam bilmediği bir dosyayı da bulabilir; bulamazsa **açık ve okunabilir "
             "bir hatayla** durur. Sessiz çökme yerine anlaşılır hata — bu proje boyunca "
             "tekrar eden bir tasarım ilkesidir.", "ok")),
    ("code", (F, 42, 47, "dosya sabitleri ve bağlantı penceresi")),
    ("p", "`L_MIN, U_MIN = 60, 300` — brief'in verdiği bağlantı penceresi. Bir yolcunun IST'te "
          "en az 60, en çok 300 dakika beklemesi gerekir. Bu iki sayı projedeki en sık "
          "kullanılan sabitlerdir ve **her dosyada yeniden tanımlanır** (05 doğrulayıcısında "
          "bile) — çünkü modülleri birbirinden bağımsız tutmak, doğrulamanın da bağımsız "
          "olmasını sağlar."),

    ("h2", "1.4  Rapor tamponu: `out`, `h1`, `h2`"),
    ("code", (F, 49, 56, "hem ekrana bas hem dosyaya biriktir")),
    ("p", "Basit ama etkili bir hile: `out()` fonksiyonu aldığı her şeyi metne çevirir, "
          "**hem `print` eder hem de `_buf` listesine ekler**. Böylece betiğin sonunda "
          "`_buf`'ı dosyaya yazmak yeterlidir — ekranda gördüğünüz rapor ile dosyadaki rapor "
          "**birebir aynıdır**. `h1` ve `h2` ise `=` ve `-` karakterlerinden başlık çizgileri "
          "üretir; düz metin raporda görsel hiyerarşi böyle kurulur."),

    ("h2", "1.5  `time_to_min()` — Excel'in saat kâbusu"),
    ("code", (F, 59, 67, "saat/süre → dakika")),
    ("p", "Excel bir hücredeki \"06:19\" değerini duruma göre **saat-of-day** (`datetime.time`) "
          "ya da **süre** (`timedelta`) olarak verir. Bu fonksiyon ikisini de dakikaya çevirir; "
          "tanımadığı bir şey gelirse `None` döndürür (sessizce sıfır varsaymaz)."),
    ("box", ("İleride büyüyecek bir sorunun ilk işareti",
             "`dt.time` için formül `saat*60 + dakika`'dır — yani **24 saati aşan bir süre bu "
             "biçimde temsil edilemez**. 30 saatlik bir yolculuk Excel'de \"06:00\" olarak "
             "görünür. Bu dosya sorunu sadece *tespit eder*; gerçek çözüm "
             "`02_data_prep.py`'nin `dur_min()` fonksiyonundadır.", "warn")),

    ("h2", "1.6  `main()` — dört dosyayı oku"),
    ("code", (F, 70, 77, "raporun açılışı ve okuma")),
    ("p", "`sheet_name=0` her dosyanın **ilk sayfasını** alır. Dosya adları değişebilir ama "
          "veri hep ilk sayfadadır. Bu noktadan sonra dört DataFrame elimizdedir: `conn` "
          "(bağlantı tablosu), `pax` (yolcu/gelir ağırlıkları), `rank` (sıralama ödül "
          "tablosu), `pair` (uçak rotasyon eşleri)."),

    ("h2", "1.7  Bölüm 1 — Bağlantı tablosunun anatomisi"),
    ("code", (F, 79, 92, "boyut, sütunlar, ElapsedTime var mı?")),
    ("p", "Buradaki en kritik satır **83–85**'tir:"),
    ("box", ("`ElapsedTime1/2` neden \"J kesin hesaplanabilir\" demek?",
             "Bu iki sütun varsa her bacağın uçuş süresi doğrudan bilinir ve "
             "**J = E1 + boşluk + E2** olarak *hesaplanır*. Yoksa J'yi yalnız `Gate-to-Gate` "
             "sütunundan okumak zorunda kalırız — o sütun ise 24 saatte sarabildiği için "
             "belirsizdir. Rapor bu durumu tek satırda \"EVET → J kesin\" / \"HAYIR → wrap "
             "riski\" olarak bildirir.", "info")),
    ("p", "`ML2` sütunu varsa taşıyıcı tipi dağılımı (M = Mainline / L = Low-cost) da yazılır. "
          "Brief'in sıralama tanımı taşıyıcı tipi ayrımı yapmadığı için bu bilgi modele "
          "girmez, sadece raporlanır."),
    ("code", (F, 94, 103, "taşıyıcı dağılımı ve TK/rakip ayrımı")),
    ("p", "`conn[\"Cr1\"] == \"TK\"` maskesi tabloyu ikiye böler: **TK satırları** (bizim "
          "optimize edeceğimiz bağlantılar) ve **rakip satırları** (kıyaslayacağımız "
          "referanslar). Bu ayrım kodun tamamında `is_tk` adıyla yaşar."),
    ("code", (F, 105, 117, "tutarlılık ve pazar kapsamı kontrolleri")),
    ("bul", ["**105–107:** `O&D` sütunu gerçekten `Dep1-Arr2` mi? Uyuşmayan satır sayısı 0 "
             "olmalı — değilse pazar anahtarına güvenilemez.",
             "**109–110:** Kaç benzersiz pazar, kaç benzersiz (pazar, gün) çifti var? Bu "
             "sayılar modelin **büyüklüğünü** belirler.",
             "**112–117:** Üç kümenin karşılaştırması: TK'nın bağlantısı olan pazarlar, hiç "
             "TK bağlantısı olmayanlar (buralarda yapabileceğimiz bir şey yok), rakibi "
             "olmayanlar (buralarda sıralama terimi tanımsızdır)."]),

    ("h2", "1.8  Bölüm 2 — Mevcut tarifedeki bağlantılar gerçekten geçerli mi?"),
    ("code", (F, 119, 134, "boşluk hesabı ve pencere kontrolü")),
    ("p", "Üç türetme, üç satırda:"),
    ("num", ["`gap_min` = kalkış − varış (dakika). Yolcunun IST'te beklediği süre.",
             "`j_min` = Gate-to-Gate süresi (dakikaya çevrilmiş). Toplam yolculuk.",
             "`legsum_min` = J − boşluk. Yani **iki bacağın uçuş süreleri toplamı** — model "
             "boyunca sabit kalacak büyüklük."]),
    ("p", "Ardından gelen istatistikler doğrudan projenin **iyileştirme potansiyelini** "
          "gösterir: kaç bağlantı zaten [60, 300] penceresinde? Kaçı çok kısa, kaçı çok uzun? "
          "**Negatif boşluk sayısı** ise saf bir veri hatası sinyalidir (kalkış varıştan önce "
          "olamaz)."),
    ("code", (F, 136, 152, "24 saat sarması ve bacak ayrıştırma fizibilitesi")),
    ("p", "**140–142** satırları az önce bahsedilen tuzağı sayar: J ≥ 24 saat olan kaç satır "
          "var? Eğer `time` biçiminde tutuluyorsa bunlar **kırpılmıştır** ve uzun pazarların "
          "J değeri olduğundan çok küçük görünür — yani model, olmayan bir üstünlüğü ödüllendirir."),
    ("p", "**144–152** ise ileriye dönük bir fizibilite testidir: aynı `(FlNo1, Gün)` çifti "
          "için birden fazla farklı varış saati var mı? Olmamalı — bir uçuşun bir gündeki "
          "IST varışı tektir. Bu sayı 0 değilse, aynı fiziksel uçuş modelde birden çok karar "
          "olayına bölünür ve tutarsız kaydırma alabilir. (02 bunu **hafta normalizasyonu** "
          "ile çözer.)"),

    ("h2", "1.9  Bölüm 3 — Rakipler"),
    ("code", (F, 154, 170, "N_od tanımı ve rakip süreleri")),
    ("p", "Buradaki soru masumca görünür ama **ödül tablosunu doğrudan etkiler**: bir pazarda "
          "\"kaç rakip var\" derken neyi sayıyoruz?"),
    ("tbl", (["Tanım", "Ne sayar?", "Sonuç"],
             [["itinerary bazlı", "Rakiplerin sunduğu **her bağlantı seçeneğini**",
               "Sayı 40'ı aşabilir → ödül tablosunun dışına çıkar"],
              ["**taşıyıcı bazlı**", "Farklı **havayolu şirketi** sayısını",
               "Veride en fazla 17 → ödül tablosu (max N = 40) **tam kapsar** ✔"]],
             [3.2, 6.4, 7.4], 8.8)),
    ("p", "Satır 168–170 bu iki tanımı sayısal olarak karşılaştırır ve `change_ranking_input"
          ".xlsx`'in kapsadığı N aralığını yazar. 02_data_prep bu bulguya dayanarak "
          "`n_od_def = \"carrier\"` seçer."),

    ("h2", "1.10  Bölüm 4 — Gelir ağırlığı ρ"),
    ("code", (F, 172, 184, "ρ kapsamı ve eksikler")),
    ("p", "`OD importance factor`, bir pazarın THY için ne kadar değerli olduğunu söyler — "
          "amaç fonksiyonundaki **çarpandır**. Bu blok iki şeyi ölçer: ρ değerleri hangi "
          "aralıkta ve **bağlantı tablosundaki kaç pazarın ρ'su yok?**"),
    ("box", ("ρ'su olmayan pazar ne anlama gelir?",
             "Amaç fonksiyonu ρ ile çarpıldığı için, ρ'su olmayan bir pazar için \"bu "
             "iyileştirme ne kadar değerli?\" sorusunun cevabı yoktur. 0 varsaymak o pazarı "
             "önemsiz saymak, ortalama atamak ise **veri uydurmak** olur. Proje "
             "üçüncü yolu seçer: bu pazarları amaç evreninden **dışlar** ama uçuşlarını hub "
             "kapasitesinde (F kısıtı) saymaya devam eder. Bu ayrım 03'te `extra_use` "
             "mekanizmasıyla hayata geçer.", "info")),

    ("h2", "1.11  Bölüm 5 — Sıralama ödül tablosu"),
    ("code", (F, 186, 197, "lookup tablosunun iç tutarlılığı")),
    ("p", "`change_ranking_input.xlsx` şu soruya yanıt verir: *\"N rakip varken b. sıradan "
          "s. sıraya çıkarsam kaç puan kazanırım?\"* Blok üç şeyi doğrular:"),
    ("bul", ["Her N için satır sayısı **N×N** mi? (tüm b→s kombinasyonları kapsanmış mı)",
             "`Son Rank > İlk Rank` olan satır var mı? — sıralamanın *kötüleştiği* durumlar "
             "tabloda tanımlı mı?",
             "`İlk Rank > Rakip Sayısı` gibi mantıksız satır var mı?"]),

    ("h2", "1.12  Bölüm 6 — Uçak rotasyonu (Flight Pairs)"),
    ("code", (F, 199, 212, "rotasyon eşleri ve kapsam")),
    ("p", "`Flight Pairs.xlsx` hangi gidiş uçuşunun hangi dönüş uçuşuyla **aynı uçağı** "
          "paylaştığını söyler. Bu, A2 kısıtının ham maddesidir. Kritik satır **211**'dir:"),
    ("box", ("\"Flight Pairs'te olmayan TK uçuşu\" ne demek?",
             "Rotasyon partneri bilinmeyen bir uçuşu kaydırmak risklidir — hangi uçağın hangi "
             "tura bağlı olduğunu bilmeden saatini değiştirirsek fiziksel olarak uygulanamaz "
             "bir tarife üretebiliriz. Proje bu uçuşları **\"ayarlanamaz / sabit\"** kabul "
             "eder (03'te `fixed_flnos`). İhtiyatlı ve savunulabilir bir tercih: "
             "bilmediğimiz şeye dokunmuyoruz.", "ok")),

    ("h2", "1.13  Bölüm 7 — Açık sorular ve raporun yazılması"),
    ("code", (F, 214, 228, "modellemeden önce karara bağlanacaklar + dosyaya yazma")),
    ("p", "Bu blok, sağlık kontrolünün **çıktısı olan altı karar sorusunu** listeler. "
          "Hepsi 02 ve 03'te bilinçli birer tercihle kapanır:"),
    ("tbl", (["Açık soru", "Nerede karara bağlandı?"],
             [["N_od tanımı: itinerary mi taşıyıcı mı?",
               "02 — `CFG[\"n_od_def\"] = \"carrier\"` (veri 17 ≤ 40)"],
              ["Gate-to-Gate 24 saat sarması",
               "02 — `dur_min()` + `ElapsedTime` ile kesin J"],
              ["T_IB / T_OB bacak sürelerini ayrıştırma",
               "02 — `flight_block_times.csv` (A2 için)"],
              ["Ayar pencereleri ve gün-içi düzenlilik",
               "03 — `wdev_min = 60`, `xdev_min = 15`, `delta_min = 10`"],
              ["ρ'su olmayan pazarlar",
               "02 — `missing_rho = \"exclude\"`; 03 — `extra_use` ile F'de sayılır"],
              ["Slot pencereleri (Kısıt H)",
               "Kapsam dışı bırakıldı; F kova kapasitesi uygulanır"]],
             [7.6, 9.4], 8.8)),
    ("p", "Son olarak `_buf` içeriği bir markdown kod bloğuna sarılarak "
          "`reports/data_health_report.md` dosyasına yazılır — böylece rapor hem düz metin "
          "okunabilirliğini korur hem de markdown araçlarıyla DOCX/PDF'e çevrilebilir."),
    ("code", (F, 231, 232, "standart giriş noktası koruması")),
    ("p", "`if __name__ == \"__main__\"` kalıbı: dosya doğrudan çalıştırıldığında `main()` "
          "koşar, ama başka bir modül tarafından `import` edildiğinde koşmaz. Bu proje bu "
          "kalıba her dosyada uyar (07 ve 08, 03'ü tam da bu sayede import edebiliyor)."),
]
