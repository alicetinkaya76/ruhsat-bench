# v7a ALTIN KÜMESİ — DONDURMA İMZA SAYFASI

**Amaç:** `data/iddialar/uretilen_iddialar_v7a.csv` HANDOVER §2'de *"onaylı — imza
bekliyor"* statüsünde. Bu sayfa imzalanınca v7a **dondurulur** ve makalede birincil
altın küme olarak kullanılabilir.

> Bu belgeyi **asistan dolduramaz.** İki kodlayıcının kendi kararlarını kendi
> beyanlarıyla onaylaması gerekir. Asistan yalnızca aşağıdaki **ölçülmüş
> bilgileri** hazırlamıştır; imzalar insanlara aittir.

---

## 1. İmzalanan nesnenin kimliği (ölçüldü, 2026-08-28)

| | |
|---|---|
| dosya | `data/iddialar/uretilen_iddialar_v7a.csv` |
| kayıt | 473 iddia |
| dağılım | 223 DOĞRU / 250 YANLIŞ |
| v6'dan farkı | **7 iddia**: 246, 257, 304, 360, 364, 382, 393 (hepsi DOĞRU → YANLIŞ) |
| üretim | `scripts/uzlasi_birlestir.py`, iki kodlayıcı kitabından |
| yeniden üretilebilirlik | Kitaplardan **birebir yeniden üretildi** (LF-normalize sha256 aynı) |

Kodlayıcı kitapları:
- `kodlayici1_uzlasi_kitabi_doldurulmus.xlsx` — sha256 `1411fc7f318e21f6…`
- `kodlayici2_uzlasi_kitabi_secenek1.xlsx` — sha256 `04d5c486e5edd889…`

Kural notları: `uzlasi/kodlayici1_UZLASI_KURAL_NOTU_doldurulmus.md`,
`uzlasi/kodlayici2_UZLASI_KURAL_NOTU_DOLU.md`

## 2. İmzalamadan ÖNCE bilinmesi gerekenler

Aşağıdakiler bu oturumda **ölçüldü** ve imza kararını etkileyebilir.

**(a) Düzeltilen 7 iddia, kural tabanlı tabanca bağımsız olarak doğrulandı.**
R3 (LLM yok, düzeltilmiş korpus) tam bu 7 iddiada karar değiştiriyor ve başka
hiçbirinde değiştirmiyor. Eski "kusursuz" 473/473, korpus ile altının aynı yönde
yanlış olmasının ürünüymüş. → `sonuclar/gorev2_raporu.txt` §1

**(b) Düzeltme TAMAMLANMAMIŞ olabilir — imzadan önce bakılmalı.**
Düzeltilen bir iddiayla **birebir aynı korpus kaymasını** paylaşan **12** iddia
düzeltilmemiş; hiç düzeltme almamış kaymalarda **5** iddia daha var. Toplam **17**.

Örnek: `TBDY/7.2.1.4 → 7.2.4` kaymasındaki 5 iddiadan 2'si (304, 382) düzeltilmiş,
3'ü (25, 123, 211) düzeltilmemiş.

> "Yalnız P1 denetlenmiş" demek **yanlış** olur: id=278 P1 olduğu hâlde düzeltilmemiş.

Bu 17 vaka `uzlasi/ACIK_17_VAKA_karar_kitabi.xlsx` içinde, her biri için iki birimin
metni ve aynı kaymada düzeltilmiş iddianın id'si ile birlikte hazır.

**Karar gerekiyor:** v7a bu 17 vaka çözülmeden mi dondurulacak, yoksa önce onlar
karara bağlanıp v7c mi üretilecek?

## 3. İmzalar

### Kodlayıcı 1

- [ ] `uzlasi/kodlayici1_UZLASI_KURAL_NOTU_doldurulmus.md` içindeki kural notu bana aittir ve doğrudur.
- [ ] v7a'daki 7 düzeltmeyi (246, 257, 304, 360, 364, 382, 393) onaylıyorum.
- [ ] §2(b)'deki 17 açık vakayı gördüm. Kararım: ☐ v7a şimdi dondurulsun ☐ önce 17 vaka çözülsün

Ad-soyad: ………………………………  Tarih: …………………  İmza: …………………

### Kodlayıcı 2

- [ ] `uzlasi/kodlayici2_UZLASI_KURAL_NOTU_DOLU.md` içindeki kural notu bana aittir ve doğrudur.
- [ ] v7a'daki 7 düzeltmeyi onaylıyorum.
- [ ] §2(b)'deki 17 açık vakayı gördüm. Kararım: ☐ v7a şimdi dondurulsun ☐ önce 17 vaka çözülsün

Ad-soyad: ………………………………  Tarih: …………………  İmza: …………………

## 4. İmza sonrası (asistan yapar)

1. Bu dosya imzalı hâliyle depoya konur.
2. `git tag v7a-donduruldu` atılır.
3. Kusur kütüğü #10 kapatılır (`durum` sütunu ONAY_BEKLIYOR → DONDURULDU).
4. Makale metninde altın küme sürümü v7a olarak sabitlenir.
