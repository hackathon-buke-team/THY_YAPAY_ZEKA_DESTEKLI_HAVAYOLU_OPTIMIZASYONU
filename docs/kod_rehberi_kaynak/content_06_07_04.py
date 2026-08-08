# -*- coding: utf-8 -*-
"""Bolum 6-7-8-9 — 06_make_figures, 07_sensitivity, 04_export_docs, run_all."""

F6 = "06_make_figures.py"
F7 = "07_sensitivity.py"
F4 = "04_export_docs.py"
FR = "run_all.py"

ITEMS = [
    # ================================================================= 06
    ("h1", ("6", "06_make_figures.py — Rapor Figürleri")),
    ("box", ("Bu dosya ne yapar?",
             "`output/` çıktılarını okuyup teknik rapora girecek **dört PNG figürü** üretir. "
             "Hiçbir hesap yapmaz, hiçbir dosyayı değiştirmez — yalnız görselleştirir. "
             "Eksik girdi varsa o figürü atlar ve nedenini yazar (koşu durmaz).")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`output/results_summary.md`, `optimized_schedule.csv`, "
                        "`market_results.csv`, `sweep_results.csv` (ops.)"],
              ["Çıktı", "`docs/figures/*.png` — 4 dosya"],
              ["Çalıştırma", "`python src/06_make_figures.py`"],
              ["Bağımlılık", "`matplotlib`, `pandas`"]],
             [3.0, 14.0], 8.8)),

    ("h2", "6.1  Kurulum ve palet"),
    ("code", (F6, 1, 32, "docstring, Agg arka ucu ve yollar")),
    ("p", "Docstring dört figürün ne olduğunu tek bakışta verir ve stil tercihini de yazar: "
          "*tek/iki renk, çekinik ızgara, doğrudan etiket*. Yani figürlerin görünümü de "
          "belgelenmiş bir karardır, rastgele değil."),
    ("p", "`matplotlib.use(\"Agg\")` satırı `pyplot` import'undan **önce** gelmelidir: Agg, "
          "ekran gerektirmeyen dosyaya-çizim arka ucudur. Bu olmadan betik ekransız bir "
          "sunucuda veya CI ortamında çöker."),
    ("code", (F6, 34, 48, "renk paleti ve global stil")),
    ("p", "Palet bilinçli olarak **dardır**: tek ana renk (mavi) ve kutupluluk için "
          "(iyileşme/gerileme) ikinci bir renk (kırmızı). Gri tonları metin hiyerarşisi "
          "içindir."),
    ("bul", ["`figure.dpi: 200` — baskı kalitesi.",
             "`axes.grid: True` + `grid.color` açık gri + `axes.axisbelow: True` — ızgara "
             "**verinin arkasında** kalır, çekinik durur.",
             "`font.family: DejaVu Sans` — Türkçe karakterleri (ı, ş, ğ, İ) eksiksiz "
             "destekleyen, matplotlib ile birlikte gelen font.",
             "`tr()` lambda'sı (48) — `123456` → `123.456` dönüşümü, Türkçe binlik ayracı."]),
    ("code", (F6, 51, 56, "style() — ortak temizlik")),
    ("p", "Üst ve sağ çerçeve çizgileri kaldırılır, dikey ızgara kapatılır, tick çizgileri "
          "sıfırlanır. Küçük bir fonksiyon ama dört figürün de aynı görünmesini sağlar."),

    ("h2", "6.2  Figür 1 — Günlük iyileşme"),
    ("code", (F6, 59, 82, "results_summary.md'den regex ile okuma")),
    ("p", "İlginç bir tercih: veriyi CSV'den değil, **kendi ürettiğimiz markdown tablosundan** "
          "regex ile okur. Bunun mantığı, figürün raporda yazan sayılarla **birebir aynı** "
          "olmasını garanti etmektir — iki farklı kaynaktan okunsa aralarında sapma "
          "olabilirdi. Tablo bulunamazsa figür atlanır ve neden yazılır."),

    ("h2", "6.3  Figür 2 — Kaydırma dağılımı"),
    ("code", (F6, 85, 104, "histogram ve özet metni")),
    ("p", "`bins = [b - 5 for b in range(-60, 80, 10)]` — kutucuklar 10'ar dakikalık "
          "değerlerin **etrafına ortalanır** (−65, −55, …), böylece bir çubuk tam olarak bir "
          "kaydırma değerini temsil eder. Başlığın altındaki metin en önemli sayıyı verir: "
          "uçuşların yüzde kaçı **hiç kımıldamadı**."),

    ("h2", "6.4  Figür 3 — λ Pareto eğrisi"),
    ("code", (F6, 107, 137, "ödünleşim eğrisi ve seçilen noktanın vurgulanması")),
    ("p", "`sweep_results.csv` yoksa (yani 07 koşulmadıysa) figür atlanır. Görsel dil "
          "ödünleşimi doğrudan anlatır: her nokta bir λ değeridir, x ekseni toplam kaydırma, "
          "y ekseni rekabetçilik kazancı. **Seçilen λ = 0.3 dolu daire ve kalın etiketle** "
          "vurgulanır; diğerleri içi boş dairedir. `offs` sözlüğü etiketlerin üst üste "
          "binmesini engeller."),

    ("h2", "6.5  Figür 4 — Sıralama iyileşmesi"),
    ("code", (F6, 140, 164, "üç renkli değişim dağılımı")),
    ("p", "`b_od − son_sıra` farkı hesaplanır: pozitif = sıralama yükseldi. Renkler doğrudan "
          "anlam taşır — mavi iyileşme, gri değişmedi, kırmızı geriledi. Başlık altındaki "
          "metin üç sayıyı birden verir, okuyucu çubukları tek tek saymak zorunda kalmaz."),
    ("code", (F6, 167, 172, "dört figürü sırayla üret")),

    # ================================================================= 07
    ("h1", ("7", "07_sensitivity.py — Duyarlılık Analizi")),
    ("box", ("Bu dosya ne yapar?",
             "Modeli üç ana parametrede (λ, Wdev, τ) **11 kez** koşturur ve tepkisinin makul "
             "ve sürekli olduğunu belgeler. **Teslim edilen çözümü değiştirmez** "
             "(`write=False`) — bu bir analiz aracıdır, bir üretim adımı değil.")),
    ("tbl", (["", "Değer"],
             [["Girdi", "`derived/`"],
              ["Çıktı", "`reports/sensitivity_analysis.md` + `output/sweep_results.csv`"],
              ["Çalıştırma", "`python src/07_sensitivity.py` (veya "
                             "`python run_all.py --with-sensitivity`)"],
              ["Süre", "~15–30 dk (11 tam-veri koşusu)"]],
             [3.0, 14.0], 8.8)),

    ("h2", "7.1  Neden duyarlılık analizi?"),
    ("p", "Bir optimizasyon sonucu tek başına bir sayıdır. \"Bu sayı ne kadar sağlam?\" "
          "sorusunun cevabı ise parametreleri oynatıp modelin tepkisine bakmakla verilir. "
          "Beklenen davranış: **sürekli ve yönü açıklanabilir** tepki. Küçük bir parametre "
          "değişikliğinde sonuç sıçrıyorsa, modelde ya bir kırılganlık ya bir hata vardır."),

    ("h2", "7.2  03'ü modül olarak yüklemek"),
    ("code", (F7, 1, 35, "docstring ve importlib ile dinamik yükleme")),
    ("p", "Docstring taranan üç parametreyi, süre beklentisini ve en önemlisi şu cümleyi "
          "içerir: **\"Teslim edilen çözümü DEĞİŞTİRMEZ (write=False)\"**. Analiz aracı ile "
          "üretim adımı arasındaki sınır baştan çizilmiştir."),
    ("p", "08 ile aynı teknik: rakamla başlayan dosya adı normal `import` ile alınamaz. "
          "`m3` referansı üzerinden `m3.CFG`, `m3.run_byday`, `m3.main_sweep` doğrudan "
          "kullanılır."),
    ("code", (F7, 38, 40, "reset_cfg — her varyanttan önce temiz sayfa")),
    ("box", ("Bu üç satır neden kritik?",
             "`m3.CFG` **paylaşılan, değiştirilebilir** bir sözlüktür. Bir varyant `wdev_min`'i "
             "90 yaparsa, sonraki varyant da 90 ile koşar ve sonuçlar birbirine karışır. "
             "`reset_cfg()` her koşudan önce temel değerlere (`BASE`) döner. Paylaşılan "
             "durumla çalışan kodda bu tür \"sıfırlama\" alışkanlığı hata önlemenin en ucuz "
             "yoludur.", "warn")),

    ("h2", "7.3  Üç tarama"),
    ("code", (F7, 42, 72, "λ, Wdev ve τ koşuları")),
    ("tbl", (["Tarama", "Değerler", "Neyi ölçer?", "Beklenen yön"],
             [["**λ**", "0, 0.1, 0.3, 0.7, 1.5",
               "Kazanç ↔ kaydırma ödünleşimi (Pareto)",
               "λ↑ → kaydırma↓; λ=0 dejenere"],
              ["**Wdev**", "30, 60, 90 dk", "Serbestlik alanının etkisi",
               "Wdev↑ → daha çok seçenek → kazanç↑"],
              ["**τ**", "30, 45, 60 dk", "Minimum yer süresinin (MCT) etkisi",
               "τ↑ → rotasyon sıkışır → kazanç↓"]],
             [2.0, 3.4, 6.2, 5.4], 8.4)),
    ("p", "λ taraması `m3.main_sweep()` ile yapılır ve sonucu `sweep_results.csv`'ye yazılır "
          "(figür 3'ün girdisi). Wdev ve τ varyantları ise doğrudan `run_byday(write=False)` "
          "ile koşturulur."),

    ("h2", "7.4  Raporun dürüst yorumu"),
    ("code", (F7, 74, 98, "raporun başlığı ve λ tablosu")),
    ("p", "Rapor başında teslim edilen yapılandırma (λ=0.3, Wdev=±60, τ=45) açıkça yazılır ve "
          "bu tablodaki rakamların **aşama-1 (byday) ölçümü** olduğu belirtilir — nihai "
          "sonuç iki aşamalı hattan gelir."),
    ("code", (F7, 99, 133, "sonuçların ve kısıtlarının birlikte yazılması")),
    ("p", "Raporun en değerli kısmı, sonuçları **kayıtsız şartsız sunmamasıdır**. İki uyarı "
          "açıkça yazılır:"),
    ("bul", ["**Wdev = ±90 için:** olay başına aday sayısı 13'ten 19'a çıkar, problem büyür ve "
             "150 s/gün sınırında çözücü kalitesi düşebilir. Ölçülen fark, *serbestlik "
             "etkisi olmayabilir* — zaman limiti etkisi olabilir.",
             "**τ için:** artefakt-sınıflandırma sınırı kaydığı için tepki monoton olmayabilir "
             "(bkz. A2'deki artefakt tanımı)."]),
    ("box", ("Bu neden bir güç göstergesi?",
             "Bir sonucun **hangi koşullarda geçerli olmadığını** bilmek, sonucu bilmek kadar "
             "değerlidir. Rapor \"Wdev=90 daha iyi\" demek yerine \"bu ölçüm zaman-limitlidir, "
             "yorum gerekir\" der. Nitekim Wdev=90 denemesi tam da bu ihtiyat sayesinde "
             "sorgulanmış ve 05 doğrulayıcısı gerçek bir A2 ihlali bulmuştur (bkz. Bölüm 5.2).",
             "ok")),
    ("p", "Rapor ayrıca teslim edilen sonucun **iki aşamalı hattan** (byday + 08) geldiğini, "
          "bu tablodaki rakamların ise **yalnız aşama-1 ölçümü** olduğunu açıkça belirtir — "
          "iki farklı sayının karıştırılmasını önler."),

    # ================================================================= 04
    ("h1", ("8", "04_export_docs.py — Doküman Dışa Aktarma")),
    ("box", ("Bu dosya ne yapar?",
             "Markdown kaynaklarını teslim biçimlerine çevirir: `.md → .docx` (pandoc ile) ve "
             "`.docx → .pdf` (Microsoft Word COM otomasyonu ile). Araçlar yoksa **atlar, "
             "çökmez** — teslimdeki hazır dosyalar geçerli kalır.")),
    ("code", (F4, 1, 30, "docstring, kaynaklar ve UTF-8 konsol")),
    ("p", "Üç doküman çevrilir: model formülasyonu, teknik rapor ve sonuç özeti. Brief "
          "yalnızca model dokümanının PDF olmasını ister; diğer ikisi de aynı akışla üretilir."),
    ("code", (F4, 33, 42, "md_to_docx — pandoc çağrısı")),
    ("box", ("`--resource-path` neden gerekli?",
             "Markdown içindeki görsel yolları göreli yazılmıştır (`docs/figures/...`). "
             "Pandoc varsayılan olarak bunları yalnız **çalışma dizinine** göre arar. "
             "`--resource-path` ile hem proje kökü hem de dosyanın kendi klasörü arama "
             "yoluna eklenir; böylece figürler betik nereden çağrılırsa çağrılsın bulunur.",
             "info")),
    ("code", (F4, 45, 62, "docx_to_pdf — Word COM üzerinden")),
    ("p", "PDF üretimi için ek bir Python kütüphanesi kurmak yerine, **zaten yüklü olan "
          "Word** kullanılır. PowerShell üzerinden COM nesnesi açılır, dosya görünmez modda "
          "açılıp `SaveAs(..., 17)` ile kaydedilir (17 = `wdFormatPDF`). Başarısız olursa "
          "kullanıcıya elle nasıl yapacağı söylenir — sessiz başarısızlık yok."),
    ("code", (F4, 65, 79, "main — zarif atlama")),
    ("p", "İlk iş pandoc var mı diye bakmaktır. Yoksa **açıklayıcı bir mesajla** çıkar: "
          "\"docx/pdf üretimi atlandı; teslimdeki hazır dosyalar geçerlidir. (Kurulum: "
          "pip install pypandoc_binary)\". Bu, `run_all.py`'nin son adımının isteğe bağlı bir "
          "araç yüzünden tüm koşuyu başarısız göstermesini engeller."),

    # ================================================================= run_all
    ("h1", ("9", "run_all.py — Uçtan Uca Koşu")),
    ("box", ("Bu dosya ne yapar?",
             "Tek komutla teslimin tamamını sıfırdan üretir. Her adımı **ayrı bir süreçte** "
             "çalıştırır; bir adım başarısız olursa akış açık bir hata mesajıyla durur ve o "
             "adımın çıkış kodunu döndürür.")),
    ("code", (FR, 1, 12, "kullanım ve süre beklentisi")),
    ("code", (FR, 14, 36, "adım listesi")),
    ("p", "Adımlar bir liste olarak tanımlanır: `(insan-okunur ad, [betik, argümanlar…])`. "
          "Bu yapı sayesinde yeni bir adım eklemek tek satırdır. Duyarlılık analizi ise "
          "**isteğe bağlıdır** (31–32): 15–30 dakika sürdüğü için varsayılan koşuya dahil "
          "değildir, `--with-sensitivity` bayrağıyla eklenir."),
    ("tbl", (["#", "Adım", "Komut", "Yaklaşık süre"],
             [["1", "Veri sağlık kontrolü", "`01_data_health_check.py`", "saniyeler"],
              ["2", "Veri hazırlama", "`02_data_prep.py`", "~15 sn"],
              ["3", "MIP modeli (byday)", "`03_model.py byday`", "~5–10 dk"],
              ["4", "Tam-hafta cilalama", "`08_fullweek_polish.py 1800`", "~30 dk"],
              ["5", "Bağımsız doğrulama", "`05_validate_solution.py`", "saniyeler"],
              ["(6)", "*Duyarlılık (ops.)*", "`07_sensitivity.py`", "15–30 dk"],
              ["6/7", "Rapor figürleri", "`06_make_figures.py`", "saniyeler"],
              ["7/8", "Teslim dokümanları", "`04_export_docs.py`", "saniyeler"]],
             [1.2, 5.0, 6.4, 4.4], 8.6)),
    ("code", (FR, 39, 52, "adımların çalıştırılması")),
    ("p", "Üç tasarım tercihi:"),
    ("bul", ["**Ayrı süreç (`subprocess.run`)** — her adım temiz bir Python yorumlayıcısında "
             "koşar. Bir adımın bıraktığı global durum (örneğin mutasyona uğramış bir CFG) "
             "diğerini etkileyemez.",
             "**`PYTHONIOENCODING=\"utf-8\"`** — alt süreçlerin Türkçe çıktısı Windows "
             "konsolunda bozulmasın diye ortam değişkeni olarak geçirilir.",
             "**`sys.exit(r.returncode)`** — hata durumunda çıkış kodu **aynen dışarı "
             "aktarılır**. 05'in FAIL'i (kod 1) böylece tüm koşuyu durdurur; bu, doğrulamanın "
             "gerçek bir kalite kapısı olmasını sağlayan mekanizmadır."]),
    ("box", ("\"Doğrulanmamış çözüm teslim edilmez\"",
             "Docstring'in ikinci paragrafı bir mühendislik taahhüdüdür: bağımsız "
             "doğrulayıcının FAIL'i koşuyu durdurur. Yani `output/` klasöründe bir sonuç "
             "varsa ve `run_all.py` başarıyla bittiyse, o sonuç **kesinlikle** 12 kontrolden "
             "geçmiştir.", "ok")),
]
