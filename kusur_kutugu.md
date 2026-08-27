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
| 5 | pypdf sürüm farkı: TBDY metni iki ortamda 870747/870751 karakter | Birim sayısı, kontroller, aday listesi AYNI çıktı (ölçüldü) | KÜTÜKTE — makalede pypdf sürümü + metin hash verilecek |
| 6 | `f4_skor.py` ECE'si kova orta noktası kullanıyor (denetim 1.10; R3 ile kanıtlandı: doğru değer 0 iken 0.050 basıyor) | Sonnet ECE'si ~0.014 şişkin | **DÜZELTİLECEK** — analiz katmanında; R3 pozitif kontrol (ECE=0 vermeli) |
| 7 | `f4_skor.py` başlığı varyanttan bağımsız "varyant A" basıyor | Kozmetik | KÜTÜKTE |
| 8 | Sonda betiğinin hüküm kapısı fazla gevşekti (CI bandı kesişimi); B'nin kendi kol içi bandı yoktu | frontCB2 k1-3 ikilileri bandı verecek; analiz bekliyor | AÇIK — görev #4 içinde |
| 9 | Kesilen ≠ ayrıştırılamayan (etiket önce yazılınca kesilme veri kaybettirmiyor) | Sonda: 3 kesilmenin 1'i kayıp | KÜTÜKTE — raporlamada iki sayaç ayrı verilecek |
| 10 | `uretilen_iddialar_v6`'da `durum` sütunu ONAY_BEKLIYOR/YENI_EK ("frozen final" terminolojisiyle çelişiyor; denetim 1.18) | Kozmetik/terminoloji | KÜTÜKTE — v7a dondurulurken sütun güncellenmeli |
