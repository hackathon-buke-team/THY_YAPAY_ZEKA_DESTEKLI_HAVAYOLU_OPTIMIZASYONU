# -*- coding: utf-8 -*-
"""Bolum 2 — 02_data_prep.py"""

F = "02_data_prep.py"

ITEMS = [
    ("h1", ("2", "02_data_prep.py — Veri Hazırlama")),

    ("box", ("Bu dosya ne yapar?",
             "Ham Excel'leri modelin doğrudan tüketebileceği **temiz CSV katmanına** çevirir. "
             "Yolculuk sürelerini kesinleştirir, 24 saat sarmasını düzeltir, hafta "
             "kopyalarını birleştirir, rakip sürelerini ve pazar ağırlıklarını hesaplar. "
             "Yaptığı **her dönüşümü** `derived/transform_log.md` içine yazar — yani hiçbir "
             "değişiklik gizli kalmaz.")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`data/` — 4 Excel (yine salt-okunur)"],
              ["Çıktı", "`derived/` — 9 CSV + `transform_log.md`"],
              ["Çalıştırma", "`python src/02_data_prep.py`"],
              ["Bağımlılık", "`pandas`, `numpy`"],
              ["Süre", "yaklaşık 10–20 saniye"]],
             [3.0, 14.0], 9.0)),

    ("h2", "2.1  Politika: \"minimal + belgeli\""),
    ("code", (F, 1, 14, "dosyanın anayasası")),
    ("p", "Bu docstring bir kullanım kılavuzu değil, bir **taahhüttür**. Dört maddesi de "
          "yarışma bağlamında savunulabilirliğin temelidir:"),
    ("tbl", (["İlke", "Ne demek?", "Neden?"],
             [["Orijinale dokunma",
               "`data/` yalnız `pd.read_excel` ile okunur, asla yazılmaz",
               "Jüri istediği an ham veriyi kontrol edebilir"],
              ["Değer uydurma",
               "Eksik bir hücre tahminle doldurulmaz",
               "Uydurulan her değer sonucu şişirir ve savunulamaz"],
              ["Minimal düzeltme",
               "J yalnız **fiziksel olarak imkânsız** satırlarda düzeltilir",
               "\"Sanırım hatalıydı\" değil, \"matematiksel olarak olamaz\""],
              ["Her şeyi logla",
               "Tüm dönüşümler `transform_log.md`'ye yazılır",
               "İzlenebilirlik = güvenilirlik"]],
             [3.0, 6.6, 7.4], 8.6)),

    ("h2", "2.2  Kurulum — 01 ile aynı kalıp"),
    ("code", (F, 16, 49, "import'lar, yollar ve dosya bulma")),
    ("p", "Bu 34 satır, `01_data_health_check.py`'nin 12–47 satırlarının neredeyse birebir "
          "aynısıdır: aynı `__file__` tabanlı yol türetmesi, aynı `_find_conn_file()` "
          "önceliklendirmesi, aynı dosya sabitleri. Fark yalnız çıktı klasörüdür — 01 "
          "`reports/`, 02 `derived/` üretir."),
    ("box", ("Kod tekrarı bir kusur değil mi?",
             "Burada bilinçli bir tercih. Her modülün **tek başına** çalışabilmesi ve "
             "birbirine bağımlı olmaması isteniyor: 01 çökerse 02 yine koşabilmeli. "
             "Paylaşılan bir `utils.py`, modüller arasında gizli bağımlılık yaratırdı ve en "
             "kritik yerde — bağımsız doğrulayıcı 05'te — bu bağımlılık **doğrulamayı "
             "geçersiz kılardı** (bkz. Bölüm 5.2). Yaklaşık 30 satırlık tekrar, bu "
             "bağımsızlığın makul bedelidir.", "info")),

    ("h2", "2.3  Yapılandırma sözlüğü (CFG) ve log"),
    ("code", (F, 51, 63, "tek yerden yönetilen parametreler")),
    ("p", "Sihirli sayılar kodun içine dağıtılmamış, tek bir sözlükte toplanmıştır. Bu, "
          "birinin \"peki bağlantı penceresini 45–360 yapsak?\" sorusuna tek satır "
          "değiştirerek cevap verebilmesi demektir. Beş anahtarın anlamı:"),
    ("tbl", (["Anahtar", "Değer", "Anlamı"],
             [["`L_min` / `U_min`", "60 / 300",
               "Bağlantı boşluğu penceresi (dakika) — brief'ten"],
              ["`tau_min`", "45", "Minimum yer süresi τ; A2 rotasyon kısıtında kullanılır"],
              ["`dewrap`", "\"minimal\"",
               "24 saat sarması düzeltmesi: yalnız imkânsız satırlarda (\"off\" = hiç yapma)"],
              ["`n_od_def`", "\"carrier\"",
               "Rakip sayısı **taşıyıcı** bazlı sayılır (01'in bulgusu: max 17 ≤ 40)"],
              ["`missing_rho`", "\"exclude\"",
               "Gelir ağırlığı olmayan pazarlar amaç evreninden çıkarılır"]],
             [3.2, 2.2, 11.6], 8.6)),
    ("p", "`log()` fonksiyonu 01'deki `out()` ile aynı fikri taşır: hem ekrana bas hem "
          "`LOG` listesine biriktir, sonunda dosyaya yaz."),

    ("h2", "2.4  `dur_min()` — projenin en kritik 27 satırı"),
    ("code", (F, 65, 98, "tmin ve dur_min")),
    ("p", "İki fonksiyon var. `tmin()` (65–69) yalnız *saat-of-day* değerlerini çevirir — "
          "basit hâl. Asıl iş `dur_min()`'de:"),
    ("p", "Bu fonksiyon neden bu kadar uzun? Çünkü Excel bir \"süre\" değerini **altı farklı "
          "şekilde** verebilir ve hangisinin geleceği dosyanın nasıl kaydedildiğine bağlıdır:"),
    ("tbl", (["Gelen tip", "Örnek", "Dönüşüm", "Satır"],
             [["`datetime`", "`1899-12-30 06:19:00`",
               "1899-12-30 epoch'undan fark — **24 saati aşan süreler gün kısmında taşınır**",
               "78–79"],
              ["`time`", "`06:19:00`", "saat×60 + dakika + saniye/60", "80–81"],
              ["`timedelta`", "`0 days 06:19:00`", "`total_seconds()/60`", "82–83"],
              ["`int` / `float`", "`0.2632`", "Excel seri numarası: 1.0 = 1 gün → ×1440", "84–85"],
              ["`str` (nokta biçim)", "`\"30.12.1899 06:19:00\"`",
               "`strptime` ile ayrıştır, epoch farkı al", "90–92"],
              ["`str` (saat biçim)", "`\"06:19\"` / `\"06:19:00\"`",
               "`:` ile böl, sayısal doğrula, dakikaya çevir", "93–97"]],
             [3.2, 4.2, 8.0, 1.6], 8.4)),
    ("box", ("Neden bu kadar önemli?",
             "J (toplam yolculuk süresi) rakiple karşılaştırılan **tek** büyüklüktür. J'yi "
             "yanlış hesaplarsanız model yanlış rakibi \"yenilmiş\" sayar, sıralama ödülünü "
             "hak etmeden alır ve tüm sonuç geçersiz olur. Bu 27 satır, sonucun doğruluğunu "
             "taşıyan temeldir. Tanımadığı bir biçim gelirse `np.nan` döner — ve bir sonraki "
             "blok o NaN'ı yakalayıp **açık hatayla** koşuyu durdurur.", "warn")),

    ("h2", "2.5  `main()` ve şema doğrulaması"),
    ("code", (F, 101, 111, "yapılandırmanın loglanması ve dört dosyanın okunması")),
    ("p", "`main()` önce CFG'yi loglar — böylece `transform_log.md` hangi ayarlarla "
          "üretildiğini kendi içinde taşır — sonra dört Excel'i okuyup boyutlarını yazar."),
    ("code", (F, 113, 122, "beklenen sütunlar gerçekten var mı?")),
    ("p", "`need()` üç satırlık bir yardımcıdır ama işlevi büyüktür: gizli test verisinde bir "
          "sütun adı değişmişse, kod 200 satır sonra anlaşılmaz bir `KeyError: 'Dep1'` "
          "vermek yerine **hemen burada** şunu der: *\"'O&D Rakip Bağlantı Tablosu' beklenen "
          "sütun(lar) eksik: ['Dep1'] — mevcut sütunlar: [...]\"*. Hata mesajı, çözümü de "
          "içinde taşır."),

    ("h2", "2.6  Ortak türetmeler"),
    ("code", (F, 124, 130, "o, d, is_tk, gap_min, J_wrap_min")),
    ("bul", ["`o` ve `d` — pazarın kalkış ve varış havalimanı kodları.",
             "`is_tk` — bu satır THY'ye mi ait? Tablo boyunca kullanılacak maske.",
             "`gap_min` — IST'teki bekleme süresi, doğrudan zaman damgalarından **kesin** "
             "hesaplanır (burada belirsizlik yok).",
             "`J_wrap_min` — Gate-to-Gate sütunundan okunan J. \"wrap\" adı, bu değerin "
             "24 saatte sarmış olabileceğini hatırlatır."]),

    ("h2", "2.7  J hesabı — iki yol, tek doğru sonuç"),
    ("img", ("f04_dewrap.png",
             "Şekil 2.1 — Sarma (wrap) problemi ve minimal de-wrap düzeltmesi.")),
    ("h3", "Yol 1 (tercih edilen): ElapsedTime sütunları varsa"),
    ("code", (F, 132, 155, "J'nin kesin hesabı ve doğrulanması")),
    ("p", "Güncellenmiş veride her bacağın süresi ayrı ayrı verildiği için J **hesaplanır**, "
          "okunmaz:"),
    ("bul", ["`legsum_min = E1 + E2` — iki bacağın toplam uçuş süresi.",
             "`J_min = legsum_min + gap_min` — kesin toplam yolculuk. **Sarma belirsizliği "
             "tamamen ortadan kalkar.**",
             "`dewrap_k` — bu kesin J ile Gate-to-Gate sütunu arasındaki fark kaç tam gündür? "
             "(Belgeleme amaçlı saklanır.)"]),
    ("p", "**149–153** satırları bir **çapraz doğrulamadır**: kesin J ile sarılı "
          "Gate-to-Gate arasındaki fark tam olarak 24 saatin katı olmalı. Değilse iki kaynak "
          "birbiriyle çelişiyor demektir ve rapor bunu \"tutarsız satır\" olarak bildirir "
          "(beklenen değer 0)."),
    ("code", (F, 156, 162, "eski sezgiselin ne kaçıracağını ölçer")),
    ("p", "Bu blok koda hiçbir şey **yapmaz** — sadece belgeler. Sorduğu soru: *\"Eğer "
          "ElapsedTime olmasaydı ve eski minimal de-wrap sezgiselini kullansaydık kaç satırı "
          "yanlış hesaplardık?\"* Bu, güncellenmiş veriyi kullanma kararının **sayısal "
          "gerekçesidir** ve teknik raporda doğrudan alıntılanabilir."),
    ("h3", "Yol 2 (yedek): eski şema — minimal de-wrap"),
    ("code", (F, 163, 182, "yalnız fiziksel olarak imkânsız satırlara +24 saat")),
    ("p", "ElapsedTime yoksa J yalnız Gate-to-Gate'ten gelir. Bu durumda **tek güvenli "
          "düzeltme kuralı** şudur: J < boşluk ise bu satır fiziksel olarak imkânsızdır "
          "(toplam yolculuk, sadece bekleme süresinden bile kısa olamaz), demek ki değer "
          "sarmıştır. Sarma sayısı `k = ceil((boşluk − J) / 1440)` ile en az kaç gün "
          "eklenmesi gerektiğinden hesaplanır."),
    ("box", ("\"Açık işaret\" satırı (180–182)",
             "23 saatten uzun görünen ama J ≥ boşluk olduğu için imkânsız sayılmayan satırlar "
             "**dokunulmadan bırakılır** ve sayıları raporlanır. Bu, projedeki ihtiyat "
             "prensibinin somut örneğidir: emin olmadığımız yerde veriyi değiştirmiyoruz, "
             "sadece riski ilan ediyoruz.", "ok")),

    ("h2", "2.8  Hafta normalizasyonu — aynı uçuşun iki kopyası"),
    ("code", (F, 184, 212, "TK adayları ve hafta kopyalarının birleştirilmesi")),
    ("p", "Veride ilginç bir tuzak var: **aynı operasyon günü** (örneğin \"Gün 1\") farklı "
          "pazarlarda farklı takvim haftalarına yazılmış olabilir. Bir satırda 4 Ağustos "
          "Pazartesi, başka satırda 11 Ağustos Pazartesi. İkisi de \"gün 1\"dir ama zaman "
          "damgaları bir hafta farklıdır."),
    ("box", ("Bu neden bir sorundur?",
             "Model, karar birimlerini `(uçuş no, rol, saat)` anahtarıyla oluşturur. Aynı "
             "fiziksel uçuş iki farklı takvim tarihine yazılmışsa **iki ayrı karar olayı** "
             "doğar ve çözücü aynı uçuşa iki farklı yeni saat verebilir. Bu, uygulanamaz bir "
             "tarifedir.", "warn")),
    ("p", "Düzeltme (198–207) cerrahi bir müdahaledir:"),
    ("num", ["Her satırın **kalkış tarihi** alınır (`ist_dep.dt.normalize()`).",
             "Her operasyon günü için o günün **kanonik** (en erken) tarihi bulunur.",
             "Fark tam olarak 7'nin katıysa satırın **iki** zaman damgası birlikte geri "
             "çekilir. **İkisi birlikte** olduğu için boşluk ve J hiç değişmez.",
             "7'nin katı değilse satıra **dokunulmaz** — bilmediğimiz bir düzen olabilir."]),
    ("p", "`ev_key` lambda'sı düzeltmeden önce ve sonra benzersiz olay sayısını ölçer; log "
          "\"birleşen hafta-kopyası: N\" satırıyla etkinin büyüklüğünü belgeler."),
    ("code", (F, 214, 228, "birebir özdeş adayların tekilleştirilmesi")),
    ("p", "Hafta kopyaları birleşince **tamamen özdeş iki satır** kalabilir. İkisini iki ayrı "
          "aday saymak, aynı ürüne çifte aktarma ödülü yazdırır — bu hem baseline'ı hem "
          "optimize sonucunu şişirir, yani sonuç *sahte* olur. `drop_duplicates` yalnız "
          "**tüm alanları** özdeş olanları atar; saatleri gerçekten farklı olan satırlar "
          "(veri anomalisi) korunur ve model onları ayrı olaylar olarak ele alır."),

    ("h2", "2.9  Bacak blok süreleri — A2 rotasyonunun yakıtı"),
    ("code", (F, 230, 248, "her (uçuş, gün, rol) için blok süresi")),
    ("p", "A2 kısıtı \"dönüş varışı ≥ gidiş kalkışı + T_OB + τ + T_IB\" der. T_OB ve T_IB'yi "
          "buradan üretiyoruz: `FlNo1`'in E1'i gelen bacağın (arr) bloğu, `FlNo2`'nin E2'si "
          "giden bacağın (dep) bloğudur."),
    ("box", ("Neden `.max()`?",
             "Aynı `(uçuş no, gün)` için birden çok farklı blok süresi görülürse **en büyüğü** "
             "alınır. Böylece minimum tur süresi asla olduğundan kısa hesaplanmaz — yani tur, "
             "brief'in gerektirdiği minimumun altına **sıkıştırılamaz**. Kuşkulu durumda "
             "ihtiyatlı tarafta kalma tercihi.", "ok")),

    ("h2", "2.10  Rakip itineraryleri ve N_od"),
    ("code", (F, 250, 268, "T_comp ve rakip sayısı")),
    ("p", "İki türetme:"),
    ("bul", ["**`tcomp_carrier`** — her (pazar, gün, taşıyıcı) için **en küçük J**. Yani "
             "\"bu rakip bu pazarda en iyi ne yapabiliyor?\" Modelin yeneceği eşik budur.",
             "**`n_od`** — pazardaki rakip sayısı. `n_od_def = \"carrier\"` olduğu için "
             "`nunique()` ile farklı **taşıyıcı** sayılır."]),
    ("p", "Satır 267–268 kapsamı doğrular: N_od aralığı ödül tablosunun desteklediği max "
          "N = 40'ı aşıyor mu? Log \"kapsam TAM\" veya \"EKSİK\" yazar — bu, 01'de sorulan "
          "açık sorunun kapanış kaydıdır."),
    ("p", "`ML2` sütunu (Mainline / Low-cost) varsa bilgi amaçlı taşınır ama modele girmez; "
          "brief'in sıralama tanımı taşıyıcı tipi ayrımı yapmaz."),

    ("h2", "2.11  Pazar tablosu — ρ, kapsam ve dışlama"),
    ("code", (F, 270, 286, "markets.csv'nin oluşumu")),
    ("p", "Her yönlü pazar için tek satır üretilir ve dört bilgi eklenir:"),
    ("tbl", (["Sütun", "Anlamı", "Nerede kullanılır?"],
             [["`rho`", "Gelir/önem ağırlığı", "Amaç fonksiyonu çarpanı (03)"],
              ["`has_tk`", "Bu pazarda TK bağlantısı var mı?", "Alt-örnek seçimi (03)"],
              ["`has_comp`", "Rakip var mı?", "Sıralama teriminin tanımlı olup olmadığı"],
              ["`excluded_no_rho`", "ρ'su yok → amaç evreni dışı",
               "03'te dışlanır, ama uçuşları F kapasitesinde sayılır"]],
             [3.6, 6.4, 7.0], 8.8)),

    ("h2", "2.12  Rotasyon kapsamı"),
    ("code", (F, 288, 295, "partneri olmayan TK uçuşları")),
    ("p", "`Flight Pairs`'te karşılığı olmayan TK uçuş numaraları ayrı bir listeye çıkarılır. "
          "03 bu listeyi `fixed_flnos` olarak okur ve o uçuşları **hiç kımıldatmaz** "
          "(`cands = [cur]`). Rotasyonunu bilmediğimiz uçağa dokunmama ilkesi."),

    ("h2", "2.13  `derived/` katmanının yazılması"),
    ("code", (F, 297, 317, "9 CSV + dönüşüm logu")),
    ("p", "`encoding=\"utf-8-sig\"` seçimi bilinçlidir: BOM'lu UTF-8, Excel'in Türkçe "
          "karakterleri doğru açmasını sağlar (jüri CSV'yi çift tıklayıp açtığında \"BaÄŸlantÄ±\" "
          "görmemeli). Son olarak `transform_log.md` yazılır ve log dosya listesini "
          "boyutlarıyla basar."),
    ("tbl", (["Dosya", "İçerik", "Kim kullanır?"],
             [["`tk_connections.csv`", "TK bağlantı adayları (pazar, gün, uçuşlar, saatler, J)",
               "03, 05, 08"],
              ["`competitor_itineraries.csv`", "Rakiplerin tüm bağlantı seçenekleri",
               "referans / rapor"],
              ["`competitor_times_carrier.csv`", "Taşıyıcı başına en iyi J (T_comp)",
               "03, 05, 08"],
              ["`market_n_od.csv`", "(pazar, gün) → rakip taşıyıcı sayısı N", "03, 05"],
              ["`markets.csv`", "Pazar listesi + ρ + kapsam bayrakları", "03, 05"],
              ["`ranking_lookup.csv`", "Sıralama ödül tablosu (N, b, s, W)", "03, 05, 08"],
              ["`flight_rotation.csv`", "Uçak rotasyon eşleri", "03, 05"],
              ["`flight_block_times.csv`", "(uçuş, gün, rol) → blok süresi", "03, 05, 08"],
              ["`tk_flights_without_partner.csv`", "Rotasyon partneri olmayan uçuşlar",
               "03 (sabit kabul)"],
              ["`transform_log.md`", "Yapılan tüm dönüşümlerin kaydı", "jüri / izlenebilirlik"]],
             [5.4, 7.6, 4.0], 8.4)),
    ("p", "Kapanış satırı bir taahhüdü tekrar eder: **\"KAYNAK DOSYALAR DEĞİŞMEDİ. Tüm "
          "dönüşümler bu logda.\"**"),
]
