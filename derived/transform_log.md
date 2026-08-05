# TEKNOFEST Veri Hazırlama — dönüşüm logu
Üretim: 2026-07-13 20:53 | Politika: minimal+belgeli
Yapılandırma: {'L_min': 60, 'U_min': 300, 'tau_min': 45, 'dewrap': 'minimal', 'n_od_def': 'carrier', 'missing_rho': 'exclude'}

Okundu (salt-okunur): bağlantı=(57317, 17) [O&D Rakip Bağlantı Tablosu_updated.xlsx], yolcu=(8075, 3), ranking=(22140, 4), pair=(1562, 4)

[J KESİN] ElapsedTime1/2 mevcut -> J = E1 + boşluk + E2 (wrap belirsizliği YOK)
  Gate-to-Gate ile mod-24sa tutarsız satır: 0 (0 beklenir)
  24 saati aşan gerçek yolculuk: 495 satır (eski şemada bunlar sarılı görünüyordu)
  Eski minimal de-wrap'in yanlış hesaplayacağı satır: 154 (TK: 29, rakip: 125)

[Hafta normalizasyonu] geri çekilen satır: 132 (7'nin katı olmayan, dokunulmayan: 0)
  Tekil (uçuş,gün,zaman) olay: 5604 -> 5474 (birleşen hafta-kopyası: 130; boşluk/J değişmedi)
  Birebir özdeş aday satırı tekilleştirildi: 157 (7850 -> 7693 aday)

[TK bağlantı] 7693 aday | pencere içi: 6843 (89.0%)

[Blok süreleri] TK bacak blokları (A2 için): 5471 (FlNo,gün,rol) kaydı | çok-değerli grup (max alındı): 173

[ML2] Taşıyıcı tipi sütunu mevcut: {'M': 42982, 'L': 6485} (M=Mainline, L=Low-cost; ranking'e etkisiz, bilgi amaçlı taşındı)

[Rakip] 49467 itinerary | taşıyıcı-bazlı T_comp satırı: 23975
  N_od (carrier) aralığı: 1–17 | ranking lookup max N=40 -> kapsam TAM

[Pazar] 1408 yönlü pazar | ρ eksik: 48 -> politika='exclude' (dışlanan: 48)
  TK olan: 805 | sadece-rakip: 603

[Rotasyon] TK uçuş no: 952 | Flight Pairs'te eşi olan: 776
  Partnersiz TK uçuş no: 176 -> politika: 'ayarlanamaz/sabit' kabul (kısıt eklenmez)
