# DURUM — RUHSAT-Bench, Linux/TF-HPC geçişi

**Son güncelleme:** 2026-08-27 · **Depo:** `~/Desktop/ruhsat-bench` (macOS) →
hedef `/workspace/ruhsat-bench` (TF-HPC konteyneri)

Bu dosya "şu an neredeyiz, sıradaki ne" sorusunu cevaplar. Tarihçe için
`REKONSTRUKSIYON.md`, ortam için `hpc/README.md`, görev listesi için `HANDOVER.md`.

---

## 1. Bitti (ölçülerek)

| iş | kanıt |
|---|---|
| Depo paketlerden yeniden kuruldu (204 dosya) | commit `380bea0`, kaynak sha256'ları `REKONSTRUKSIYON.md` §4 |
| Satır sonları LF'e normalize edildi (87 dosya, yalnız-CR 0) | commit `80cf672`, `sonuclar/port_satirsonu_raporu.txt` |
| **Zincir 17/17 koştu** (macOS, Python 3.11.9, pypdf 5.9.0) | commit `f3b2435`, `sonuclar/dogrulama_macos_20260827.log` |
| Altın etiketler iki kodlayıcı kitabından **birebir** yeniden üretildi | v7a/v7b LF-hash'leri devir paketiyle aynı |
| Mühürlü üreteç iki bağımsız pakette **aynı sha256** | `291f61f2…`, `REKONSTRUKSIYON.md` §3 |
| TF-HPC taşıma katmanı yazıldı (`hpc/`) | commit `8adc32b` |
| nginx 1 MiB sınırı ölçüldü (704 KiB geçer / 768 KiB düşer) → parçalı yükleme | kütük #17, pozitif kontrol 3 MiB sha256 birebir |
| MarkLLM'in `/workspace/env.sh`'i **bozulmadan** ayrıldı | kütük #18 |
| **TF-HPC'de 17/17** (Ubuntu 24.04.1, Python 3.12.3, pypdf 5.9.0) | `sonuclar/dogrulama_hpc_20260827.{txt,log}` |
| Sürüm kayması **YOK**: 6 belgenin 6'sında `metin_sha256` birebir, Δkarakter 0 | `sonuclar/ortam_kayma_hpc.json` |
| Kütük #5 daraltıldı: 870747/870751 ayrımı işletim sistemi değil, **pypdf sürümü** farkı | üç ortamda TBDY = 870747 |
| **Ollama 0.32.14 kuruldu**, CUDA görüyor, 3 model (38 GB) | `sonuclar/duman/duman_ollama_20260827.txt` |
| Uçtan uca duman testi: `f4_kos.py` iki koşuda **20/20 birebir** (deterministik) | `sonuclar/duman/duman_k{1,2}.jsonl` |
| `ortam_kayma.py` **pozitif kontrolden geçti** (planlanmış +252 karakter sapması yakalandı, çıkış 2) | bu oturumda koşuldu |
| `f4_api_v2.py` yamadan yeniden üretildi (4/4 yama, özdoğrulama geçti) | commit `75d3bde` |
| GECIS_LINUX.md §2.7 açık kalemi **kapandı**: anahtar zaten ortam değişkeninden okunuyor (`--anahtar-env`, varsayılan `LLM_API_KEY`) | `scripts/f4_api_v2.py:222` |

## 2. Kaybolan — makaleye girecek

**Git geçmişi kayboldu.** Windows deposuna erişim yok; commit tarih damgaları
gitti. Bir ön-kaydın ilgili koşudan önce yazıldığı git ile kanıtlanamaz.
Beyan metni `REKONSTRUKSIYON.md` §7'de hazır.

## 3. Port TAMAM — kapı geçildi

`/workspace/ruhsat-bench` ayakta, dört kapının dördü geçti, `linux-port-dogrulandi`
etiketi atıldı. Kodu tazelemek için:

```bash
cd ~/Desktop/ruhsat-bench && .venv/bin/python -m hpc.deploy --sadece-gonder
```

Ollama da kuruldu ve duman testinden geçti. 18 modelin tamamı gerekirse
(disk: 278 GB boş):

```bash
cd ~/Desktop/ruhsat-bench && .venv/bin/python -m hpc.remote nohup "cd /workspace/ruhsat-bench && bash hpc/remote_scripts/ollama_kur.sh --tam" --log /workspace/logs/ollama_tam.log
```

**Kurulum bitti. Sıradaki iş bilimsel: HANDOVER §4.**

## 3b. Görev 1 ve 2 BİTTİ (2026-08-27)

| iş | kanıt |
|---|---|
| `scripts/maddeler2.py` — Ek/Geçici/Mükerrer kurtarma | 158/158 bayt-aynı, 74/75 = 0.9867, öz-test 5/5 |
| `korpus_kur.py --rafine {yok,madde,bent,hepsi}` | `madde` modu üç kontrolü de geçiyor (1440 birim, çıkış 0) |
| **EK-5 §10 CEVAPLANDI** | R3'ün eski 473/473'ünün **7/473 = %1,48**'i kaynaşmadan geliyormuş; o 7, EK-5'in döndürdüğü 7 altının **tam olarak kendisi** |
| Negatif kontrol 5 tohum | `korpus_v2` ort 0.5315 · ham ort 0.5408 — bandın (0.50–0.56) içinde |
| Kontrol A birim-esnek tanı | 31 = 5 `~N` + 2 üst-birim + 24 ilişkisiz (7'si EK-5 düzeltmesi) → 17 gerçekten açık |
| Kapı korundu | `dogrula_linux.sh` iki kez yeniden koşuldu: **17/17** |

Raporlar: `sonuclar/gorev1_raporu.txt`, `sonuclar/gorev2_raporu.txt`,
`sonuclar/gorev1_olcum_20260827.txt`, `sonuclar/maddeler2_raporu.txt`

## 3d. Görev 3 BİTTİ (2026-08-28)

`scripts/f4_dayanak.py` — R1/R2/R3-bm25, EK-4 + **EK-6** şartlarıyla.
Beyan EK-6 (korpus seçimi) **koşudan önce** yazılıp commit'lendi.

Kabul kriterleri geçti: istem sha'ları basılıyor · R1 istemi doğru birim
metnini içeriyor (3 örnek elle gösterildi) · R2 geri çağırma alanı dolu ·
kesilen 0/78 (`qwen2.5:32b`).

**İki taşıyıcı bulgu — üretim koşusunu etkiler:**

1. **3B sınıfı model dayanaklı kolda kullanılamaz** (kütük #28). `llama3.2:3b`
   dayanak verilince biçim talimatını bırakıyor; ayrıştırılamayan 15/78.
   `qwen2.5:32b` aynı istemle 0/78.
2. **Dayanaklı kollar deterministik değil** (kütük #29). Aynı model/makine/gün/
   tohum: kapalı kitap 20/20 birebir, dayanaklı **17/20**. Biri kararın kendisi.
   → Yerel dayanaklı kollar **3 koşu + çoğunluk oyu** gerektirir; üretim
   maliyeti 3 katına çıkar.

## 3c. Görev 3'ün korpus kapısı — EK-6 ile ÇÖZÜLDÜ

`korpus_kur.py` rafine korpusu kendi kapısıyla reddediyor (çıkış 2):
*"31 alıntı BAŞKA birimde — bu maddelerde dayanaklı kol modele YANLIŞ maddeyi
gösterir."* Ölçüm bunun 14'ünün hata olmadığını gösterdi; kalan **17 iddia**
(kütük #26) tarihçi kararı bekliyor — CLAUDE.md gereği otomatik çözülmez.

Görev 3'ün betiği bu karardan bağımsız yazılabilir; **üretim koşusu** için
korpus seçimi bu 17'ye bağlı.

## 3e. Görev 4 ve 5 BİTTİ (2026-08-28)

`scripts/f4_analiz.py` — `f4_skor.py`'ye **dokunulmadan**.

| iş | sonuç |
|---|---|
| Standart ECE (kütük **#6 KAPANDI**) | pozitif kontrol 3 çiftte, standart **0.0000** vs arşiv **0.0500** |
| Kümeli bootstrap (10k, küme=kanun+madde) | Sonnet E1 **0.692 [0.633, 0.750]**; Haiku E1 0.530 **[0.489, 0.570] → 0.5'i içeriyor** |
| B kol içi bandı (kütük **#8 KAPANDI**) | A@32 [0.9017, 0.9133] · B@128 [0.9165, 0.9228] · A×B **0.8302 → band altı** |
| P6 prob içi BAcc | tek sınıflı tabakalar "altın sınıfı seçme oranı" diye etiketlendi |
| Risk–kapsam | E1 güven eşiği taranarak model başına |
| Üç altın tek tabloda | 56 hücre, v7a birincil + v6/v7b duyarlılık |
| **Görev 5** | `sonuclar/f4_analiz_raporu.txt` (885 satır) + `f4_analiz.csv` (56 hücre) |

**Yeni bulgular:** varyant etkisi hükmü **tersine döndü** (kütük #30) — düzeltilmiş
B koluyla A×B uyuşması her iki bandın altında; `yama_f4_api.py`'nin eski hükmü
artık geçersiz. Ve kendi analizimde bir kusur çıkıp kapandı (kütük #31): güven
taşıyan kaydı az olan hücreler "ECE 0.000" basıyordu.

**Mühürlü dosyalar doğrulandı:** `uret_iddia_v3_6.py`, `f4_skor.py`, `f4_api.py`,
`f4_kos.py`, `bent_bol.py`, `bentler2.py`, `atif_coz.py`, `kural_taban.py` —
rekonstrüksiyondan beri **hiçbiri değişmedi** (HANDOVER §5 son kriteri).

## 4. Bundan sonra — HANDOVER §4 görevleri

Kabul kapısı geçtikten sonra devam edilecek sıra değişmedi:

1. ~~`maddeler2.py` + korpusun kurulumu~~ **BİTTİ**
2. ~~R3 + kontroller, düzeltilmiş korpusta~~ **BİTTİ** (EK-5 §10 cevaplandı)
3. ~~`f4_dayanak.py` (R1/R2 koşucusu)~~ **BİTTİ** (EK-6 beyanıyla)
4. ~~`f4_analiz.py`~~ **BİTTİ**
5. ~~v7a ile yeniden puanlama~~ **BİTTİ** (Görev 4 çıktısı)

**HANDOVER §4'ün beş görevi de kapandı.** Kalan iş koşu ve yazım — HANDOVER'da "sende değil" diye işaretli.

## 5. Kullanıcıda bekleyen (asistanda değil)

- `frontCA32_bugun` koşusu — sürüm kayması mı bütçe etkisi mi (HANDOVER §7 dallanması)
- İki kodlayıcının kural notu **imzaları** — v7a imzasız dondurulamaz.
  Doldurulmuş notlar depoda: `uzlasi/kodlayici1_UZLASI_KURAL_NOTU_doldurulmus.md`,
  `uzlasi/kodlayici2_UZLASI_KURAL_NOTU_DOLU.md`
- F5 API koşuları (anahtar kullanıcıda), P6 için 20 maddelik mevzuat.gov.tr doğrulaması

## 6. Ortam farkı — açık ve izlenen

| | referans ölçüm (02 Ağu) | rekonstrüksiyon | TF-HPC |
|---|---|---|---|
| işletim sistemi | Ubuntu 24.04 | macOS 25.5 | Ubuntu 24.04.1 |
| Python | 3.12.3 | **3.11.9** | 3.12.3 |
| pypdf | 5.9.0 | 5.9.0 | 5.9.0 |
| numpy | — | 2.4.6 | **2.5.2** (kütük #19) |
| zincir | 17/17 | **17/17** | **17/17** |
| TBDY karakter | 870747 | 870747 | 870747 |

Zincir **üç ortamda da** aynı sayıları verdi. pypdf 5.9.0 sabitken metin çıkarımı
macOS ve Linux'ta bayt-birebir — kütük #5'in "iki ortam" ifadesi artık "iki pypdf
sürümü" diye daraltılabilir. Tek açık ortam farkı numpy; kapıdan geçen zincir
onu kullanmıyor ama `f4_dayanak.py`'nin BM25'i kullanacak.

## 7. 5. TUR — makale yazimi (29.08.2026)

`makale/RUHSAT_JESTECH_taslak_tur5.md` (tur4'ten uretildi, 4. tur denetiminin
buldugu her kalem islendi).

| kalem | ne yapildi |
|---|---|
| Abstract + Keywords + yazar blogu | YAZILDI (yazar alanlari bilerek BOS) |
| **Ön-kayitli birincil aile H1/H2** | YENI 4.6.3 + Tablo 6; dordu de sifiri disliyor |
| Bonferroni ailesi | 4.3.1 duzeltildi: Bonferroni-**17** (ana on kayit 1.2), 2 degil. Sonnet [+0.0018, +0.1343] — KIL PAYI |
| Delta | Tablo 4'e %95 GA sutunu; 7 aralikin 5'i sifiri disliyor |
| Delta nuansi | 4.4 + 5.2: **Delta ekseninde bugun ile arsiv AYIRT EDILEMIYOR**; surum kaymasi BAcc farkina dayanir |
| EK-7 karar kurali | 4.4'e AYNEN yazildi: [0.6796,0.6986] butce · <=0.66 kayma · arada belirsiz; 0.66'nin dissal gerekcesi YOK, boyle yaziliyor |
| lambda | tek tanim (kodla ayni). P1 "always-true" DEGIL: 163 iddianin 156'si dogru, 7'si yanlis |
| A_nc / A_abs | her yerde **A_nc** |
| 5.4 aralik hatasi | "touch" -> R1/E1 alt 0.8804 > R2/E1 ust 0.8579, **AYRIKLAR** |
| manset statusu | R2-R3bm25'in EK-4 4'te **ikincil/kesifsel** oldugu yazildi |
| capraz gonderme | 3.7'deki "Tablo 3" -> Tablo 4 |
| Kaynakca | tur4'te bitmisti; 17 atif OpenAlex'ten dogrulandi, 3 yil kaymasi duzeltildi |

**Sayi denetimi:** taslaktaki 265 ayrik ondalik degerin tamami tarandi.
5. turda GIREN ve kanonik cizelgede olmayan tek deger `0.6395` idi (A@128);
muhurlu `f4_skor.py` ile v7a altina karsi YENIDEN URETILDI ve cizelgeye
eklendi. Kalan eslesmeyenler DOI/arXiv numaralari ve bolum numaralari.

### ACIK TEK KALEM — EK-6 duyarlilik kolu (1366)

EK-6 3 zorunlu tutuyor ve makale bu tabloyu VAAT EDIYOR. TF-HPC kolu
baslatilmisti ama **VPN kapali**, cikti alinamadi.

Cozum: **EK-8** yazildi ve commit'lendi (kosudan ONCE), kol YEREL makinede
kosuluyor (`sonuclar/f5/duyarlilik_1366_yerel.jsonl`).
Kuru kosu ile HPC'ye karsi `istem_sha256` / `korpus_sha256` / `getirilen`
**124/124 birebir** — boru hatti ozdes, tek bilinmeyen model agirliklari.
EK-8 3 bunun icin davranissal pozitif kontrol kapisi koydu (120 cagri,
`ham` birebir). Kapi dusetse kol yine kosulur ama **tablo yan yana
verilmez**, karisiklik raporlanir.

Taslakta bu bosluk `[STATUS — TO BE COMPLETED BEFORE SUBMISSION]` diye
GORUNUR birakildi; kolun sayisi gelmeden makale gonderilmez.

### EK-6 DUYARLILIK KOLU — KAPANDI (30.08.2026)

VPN geldi. Kol TF-HPC'de zaten bitmişti (29 Ağu 12:34, 1997 kayıt).
İndirildi; `sha256` uzaktaki dosyayla **birebir**
(`1cb99fb8611a4689…`). EK-4 §10 geçersizlik şartları geçti: kesilen
0/1524, geri çağırma basıldı, 1997/1997 `tamam`.

**Ön koşul sınandı:** birincil kol 3 koşunun çoğunluğu, duyarlılık kolu tek
koşu. Üç koşu **1524/1524 birebir** olduğu için çoğunluk oyu = tek koşu;
karşılaştırma eşit granülerlikte.

**Sonuç — hiçbir kolda korpus etkisi sıfırı dışlamıyor:**

| kol | koşul | 1755 | 1366 | eşli fark | %95 GA |
|---|---|---|---|---|---|
| R1 | E1 | 0.9164 | 0.8976 | +0.0188 | [−0.0040, +0.0475] |
| R1 | E2 | 0.8615 | 0.8486 | +0.0128 | [+0.0000, +0.0343] |
| R2 | E1 | 0.8229 | 0.8159 | +0.0070 | [−0.0203, +0.0354] |
| R2 | E2 | 0.8100 | 0.8027 | +0.0073 | [−0.0151, +0.0296] |
| R3-BM25 | — | 0.5938 | 0.5938 | +0.0000 | — |

Makaleye **§4.6.5 + Tablo 7** olarak girdi; §3.2'deki yer tutucu kaldırıldı.

**İki yan bulgu:**
1. Ham korpusun BM25 geri çağırması **daha yüksek** (0.3010 vs 0.2734) ama
   dört dayanaklı hücrenin dördünde de puanı **daha düşük**. §4.6.4'ün
   "getirim doğruluğa tavan koymaz" bulgusunun bağımsız ikinci kanıtı.
2. R3-BM25 iki korpusta **473/473 aynı** kararı veriyor; getirilen pasaj
   kümesi 271/473 iddiada farklı olmasına rağmen. Boru hattı hatası
   olmadığı korpus sha256 ve getirilen listeleri karşılaştırılarak
   doğrulandı.

**Kendi hatam, pozitif kontrolle yakalandı:** eşli bootstrap'ta küme
anahtarını `kanun`/`madde` diye almıştım; altın kayıtta o alanlar yok,
doğrusu `altin[id]['kume']`. Yanlış anahtar her şeyi tek kümeye topluyor ve
**sıfır genişlikte GA** üretiyordu. Bilinen bir sonuç (R2−R3bm25 +0.2292
[+0.1939, +0.2635]) yeniden üretilerek kapı kondu; düzeltilmiş uygulama
+0.2292 [+0.1932, +0.2639] veriyor.

**Yerel koşu denemesi:** VPN yokken kol yerelde koşulmak istendi (EK-8
beyanı koşudan önce yazıldı ve commit'lendi). 32B model bu makinenin
belleğine sığmadı — swap 20 GB'ın 19,7 GB'ı dolu ölçüldü — ve koşu
durduruldu. Rapor: `sonuclar/ek8_yerel_kosu_raporu.txt`. EK-8 arşivde
kalıyor; kapıya varılamadığı yazılı.

## 8. DENETİM TURLARI 5 VE 6 (30.08.2026)

İki tur koştu: 5. tur (5 mercek) **43 bulgu**, 6. tur doğrulama (4 mercek)
**28 bulgu**. Hepsi işlendi. Ölçüm gerektiren yedi tanesi:

| bulgu | sonuç |
|---|---|
| Bonferroni ailesi "17" | **türetilemiyor** — sayım 28/21/15/18/20 veriyor. Aile **20** (koşulan model) oldu; Tablo 3b aile 2–21 duyarlılığını veriyor, hüküm hiç değişmiyor |
| "18 model koşuldu" | yanlış; 18 yalnız açık ağırlıklı. Koşulan **20** (18 + 2 barındırılan) |
| λ'nın nötr noktası | 0 değil **±0.0429** (P1 156/163 doğru) |
| R3-BM25'in λ'sı | −0.043 = sabit-DOĞRU değerinin ta kendisi; DOĞRU dediği küme **P1∪P5'in birebir kendisi** (284/473) |
| H2/E1'in R0 tabanı | **29 taahhüt**, kendi 30 kapımızın altında — işaretlendi, dayanılmadı |
| λ'nın altın duyarlılığı | 4 hücrenin **3'ünde BAcc'den fazla** oynuyor — 5. turda tersini yazmıştım |
| v6 altında hüküm | **değişiyor**: gemma3:12b v6'da şansı aşıyor (0.5013), v7a'da aşmıyor (0.4915) |

**Yerine getirilmemiş üç ön kayıt taahhüdü bulundu ve karşılandı:**

* **EK-1 §1 orijinal kapı kolu** — koşuldu. Sonuç sert: orijinal kuralla
  7 hücre puanlanır, 13 elenir; elenenler arasında sonnet (0.615),
  haiku (0.710) ve qwen32b (0.173) var. **Bu sapma taşıyıcı**, korpus
  sapmasının aksine. Makale artık bunu açıkça söylüyor.
* **EK-6 §4 — 17 needs_human_review iddiası** — ayrı satır (Tablo 8) +
  duyarlılık; manşeti hareket ettirmiyor.
* **EK-5 §8 — v6/v7 çifte altın** — §4.7.3 olarak yazıldı, yukarıdaki
  hüküm değişimiyle birlikte.
* **Ana ön kayıt md.2/md.6 alt-tür kırılımı** — §4.3.3. Yeni bulgu:
  **sonnet 120 P6 iddiasının 119'una YANLIŞ diyor**; 0.508'lik "şans"
  görüntüsü 60/60 dengeli tasarımın artefaktı.
* **EK-2 ve EK-3** ilk kez anıldı (varyant B'nin rol değişimi;
  düşünme açıkken koşulan 8 arşiv koşusunun neden raporlanmadığı).

**Düzeltilen ciddi provenans hatası:** §4.6.6'da 17 vakanın "uzman
kodlayıcılarca karara bağlandığını" yazmıştım. Yanlış: kararları bir **dil
modeli** verdi (kitapta `KODLAYICI: GPT-5.6 Pro`), üç etiket değişikliği
önerdi, öneriler EK-4 §2/§9(d) gerekçesiyle geri alındı ve **R3-rule bunu
bağımsız yakaladı** (473/473 → 470/473, tam o üç id). 17 iddia hâlâ
`needs_human_review`.

**Sayı disiplini:** taslaktaki 337 ayrık ondalık değerin tamamı tarandı;
kanonik çizelgede olmayan hiçbir yeni sayı yok. Çizelgeye 5. ve 6. tur
bölümleri eklendi (`ONCEKI SATIRLARI EZER`).

### AÇIK KALAN TEK İÇERİK KARARI: UZUNLUK

26.824 kelime, JESTECH tipik uzunluğunun ~3 katı. Kesme değil **ayırma**
öneriliyor (ek dosya); somut plan `KILAVUZ.md` SIRA 4'te. Ali'nin onayı
olmadan yapılmadı.

Taslakta bilerek boş iki alan: **yazar bloğu** ve **arşiv DOI'si**. İkincisi
için makaleye "bu blok dolmadan gönderilmez" notu konuldu, çünkü öz
"released" diyor.

## 9. MAKALE AYRILDI (30.08.2026)

Hakemin tek büyük itirazı uzunluktu: 26.824 kelime, JESTECH'in ~3 katı.
**Karar: kesme değil ayırma.**

| dosya | kelime | ne |
|---|---|---|
| `makale/RUHSAT_JESTECH_ana_metin.md` | 9.741 | gönderilecek |
| `makale/RUHSAT_JESTECH_ek.md` | 9.333 | S1–S9 supplementary |
| `makale/RUHSAT_JESTECH_taslak_tur5.md` | 26.824 | kaynak, arşivde kalır |

Ana metin **baştan yazıldı** — 26.824'ten 19.074'e inen fark (7.750 kelime)
taşınmadı, sıkıştırıldı. Ek ise tur5'in denetimden geçmiş metninin **birebir
kendisi**; yalnız tablo etiketleri Table S1–S7'ye çevrildi.

**Ayırma kuralı: hiçbir dürüstlük beyanı eke gömülmedi.** Ana metinde kalanlar:
EK-1 kapı sapmasının taşıyıcı olduğu · λ'nın nötr noktasının ±0.0429 olduğu ·
R3-BM25'in P1∪P5 üzerinde sabit cevap verdiği · H2/E1'in 29 taahhüt üzerinde
olduğu · v6 altında gemma3:12b hükmünün değiştiği · 17 vakayı bir dil modelinin
karara bağladığı · ikinci geçiş κ'sının aralığı · arşiv koşularının zaman
damgası taşımadığı · EK-2 ve EK-3. Eke giden yalnızca dökümler ve tablolar.

**Doğrulandı:** ana metindeki 205 ayrık ondalık değerin tamamı kanonik
çizelgeyle uyuşuyor (eşleşmeyen 5'i DOI parçası); ekte 0 eşleşmeyen. Kırık
bölüm göndermesi yok. Dokuz S bölümünün dokuzuna da atıf var.

**Ali'de kalan:** imzalar · yazar bloğu · arşiv DOI'si. Başka içerik kararı yok.
