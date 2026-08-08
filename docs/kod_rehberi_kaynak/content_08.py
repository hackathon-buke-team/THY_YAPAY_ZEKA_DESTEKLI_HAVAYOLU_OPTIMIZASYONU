# -*- coding: utf-8 -*-
"""Bolum 4 — 08_fullweek_polish.py"""

F = "08_fullweek_polish.py"

ITEMS = [
    ("h1", ("4", "08_fullweek_polish.py — Tam-Hafta Warm-Start Cilalaması")),

    ("box", ("Bu dosya ne yapar?",
             "03'ün güne-göre ürettiği çözümü, **haftanın tamamını kapsayan tek MIP'e** "
             "başlangıç noktası (MIP-start) olarak verir ve HiGHS'in bu noktadan küresel "
             "olarak iyileştirmesini sağlar. Kazancı iki katlıdır: (i) günler-arası "
             "koordinasyon kazanılır, (ii) **global MIP-gap** raporlanabilir — yani greedy "
             "gün zincirinin veremediği *optimalite kanıtı* elde edilir.")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`derived/` + `output/optimized_schedule.csv` (aşama-1 çözümü)"],
              ["Çıktı", "`output/` (iyileşme varsa yeniden yazılır) + "
                        "`reports/fullweek_polish.md`"],
              ["Çalıştırma", "`python src/08_fullweek_polish.py [süre_s] [λ] [Wdev_dk]` — "
                             "`run_all.py` bunu 1800 s ile çağırır"],
              ["Bağımlılık", "`03_model.py` (dinamik import), `pyomo`, `pandas`"],
              ["Süre", "verilen süre sınırı kadar (varsayılan 600 s, teslim koşusunda 1800 s)"]],
             [3.0, 14.0], 8.8)),

    ("h2", "4.1  Neden böyle bir adım gerekiyor?"),
    ("code", (F, 1, 21, "yöntemin gerekçesi ve beş adımı")),
    ("p", "Sorun şudur: `byday`, günleri **sırayla** çözer ve her günün kararı bir sonrakini "
          "kısıtlar (G bandı). Bu bir **greedy zincirdir** — 3. günde alınan bir karar 6. gün "
          "için daha iyi bir seçeneği kapatmış olabilir ve bunu geri alma imkânı yoktur. "
          "Ayrıca greedy bir yöntem \"bulduğum çözüm optimumdan en fazla %X uzak\" diyemez."),
    ("box", ("Warm-start matheuristiği nedir?",
             "Literatürde \"fix-and-optimize / warm-start\" ailesine giren bir yöntemdir: "
             "hızlı bir sezgiselle **uygun** bir çözüm bulunur, sonra bu çözüm tam modelin "
             "branch-and-bound arayışına *incumbent* (eldeki en iyi) olarak verilir. Çözücü "
             "artık sıfırdan çözüm aramaz — elindeki iyi noktayı **iyileştirmeye** çalışır ve "
             "aynı anda üst sınırı (bound) daraltarak gap üretir.", "info")),
    ("code", (F, 22, 42, "G düzenliliğinin özel kurulumu ve Wdev deneyi")),
    ("p", "Kritik bir uyum ayrıntısı: **G kısıtı bu betikte farklı kurulur.** Nedeni, "
          "bağımsız doğrulayıcının (05) G'yi \"ilk günün yerleşimi çapadır, sonraki günler "
          "±Xdev\" biçiminde denetlemesidir. 08 aynı kısıtı **birebir aynı biçimde** kurar "
          "— ama çapayı da değişken bırakarak (çapa da kayabilir) günler-arası eşgüdüme "
          "serbestlik tanır."),
    ("box", ("Wdev genişletme deneyi ve neden iptal edildi",
             "Docstring, `Wdev_dk > 60` verilirse pencere genişletme denemesi yapılabileceğini "
             "söyler. Wdev = 90 denendiğinde sonuç %5.34'e çıktı — **ama 05 doğrulayıcısı "
             "gerçek bir A2 ihlali yakaladı**. Sonuç iptal edildi ve Wdev = 60'a dönüldü. "
             "Daha yüksek bir rakam uğruna doğrulanmamış bir çözüm teslim edilmedi; bu, "
             "projenin en net karakter göstergelerinden biridir.", "warn")),

    ("h2", "4.2  03'ü modül olarak yüklemek"),
    ("code", (F, 44, 69, "dinamik import ve kısayollar")),
    ("p", "`03_model.py` normal `import` ile yüklenemez — Python modül adları rakamla "
          "başlayamaz. Çözüm `importlib.util` ile **dosya yolundan** yüklemektir "
          "(62–64). Bundan sonra `M3.build_instance()`, `M3.CFG`, `M3.solve_model()` gibi "
          "her şey erişilebilir."),
    ("box", ("Bu neden değerli?",
             "Amaç fonksiyonu, kısıtlar ve çözücü ayarları **kopyalanmaz, paylaşılır**. "
             "Yani 08, 03'ün modelini kelimesi kelimesine aynı kurar; yalnızca *çözüm "
             "yöntemi* değişir. \"Kurallara dokunulmadı, yalnız yöntem güçlendi\" iddiası "
             "böyle savunulabilir hâle gelir.", "ok")),
    ("p", "Üç kısayol lambda'sı: `HHMM` (dakika → \"08:30\"), `ROL` (\"dep\"→\"kalkış\"), "
          "`TOD` (mutlak dakika → saat-içi dakika)."),

    ("h2", "4.3  `load_phase1()` — aşama-1 çözümünü okumak"),
    ("code", (F, 72, 101, "kaydırmalar, sunum listesi ve muafiyetler")),
    ("p", "Dört şey okunur:"),
    ("tbl", (["Okunan", "Kaynak", "Ne için?"],
             [["`shift`", "`optimized_schedule.csv`",
               "(gün, uçuş, rol, eski saat) → değişim dakikası"],
              ["`offered`", "`selected_connections.csv`",
               "byday'in gerçekten **sunduğu** bağlantı kümesi"],
              ["`byday_total`", "`market_results.csv`",
               "byday'in kayıtlı saf rekabetçilik toplamı — yeniden yazma bariyerinin eşiği"],
              ["`exempt`", "`g_band_exemptions.csv`", "byday'in belgeli G muafiyetleri"]],
             [2.8, 5.4, 8.8], 8.6)),
    ("box", ("`offered` neden uygunluktan türetilemez? (docstring 77–80)",
             "\"Boşluk 60–300 arasındaysa sunuluyor demektir\" varsayımı **yanlıştır**. "
             "byday, E1 yönsel dengesini sağlamak için uygun bağlantıların bir kısmını "
             "**bilinçli olarak sunmaz** (~265 aday). Warm-start'ta y'yi uygunluktan "
             "türetmek, E1'i ihlal eden bir başlangıç noktası üretir — HiGHS bunu reddeder ve "
             "warm-start hiç işe yaramaz. Bu yüzden y, byday'in gerçek sunum listesinden "
             "alınır.", "warn")),
    ("p", "Tarife dosyası yoksa fonksiyon `M3.run_byday(...)` çağırıp aşama-1'i kendisi "
          "koşturur — betik tek başına da çalışabilir."),

    ("h2", "4.4  `pin_merged_events()` — gün-görünümü kopyalarının sabitlenmesi"),
    ("code", (F, 104, 142, "birleşen olayların byday saatine kilitlenmesi")),
    ("p", "İnce ama gerçek bir tutarsızlık kaynağı: aynı fiziksel zaman damgası birden çok "
          "operasyon gününde kayıtlı olabilir. Tam-hafta ekseninde bu **tek bir olaya** "
          "birleşir; ama byday ve 05 doğrulayıcısı onu gün-görünümü başına **ayrı** "
          "değerlendirir. Bu uyumsuzluk iki şekilde çözülür:"),
    ("num", ["Birleşik **ayarlanabilir** olay, byday'in verdiği saate **sabitlenir** "
             "(`cands = [t*]`, satır 139). Çözücü onu oynatamaz → öteki gün-görünümünün "
             "(modelde kurulmayan) A2/F bağları riske girmez.",
             "Olayın **tüm gün görünümleri** `inst.view_days`'e kaydedilir (141). Tarife "
             "çıktısına her görünüm için ayrı satır yazılır → doğrulayıcı iki günü de tutarlı "
             "görür."]),
    ("p", "Yorum bu veride tam **1** böyle olay olduğunu söylüyor (uçuş 1304 varışı). Tek bir "
          "satır için yazılmış 39 satırlık kod — ama o tek satır doğrulamayı FAIL'e "
          "düşürebilirdi."),

    ("h2", "4.5  `warm_times()` — başlangıç noktasının zamanları"),
    ("code", (F, 145, 162, "her olayın aşama-1 saati")),
    ("p", "Her olay için `t*[eid]` hesaplanır: sabitler mevcut saatlerinde, ayarlanabilirler "
          "`cur + değişim`. İki emniyet kontrolü var:"),
    ("bul", ["Bir ayarlanabilir olay tarife dosyasında **bulunamazsa** `missing` listesine "
             "eklenir. `main()` bunu görürse \"byday çıktısı bayat\" diyip çıkar — eski bir "
             "çözümle yeni bir model karıştırılmaz.",
             "Kaydırma **pencere dışındaysa** `ValueError` fırlatılır. Bu, 03 ile 08 arasında "
             "Wdev/Δ uyumsuzluğunun sessizce geçmesini engeller."]),

    ("h2", "4.6  `add_star_G()` — doğrulayıcı-birebir G kısıtı"),
    ("code", (F, 165, 206, "ilk-gün çapalı ±Xdev bandı")),
    ("p", "Her `(uçuş, rol)` grubunda **ilk günün olayı çapadır** ve sonraki her gün için iki "
          "kısıt yazılır: `θ'_gün − θ'_çapa ∈ [−Xdev, +Xdev]`. Çapanın kendisi de bir "
          "değişken olduğu için tüm grup birlikte kayabilir — byday'in sabit bandına göre "
          "**daha fazla serbestlik**."),
    ("p", "Kısıt yalnız üç koşul birden sağlanırsa kurulur (194–196):"),
    ("num", ["Çapa ve olay günü **tekil** olmalı (anomali olay grupları determinizm için "
             "muaf tutulur).",
             "Pencereler ortak banda yetişebilmeli: `|Δcur| ≤ 2·Wdev + Xdev`.",
             "**Warm-start noktası kısıtı sağlamalı**: byday zaten bandın dışında bıraktıysa, "
             "kısıt eklemek başlangıç noktasını geçersiz kılardı."]),
    ("box", ("\"Kısıtlı → geçer, kısıtsız → muaf\" tasarımı",
             "Kurulmayan her bağ, doğrulayıcı formatında **belgeli muafiyet** olarak "
             "`new_ex` listesine yazılır ve `g_band_exemptions.csv`'ye eklenir. Böylece "
             "05'te hiçbir bağ \"bant dışı\" olarak FAIL veremez: ya kısıtlanmıştır (geçer) "
             "ya da muaf olarak ilan edilmiştir. Sessiz ihlal imkânsız hâle getirilmiştir.",
             "ok")),

    ("h2", "4.7  `set_start_values()` — MIP-start'ın yazılması"),
    ("code", (F, 209, 235, "x ve y değerleri")),
    ("p", "`03.set_warmstart`'ın genelleştirilmiş hâli. `x` byday kovasına, `y` ise byday'in "
          "**gerçek sunum listesine** göre atanır. Ek bir kontrol var (232–234): "
          "`pin_merged_events` ile dondurulmuş bir olay yüzünden bir bağlantı artık pencerede "
          "değilse, o bağlantı sunumdan düşürülür ve sayılır."),
    ("code", (F, 236, 264, "E1 onarımı")),
    ("p", "Düşürmeler bir yönün bağlantı sayısını azaltıp warm noktada E1 dengesini bozabilir. "
          "Bu döngü, denge sağlanana kadar **fazla olan yönden** sunum geri çeker. Seçim "
          "deterministiktir (en yüksek indeksli) — aynı girdi her makinede aynı sonucu verir."),
    ("box", ("Neden bu kadar uğraşılıyor?",
             "HiGHS, MIP-start olarak verilen noktayı **uygunluk açısından denetler**. Tek bir "
             "kısıt ihlali varsa noktayı tümüyle reddeder ve çözücü sıfırdan başlar — yani "
             "08'in tüm varlık sebebi ortadan kalkar. Bu yüzden başlangıç noktasının "
             "**kusursuz uygun** olması gerekir.", "warn")),
    ("code", (F, 265, 291, "z, w, β, γ değerlerinin tutarlı yazılması")),
    ("p", "Kalan tüm ikili değişkenler y'den türetilir: `z` monoton doldurma, `w`/`β` rakip "
          "yenme göstergeleri, `γ` yenilen sayısı seçicisi. Sıra ve tutarlılık, 03'teki "
          "`set_warmstart` ile birebir aynıdır (E2/B2 blokları yoktur çünkü tam ölçekte "
          "kapalıdırlar)."),

    ("h2", "4.8  Raporlama yardımcıları"),
    ("code", (F, 294, 319, "totals_by_day — gün kırılımı")),
    ("p", "Tam-hafta çözümünde \"gün\" artık bir çözüm birimi değil, sadece bir **etikettir** "
          "(`k[1]`). Bu fonksiyon hem optimize hem baseline değerini gün gün toplar, böylece "
          "`results_summary.md`'nin gün tablosu byday ile aynı formatta kalır."),
    ("code", (F, 322, 353, "collect_market_outputs_week")),
    ("p", "`03.collect_market_outputs`'un çok-günlü karşılığı. Tek fark: gün bilgisi "
          "parametreden değil, pazar-gün anahtarından (`k[1]`) alınır. Üretilen satır formatı "
          "**birebir aynıdır** — bu yüzden 05 doğrulayıcısı hangi aşamanın ürettiğini "
          "bilmeden çalışabilir."),
    ("code", (F, 356, 394, "a2x_check — gece-aşan rotasyon doğrulaması")),
    ("p", "`run_byday` içindeki A2 kontrolünün tam-hafta çözümü üzerindeki karşılığı. Aynı "
          "artefakt/YENİ-ihlal ayrımını yapar ve üç sayaç döndürür."),

    ("h2", "4.9  `main()` — akışın tamamı"),
    ("code", (F, 398, 418, "sıralama tuzağı ve CFG kurulumu")),
    ("box", ("400–402'deki yorum bir hata ayıklama hikâyesidir",
             "`load_phase1` gerektiğinde `run_byday` çağırır — ve `run_byday`, CFG'yi "
             "**mutasyona uğratır** (`days` son güne düşer, `time_limit` ve `mip_gap` "
             "değişir). Bu yüzden CFG kurulumu aşama-1'den **sonra** yapılmalıdır. Sırayı "
             "ters çevirmek, sessizce yalnız son günü çözen bir betik üretirdi.", "warn")),
    ("p", "CFG'de üç kritik ayar:"),
    ("bul", ["`G_regularity = False` — G'yi bu betik kendi (doğrulayıcı-birebir) biçiminde "
             "kuracak.",
             "`warmstart = True` — appsi katmanı bunu HiGHS `setSolution` MIP-start'ına çevirir.",
             "`highs_extra_options = {\"mip_heuristic_effort\": 0.3}` — varsayılan 0.05'ten "
             "yükseltilir. Warm-start'lı büyük MIP'te iyileştirmeler çoğunlukla incumbent "
             "çevresinde çalışan sezgisellerden (RINS vb.) gelir; onlara daha çok bütçe "
             "verilir."]),
    ("code", (F, 420, 435, "örnek kurulumu ve bayatlık kontrolü")),
    ("p", "Tam-hafta örneği kurulur, gece-aşan koruma sınırları **tüm günler için** düzleştirilerek "
          "eklenir (423–424), gün-görünümü kopyaları sabitlenir. Ardından `warm_times` "
          "çağrılır; eksik olay varsa betik **1 ile çıkar** ve kullanıcıya byday'i yeniden "
          "koşmasını söyler."),
    ("code", (F, 437, 455, "model, G kısıtları ve başlangıç noktasının ölçülmesi")),
    ("p", "Konsola basılan iki satır tanı açısından çok değerlidir:"),
    ("bul", ["`MIP-start: SAF=… cezalı=… (baseline …, Δ=…)` — başlangıç noktasının kalitesi.",
             "`warm − byday = …` — **0'a yakın olmalıdır**. Değilse, warm noktanın "
             "kurulumunda bir eşleşme kaybı var demektir ve bu hemen görülür."]),
    ("code", (F, 457, 474, "çözüm ve iyileşme ölçümü")),
    ("p", "**461–464:** Çözüm yüklenemezse betik **0 ile çıkar**, 1 ile değil. Neden? Çünkü "
          "byday çıktısı hâlâ geçerlidir — cilalama isteğe bağlı bir iyileştirmedir ve "
          "başarısızlığı uçtan uca koşuyu durdurmamalıdır."),
    ("code", (F, 475, 484, "yeniden yazma bariyeri ve A2 kontrolü")),
    ("box", ("İki koşullu bariyer",
             "`output/` dosyaları **yalnız** şu iki koşul birlikte sağlanırsa yeniden yazılır:\n"
             "**(1)** `pol_pure > byday_total + 0.5` — cilalanmış çözüm byday'in **kayıtlı "
             "gerçek toplamını** anlamlı biçimde geçmeli. Karşılaştırma warm noktaya göre "
             "değil byday'in kaydına göre yapılır; warm nokta eşleşme kayıplarıyla düşük "
             "olabilir ve kötü bir çözümle iyi bir çıktıyı ezmek yasaktır.\n"
             "**(2)** `a2x_viol == 0` — hiçbir yeni fiziksel rotasyon ihlali doğmamalı.",
             "ok")),
    ("code", (F, 485, 522, "çıktıların yeniden yazılması")),
    ("p", "İyileşme varsa tüm çıktılar aynı formatta yeniden üretilir. **496:** birleşik "
          "olayların her gün görünümü için ayrı satır yazılır — doğrulayıcı iki günü de aynı "
          "kaydırmayla görsün diye. Yazma işi `M3.write_outputs` ile yapılır, yani format "
          "kaymaz."),
    ("code", (F, 523, 547, "sonuç özetinin güncellenmesi")),
    ("p", "`results_summary.md` iki aşamalı hattı yansıtacak şekilde düzeltilir: komut satırı "
          "`03 byday → 08` olarak güncellenir, başlık \"+ tam-hafta cilalaması\" olur ve "
          "sonuna aşama-1 → aşama-2 karşılaştırması ile **global MIP-gap** eklenir."),
    ("code", (F, 548, 552, "iyileşme yoksa ne olur?")),
    ("p", "Bariyer geçilmezse `output/` dosyalarına **dokunulmaz** ve nedeni açıkça yazılır: "
          "\"A2 gece-aşan yeni ihlal\" veya \"anlamlı iyileşme yok\". byday çıktısı geçerli "
          "kalır, koşu devam eder. Yani bu adım **asla zarar veremez** — en kötü ihtimalle "
          "hiçbir şey yapmaz."),
    ("code", (F, 553, 589, "koşu raporu")),
    ("p", "`reports/fullweek_polish.md` bir tablo hâlinde her şeyi kayda geçirir: gün sayısı, "
          "pencere, ikili değişken sayısı, G bağ ve muafiyet sayıları, aşama-1 toplamı, "
          "MIP-start değeri, cilalanmış değer, baseline, iyileşme, kaydırma, **global "
          "MIP-gap**, süre, A2 doğrulama, ve `output/` güncellendi mi."),
    ("box", ("Global MIP-gap neden bu kadar vurgulanıyor?",
             "Çünkü greedy bir yöntemin **veremediği** tek şey odur: *\"tam-hafta modelinin "
             "gerçek optimumu, raporladığım değerin en fazla %X üzerindedir.\"* Bu, "
             "\"iyi bir çözüm buldum\" ile \"bulduğum çözümün optimale ne kadar yakın "
             "olduğunu kanıtlayabiliyorum\" arasındaki farktır — ve optimizasyon "
             "yarışmalarında tam olarak bu fark değerlendirilir.", "info")),
    ("code", (F, 592, 596, "komut satırı argümanları")),
    ("p", "Üç isteğe bağlı argüman: süre sınırı (saniye), λ, Wdev. `run_all.py` bunu "
          "`08_fullweek_polish.py 1800` olarak çağırır."),
]
