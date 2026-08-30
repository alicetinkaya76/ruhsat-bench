# Atıf doğrulama — RUHSAT-Bench (JESTECH)

**Son tur: 2026-08-30 · Kaynak: Crossref REST API (`api.crossref.org/works/<DOI>`)
+ OpenAlex.** Önceki tur (2026-08-29, yalnız OpenAlex) bu belgeyi **eziyor.**

> Selef makale kısmen doğrulanmamış ve kaymış atıflar yüzünden reddedildi.
> Bu turda her DOI **çözdürüldü** ve künye alanları tek tek karşılaştırıldı.

---

## ⚠ ÖNCEKİ TURUN ÜRETTİĞİ İKİ HATA — DÜZELTİLDİ

29 Ağustos turu OpenAlex'e bakıp iki künyenin yılını "düzeltti". **İkisi de
yanlıştı.** Sebep: OpenAlex'in verdiği tarih ile derginin **sayı (issue)**
tarihi farklı; makaleler online-first çıkıp aylar/yıllar sonra sayıya girmiş.
Atıfta kullanılacak olan **sayı yılıdır**.

| künye | önceki tur ne yaptı | Crossref gerçeği | ŞİMDİ |
|---|---|---|---|
| Zhang & El-Gohary | 2016 → **2013** yaptı | `published-print` **2016-03**, cilt 30(2); `created` 2013-07-25 | **2016** |
| Zhou & El-Gohary | 2017 → **2016** yaptı | `published-print` **2017-02**, cilt 74, ss. 103–117; `created` 2016-12-01 | **2017** |

**Ders:** OpenAlex'in `publication_year`'ı online-first tarihini verebiliyor.
Künye yılı için Crossref `published-print` / `journal-issue` alanı esas alınır.

---

## ⚠ GEÇERSİZ DOI — KALDIRILDI

**El-Yaniv & Wiener 2010.** Taslakta `doi:10.5555/1756006.1859904` yazıyordu.
`https://doi.org/10.5555/1756006.1859904` → **HTTP 404, çözülmüyor.**
`10.5555` ön eki ACM Digital Library'nin, DOI'si olmayan kayıtlar için
kullandığı yer tutucu ad alanıdır; tescilli bir DOI değildir. JMLR makalelerinin
çoğunun DOI'si yoktur.

**Yeni hâli:** *Journal of Machine Learning Research* **11**, 1605–1641 (DOI yok).
Cilt ve sayfa OpenAlex kaydından doğrulandı.

---

## Crossref'te DOĞRULANDI (11 künye)

Her satır için yıl, yazar soyadları, başlık ve dergi adı karşılaştırıldı.

| künye | DOI | Crossref yıl | dergi |
|---|---|---|---|
| Chen et al. 2024 | 10.3390/buildings14071983 | 2024 | Buildings |
| Chow 1970 | 10.1109/tit.1970.1054406 | 1970 | IEEE Trans. Inf. Theory |
| Dahl et al. 2024 | 10.1093/jla/laae003 | 2024 | J. Legal Analysis |
| Eastman et al. 2009 | 10.1016/j.autcon.2009.07.002 | 2009 | Automation in Construction |
| Jiang et al. 2021 | 10.1162/tacl_a_00407 | 2021 | TACL |
| Magesh et al. 2025 | 10.1111/jels.12413 | 2025 | J. Empirical Legal Studies |
| Naeini et al. 2015 | 10.1609/aaai.v29i1.9602 | 2015 | AAAI |
| Robertson & Zaragoza 2009 | 10.1561/1500000019 | 2009 | Found. Trends Inf. Retr. |
| Solihin & Eastman 2015 | 10.1016/j.autcon.2015.03.003 | 2015 | Automation in Construction |
| Zhang & El-Gohary **2016** | 10.1061/(ASCE)CP.1943-5487.0000346 | 2016 | J. Comput. Civ. Eng. 30(2) |
| Zhou & El-Gohary **2017** | 10.1016/j.autcon.2016.09.004 | 2017 | Automation in Construction 74 |

**Not:** Crossref'in döndürdüğü Jiang ve Magesh başlıkları HTML işaretlemesi
(`<i>`, `<scp>`) içeriyor; makaledeki düz metin hâlleri doğrudur.

## DOI'siz, arXiv ile anılanlar (4 künye)

Bunlar önbaskı olarak anılıyor; arXiv numaraları OpenAlex'te doğrulandı.

| künye | arXiv | not |
|---|---|---|
| Geifman & El-Yaniv 2017 | 1705.08500 | arXiv sürümüyle anılıyor |
| Guo et al. 2017 | 1706.04599 | ICML 2017; arXiv ile anılıyor |
| Kadavath et al. 2022 | 2207.05221 | önbaskı |
| Lin et al. 2022 | 2205.14334 | önbaskı |
| Xiong et al. 2024 | 2306.13063 | önbaskı 2023, ICLR sürümü 2024; makale **ICLR 2024** sürümünü anıyor ve künyede bunu belirtiyor |

## Standart

**IEC 61508** — dergi makalesi değil, standart. OpenAlex/Crossref kapsamı
dışında; künye IEC kataloğundan **doğrulanmadı**. Edisyon ve bölüm numarası
gönderimden önce IEC kataloğundan tamamlanmalıdır. Bu, bu belgede
**doğrulanmamış** olarak duran tek kalemdir.

## Metin içi atıf denetimi

18 künyenin **18'i** de gövdede en az bir kez anılıyor (kaynakçadan önceki
bölümlerde betikle sayıldı). Yetim atıf yok.
