# -*- coding: utf-8 -*-
"""Dokuman 3 — Bolum 1-2: Biz ne yaptik, ozgunluk, yapmasaydik ne olurdu."""

F3 = "03_model.py"
F2 = "02_data_prep.py"
F5 = "05_validate_solution.py"
F8 = "08_fullweek_polish.py"

ITEMS = [
    # ================================================================= 1
    ("h1", ("1", "Biz bu projede ne yaptık?")),

    ("p", "Bu bölüm tek bir soruya cevap veriyor: **\"Çözücüyü kullandınız, sizin katkınız "
          "ne?\"** Jüri bunu soracak. Cevap sandığınızdan güçlü — ama önce bir kavram "
          "karışıklığını temizlemek gerekiyor."),

    ("h2", "1.1  \"Model yaptık mı?\" — kelimenin iki anlamı"),
    ("tbl", (["\"Model\" ne demek?", "Bu projede", "Açıklama"],
             [["**Eğitilmiş yapay zekâ artefaktı**\n(makine öğrenmesi modeli)",
               "**YOK** — ve olmamalı",
               "Bu bir tahmin problemi değil. Geçmişten öğrenip gelecek tahmin etmiyoruz; "
               "kısıtlar altında en iyi kararı arıyoruz"],
              ["**Matematiksel formülasyon**\n(değişkenler, kısıtlar, amaç)",
               "**TAMAMEN BİZİM**",
               "`03_model.py`'nin 1.357 satırı. Brief size düz yazıyla bir iş problemi "
               "verdi; onu çözülebilir bir matematiksel yapıya çevirmek işin özüdür"]],
             [4.4, 3.4, 9.2], 8.6)),
    ("box", ("Neden bu ayrım önemli?",
             "Jüri \"yapay zekâ\" başlığını görüp bir sinir ağı bekleyebilir. Sinir ağı "
             "burada **yanlış araç** olurdu: sinir ağı size *muhtemelen iyi* bir tarife "
             "verir, ama hiçbir kısıtı garanti edemez ve \"bu en iyisi mi?\" sorusunu "
             "yanıtlayamaz. MIP ise hem her kısıtı **matematiksel olarak garanti eder** hem "
             "de optimale ne kadar yakın olduğunu **kanıtlar**.", "info")),

    ("h2", "1.2  Çözücü ne yapıyor, biz ne yaptık?"),
    ("img", ("h1_katki_haritasi.png",
             "Şekil 1.1 — Brief'ten sonuca giden beş adımın dördü bizim tasarımımız.")),
    ("p", "HiGHS havayolu bilmiyor. Aktarma nedir, hub nedir, uçak rotasyonu nedir — hiçbir "
          "fikri yok. Ona ne verirseniz onu çözer. Bu yüzden:"),
    ("box", ("Çözücü, sorduğunuz sorunun cevabını verir. Bütün maharet doğru soruyu sormaktır.",
             "Yanlış formüle ederseniz çözücü size **yanlış sorunun kusursuz optimal "
             "cevabını** verir — ve bunu fark etmenizin hiçbir yolu olmaz. Örneğin J'yi 24 "
             "saat eksik hesaplasaydınız, çözücü \"yenmediğiniz rakipleri yendiniz\" der ve "
             "bunu mükemmel bir matematikle kanıtlardı.")),
    ("p", "\"Hesabı çözücüye yaptırdık\" demek, *\"binayı vinç yaptı\"* demek gibidir. Vinç "
          "ağırlığı kaldırır; neyin nereye konacağına mühendis karar verir."),

    # ================================================================= 2
    ("h1", ("2", "Özgünlük — beş başlıkta")),

    ("h2", "2.1  Formülasyon kararları (asıl entelektüel katkı)"),
    ("p", "Brief'te \"karar değişkenini olay bazında tanımlayın\" yazmıyor. Bunların hepsi "
          "tasarım tercihidir ve her birinin bir gerekçesi var:"),
    ("tbl", (["Karar", "Neden önemli?", "Kodda"],
             [["**Olay soyutlaması** — karar birimi bağlantı değil, `(uçuş, rol, saat)`",
               "Bir uçuş 20 bağlantıda geçiyor. Bağlantı başına karar verseydik aynı uçağa "
               "20 farklı saat atanabilirdi. Bu tasarım tutarsızlığı **yapısal olarak "
               "imkânsız** kılıyor", "`03:232–247`"],
              ["**Tek-sıcak (one-hot) zaman kodlaması**",
               "Tarife-değişim cezası `Σ|v−cur|·x` olarak **tam doğrusal** yazılabiliyor — "
               "sıfır ek değişken, sıfır big-M. F kapasitesi de aynı değişkenlerden kuruluyor",
               "`03:348–354`"],
              ["**`z` slot yapısı (Kısıt C)**",
               "\"1. bağlantı çok değerli, 5.'si değersiz\" fikrini monoton doldurma "
               "kısıtıyla doğrusallaştırma", "`03:402–418`"],
              ["**`γ` seçici yapısı (Kısıt D)**",
               "Ayrık bir lookup tablosunu (doğrusal olmayan fonksiyon) doğrusal amaç "
               "terimlerine çevirme", "`03:459–475`"],
              ["**Yön-yerel sıkı big-M**",
               "Genel bir \"büyük sayı\" yerine her bağlantının gerçekten ulaşabileceği "
               "aralıktan hesaplanan en sıkı M. Gevşek M = çözücü ağaçta kaybolur",
               "`03:386–390`"],
              ["**Üç yollu `w` elemesi**",
               "13.015 (bağlantı × rakip) çiftinin **%42'si için hiç değişken yaratılmıyor**",
               "`03:428–441`"],
              ["**`b_od`'nin `s` ile aynı tabandan türetilmesi**",
               "Bu yakalayış olmasaydı mevcut tarife pazarların **~%29'unda** hiçbir şey "
               "yapmadan sıralama ödülü kazanacak, iyileşmemiz sahte görünecekti",
               "`03:298–314`"]],
             [4.4, 9.2, 3.4], 8.2)),

    ("h2", "2.2  Çözüm stratejisi (algoritmik katkı)"),
    ("p", "Bu kısım tamamen bizim tasarımımız, çünkü **çözücü tek başına çözemiyordu**:"),
    ("img", ("h4_warmstart_kazanc.png",
             "Şekil 2.1 — İki aşamalı çözümün katkısı. Aşama-2 tek başına +14.752 puan "
             "getirdi ve global optimalite kanıtını üretti.")),
    ("num", ["**İki aşamalı matheuristik.** Monolitik 7-gün MIP çözülemiyor (~100k ikili, "
             "HiGHS tek bir uygun çözüm bile bulamıyor). Güne-göre ayrıştırma → tam-hafta "
             "warm-start hattını biz tasarladık.",
             "**Gece-aşan rotasyon koruması** (`compute_overnight_guards`, `03:979–1024`) — "
             "en zarif parça. Gün ayrıştırması gece-aşan turları göremez. Mevcut payı statik "
             "olarak ikiye bölüp iki **tek-taraflı sınıra** çevirdik; böylece iki gün "
             "birbirini hiç görmese bile ihlal *matematiksel olarak imkânsız* hâle geldi. "
             "Bağlaşık bir kısıtı, bağlaşıklık yaratmadan garantilemek.",
             "**G bandının günler arası zincirlenmesi** + çatışmada **iki aşamalı hedefli "
             "gevşetme** (önce yalnız rotasyon-korumalı uçuşların bandını bırak, sonra tam "
             "gevşet) — `03:1066–1084`.",
             "**Warm-start'ta `y`'nin uygunluktan değil byday'in gerçek sunumundan "
             "alınması** (`08:77–80`). Bunu fark etmeseydik HiGHS başlangıç noktasını "
             "reddedecek ve 08 hiç çalışmayacaktı.",
             "**Yeniden yazma bariyeri** (`08:475–485`) — iyi bir çözüm asla kötüsüyle "
             "ezilmiyor; iki koşul birden sağlanmadan `output/` dosyalarına dokunulmuyor."]),

    ("h2", "2.3  Veri mühendisliği"),
    ("tbl", (["Bulgu", "Ne yaptık?", "Etkisi"],
             [["**24 saat sarması**", "J'yi hazır sütundan okumak yerine bacak sürelerinden "
               "hesapladık + mod-24 çapraz doğrulaması", "57.317 satırda 0 tutarsızlık; "
               "eski yöntemle 154 satır yanlış olacaktı"],
              ["**Hafta kayması**", "Aynı operasyon gününün farklı takvim haftalarına "
               "yazılmasını hizaladık", "130 kopya olay birleşti; aynı uçağa iki farklı saat "
               "atanması engellendi"],
              ["**Özdeş kopyalar**", "Hizalama sonrası birebir aynı kalan satırları attık",
               "157 bağlantının iki kez ödüllendirilmesi engellendi"],
              ["**Amaç evreni eksikliği (F)**", "`extra_use` — modellenmeyen uçuşları "
               "kapasitede sabit doluluk olarak saydık",
               "Model olmayan kapasiteye uçuş yerleştiremiyor"],
              ["**Amaç evreni eksikliği (A2)**", "`full_role_time` — rotasyon ortağının "
               "modellenmeyen tarafını gerçek saatiyle ankorladık",
               "**Gerçek bir A2 ihlali** kapatıldı (doğrulayıcı yakalamıştı)"]],
             [4.0, 6.4, 6.6], 8.4)),

    ("h2", "2.4  Doğrulama — en ayırt edici yanımız"),
    ("box", ("Çift kayıt ilkesi",
             "`05_validate_solution.py` modelin kodundan **tamamen ayrı**. Pyomo import "
             "etmiyor, `03_model.py`'ye dokunmuyor, sabitleri (Wdev, τ, Xdev, kapasiteler) "
             "kendi dosyasında **yeniden yazıyor**. Girdisi yalnız `derived/` (veri) ve "
             "`output/` (çözüm). Baseline'ı bile sıfırdan hesaplıyor.\n\n"
             "Böylece modeldeki bir hata, doğrulamada **aynı hatayla örtülemez**.", "ok")),
    ("p", "Ve gerçekten iş gördü. Kod içindeki not (`05:52–60`) şunu kaydediyor:"),
    ("num", ["Pencere ±90 dakikaya çıkarıldı, sonuç **%5,34**'e yükseldi — cazip.",
             "Doğrulayıcı **gerçek bir A2 ihlali** yakaladı (uçuş 2200/2201, gün 2).",
             "Kök neden bulundu: rotasyon ortağının o günkü olayı ρ'suz bir pazara ait "
             "olduğu için hiç modellenmiyordu.",
             "**Yüksek rakam iptal edildi**, ±60'a dönüldü, kök neden kalıcı olarak "
             "düzeltildi."]),
    ("box", ("Sunumda anlatılacak hikâye",
             "*\"Daha yüksek bir sonucumuz vardı. Kendi doğrulayıcımız gerçek bir kısıt "
             "ihlali yakaladı. O sonucu çöpe attık ve hatayı kalıcı olarak düzelttik.\"*\n\n"
             "Bu cümle, bir jürinin bir takım hakkında duyabileceği en güçlü cümlelerden "
             "biridir.", "ok")),
    ("p", "Doğrulayıcının bir başka ince ayrıntısı: **fazla-beyan hata, eksik-beyan not** "
          "sayılıyor. Yani kendi lehimize olan sapmalar hata kabul ediliyor, aleyhimize "
          "olanlar edilmiyor. Ölçüm kendine karşı kurulmuş."),

    ("h2", "2.5  Dürüst raporlama"),
    ("bul", ["**λ tahminle değil taramayla seçildi** — 5 değerlik Pareto taraması, knee "
             "noktası (`03_model.py sweep`, `output/sweep_results.csv`).",
             "**Duyarlılık analizi, ölçümlerin neyi kanıtlamadığını açıkça yazıyor** — "
             "\"Wdev=90 ölçümü zaman-limitlidir, fark serbestlik etkisi olmayabilir\".",
             "**Sınırlar sonuçla birlikte yayınlanıyor** — E2'nin kapalı olduğu, G "
             "muafiyetlerinin sayısı (1.132), A2 artefaktları: hepsi `results_summary.md`'de.",
             "**Global MIP-gap %1,18** — optimalite kanıtı; greedy bir yöntemin veremeyeceği "
             "tek şey."]),

    # ================================================================= 3
    ("h1", ("3", "En güçlü kanıt: \"yapmasaydık ne olurdu?\"")),
    ("p", "Katkıyı anlatmanın en ikna edici yolu, her tasarım kararının **alternatifini** "
          "göstermektir. Aşağıdaki her satır bir karardır; hiçbiri çözücüden gelmiyor."),
    ("tbl", (["Yapmasaydık", "Ne olurdu?", "Sayısal etki"],
             [["**Kesin J hesabı**",
               "Toplam yolculuk süresi hazır sütundan okunurdu; 24 saati aşanlar 24 saat "
               "kısa görünürdü → yenmediğimiz rakipleri yenmiş sayardık",
               "**154 satır** yanlış; 29'u bizim, ortalama ρ = 487 olan pazarlarda"],
              ["**`b_od` düzeltmesi**",
               "Mevcut tarife ödül tablosunun köşegenine oturmaz, hiçbir şey yapmadan "
               "sıralama ödülü kazanırdı → baseline şişer, iyileşme sahte görünürdü",
               "Pazarların **~%29'u** etkilenirdi"],
              ["**Hafta normalizasyonu**",
               "Aynı fiziksel uçuş iki ayrı karar olayına bölünür, çözücü ona iki farklı "
               "saat atayabilirdi → uygulanamaz tarife",
               "**130** kopya olay"],
              ["**Tekilleştirme**",
               "Birebir özdeş satırlar iki ayrı ürün sayılır, aktarma ödülü iki kez "
               "yazılırdı", "**157** bağlantı"],
              ["**`extra_use`**",
               "ρ'suz pazarların uçakları kapasitede sayılmaz, model gerçekte olmayan "
               "boşluğa uçuş yerleştirirdi", "**79** kova etkileniyor"],
              ["**`full_role_time` ankoru**",
               "Rotasyon ortağının modellenmeyen günlerinde A2 kısıtı hiç kurulmazdı",
               "**Gerçek A2 ihlali** (doğrulayıcı yakaladı)"],
              ["**byday ayrıştırması**",
               "Tam-hafta modeli tek seferde çözülemiyor — HiGHS incumbent bulamıyor",
               "**Hiç çözüm yok**"],
              ["**Tam-hafta cilalama**",
               "Günler-arası koordinasyon kaybı kalırdı ve optimalite kanıtı üretilemezdi",
               "**−14.752** puan + **gap kanıtı yok**"],
              ["**λ cezası**",
               "Çözücü amacı değiştirmeyen kaydırmaları da yapardı (dejenerasyon)",
               "Uçuşların **~%90'ı** sıfır kazanç için kaydırılırdı"],
              ["**Bağımsız doğrulayıcı**",
               "Wdev=90 denemesindeki gerçek A2 ihlali fark edilmezdi",
               "**%5,34** ihlalli olarak teslim edilirdi"]],
             [3.4, 8.0, 5.6], 8.2)),
    ("box", ("Bu tablo neden bu kadar güçlü?",
             "Çünkü her satır **ölçülmüş**. \"İyi iş çıkardık\" demiyoruz; \"şunu yapmasaydık "
             "şu kadar hata olurdu\" diyoruz ve sayı veriyoruz. Bir jüri için bu, ezberlenmiş "
             "bir sunumdan çok daha ikna edicidir.", "ok")),

    # ================================================================= 4
    ("h1", ("4", "Dürüst olalım: neler bizim değil?")),
    ("p", "Bunu söylemek sizi **güçlendirir**, zayıflatmaz. Jüri overclaim'i (abartılı iddia) "
          "hemen yakalar; sınırlarını bilen bir takım güven verir."),
    ("tbl", (["Bizim DEĞİL", "Ne kadarı hazır geldi?", "Bizim kattığımız"],
             [["**HiGHS'in algoritması**",
               "Dallanma-sınırlama, kesme düzlemleri, sezgiseller — tamamı hazır",
               "Ayarları (determinizm, sezgisel bütçesi) ve **çözülebilir bir model** vermek"],
              ["**Pyomo**", "Modelleme dili ve çözücü arayüzü hazır",
               "Modelin kendisi — 1.357 satır formülasyon"],
              ["**Warm-start fikri**",
               "Literatürde var (*fix-and-optimize* ailesi)",
               "Bu probleme uyarlanması, gece-aşan koruma tasarımı, E1 onarımı, bariyer"],
              ["**Standart OR teknikleri**",
               "Azalan getiri, big-M, one-hot kodlama — hepsi bilinen teknikler",
               "**Hangisinin nereye uygulanacağı** ve M'lerin nasıl sıkılaştırılacağı"]],
             [3.6, 6.4, 7.0], 8.4)),
    ("box", ("Jüri \"bunu siz mi buldunuz?\" derse",
             "*\"Teknikler standart yöneylem araştırması araçları — big-M, one-hot kodlama, "
             "azalan getiri, warm-start. Bizim katkımız bu araçların bu probleme nasıl "
             "uygulanacağına dair tasarım kararları: karar biriminin ne olacağı, hangi "
             "değişkenin hiç yaratılmayacağı, M'lerin nasıl sıkılaştırılacağı, çözülemeyen "
             "modelin nasıl ikiye bölüneceği ve sonucun nasıl bağımsız doğrulanacağı.\"*",
             "info")),
]
