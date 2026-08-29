# v7c GEÇERSİZ — neden arşivde duruyor

**Tarih:** 2026-08-29 · Proje kuralı: başarısız denemeler silinmez, arşivlenir.

## Ne yapıldı
`uretilen_iddialar_v7a.csv`'den üç altın etiket DOĞRU→YANLIŞ çevrildi: **278, 426, 444**.
Gerekçe: 17 açık vaka karar kitabında bu üç iddianın alıntısı, CSV'nin `madde`
sütununun gösterdiğinden başka bir birimde bulunuyordu.

## Neden GEÇERSİZ

**Asistan hatası: `madde` sütunu iddianın ATIF YAPTIĞI yer sanıldı.**

EK-4 §2 harfiyen:

> "CSV'nin `kanun`/`madde` sütunları iddianın ATIF YAPTIĞI yeri değil, metnin
> GERÇEK KAYNAĞINI tutar. P5'te bu ikisi kasten farklıdır."

Karar kitabı bu sütunu "CSV_kanun_madde" diye sunup görevi *"atıf yanlışsa iddia
yanlıştır"* diye tarif etti. Bu, **madde düzeyi** atıflar için doğru, **belge
düzeyi** atıflar için yanlıştır.

## Ölçülen ayrım

| grup | atıf düzeyi (`atif_coz`) |
|---|---|
| Uzmanların döndürdüğü 7 (246, 257, 304, 360, 364, 382, 393) | **7/7 madde düzeyi** — *"TBDY 2018'in 2.1.2 numaralı bendine göre..."* |
| v7c'de çevrilen 3 (278, 426, 444) | **3/3 belge düzeyi** — *"TBDY 2018'e göre..."* |

EK-4 §9(d): *"Belge düzeyinde atıf → belgenin tamamında aranır."*
Üç iddianın da içeriği TBDY 2018'de **vardır** (14.15.4, 15.2.2, 15.2.12).
Dolayısıyla iddialar DOĞRUdur ve v7a'daki etiketleri zaten doğruydu.

## Bunu ne yakaladı

**Kural tabanlı taban R3.** v7a ile 473/473 veren R3, v7c ile 470/473'e düştü ve
uyuşmadığı üç id tam olarak 278, 426, 444 çıktı. Gerekçe alanı üçünde de
`belge duzeyi TBDY` yazıyordu.

Yani ön-kayıtlı deterministik taban, altın etiketteki bir hatayı yakaladı.
Bu, R3'ün makaledeki rolü için doğrudan bir örnektir.

## Sonuç

* **Birincil altın v7a olarak KALIR** (223 DOĞRU / 250 YANLIŞ).
* 17 vakadan **hiçbiri** etiket değişikliği gerektirmiyor.
* Karar kitabındaki 323 kararı (`degisiklik_yok`) zaten doğruydu.
* `KODLAYICI` alanındaki provenans sorunu ayrıca duruyor
  (`uzlasi/17_VAKA_KARARLARI_ve_DOGRULAMA.md` §1).
