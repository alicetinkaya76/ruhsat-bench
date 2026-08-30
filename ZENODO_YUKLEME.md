# Arşiv DOI'si — ne olduğu ve nasıl alınacağı

**Kısa cevap: 5 dakikalık bir iş, dosya hazır.**

## Arşiv DOI'si nedir

Makalenin özü ve girişi *"kod ve veri yayımlandı"* diyor. Bir hakem bunu okur ve
sorar: *nerede?* Bir GitHub bağlantısı yeterli değil, çünkü depo silinebilir,
taşınabilir ya da içeriği sessizce değişebilir. Dergiler bu yüzden **kalıcı
tanımlayıcı** ister: dosyayı bir arşiv servisine yatırırsın, servis sana
`10.5281/zenodo.XXXXXXX` biçiminde bir **DOI** verir, ve o DOI **o anki dosyaya**
sonsuza kadar bağlı kalır. Sen depoyu silsen bile arşiv durur.

Bunu daha önce iki projede yaptın (Bankspeak ve *Answering Less*), aynı yer:
**Zenodo**. Aynı hesabı kullan.

## Dosya hazır

    /Users/alicetinkaya/Desktop/RUHSAT-Bench-v1.0.0.zip     (12 MB)

İçinde 287 dosya: altı kaynak PDF, üç korpus, 473 iddia ve üç altın sürümü,
ön kayıt + sekiz ek, bütün koşu kayıtları, puanlama ve analiz çıktıları,
sayı çizelgesi, betikler, makale ve eki, kusur kütüğü.

**Kontrol edildi:** `.env` YOK (API anahtarların girmedi), önbellek YOK,
kişisel ad YOK (uzmanlar yalnız `INS_MUH` / `ISG_UZM` rol koduyla geçiyor).
Kapak mektubu çıkarıldı — o yazışma, araştırma çıktısı değil.
Her dosyanın SHA-256'sı `MANIFEST.sha256` içinde.

## Adımlar

1. **zenodo.org** → giriş yap → sağ üstte **New upload**.
2. Zip dosyasını sürükle.
3. Alanları aşağıdaki kutudan kopyala.
4. **Publish**. Zenodo `10.5281/zenodo.XXXXXXX` verir.
5. **Bana DOI'yi yolla**, makaleye ben yerleştiririm (tek yerde, veri
   erişilebilirliği bloğunda).

> Yayımlamadan önce **Reserve DOI** düğmesine basarsan DOI'yi önceden alırsın ve
> makaleye yazabilirsin; yayımlama sonra da olur. Gönderim sırası açısından bu
> daha rahat, ama şart değil.

## Zenodo alanları — kopyala yapıştır

**Resource type:** Dataset
*(Zenodo "Software" da kabul eder; burada ağırlık veri ve koşu kayıtlarında,
o yüzden Dataset daha doğru.)*

**Title:**

    RUHSAT-Bench: a 473-claim abstention benchmark over Turkish construction and occupational-safety regulation — data, code and pre-registration

**Creators:**

    Çetinkaya, Ali — Selçuk University, Faculty of Technology, Department of Computer Engineering — ORCID 0000-0002-7747-6854

**Description:**

    Release archive for the paper "Measuring abstention, not accuracy: a
    re-qualification benchmark for language-model decision support on Turkish
    construction and occupational-safety regulation".

    RUHSAT-Bench is a set of 473 true/false claims over six frozen Turkish
    regulatory documents (Laws 3194, 4708 and 6331, the Building Inspection
    Implementation Regulation, the OHS Risk Assessment Regulation, and the
    Turkish Building Earthquake Code TBDY 2018). Each claim is asked under two
    conditions: one permitting an explicit "not sure" and one forcing a binary
    verdict, so that abstention behaviour is measured rather than assumed.

    The archive contains the source documents with checksums, three parsed
    corpora, the claim set in three gold-label versions, the blinded expert-audit
    workbooks including the negative second-pass result, the pre-registration and
    its eight annexes, every run record, the scoring and analysis code, and a
    number sheet mapping every figure in the paper to the file and script that
    produced it.

    Two limits are stated in the archive README: the development repository's
    version history was lost and the repository was reconstructed from dated
    hand-over packages, so pre-registration timing rests on document dates rather
    than commit timestamps; and the expert coders are identified only by role.

**Keywords:**

    compliance checking; decision-support software qualification; abstention;
    selective prediction; large language models; building regulation; Turkish law;
    benchmark

**Licence:** Creative Commons Attribution 4.0 International (CC BY 4.0)
*(Kodun MIT olduğu arşiv README'sinde yazıyor; Zenodo tek lisans alanı istiyor,
oraya CC BY 4.0 yaz.)*

**Version:** 1.0.0

**Language:** English

**Related identifiers:** makale yayımlandığında
`is supplement to` → makalenin DOI'si. Şimdilik boş bırak.

## Sonrası

DOI geldiğinde makalede tek bir blok değişir:

    makale/RUHSAT_JESTECH_ana_metin.md → "Data and code availability"

Orada şu an duran `[TO BE COMPLETED BEFORE SUBMISSION]` uyarısı silinir ve
yerine DOI yazılır. Bunu ben yaparım; sen sadece numarayı ver.
