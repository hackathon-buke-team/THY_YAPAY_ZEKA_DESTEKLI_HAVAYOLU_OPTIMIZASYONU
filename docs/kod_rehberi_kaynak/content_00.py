# -*- coding: utf-8 -*-
"""Bolum 0 — Kusbakisi."""

ITEMS = [
    ("h1", ("0", "Kuşbakışı — Bu proje ne yapıyor, kod nasıl bölünmüş?")),

    ("h2", "0.1  Problem, beş cümlede"),
    ("p", "İstanbul (IST) bir **aktarma merkezidir**: yolcu bir uçuşla IST'e gelir, bir "
          "süre bekler, ikinci uçuşla nihai varış noktasına gider. Bu ikili birleşime "
          "**bağlantı** (itinerary) denir ve satılabilir bir üründür. Bir bağlantının "
          "gerçekten satılabilmesi için IST'teki bekleme süresinin ne çok kısa "
          "(yetişemezsiniz) ne de çok uzun (kimse tercih etmez) olması gerekir — brief bu "
          "pencereyi **60–300 dakika** olarak sabitler. Aynı O–D pazarında rakip havayolları "
          "da bağlantı satar; kim daha kısa toplam yolculuk süresi (J) sunuyorsa sıralamada "
          "önde olur. **Bu projenin görevi: THY'nin IST kalkış/varış saatlerini ±60 dakikalık "
          "bir pencerede, 10 dakikalık ızgarada oynatarak, fiziksel ve operasyonel kısıtları "
          "hiç bozmadan, gelir-ağırlıklı rekabetçilik puanını en yükseğe çıkarmak.**"),

    ("box", ("Tek cümlelik özet",
             "Kod, dört Excel dosyasını okur → tutarlı bir veri katmanı üretir → bunu bir "
             "**Karışık Tamsayılı Programlama (MIP)** modeline çevirir → HiGHS çözücüsüyle "
             "çözer → sonucu bağımsız bir ikinci kodla doğrular → rapor, figür ve teslim "
             "dosyalarını yazar.")),

    ("h2", "0.2  Kod nasıl organize edilmiş? (\"class\" meselesi)"),
    ("p", "`src/` altındaki sekiz dosya birer **modül**dür; projenin organizasyon birimi "
          "sınıf değil, **modüldür**. Bunun bilinçli bir nedeni var: her modül tek bir "
          "sorumluluk taşır, kendi başına çalıştırılabilir (`python src/02_data_prep.py`) ve "
          "diskteki dosyalar üzerinden bir sonrakine bağlanır. Bu, akademik/yarışma "
          "projelerinde tercih edilen **boru hattı (pipeline) mimarisidir**: bir adım "
          "çöktüğünde hangi adımın hangi dosyayı bozduğu tek bakışta anlaşılır."),
    ("p", "Projede yalnızca **iki gerçek sınıf** vardır ve ikisi de bilinçli olarak çok "
          "sadedir:"),
    ("tbl", (["Sınıf", "Dosya", "Görevi"],
             [["`Instance`", "`03_model.py` (satır 205–207)",
               "Modelin tüketeceği ön-işlenmiş alt-örneği taşıyan **boş veri kabı**. Gövdesi "
               "yalnız `pass`'tır; alanları dışarıdan (`build_instance`) atanır. Amaç: 15+ "
               "değişkeni fonksiyonlar arasında tek tek taşımak yerine tek nesnede toplamak."],
              ["`Checks`", "`05_validate_solution.py` (satır 87–102)",
               "Doğrulama sonuçlarını biriktiren **PASS/FAIL toplayıcı**. `add()` ile kontrol "
               "ekler, ekrana basar ve rapor satırını saklar; bir tane bile FAIL varsa "
               "`failed` bayrağını kaldırır."]],
             [2.6, 4.4, 10.0])),
    ("pm", "Yani \"sınıfları öğrenmek\" istediğinizde aslında öğrenmeniz gereken şey "
           "modüllerin ne yaptığıdır — bu doküman tam olarak bunu, blok blok anlatır."),

    ("h2", "0.3  Boru hattı: hangi dosya ne zaman çalışır?"),
    ("img", ("f01_pipeline.png",
             "Şekil 0.1 — `run_all.py` adımları çalışma sırasıyla koşturur. Numaralandırma "
             "dosya adına göredir; çalışma sırası 01 → 02 → 03 → 08 → 05 → 06 → 04'tür.")),
    ("p", "Dikkat edilecek iki nokta:"),
    ("bul", ["**08, 03'ten sonra gelir** (numarası büyük ama aşama-2'dir): 03 haftanın "
             "günlerini ayrı ayrı çözer, 08 aynı çözümü haftanın tamamını kapsayan tek "
             "modele başlangıç noktası olarak verip küresel olarak iyileştirir.",
             "**05 en sonda değil, ortadadır**: doğrulama başarısız olursa figür ve doküman "
             "üretilmeden koşu durur. Doğrulanmamış bir çözüm için rapor üretmek, hatayı "
             "cilalamak demektir."]),

    ("h2", "0.4  Veri katmanları: hangi klasör neyi tutar?"),
    ("img", ("f02_veri_katmanlari.png",
             "Şekil 0.2 — Tek yönlü veri akışı. Sol taraf asla değişmez; sağa doğru her "
             "katman bir öncekinden türetilir.")),
    ("tbl", (["Klasör", "İçerik", "Kim yazar?", "Kim okur?"],
             [["`data/`", "Yarışmanın orijinal 4 Excel dosyası", "**Hiç kimse** (salt-okunur)",
               "01, 02"],
              ["`derived/`", "Temizlenmiş, türetilmiş CSV veri katmanı", "02", "03, 05, 07, 08"],
              ["`output/`", "Çözüm dosyaları (teslim #3)", "03, 08", "05, 06, 08"],
              ["`reports/`", "Sağlık raporu, doğrulama raporu, duyarlılık analizi", "01, 05, 07, 08",
               "04 (docx'e çevirir)"],
              ["`docs/`", "Model formülasyonu + figürler", "06", "04"]],
             [2.3, 6.0, 4.4, 4.3])),

    ("h2", "0.5  Modelin temel nesnesi: bir bağlantı (π)"),
    ("p", "Kodun her yerinde karşınıza çıkacak dört büyüklüğü baştan oturtalım. Bunları "
          "bilmeden 03_model.py okunmaz:"),
    ("img", ("f03_baglanti_anatomisi.png",
             "Şekil 0.3 — Bağlantının anatomisi. Model uçuş sürelerini değiştiremez; "
             "yalnızca iki kırmızı çizgiyi (IST varış ve IST kalkış saatlerini) oynatabilir.")),
    ("tbl", (["Simge", "Koddaki adı", "Ne demek?"],
             [["θ (theta)", "`theta_expr(...)`, `x[eid,v]`",
               "Bir uçuş olayının IST saati (dakika). Modelin **karar değişkeni** budur."],
              ["boşluk (gap)", "`gap_min`, `m._gap[pi]`",
               "θ_kalkış − θ_varış. Yolcunun IST'te bekleme süresi."],
              ["legsum", "`legsum_min`",
               "İki bacağın uçuş süreleri toplamı (E1 + E2). **Sabittir**, model değiştiremez."],
              ["J", "`J_min`, `J_dk`",
               "Toplam yolculuk süresi = legsum + boşluk. Rakiple kıyaslanan büyüklük budur."]],
             [2.4, 4.4, 10.2])),

    ("h2", "0.6  Kısıt haritası — kod boyunca A1, B1, E2 gibi etiketler göreceksiniz"),
    ("p", "Kısıtlar `docs/model_formulation.md` ile aynı harflerle etiketlenmiştir. Bu "
          "doküman boyunca her kısıt kodda geçtiği yerde ayrıntılı açıklanır; burası "
          "sadece haritadır:"),
    ("tbl", (["Kod", "Adı", "Ne garanti eder?", "Nerede kurulur?"],
             [["**A1**", "Tekil zaman ataması",
               "Her uçuş olayı ±60 dk pencerede, 10 dk ızgarada **tam bir** saate atanır",
               "03: 372–375"],
              ["**A2**", "Uçak rotasyonu",
               "Dönüş varışı ≥ gidiş kalkışı + T_OB + τ + T_IB (aynı uçak gidip döner)",
               "03: 492–566"],
              ["**B1**", "Bağlantı uygunluğu",
               "y_π = 1 ⟺ 60 ≤ boşluk ≤ 300 dk", "03: 386–393"],
              ["**B2**", "Zorunlu sunum",
               "Uygun her bağlantı sunulmalı — **kapalı** (E1 ile çatışıyor)", "03: 394–400"],
              ["**C**", "Azalan getiri",
               "Bir pazardaki j. bağlantının ödülü (½)^(j−1); monoton doldurma", "03: 402–418"],
              ["**D**", "Rakip yenme + sıralama",
               "J ≤ T_comp ise rakip yenilir; yenilen sayısı sıralama ödülüne çevrilir",
               "03: 420–475"],
              ["**E1**", "Yönsel sayı dengesi",
               "|n_od − n_do| ≤ 0.20·(n_od + n_do)", "03: 477–490"],
              ["**E2**", "En iyi süre dengesi",
               "|J_min(o→d) − J_min(d→o)| ≤ 30 dk — tam ölçekte **kapalı**", "03: 649–684"],
              ["**F**", "IST hub kapasitesi",
               "Her 10 dk kovada kalkış ≤ 10, varış ≤ 15", "03: 686–725"],
              ["**G**", "Tarife düzenliliği",
               "Aynı uçuş no'nun saat-içi zamanı günler arası ±15 dk bandında", "03: 590–647"],
              ["**P**", "Tarife-değişim cezası",
               "Amaçtan −λ·Σ|θ−cur| düşülür (λ = 0.3)", "03: 734–748"]],
             [1.5, 3.4, 8.2, 3.9], 8.2)),

    ("h2", "0.7  Terimler sözlüğü (kodda geçtiği hâliyle)"),
    ("tbl", (["Terim", "Anlamı"],
             [["**O–D (pazar)**",
               "Origin–Destination, yönlü pazar. Örn. `\"AGP-KCM\"`. Kodda `market`."],
              ["**itinerary**",
               "Bir aktarmalı yolculuk seçeneği. TK'nınkine `conns`, rakibinkine "
               "`competitor_itineraries` denir."],
              ["**ρ (rho)**",
               "Pazarın gelir/önem ağırlığı (`OD importance factor`). Amaç fonksiyonundaki "
               "çarpan — büyük pazarda kazanılan puan daha değerlidir."],
              ["**N_od**",
               "O–D pazarındaki rakip **taşıyıcı** sayısı (`n_od_def = \"carrier\"`)."],
              ["**T_comp**",
               "Bir rakip taşıyıcının o pazardaki **en iyi** (en kısa) J değeri."],
              ["**b_od**",
               "Pazarın **başlangıç sırası** — mevcut tarifedeki performansa göre hesaplanır. "
               "Sıralama ödülü b_od'den s'ye geçişin ödülüdür."],
              ["**s**",
               "Son sıra = clip(N − yenilen, 1, N). Küçük s = daha iyi sıralama."],
              ["**baseline**",
               "Mevcut (hiç dokunulmamış) tarifenin amaç değeri. Tüm iyileşme buna göre "
               "ölçülür."],
              ["**MIP**",
               "Mixed-Integer Programming. Bazı değişkenleri tam sayı (burada 0/1) olan "
               "doğrusal optimizasyon."],
              ["**Pyomo / HiGHS**",
               "Pyomo modeli Python'da kurar, HiGHS açık-kaynak çözücü onu çözer."],
              ["**ikili değişken**",
               "0 veya 1 değeri alan karar değişkeni. `x`, `y`, `z`, `w`, `β`, `γ` hepsi ikilidir."],
              ["**big-M**",
               "\"Şu koşul aktifse şu eşitsizlik geçerli olsun\" mantığını doğrusal hâle "
               "getiren büyük sabit. Kodda `Mlo`, `Mhi`, `Mw`, `MJ` isimleriyle geçer."],
              ["**warm-start / MIP-start**",
               "Çözücüye \"işte elimde çalışan bir çözüm, buradan başla\" demek. 08'in "
               "tüm yöntemi budur."],
              ["**MIP-gap**",
               "Bulunan çözüm ile teorik üst sınır arasındaki bağıl fark. %0.1 gap = "
               "\"en fazla binde bir daha iyisi olabilir\"."],
              ["**byday**",
               "Güne-göre ayrıştırma: 7 günü ayrı ayrı çözme stratejisi (`03_model.py byday`)."],
              ["**λ (lambda)**",
               "Tarife-değişim cezasının ağırlığı. Büyük λ = \"uçuşları kımıldatma\"."],
              ["**Wdev / Xdev / τ / Δ**",
               "Sırasıyla: uçuş penceresi (±60 dk), günler-arası düzenlilik bandı (15 dk), "
               "minimum yer süresi (45 dk), ızgara adımı (10 dk)."]],
             [3.4, 13.6], 8.6)),

    ("h2", "0.8  Bu dokümanı nasıl okumalısınız?"),
    ("bul", ["Her bölüm bir dosyayı anlatır. Bölüm başında **\"Bu dosya ne yapar\"** özeti, "
             "girdi/çıktı tablosu ve çalıştırma komutu vardır.",
             "Ardından dosya **baştan sona, blok blok** ilerler. Her blokta önce **gerçek kod** "
             "(satır numaralarıyla, kaynaktan birebir), sonra **ne yaptığının açıklaması** gelir.",
             "Gri kutular bağlam/uyarı, mavi kutular önemli fikirler, yeşil kutular "
             "\"neden böyle yapılmış\" gerekçeleridir.",
             "Sadece belirli bir kısıtı anlamak istiyorsanız **0.6'daki haritadan** doğrudan "
             "ilgili satır aralığına gidin."]),
]
