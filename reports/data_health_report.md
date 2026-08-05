# TEKNOFEST Veri Sağlık Raporu

```

==========================================================================================
TEKNOFEST VERİ SAĞLIK RAPORU
==========================================================================================
Üretim tarihi: 2026-07-13 20:53

==========================================================================================
1) BAĞLANTI TABLOSU  (O&D Rakip Bağlantı Tablosu_updated.xlsx)
==========================================================================================
Boyut: (57317, 17)
Kolonlar: ['Cr1', 'Carrier Name', 'Dep1', 'Arr1', 'FlNo1', 'ElapsedTime1', 'Arr Time', 'Cr2', 'Dep2', 'Arr2', 'FlNo2', 'ML2', 'ElapsedTime2', 'Dep Time', 'Gate-to-Gate Uçuş Süresi', 'O&D', 'Gün']
ElapsedTime1/2 (bacak süreleri) mevcut: EVET -> J kesin hesaplanabilir
ML2 (taşıyıcı tipi, M=Mainline/L=Low-cost) dağılımı: {'M': 50832, 'L': 6485}

Arr Time aralığı: 2025-08-03 18:05:00 -> 2025-08-10 23:59:00
Dep Time aralığı: 2025-08-03 19:30:00 -> 2025-08-11 03:50:00
Gün değerleri: [1, 2, 3, 4, 5, 6, 7]

----------------------------------------------------------------------
Taşıyıcı dağılımı (Cr1)
----------------------------------------------------------------------
Toplam taşıyıcı: 88
Cr1
TK    7850
AF    5922
LH    5773
KL    3314
BA    2553
LX    2492
FR    2411
IB    1936
VY    1852
EK    1707
UA    1618
MU    1566
OS    1257
CX    1250
AZ    1020

TK satır: 7850  | Rakip satır: 49467

TK Arr1 (gelen bacağın varışı) benzersiz: ['IST']
TK Dep2 (giden bacağın kalkışı) benzersiz: ['IST']

O&D kolonu, (Dep1-Arr2) ile uyuşmayan satır sayısı: 0

Benzersiz O&D pazarı (yönlü): 1408
Benzersiz (O&D, Gün) anahtarı: 8864

TK bağlantısı OLAN pazar sayısı: 805
TK bağlantısı OLMAYAN (sadece rakip) pazar sayısı: 603
Rakip bağlantısı OLMAYAN (sadece TK) pazar sayısı: 266

==========================================================================================
2) TK BAĞLANTI GEÇERLİLİĞİ  (mevcut tarifede)
==========================================================================================
Bağlantı boşluğu (dk): min/medyan/max = 60.0 / 150.0 / 355.0
[60,300] penceresinde olan TK bağlantısı: 6986 / 7850  (89.0%)
Negatif boşluk (veri hatası?) sayısı: 0
Boşluk < L (kısa) : 0  | Boşluk > U (uzun): 864

Gate-to-Gate (J) dakika: min/medyan/max = 15.0 / 705.0 / 1435.0
J >= 24h (time formatında temsil edilemez!) sayısı: 0   -> uzun itineraryler 'time' alanında kırpılmış olabilir, KONTROL ET

----------------------------------------------------------------------
Bacak blok süresi ayrıştırma fizibilitesi
----------------------------------------------------------------------
Aynı (FlNo1,Gün) için farklı 'Arr Time' sayısı >1 olan grup: 132  (0 olmalı: bir gelen uçuşun tek IST varışı var)
Aynı (FlNo2,Gün) için farklı 'Dep Time' sayısı >1 olan grup: 1  (0 olmalı: bir giden uçuşun tek IST kalkışı var)
Benzersiz gelen TK uçuş örneği (FlNo1,Gün): 2740
Benzersiz giden TK uçuş örneği (FlNo2,Gün): 2731

==========================================================================================
3) RAKİP SÜRELERİ ve RAKİP SAYISI (N_od)
==========================================================================================
Rakip itinerary sayısı / (O&D,Gün): min/medyan/max = 1 / 4 / 90
Farklı rakip taşıyıcı / (O&D,Gün): min/medyan/max = 1 / 2 / 17
Rakip J (dk): min/medyan/max = 0.0 / 595.0 / 1435.0

NOT: N_od (rakip sayısı) tanımı netleştirilmeli — farklı itinerary mi, farklı taşıyıcı mı?
Ranking lookup 'Rakip Sayısı' aralığı: 1 - 40
Itinerary-bazlı rakip sayısı 40'ı aşan (O&D,Gün) sayısı: 73  | taşıyıcı-bazlı 40'ı aşan: 0

==========================================================================================
4) YOLCU VERİSİ / GELİR AĞIRLIĞI (ρ_od)
==========================================================================================
Boyut: (8075, 3)  | Kolonlar: ['Orig Airport Code', 'Dest Airport Code', 'OD importance factor']
ρ (önem) aralığı: 1 - 1000
Tekrarlı O-D satırı: 8  | Benzersiz O-D: 8066
Bağlantı tablosundaki pazar sayısı: 1408
ρ değeri OLMAYAN pazar sayısı: 48
  Örnek eksikler: ['KUL-PEK', 'CGK-PEK', 'KFS-VCE', 'TJK-VCE', 'HAN-PEK', 'ISE-VCE', 'PEK-HAN', 'PEK-SXZ', 'KIX-PEK', 'PEK-KUL']

==========================================================================================
5) RANKING ÖDÜL TABLOSU (change_ranking_input.xlsx)
==========================================================================================
Boyut: (22140, 4)  | Kolonlar: ['Rakip Sayısı', 'İlk Rank', 'Son Rank', 'Weight']
Weight aralığı: -0.9744 - 1.6321

N -> satır sayısı (ilk birkaç):
  N=1: 1 satır (beklenen N*N=1)
  N=2: 4 satır (beklenen N*N=4)
  N=3: 9 satır (beklenen N*N=9)
  N=4: 16 satır (beklenen N*N=16)
  N=5: 25 satır (beklenen N*N=25)
  N=6: 36 satır (beklenen N*N=36)
Son Rank > İlk Rank olan satır (sıralama kötüleşmesi): 10660
İlk Rank > Rakip Sayısı olan (tutarsız) satır: 0

==========================================================================================
6) FLIGHT PAIRS / ROTASYON (Flight Pairs.xlsx)
==========================================================================================
Boyut: (1562, 4)  | Kolonlar: ['FlNo', 'Orig', 'Dest', 'Pair']
Benzersiz Pair: 708  | Benzersiz FlNo: 1381
Pair başına uçuş sayısı dağılımı: {2: 617, 4: 44, 3: 40, 6: 2, 1: 2, 5: 2, 8: 1}
IST'ten kalkan (Orig=IST) uçuş: 746  | IST'e gelen (Dest=IST): 747

Bağlantı tablosundaki benzersiz TK uçuş no: 952
Flight Pairs'teki uçuş no: 1381
TK uçuş no'su olup Flight Pairs'te OLMAYAN: 176
Flight Pairs'te olup bağlantı tablosunda kullanılmayan uçuş no: 605

==========================================================================================
7) ÖZET / AÇIK SORULAR (modellemeden önce karara bağlanmalı)
==========================================================================================
- N_od tanımı: rakip = farklı itinerary mi, farklı taşıyıcı mı? (ranking ödülünü doğrudan etkiler)
- Gate-to-Gate 'time' formatı 24h'i aşan itineraryleri kırpıyor olabilir — uzun pazarları doğrula.
- T_IB / T_OB bacak blok sürelerini connection'dan ayrıştırma stratejisi (J - boşluk = sabit).
- Ayar pencereleri (Standard: sınır yok) — gün-içi düzenlilik (X_dev=15dk) ve hub kovaları (10dk) ile etkileşim.
- ρ eksik pazarlar için varsayım (0 mı, ortalama mı, ele mi?).
- Constraint H (slot pencereleri) sadece sunumda — dahil edilecek mi netleştir.
```
