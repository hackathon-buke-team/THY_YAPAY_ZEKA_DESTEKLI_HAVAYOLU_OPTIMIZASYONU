# -*- coding: utf-8 -*-
"""ALGORITMA — SIFIRDAN ANLATIM · Bolum 0-3
(problem · veri · optimizasyon temelleri)

Oge tipleri builder.Doc.render + main4.Doc4 tarafindan islenir.
"eq" = ortalanmis formul satiri (main4'te tanimli).
"""

F3 = "03_model.py"
F2 = "02_data_prep.py"

ITEMS = [
    # =================================================================== 0
    ("h1", ("0", "Bu doküman ne işe yarar?")),
    ("p", "Salı günü jüri karşısında olacaksınız. Bu doküman, projenin **en başından** — "
          "yani elinize gelen dört Excel dosyasından — **en sonuna** — yani \"çözümümüz "
          "optimalin en fazla %1,18 uzağında\" cümlesine kadar her adımı, hiçbir adımı "
          "atlamadan anlatır."),
    ("p", "Üç sorunuz vardı. Cevapları burada, ama nerede olduklarını baştan söyleyeyim:"),
    ("tbl", (["Sorunuz", "Cevabın yeri", "Tek cümlelik cevap"],
             [["\"**E2** ne? Anlamadım.\"", "**Bölüm 6** (tamamı)",
               "Projede **iki ayrı E2** var ve karıştırılıyor: biri veri sütunu, biri model "
               "kısıtı. İkisi de Bölüm 6'da."],
              ["\"**%1,18** kesin mi, nereden biliyoruz?\"", "**Bölüm 9** (tamamı)",
               "Kesin. Çünkü bu sayı bizim iddiamız değil, çözücünün **matematiksel "
               "kanıtı**; kodun hangi satırında okunduğunu da göstereceğim."],
              ["\"**100.552 ikili değişken** ne demek?\"", "**Bölüm 4** + **Ek A**",
               "Modelin sorduğu evet/hayır sorularının sayısı. Dökümünü **yeniden sayarak** "
               "doğruladım — ve raporlardaki iki farklı sayının nedenini buldum."]],
             [4.4, 3.4, 9.2], 8.6)),
    ("box", ("Okuma sırası önerisi",
             "Zamanınız kısıtlıysa: **Bölüm 3** (optimizasyon temelleri) → **Bölüm 6** (E2) → "
             "**Bölüm 9** (MIP gap) → **Bölüm 12** (jüri soruları). Bu dördü, sorduğunuz "
             "soruların tamamını kapatır. Bölüm 1–2 problemi ve veriyi, 4–5 modeli, 7–8 "
             "çözüm yöntemini, 10–11 doğrulama ve sonuçları anlatır.", "info")),

    ("h2", "0.1  Önce 60 saniyelik özet — tüm proje tek sayfada"),
    ("p", "Jüri size \"projenizi bir dakikada anlatın\" derse söyleyeceğiniz şey budur:"),
    ("num", [
        "**Problem.** THY'nin İstanbul aktarma merkezinde (IST) haftalık bir uçuş tarifesi "
        "var. Bir yolcu Berlin'den Bangkok'a giderken IST'te aktarma yapıyor. Bu yolculuğun "
        "toplam süresi, rakip havayollarının aynı rotadaki süreleriyle yarışıyor. **Uçuş "
        "saatlerini ±60 dakika kaydırarak** bu yarışta daha iyi bir yere gelebilir miyiz?",
        "**Karar.** Değiştirdiğimiz tek şey: ayarlanabilir uçuşların IST'teki kalkış/varış "
        "saatleri. Uçak filosunu, rotaları, uçuş sürelerini, hiçbirini değiştirmiyoruz.",
        "**Ölçüt.** Her pazarın (Berlin→Bangkok gibi) bir gelir ağırlığı ρ var. Fayda = "
        "ρ × (kaç geçerli bağlantı sunduğumuz + rakip sıralamasında ne kadar yükseldiğimiz). "
        "Tüm pazarlar üzerinden toplanır.",
        "**Yöntem.** Problemi bir **Karışık Tamsayılı Programlama (MIP)** modeline çevirdik: "
        "yüz binin üzerinde evet/hayır değişkeni. Sezgisel (genetik algoritma vb.) "
        "kullanmadık — bilinçli bir tercih, nedeni Bölüm 9'da.",
        "**Çözüm.** Açık kaynak HiGHS çözücüsü, iki aşamada: önce gün gün (hızlı), sonra "
        "tüm hafta tek modelde cilalama (30 dakika).",
        "**Sonuç.** Rekabetçilik **+%4,72**. Bunun için uçuşların yalnız **%23'ü**, "
        "ortalama **19 dakika** kaydırıldı. Ve çözümün optimale en fazla **%1,18** uzak "
        "olduğu **kanıtlandı**.",
        "**Güvence.** Sonuç, modeli hiç görmeyen **bağımsız bir doğrulayıcıyla** baştan "
        "hesaplandı: kontrollerin tamamı PASS."]),

    # =================================================================== 1
    ("h1", ("1", "Problem — neye karar veriyoruz?")),
    ("p", "Optimizasyon modelinin ilk kuralı şudur: **neyin karar, neyin veri olduğunu** "
          "netleştirmeden tek satır kod yazamazsınız. Bu bölüm tam olarak onu yapıyor."),

    ("h2", "1.1  Aktarma ağı ve \"bağlantı\" kavramı"),
    ("p", "THY'nin ağı bir **hub-and-spoke** (merkez-ve-parmak) ağıdır. Yolcuların büyük "
          "bölümü A noktasından B'ye doğrudan uçmaz; IST'e gelir, uçak değiştirir, oradan "
          "devam eder. Bu iki bacaklı yolculuğa **bağlantı** (connection / itinerary) diyoruz."),
    ("img", ("f03_baglanti_anatomisi.png",
             "Şekil 1.1 — Bir bağlantının anatomisi. Modelin oynadığı tek şey ortadaki "
             "boşluktur; iki bacağın uçuş süreleri sabittir.")),
    ("p", "Bir bağlantının üç parçası vardır ve bunları ayırt etmek **kritik** — çünkü "
          "sorduğunuz \"E2\" sorusunun cevabı burada başlıyor:"),
    ("tbl", (["Parça", "Sembol", "Ne demek", "Karar mı, veri mi?"],
             [["1. bacak süresi", "**E1**  *(ElapsedTime1)*",
               "Örn. Berlin→IST uçuşunun havada geçen süresi", "**VERİ** — değişmez"],
              ["Aktarma boşluğu", "**boşluk**  *(gap)*",
               "Uçağın IST'e varışı ile sonraki uçağın kalkışı arasındaki bekleme",
               "**KARAR** — saatleri kaydırınca değişir"],
              ["2. bacak süresi", "**E2**  *(ElapsedTime2)*",
               "Örn. IST→Bangkok uçuşunun havada geçen süresi", "**VERİ** — değişmez"]],
             [3.4, 3.2, 6.4, 4.0], 8.4)),
    ("box", ("İlk \"E2\" burada — ve bu bir KISIT DEĞİL",
             "Verideki `ElapsedTime2` sütunu kodda `E2_min` adını alır ve **ikinci bacağın "
             "uçuş süresidir**. Bunun modelin \"E2 kısıtı\" ile **hiçbir ilgisi yoktur**. "
             "Aynı harfin iki farklı şeye verilmiş olması talihsiz bir isim çakışmasıdır; "
             "Bölüm 6.1'de ikisini yan yana koyup ayıracağım.", "warn")),
    ("p", "Toplam yolculuk süresi (J) bu üçünün toplamıdır:"),
    ("eq", "**J   =   E1   +   boşluk   +   E2**"),
    ("p", "E1 ve E2 sabit olduğuna göre, **J'yi değiştirmenin tek yolu boşluğu "
          "değiştirmektir** — yani uçuş saatlerini kaydırmak. Projenin tüm mantığı bu tek "
          "denklemin üzerine kurulu."),

    ("h2", "1.2  Neyi değiştiriyoruz, neyi değiştirmiyoruz"),
    ("img", ("g1_ne_degistiriyoruz.png",
             "Şekil 1.2 — Kararımız tek bir şey: ayarlanabilir uçuşların IST saatleri.")),
    ("tbl", (["DEĞİŞTİRDİĞİMİZ (karar)", "DEĞİŞTİRMEDİĞİMİZ (veri / dış kısıt)"],
             [["Ayarlanabilir uçuşların IST kalkış/varış saati",
               "Uçuş süreleri (bacak blokları)"],
              ["— 10 dakikalık ızgarada", "Hangi uçuş nereye uçuyor (rotalar)"],
              ["— mevcut saatin ±60 dakika penceresinde", "Filo, uçak sayısı, kapasite"],
              ["Hangi bağlantının \"sunulduğu\" (bunun sonucu olarak)",
               "Rakiplerin tarifeleri"],
              ["", "Pazarların gelir ağırlıkları ρ"]],
             [8.5, 8.5], 8.8)),
    ("p", "Neden ±60 dakika? Brief bir sınır koymuyor, ama sınırsız bırakmak iki sorun "
          "yaratırdı: *(i)* modelin boyutu patlar (her uçuş için 13 seçenek yerine 144), "
          "*(ii)* gerçek hayatta bir uçuşu 5 saat kaydırmak operasyonel olarak anlamsızdır. "
          "±60 dk bilinçli ve belgeli bir tasarım kararıdır "
          "(`docs/model_formulation.md`, karar D3)."),
    ("p", "Neden 10 dakikalık ızgara? Çünkü brief'in hub kapasite kısıtı zaten 10 dakikalık "
          "kovalarda tanımlı. Aynı ızgarayı kullanmak hem kısıtı doğal kılar hem modeli "
          "küçültür. **±60 dk penceresi ÷ 10 dk ızgara = uçuş başına 13 seçenek** "
          "(−60, −50, …, 0, …, +50, +60). Bu \"13\" sayısını aklınızda tutun; Bölüm 4'te "
          "yüz binlik değişken sayısının nereden geldiğini açıklarken karşınıza çıkacak."),

    ("h2", "1.3  Neyi iyileştiriyoruz — \"rekabetçilik\" tam olarak ne?"),
    ("p", "Fayda iki bileşenden oluşur. Her ikisi de her (pazar, gün) için ayrı hesaplanır "
          "ve o pazarın gelir ağırlığı ρ ile çarpılır."),
    ("h3", "(a) Bağlantı sayısı ödülü — azalan getiri"),
    ("p", "Bir pazarda ne kadar çok geçerli aktarma sunarsanız o kadar iyi. Ama ikinci "
          "bağlantı birinciden, üçüncü ikinciden daha az değerlidir (yolcuya zaten bir "
          "seçenek sunmuşsunuzdur). Bunu **yarıya inen ağırlıklarla** modelledik:"),
    ("eq", "**1. bağlantı: 1,000  ·  2.: 0,500  ·  3.: 0,250  ·  4.: 0,125 …**"),
    ("eq", "yani j. bağlantının ağırlığı  **(½)^(j−1)**"),
    ("img", ("f06_azalan_getiri.png",
             "Şekil 1.3 — Azalan getiri: her ek bağlantının katkısı yarıya iner.")),
    ("h3", "(b) Sıralama ödülü — rakibi yenmek"),
    ("p", "Bir pazarda N rakip taşıyıcı var. Bizim en iyi bağlantımızın toplam süresi J, "
          "bir rakibin süresinden **kısaysa** o rakibi \"yendik\" sayılır. Yenilen rakip "
          "sayısı sıralamamızı belirler, sıralama da yarışmanın verdiği **ödül tablosundan** "
          "(`change_ranking_input.xlsx`) okunur."),
    ("img", ("f07_rakip_siralama.png",
             "Şekil 1.4 — Yenilen rakip sayısı → yeni sıra → tablodan okunan ödül.")),
    ("box", ("Neden bu ikisi birden?",
             "Yalnız bağlantı sayısını ödüllendirseydik model, hiçbir rakibi yenmeyen ama "
             "çok sayıda vasat bağlantı üretirdi. Yalnız sıralamayı ödüllendirseydik tek bir "
             "çok hızlı bağlantı yapıp gerisini boşlardı. İkisi birlikte, brief'in istediği "
             "dengeyi kurar: **hem çok, hem hızlı**.", "info")),

    # =================================================================== 2
    ("h1", ("2", "Veri — dört Excel dosyasından modele giden yol")),
    ("p", "Model kurmadan önce veriyi anlamak ve temizlemek zorundayız. Bu iş iki betikte "
          "yapılır: `01_data_health_check.py` (teşhis — hiçbir şeyi düzeltmez, sadece "
          "raporlar) ve `02_data_prep.py` (dönüşüm — `derived/` katmanını üretir)."),
    ("img", ("f02_veri_katmanlari.png",
             "Şekil 2.1 — Ham Excel → derived/ → model. Ham dosyalara hiç dokunulmaz.")),

    ("h2", "2.1  Elimizdeki dört dosya"),
    ("tbl", (["Dosya", "Satır", "Ne içerir"],
             [["`O&D Rakip Bağlantı Tablosu_updated.xlsx`", "**57.317**",
               "Her satır bir aktarmalı yolculuk. 7.850'si THY, 49.467'si rakip. Sütunlar: "
               "iki bacağın uçuş no'ları, saatleri, süreleri (`ElapsedTime1/2`), taşıyıcı, "
               "pazar (O&D), gün."],
              ["`Yolcu Verisi_masked.xlsx`", "8.075",
               "Pazar başına **gelir/önem ağırlığı ρ** (1–1000 arası). Amaç fonksiyonunun "
               "ağırlıkları buradan gelir."],
              ["`change_ranking_input.xlsx`", "22.140",
               "**Sıralama ödül tablosu**: (rakip sayısı N, ilk sıra b, son sıra s) → ödül. "
               "Her N için tam N² satır."],
              ["`Flight Pairs.xlsx`", "1.562",
               "Uçak **rotasyon eşleri**: hangi gidiş uçuşu hangi dönüşle aynı uçağı "
               "kullanıyor. A2 kısıtının kaynağı."]],
             [5.6, 1.8, 9.6], 8.4)),
    ("p", "Toplam **89.094 satır** ham veri. Modelin ihtiyaç duyduğu her şey bunlardan "
          "türetilir."),

    ("h2", "2.2  Veri sağlık kontrolü — ne bulduk?"),
    ("p", "`01_data_health_check.py` hiçbir şeyi düzeltmez; sadece bakar ve raporlar "
          "(`reports/data_health_report.md`). Bulduğu ve modeli şekillendiren başlıca "
          "şeyler:"),
    ("tbl", (["Bulgu", "Sayı", "Ne yaptık"],
             [["ρ değeri olmayan pazar", "**48**",
               "Amaç fonksiyonundan **dışladık**. Değer uydurmak yerine ihtiyatlı dışlama."],
              ["Rotasyon eşi olmayan TK uçuş no", "**176**",
               "**Sabit** kabul ettik — hiç kaydırmıyoruz (rotasyon güvenliği "
               "doğrulanamaz)."],
              ["Aynı (uçuş, gün) için farklı saat", "**132**",
               "Hafta normalizasyonu ile düzelttik (bkz. 2.4)."],
              ["Rakip sayısı N (taşıyıcı bazlı)", "1–17",
               "Ödül tablosu N ≤ 40'ı kapsıyor → **tam kapsam**. Itinerary bazlı sayımda "
               "73 pazar 40'ı aşıp tablo dışına çıkardı → taşıyıcı bazlı tanım seçildi."],
              ["Bağlantı boşluğu 60–300 dk penceresinde", "%89,0",
               "Kalan %11 zaten geçersiz; ön-işlemede elenir."]],
             [6.2, 2.2, 8.6], 8.4)),

    ("h2", "2.3  J'nin kesin hesabı — ve \"sarma\" tuzağı"),
    ("p", "Veri toplam yolculuk süresini `Gate-to-Gate Uçuş Süresi` sütununda veriyor. Ama "
          "bu sütun **saat formatında** (time-of-day): 25 saatlik bir yolculuk 01:00 olarak "
          "görünüyor. Buna **sarma** (wrap) denir ve düzeltilmezse ultra-uzun uçuşlarda tam "
          "24 saatlik hata yapar."),
    ("p", "Neyse ki güncellenmiş veri iki bacağın sürelerini ayrı ayrı veriyor "
          "(`ElapsedTime1`, `ElapsedTime2`). O zaman J'yi **doğrudan** kurabiliriz:"),
    ("code", (F2, 137, 155, "J = E1 + boşluk + E2 — sarma belirsizliği YOK")),
    ("p", "Satır 145–146 tam olarak Bölüm 1.1'deki denklemdir. Satır 150–151 ise bir "
          "**öz-doğrulamadır**: hesapladığımız kesin J ile verideki sarılı sütun, 24 saatin "
          "katları dışında birbirini tutmalı. Sonuç: **tutarsız satır 0**. Yani iki bağımsız "
          "kaynak birbirini doğruluyor."),
    ("box", ("Bu bir jüri kozu",
             "Veride gerçekten 24 saati aşan **495** yolculuk var. Eski (ElapsedTime'sız) "
             "sezgisel yöntem bunların **154'ünü** yanlış hesaplıyordu. Yani bu düzeltme "
             "kozmetik değil: 154 satırda tam 24 saatlik hata engellendi. Jüri \"veriyi ne "
             "kadar iyi anladınız\" diye sorarsa cevap budur.", "ok")),

    ("h2", "2.4  Hafta normalizasyonu — gerçek bir hatanın yakalanışı"),
    ("p", "Veride aynı operasyon günü (\"Gün 1\") farklı pazarlarda **farklı takvim "
          "haftalarına** yazılmış: bir pazarda 4 Ağustos Pazartesi, diğerinde 11 Ağustos "
          "Pazartesi. Model bunları **iki ayrı uçuş** sanar ve aynı fiziksel uçağa iki farklı "
          "saat atayabilir — çıktıda bu gerçekten gözlendi (bir kopya −50 dk, öteki 0)."),
    ("code", (F2, 198, 212, "her iki zaman damgası BİRLİKTE 7k gün geri çekilir")),
    ("p", "Kritik nokta satır 206–207: iki zaman damgası **birlikte** kaydırılır, dolayısıyla "
          "aralarındaki boşluk ve J **hiç değişmez**. Sonuç: 132 satır normalize edildi, olay "
          "sayısı 5.604 → 5.474'e indi. Ardından birebir özdeş adaylar tekilleştirildi "
          "(7.850 → 7.693) — aksi hâlde aynı fiziksel bağlantı **iki kez ödül** kazandırırdı."),

    ("h2", "2.5  ρ (gelir ağırlığı) nereden geliyor?"),
    ("p", "Bu soruyu jüri sorabilir; cevabı çok basit: **ρ hesaplanmıyor, doğrudan "
          "okunuyor.** `Yolcu Verisi_masked.xlsx`'teki `OD importance factor` sütunu, pazar "
          "anahtarıyla eşleştirilip aynen kullanılır. Hiçbir normalizasyon, ölçekleme veya "
          "dönüşüm yok — 1..1000 aralığındaki ham değer. Bu bilinçli: yarışmanın verdiği "
          "ağırlığı değiştirmek, yarışmanın ölçütünü değiştirmek olurdu."),

    ("h2", "2.6  Hangi uçuş \"ayarlanabilir\", hangisi \"sabit\"?"),
    ("p", "Bu ayrım modelin boyutunu doğrudan belirler, o yüzden net olalım:"),
    ("code", (F3, 238, 246, "sabit uçuşun tek adayı var: mevcut saati")),
    ("p", "Kural (satır 240): bir TK uçuş numarasının `Flight Pairs.xlsx`'te **rotasyon eşi "
          "yoksa sabittir**. Gerekçe: eşi bilinmeyen bir uçuşu kaydırırsak, o uçağın bir "
          "sonraki görevine yetişip yetişmediğini **doğrulayamayız**. Emin olamadığımız yerde "
          "oynamıyoruz."),
    ("tbl", (["", "Uçuş no", "Model olayı", "Aday saat sayısı"],
             [["**Ayarlanabilir**", "776", "**4.553**", "13  (±60 dk / 10 dk)"],
              ["**Sabit**", "176", "823", "1  (mevcut saati)"],
              ["**Toplam**", "952", "**5.376**", "—"]],
             [4.2, 3.0, 4.2, 5.6], 8.6)),
    ("pm", "Not: \"uçuş no\" ile \"olay\" farklı şeylerdir. Bir uçuş numarası haftanın birden "
           "çok gününde uçar; her (uçuş no, rol, gün) üçlüsü ayrı bir olaydır ve ayrı karar "
           "verilir. 776 ayarlanabilir uçuş numarası → 4.553 ayarlanabilir olay."),

    # =================================================================== 3
    ("h1", ("3", "Optimizasyon 101 — sıfırdan, jargonsuz")),
    ("p", "Bu bölüm, matematiksel programlamayı hiç bilmeyen birine anlatır gibi yazıldı. "
          "Jüri temel kavramları sorarsa buradaki cümleleri doğrudan kullanabilirsiniz."),

    ("h2", "3.1  Karar değişkeni, kısıt, amaç — üç parça"),
    ("p", "Her optimizasyon modeli üç şeyden oluşur:"),
    ("tbl", (["Parça", "Sorusu", "Bizim projemizde"],
             [["**Karar değişkeni**", "Neyi seçebiliyorum?",
               "Her ayarlanabilir uçuş hangi saate atansın?"],
              ["**Kısıt**", "Hangi seçimler yasak?",
               "Uçak dönüşe yetişmeli, hub kapasitesi aşılmamalı, aynı uçuş günler arası "
               "±15 dk'dan fazla oynamamalı…"],
              ["**Amaç fonksiyonu**", "\"İyi\" ne demek?",
               "ρ-ağırlıklı rekabetçilik faydası — enbüyüklenecek."]],
             [3.6, 4.0, 9.4], 8.6)),

    ("h2", "3.2  Neden \"ikili\" (binary) değişken?"),
    ("p", "Bazı kararlar kesirli **olamaz**. \"2,7 uçuş\" diye bir şey yoktur. Daha "
          "önemlisi, bazı kararlar doğası gereği **EVET / HAYIR**'dır:"),
    ("bul", ["Bu uçuş 14:30 kovasına mı atandı?  **Evet (1) / Hayır (0)**",
             "Bu bağlantı sunuluyor mu?  **Evet (1) / Hayır (0)**",
             "Bu rakip yenildi mi?  **Evet (1) / Hayır (0)**"]),
    ("p", "Yalnız 0 veya 1 değeri alabilen değişkene **ikili (binary) değişken** denir. "
          "Bunlar modelin en güçlü parçasıdır — ama aynı zamanda en pahalısı. Nedenini "
          "anlamak için önce çözücünün nasıl çalıştığını görmek gerek."),
    ("h3", "\"Tek atama\" kalıbı (one-hot) — en sık kullandığımız yapı"),
    ("p", "Bir uçuşun 13 aday saatinden **tam birine** atanmasını nasıl söylersiniz? "
          "13 tane ikili değişken açıp toplamlarını 1'e eşitleyerek:"),
    ("code", (F3, 372, 375, "A1 — her ayarlanabilir olay tam bir kovaya atanır")),
    ("img", ("h2_onehot.png",
             "Şekil 3.1 — 13 ikili değişkenden tam biri 1 olur; uçuşun saati budur.")),
    ("p", "Bu yapının güzelliği şu: uçuşun gerçek saati artık **doğrusal bir ifadedir** — "
          "`θ = Σ (saat değeri × x)`. Toplamdaki 13 terimin 12'si sıfırla çarpılır, biri "
          "kalır. Böylece \"saat\" gibi bir sayıyı ikili değişkenlerle **tam doğrusal** "
          "biçimde modelleyebiliyoruz. Bu kalıp Bölüm 5'te ceza teriminin neden bedavaya "
          "geldiğini de açıklayacak."),

    ("h2", "3.3  LP gevşetmesi — çözücünün en önemli numarası"),
    ("p", "Yüz binlik ikili değişkenin tüm kombinasyonlarını denemek imkânsızdır. Çözücü "
          "bunun yerine şu numarayı yapar:"),
    ("box", ("LP gevşetmesi (linear relaxation)",
             "\"x ya 0 ya 1 olmalı\" kuralını **geçici olarak kaldır**; x'in 0 ile 1 arasında "
             "herhangi bir kesirli değer almasına izin ver. Ortaya çıkan problem artık bir "
             "**doğrusal programdır** (LP) ve LP'ler çok hızlı, kesin çözülür "
             "(simpleks / iç-nokta yöntemleri).", "info")),
    ("p", "Peki bunun ne faydası var? Şu: gevşetilmiş problem, gerçek problemden **daha "
          "serbesttir** — daha fazla seçeneği vardır. Dolayısıyla bulduğu en iyi değer, "
          "gerçek problemin en iyi değerinden **asla kötü olamaz**. Enbüyükleme yaptığımız "
          "için bu şu demek:"),
    ("eq", "**LP'nin cevabı   ≥   gerçek MIP'in cevabı**"),
    ("p", "İşte bu bir **üst sınırdır** (bound): \"cevap bundan daha iyi olamaz\" garantisi. "
          "Bölüm 9'daki %1,18'in yarısı tam olarak bu cümleden geliyor."),

    ("h2", "3.4  Dallanma-sınırlama (branch and bound)"),
    ("p", "LP gevşetmesi genelde kesirli bir cevap verir (\"bu uçuş %30 saat 14:30'da, %70 "
          "saat 14:40'ta\"). Bu gerçek bir tarife değildir. Çözücü o zaman **dallanır**: "
          "kesirli çıkan bir değişkeni seçer ve iki alt problem kurar — birinde x=0, "
          "diğerinde x=1. Her alt problemi yine LP ile çözer. Ağaç böyle büyür."),
    ("img", ("g6_branch_bound.png",
             "Şekil 3.2 — Dallanma ve budama. Bir dalın LP üst sınırı eldeki en iyi çözümden "
             "kötüyse, o dalın altındaki tüm kombinasyonlar tek hamlede elenir.")),
    ("p", "**Budama (pruning)** işin sihridir: bir dalın LP üst sınırı 3,399 çıkmışsa ve "
          "elimizde zaten 3,405 değerinde gerçek bir çözüm varsa, o dalın altında hiçbir şey "
          "3,399'u geçemez — dolayısıyla o dalın altındaki milyarlarca kombinasyon tek "
          "hamlede elenir. Çözücü devasa arama uzayını işte böyle yönetilebilir kılıyor."),
    ("p", "Ve şimdi her ikili değişkenin neden **pahalı** olduğunu anlayabiliriz: her ikili "
          "değişken, dallanma ağacında potansiyel bir çatallanma noktasıdır. Değişken sayısı "
          "arttıkça ağaç büyür."),

    ("h2", "3.5  İki sayı: incumbent ve bound"),
    ("p", "Çözücü çalışırken sürekli **iki** sayı tutar. Bunları karıştırmamak, Bölüm 9'u "
          "anlamanın anahtarıdır:"),
    ("tbl", (["", "Adı", "Ne demek", "Enbüyüklemede rolü"],
             [["**Elde olan**", "**incumbent**",
               "Şu ana kadar bulunmuş en iyi **GERÇEK** çözüm — tüm kısıtları sağlayan, tüm "
               "ikili değişkenleri gerçekten 0/1 olan bir tarife",
               "**ALT** sınır — optimum bundan **küçük olamaz**"],
              ["**Kanıt**", "**bound**",
               "LP gevşetmelerinden gelen \"cevap bundan iyi olamaz\" sınırı",
               "**ÜST** sınır — optimum bundan **büyük olamaz**"]],
             [2.6, 2.8, 7.4, 4.2], 8.4)),
    ("p", "Gerçek optimum bu iki sayının **arasında** bir yerdedir. Çözüm ilerledikçe "
          "incumbent yükselir, bound düşer; ikisi buluştuğunda (gap = 0) çözüm **kanıtlanmış "
          "optimaldir**."),
    ("eq", "**MIP gap  =  | bound − incumbent |  /  | incumbent |**"),
    ("box", ("Şimdiden bir uyarı",
             "Bizim gap'imiz %1,18 ve bu bir **belirsizlik** değil, bir **garantidir**: "
             "\"bulduğumuz çözüm, ulaşılabilecek en iyisinden en fazla %1,18 uzakta.\" "
             "Ama bu garanti tam olarak neyin garantisi — ve neyin değil — Bölüm 9'da "
             "titizlikle ayrılıyor. Jüri oradan soru sorarsa hazırlıklı olmalısınız.", "warn")),
]
