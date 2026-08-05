# -*- coding: utf-8 -*-
"""
TEKNOFEST Havayolu Optimizasyonu — Teslim Dokümanı Dışa Aktarma (4. adım)

Markdown kaynaklarından teslim biçimlerini üretir:
  .md → .docx  (pandoc / pypandoc)
  .docx → .pdf (Microsoft Word COM otomasyonu; Word yüklü değilse atlanır ve
                'Word'de açıp Farklı Kaydet → PDF' notu basılır)

Çalıştırma:  python src/04_export_docs.py   (proje kökünden)
Brief §5: model dokümanı PDF ister; teknik rapor ve sonuç özeti de aynı akışla üretilir.
"""

import os
import subprocess
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

DOCS = [
    os.path.join(ROOT, "docs", "model_formulation.md"),
    os.path.join(ROOT, "reports", "technical_report.md"),
    os.path.join(ROOT, "output", "results_summary.md"),
]


def md_to_docx(md_path):
    import pypandoc  # yoksa main() bunu yakalar ve adım atlanır (koşu durmaz)
    docx_path = os.path.splitext(md_path)[0] + ".docx"
    # --resource-path: md içindeki göreli görsel yolları (docs/figures/…) proje kökünden
    # ve dosyanın kendi klasöründen çözülsün (pandoc varsayılanı yalnız CWD'dir)
    res = os.pathsep.join([ROOT, os.path.dirname(md_path)])
    pypandoc.convert_file(md_path, "docx", outputfile=docx_path,
                          extra_args=["--resource-path", res])
    print(f"[docx] {os.path.relpath(docx_path, ROOT)}")
    return docx_path


def docx_to_pdf(docx_path):
    """Word COM üzerinden PDF (wdFormatPDF=17). PowerShell ile — ek Python bağımlılığı yok."""
    pdf_path = os.path.splitext(docx_path)[0] + ".pdf"
    ps = (
        "$ErrorActionPreference='Stop';"
        "$word = New-Object -ComObject Word.Application;"
        "$word.Visible = $false;"
        f"$doc = $word.Documents.Open('{docx_path}');"
        f"$doc.SaveAs('{pdf_path}', 17);"
        "$doc.Close($false); $word.Quit()"
    )
    r = subprocess.run(["powershell", "-NoProfile", "-Command", ps],
                       capture_output=True, text=True)
    if r.returncode == 0 and os.path.exists(pdf_path):
        print(f"[pdf ] {os.path.relpath(pdf_path, ROOT)}")
    else:
        print(f"[pdf ] ÜRETİLEMEDİ ({os.path.basename(docx_path)}): Word COM hatası — "
              f"dosyayı Word'de açıp 'Farklı Kaydet → PDF' ile dışa aktarın.\n{r.stderr.strip()}")


def main():
    try:
        import pypandoc  # noqa: F401 — varlık kontrolü
        pypandoc.get_pandoc_version()
    except Exception as e:
        print(f"[atla] pypandoc/pandoc bulunamadı ({e}) — docx/pdf üretimi atlandı; "
              "teslimdeki hazır .docx/.pdf dosyaları geçerlidir. "
              "(Kurulum: pip install pypandoc_binary)")
        return
    for md in DOCS:
        if not os.path.exists(md):
            print(f"[atla] bulunamadı: {md}")
            continue
        docx = md_to_docx(md)
        docx_to_pdf(docx)


if __name__ == "__main__":
    main()
