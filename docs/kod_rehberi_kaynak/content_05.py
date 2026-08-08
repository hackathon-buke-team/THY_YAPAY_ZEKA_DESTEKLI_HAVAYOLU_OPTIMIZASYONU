# -*- coding: utf-8 -*-
"""Bolum 5 — 05_validate_solution.py"""

F = "05_validate_solution.py"

ITEMS = [
    ("h1", ("5", "05_validate_solution.py — Bağımsız Doğrulayıcı")),

    ("box", ("Bu dosya ne yapar?",
             "`output/` altındaki çözümü, **modelin içinden hiç geçmeden**, yalnız `derived/` "
             "veri katmanı üzerinden yeniden hesaplar ve her kısıtı tek tek denetler. Bir "
             "tane bile FAIL varsa **1 ile çıkar** ve `run_all.py` koşuyu durdurur. Muhasebede "
             "buna **çift kayıt** denir: aynı sayıya iki bağımsız yoldan varmak.")),
    ("img", ("f13_cift_kayit.png", "Şekil 5.1 — Üreten kod ile doğrulayan kod ayrıdır.")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`derived/` (veri) + `output/` (çözüm) — **`src/03_model.py` DEĞİL**"],
              ["Çıktı", "`reports/validation_report.md`"],
              ["Çalıştırma", "`python src/05_validate_solution.py`"],
              ["Çıkış kodu", "**0** = tüm kontroller PASS · **1** = en az bir FAIL"],
              ["Bağımlılık", "`pandas`, `numpy` — *Pyomo yok, çözücü yok*"],
              ["Süre", "birkaç saniye"]],
             [3.0, 14.0], 8.8)),

    ("h2", "5.1  Doğrulama listesi"),
    ("code", (F, 1, 30, "hangi kontroller yapılıyor?")),
    ("p", "Docstring, kontrol edilecek her kısıtı `docs/model_formulation.md` ile aynı "
          "harflerle sıralar. Bu, jürinin \"şu kısıt doğrulandı mı?\" sorusunu tek bakışta "
          "yanıtlamasını sağlar."),

    ("code", (F, 32, 48, "import'lar — burada ne YOK'a dikkat")),
    ("p", "Bu 17 satırın en anlamlı yanı **içermediği** şeydir: ne `pyomo`, ne `highspy`, ne "
          "de `03_model.py`. Doğrulayıcı yalnız `pandas` ve `numpy` kullanır. Modeli "
          "kuran/çözen hiçbir kod bu dosyaya girmez — bağımsızlığın ilk ve en görünür "
          "işareti budur."),

    ("h2", "5.2  En önemli tasarım kararı: sabitlerin tekrar yazılması"),
    ("code", (F, 50, 66, "03'ten import ETMEYEN sabitler")),
    ("box", ("Neden `from model03 import WDEV` yazılmadı?",
             "Çünkü o zaman doğrulama **bağımsız olmazdı**. 03'teki bir sabit yanlış olsaydı, "
             "05 aynı yanlış sabitle kontrol eder ve PASS verirdi — yani hata kendini "
             "doğrulardı. Sabitleri elle tekrar yazmak, ikisinin **birbirinden bağımsız iki "
             "kayıt** olmasını sağlar. Uyuşmazlık olursa doğrulama FAIL verir; bu bir kusur "
             "değil, sistemin **çalıştığının kanıtıdır**.", "ok")),
    ("h3", "Kodun içine gömülmüş bir hata ayıklama günlüğü (satır 52–60)"),
    ("p", "Yukarıdaki bloğun ortasındaki dokuz satırlık yorum, bu dosyanın **gerçekten iş "
          "gördüğünün** kanıtıdır. Anlattığı olay şudur:"),
    ("num", ["`08_fullweek_polish.py` Wdev = 90 ile denendi ve sonuç %5.34'e çıktı — cazip.",
             "Doğrulayıcı **gerçek bir A2 ihlali** yakaladı: uçuş 2200/2201, gün 2.",
             "Kök neden bulundu: 2201'in o günkü varışı ρ'su olmayan bir pazara (KCM–AGP) "
             "ait olduğu için `build_instance()` o olayı hiç oluşturmuyordu → rotasyon "
             "ortağıyla A2 kısıtı o gün hiç kurulmuyordu.",
             "Wdev = 60'ta çözücü bu boşluğu tetikleyecek kadar kaydırma yapmamıştı; Wdev = 90 "
             "tetikledi.",
             "**Karar: yüksek rakam iptal, Wdev = 60'a dönüldü.** Kök neden ise 03'te "
             "`full_role_time` evren-ankoru ile kalıcı olarak kapatıldı (bkz. 3.4)."]),

    ("h2", "5.3  Yardımcılar ve `Checks` sınıfı"),
    ("code", (F, 69, 84, "okuma ve ızgara yuvarlaması")),
    ("p", "`snap10()` bilinçli olarak 03'teki `snap` ile **aynı yuvarlama kuralını** kullanır "
          "(Python `round`). Farklı bir yuvarlama, gerçek olmayan tutarsızlıklar üretirdi — "
          "bağımsızlık, *aynı tanımı* kullanmayı engellemez; *aynı kodu* kullanmayı engeller."),
    ("code", (F, 87, 102, "PASS/FAIL toplayıcı")),
    ("p", "Projedeki ikinci (ve son) sınıf. Üç görevi vardır:"),
    ("bul", ["`add(name, scope, ok, detail)` — kontrolü kaydeder, ekrana basar ve `ok` "
             "yanlışsa `failed` bayrağını kaldırır.",
             "`note(...)` — PASS/FAIL olmayan bilgi satırları (örneğin olay eşleme sayıları) "
             "için.",
             "`rows` listesi — sonunda markdown tablosuna dönüşür."]),

    ("h2", "5.4  Veriyi ve çözümü yükleme"),
    ("code", (F, 105, 146, "iki katman + kaydırma sözlüğü")),
    ("p", "Kilit yapı `shift` sözlüğü ve `opt_dt()` fonksiyonudur:"),
    ("box", ("Optimize saati nasıl bulunuyor?",
             "Doğrulayıcı çözücüden hiçbir şey almaz. Elinde yalnız (a) `derived/`'deki "
             "**mevcut** saatler ve (b) `optimized_schedule.csv`'deki **değişim dakikaları** "
             "vardır. `opt_dt()` bu ikisini birleştirir: `optimize = snap(mevcut) + değişim`. "
             "Tarifede kaydı olmayan bir olay **sabit** kabul edilir (değişim = 0). Yani "
             "doğrulayıcı çözümü sıfırdan yeniden inşa eder.", "info")),

    ("h2", "5.5  Kontrol A1 — ızgara, pencere ve saat aritmetiği"),
    ("code", (F, 147, 160, "üç ayrı A1 kontrolü")),
    ("tbl", (["Kontrol", "Ne doğrular?", "Beklenen"],
             [["Izgara", "Her değişim 10'un katı mı?", "`degisim_dk % 10 == 0`"],
              ["Pencere", "Hiçbir kaydırma ±60 dk'yı aşıyor mu?", "`|degisim_dk| ≤ 60`"],
              ["Saat aritmetiği", "`eski_IST + değişim == yeni_IST` mi?",
               "0 tutarsız satır"]],
             [3.2, 8.0, 5.8], 8.8)),
    ("p", "Üçüncü kontrol basit görünür ama önemlidir: çıktı dosyasındaki `yeni_IST` sütunu, "
          "`eski_IST` ve `degisim_dk` ile **tutarlı** olmalıdır. Bir yazma hatası bu kontrolde "
          "yakalanır."),

    ("h2", "5.6  Olay tablosunun yeniden inşası"),
    ("code", (F, 162, 176, "varış ve kalkış olaylarının birleştirilmesi")),
    ("p", "`tk_connections.csv`'den varış ve kalkış olayları ayrı ayrı çıkarılıp "
          "`drop_duplicates` ile tekilleştirilir — 03'teki `events` sözlüğünün **bağımsız "
          "karşılığı**. `note` satırı kaç olayın tarife dosyasıyla eşleştiğini (ayarlanabilir) "
          "ve kaçının sabit olduğunu bildirir; bu sayılar 03'ün konsol çıktısıyla "
          "karşılaştırılabilir."),

    ("h2", "5.7  Kontrol F — kova kapasitesi"),
    ("code", (F, 178, 188, "her gün × 10 dk kova doluluğu")),
    ("p", "Kritik nokta: gruplama `opt` (optimize saat) üzerinden yapılır, `cur` üzerinden "
          "değil. Yani **çözümün ürettiği** dolulukları sayar. Ayrıca **tüm** TK uçuşları "
          "sayılır — sabitler, ayarlananlar ve amaç evreni dışındakiler. Bu, 03'ün "
          "`extra_use` mekanizmasının doğru çalışıp çalışmadığının bağımsız testidir."),

    ("h2", "5.8  Kontrol A2 — rotasyon, gerçek zaman ekseninde"),
    ("code", (F, 190, 225, "gece-aşan turlar dahil doğrulama")),
    ("p", "Doğrulayıcının en değerli kontrolü budur, çünkü **modelin göremediği** bir şeyi "
          "görür: byday ayrıştırmasında gün h'nin kalkışı ile gün h+1'in dönüşü aynı modelde "
          "yer almaz. Burada ikisi de dosyadan okunur ve gerçek zaman ekseninde karşılaştırılır."),
    ("p", "Dönüş örneğini **mevcut tarife** belirler (206–213): kalkıştan sonraki ilk "
          "varış — önce aynı gün, yoksa ertesi gün. Bu, uçağın gerçek eşleşmesinin en "
          "makul yorumudur."),
    ("tbl", (["Sonuç", "Anlamı", "FAIL mı?"],
             [["`a2_base`", "Mevcut tarife de bu turu sağlamıyor → eşleşme artefaktı",
               "**Hayır** — ama sayılır ve raporlanır"],
              ["`a2_new`", "Mevcut sağlıyordu, optimizasyon bozdu",
               "**Evet** — 0 olmalıdır"]],
             [2.6, 9.2, 5.2], 8.8)),
    ("code", (F, 227, 244, "aynı-gün model çapasının korunması")),
    ("p", "İkinci A2 kontrolü modelin **kendi kuralını** denetler: aynı-gün turlarda optimize "
          "tur ≥ `min(brief-exact, mevcut tur)` olmalı. Yani model, kendi kurduğu kısıta "
          "gerçekten uymuş mu?"),

    ("h2", "5.9  Kontrol G — düzenlilik bandı"),
    ("code", (F, 246, 272, "ilk-gün çapalı ±Xdev denetimi")),
    ("p", "Her `(uçuş, rol)` grubunda ilk günün optimize yerleşimi bant merkezi (`c0`) kabul "
          "edilir; sonraki günler `|yerleşim − c0| ≤ Xdev` sağlamalı. Üç istisna kategorisi "
          "vardır ve **hepsi ayrı ayrı sayılır**:"),
    ("tbl", (["Kategori", "Koşul", "Nasıl işlenir?"],
             [["Belgeli muafiyet", "`(gün, uçuş, rol) ∈ g_band_exemptions.csv`",
               "`g_exempt++`, atlanır — rotasyon güvenliği bandın önündedir"],
              ["Yapısal atlama", "`|tod(cur) − c0| > Wdev + Xdev`",
               "`g_skip++`, atlanır — pencere banda **fiziksel olarak** yetişemiyor"],
              ["Denetlenen", "Diğer her şey", "`g_chk++`; band dışıysa `g_bad++` → FAIL"]],
             [3.2, 6.4, 7.4], 8.4)),
    ("box", ("Muafiyet listesini modelin kendisi yazıyor — bu bir açık mı?",
             "Hayır, çünkü liste **dosyaya yazılır ve raporlanır**. Jüri "
             "`output/g_band_exemptions.csv`'yi açıp kaç muafiyet olduğunu görebilir. "
             "Alternatif — muafiyetleri hiç bildirmemek — çok daha kötü olurdu: o zaman G "
             "kısıtının nerede uygulanmadığı **bilinemezdi**. Şeffaflık, gizli gevşetmeden "
             "iyidir.", "info")),

    ("h2", "5.10  Kontrol B1 — bağlantı tutarlılığı"),
    ("code", (F, 274, 313, "üç katmanlı çapraz kontrol")),
    ("p", "Seçilen her bağlantı için üç şey doğrulanır:"),
    ("num", ["**Boşluk penceresi:** `60 ≤ bosluk_dk ≤ 300`.",
             "**J tutarlılığı:** `legsum_min + bosluk_dk == J_dk` (veriden okunan legsum ile).",
             "**Tarife ↔ bağlantı tutarlılığı:** `selected_connections.csv`'deki `IST_varis` "
             "ve `IST_kalkis` saatleri, `optimized_schedule.csv`'deki kaydırmalardan "
             "hesaplananla **birebir** eşleşmeli."]),
    ("p", "Üçüncüsü en güçlüsüdür: iki farklı çıktı dosyasının birbiriyle çeliştiğini yakalar. "
          "Bir dosyaya doğru, diğerine yanlış yazan bir hata burada FAIL verir."),
    ("p", "**289–302:** Anomali olaylar için ince bir esneklik var — aynı anahtarda farklı "
          "saatli birden çok satır olabileceğinden, **herhangi biriyle** tutarlıysa geçerli "
          "sayılır."),

    ("h2", "5.11  Kontroller C, D ve amaç"),
    ("code", (F, 315, 364, "ödüllerin ve katkıların yeniden hesabı")),
    ("p", "Her pazar-gün satırı için beş şey yeniden hesaplanır ve dosyadakiyle karşılaştırılır:"),
    ("tbl", (["Kontrol", "Yeniden hesap", "Hata koşulu"],
             [["Bağlantı sayısı",
               "`selected_connections.csv`'den sayılan n = `market_results`'taki n mi?",
               "`bad_cnt`"],
              ["**C** aktarma ödülü", "`Σ (½)^(j−1)`, j = 1..n", "`bad_c`"],
              ["**D** yenilen rakip",
               "Pazarın en iyi optimize J'si ≤ T_comp olan rakip sayısı",
               "`over_beat` (fazla-beyan)"],
              ["**D** sıralama ödülü", "lookup'tan `W(N, b_od, s)`, `s = clip(N−beat, 1, N)`",
               "`bad_rank`"],
              ["Amaç katkısı", "`ρ × (aktarma + sıralama)`", "`bad_katki`"]],
             [3.6, 8.0, 5.4], 8.4)),
    ("box", ("Fazla-beyan ile eksik-beyan neden farklı muamele görüyor?",
             "**Fazla-beyan** (`over_beat`) = dosyada yazandan az rakip gerçekten yenilmiş → "
             "amaç değeri **şişirilmiş** → gerçek hata, FAIL.\n"
             "**Eksik-beyan** (`under_beat`) = gerçekte yenilmiş ama çözücü β göstergesini "
             "bağlamamış → amaç değeri **olduğundan küçük** görünüyor → hata değil, "
             "ihtiyatlılık. Sadece not edilir.\n"
             "Bu asimetri bilinçlidir: kendi lehimize olan sapmalar hata sayılır, aleyhimize "
             "olanlar sayılmaz.", "ok")),

    ("h2", "5.12  Kontrol E1"),
    ("code", (F, 366, 380, "yön-çifti dengesi")),
    ("p", "`market_results.csv`'den her yön ve tersi eşleştirilir, `|n_od − n_do| ≤ "
          "0.20·(n_od + n_do)` denetlenir. `seen` kümesi her çiftin bir kez sayılmasını "
          "sağlar."),

    ("h2", "5.13  Baseline'ın tamamen sıfırdan hesaplanması"),
    ("code", (F, 382, 406, "output/'a hiç bakmadan baseline")),
    ("p", "Bu blok `output/` klasörüne **hiç bakmaz**. Yalnız `derived/`'den, mevcut tarifenin "
          "amaç değerini baştan hesaplar: pencere içindeki bağlantılar, azalan getiri ödülü, "
          "en iyi J'nin yendiği rakipler, sıralama ödülü."),
    ("p", "**403–405** satırı dikkat çekicidir: baseline için `b == s` olarak alınır — yani "
          "mevcut tarife lookup tablosunun **köşegenine** oturur ve \"değişim yok\" nötr "
          "referansını alır. Bu, 03'teki `b_od` tanımının bağımsız teyididir."),
    ("code", (F, 408, 431, "raporlanan sayılarla karşılaştırma")),
    ("p", "`results_summary.md` dosyası **regex ile** okunur ve raporlanan OPTIMIZE/BASELINE "
          "sayıları çekilir. Üç karşılaştırma yapılır:"),
    ("bul", ["`market_results` toplamı ↔ bağımsız yeniden hesap (fark < 5.0 olmalı)",
             "`market_results` toplamı ↔ `results_summary.md`'de **raporlanan** OPT",
             "Bağımsız baseline ↔ raporlanan BASELINE"]),
    ("box", ("Bu üçlü kontrol neyi kapatıyor?",
             "Bir sonucun üç yerde birden yanlış olması gerekir ki fark edilmesin: çözüm "
             "dosyalarında, özet raporunda ve bağımsız hesapta. Pratikte bu, \"raporda yazan "
             "sayı ile dosyadaki veri farklı\" tipi hataları **imkânsız** hâle getirir.",
             "info")),

    ("h2", "5.14  Raporun yazılması ve çıkış kodu"),
    ("code", (F, 433, 466, "markdown tablo ve genel sonuç")),
    ("p", "Tüm kontroller bir markdown tablosuna dökülür ve `reports/validation_report.md` "
          "yazılır. Rapor sonunda iki kavram açıkça tanımlanır (ihtiyatlı eksik-beyan ve "
          "A2 eşleşme artefaktı) — okuyucu bu terimlerle raporda karşılaştığında ne demek "
          "olduğunu bilir."),
    ("code", (F, 469, 470, "sys.exit ile çıkış kodu")),
    ("box", ("`sys.exit(main())` — tek satırın gücü",
             "`main()` FAIL varsa 1 döndürür. `sys.exit(1)` ise işletim sistemine \"bu betik "
             "başarısız oldu\" der. `run_all.py` bu kodu okur ve **koşuyu durdurur**. Yani "
             "doğrulama yalnızca bir rapor değil, boru hattının içine gömülmüş bir "
             "**kalite kapısıdır**: doğrulanmamış bir çözüm için figür bile üretilmez.",
             "ok")),
]
