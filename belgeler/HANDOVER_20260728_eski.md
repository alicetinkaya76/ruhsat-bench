# RUHSAT-Bench — DEVİR NOTU (HANDOVER)

**Son güncelleme:** 28 Temmuz 2026
**Depo:** `D:\jestech\ruhsat-bench` (git, master)
**Durum:** Kod ve deney tarafı KAPALI. Kalan iş: uzlaşı (uzmanlarda) + yazım.

---

## 1. Proje nedir

Türk mühendislik mevzuatı üzerinde LLM'lerin **"bilmiyorum" diyebilme** yetisini
ölçen bir benchmark. Hedef dergi JESTECH (Q1).

Her iddia iki koşulda sorulur:

| koşul | seçenekler |
|---|---|
| **E1** | DOGRU / YANLIS / EMIN_DEGILIM (kaçınma serbest) |
| **E2** | DOGRU / YANLIS (zorunlu seçim) |

**Kaynak belgeler (6):** 3194 İmar Kanunu · 4708 Yapı Denetimi · 6331 İSG ·
İSG Risk Değerlendirmesi Yönetmeliği · Yapı Denetimi Uygulama Yönetmeliği ·
TBDY 2018

**Prob taksonomisi:**

| prob | ne test eder | altın | n |
|---|---|---|---|
| P1_dogrudan | doğrudan alıntı (verbatim / madde atıflı) | DOGRU | 163 |
| P2_sayisal | sayı takası | YANLIS | 37 |
| P3_anakronizm | kabul yılı / yürürlük | karışık | 19 |
| P4_uydurma | var olmayan belge | YANLIS | 13 |
| P5_capraz | yanlış madde (maddeshift) / yanlış belge (lawshuffle) | YANLIS | 121 |
| P6_guncellik | 2×2 dengeli: yil / yil_yanlis / degismedi / degismedi_dogru | 30 her biri | 120 |

**Nihai küme:** `data/iddialar/uretilen_iddialar_v6_onarilmis.csv` — **473 iddia**,
altın 230 DOGRU / 243 YANLIS.

---

## 2. Ana bulgular (hepsi commit'li dosyalardan)

### 2.1 Hiçbir açık ağırlıklı model şans üstünde değil
18 model × 2 koşul × 473 iddia = 17.028 çağrı. İkisi yanıt kapısını geçemedi
(etiket yerine iddiayı geri yazıyorlar). Kalan 16'da:

- dengeli doğruluk **0.48 – 0.64**
- Youden J **−0.04 – 0.28**
- λ = doğruluk(P1) + doğruluk(P5) − 1 → medyan **0.03**, en yüksek 0.21
- güven AUROC **0.46 – 0.54** (tamamen bilgisiz), ECE 0.21 – 0.44

### 2.2 Kaçınma var, seçicilik yok
Kaçınma oranları **%0 – %99** arasında savruluyor ve model ailesi/nicemleme ile
değişiyor, yetkinlikle değil. Kaçınılan maddelerdeki E2 doğruluğu ile taahhüt
edilen maddelerdekini karşılaştıran testte **hiçbir yerel model p<0.05'e
ulaşmıyor** (en büyük Δ = +0.12, p = 0.39).

### 2.3 Zorunlu seçim cevabı değiştiriyor
llama3.2:3b'nin üç nicemlemesi kararlarının **%72–80'ini** tersine çeviriyor ve
E2'de **%100 YANLIS** diyor. 36 hücrenin **8'i dejenere** (≥%90 tek etiket).
Doğruluk üzerinden McNemar bunu göremiyor: gemma3:12b'de P1 0.70→0.39 düşerken
P5 0.39→0.64 yükseliyor, toplam sabit, p = 0.49 — ama yanlılık tamamen dönmüş.

### 2.4 Ölçümün kararlılığı da bir yetenek eşiği
Prompt yeniden yazıldığında (varyant B), **kendi büyüklüğüne göre** savrulma:

| göreli savrulma | yerel (9 hücre) | claude-sonnet-5 (2 hücre) |
|---|---|---|
| yanlılık — P(DOGRU) | **1.76** | **0.03** |
| kaçınma oranı | 1.56 | 0.03 |
| taahhüt doğruluğu | 0.96 | 0.24 |
| λ | 0.92 | 0.34 |

**~59× fark.** Yerelde her ölçüt kendi büyüklüğü kadar veya daha fazla oynuyor.

> **DİKKAT — iki kez düzeltilmiş iddia.** Erken taslakta "P(DOGRU) 0.335 savruluyor,
> λ 0.044 → ×7.5, λ prompt-bağışık" yazılmıştı. **Yanlış.** ×7.5 mutlak ölçek
> yanılsaması; göreli olarak ×1.9. Ve yerelde λ = 0.048 ± 0.044, yani
> **sıfırdan ayırt edilemez** — "kararlı" değil, ölçülecek şey yok.
> Sonnet'te λ prompt değişince %25–33 düşüyor (0.33→0.25, 0.30→0.20).
> **λ hiçbir düzeyde prompt-bağışık değildir.** Doğru cümle:
> *her iki prompt altında da yerel modellerde bilgi sıfırdan ayırt edilemez;
> güçlü modelde nitel sonuç dayanıklı, etki büyüklüğü değil.*

### 2.5 Yetenek eşiği — süreksizlik, gradyan değil

| | yerel (16) | haiku-4.5 | sonnet-5 |
|---|---|---|---|
| λ (E1/E2) | medyan 0.03 | −0.018 / +0.067 | **+0.334 / +0.300** |
| dengeli doğruluk E1 | 0.48–0.64 | 0.53 | **0.70** |
| Youden J E1 | −0.04–0.28 | 0.07 | **0.39** |
| ECE E1 | 0.21–0.44 | 0.231 | **0.036** |
| kaçınma E1 | %0–99 | %27 | %38 |
| kaçınma seçici mi | hiçbiri | hayır (Δ+0.05, p=0.32) | **evet (Δ+0.16, p=0.0005)** |
| E1→E2 dönme | %13–80 | %15 | **%9** |
| dejenere hücre | 36'nın 8'i | 0 | 0 |

**Haiku kontrolü kritik:** aynı sağlayıcı, aynı API, aynı prompt, aynı protokol —
ama yerel modellerle aynı davranıyor. Sonnet farkı barındırma/aile/araç
kaynaklı değil, **yetenek** kaynaklı.

### 2.6 Hiçbir sistemin yapamadığı şey
P6 (bir maddenin hangi yıl değiştiği): **1B'den frontier'a kadar herkes 0.50**.
Sonnet bu alt ailenin **69 maddesinin tamamında kaçınıyor** — yapamadığını
biliyor. Komşu şablonda (`degismedi_dogru`) ise bilmediğini bilmiyor ve
51 maddenin hepsine tek etiket basıyor. Tek prob içinde iki başarısızlık kipi.

### 2.7 Uzman denetimi — iki geçiş, iki farklı sonuç

| | geçiş 1 (alıntıya karşı) | geçiş 2 (kaynak maddeye karşı) |
|---|---|---|
| κ (karar) | 1.000 | **0.722** |
| uyuşmazlık | 0/150 | 6/58, **hepsi tek yönde** (p=0.031) |
| bulunan hata | 0 (üst sınır %2.50) | **%6.7 [%1.6–11.8]** çerçeve içi |
| bileşik ağırlıkla | — | **%8.8** (bütün kümeye yansıtılmış) |
| kontrol yakalama | 8/8 mekanik tuzak | **1/2 gerçek altın hatası** |
| κ (kalite ekseni) | 0.860 [0.759, 0.961] | — |

**Üç aktarılabilir metodoloji bulgusu:**
1. Etiketin türetildiği alıntı üzerinden yapılan denetim **etiketi doğrulayamaz** —
   denetçi üretecin mantığını yeniden türetir, κ=1.00 ve sıfır bulgu verir.
2. **Oybirliği kuralı duyarlılığı öldürüyor.** "İki uzman da altından farklı"
   kuralı, bulunan tek gerçek altın hatasını atardı.
3. **Model konsensüsü etiket denetçisi olarak çalışmıyor** — kesinlik %4.5,
   şans tabanı %2.4.

---

## 3. Bir sonraki oturumda dikkat: asistanın tahmin sicili

Bu oturumda yapısal tahminlerin çoğu tutmadı. Sırayla:

| tahmin | sonuç |
|---|---|
| P6 kalıp sızıntısını modeller sömürüyordur | hayır, at-chance |
| `num_ctx` sabit maliyetin sebebidir | hayır, ×1.00 |
| `keep_alive` çözer | hayır |
| gemma her çağrıda yeniden yükleniyor | hayır, istemci tarafı IPv6 gecikmesi |
| frontier boş yanıtları `max_tokens` kesmesi | hayır, düşünme bütçesi |
| kararsızlık, güvenden iyi hata sinyalidir | hayır, güven kazandı (4 koşuda üst üste) |
| Haiku ara nokta olur | hayır, yerel modellerin yanına düştü (daha iyi bir sonuç) |
| λ prompt-bağışıktır | hayır, iki kez düzeltildi |

**Kural (kullanıcı koydu):** *tahminlere değil ölçüme güven; her yeni kontrol için
pozitif kontrol iste.* Bu oturumda işe yarayan her şey ölçümle çıktı.

---

## 4. Betikler ve ne ürettikleri

### F2 — üretim
| betik | çıktı |
|---|---|
| `uret_iddia_v3_6.py` | **MÜHÜRLÜ, ASLA YENİDEN ÇALIŞTIRILMAZ** (486 id konsensüs koşusuna bağlı) |

### F3 — altın etiket QA
| betik | çıktı |
|---|---|
| `temizle_v38.py` / `temizle_v39.py` | `uretilen_iddialar_v4_temiz.csv` (472) |
| `p6_denge_ek.py` | `..._v5_p6dengeli.csv` (473) |
| `kelime_onar.py` | `..._v6_onarilmis.csv` (473) **← NİHAİ** |
| `belge_guncellik.py` | `belge_guncellik.txt` |
| `kapsanma_kalibrasyon.py` | `kapsanma_kalibrasyon_temiz.txt` |
| `p6_kestirilebilirlik.py` | `p6_kestirilebilirlik.txt` |
| `denetim_kitabi.py` | kör uzman kitapları (geçiş 1) |
| `kitap_dogrula.py` | `kitap_dogrulama.txt` (şema-duyarlı, pozitif kontrollü) |
| `kappa_birlestir.py` | `kappa_raporu.txt` |
| `denetim_ikinci_gecis.py` | geçiş 2 kitapları + anahtar |
| `gecis2_birlestir.py` | `gecis2_raporu.txt`, `gecis2_uzlasi.csv` |
| `gecis2_uzlasi_isle.py` | **BEKLİYOR** — uzlaşı dolunca `gecis2_nihai.txt` |

### F4 — model matrisi
| betik | çıktı |
|---|---|
| `f4_kos.py` | `f4_sonuclar.jsonl` (yerel, A+B) |
| `f4_api.py` | `frontC_k*.jsonl`, `frontH_k*.jsonl`, `frontCB_k*.jsonl` |
| `f4_cok_kosu.py` | çoğunluk oyu + `kararsizlik_*.txt` |
| `f4_skor.py` | `f4_metrikler*.csv`, `f4_rapor*.txt` |
| `varyant_karsilastir.py` | `varyant_kararlilik*.csv/txt` |
| `makale_sayilari.py` | `makale_sayilari.txt` — **metindeki her sayıyı dosyalardan üretir** |

### Teşhis (tek seferlik, arşiv)
`ctx_testi.py` · `yuk_testi.py` · `api_teshis.py`

---

## 5. Beyan zinciri (OSF / şeffaflık)

| dosya | ne zaman yazıldı |
|---|---|
| `F4_on_kayit.txt` | koşudan ÖNCE |
| `F4_on_kayit_ek.txt` (EK-1) | koşu bitti, **hiçbir doğruluk metriği hesaplanmadan** önce |
| `F4_on_kayit_ek2.txt` (EK-2) | varyant B koşuldu, karşılaştırma yapılmadan önce |
| `F4_on_kayit_ek3.txt` (EK-3) | frontier koşuları geçersiz ilan edildi, yeniden koşudan önce |

**Makalede "preregistered" DEMEYİN.** Doğru ifade:
*"declared before analysis and timestamped in the repository"*. OSF'e yüklenecek
şey ön-kayıt değil, bu tarihli beyan zinciri + git logu.

### EK-1'in düzelttiği şey (önemli)
Ön-kayıt "maddelerin %80'inden azına **cevap verirse** puanlanmaz" diyordu.
"Cevap vermek" iki ayrı şeydi:
- **yanıt oranı** = ayrıştırılabilir çıktı → uyum ölçüsü, kapı olmalı
- **taahhüt oranı** = kaçınmama → **bağımlı değişken**, kapı OLAMAZ

Harfiyen uygulansaydı 13 hücre elenirdi ve çoğu *kaçındığı için*. Eşik yanıt
oranına taşındı; orijinal kural `[1.6]`'da duyarlılık analizi olarak duruyor.

### EK-3'ün geçersiz ilan ettiği koşular
`front_k1-3`, `frontB_k1-3`, `det1`, `det2` — claude-sonnet-5 genişletilmiş
düşünme kullanıyordu ve bütçenin tamamı düşünmeye gidiyordu. Bir madde ancak
model **az düşünerek** cevaplayabildiğinde puanlanıyordu → kayıp rastgele değil,
kolay maddelere yanlı. **Arşivde tutuluyor, sonuç olarak raporlanmıyor.**
Geçerli frontier kolu: `frontC_*` (düşünme kapalı, düşünme token'ı 0,
yanıt oranı 1.00).

---

## 6. Kalan iş

### 6.1 Uzmanlarda — uzlaşı (8 madde)
`sonuclar/gecis2_uzlasi.csv`. **Önce KURAL, sonra maddeler.**

Karar verilecek soru:
> *Kaynakta geçen ama koşulu düşürülmüş bir iddia DOĞRU mu YANLIŞ mı?*

İki uzman altı maddede tam olarak bu noktada ayrıştı ve altısı da aynı yönde
(işaret testi p = 0.031). Bu ölçüm hatası değil **tanım sorunu**; ortalamayla
kapatılamaz. Kural `KURAL_NOTU` sütununa yazılmadan `UZLASI` doldurulmamalı.

Dolduğunda:
```powershell
python scripts\gecis2_uzlasi_isle.py --dosyalar data\iddialar\gecis2_INS_MUH_doldurulmus.xlsx,data\iddialar\gecis2_ISG_UZM_doldurulmus_.xlsx
```
Çıkan iki sayı (çerçeve tahmini + bileşik) Bölüm 3.6'daki tek yer tutucuyu doldurur.

### 6.2 Yazım
| bölüm | durum |
|---|---|
| 3.6 uzman denetimi | **yazıldı** (`RUHSAT-Bench_3.6_uzman_denetimi.md`), 1 yer tutucu |
| 3.1–3.5 yöntem | taslak var (`RUHSAT-Bench_Methods_taslak.md`) |
| 4 bulgular | **yazıldı** (`RUHSAT-Bench_4_bulgular.md`) — **§4.5 revize edilmeli**, bkz. §2.4 uyarısı |
| 1 giriş | yok |
| 2 ilgili çalışmalar | yok — **kaynak taraması gerekiyor** |
| 5 tartışma + sınırlılıklar | yok |
| özet | yok |
| depo README | yok |

### 6.3 Koşulmayan, isteğe bağlı
- **Düşünme açık frontier kolu.** *"Bu görevde düşünmek ölçüye yansıyan katkı
  sağlıyor mu?"* Cömert bütçe gerekir (~1.4M çıktı token, en pahalı kalem).
  **Öneri: koşmayın.** Makale onsuz tam; sonraki çalışmaya bırakılır.
- 1500 iddiaya genişletme. **P3'ü kurtarmaz** — P3 belge sayısıyla ölçeklenir,
  iddia sayısıyla değil.

---

## 7. Makale bölünmesi önerisi (karar verilmedi)

Elimizde **iki ayrı makale** var:

**(a) Benchmark makalesi** → JESTECH. Kaçınma bulguları, yetenek eşiği,
zorunlu seçimin sinyal imal etmesi, ölçüm kararlılığı.

**(b) Metodoloji makalesi** → değerlendirme/veri kalitesi odaklı bir yer.
İki geçişli denetim, oybirliği kuralının duyarlılığı öldürmesi, model
konsensüsünün çalışmaması, kural kapsamının %50 veri kaybına yol açması,
çapraz-render kelime kırığı tespiti.

(b) şu an 3.6'ya sıkışmış durumda ve orada değerinin altında kalıyor.
Doçentlik için iki yayın da avantaj.
