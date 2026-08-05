"""
TEK KOMUTLA UÇTAN UCA KOŞU — teslimin tamamını sıfırdan üretir. (Takım: Büke)

  python run_all.py                    veri sağlığı → hazırlama → model (byday λ=0.3)
                                       → tam-hafta warm-start cilalaması (≤1800 s)
                                       → bağımsız doğrulama → figürler → docx/pdf
                                       (toplam ~35–40 dk; ~30 dk'sı cilalama adımı)
  python run_all.py --with-sensitivity ayrıca λ/Wdev/τ duyarlılık taraması (~15–30 dk)

Her adım ayrı süreçte koşar; bir adım başarısız olursa akış AÇIK hata ile durur
(bağımsız doğrulayıcının FAIL'i de koşuyu durdurur — çözüm doğrulanmadan teslim edilmez).
"""

import os
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src")

STEPS = [
    ("Veri sağlık kontrolü", ["01_data_health_check.py"]),
    ("Veri hazırlama (derived/)", ["02_data_prep.py"]),
    ("MIP modeli — tam veri, güne göre (λ=0.3)", ["03_model.py", "byday"]),
    # 08: byday çözümünü tam-hafta MIP'ine MIP-start verip küresel iyileştirir;
    # iyileşme yoksa byday çıktısını korur (koşuyu durdurmaz). Süre: 1800 s.
    ("Tam-hafta warm-start cilalaması", ["08_fullweek_polish.py", "1800"]),
    ("Bağımsız çözüm doğrulama", ["05_validate_solution.py"]),
]
if "--with-sensitivity" in sys.argv:
    STEPS.append(("Duyarlılık analizi (λ, Wdev, τ)", ["07_sensitivity.py"]))
STEPS += [
    ("Rapor figürleri", ["06_make_figures.py"]),
    ("Teslim dokümanları (.docx/.pdf)", ["04_export_docs.py"]),
]


def main():
    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    t_all = time.time()
    for i, (name, cmd) in enumerate(STEPS, 1):
        print(f"\n{'=' * 74}\n[{i}/{len(STEPS)}] {name}  —  python src/{' '.join(cmd)}\n{'=' * 74}")
        t = time.time()
        r = subprocess.run([sys.executable, os.path.join(SRC, cmd[0]), *cmd[1:]],
                           cwd=ROOT, env=env)
        if r.returncode != 0:
            print(f"\n!! ADIM BAŞARISIZ ({name}, çıkış kodu {r.returncode}) — koşu durduruldu.")
            sys.exit(r.returncode)
        print(f"[{i}/{len(STEPS)}] tamam ({time.time() - t:.0f}s)")
    print(f"\n>> TÜM ADIMLAR TAMAM ({(time.time() - t_all) / 60:.1f} dk). "
          f"Teslim çıktıları: output/ · docs/ · reports/")


if __name__ == "__main__":
    main()
