# RUHSAT-Bench — KUSUR KÜTÜĞÜ

Durma kuralı gereği (02.08.2026): yeni bulunan kusurlar KOVALANMAZ, buraya
yazılır. Kayıt üç soruya cevap verir: ne, etkisi ölçüldü mü, karar ne.

Etki testi referansı: v6→v7a yeniden puanlamada 32 hücrede |ΔBAcc|
ortalama 0.0046, maks 0.0347; hiçbir niteliksel sonuç değişmedi
(`sonuclar/uzlasi_nihai.txt` ve etki analizi).

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 1 | `maddeler()` `Ek Madde`/`Geçici Madde`yi ayrı birim yapmıyor; 75 parça ~76k karakter korpusta yok (3194 tek başına 50k) | Altın etkisi SIFIR (atılan metinden hiç iddia üretilmemiş — ölçüldü). F5 retrieval'ını etkiler | **DÜZELTİLECEK** (F5 öncesi, tek seferde) — görev listesi #1 |
| 2 | `bentler()` kaynaşması (456 tanınmayan başlık, 27 sahte birim) | 7 altın döndü (EK-5, uzman onaylı); etki testi geçti | KAPANDI — `bent_bol.py` ile |
| 3 | `kaynak_alinti` sütunu ~200 karakterde kırpık; P1/P2/P5'in %15'inde iddia içeriği alıntıdan uzun | Denetim 1. geçişinde uzmanlar kırpık alıntı gördüyse κ=1.00'a ek açıklama olabilir; `denetim_kitabi.py`'nin hangi alanı bastığı BAKILMADI | KÜTÜKTE — makale sınırlılığına aday; kovalanmıyor |
| 4 | id=391 (YDUY/14): `temizle_v39` şerh ayıklaması alıntı ortasına denk gelmiş, 441'de 1 katı eşleşme kaybı | Ölçüldü, tek madde, gevşek eşleşme buluyor | KAPANDI — dipnot |
| 5 | pypdf sürüm farkı: TBDY metni iki ortamda 870747/870751 karakter | Birim sayısı, kontroller, aday listesi AYNI çıktı (ölçüldü). **2026-08-27 DARALTILDI:** fark işletim sistemine değil, yalnız pypdf SÜRÜMÜNE bağlı — pypdf 5.9.0 ile macOS/py3.11.9 ve Ubuntu/py3.12.3 altı belgenin altısında da bayt-birebir metin verdi (Δkarakter=0, `metin_sha256` eşit) | KÜTÜKTE — makalede pypdf sürümü + metin hash verilecek; artık "iki ortam" değil "iki pypdf sürümü" diye yazılır |
| 6 | `f4_skor.py` ECE'si kova orta noktası kullanıyor (denetim 1.10; R3 ile kanıtlandı: doğru değer 0 iken 0.050 basıyor) | Sonnet ECE'si ~0.014 şişkin | **DÜZELTİLECEK** — analiz katmanında; R3 pozitif kontrol (ECE=0 vermeli) |
| 7 | `f4_skor.py` başlığı varyanttan bağımsız "varyant A" basıyor | Kozmetik | KÜTÜKTE |
| 8 | Sonda betiğinin hüküm kapısı fazla gevşekti (CI bandı kesişimi); B'nin kendi kol içi bandı yoktu | frontCB2 k1-3 ikilileri bandı verecek; analiz bekliyor | AÇIK — görev #4 içinde |
| 9 | Kesilen ≠ ayrıştırılamayan (etiket önce yazılınca kesilme veri kaybettirmiyor) | Sonda: 3 kesilmenin 1'i kayıp | KÜTÜKTE — raporlamada iki sayaç ayrı verilecek |
| 10 | `uretilen_iddialar_v6`'da `durum` sütunu ONAY_BEKLIYOR/YENI_EK ("frozen final" terminolojisiyle çelişiyor; denetim 1.18) | Kozmetik/terminoloji | KÜTÜKTE — v7a dondurulurken sütun güncellenmeli |

---

## Linux/TF-HPC geçişinde eklenenler (2026-08-27)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 11 | Git geçmişi kayboldu: Windows deposu (`D:\jestech\ruhsat-bench`) erişilemez, `git bundle` alınamadı | Dosya içerikleri tam (17/17 koştu, mühürlü üreteç iki pakette aynı sha256). Kaybolan: commit tarih damgaları → ön-kayıt-önceliği git ile kanıtlanamaz | KAPANDI — `REKONSTRUKSIYON.md` beyanı yazıldı; makale cümlesi §7'de |
| 12 | `f4_api_v2.py` hiçbir arşiv paketinde yoktu (HANDOVER dosya haritası depoda sayıyordu) | `yama_f4_api.py` ile deterministik yeniden üretildi; 4/4 yama, özdoğrulama geçti | KAPANDI |
| 13 | `f4_api.py`/`v2` hata mesajı PowerShell biçiminde ipucu basıyor (`$env:LLM_API_KEY = ...`) | Kozmetik. Anahtar okuma zaten doğru: `os.environ.get(--anahtar-env)` | KÜTÜKTE — donmuş dosya, dokunulmuyor |
| 14 | `uzlasi_birlestir.py` v7a/v7b'yi CRLF ile yazıyor (Linux'ta da) | İçerik etkilenmiyor (LF-normalize sonrası birebir aynı, ölçüldü); `.gitattributes` commit'te normalize ediyor | KÜTÜKTE — kovalanmıyor |
| 15 | `ollama_kur.sh` hedef ortamda **hiç koşulmadı** (konteynerde systemd yok; tarball + `setsid nohup` yolu belgeden yazıldı) | Ölçülmedi. Deterministik zincir bundan etkilenmiyor | AÇIK — ilk `--ollama` koşusunda ölçülecek, betikteki uyarı bloğu o zaman silinir |
| 16 | Windows koşularında kullanılan **Ollama sürümü hiçbir yerde kayıtlı değil** (`ORTAM.md` §8 model adlarını veriyor, sürümü vermiyor) | Ölçülemez (kaynak makine yok). GECIS_LINUX.md §7: model dosyalarının sürümler arası bayt-birebir aynı olacağı garanti değil | AÇIK — yerel kollar yeniden koşulursa yeni sürüm sonuç dosyalarına yazılıp beyan edilecek |

### TF-HPC ilk kurulumunda ölçülenler (2026-08-27)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 17 | JupyterHub'ın önündeki nginx yükleme boyutunu sınırlıyor: `413 Request Entity Too Large`. İkili aramayla ölçüldü — **704 KiB ham geçti, 768 KiB düştü** (base64 4/3 ile `client_max_body_size=1m`) | `data/` (9,6 MB) hiç gönderilemiyordu; deploy 1. adımda düşüyordu | KAPANDI — `put_bytes_parcali()`, `PARCA_HAM=640 KiB`. Pozitif kontrol: 3 MiB 5 parçada, sha256 birebir |
| 18 | `/workspace/env.sh` **MarkLLM'in** ve `~/.bashrc` onu source ediyor; `bootstrap.sh` üzerine yazacaktı | Yazsaydı MarkLLM'in `HF_HOME`/`TRANSFORMERS_CACHE`/`PYTHONPATH`'i silinirdi — paylaşılan konteynerde DİĞER proje bozulurdu. Deploy öncesi `ls /workspace` ile yakalandı, hasar OLUŞMADI | KAPANDI — ortam `/workspace/ruhsat-bench/env.sh`'e taşındı; MarkLLM'in dosyasına ve `~/.bashrc` satırına dokunulmuyor |
| 19 | numpy sürümü iki ortamda farklı: macOS 2.4.6, HPC 2.5.2 (`rank_bm25`'in geçişli bağımlılığı) | Kabul kapısından geçen zincir numpy KULLANMIYOR — 17/17 etkilenmedi (ölçüldü) | AÇIK — `f4_dayanak.py`'nin BM25'i numpy kullanacak; o koşudan önce iki sürümün aynı sıralamayı verdiği gösterilmeli ya da numpy pinlenmeli |
