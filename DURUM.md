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

## 4. Bundan sonra — HANDOVER §4 görevleri

Kabul kapısı geçtikten sonra devam edilecek sıra değişmedi:

1. `maddeler2.py` + korpusun nihai kurulumu (kusur kütüğü #1: 75 parça ~76k karakter)
2. R3 + kontroller, düzeltilmiş korpusta
3. `f4_dayanak.py` (R1/R2 koşucusu, EK-4 şartlarıyla)
4. `f4_analiz.py` (kümeli çıkarım, standart ECE, P6 BAcc, risk–kapsam)
5. Mevcut koşuların v7a ile yeniden puanlanması

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
