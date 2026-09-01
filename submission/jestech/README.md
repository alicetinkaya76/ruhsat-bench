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

## ⚠ İKİ BİÇİMSEL BLOKE EDİCİ — DOĞRULANDI (01.09.2026)

### Ne bulundu

JESTECH'in yazar kılavuzunda iki ayrı şart var ve **ikisi de bizi tutuyor**:

> *"the editorial board of the journal has decided to limit all published pages
> within **10 pages**"*
>
> *"All authors are requested to use the **Word Author Template or LaTeX Author
> Template**… the journal **will not proceed with the peer-review process** if
> authors do not submit their articles using the Author Template."*

**Doğrulama notu — dürüstçe:** kılavuzun kendi sayfasını (`sciencedirect.com`)
**okuyamadım**; hem `WebFetch` hem tarayıcı **HTTP 403** aldı (bot koruması).
İki bağımsız arama bu iki cümleyi aynı şekilde, aynı kılavuz sayfasına işaret
ederek döndürdü ve üçüncü göz denetimi de aynı kaynağı gösterdi. Yani şart
**yüksek olasılıkla doğru ama birincil kaynaktan teyit edilmedi.** Ali'nin
kılavuzu bir kez kendi tarayıcısında açıp bakması 30 saniyelik iş ve bu notu
kapatır.

### Neredeyiz

Ana metin **13.504 kelime**. Elsevier iki sütunlu düzende bir yayımlanmış sayfa
kabaca 800–1.000 kelime; yani **~14–17 sayfa**. Sınırın belirgin biçimde
üstündeyiz. Ek materyal (S1–S9) normalde sayfa sınırına girmez.

### Yapılacaklar

**1. Şablon.** Elinde Markdown var, dergi Word ya da LaTeX istiyor. LaTeX
şablonu bu makale için daha uygun (çok tablo var). Şablonu indirip metni
aktarmak lazım; bunu yapabilirim ama şablonu senin indirmen gerekiyor
(Elsevier sayfası bana kapalı).

**2. Kısaltma — ~4.500 kelime.** Hedef ana metin ~9.000. Kesme sırası, en az
zararlıdan:

| taşınacak | kelime | gövdede kalacak |
|---|---|---|
| §4.2'nin model-model dökümü ve Tablo 2 | ~700 | iki cümle + "biri şansı aşıyor" |
| §4.7'nin denetim ayrıntısı | ~900 | κ değerleri + ikinci geçişin olumsuz sonucu |
| §3.4'ün kapı sapması tartışması | ~800 | 4 cümle: sapma var, taşıyıcı, gerekçe kavramsal |
| §4.6.5 duyarlılık tabloları | ~500 | "hiçbiri sonucu değiştirmiyor" |
| §1'in ilgili çalışma paragrafı | ~350 | yarıya iner, atıflar kalır |
| §6'nın uzun maddeleri | ~700 | her madde 2-3 cümleye iner |
| §5.4'ün sayı tekrarları | ~600 | tablodan okunur, metinde tekrarlanmaz |

**3. KESİLMEYECEKLER.** Bunlar hakemin bulup da yazarın yazmadığı hâlde
makaleyi batıracak sınıfta; ek dosyaya da gömülmezler, gövdede kalırlar:

* kısayol tabanı (§4.6.6) — şablon-yalnız taban 0.9860 ile her kolu geçiyor
* sürüm kaymasının aralık nitelemesi — değişim aralığı sıfırı içeriyor
* EK-1 kapı sapmasının **taşıyıcı** olduğu — orijinal kuralla üç ana sistem elenirdi
* 17 vakanın provenansı — kararları bir dil modeli verdi
* λ'nın aile-koşullu cevaba karşı korumasız olduğu

## Gönderimden önce kalan iş

- [ ] **Sayfa sınırı** — yukarıdaki blok
- [ ] İki kodlayıcının uzlaşı kural notu **imzası** (`uzlasi/IMZA_SAYFASI_v7a.md`)
- [x] ~~YZ beyanı~~ yazıldı ve kesinleşti
- [x] ~~Kaynakça tamamlama~~ 21 künye Crossref'ten tam cilt/sayı/sayfayla
- [x] ~~Arşiv DOI~~ v1.0.2, `10.5281/zenodo.22180708`

**Not:** makale 9. turdan sonra değişti; gönderimden önce bir `v1.0.3` release
alıp DOI'yi güncellemek gerekir. Bunu imzalar gelince tek seferde yaparım.
