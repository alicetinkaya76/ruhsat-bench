# submission/jestech — gönderim paketi

**Hedef dergi:** Engineering Science and Technology, an International Journal
(JESTECH), Elsevier · ISSN 2215-0986

## Dosyalar

| dosya | ne | JESTECH'e yüklenir mi |
|---|---|---|
| `00_TITLE_PAGE.md` | başlık, yazar, kurum, ORCID, kelime sayısı, veri bağlantıları | evet, ayrı dosya |
| `01_MANUSCRIPT.md` | ana metin, 10.933 kelime | **evet, ana dosya** |
| `02_SUPPLEMENTARY_S1-S9.md` | ek materyal, 9.438 kelime | evet, supplementary |
| `03_COVER_LETTER.md` | editöre kapak mektubu | evet |
| `04_HIGHLIGHTS.md` | 5 madde, her biri ≤85 karakter (betikle sayıldı) | evet |
| `05_DECLARATION_OF_INTEREST.md` | çıkar çatışması, fon, CRediT, YZ beyanı | evet |
| `90_REF_VERIFICATION_RECORD.md` | atıfların OpenAlex doğrulama kaydı | hayır — iç belge |
| `91_NUMBER_SHEET.txt` | kanonik sayı çizelgesi | hayır — iç belge |
| `PROMPT_DEGERLENDIRME.md` | bağımsız değerlendirme görev metni | hayır — iç belge |

## Değerlendirme promptunu kullanırken

`PROMPT_DEGERLENDIRME.md` içindeki metni görev olarak ver ve **yanına şu beş
dosyayı ekle:**

1. `01_MANUSCRIPT.md` — denetlenecek asıl metin
2. `02_SUPPLEMENTARY_S1-S9.md` — ana metnin S1–S9 göndermeleri buraya gider;
   bu dosya olmadan "eke taşındı mı yoksa kayboldu mu" sorusu cevaplanamaz
3. `03_COVER_LETTER.md` — editör merceği kapak mektubunu da değerlendirir
4. `90_REF_VERIFICATION_RECORD.md` — atıf denetiminin karşılaştırma tabanı
   (prompt bunu "veri kabul etme, yeniden doğrula" diye işaretliyor)
5. `91_NUMBER_SHEET.txt` — her sayının izlenebilirlik kaynağı

**Ekleme:** `04_HIGHLIGHTS.md` ve `05_DECLARATION_OF_INTEREST.md` yalnızca
Görev 1.3 (biçimsel eksikler) için gerekli; değerlendirici bunları da isterse
ver, istemezse şart değil.

**Verme:** depo geçmişi, `KILAVUZ.md`, `DURUM.md`, kusur kütüğü. Bunlar iç
çalışma belgeleri; değerlendiriciyi yönlendirir ve bağımsızlığı bozar.

## ⚠ GÖNDERİMİ BLOKE EDEN TEK ŞEY: SAYFA SINIRI

Üçüncü göz denetimi JESTECH'in yazar kılavuzunda **yayımlanan sayfaların 10
sayfayı aşmaması** şartını gösterdi ve bu şartı karşılamayan dosyaların hakem
sürecine alınmadığını belirtti. **Bunu ben doğrulayamadım** — kılavuz sayfasına
bu oturumdan erişemedim — ama denetçi somut kaynak verdi ve ciddiye alınmalı.

Ana metin şu anda **13.504 kelime**. Elsevier'in iki sütunlu düzeninde bir
yayımlanmış sayfa kabaca 800–1.000 kelime tutar; yani 10 sayfa ≈ 8–10 bin
kelime, tablolar ve kaynakça dahil. **Muhtemelen sınırın üstündeyiz.**

**Yapılması gereken sırayla:**

1. Kılavuzu aç ve sınırı doğrula (`sciencedirect.com` → JESTECH → Guide for
   Authors). Sınır yoksa bu blok düşer.
2. Metni resmî JESTECH Word/LaTeX şablonuna aktar ve **gerçek** sayfa sayısını
   gör. Kelime sayısından sayfa tahmin edilemez.
3. Sınırın üstündeyse kes. **Ama neyi keseceğin bir karar** ve bana sorman
   lazım: bu makalenin savunulabilirliği dürüstlük aygıtından geliyor ve onu
   keserek sığdırmak selef makalenin hatasını tersinden tekrarlamak olur.
   Kesilebilecek yerler, en az zararlıdan başlayarak: §4.2'nin model dökümü
   (eke), §4.7'nin denetim ayrıntısı (eke), §3.4'ün kapı tartışması (eke),
   §1'in ilgili çalışma paragrafı (kısaltılabilir).
4. **Kesilmeyecekler:** kısayol tabanı (§4.6.6), sürüm kaymasının aralık
   nitelemesi, EK-1 sapmasının taşıyıcılığı, 17 vakanın provenansı. Bunlar
   hakemin bulup da yazarın yazmadığı hâlde makaleyi batıracak sınıfta.

## Gönderimden önce kalan iş

- [ ] **Sayfa sınırı** — yukarıdaki blok
- [ ] İki kodlayıcının uzlaşı kural notu **imzası** (`uzlasi/IMZA_SAYFASI_v7a.md`)
- [x] ~~YZ beyanı~~ yazıldı ve kesinleşti
- [x] ~~Kaynakça tamamlama~~ 21 künye Crossref'ten tam cilt/sayı/sayfayla
- [x] ~~Arşiv DOI~~ v1.0.2, `10.5281/zenodo.22180708`

**Not:** makale 9. turdan sonra değişti; gönderimden önce bir `v1.0.3` release
alıp DOI'yi güncellemek gerekir. Bunu imzalar gelince tek seferde yaparım.
