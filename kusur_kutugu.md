# RUHSAT-Bench — KUSUR KÜTÜĞÜ

Durma kuralı gereği (02.08.2026): yeni bulunan kusurlar KOVALANMAZ, buraya
yazılır. Kayıt üç soruya cevap verir: ne, etkisi ölçüldü mü, karar ne.

Etki testi referansı: v6→v7a yeniden puanlamada 32 hücrede |ΔBAcc|
ortalama 0.0046, maks 0.0347; hiçbir niteliksel sonuç değişmedi
(`sonuclar/uzlasi_nihai.txt` ve etki analizi).

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 1 | `maddeler()` `Ek Madde`/`Geçici Madde`yi ayrı birim yapmıyor; 75 parça ~76k karakter korpusta yok (3194 tek başına 50k) | Altın etkisi SIFIR (atılan metinden hiç iddia üretilmemiş — ölçüldü). F5 retrieval'ını etkiler | **DÜZELTİLECEK** (F5 öncesi, tek seferde) — görev listesi #1 |
| 2 | `bentler()` kaynaşması (456 tanınmayan başlık, 27 sahte birim) | 7 altın döndü (EK-5, uzman onaylı); etki testi geçti | KAPANDI — `bent_bol.py` ile |
| 3 | `kaynak_alinti` sütunu ~200 karakterde kırpık; P1/P2/P5'in %15'inde iddia içeriği alıntıdan uzun | Denetim 1. geçişinde uzmanlar kırpık alıntı gördüyse κ=1.00'a ek açıklama olabilir; `denetim_kitabi.py`'nin hangi alanı bastığı BAKILMADI | KÜTÜKTE — makale sınırlılığına aday; kovalanmıyor |
| 4 | id=391 (YDUY/14): `temizle_v39` şerh ayıklaması alıntı ortasına denk gelmiş, 441'de 1 katı eşleşme kaybı | Ölçüldü, tek madde, gevşek eşleşme buluyor | KAPANDI — dipnot |
| 5 | pypdf sürüm farkı: TBDY metni iki ortamda 870747/870751 karakter | Birim sayısı, kontroller, aday listesi AYNI çıktı (ölçüldü). **2026-08-27 DARALTILDI:** fark işletim sistemine değil, yalnız pypdf SÜRÜMÜNE bağlı — pypdf 5.9.0 ile macOS/py3.11.9 ve Ubuntu/py3.12.3 altı belgenin altısında da bayt-birebir metin verdi (Δkarakter=0, `metin_sha256` eşit) | KÜTÜKTE — makalede pypdf sürümü + metin hash verilecek; artık "iki ortam" değil "iki pypdf sürümü" diye yazılır |
| 6 | `f4_skor.py` ECE'si kova orta noktası kullanıyor (denetim 1.10; R3 ile kanıtlandı: doğru değer 0 iken 0.050 basıyor) | Sonnet ECE'si ~0.014 şişkin | **KAPANDI** (28 Ağu) — `f4_analiz.py` standart ECE (kova ortalama güveni) kullanıyor. Pozitif kontrol 3 çift üzerinde: önkoşulu sağlayan iki çiftte standart **0.0000** / arşiv **0.0500**; önkoşulu sağlamayan çifti kontrol doğru şekilde ayırt ediyor. `f4_skor.py` DEĞİŞMEDİ |
| 7 | `f4_skor.py` başlığı varyanttan bağımsız "varyant A" basıyor | Kozmetik | KÜTÜKTE |
| 8 | Sonda betiğinin hüküm kapısı fazla gevşekti (CI bandı kesişimi); B'nin kendi kol içi bandı yoktu | frontCB2 k1-3 ikilileri bandı verecek; analiz bekliyor | **KAPANDI** (28 Ağu) — bandlar ölçüldü: A@32 [0.9017, 0.9133] · B@128 [0.9165, 0.9228]. Eş granülerlikte (tek koşu × tek koşu) A×B = 0.8302 → **her iki bandın altında** |
| 9 | Kesilen ≠ ayrıştırılamayan (etiket önce yazılınca kesilme veri kaybettirmiyor) | Sonda: 3 kesilmenin 1'i kayıp | KÜTÜKTE — raporlamada iki sayaç ayrı verilecek |
| 10 | `uretilen_iddialar_v6`'da `durum` sütunu ONAY_BEKLIYOR/YENI_EK ("frozen final" terminolojisiyle çelişiyor; denetim 1.18) | Kozmetik/terminoloji | KÜTÜKTE — v7a dondurulurken sütun güncellenmeli |

---

## Linux/TF-HPC geçişinde eklenenler (2026-08-27)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 11 | Git geçmişi kayboldu: Windows deposu (`D:\jestech\ruhsat-bench`) erişilemez, `git bundle` alınamadı | Dosya içerikleri tam (17/17 koştu, mühürlü üreteç iki pakette aynı sha256). Kaybolan: commit tarih damgaları → ön-kayıt-önceliği git ile kanıtlanamaz | KAPANDI — `REKONSTRUKSIYON.md` beyanı yazıldı; makale cümlesi §7'de |
| 12 | `f4_api_v2.py` hiçbir arşiv paketinde yoktu (HANDOVER dosya haritası depoda sayıyordu) | `yama_f4_api.py` ile deterministik yeniden üretildi; 4/4 yama, özdoğrulama geçti | KAPANDI |
| 13 | `f4_api.py`/`v2` hata mesajı PowerShell biçiminde ipucu basıyor (`$env:LLM_API_KEY = ...`) | Kozmetik. Anahtar okuma zaten doğru: `os.environ.get(--anahtar-env)` | KÜTÜKTE — donmuş dosya, dokunulmuyor |
| 14 | `uzlasi_birlestir.py` v7a/v7b'yi CRLF ile yazıyor (Linux'ta da) | İçerik etkilenmiyor (LF-normalize sonrası birebir aynı, ölçüldü); `.gitattributes` commit'te normalize ediyor | KÜTÜKTE — kovalanmıyor |
| 15 | `ollama_kur.sh` hedef ortamda **hiç koşulmadı** (konteynerde systemd yok; tarball + `setsid nohup` yolu belgeden yazıldı) | **2026-08-27 KOŞTU ve ÖLÇÜLDÜ:** ollama 0.32.14, CUDA compute 7.5, 3/3 model (38 GB), uçtan uca duman testi `f4_kos.py` ile 20/20 birebir deterministik | KAPANDI — betikteki uyarı bloğu silindi; iki tuzak çıktı: `.tgz` → `.tar.zst` varlık değişimi ve `lib/` için `LD_LIBRARY_PATH` |
| 16 | Windows koşularında kullanılan **Ollama sürümü hiçbir yerde kayıtlı değil** (`ORTAM.md` §8 model adlarını veriyor, sürümü vermiyor) | Ölçülemez (kaynak makine yok) → eskisiyle eşleşmek imkânsız. GECIS_LINUX.md §7: model dosyaları sürümler arası bayt-birebir olmayabilir | **YENİ TABAN İLAN EDİLDİ: ollama 0.32.14** (kullanıcının Mac'inde de koşan sürüm, ölçüldü). Yerel kollar bu tabanda yeniden koşulur ve sürüm makalede beyan edilir. Eski Windows yerel sonuçları bu tabanla KARŞILAŞTIRILAMAZ |

### TF-HPC ilk kurulumunda ölçülenler (2026-08-27)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 17 | JupyterHub'ın önündeki nginx yükleme boyutunu sınırlıyor: `413 Request Entity Too Large`. İkili aramayla ölçüldü — **704 KiB ham geçti, 768 KiB düştü** (base64 4/3 ile `client_max_body_size=1m`) | `data/` (9,6 MB) hiç gönderilemiyordu; deploy 1. adımda düşüyordu | KAPANDI — `put_bytes_parcali()`, `PARCA_HAM=640 KiB`. Pozitif kontrol: 3 MiB 5 parçada, sha256 birebir |
| 18 | `/workspace/env.sh` **MarkLLM'in** ve `~/.bashrc` onu source ediyor; `bootstrap.sh` üzerine yazacaktı | Yazsaydı MarkLLM'in `HF_HOME`/`TRANSFORMERS_CACHE`/`PYTHONPATH`'i silinirdi — paylaşılan konteynerde DİĞER proje bozulurdu. Deploy öncesi `ls /workspace` ile yakalandı, hasar OLUŞMADI | KAPANDI — ortam `/workspace/ruhsat-bench/env.sh`'e taşındı; MarkLLM'in dosyasına ve `~/.bashrc` satırına dokunulmuyor |
| 19 | numpy sürümü iki ortamda farklı: macOS 2.4.6, HPC 2.5.2 (`rank_bm25`'in geçişli bağımlılığı) | Kabul kapısından geçen zincir numpy KULLANMIYOR — 17/17 etkilenmedi (ölçüldü) | AÇIK — `f4_dayanak.py`'nin BM25'i numpy kullanacak; o koşudan önce iki sürümün aynı sıralamayı verdiği gösterilmeli ya da numpy pinlenmeli |
| 20 | `hpc.remote sh "... &"` işi arka plana ATMIYOR: çocuk süreç koşar ama saran `/bin/bash -c` çıkmaz, çağrı zaman aşımına uğrar (300 s'de ölçüldü) | Ollama model çekimi aslında başlamıştı; yalnız istemci bekledi. Veri kaybı yok | KAPANDI — `remote.py`'de zaten doğru yapan `nohup()` vardı, CLI'ya `nohup` alt komutu olarak açıldı |

### Görev 1 zemin ölçümünde bulunan (2026-08-27)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 21 | `maddeler()` gövdeyi **4000 karakterde kırpıyor** (`uret_iddia_v3_6.py:104`, `govde[:4000]`); `korpus_kur.py:123` bu çıktıyı kullandığı için korpus kırpmayı DEVRALIYOR | **ÖLÇÜLDÜ:** 158 birimin **21'i** kırpık, **71.748 karakter** korpusta yok — Ek/Geçici kaybıyla (75.719) aynı büyüklükte. Birim SAYISI kapısından görünmez (158 yine 158). `korpus.jsonl`'da ≥4000 karakterlik birim sayısı 21, ölçümle tutuyor | KÜTÜKTE — durma kuralı. Görev 1'in kabul kriteri *"mevcut 158 birimin metni bayt-aynı"* olduğu için bu pass'te DÜZELTİLEMEZ; ayrı bir karar gerektirir. `bentler()` de 2500'de kırpıyor (TBDY) — ölçülmedi |
| 22 | Düşen 75 parçanın **1'inin Ek/Geçici öneki yok**: 4708 / "Madde 7" aslında 4708'in maddesi değil, 4708'in **değiştirdiği 3458 sayılı Kanun'un** 7. maddesinin alıntı metni | Körlemesine geri eklenirse F5 getirimi **başka bir kanunun metnini** 4708 diye döndürür | AÇIK — `maddeler2` bunu 4708 birimi olarak EKLEMEYECEK; `needs_human_review` işaretlenir (CLAUDE.md: borderline vakalar otomatik çözülmez) |

**Kapatılan risk (ölçüldü):** 473 iddianın hiçbiri Ek/Geçici maddeye atıf yapmıyor
(`iddia` metninde 0 geçiş, `madde` sütunu tümüyle sayısal, `atif_coz.py:50-52`
yalnız sayısal kalıp tanıyor). Yeni `E*`/`G*` birimleri **saf eklemedir**;
Kontrol A/B/C'yi bozamaz. Kanıt: `sonuclar/gorev1_olcum_20260827.txt`.
| 23 | `maddeler()` bölme kalıbı `MADDE N/X-` biçimini tanımıyor (`\d+\s*[–\-—]`, `/A` araya giriyor); gövdeler önceki birime kaynaşıyor | **ÖLÇÜLDÜ:** yalnız 6331'de, 2 başlık (`MADDE 24/A-`, `MADDE 25/A –`) → 6331/24 ve 6331/25 kirli. Diğer 4 belgede 0. **Altın etkisi SIFIR** (aşağıya bak) | KÜTÜKTE — EK-5 §10'un istediği tarama yapıldı; durma kuralı gereği kovalanmıyor |
| 24 | Belge sonundaki "Değişen veya İptal Edilen Maddeler" tablosu tiresiz satırlar içerdiği için bölünmüyor, son birime yapışıyor | **ÖLÇÜLDÜ:** 6331/39, 4708/15, 3194/50. Sayı/yıl yoğunluğu yüksek → P2 ve P6 için riskli görünüyordu; **altın etkisi SIFIR** | KÜTÜKTE — kovalanmıyor |
| 25 | Düşen parça kendi Ek/Geçici önekini yutuyor; dizi sınırlarında önceki birimin sonunda artık önek kalıyor | **ÖLÇÜLDÜ:** 4 birim (6331/37, 3194/47, ISGRISK/17, YDUY/34), her biri metnin SONUNDA tek kelime | KÜTÜKTE — kozmetik; `maddeler2` isterse temizler |

**EK-5 §10 birinci maddesi KAPANDI (ölçümle).** Beş kirli birimdeki **18 iddianın
18'inin** `kaynak_alinti`'sı temiz bölgeden geliyor: KAYNAŞMIS 0, bulunamadı 0,
alıntı boş 0. Kütük #2'de (`bentler()`) 7 altın etiketi dönmüştü; `maddeler()`
kaynaşmasında **dönen etiket yok**. Kanıt: `sonuclar/gorev1_olcum_20260827.txt` §6.

**Anahtar biçimi kararı (ölçümle gerekçeli):** `bent_bol.py:238-240` `~N` ekini
atıf çözerken tabana indiriyor — `~N` semantiği *"aynı birimin ikinci geçişi"*.
Geçici Madde 3, Madde 3'ün kopyası değil **başka bir maddedir**; `3~2` kullanmak
R1/R2'de "Madde 3" atfına "Geçici Madde 3" metnini döndürtebilir. `~N` bu iş için
yanlış araçtır.

### Görev 2'de ölçülen (2026-08-27)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 26 | EK-5'in altın düzeltmesi **tamamlanmamış olabilir**: aynı korpus kaymasını paylaşan iddiaların bir kısmı düzeltilmiş, bir kısmı dokunulmamış | **ÖLÇÜLDÜ:** 9 farklı kayma sınıfı var. Düzeltilen bir iddiayla **birebir aynı** kaymayı paylaşıp düzeltilmemiş **12** iddia; hiç düzeltme almamış kaymalarda **5** iddia → toplam **17** açık. Örn. `TBDY/7.2.1.4 → 7.2.4`: 5 iddiadan 2'si düzeltilmiş, 3'ü değil. **"Yalnız P1 denetlendi" demek YANLIŞ** — id=278 P1 olduğu hâlde düzeltilmemiş | AÇIK — `needs_human_review`. CLAUDE.md gereği otomatik çözülmez; tarihçiler karar verir. Kanıt: `sonuclar/gorev2_raporu.txt` §4 |
| 27 | HANDOVER §5'in iki kabul kriteri **aynı anda sağlanamaz**: "Kontrol A ≥ 440/441" ve "toplam birim > 1593" | İkincisi TBDY bölmesini gerektirir; bölme alıntıları ince birimlere taşır, iddia CSV'si bölme öncesi kimliği tutar. **ÖLÇÜLDÜ:** kaymanın 31/31'i TBDY'den, `maddeler2`'nin payı 0 | KISMEN ÇÖZÜLDÜ — `korpus_kur.py`'ye **birim-esnek tanı** eklendi (katı sayı değişmedi, kapı değişmedi). 31'in 14'ü hata değil (5 `~N` + 2 üst-birim + 7 EK-5 düzeltmesi); 17'si açık (#26) |

**EK-5 §10 ikinci maddesi KAPANDI (ölçümle).** *"R3 473/473'ün ne kadarı kaynaşmış
ayrıştırmadan pay alıyordu?"* → **7/473 = %1,48**, ve o 7 iddia EK-5'in döndürdüğü
7 altın etiketin **tam olarak kendisi**. Eski 473/473, korpus ile altının aynı
yönde yanlış olmasının ürünüydü. Kanıt: `sonuclar/gorev2_raporu.txt` §1.

### Görev 3'te ölçülen (2026-08-28)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 28 | `llama3.2:3b-instruct-q8_0` **dayanak verilince biçim talimatını bırakıyor**: iddiayı geri yazıyor, şablonu (`ETIKET\|GUVEN`) olduğu gibi basıyor, ya da tekrar döngüsüne girip bütçeyi dolduruyor | **ÖLÇÜLDÜ:** 78 çağrıda kesilen %16,7 (32 token) → %2,56 (64/128/256 **birebir aynı** — kalan 2 kesilme bütçe değil tekrar dejenerasyonu); ayrıştırılamayan 15/78. Aynı koşuda `qwen2.5:32b-instruct` **0/78 kesilme, 0 ayrıştırılamayan** | KÜTÜKTE — betik hatası DEĞİL, model bulgusu. Dayanaklı kollarda 3B sınıfı model kullanılamaz; makalede kapasite bulgusu olarak yazılabilir |
| 29 | **Dayanaklı kollar deterministik DEĞİL** — ORTAM.md §3'ün *"temperature 0 + sabit seed → 946/946 birebir"* ölçümüyle çelişiyor | **ÖLÇÜLDÜ (aynı model, aynı makine, aynı gün, aynı tohum):** kapalı kitap (`f4_kos.py`, 20 çağrı) **20/20 birebir**; dayanaklı (`f4_dayanak.py`, 20 çağrı) **17/20** — 3 fark, biri **kararın kendisi** (`DOGRU` → ayrıştırılamadı), biri güven (85 → 60). Fark uzun/dayanaklı istemle ilişkili | AÇIK — **taşıyıcı sonuç:** yerel dayanaklı kollar tek koşuyla raporlanamaz; API kollarındaki 3 koşu + çoğunluk oyu yordamı burada da gerekir. Sebep araştırılmadı (durma kuralı) |

**EK-4 §10 uyumu (ölçüldü, `qwen2.5:32b`, 78 çağrı):** kesilen **0/78 = 0.0000**;
her satırda `istem_sha256`, `sistem_sha256`, `korpus_sha256`, `betik_sha256`;
R2 geri çağırma ayrı alan ve özette zorunlu. Kanıt: `sonuclar/gorev3_raporu.txt`.

### Görev 4'te ölçülen (2026-08-28)

| # | kusur | etki ölçümü | karar |
|---|---|---|---|
| 30 | **Varyant etkisi hükmü TERSİNE DÖNDÜ.** `yama_f4_api.py` docstring'i *"kollar arası uyuşma kol içi aralığın İÇİNDE; iki kol aynı koşulun altı koşusundan ibarettir"* diyor — ama o ölçüm **yanlış yönlendirilmiş** B kolunda (B etiketi taşıyıp A istemi gönderen koşular) yapılmıştı | **ÖLÇÜLDÜ (düzeltilmiş B ile, eş granülerlik):** A@32 kol içi [0.9017, 0.9133] · B@128 kol içi [0.9165, 0.9228] · A×B [0.8266, 0.8319]. A×B **her iki bandın altında** → varyant etkisi GERÇEK | KÜTÜKTE — makalede `yama_f4_api.py` docstring'indeki eski hüküm ARTIK GEÇERSİZ; düzeltilmiş sonuç raporlanmalı |
| 31 | `f4_analiz.py` ilk sürümü, güven taşıyan kaydı çok az olan hücrelerde anlamsız ECE/Brier basıyordu | **ÖLÇÜLDÜ:** `llama3.2:3b-instruct-fp16/E1/B` hücresinde 410 taahhütten **1'i** güven taşıyor → "ECE 0.000" (kusursuz kalibrasyon görünümü). 8/56 hücrede gvn_n < 60 | **KAPANDI** — `gvn_n` sütunu + `--min-guven-n` (varsayılan 50) kapısı; eşik altında `az-n`. Eşik dışsal olarak gerekçelendirilmiş DEĞİL |

**Hâlâ açık — `frontCA32_bugun` GEREKLİ.** Uyuşma ekseninde A@128 ile A@32 ayırt
edilemiyor (0.8985–0.9038 vs band 0.9017–0.9133) ama **BAcc ekseninde A@128
(0.6395) A@32 aralığının (0.6796–0.6986) DIŞINDA**. Çelişki değil: az sayıda karar
dönmesi tek sınıfta yoğunlaşırsa uyuşmayı az, BAcc'yi çok oynatır. A@128 arşiv
koşularından **farklı bir günde** koşulduğu için tarih ve bütçe karışık; bu rapor
`frontCA32_bugun` ihtiyacını ortadan kaldırmaz, **niceleştirir**.

**Yan bulgu:** B@128 (0.6992–0.7172) A@32'den (0.6796–0.6986) yüksek ve fark kol içi
gürültünün dışında. Varyant B, varyant A'dan iyi performans veriyor.

### frontCA32_bugun sonucu (2026-08-28)

| # | kayit | ölçüm | karar |
|---|---|---|---|
| 32 | **`claude-sonnet-5` arkasındaki davranış zaman içinde DEĞİŞTİ.** EK-7'nin koşudan önce sabitlenen kuralı: BAcc ≤ 0.66 → sürüm kayması | **ÖLÇÜLDÜ:** arşiv A@32 [0.6796, 0.6986] · A@32 **bugün 0.6422** → aralık dışı, eşik altı. A@128'in düşüşü (0.6395) **bütçeye bağlanamaz** | **HANDOVER §7 dallanması KAPANDI** — sürüm kayması. Arşiv ve yeni koşular aynı tabloda karşılaştırılamaz; makalede beyan edilmeli |
| 33 | Kayma **yalnız E1'de**; E2 etkilenmemiş | arşiv E2 [0.6012, 0.6220] · bugün **0.6090 → aralık İÇİ**. Kaçınma oranı da değişmemiş (arşiv 181/184/182, bugün 178) | KAYIT — zorunlu seçim korunmuş, kaçınma kolu gerilemiş |
| 34 | **Kaçınmanın seçiciliği yarıya düştü.** BAcc(E1)−BAcc(E2) kazancı | arşiv [0.0735, 0.0784] ort **0.0762** · bugün **0.0332** = arşivin **%44'ü**, aralık dışı | KAYIT — makalenin ana savı için doğrudan kanıt: zorunlu-seçim değerlendirmesi bu gerilemeyi GÖRMEZDİ |

### Makale taslagi denetiminde yakalananlar (2026-08-28) — UCU DE ASISTAN HATASI

| # | kusur | ölçüm | karar |
|---|---|---|---|
| 35 | **"Hiçbir açık ağırlıklı model şansı aşmadı" İFADESİ YANLIŞ** — taslağın Tartışma ve Sonuç bölümlerinde vardı ve kendi Bulgular bölümüyle çelişiyordu | **ÖLÇÜLDÜ:** E1/varyant A'da **4** açık ağırlıklı modelin GA'sı 0.5'i dışlıyor: `qwen2.5:32b` [0.5833, 0.7618] · `gemma3:27b` [0.5230, 0.6115] · `llama3.2:3b-q8_0` [0.5073, 0.5963] · `gemma3:12b` [0.5139, 0.5836] | **KAPANDI** — selef makaleyi öldüren savunulamaz-iddia sınıfının aynısı. Doğru anlatı: `qwen2.5:32b` 0.6769'a **kapsam 0.173** ile ulaşıyor (82 madde); üç model ise neredeyse tam kapsamda 5–7 puan üstünde. Bu bir kapsam–isabet takasıdır |
| 36 | **"Kaçınma oranı değişmedi" İFADESİ YANLIŞ** (kullanıcıya da böyle bildirildi) | 178 ∉ [181, 184]. Doğru ifade: kaçınma **sayısı** küçük ölçüde düştü (182 ort → 178, %2,2 göreli), **kazanç** ise yarıya indi (0.0762 → 0.0332, %56 göreli). Sıklık kabaca korunurken **seçicilik** çöktü | **KAPANDI** — sayı çizelgesine düzeltme yazıldı |
| 37 | Sürüm kayması hükmü **tek koşuyu üç koşunun min-maks'ıyla** karşılaştırıyor; makalenin kendi kümeli bootstrap GA'sı [0.633, 0.750] ve bugünkü 0.6422 onun **İÇİNDE** | İki taban farklı soru cevaplıyor: bootstrap "başka iddialara genellenir mi" (maddeler değişken), koşu aralığı "aynı 473 maddede model değişti mi" (maddeler SABİT). Sürüm sorusu için doğru taban koşu aralığıdır | AÇIK — seçim makalede **gerekçelendirilmeli** ve bootstrap GA'sı da raporlanmalı; hakem soracaktır |

**Betik zinciri doğrulandı (denetimin haklı şüphesi, ölçümle kapatıldı):** arşiv koşuları
`f4_api.py` ile, bugünkü koşu yeniden üretilen `f4_api_v2.py` ile yapıldı. **Varyant A
istemleri yama öncesi/sonrası bayt-birebir** (E1 `8a8ef386b0b2b619`, E2 `64dedda000ce465e`).
SINIR: arşiv koşuları hiç hash taşımıyor; özdeşlik kayıttan değil **arşiv kaynak kodundan**
yeniden türetildi. Makalede böyle yazılmalı; "bizim tarafımızda hiçbir şey değişmedi"
cümlesi bu hâliyle savunulamaz.
