# -*- coding: utf-8 -*-
"""Ekler."""

ITEMS = [
    # ================================================================ EK A
    ("h1", ("A", "Ek A — Hızlı Başvuru")),

    ("h2", "A.1  Komutlar"),
    ("tbl", (["Ne yapmak istiyorum?", "Komut"],
             [["Her şeyi sıfırdan üret", "`python run_all.py`"],
              ["Duyarlılık analiziyle birlikte", "`python run_all.py --with-sensitivity`"],
              ["Sadece veri sağlığını gör", "`python src/01_data_health_check.py`"],
              ["Sadece veri katmanını yenile", "`python src/02_data_prep.py`"],
              ["Tam veri çöz (aşama-1)", "`python src/03_model.py byday`"],
              ["Farklı λ ile çöz", "`python src/03_model.py byday 0.7`"],
              ["λ ödünleşim tablosu", "`python src/03_model.py sweep`"],
              ["Küçük alt-örnekte tüm kısıtları dene", "`python src/03_model.py`"],
              ["Tam-hafta cilalama (aşama-2)", "`python src/08_fullweek_polish.py 1800`"],
              ["Çözümü doğrula", "`python src/05_validate_solution.py`"],
              ["Figürleri yenile", "`python src/06_make_figures.py`"],
              ["Dokümanları DOCX/PDF yap", "`python src/04_export_docs.py`"]],
             [7.6, 9.4], 9.0)),

    ("h2", "A.2  Sabitler ve nerede tanımlı oldukları"),
    ("tbl", (["Sabit", "Değer", "Anlamı", "03'te", "05'te"],
             [["Δ (`delta_min` / `DELTA`)", "10 dk", "Zaman ızgarası adımı", "satır 74",
               "satır 51"],
              ["Wdev (`wdev_min` / `WDEV`)", "±60 dk", "Uçuş kaydırma penceresi", "75", "61"],
              ["ℓ, u (`L_min`,`U_min` / `L_GAP`,`U_GAP`)", "60, 300 dk",
               "Bağlantı boşluğu penceresi", "76", "62"],
              ["α (`alpha` / `ALPHA`)", "0.20", "E1 yönsel dengesizlik toleransı", "80", "63"],
              ["τ (`tau_min` / `TAU`)", "45 dk", "Minimum yer süresi", "81", "64"],
              ["Γ (`gamma_min`)", "30 dk", "E2 süre farkı eşiği", "82", "—"],
              ["Xdev (`xdev_min` / `XDEV`)", "15 dk", "Günler-arası düzenlilik bandı",
               "83", "65"],
              ["cap_dep / cap_arr", "10 / 15", "Kova başına kalkış / varış kapasitesi",
               "95–96", "66"],
              ["λ (`DEFAULT_LAMBDA`)", "0.3", "Tarife-değişim cezası ağırlığı", "976", "—"]],
             [4.6, 2.0, 5.6, 1.5, 1.3], 8.2)),
    ("pm", "05'teki sabitler bilinçli olarak 03'ten import edilmez — çift kayıt ilkesi "
           "(bkz. Bölüm 5.2)."),

    ("h2", "A.3  Çıktı dosyaları sözlüğü"),
    ("tbl", (["Dosya", "Sütunlar / içerik", "Kim üretir?"],
             [["`output/optimized_schedule.csv`",
               "`gun, ucus_no, rol, eski_IST, yeni_IST, degisim_dk, G_gevsetildi`",
               "03 (byday) veya 08"],
              ["`output/market_results.csv`",
               "`gun, pazar, rho, N_rakip, sunulan_baglanti, aday_baglanti, yenilen_rakip, "
               "baslangic_sira_bod, son_sira, aktarma_odul, siralama_odul, rho_katki`",
               "03 / 08"],
              ["`output/selected_connections.csv`",
               "`gun, pazar, gelen_ucus, giden_ucus, IST_varis, IST_kalkis, bosluk_dk, "
               "J_dk, yendigi_rakip`", "03 / 08"],
              ["`output/g_band_exemptions.csv`",
               "`gun, ucus_no, rol` — belgeli G muafiyetleri (boşsa da yazılır)", "03 / 08"],
              ["`output/results_summary.md`",
               "Sonuç özeti, gün tablosu, notlar, çıktı listesi", "03 / 08"],
              ["`output/sweep_results.csv`",
               "`lam, delta, dpct, moved, movedpct, shift_dk`", "07"],
              ["`reports/data_health_report.md`", "Veri sağlık raporu", "01"],
              ["`reports/validation_report.md`", "12 kontrolün PASS/FAIL tablosu", "05"],
              ["`reports/fullweek_polish.md`", "Cilalama koşu raporu + global MIP-gap", "08"],
              ["`reports/sensitivity_analysis.md`", "λ / Wdev / τ duyarlılık tabloları", "07"],
              ["`derived/transform_log.md`", "Yapılan tüm veri dönüşümlerinin kaydı", "02"]],
             [5.0, 8.4, 3.2], 8.2)),

    ("h2", "A.4  Fonksiyon dizini — \"şunu nerede bulurum?\""),
    ("tbl", (["Aradığım şey", "Dosya · fonksiyon", "Satır"],
             [["Bağlantı penceresi kısıtı (B1)", "`03_model.py` · `build_model`", "386–393"],
              ["Azalan getiri ödülü (C)", "`03_model.py` · `build_model`", "402–418"],
              ["Rakip yenme mantığı (D)", "`03_model.py` · `build_model`", "420–475"],
              ["Uçak rotasyonu (A2)", "`03_model.py` · `build_model`", "492–566"],
              ["Hub kapasitesi (F)", "`03_model.py` · `build_model`", "686–725"],
              ["Tarife düzenliliği (G)", "`03_model.py` · `build_model`", "590–647"],
              ["Amaç fonksiyonu", "`03_model.py` · `build_model`", "727–748"],
              ["Baseline hesabı", "`03_model.py` · `current_baseline`", "813–828"],
              ["Gün-gün çözüm döngüsü", "`03_model.py` · `run_byday`", "1027–1199"],
              ["Gece-aşan koruma sınırları", "`03_model.py` · `compute_overnight_guards`",
               "979–1024"],
              ["Çıktı dosyalarının yazımı", "`03_model.py` · `write_outputs`", "1270–1347"],
              ["Warm-start noktasının kurulması", "`08_fullweek_polish.py` · "
               "`set_start_values`", "209–291"],
              ["Excel süre ayrıştırma", "`02_data_prep.py` · `dur_min`", "72–98"],
              ["Hafta normalizasyonu", "`02_data_prep.py` · `main`", "190–212"],
              ["Doğrulama kontrolleri", "`05_validate_solution.py` · `main`", "147–431"]],
             [6.0, 8.6, 2.0], 8.4)),

    # ================================================================ EK B
    ("h1", ("B", "Ek B — Kodla İlgili Muhtemel Sorular")),
    ("p", "Aşağıdaki sorular, koda bakan birinin ilk soracağı türden sorulardır. Cevaplar "
          "doğrudan kodun ilgili satırlarına dayanır."),

    ("h3", "1. Neden Pyomo + HiGHS? Gurobi/CPLEX neden kullanılmadı?"),
    ("p", "HiGHS **açık kaynaktır ve lisans gerektirmez** — jüri kodu kendi makinesinde "
          "`pip install` sonrası doğrudan koşturabilir. Pyomo ise modeli çözücüden bağımsız "
          "yazmayı sağlar: `CFG[\"solver\"]` değiştirilerek başka bir çözücüye geçilebilir. "
          "Tekrar-üretilebilirlik, marjinal hız kazancından önemli görüldü."),

    ("h3", "2. `threads: 1` performansı düşürmüyor mu?"),
    ("p", "Evet, düşürür. Ama çok çekirdekli MIP çözümü **deterministik değildir** — aynı "
          "girdiyle farklı çalışmalarda farklı çözümler dönebilir. Yarışma teslimi için "
          "\"jüri koştuğunda aynı sayıyı görmeli\" kısıtı hız kaygısının önüne konmuştur "
          "(`03_model.py` satır 922)."),

    ("h3", "3. Model neden haftanın tamamını tek seferde çözmüyor?"),
    ("p", "Denendi ve olmadı: tam-hafta modelinde ~102.000 ikili değişken var; HiGHS makul "
          "sürede tek bir uygun çözüm bile bulamıyor (`03_model.py` satır 1030). Çözüm iki "
          "aşamalı: byday hızlı ve garanti bir çözüm üretir, `08_fullweek_polish.py` onu tam "
          "modele **başlangıç noktası** olarak verip küresel iyileştirme ve global MIP-gap "
          "elde eder."),

    ("h3", "4. Bir kısıtı kapattınız (E2) — bu modeli zayıflatmıyor mu?"),
    ("p", "E2 küçük ölçekte **açık ve doğrulanmıştır**; yalnız tam ölçekte kapatılmıştır ve "
          "gerekçesi ölçülmüştür: çekirdek + E2 tek başına çözülemiyor, çekirdek + "
          "A2/G/F/E1 hepsi hızlı (`03_model.py` satır 27–28, 110–112). Kapatma kararı "
          "gizlenmemiş, `results_summary.md`'nin notlar bölümünde açıkça ilan edilmiştir."),

    ("h3", "5. B2 kapalıysa model uygun bağlantıları sunmayabilir — bu bir kayıp değil mi?"),
    ("p", "Amaç fonksiyonu zaten sunmayı **ödüllendirir** (C ödülü), dolayısıyla model "
          "kârlı olan her bağlantıyı kendiliğinden sunar. B2'yi zorlamak ise E1 yönsel "
          "dengesiyle çatışıp modeli **infeasible** yapıyor (bisection ile doğrulandı, "
          "satır 86–89). Yani B2 açık olsaydı hiç çözüm alamazdık."),

    ("h3", "6. λ = 0.3 nereden geldi?"),
    ("p", "Taramadan. `03_model.py sweep` beş λ değerini koşturur; λ ∈ [0.1, 1.5] aralığında "
          "kazanç düz bir plato çizer (%4.2–4.3) ve λ = 0.3 bu platonun dizidir: en yüksek "
          "kazanç, en düşük kaydırma. Sonuçlar `output/sweep_results.csv` ve Figür 3'te."),

    ("h3", "7. \"Artefakt\" dediğiniz A2 ihlalleri gerçek ihlal olabilir mi?"),
    ("p", "Artefakt olarak sayılan turlar, **mevcut yayınlanan tarifenin kendisinin de "
          "sağlamadığı** turlardır — yani o gün o çift zaten tek uçakla dönülmüyor. "
          "Optimizasyon bunları yaratmadı, sadece devraldı. Kod bu ikisini asla "
          "karıştırmaz: `a2x_base` (artefakt) ve `a2x_viol` (YENİ ihlal) ayrı sayılır ve "
          "**ikisi de** raporlanır. YENİ ihlal sayısı 0 olmalıdır ve 08'de bu bir yeniden "
          "yazma bariyeridir."),

    ("h3", "8. G muafiyetlerini modelin kendisi yazıyor — bu kendi kendini aklama değil mi?"),
    ("p", "Muafiyet listesi diske yazılır (`output/g_band_exemptions.csv`), raporlarda "
          "sayısıyla birlikte anılır ve doğrulayıcı onu okuyup ayrıca sayar. Alternatif — "
          "muafiyetleri hiç bildirmemek — G'nin nerede uygulanmadığını **bilinemez** kılardı. "
          "Şeffaf gevşetme, gizli gevşetmeden iyidir."),

    ("h3", "9. Doğrulayıcı modelden bağımsız derken ne kadar bağımsız?"),
    ("p", "`05_validate_solution.py` ne Pyomo import eder ne de `03_model.py`'ye dokunur. "
          "Sabitleri (Wdev, τ, Xdev, kapasiteler) kendi dosyasında **yeniden yazar**. Girdisi "
          "yalnız `derived/` (veri) ve `output/` (çözüm dosyaları)dır. Baseline'ı bile "
          "sıfırdan hesaplar. Tek ortaklık, aynı *tanımları* kullanmasıdır — aynı *kodu* "
          "değil."),

    ("h3", "10. Bu doğrulayıcı hiç gerçek hata yakaladı mı?"),
    ("p", "Evet. `05_validate_solution.py` satır 52–60'taki not, Wdev = 90 denemesinde "
          "yakalanan gerçek bir A2 ihlalini kaydeder (uçuş 2200/2201, gün 2). Kök neden "
          "bulundu (amaç evreni dışındaki rotasyon ortağı için A2 kısıtının hiç kurulmaması), "
          "yüksek rakam **iptal edildi** ve 03'te `full_role_time` evren-ankoru ile kalıcı "
          "olarak düzeltildi."),

    ("h3", "11. Sonuçlar başka bir makinede aynı çıkar mı?"),
    ("p", "Evet, tasarım gereği: tek iş parçacığı, sabit rasgele tohum (`random_seed: 0`), "
          "sabit MIP-gap ve süre sınırları, veriden türetilen (hardcode edilmeyen) gün "
          "listesi. Tek değişken, süre sınırına takılan koşuların makine hızına bağlı "
          "olmasıdır — bu yüzden gap ve süre sınırları raporlarda **açıkça** yazılır."),

    ("h3", "12. Gizli test verisi farklı gelirse kod çalışır mı?"),
    ("p", "Kod bunun için hazırlanmıştır:"),
    ("bul", ["Gün listesi veriden okunur, hardcode edilmez (`all_operation_days()`).",
             "Dosya adı farklıysa `glob` yedeğiyle aranır (`_find_conn_file()`).",
             "Beklenen sütun yoksa **anlaşılır** hata verir (`need()` — 02, satır 113–122).",
             "`ElapsedTime` sütunları yoksa eski şemaya (minimal de-wrap) otomatik düşer.",
             "`flight_block_times.csv` yoksa A2 ihtiyatlı moda geçer.",
             "Tek bir günün çözümü hata verirse o gün atlanır, koşu devam eder "
             "(`run_byday`, satır 1085–1088)."]),
    ("box", ("Kapanış",
             "Bu projenin kodu yalnız bir sonuç üretmiyor; **ürettiği sonucun neden "
             "güvenilir olduğunu da üretiyor**. Sağlık raporu, dönüşüm logu, bağımsız "
             "doğrulama, duyarlılık analizi ve global MIP-gap — hepsi aynı amaca hizmet "
             "eder: bir sayı söylediğinizde, arkasında durabilmek.", "ok")),
]
