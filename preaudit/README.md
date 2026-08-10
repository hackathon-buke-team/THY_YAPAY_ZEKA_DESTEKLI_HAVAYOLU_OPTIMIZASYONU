# Ön-Denetim Betikleri (final sunumu hazırlığı)

**Takım Büke** · TEKNOFEST Yapay Zekâ Destekli Havayolu Optimizasyonu

Bu klasör, final öncesinde **kendi çözümümüze rakip bir hakem gibi saldırmak** için yazılmış
bağımsız ölçüm betiklerini içerir. Hiçbiri `src/` altındaki koddan bir şey import etmez;
yalnız `data/`, `derived/` ve `output/` dosyalarını okuyup sıfırdan yeniden hesaplar.

Bulguların tamamı ve hazır jüri cevapları:
`docs/Buke_FINAL_Sunum_Hazirlik_Dosyasi.docx` → **§13.11** ve **§15.2b**.

## Çalıştırma

```bash
python preaudit/01_iddia_dogrulama.py              # rho cakismasi, rotasyon kapsami, G bandi, duplicate
python preaudit/02_izgara_ve_rotasyon_olcumu.py    # IZGARA ARTEFAKTI + A2 korumasiz ucuslar
python preaudit/03_kapasite_E1_baglanti_olcumu.py  # F kova asimlari, E1 baseline ihlali, kayip/kazanc
python preaudit/04_urun_kalitesi_ve_marjlar.py     # urun kalitesi, MCT sinir riski, yenme marjlari
python preaudit/05_ikili_degisken_sayimi.py        # ikili degisken sayimi denetimi
python preaudit/06_amac_evreni_disi_sabitler.py    # "HANGILERI?" — extra_use / fixed_flnos / full_role_time
python preaudit/07_rakip_bazli_kazanim.py          # rakip bazli ONCE/SONRA yenme tablosu
python preaudit/08_kapali_kisit_kanitlari.py       # E2 / B2 / G — kapali kisitlarin SAYISAL kaniti
```

> 06 ve 07 `output/audit_*.csv` ve `output/rakip_kazanim_*.csv` uretir; bunlari
> `python src/09_rakip_figurleri.py` (PNG) ve `python src/10_rakip_panosu.py`
> (tek sayfalik HTML pano) tuketir.

Her biri saniyeler sürer; ek bağımlılık gerektirmez (pandas + numpy + openpyxl).

## Ölçülen başlıca bulgular

| # | Bulgu | Sayı |
|---|---|---|
| 1 | **Izgara artefaktı** — baseline ham dakika, model 10 dk ızgara | +21.597 puan = kazancın **%14,1'i**; ızgara-tutarlı iyileşme **+%4,03** (raporlanan +%4,72) |
| 2 | **A2 rotasyon kapsam boşluğu** — 512 Pair'in yalnız 291'i kullanılabilir | 221 uçuş korumasız; 100'ü oynatılmış, 248 hareket = tüm kaydırmaların **%23,2'si** |
| 3 | **Flight Pairs farklı sezon** — sayfa adı `W26 Flight Pair 20260227` | Tarife verisi Ağustos 2025 (Yaz); eşleştirme Kış 2026 |
| 4 | **ρ çakışması** — 6 pazarda çelişkili değer, `keep='first'` | PEK–AGP 45 vs 627 (13,9 kat) dâhil |
| 5 | **Sıralama ödülü ölü bölgesi** — W(1,1,1)=0 | 2.638 / 4.660 pazar-gün = **%56,6** |
| 6 | ~~**G muafiyet oranı** 1.131 / 2.644 = %42,8~~ **DÜZELTİLDİ (08)** — payda yanlıştı: 2.644 doğrulayıcının *denetlediği* bağ sayısı; toplam bağ = 2.644 + 1.131 = **3.775** | gerçek oran **1.131/3.775 = %30,0** |
| 7 | **Bağlantı takası** | +529 kazanılan / −311 kaybedilen = net **+218** (ρ bazında ~2:1 lehte) |
| 8 | **Ürün karması** — itiraza karşı çürütme | En iyi bant 60–90 dk: 1.187 → **1.332 (+145)**; medyan bekleme 140 dk'da **değişmedi** |
| 9 | **MCT sınır riski** | Tam 60 dk bekleyen: 202 (%3,0) → **541 (%7,8)** |
| 10 | **Rakip yenme marjları** | Medyan marj **110 dk**; <30 dk marjla kazanılan %15,4 |
| 11 | **Mevcut tarifenin ihlalleri** (bizim sağladığımız) | F: 96 kova · E1: 379 / 2.001 yön-çifti · G: 157 / 3.775 bağ (bizde 105) |
| 12 | **E2 yapısal ayrıştırma** (08) — farkın ne kadarı fizik? | Aktif yön-çiftlerinin **%62,7'sinde** Γ=30 dk imkânsız (10 çift) veya **ancak ürünü bozarak** (1.237 çift, toplam **46.695 dk** bozulma). İhlallerin %71'i **yalnız blok süresi** farkından. |
| 13 | **B2 ihlallerinin kaynağı** (08) | Nihai çözümde B2 uyumu **%96,86** (aşama-1'deki %90,8 değil). Sunulmayan 226 uygun bağlantının **%100'ü** eklendiğinde E1'i ihlal ediyor ⇒ **bizim tercihimiz değil, E1 zorlaması**. |
| 14 | **G muafiyetleri fiilen kullanılmadı** (08) | 1.131 muafiyetin **1.026'sı (%90,7)** ±15 dk bandında kaldı. Gerçekten bant dışı **105 bağ (%2,8)**; bunların **%43,8'i mevcut tarifeden miras**. G fiilen **%97,2** sağlanıyor. *Karşı-bulgu: toplam yayılım 7.850 → 14.270 dk arttı.* |

> **Not:** Bulgu 1 ve 2 manşet rakamın yorumunu etkiler. İkisi de dokümanda açıkça
> raporlanmıştır; sunumda **sorulmadan önce** dile getirilmesi tavsiye edilir.
>
> Bulgu 12–14'ün tam anlatımı, birebir brief alıntıları ve jüri cevap kartları:
> `docs/Buke_KISIT_REFERANS_ve_KANIT.pdf`
