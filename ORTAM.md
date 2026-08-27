# ÇALIŞMA ORTAMI — RUHSAT-Bench

Bir sonraki oturumda bu dosyayı ilk sırada okut. Buradaki her madde bu
oturumda **ölçülerek** öğrenildi; tahmin değil.

---

## 1. Makine ve erişim

| | |
|---|---|
| Sistem | Windows, RDP üzerinden |
| Çalışma dizini | `D:\jestech\ruhsat-bench` |
| Kabuk | PowerShell 5.1 |
| Python | 3.13, `.venv` içinde (`.\.venv\Scripts\Activate.ps1`) |
| Ayrıca | conda `base` aktif (prompt'ta `(base)` görünür) |
| GPU | Quadro RTX 8000, 48 GB |
| Yerel çıkarım | Ollama |
| Disk | D: sürücüsünde ~57 GB boş |

## 2. Sert kurallar (ihlal edilirse iş bozulur)

### 2.1 `localhost` DEĞİL, `127.0.0.1`
Windows'ta `localhost` önce IPv6 `::1`'e çözülür, Ollama IPv4'te dinlediği için
bağlantı zaman aşımına uğrayıp IPv4'e düşer. **Çağrı başına ~2.3 saniye ceza.**

Ölçüm: aynı 946 çağrı → `localhost` **47.7 dk**, `127.0.0.1` **11.2 dk** (×4.2),
çıktılar **946/946 birebir aynı**. `f4_kos.py` varsayılanı artık IP.

### 2.2 Kodlama
- Python **daima** `utf-8-sig` ile yazar, yoksa PowerShell Türkçe karakterleri bozar.
- Python **daima** `utf-8-sig` ile okur — PowerShell `Set-Content -Encoding UTF8`
  dosya başına BOM koyar ve `utf-8` ile okumak `JSONDecodeError` verir.
- PowerShell: `Import-Csv -Encoding UTF8`

### 2.3 Uyku kapalı
```powershell
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change monitor-timeout-ac 0
```
Kapatılmadan önce bir koşuda 28 dakika askıda geçti (47 dk çıkarım, 75 dk duvar saati).

### 2.4 `Measure-Command` kullanmayın
Çıktıyı yutar; koşu takılmış sanılır. `python -u` ile tamponsuz çalıştırın.
Betikler zaten geçen/kalan süreyi basar.

### 2.5 Betik çıktı adları
`f4_skor.py` artık girdi adından türetiyor. Yine de farklı bir `--jsonl` verirken
`--out` ve `--rapor` da verin. Bir kez `det2.jsonl` puanlaması 18 modellik
`f4_metrikler.csv`'yi ezdi (ham jsonl duruyordu, yeniden üretildi).

## 3. Ollama davranışı (ölçüldü)

| | |
|---|---|
| Sabit istek maliyeti | ~0.9 s/çağrı (model boyutundan bağımsız) |
| Saf hesap | 0.24–0.7 s |
| İlk yükleme (32b) | ~49 s, model başına bir kez |
| `keep_alive` | işe yaramadı |
| `num_ctx` düşürmek | çıktıyı değiştirmiyor (25/25 aynı) ama hızlandırmıyor (×1.00) |
| gemma3 önbellek | SWA nedeniyle kullanılamıyor, her çağrıda tam istem işleme |
| Determinizm | `temperature 0` + sabit `seed` → **946/946 birebir tekrar** |

**Tam yerel matris:** 18 model × 2 koşul × 473 iddia = 17.028 çağrı ≈ **148 dakika**.

## 4. Anthropic API davranışı (ölçüldü)

| | |
|---|---|
| `temperature` | **claude-sonnet-5 KABUL ETMİYOR** (400 döner). Gönderilmemeli. |
| Determinizm | garanti değil → **3 koşu + çoğunluk oyu** zorunlu |
| Tekrar oranı (düşünme kapalı) | sonnet oybirliği 0.84/0.88 · haiku 0.73/0.81 |
| Genişletilmiş düşünme | **VARSAYILAN AÇIK.** Kapatılmazsa bütçe düşünmeye gider, `text` bloğu hiç oluşmaz |
| Düşünme kapalı token | ~10 çıktı token/çağrı (yerel modellerin 6–11 aralığıyla eşit) |
| Bir koşu maliyeti | 946 çağrı ≈ 262k girdi + 10k çıktı token, ~29 dk |

**Doğru çağrı biçimi:**
```powershell
python -u scripts\f4_api.py --saglayici anthropic --taban https://api.anthropic.com `
  --models claude-sonnet-5 --dusunme kapali --max-token 32 --out sonuclar\<ad>.jsonl
```

Betik her koşu sonunda `dusunme 0` doğrulamasını basar. Sıfır değilse o kol
birincil sayılmaz.

## 5. API anahtarı

**Komut satırına YAZMAYIN** — bu oturumda iki kez açık metin olarak yapıştırıldı
ve iptal edilmesi gerekti.

```powershell
[Environment]::SetEnvironmentVariable("LLM_API_KEY","<anahtar>","User")
Remove-Item (Get-PSReadlineOption).HistorySavePath -Force -ErrorAction SilentlyContinue
```
Yeni oturumda `$env:LLM_API_KEY` otomatik dolu gelir.

## 6. Dosya alışverişi

- Kullanıcının yüklemeleri **sık sık sıfır bayt** gelir → konsol çıktısını metin
  olarak yapıştırır. Zip bazen sağlam geçer.
- Asistan çıktıları indirilir, sonra `Move-Item ... "D:\jestech\ruhsat-bench\scripts\" -Force`

## 7. İletişim tercihleri

- Komutlar **yorumsuz, kopyala-yapıştır hazır PowerShell blokları** olarak
- Konuşma Türkçe, akademik çıktılar İngilizce
- Derin akıl yürütme, kısa konuşma
- **Tahmine değil ölçüme güven. Her yeni kontrol için pozitif kontrol iste.**

## 8. Kurulu yerel modeller

```
qwen2.5: 32b-instruct, 14b-instruct,
         7b-instruct  (q4_K_M, q5_K_M, q8_0, fp16),
         3b-instruct  (q4_K_M, q5_K_M, q8_0, fp16)
gemma3:  27b, 12b, 4b
llama3.2: 3b-instruct (q4_K_M, q5_K_M, q8_0, fp16), 1b
```

## 9. Bağlı MCP sunucuları

Dergipark MCP · Gmail · Google Calendar · Google Drive · markitdown-mcp ·
YEK MCP · YokTez MCP · YÖK Atlas MCP

**Kaynak taraması için:** DergiPark MCP (Türkçe literatür) + `literature-review`
skill'i (PubMed, OpenAlex, Crossref, Semantic Scholar, arXiv, Scopus, WoS).
