# RUHSAT-Bench — LINUX'A GEÇİŞ KILAVUZU
**02.08.2026** · Hedef: depoyu Windows'tan yeni bir Linux makinesine, beyan zincirini kırmadan taşımak ve akışı orada sürdürmek.

Bu kılavuzdaki her doğrulama sayısı tahmin değil, ölçümdür: zincirin tamamı
Ubuntu 24 / Python 3.12.3 / pypdf 5.9.0 üzerinde koşuldu ve `dogrula_linux.sh`
**17/17** verdi. Sizin kurulumunuz aynı sayıları vermek zorunda.

---

## 0. Varsayımlar (yanlışsa söyleyin)

- Windows'taki `D:\jestech\ruhsat-bench` deposu duruyor ve son commit `e9c337f` civarı. ("Yerel repo yok" ile **Linux tarafında** henüz depo olmadığını kastettiğinizi varsayıyorum; Windows deposu kaybolduysa bu kılavuzun 1. bölümü çalışmaz — o durumda elimdeki devir zip'i + arşiv zip'lerinden depo yeniden kurulur, tarih damgaları kaybolur ve bu makalede açıkça beyan edilir. Bana bildirin, o yolu ayrıca yazarım.)
- Linux makinesi Ubuntu 22.04+ (24 önerilir), GPU'lu (Ollama için; RTX8000 taşınıyorsa sürücüler kurulacak).
- Uzak git sunucusu (GitHub vb.) kullanmak istemeyebilirsiniz; bu yüzden taşıma **git bundle** ile anlatılıyor — tek dosya, bütün geçmişi taşır.

---

## 1. Neden kopyala-yapıştır değil: beyan zinciri git geçmişinde yaşıyor

Bu projenin bilimsel iddialarından biri "her beyan koşudan önce, tarih damgalı".
O damgalar **commit geçmişinde**. Klasörü zip'leyip taşırsanız dosyalar gelir,
kanıt zinciri gelmez. Doğru araç `git bundle`: depo geçmişinin tamamını tek
dosyada taşır, Linux'ta ondan klonlanır, `git log` birebir aynı kalır.

### Windows tarafı (son PowerShell komutlarınız)

```powershell
cd D:\jestech\ruhsat-bench
git add -A
git commit -m "Linux gecisi oncesi son durum" --allow-empty
git bundle create "$env:USERPROFILE\Desktop\ruhsat-bench.bundle" --all
git bundle verify "$env:USERPROFILE\Desktop\ruhsat-bench.bundle"

# git'e girmemis buyuk/ikili veriler (PDF'ler, jsonl'ler git'teyse bu zip kuculur):
Compress-Archive -Path data\kaynak_pdf\*, sonuclar\*.jsonl, sonuclar\*.xlsx, data\iddialar\*.csv `
  -DestinationPath "$env:USERPROFILE\Desktop\ruhsat-bench_veri.zip" -Force
Get-FileHash "$env:USERPROFILE\Desktop\ruhsat-bench.bundle","$env:USERPROFILE\Desktop\ruhsat-bench_veri.zip" -Algorithm SHA256
```

İki dosyayı (bundle + veri zip'i) USB/scp ile Linux'a taşıyın; sha256'ları not alın.

---

## 2. Linux tarafı — sistem ve depo kurulumu

```bash
# 2.1 sistem paketleri
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip unzip

# 2.2 tasinan dosyalarin butunlugu
sha256sum ~/ruhsat-bench.bundle ~/ruhsat-bench_veri.zip   # Windows'taki degerlerle karsilastirin

# 2.3 depoyu bundle'dan klonla
mkdir -p ~/jestech && cd ~/jestech
git clone ~/ruhsat-bench.bundle ruhsat-bench
cd ruhsat-bench
git log --oneline | head -5        # e9c337f, c41494d, 1b360b1 ... gorunmeli

# 2.4 git'te olmayan verileri yerine koy
unzip -o ~/ruhsat-bench_veri.zip -d /tmp/veri
mkdir -p data/kaynak_pdf
cp /tmp/veri/*.pdf data/kaynak_pdf/ 2>/dev/null
cp /tmp/veri/*.jsonl /tmp/veri/*.xlsx sonuclar/ 2>/dev/null
cp /tmp/veri/*.csv data/iddialar/ 2>/dev/null
sha256sum data/kaynak_pdf/*.pdf    # data/korpus/belge_manifest.txt ile karsilastirilacak (adim 5)
```

### 2.5 Satır sonları — bir kerelik, etiketli commit

Windows çalışma kopyası CRLF taşıyor (commit'lerdeki `warning: LF will be
replaced by CRLF` bundandı). Linux'ta bir kez normalize edin:

```bash
git config core.autocrlf input
cat > .gitattributes << 'EOF'
* text=auto eol=lf
*.pdf  binary
*.xlsx binary
*.png  binary
EOF
git add --renormalize .
git commit -m "PORT: satir sonlari LF'e normalize edildi (Linux gecisi)"
```

**Bilinçli sınır:** bu commit metin dosyalarının bayt içeriğini değiştirir;
`kural_taban.py`'nin bastığı `betik_sha256` gibi geçmiş kayıtlardaki betik
hash'leri bu sınırın öncesine aittir. Zincir kırılmıyor — sınır git'te
etiketli ve makalede tek cümleyle beyan edilir: *"Depo 02.08.2026'da Linux'a
taşınmış, satır sonları normalize edilmiştir; betik hash'leri bu commit
öncesi/sonrası ayrı ailelerdir."*

### 2.6 Python ortamı

```bash
cd ~/jestech/ruhsat-bench
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt     # bu kilavuzla birlikte geliyor; surumler SABIT
pip freeze > sonuclar/pip_freeze_linux_$(date +%Y%m%d).txt
```

`requirements.txt` sürümleri doğrulamanın yapıldığı sürümlerdir — özellikle
**pypdf==5.9.0**. pypdf'i serbest bırakmayın: metin çıkarımı sürümle oynar
(ölçüldü: iki pypdf sürümü TBDY'de 4 karakter fark verdi; zararsızdı ama
ancak ölçüldüğü için biliyoruz).

```bash
cat > .gitignore << 'EOF'
.venv/
__pycache__/
*.pyc
.env
EOF
git add .gitignore && git commit -m "PORT: gitignore"
```

### 2.7 API anahtarı — asla dosyaya/sohbete değil

ORTAM.md §5'teki iki iptal vakasının Linux karşılığı:

```bash
# ~/.bashrc'ye DEGIL; her oturumda elle ya da ayri bir kaynak dosyadan:
export ANTHROPIC_API_KEY="sk-..."      # kosudan once, o kabukta
```

`f4_api_v2.py` anahtarı ortam değişkeninden okumuyorsa bu, Claude Code'a
verilecek küçük bir yamadır (HANDOVER görev listesine not düşüldü sayın).

---

## 3. Ollama ve yerel modeller

```bash
curl -fsSL https://ollama.com/install.sh | sh
sudo systemctl enable --now ollama
# GPU: nvidia surucusu kuruluysa ollama otomatik kullanir; dogrulama:
ollama run llama3.2:3b-instruct-q8_0 "merhaba" && nvidia-smi | head -15
```

**F5 planı için gereken asgari küme** (EK-4 model seçimi):

```bash
ollama pull qwen2.5:32b-instruct
ollama pull gemma3:27b
ollama pull llama3.2:3b-instruct-q8_0
```

Kapalı kitap tablosunu yeniden koşmak gerekmedikçe 18 modelin kalanını
çekmeyin (disk ve saat). Tam liste `arsiv` metrik CSV'sindeki model
sütunundadır.

Kural değişmiyor: betikler `http://127.0.0.1:11434`'e bağlanır,
`localhost` değil.

---

## 4. Komut çevirisi — değişen ve değişmeyen

| Windows (PowerShell 5.1) | Linux (bash) |
|---|---|
| `Move-Item a b -Force` | `mv -f a b` |
| `Compress-Archive -Path x -DestinationPath y` | `zip -r y x` |
| `Get-FileHash f -Algorithm SHA256` | `sha256sum f` |
| `foreach ($t in 1,2,3) { ... }` | `for t in 1 2 3; do ...; done` |
| `> dosya.txt 2>&1` | aynı |
| `python -u scripts\betik.py --arg` | `python3 -u scripts/betik.py --arg` |

**Değişmeyenler** (ORTAM.md'nin çekirdeği aynen geçerli):
- Tahmine değil ölçüme güven; her kontrol için pozitif kontrol.
- Beyan koşudan önce yazılır ve commit'lenir.
- Dosya IO `utf-8-sig` (Windows'a dönen xlsx/csv'ler için de güvenli).
- Betik başındaki stdout UTF-8 reconfigure **kalıyor** — Linux'ta zararsız,
  dosya Windows'a dönerse hayat kurtarır.
- Başarısız denemeler silinmez, arşivlenir.
- Kusur avı kapalı; yeni kusur → `kusur_kutugu.md`.

cp1252 borulama çökmesi Linux'ta yoktur; o sınıf dert biter. Türkçe dosya
adları (`kodlayıcı1_...xlsx`) ext4/UTF-8'de sorunsuzdur.

---

## 5. Kabul testi — 17/17 şart

```bash
cd ~/jestech/ruhsat-bench
# kodlayici xlsx'leri depo kokunde olmali (adim 2.4 kopyaladi)
bash scripts/dogrula_linux.sh
```

Betik bütün deterministik zinciri koşar ve **gömülü beklenen değerlerle**
karşılaştırır:

| adım | beklenen |
|---|---|
| korpus_kur | 1366 birim; Kontrol A 440/441, B 473/473, C 120/120 |
| bent_bol | 1523 birim; kurtarma 0.9632; 364 → 15.3.1 |
| kural_taban R3 | 473/473 |
| negatif kontrol (tohum 1–5) | 0.5137 · 0.5412 · 0.5201 · 0.5201 · 0.5349 |
| uzlasi_birlestir | v7a 223/250, v7b 221/252 |
| etki_analizi | ort 0.0046, maks 0.0347; Sonnet E1 0.697→0.692 |

Çıktının son satırı `SONUC: 17 tamam, 0 hata` olmalı. Değilse ortam farkı
vardır: `pip freeze`'i ve `/tmp/rb/*.log`'ları inceleyin, **makaleye tek sayı
geçmeden** kapatın. (Tohum değerleri deterministiktir; tutmamaları rastgelelik
değil, ortam farkı demektir.)

Geçince etiketleyin:

```bash
git add sonuclar/pip_freeze_linux_*.txt
git commit -m "PORT: Linux dogrulama 17/17 (dogrula_linux.sh)"
git tag linux-port-dogrulandi
```

---

## 6. HANDOVER eki — Claude Code artık Linux'ta

`HANDOVER.md` PowerShell 5.1 hedefiyle yazıldı. Claude Code'a HANDOVER ile
birlikte şu eki verin (ya da bu dosyayı okutun):

> **Ortam değişikliği:** Çalışma ortamı artık Linux/bash
> (`~/jestech/ruhsat-bench`, `.venv`). HANDOVER §3'teki "PowerShell 5.1
> kopyala-yapıştır blokları" kuralı "bash blokları" olarak okunur; betik
> docstring'lerindeki PowerShell örnekleri yeni betiklerde bash yazılır,
> eskilerde dokunulmaz. Diğer bütün kurallar (mühürlü dosyalar, beyan-önce-
> koşu, pozitif kontrol, utf-8-sig, 127.0.0.1, durma kuralı) aynen geçerli.
> İlk işin `bash scripts/dogrula_linux.sh` koşup 17/17 görmek; geçmiyorsa
> ortam farkını görevlerden ÖNCE çöz.

---

## 7. Taşınmayanlar / dikkat

- **Ollama model dosyaları** bundle'da değil; 3. bölümde yeniden çekiliyor.
  Modellerin Ollama sürümüyle bayt-birebir aynı olacağı garanti değildir —
  yerel koşular yeniden yapılacaksa bu, sonuç dosyalarına Ollama sürümünü
  yazarak beyan edilir (frontier'daki sürüm-kayması dersinin yerel karşılığı).
- **`frontCA32_bugun` hâlâ koşulmadı** ve API koşuları hangi makineden
  yapılırsa yapılsın aynı soruyu taşıyor; port bunu değiştirmez.
- Windows makinesini hemen silmeyin: 17/17 + etiket commit'i görülene kadar
  kaynak makine yedek sayılır.
