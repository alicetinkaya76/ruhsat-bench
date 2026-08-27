# RUHSAT-Bench — oturum acilis durum ozeti
# Kullanim:  powershell -ExecutionPolicy Bypass -File scripts\durum_ozeti.ps1
# Ciktiyi komple kopyalayip sohbete yapistirin; yeni oturum boylece projeyi tanir.

$ErrorActionPreference = "SilentlyContinue"
$KOK = "D:\jestech\ruhsat-bench"
Set-Location $KOK

function Baslik($m) {
    Write-Host ""
    Write-Host ("=" * 78)
    Write-Host $m
    Write-Host ("=" * 78)
}

function Dosya($yol, $etiket) {
    $t = Join-Path $KOK $yol
    if (Test-Path $t) {
        $f = Get-Item $t
        $satir = ""
        if ($f.Extension -in ".csv", ".jsonl", ".txt", ".md", ".py", ".ps1") {
            $n = (Get-Content $t -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
            $satir = "{0,7} satir" -f $n
        }
        "{0,-46} {1,10:N0} B  {2,-14} {3}" -f $yol, $f.Length, $satir, $f.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
    }
    else {
        "{0,-46} {1,10}  {2}" -f $yol, "YOK", "<-- eksik"
    }
}

Baslik "RUHSAT-Bench DURUM OZETI"
Write-Host ("tarih      : " + (Get-Date).ToString("yyyy-MM-dd HH:mm"))
Write-Host ("kok klasor : " + $KOK)
Write-Host ("makine     : " + $env:COMPUTERNAME + "  /  kullanici: " + $env:USERNAME)

Baslik "1) ORTAM"
$py = & python --version 2>&1
Write-Host ("python (sistem) : " + $py)
if (Test-Path "$KOK\.venv\Scripts\python.exe") {
    $vpy = & "$KOK\.venv\Scripts\python.exe" --version 2>&1
    Write-Host ("python (venv)   : " + $vpy + "   [.venv VAR]")
    $paketler = & "$KOK\.venv\Scripts\python.exe" -m pip list 2>&1 |
        Select-String -Pattern "^(pypdf|openpyxl|matplotlib|requests|numpy|pandas)\s"
    foreach ($p in $paketler) { Write-Host ("   " + $p.ToString().Trim()) }
}
else {
    Write-Host "python (venv)   : .venv YOK  ->  python -m venv .venv"
}
$og = Get-Process ollama -ErrorAction SilentlyContinue
if ($og) { Write-Host ("ollama          : CALISIYOR (pid " + ($og[0].Id) + ")") }
else { Write-Host "ollama          : kapali  ->  ollama serve" }
Write-Host "kurulu modeller :"
$ml = & ollama list 2>&1 | Select-Object -Skip 1
if ($ml) { foreach ($m in $ml) { Write-Host ("   " + $m) } } else { Write-Host "   (ollama yanit vermedi)" }

Baslik "2) KAYNAK BELGELER  (data\kaynak_pdf)"
Dosya "data\kaynak_pdf\3194.pdf"     "imar"
Dosya "data\kaynak_pdf\4708.pdf"     "yapi denetimi"
Dosya "data\kaynak_pdf\6331.pdf"     "isg"
Dosya "data\kaynak_pdf\isg_risk.pdf" "risk yon."
Dosya "data\kaynak_pdf\yduy.pdf"     "yapi denetimi uyg."
Dosya "data\kaynak_pdf\20180318M1-2-1.pdf" "TBDY 2018"

Baslik "3) IDDIA SETLERI  (data\iddialar)"
Dosya "data\iddialar\uretilen_iddialar_v1.csv"
Dosya "data\iddialar\uretilen_iddialar_v2_temiz.csv"
if (Test-Path "$KOK\data\iddialar\uretilen_iddialar_v1.csv") {
    $r = Import-Csv "$KOK\data\iddialar\uretilen_iddialar_v1.csv" -Encoding UTF8
    Write-Host ""
    Write-Host ("  v1 iddia sayisi : " + $r.Count)
    Write-Host "  gold dagilimi   :"
    $r | Group-Object gold | Sort-Object Count -Descending |
        ForEach-Object { Write-Host ("     {0,-10} {1,5}" -f $_.Name, $_.Count) }
    Write-Host "  probe dagilimi  :"
    $r | Group-Object probe | Sort-Object Name |
        ForEach-Object { Write-Host ("     {0,-16} {1,5}" -f $_.Name, $_.Count) }
    Write-Host "  P5 alt-turleri  :"
    $ms = ($r | Where-Object { $_.uretim_sablonu -like "*P5_maddeshift*" }).Count
    $ls = ($r | Where-Object { $_.uretim_sablonu -like "*P5_lawshuffle*" }).Count
    $p2 = ($r | Where-Object { $_.uretim_sablonu -like "*P2_swap*" }).Count
    Write-Host ("     P5_maddeshift {0,5}" -f $ms)
    Write-Host ("     P5_lawshuffle {0,5}" -f $ls)
    Write-Host ("     P2_swap       {0,5}" -f $p2)
}

Baslik "4) BETIKLER  (scripts)"
foreach ($s in @(
    "uret_iddia_v3_6.py", "temizle_v37.py", "kaynak_dogrula.py", "kaynak_dogrula_v2.py",
    "kapsanma_kalibrasyon.py", "konsensus_uyari_v2.py", "konsensus_dogrulama.py",
    "ornek_denetim.py", "onay_dosyasi.py", "run_local.py", "score_local.py", "durum_ozeti.ps1")) {
    Dosya ("scripts\" + $s)
}

Baslik "5) SONUCLAR  (sonuclar)"
if (Test-Path "$KOK\sonuclar") {
    Get-ChildItem "$KOK\sonuclar" -File | Sort-Object LastWriteTime |
        ForEach-Object {
            "{0,-40} {1,10:N0} B  {2}" -f $_.Name, $_.Length, $_.LastWriteTime.ToString("yyyy-MM-dd HH:mm")
        }
}
else { Write-Host "sonuclar\ klasoru YOK" }

Baslik "6) YAPILMIS BUYUK KOSULAR"
$kontroller = @(
    @("sonuclar\yerel_sonuclar.jsonl", "F1 pilot: 18 yerel model x 2 kosul"),
    @("sonuclar\konsensus.jsonl", "F3a: 5 model x 2 kosul x 486 iddia konsensus"),
    @("sonuclar\konsensus_dogrulama.txt", "F3a: yanlilik simulasyonu"),
    @("sonuclar\kaynak_dogrulama_v2.txt", "F3b: koken + kazara-dogruluk denetimi"),
    @("sonuclar\kapsanma_kalibrasyon.txt", "F3c: [C2] pozitif kontrol"),
    @("sonuclar\temizlik_raporu.txt", "F3c: cerrahi temizlik"),
    @("data\iddialar\onay_turu_v2_uyarili.xlsx", "F3: uzman calisma kitabi v2")
)
foreach ($k in $kontroller) {
    if (Test-Path (Join-Path $KOK $k[0])) { Write-Host ("  [X] " + $k[1]) }
    else { Write-Host ("  [ ] " + $k[1] + "   (" + $k[0] + " yok)") }
}

Baslik "7) GIT"
& git -C $KOK log --oneline -n 8 2>&1
Write-Host ""
& git -C $KOK status --short 2>&1

Baslik "8) SIRADAKI ADIMLAR (HANDOVER.md bolum 8)"
Write-Host "  1. python scripts\kapsanma_kalibrasyon.py --ayrinti      ([C2] pozitif kontrol)"
Write-Host "  2. python scripts\temizle_v37.py --kuru                  (once kuru kosu)"
Write-Host "  3. python scripts\temizle_v37.py                         (onaydan sonra)"
Write-Host "  4. uzman calisma kitabi (150 satir) + 2 uzman + kappa"
Write-Host "  5. F4 tam model matrisi (P5 alt-tur ayrimiyla)"
Write-Host ""
Write-Host "Bu ciktinin TAMAMINI kopyalayip yeni oturuma yapistirin."
Write-Host ("=" * 78)
