# Arşiv DOI'si — GitHub üzerinden Zenodo

**Depo açıldı ve canlı:** https://github.com/alicetinkaya76/ruhsat-bench
(public, 291 dosya, `main` dalı)

Şimdi geriye tek şey kaldı: bu depoyu Zenodo'ya bağlamak ve bir **release**
yayımlamak. Zenodo o release'i arşivler ve sana kalıcı bir DOI verir.

## Neden hem depo hem DOI

Depo adresi hakem için yeterli değil: depo taşınabilir, yeniden yazılabilir,
silinebilir. DOI ise **o anki dosyaların dondurulmuş hâline** bağlanır ve
değişmez. Makalede ikisi de yer alacak — depo "burada çalışılıyor", DOI "makale
şu hâlden üretildi" demek.

GitHub–Zenodo bağlantısının güzel yanı: bundan sonra her yeni release otomatik
arşivlenir ve kendi DOI'sini alır. Bir de üstünde duran "concept DOI" olur, o
hep en son sürüme gider.

## Senin yapacağın — 3 adım, ~3 dakika

**1. Zenodo'yu GitHub'a bağla**

* zenodo.org → giriş yap (daha önce Bankspeak ve *Answering Less* için
  kullandığın hesap)
* Sağ üst → **Settings** → sol menüden **GitHub**
* Sayfada depolarının listesi çıkar. `ruhsat-bench` satırını bul ve
  anahtarı **ON** yap.
* Liste boşsa **Sync now** düğmesine bas.

**2. Bana haber ver**

Anahtar açıldıktan sonra release'i ben yayımlarım (`v1.0.0`, notları hazır).
İstersen kendin de yapabilirsin: GitHub'da depo → sağdaki **Releases** →
**Create a new release** → tag `v1.0.0` → **Publish release**.

> **Sıra önemli:** anahtar ÖNCE açılmalı. Release'i önce yayımlarsan Zenodo
> onu görmez ve tag'i silip yeniden oluşturman gerekir.

**3. DOI'yi bana yolla**

Zenodo dakikalar içinde `10.5281/zenodo.XXXXXXX` üretir. Numarayı bana ver,
makaleye ben yerleştiririm — tek yerde, "Data and code availability" bloğunda.

## Zenodo metadatasını dert etme

Depoda `.zenodo.json` var; Zenodo başlığı, yazarı, ORCID'i, lisansı ve açıklamayı
oradan okur. Elle bir şey doldurman gerekmiyor. `CITATION.cff` de eklendi, bu
sayede GitHub sayfasında "Cite this repository" kutusu çıkıyor.

## Lisans (bilgin olsun)

* Kod (`scripts/`, `hpc/`) → MIT
* Veri, çıktılar, makale → CC BY 4.0
* Kaynak mevzuat PDF'leri → Resmî Gazete metinleri, olduğu gibi yeniden
  dağıtılıyor, üzerlerinde ek hak iddia edilmiyor

Bu ayrım `LICENSE` dosyasında yazılı.
