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
