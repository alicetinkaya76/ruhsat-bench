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

## Gönderimden önce kalan iş

- [ ] İki kodlayıcının uzlaşı kural notu **imzası** (`uzlasi/IMZA_SAYFASI_v7a.md`)
- [ ] `05_DECLARATION_OF_INTEREST.md` içindeki **üretken yapay zekâ kullanım
      beyanı** bloğu — yazarın kendi ifadesiyle doldurulacak, olduğu gibi
      bırakılamaz
- [ ] Zenodo kaydında v1.0.1'in sürüm alanı hâlâ "1.0.0" görünüyor (kozmetik;
      DOI ve dosya adı doğru)
