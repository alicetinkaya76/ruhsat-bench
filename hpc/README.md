# `hpc/` — Selçuk TF-HPC ortam katmanı (RUHSAT-Bench)

Bu klasör **ortama ait olan her şeyi** tutar. Bilimsel kod `scripts/` altında kalır ve
**değiştirilmez** — `uret_iddia_v3_6.py` mühürlü, `f4_skor.py` ve `f4_api_v2.py`
arşiv karşılaştırılabilirliği için donduruldu. Buradaki dosyalar `scripts/`'i
*taşır ve koşturur*, kopyalamaz.

Desen MarkLLM projesinden devralındı; `remote.py` oradan **uyarlandı** (aynı
JupyterHub, aynı tuzaklar). Değişenler yalnız `REMOTE_ROOT` ve `PROBE`.

---

## 1. Ortam envanteri

**2026-08-27'de bu projede ölçüldü** (`python -m hpc.remote probe`; sapan
satırlar MarkLLM'in 2026-08-19 ölçümüyle yan yana verildi).

| | | 19 Ağu (MarkLLM) |
|---|---|---|
| Erişim | JupyterHub → kullanıcı başına Docker konteyneri, içinde **root**, `cwd=/workspace` | aynı |
| | SSH/SLURM **yok**. Yalnız **üniversite VPN'i**; sertifika **kendinden imzalı** → `verify=False` | aynı |
| | ⚠ Önünde **nginx/1.18.0**, `client_max_body_size=1m` → yükleme parçalanmalı (kütük #17) | ölçülmemişti |
| GPU | **Quadro RTX 8000** · 49152 MiB · sürücü 580.159.03 · **1 MiB kullanımda, %0** | aynı kart |
| CPU / RAM | konteynere **12** çekirdek · 125 GB | aynı |
| Disk | `/workspace` **ext4 gerçek blok cihaz**, 685 GB toplam, **280 GB boş** | 478 GB boştu |
| OS / Python | Ubuntu 24.04.1 LTS · **Python 3.12.3** | aynı |
| Ortak durum | `/workspace/env.sh`, `/workspace/hf` (52 GB), `/workspace/MarkLLM` **MarkLLM'e ait** — dokunulmaz (kütük #18) | — |

**Kabul testi 2026-08-27'de geçti: 17/17, sürüm kayması YOK.**
Kanıt: `sonuclar/dogrulama_hpc_20260827.{txt,log}`, `sonuclar/ortam_kayma_hpc.json`.
Altı belgenin altısında `metin_sha256` macOS ölçümüyle birebir (Δkarakter = 0).

### Ollama (2026-08-27 ölçüldü)

| | |
|---|---|
| sürüm | **0.32.14** — `.tar.zst` (v0.32+ `.tgz` yayınlamıyor), sha256 `c620917a…` doğrulandı |
| hızlandırıcı | **CUDA**, compute 7.5, Quadro RTX 8000, 47,1 GiB kullanılabilir |
| modeller | `qwen2.5:32b-instruct` · `gemma3:27b` · `llama3.2:3b-instruct-q8_0` — 3/3, 0 hata, **38 GB** |
| model dizini | `/workspace/ollama/models` → ext4 blok cihaz, **overlay değil** |
| sunucu | `127.0.0.1:11434`, `setsid nohup` altında |
| uçtan uca | `scripts/f4_kos.py` iki koşuda **20/20 birebir** → deterministik |

Kanıt: `sonuclar/duman/duman_ollama_20260827.txt`, `duman_k{1,2}.jsonl`.
⚠ Windows koşularının Ollama sürümü kayıtlı olmadığı için (kütük #16) bu **yeni
bir tabandır**; eski yerel sonuçlarla karşılaştırılamaz ve makalede beyan edilir.

Windows tarafındaki eski ortam (`ORTAM.md`): Windows/RDP, PowerShell 5.1,
Python 3.13, Quadro RTX 8000 48 GB, D: sürücüsünde ~57 GB boş.

## 2. Kurulum

```bash
# 0) tek seferlik: .env'e TFHPC_TOKEN + TFHPC_USER (PAROLA DEGIL, token)
#    MarkLLM'de zaten varsa kopyalanabilir:
#      cp ~/Desktop/MarkLLM/MarkLLM/.env ~/Desktop/ruhsat-bench/.env
#    .env gitignore'da; kabuk gecmisine token YAZMAYIN (ORTAM.md 5).

# 1) yerel tasima bagimliliklari
.venv/bin/pip install -r hpc/requirements-hpc.txt

# 2) VPN acikken:
python -m hpc.remote probe            # once ortami GOR
python -m hpc.deploy                  # gonder + kur + kayma olcumu + KABUL KAPISI
python -m hpc.deploy --ollama         # + Ollama (asgari 3 model)
```

`deploy.py` dört adımı sırayla koşar ve **her biri kapıdır**:

| adım | ne yapar | düşerse |
|---|---|---|
| 1 gönder | depoyu tek tar olarak `/workspace/ruhsat-bench`'e açar | — |
| 2 bootstrap | temiz venv + `requirements.txt` pinleri + `py_compile` | çıkış 1 |
| 3 sürüm kayması | `ortam_kayma.py`: pypdf metin çıkarımı belge belge | çıkış 2 |
| 4 kabul kapısı | `scripts/dogrula_linux.sh` → **17/17 şart** | çıkış 3 |

17/17 görülmeden yeni koşu başlatılmaz (GECIS_LINUX.md §5).

## 3. Dosyalar

| dosya | nerede çalışır | ne yapar |
|---|---|---|
| `remote.py` | **yerel** | JupyterHub REST + websocket istemcisi (token ile) |
| `deploy.py` | **yerel** | gönder → bootstrap → kayma → kabul kapısı |
| `remote_scripts/bootstrap.sh` | **konteyner** | dizinler, temiz venv, pinli paketler, derlenebilirlik |
| `remote_scripts/ortam_kayma.py` | **konteyner** | pypdf metin çıkarımı kayması (kusur kütüğü #5) |
| `remote_scripts/ollama_kur.sh` | **konteyner** | Ollama ikilisi + sunucu + model çekme |

```bash
python -m hpc.remote probe
python -m hpc.remote sh "nvidia-smi"
python -m hpc.remote sh "cd /workspace/ruhsat-bench && python scripts/kural_taban.py --help" --venv
python -m hpc.remote push scripts                     # yalniz kodu tazele
python -m hpc.remote log /workspace/logs/kosu.log -n 60
python -m hpc.remote get /workspace/ruhsat-bench/sonuclar/r3.jsonl ./r3.jsonl
```

## 4. Tasarım kararları

1. **Her şey `/workspace` altında.** Konteynerin kökü *overlay*'dir; idle-culler
   sunucuyu durdurunca yazılabilir katman gider. MarkLLM'de aynı hata HF önbelleğinde
   ölçülmüştü (30 GB uçacaktı). Buradaki karşılığı **`OLLAMA_MODELS`**: varsayılan
   `~/.ollama` overlay'dedir, 18 modelin tamamı her yeniden başlatmada uçardı.

2. **Temiz venv** (MarkLLM'deki `--system-site-packages`'in tersi). Orada sistemdeki
   torch sürücüyle eşleşiyordu ve korunmalıydı. Burada torch yok; buna karşılık
   **pypdf sürümü bilimsel olarak bağlayıcı** (kütük #5: iki sürüm TBDY'de 870747 /
   870751 karakter verdi). Sistem paketleri pini gölgelemesin diye temiz venv.

3. **`requirements.txt` dokunulmaz.** Taşıma katmanının kendi bağımlılıkları
   `hpc/requirements-hpc.txt`'de ve yalnız YEREL tarafta kurulur; konteynere girmez,
   sonuçlara karışmaz.

4. **`127.0.0.1`, `localhost` değil.** ORTAM.md §2.1'de ölçüldü: aynı 946 çağrı
   `localhost` ile 47,7 dk, `127.0.0.1` ile 11,2 dk (×4,2), çıktılar 946/946 aynı.

5. **Uzun işler `remote.nohup()` ile.** VPN düşerse istemci kopar, konteynerdeki iş
   kopmaz. Çekirdek hücresinde uzun iş çalıştırmak tercih edilmez: websocket kopunca
   çekirdek öldürülebilir.

6. **GPU tek ve paylaşımlı.** MarkLLM oturumu aynı kartı kullanıyor. Model
   yüklemeden önce `nvidia-smi`; iki oturumun aynı anda model yüklememesi için sıra.

## 5. ÖLÇÜLMEMİŞ — iddia edilmiyor

Projenin kuralı "ölçülmeyeni varsayma". Bu satırlar henüz **ölçüm değildir**:

| bilinmeyen | nasıl ölçülecek |
|---|---|
| numpy 2.4.6 ↔ 2.5.2 BM25 sıralaması | `f4_dayanak.py` koşusundan önce iki sürüm aynı sıralamayı veriyor mu gösterilecek, yoksa numpy pinlenecek (kütük #19) |
| `/workspace` kotası | `quota` komutu yok; gerçek tüketim izlenerek ölçülecek |
| API kolları | anahtar kullanıcıda; koşuyu kullanıcı yapar |

**Kapanmış olanlar** (bu bölümden çıkarıldı, çünkü artık ölçüm): `bootstrap.sh`
hedef ortamda koşuyor (2/5–5/5 geçti) · Python 3.12.3 ile zincir 17/17 ·
`f4_api_v2.py` anahtarı `os.environ`'dan okuyor (`--anahtar-env`, varsayılan
`LLM_API_KEY`) — GECIS_LINUX.md §2.7'nin açık kalemi kapandı · `ollama_kur.sh`
koştu (kütük #15) ve yeni Ollama tabanı ilan edildi (kütük #16).

## 6. Değişmeyen kurallar

`ORTAM.md`'nin çekirdeği aynen geçerli; yalnız kabuk değişti (PowerShell 5.1 → bash):

- Tahmine değil ölçüme güven. Her yeni kontrol için **pozitif kontrol**.
- Beyan koşudan **önce** yazılır ve commit'lenir.
- Dosya IO `utf-8-sig`; betik başında stdout/stderr UTF-8 reconfigure **kalır**.
- Başarısız denemeler silinmez, arşivlenir.
- Kusur avı kapalı; yeni kusur → `kusur_kutugu.md`, kullanıcıya bildir, işine dön.
- Kesilen yanıt oranı herhangi bir kolda >%1 ise koşu geçersiz (EK-4 m.10).
