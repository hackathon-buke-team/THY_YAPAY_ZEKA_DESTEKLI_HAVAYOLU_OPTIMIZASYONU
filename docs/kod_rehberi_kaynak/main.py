# -*- coding: utf-8 -*-
"""Kod Rehberi DOCX — ana kurucu."""
import os
import sys
import importlib

from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

from builder import Doc, BLUE, BLUE_D, INK, INK2, MUTED, GREEN, RED

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = r"C:\Users\darkb\Desktop\Buke_cozum\docs\Buke_KOD_REHBERI.docx"

MODULES = ["content_00", "content_01", "content_02", "content_03",
           "content_08", "content_05", "content_06_07_04", "content_ek"]


def cover(D):
    d = D.d
    for _ in range(3):
        D.spacer(10)
    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(2)
    r = p.add_run("TEKNOFEST · Yapay Zekâ Destekli Havayolu Optimizasyonu")
    r.font.size = Pt(11); r.font.color.rgb = MUTED; r.font.name = "Segoe UI"

    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(0)
    r = p.add_run("KOD REHBERİ")
    r.font.size = Pt(40); r.bold = True; r.font.color.rgb = BLUE_D; r.font.name = "Segoe UI"

    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run("src/ klasöründeki her modülün, blok blok anlatımı")
    r.font.size = Pt(14); r.font.color.rgb = INK2; r.font.name = "Segoe UI"

    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_after = Pt(26)
    r = p.add_run("Takım: Büke")
    r.font.size = Pt(12); r.bold = True; r.font.color.rgb = INK; r.font.name = "Segoe UI"

    D.img("f01_pipeline.png", None, 16.0)

    D.spacer(6)
    D.tbl(["Dosya", "Satır", "Rolü", "Bölüm"],
          [["`01_data_health_check.py`", "232", "Veri sağlık kontrolü — teşhis raporu", "1"],
           ["`02_data_prep.py`", "321", "Veri hazırlama — `derived/` katmanı", "2"],
           ["`03_model.py`", "1357", "MIP modeli, çözüm ve çıktı (**çekirdek**)", "3"],
           ["`08_fullweek_polish.py`", "596", "Tam-hafta warm-start cilalaması", "4"],
           ["`05_validate_solution.py`", "470", "Bağımsız doğrulayıcı (çift kayıt)", "5"],
           ["`06_make_figures.py`", "172", "Rapor figürleri (PNG)", "6"],
           ["`07_sensitivity.py`", "133", "Duyarlılık analizi (λ, Wdev, τ)", "7"],
           ["`04_export_docs.py`", "83", "Markdown → DOCX/PDF dönüşümü", "8"],
           ["`run_all.py`", "56", "Tek komutla uçtan uca koşu", "9"]],
          [5.2, 1.6, 8.4, 1.8], 8.8)

    p = d.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run("Toplam 3.364 satır Python · Pyomo + HiGHS · tüm açıklamalar Türkçe")
    r.font.size = Pt(9); r.italic = True; r.font.color.rgb = MUTED; r.font.name = "Segoe UI"


def toc(D):
    D.pagebreak()
    D.h2("İçindekiler")
    rows = [
        ["**0**", "Kuşbakışı — proje ne yapıyor, kod nasıl bölünmüş?",
         "problem · sözlük · boru hattı · kısıt haritası"],
        ["**1**", "`01_data_health_check.py` — Veri Sağlık Kontrolü",
         "teşhis raporu · veri tuzakları"],
        ["**2**", "`02_data_prep.py` — Veri Hazırlama",
         "de-wrap · hafta normalizasyonu · `derived/`"],
        ["**3**", "`03_model.py` — MIP Modeli (çekirdek)",
         "A1–G kısıtları · amaç · çözücü · byday"],
        ["**4**", "`08_fullweek_polish.py` — Tam-Hafta Cilalama",
         "warm-start · global MIP-gap · bariyer"],
        ["**5**", "`05_validate_solution.py` — Bağımsız Doğrulayıcı",
         "çift kayıt · 12 kontrol · PASS/FAIL"],
        ["**6**", "`06_make_figures.py` — Rapor Figürleri", "4 PNG · palet · stil"],
        ["**7**", "`07_sensitivity.py` — Duyarlılık Analizi", "λ · Wdev · τ taramaları"],
        ["**8**", "`04_export_docs.py` — Doküman Dışa Aktarma", "pandoc · Word COM"],
        ["**9**", "`run_all.py` — Uçtan Uca Koşu", "adım sırası · hata yönetimi"],
        ["**A**", "Ek A — Hızlı başvuru", "sabitler · CFG · komutlar · çıktı dosyaları"],
        ["**B**", "Ek B — Kodla ilgili muhtemel jüri soruları", "12 soru ve cevabı"],
    ]
    D.tbl(["#", "Bölüm", "İçerik"], rows, [1.2, 8.0, 7.8], 9.2)


def main():
    sys.path.insert(0, HERE)
    D = Doc()
    cover(D)
    toc(D)
    for mod in MODULES:
        try:
            m = importlib.import_module(mod)
        except ModuleNotFoundError:
            print("[atla] henüz yok:", mod)
            continue
        print("[render]", mod, f"({len(m.ITEMS)} öğe)")
        D.render(m.ITEMS)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    D.save(OUT)


if __name__ == "__main__":
    main()
