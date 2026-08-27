# REKONSTRÜKSİYON BEYANI — RUHSAT-Bench deposu

**Tarih:** 2026-08-27 · **Yapan:** Claude Code (macOS) · **Kullanıcı onayı:** var (Windows deposuna erişim yok beyanı)

Bu belge, deponun git geçmişinin neden 2026-08-27'de başladığını ve bunun
neyi kanıtlayıp neyi kanıtlamadığını kayda geçirir. `GECIS_LINUX.md` §0 ve §1
bu durumu öngörmüş ve "makalede açıkça beyan edilir" demişti; bu, o beyandır.

---

## 1. Ne oldu

Özgün depo **`D:\jestech\ruhsat-bench`** (Windows, RDP, PowerShell 5.1) idi.
Beyan zinciri — *"her ön-kayıt koşudan önce, tarih damgalı"* iddiasının kanıtı —
o deponun **commit geçmişinde** yaşıyordu.

Kullanıcı 2026-08-27'de o makineye **erişimi olmadığını** bildirdi. `git bundle`
alınamadı. `GECIS_LINUX.md` §1'in tarif ettiği doğru yol (bundle → klon) bu
yüzden kullanılamadı.

Depo, kullanıcının Mac'inde duran **paket arşivlerinden yeniden kuruldu**.

## 2. Ne KAYBOLDU

- **Commit tarih damgaları.** Git geçmişi 2026-08-27'de başlar. Bir ön-kaydın
  ilgili koşudan önce yazıldığı **git ile kanıtlanamaz**.
- Commit mesajları, dal yapısı, yazar kayıtları, `e9c337f` gibi karma değerleri.
- Ara sürümlerin diff geçmişi (yalnız paketlenmiş son haller elde).

## 3. Ne KORUNDU

- **Dosya içeriklerinin tamamı, bayt düzeyinde.** Aşağıdaki paketlerin sha256'ları
  kayıtlı; her dosya bu paketlerden geldi, elle düzenlenmedi.
- **Beyan dosyalarının kendi içindeki tarihler.** `F4_on_kayit*.txt`,
  `ORTAM.md`, `HANDOVER.md` metinlerinde yazılı tarihler duruyor. Bunlar
  git damgası kadar güçlü değildir (sonradan yazılabilirdi) ama **paket
  arşivlerinin içindeki dosya mtime'ları** onları destekler (§4).
- **Zip içi mtime damgaları.** `ruhsat-bench_arsiv_20260801.zip` içindeki
  dosyalar 2026-07-24 – 2026-08-01 aralığında damgalı; bu damgalar arşiv
  2026-08-01'de paketlendiğinde dondu ve o günden beri değişmedi.
- **Bağımsız bütünlük kontrolü (ölçüldü):** mühürlü üreteç
  `scripts/uret_iddia_v3_6.py`, **birbirinden bağımsız iki pakette** (28 Temmuz
  teslim paketi ve 1 Ağustos arşivi) **birebir aynı sha256** ile bulundu:
  `291f61f21b8d3ead176d75285a40140a9439ad419485aa860b8e49cfb0ce474d`.
  Mühür, iki ayrı paketleme anı arasında bozulmamış.
- **Devir paketinin bütünlüğü (ölçüldü):** 31 dosyanın 31'i
  `RUHSAT-Bench_claude_devir_20260802.zip` içeriğiyle bayt-aynı; 0 fark.

## 4. Kaynak paketler (sha256, 2026-08-27'de ölçüldü)

| paket | sha256 | iç mtime aralığı | ne getirdi |
|---|---|---|---|
| `ruhsat-bench_arsiv_20260801.zip` | `3acaefd8a086e8979eb84d48b2de7a342fce00bc0eb2e3438a36ff684cd12027` | 2026-07-24 → 2026-08-01 | 34 arşiv betiği (mühürlü üreteç, `f4_skor.py`, `f4_api.py`), 61 koşu/rapor çıktısı, 20 iddia dosyası |
| `kaynak_pdf.zip` | `35521dde3ed3427153cbe30eea24297c59a778930516f644cfa477647d07d8f7` | 2026-07-24 → 2026-07-28 | 11 kaynak PDF (6 mevzuat + 5 "taze" kopya) |
| `RUHSAT-Bench_teslim_paketi.zip` | `fc343dfc8fb9fc8ea85502b63ceeea14fd196ec16ab3693d2981f0dde6d590da` | 2026-08-01 | `ORTAM.md`, makale taslakları, üçüncü göz istemi |
| `RUHSAT_uzlasi_paketi.zip` | `b410b5f118d57d68a2f2640ad8eb890a9bed1b14c99f310c8440a80634f4ed53` | 2026-08-02 | boş uzlaşı kitabı şablonu |
| `RUHSAT-Bench_claude_devir_20260802.zip` | `fa116f6acf83b0f1144e8df9b4cb7041eb3f2fe8486b8ae819f3ad294e18c562` | (yeniden damgalı) | 15 yeni betik, EK-4/EK-5, v7a/v7b altın, `GECIS_LINUX.md`, `HANDOVER.md`, `kusur_kutugu.md` |

Zip'lenmemiş, tekil indirilen dosyalar (mtime 2026-08-02):

| dosya | sha256 |
|---|---|
| `kodlayici1_uzlasi_kitabi_doldurulmus.xlsx` | `1411fc7f318e21f621914c957a92f7d74ecb6deed803c13f5f591a0827360cb2` |
| `kodlayici2_uzlasi_kitabi_secenek1.xlsx` | `04d5c486e5edd8894f057e13d5381fc23db5659d38fb06ecbf29b9aec2fa34db` |
| `uzlasi/kodlayici1_UZLASI_KURAL_NOTU_doldurulmus.md` | `ee99d508613a149017e7fe7d700e177c219ecdc8a43faedb7465858dab461e3f` |
| `uzlasi/kodlayici2_UZLASI_KURAL_NOTU_DOLU.md` | `7674a8843beed2cae2eab9ba4434bd7a2096d0c1f2db3c9e2caefc22974c386b` |
| `belgeler/RUHSAT_Bench_Ucuncu_Goz_Raporu_2026-08-01.md` | `addd99faec980504e91c3e4ebc83745f36f23858933f157eecd51b92ccd69d0a` |

> Türkçe noktasız-ı taşıyan özgün dosya adları (`kodlayıcı1_…`) depoya
> ASCII'leştirilerek alındı (`kodlayici1_…`); **içerik değişmedi**, yalnız ad
> değişti. `scripts/dogrula_linux.sh` §5 `kodlay*1*.xlsx` kalıbı ikisini de yakalar.

## 5. Yerleşim kararları (özgün yerleşimden farklar)

- `data/uretilen_iddialar_v7{a,b}.csv` → `data/iddialar/` altına taşındı
  (arşivdeki diğer iddia dosyalarıyla aynı yerde olsun diye;
  `dogrula_linux.sh` zaten `data/iddialar/` bekliyor).
- Kök dizindeki `dogrula_linux.sh` kaldırıldı: `scripts/dogrula_linux.sh` ile
  **bayt-aynıydı** (ölçüldü). Kanonik kopya `scripts/` altında.
- `F4_on_kayit.txt`, `_ek`, `_ek2`, `_ek3` arşivdeki yerinde (`sonuclar/`) bırakıldı;
  `beyanlar/` yalnız devir paketinin getirdiği `_ek4` ve `_ek5`'i tutar.
  Beyan zinciri iki dizine yayılıdır — kopyalanmadı, çünkü tek dosyanın iki
  kopyası provenansı zayıflatır.
- Yeni dizinler: `makale/` (taslaklar), `belgeler/` (üçüncü göz raporu, eski HANDOVER,
  OKUBENI).

## 6. Satır sonu sınırı

`GECIS_LINUX.md` §2.5 uyarınca satır sonları LF'e normalize edildi. Bu iş
**ayrı ve etiketli bir commit**tir; öncesindeki commit, dosyaları Windows'tan
geldikleri **ham bayt hâliyle** tutar. Böylece normalize edilmemiş baytlar
`git show` ile geri alınabilir.

Etkilenen dosyalar ve ölçüm `sonuclar/port_satirsonu_raporu.txt` içindedir.

Makale beyanı (tek cümle, değişmedi): *"Depo Linux'a taşınırken satır sonları
normalize edilmiştir; betik hash'leri bu commit öncesi/sonrası ayrı ailelerdir."*

## 7. Bu beyanın makaledeki karşılığı

> Çalışmanın deposu 2026-08-27'de kaynak makineye erişim kaybı nedeniyle
> paketlenmiş arşivlerden yeniden kurulmuştur. Dosya içerikleri arşiv
> sha256'larıyla doğrulanabilir; ancak commit tarih damgaları kaybolmuştur ve
> ön-kayıtların ilgili koşulardan önce yazıldığı git geçmişiyle
> kanıtlanamamaktadır. Ön-kayıt metinlerinin kendi içindeki tarihler ve
> arşivlerin dosya damgaları destekleyici, git damgasına eşdeğer olmayan
> kanıttır.
