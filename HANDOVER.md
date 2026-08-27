# RUHSAT-Bench — Claude Code Devir Belgesi
**Tarih:** 02.08.2026 · **Depo:** `D:\jestech\ruhsat-bench` · **Kaynak:** claude.ai oturumu (arşiv + bu paket)

---

## 1. Bağlam (Ne ve Neden)

RUHSAT-Bench, Türk mühendislik mevzuatı (İmar K. 3194, Yapı Denetimi 4708, İSG 6331, İSG Risk Yön., TBDY 2018, YDUY) üzerinde LLM'lerin **"bilmiyorum" deme yetisini** ölçen 473 maddelik bir doğru/yanlış kıyaslama kümesi. Hedef: JESTECH'e (Q1) makale. İki koşul var: E1 (kaçınma serbest) ve E2 (zorunlu seçim); ana metrikler dengeli doğruluk (BAcc), λ = doğruluk(P1)+doğruluk(P5)−1, kaçınmanın seçiciliği.

Üçüncü göz denetim raporu (01.08.2026) makaleyi "kurtarılabilir ama üç blok iş var" diye değerlendirdi: (P0) geçersiz Sonnet-B kolunun onarımı, (P1) dayanaklı baseline'lar (R0–R3), (P2) analiz katmanının yeniden kurulması. Bu oturumda P0 bitti, P1'in altyapısı kuruldu, ve beklenmedik büyüklükte bir iş çıktı: **TBDY ayrıştırıcısında sistematik bent kaynaşması** bulundu, 7 altın etiket uzman onayıyla düzeltildi (v7a). Etki testi yapıldı: **hiçbir niteliksel sonuç değişmiyor**; kusur avı resmen kapatıldı (durma kuralı).

Senin görevin: kalan mühendislik işini (korpus düzeltmesi, dayanaklı koşucular, analiz katmanı) bitirmek. API koşuları ve makale yazımı sende değil.

---

## 2. Mevcut Durum

### Bitmiş işler
| iş | kanıt |
|---|---|
| P0-1: varyant yönlendirme hatası yamandı; Sonnet-B @128 ×3 + Sonnet-A @128 ×1 koşuldu | `sonuclar/frontCB2_k1..3.jsonl`, `frontCA128_k1.jsonl` |
| Uzman uzlaşısı tamamlandı: OLGU 7/7 oybirliği, TANIM 3/5; v7a (birincil, 223/250) ve v7b (duyarlılık, 221/252) üretildi | `data/iddialar/uretilen_iddialar_v7a.csv`, `v7b.csv`, `sonuclar/uzlasi_nihai.txt` |
| EK-4 (dayanaklı kollar ön kaydı) ve EK-5 (kaynaşma + altın düzeltme beyanı) commit'li | `sonuclar/F4_on_kayit_ek4.txt`, `F4_on_kayit_ek5.txt` |
| TBDY rafine ayrıştırıcı: 1208→1523 birim, gömülü başlık 0, içerik kurtarma 0.9632 korundu | `scripts/bent_bol.py` doğrulama tablosu |
| R3 kural tabanlı baseline: 473/473 + 5 tohumlu negatif kontrol (ortalama 0.526) | `sonuclar/r3_kural.jsonl`, `r3_nk_*.jsonl` |
| Etki testi: 32 hücre v6/v7a/v7b ile yeniden puanlandı; \|ΔBAcc\| ort 0.0046, maks 0.0347 | `scripts/etki_analizi.py`, `sonuclar/etki_analizi.txt` |

### Bekleyen işler (bu devrin kapsamı → Bölüm 4)
1. `maddeler()` Ek/Geçici Madde düzeltmesi + korpusun nihai kurulumu
2. R3 ve Kontrol C'nin düzeltilmiş korpusta yeniden koşulması
3. `f4_dayanak.py` (R1/R2 koşucusu) — EK-4 şartlarıyla
4. Analiz katmanı (`f4_analiz.py`) — kümeli çıkarım, standart ECE, P6 BAcc, risk–kapsam
5. Mevcut koşuların v7a ile yeniden puanlanması

### Kullanıcıda bekleyen (SENDE DEĞİL)
- `frontCA32_bugun` koşusu (sürüm kayması vs bütçe etkisi ayrımı — sonucu Bölüm 7'deki dallanmayı belirler)
- İki kodlayıcının kural notu imzaları (v7a imzasız dondurulamaz)
- F5 API koşuları (anahtar kullanıcıda), P6 için 20 maddelik mevzuat.gov.tr dış doğrulaması

### Dosya haritası (bu paketle gelenler)
```
scripts/
  atif_coz.py          iddia metninden atıf çözümü (473/473 doğrulandı; CSV kanun/madde
                       sütunu GERÇEK kaynağı tutar, atıf yapılan yeri DEĞİL — P5'te kasten farklı)
  korpus_kur.py        korpus kurucu + 3 pozitif kontrol (A alıntı, B atıf, C P6) + manifest
  bent_bol.py          TBDY rafine edici (bentler() çıktısını bozmadan böler; ~2 kopya saklar)
  bentler2.py          BAŞARISIZ sıfırdan deneme — ARŞİV, kullanma (EK-5 §4'te gerekçesi)
  birim_kaynasma.py    kesmeyen kaynaşma tespiti (eski ayrıştırma üzerinde; tespit için güvenilir)
  madde_kaynasma.py    diğer 5 belge taraması (Ek/Geçici Madde kaybını ölçtü; altın etkisi SIFIR)
  birim_bak.py         korpus inceleme aracı (--liste/--birim/--ara)
  kural_taban.py       R3 koşucusu + öz-test + --karistir negatif kontrolü + --tani
  uzlasi_kitabi.py     uzlaşı kitabı üretici (TANIM/OLGU/KONTROLLER sayfaları)
  uzlasi_birlestir.py  iki kodlayıcı kitabını birleştirir → v7a/v7b + rapor
  etki_analizi.py      v6/v7a/v7b yeniden puanlama karşılaştırması
  sonda_karsilastir.py max_token sonda karşılaştırıcısı (hüküm kapısı gevşek — görev 4'te düzelt)
  yama_f4_api.py       f4_api.py→f4_api_v2.py yaması (uygulandı; referans)
  pk_varyant.py        varyant karışıklığının kol içi/kollar arası uyum ölçümü (referans)
beyanlar/   F4_on_kayit_ek4.txt, F4_on_kayit_ek5.txt
uzlasi/     UZLASI_KURAL_NOTU.md, UZLASI_KILAVUZ.md, uzlasi_kitabi_ORNEK.xlsx, uzlasi_nihai.txt
data/       uretilen_iddialar_v7a.csv, v7b.csv
sonuclar/   altin_adaylari.csv, kaynasma_raporu.txt, kaynasma_etkilenen.csv, etki_analizi.txt
kusur_kutugu.md   bilinen-kovalanmayan kusurlar (10 kayıt; #1 ve #6 bu devirde DÜZELTİLECEK)
```
Depoda ayrıca: `ORTAM.md` (çalışma kuralları — OKU), `HANDOVER.md` (makale devri, eski), üçüncü göz raporu, `scripts/uret_iddia_v3_6.py` (MÜHÜRLÜ), `scripts/f4_api_v2.py`, `scripts/f4_skor.py`, arşiv koşu çıktıları.

---

## 3. Kararlar (Nasıl — ve Neden)

**v7a birincil, v6+v7b duyarlılık.** İki kodlayıcı farklı kural seçti (Seçenek 1 vs 3). Seçenek 3 atıfsız iddialarda semantik yargı gerektirir ve yalnız denetlenen 138 maddede yapıldı; uygulanırsa denetlenen/denetlenmeyen maddeler farklı ölçütle etiketlenir. Seçenek 1 tekdüze uygulanabilir. **Seçim sonuca değil, tekdüze uygulanabilirliğe dayanır** — bu gerekçe makaleye girecek.

**Mühürlü üreteç dokunulmaz.** `uret_iddia_v3_6.py` ve iddia METİNLERİ sabit (486 id konsensüs koşusuna bağlı). Düzeltmeler yalnız altın etiketlerde (uzman onaylı) ve korpus katmanında yapılır. Korpus için `bent_bol.py` üretecin `bentler()` çıktısını İTHAL EDİP rafine eder — üreteci kopyalamaz.

**Ayrıştırıcı düzeltmesi rafine ederek, sıfırdan yazarak değil.** Sıfırdan deneme ölçülüp başarısız oldu (kurtarma 0.9632→0.022; EK-5 §4). Aynı ilke `maddeler()` için de geçerli: mevcut çıktıyı bozma, ekle.

**R1 tavan olarak kaldı, manşet karşılaştırma R2 − R3-bm25.** R3 (kural+oracle atıf) 1.00 verdi → kümenin yüzey inşası deterministik geri çözülebilir; R1−R0 "bilgi eklendi" kanıtı olamaz. Bilgi taşıyan soru: aynı kanıt verildiğinde LLM dizgi eşleştirmeye ne katıyor. (EK-4 bu revizyonla birlikte okunmalı.)

**Tek sınıflı problarda doğruluk bilgi ölçmez — ampirik kanıtla.** Negatif kontrolde P2/P4 karıştırılmış eşlemede bile 1.00 kaldı (altınları YANLIS, bozuk arama da YANLIS üretir). Analiz katmanı bu yüzden BAcc'yi birincil tutar ve tek sınıflı tabaka değerlerini "altın sınıfı seçme oranı" diye etiketler.

**max_token = 128, hosted kollar.** 32'de istem B %3.75 kesiliyor (A %0.11); 128'de sıfır. B@32↔B@128 uyuşması 0.848 çıktı ama bunun yorumu B'nin KENDİ kol içi bandına muhtaç — o band frontCB2 k1-3 ikililerinden hesaplanacak (görev 4). A@128 tek koşu, arşiv A@32 aralığının (0.684–0.703) dışında (0.64): sürüm kayması mı bütçe etkisi mi sorusu `frontCA32_bugun` ile ayrışacak (kullanıcıda).

**Durma kuralı.** Etki testi geçti → kusur avı bitti. Yeni kusur bulursan KOVALAMA: `kusur_kutugu.md`'ye kaydet, kullanıcıya bildir, işine dön. Kütükte DÜZELTİLECEK işaretli iki kayıt (#1 Ek/Geçici, #6 ECE) bu devrin görevleri; gerisi kütükte kalır.

**Çalışma kültürü (ORTAM.md'nin özü + bu oturumun ekleri):**
- Tahmine değil ölçüme güven. Bu oturumda 7 tahmin yapıldı, 7'si yanlıştı.
- Her yeni kontrol için pozitif kontrol: kontrolün hatayı yakaladığını bilinen bir vakayla göster (ör. 364 = 15.1→15.3.1 çıpası).
- Beyan koşudan ÖNCE yazılır ve commit'lenir.
- Başarısız denemeler silinmez, arşivlenir (bentler2.py örneği).
- Her betiğin başında stdout/stderr UTF-8 reconfigure (cp1252 borulama çökmesi — ölçüldü). Dosya IO `utf-8-sig`. Ollama için `127.0.0.1`, `localhost` değil.
- Kullanıcıya komutlar kopyala-yapıştır PowerShell 5.1 blokları olarak verilir; iç içe tırnaklı tek satırlıklardan kaçın (iki kez patladı).

---

## 4. Bu İterasyonun Kapsamı (Görevler — sıralı, kapılı)

### Görev 1 — `maddeler2` + korpusun nihai kurulumu
`maddeler()` şu kusuru taşıyor: `Ek Madde 3 –` metni `Madde 3 –` kalıbını sağlıyor, 3 zaten kayıtlı olduğu için parça ATILIYOR. 75 parça ~76k karakter korpusta yok (3194: 50k). Altın etkisi sıfır (ölçüldü — üreteç de aynı ayrıştırıcıyı kullandığından o metinlerden iddia üretmedi) ama F5 retrieval'ı için ciddi eksik.

Yap: `scripts/maddeler2.py` — `maddeler()` çıktısını İTHAL et, atılan parçaları yakala, `E3`/`G5` gibi ayrı anahtarlarla ekle (bent_bol'un ~N kopya deseni gibi). `korpus_kur.py`'yi güncelle: TBDY→`bent_bol`, diğer beş→`maddeler2`. Manifest ve üç pozitif kontrol korunur.

### Görev 2 — R3 + kontroller, düzeltilmiş korpusta
`kural_taban.py`'yi yeni korpusla koş (+5 tohum negatif kontrol). EK-5 §10'un sorusunu cevapla: eski 473/473'ün ne kadarı kaynaşmış ayrıştırmadan pay alıyordu? v7a altınla puanla; 7 dönen maddede kuralın ne yaptığını `--tani` ile raporla.

### Görev 3 — `f4_dayanak.py` (R1/R2 koşucusu)
EK-4 şartları: R1 = madde düzeyi atıf çözülebilen 289 iddia, doğru birimin tam metni istemde; R2 = BM25 (`rank_bm25`), k=3, 473 iddia; her JSONL satırına istem sha256, getirilen birim kimlikleri, `bitis_sebebi`; R2 geri çağırma (doğru birim ilk k'da mı) ayrı sütun; R3-bm25 = LLM'siz, R2 ile AYNI getirilen pasajlarda dizgi eşleştirme. Kesilme sayaçları "kesilen" ve "ayrıştırılamayan" AYRI (kütük #9). Ollama arayüzü `f4_api_v2.py`'deki yerel yol ile aynı; API kolları için betik hazır olur, koşuyu kullanıcı yapar. Önce `--sinir 10` dumanı testi çıktısı üret.

### Görev 4 — Analiz katmanı: `f4_analiz.py`
- Kümeli bootstrap: madde (kanun+madde) kümesinde, 10k yeniden örnekleme; BAcc/λ/Δ'lara CI.
- Standart ECE (kovadaki ORTALAMA güvenle) + Brier. **Pozitif kontrol: R3'e ECE=0 vermeli** (arşiv skorlayıcı 0.050 basıyor; kütük #6, denetim 1.10).
- P6 için prob içi BAcc; tek sınıflı tabakalar "altın sınıfı seçme oranı" etiketiyle.
- Risk–kapsam eğrisi (E1 güven eşiği taranarak) model başına.
- B kolunun kol içi bandı: frontCB2 k1/k2/k3 ikili uyuşmaları → `sonda_karsilastir.py`'nin hükmü bu bandla yeniden verilir (mevcut kapı gevşek; kütük #8).
- Girdi: mevcut tüm JSONL'ler; altın: v7a birincil, v6+v7b duyarlılık (üçü tek tabloda, `etki_analizi.py` deseni).

### Görev 5 — yeniden puanlama çıktıları
`f4_skor.py`'ye DOKUNMADAN (arşiv bütünlüğü) `f4_analiz.py` üzerinden tüm hücrelerin v7a tabloları; `sonuclar/` altına tek rapor + CSV.

---

## 5. Kabul Kriterleri

- [ ] `maddeler2` doğrulaması: atılan 75 parçanın ≥%95'i korpusta; mevcut 158 birimin metni bayt-aynı; Kontrol A ≥ 440/441, B = 473/473, C = 120/120 (C'nin dairesellik uyarısı raporda kalır)
- [ ] Yeni korpusta toplam birim > 1523 + ~70 ve `korpus.jsonl` manifest sha'sı rapora yazılmış
- [ ] R3 yeni korpusta koşuldu; v7a ile puan + 7 dönen maddenin `--tani` dökümü; 5 tohum negatif kontrol 0.50–0.56 bandında
- [ ] `f4_dayanak.py --sinir 10 --kuru` istem sha'larını basıyor; R1'de istem doğru birim metnini içeriyor (rastgele 3 örnek elle gösterilmiş); R2 satırlarında geri çağırma alanı dolu
- [ ] `f4_analiz.py` R3'e ECE=0.000 veriyor (pozitif kontrol); Sonnet E1 BAcc v7a CI'sı raporda; B kol içi bandı üç ikiliden hesaplanmış
- [ ] Tüm yeni betikler: başta UTF-8 reconfigure, `utf-8-sig` IO, `python -m py_compile` temiz, PowerShell 5.1'de kopyala-yapıştır koşu bloğu docstring'de
- [ ] Hiçbir mevcut arşiv dosyası ve `uret_iddia_v3_6.py`, `f4_api_v2.py`, `f4_skor.py` DEĞİŞMEMİŞ (git diff boş)

---

## 6. Kısıtlar ve Yapılmayacaklar

- `uret_iddia_v3_6.py` MÜHÜRLÜ — okuma/ithal serbest, değişiklik yasak. İddia metinleri ve id'ler sabit.
- API anahtarı isteme, API koşusu yapma; hosted koşular kullanıcının makinesinde. Sen betiği ve dumanı testini hazırla.
- `f4_skor.py`'yi düzeltme (arşivle karşılaştırılabilirlik için donduruldu); düzeltmeler `f4_analiz.py`'de yaşar.
- Yeni kusur avı yok (durma kuralı). Bulursan kütüğe yaz, devam et.
- Uzlaşı dosyalarına ve altın CSV'lere yeni düzeltme uygulama; v7a/v7b son hali (imza bekliyor).
- `bentler2.py`'yi kullanma/silme — arşiv kaydı.
- Kesilen yanıt oranı herhangi bir kolda >%1 ise koşu geçersiz (EK-4 m.10) — sayaçla ve uyar.

---

## 7. Varsayımlar (yanlışsa düzelt)

- İmzalar gelecek; v7a "onaylı-imza bekliyor" statüsünde. Dondurma commit'i imza sonrası, kullanıcı yapar.
- `frontCA32_bugun` sonucu bilinmiyor. 0.68–0.70 çıkarsa bütçe etkisi → kullanıcı A@128 iki koşu daha yapar, karşılaştırma 128'de kurulur; ~0.64 çıkarsa sürüm kayması → EK-6 beyanı gerekir (o beyanı kullanıcıyla birlikte yazarsın, bu devirde değil). Görev 4'ü her iki dala da hazır kur: hücre etiketlerinde max_token ve koşu tarihi taşınsın.
- `rank_bm25` kurulabilir (`pip install rank_bm25 --break-system-packages`); değilse saf-Python BM25 yaz, dışa bağımlılığı raporla.
- Ollama modelleri arşivdeki listeyle aynı adlarla duruyor.

---

## 8. İlk Adım — Senden İstediğim

Lütfen kodlamaya HEMEN başlama. Önce:
1. Şunları oku: bu belge, `ORTAM.md`, `sonuclar/F4_on_kayit_ek4.txt`, `F4_on_kayit_ek5.txt`, `kusur_kutugu.md`, `scripts/bent_bol.py` (rafine deseni), `scripts/korpus_kur.py`, `scripts/kural_taban.py`, `scripts/uret_iddia_v3_6.py` içindeki `maddeler()` ve `bentler()`.
2. Belirsiz veya çelişik bulduğun noktaları bana sor — özellikle korpus şeması (birim anahtarları `E3`/`G5` mi başka biçim mi) ve R2 istem şablonunun Türkçe ifadesi.
3. Görev 1–2 için kısa bir uygulama planı öner (hangi dosyalar, hangi doğrulamalar, hangi sırayla). Görev 3–4'ün planını, 1–2 bitip çıktıları görünce ver.
4. Ben planı onayladıktan sonra uygula. Her görevin sonunda doğrulama çıktısını göster; ilk denemeni nihai sayma.
