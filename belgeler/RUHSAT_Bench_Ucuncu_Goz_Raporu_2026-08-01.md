# RUHSAT-Bench — Üçüncü-Göz İstatistik, İddia ve Dergi Uygunluğu Denetimi

**Denetim tarihi:** 1 August 2026  
**İnceleme biçimi:** source-code-and-raw-output audit; adversarial peer review  
**Karar:** **Gönderime hazır değil — major reanalysis required.**  
**Önerilen editoryal karşılık:** Makale bugün gönderilirse, özellikle §4.5, §4.7 ve uzman denetimi nedeniyle *major revision* değil, **reject-and-resubmit / substantial reanalysis** riski taşır.

---

## Yönetici özeti

Çalışmanın çekirdeği değerlidir: Türk mühendislik mevzuatına dayalı 473 maddelik, kaçınmalı ve zorunlu-seçimli çift koşullu bir benchmark; açık ağırlıklı modeller, iki barındırılan model ve iki geçişli uzman denetimi aynı deney çatısı altında birleştirilmiştir. Ham deney materyali büyük ölçüde korunmuş, yerel koşular tekrar üretilebilir ve devir notu önceki yanlış yorumları açıkça kaydetmiştir. Buna rağmen mevcut bulgular metni, **üç ayrı P0 düzeyindeki engel** nedeniyle yayımlanabilir değildir:

1. **Barındırılan varyant-B koşusu uygulamada B istemini kullanmamış görünüyor.** Arşivdeki `f4_api.py`, `--varyant B` değerini çıktıya yazıyor fakat sistem istemini her zaman A’dan seçiyor. Bu, Sonnet’in A–B istem kararlılığına, yerel–Sonnet “~59×” karşılaştırmasına ve §4.5’in hosted kısmına doğrudan zarar verir.
2. **P6 için raporlanan ölçüt, betikte tarif edilen dengeli doğruluk değildir.** `f4_skor.py` prob düzeyinde `d_/n_` ile düz doğruluk basıyor. Ham veriden doğru BAcc yeniden hesaplandığında yerel hücreler 0.380–0.570 arasında değişiyor; “bütün sistemler 0.50” ve “tek etiket” anlatısı veriden çıkmıyor.
3. **İkinci uzman geçişi sonuçlanmamıştır.** Sekiz uzlaşı satırının karar ve kural alanları boştur. Bu nedenle %6.7 ve %8.8 şu anda nihai altın-etiket hata oranları değil, lenient rule altında **pre-adjudication candidate contextual-defect estimates**’tir. Üstelik iki pozitif kontrolden yalnız biri gerçek bir etiket hatasıdır.

Bunlara ek olarak; kaynak-alıntı kümelenmesini yok sayan bağımsızlık varsayımı, kapsamı çok farklı E1 hücrelerinin doğrudan karşılaştırılması, yalnız McNemar testine uygulanan eksik çoklu-karşılaştırma düzeltmesi, E2’yi E1 kaçınmasının “gizli cevabı” gibi kullanan seçicilik testi ve tek güçlü hosted modelden çıkarılan “yetenek eşiği” nedenselliği ana sonuçları olduğundan güçlü gösteriyor.

**Kurtarılabilirlik kararı:** Çalışma kurtarılabilir ve doğru yeniden analizle güçlü olabilir. Sorun benchmark fikrinde değil; uygulama doğrulaması, estimand tanımı, istatistiksel bağımlılık ve iddia dilindedir. Aşağıdaki P0 adımları tamamlanmadan makale gönderilmemelidir.

### Gönderimi bloke eden işler

| Öncelik | Yapılacak iş | Neden zorunlu | Tamamlanma ölçütü |
|---|---|---|---|
| P0-1 | `f4_api.py` varyant yönlendirmesini düzelt; Sonnet-B’yi 3 kez yeniden koş; çoğunluk oyu üret | Hosted istem-kararlılığı şu anda uygulama-geçersiz | A ve B sistem istemlerinin hash’leri farklı; JSONL satırlarında prompt hash/variant doğrulanmış; üç koşu arşivli |
| P0-2 | Sekiz uzman maddesi için önce karar kuralını sabitle, sonra uzlaşıyı doldur | %6.7/%8.8 nihai değildir | `KURAL_NOTU` önceden sabitlenmiş; sekiz `UZLASI` dolu; v7 veri kümesi + changelog + hash |
| P0-3 | Etiket değiştiyse bütün skorları yeniden üret; değişmediyse etiket-duyarlılık analizi ver | Nihai altın set ile raporlanan sonuç aynı sürüm olmalı | Makale tabloları yalnız v7/hash’e dayanıyor |
| P0-4 | P6, standart ECE ve hücre paydalarını düzelt | Mevcut §4.7 ve bazı §4.6 cümleleri yanlış | Prob düzeyinde BAcc; standard ECE; 8/28 veya 8/32 doğru payda |
| P0-5 | Kaynak-alıntı kümeli çıkarım ve kapsam-duyarlı seçmeli tahmin analizi yap | 344/473 madde tekrar eden kaynak kümelerine bağlı; E1 kapsamları %0–99 | Cluster bootstrap/GEE; risk–coverage/AUGRC; ortak-kapsam veya standardised-coverage sonuçları |
| P0-6 | Bulgular başlıklarını ve nedensel dili yeniden yaz | “none above chance,” “threshold,” “prompt-immune,” “universal P6 failure” desteklenmiyor | Aşağıdaki replacement text ile uyumlu, önceden tanımlı–post hoc ayrımı açık |

---

# 1. İstatistik denetimi

## 1.1 Denetimin kapsamı ve estimand ayrımı

Bu denetim üç düzeyi birbirinden ayırır:

- **Arşiv doğrulaması:** mevcut betiğin gerçekten ne yaptığı ve raporlanan sayının ham çıktıdan çıkıp çıkmadığı.
- **Yeniden hesaplama:** aynı ham sonuçlardan, metinde tarif edilen metriğin doğru uygulanması.
- **Post hoc sağlamlık analizi:** makalede önceden tanımlanmamış fakat hakemin isteyeceği cluster-robust testler. Bunlar mevcut “confirmatory” sonuçların yerine sessizce geçirilemez; açıkça audit-driven/post hoc diye etiketlenmelidir.

Temel veri yapısı bağımsız 473 Bernoulli gözlem değildir. `kaynak_alinti` alanında **277 benzersiz kaynak izi** vardır; küme büyüklükleri {1:129, 2:112, 3:31, 4:3, 5:1, 10:1}’dir. **344 madde**, en az bir başka maddeyle aynı kaynak izini paylaşır. P1, P2 ve P5’in aynı kaynak izinden birlikte üretildiği 28 küme vardır. Dolayısıyla “benchmark maddeleri sabit bir finite population” estimandı ile “benzer mevzuat pasajlarına genellenebilir model performansı” estimandı ayrı raporlanmalıdır.

## 1.2 P0 — Hosted varyant-B yönlendirme hatası

### Arşiv kanıtı

`archive/scripts/f4_api.py` içinde:

- satır 58–68 yalnız A istemlerini (`E1_SISTEM`, `E2_SISTEM`) tanımlar;
- satır 153 `--varyant` parametresini kabul eder;
- satır 230 koşula göre daima A istemlerinden birini seçer;
- satır 262 ise verilen varyant harfini JSONL’ye kaydeder.

Böylece dosya adı veya JSONL alanı B olsa bile gönderilen istem A’dır. Yerel betik `f4_kos.py` ise satır 54–71’de B istemlerini tanımlar ve `PROMPT` haritası kullanır. Arşivde hosted koşu için başka bir runner veya istek gövdesi kanıtı bulunmadığı sürece **`frontCB_*` koşuları varyant-B olarak kabul edilemez.**

### Hakem raporuna yazacağım cümle

> The hosted prompt-robustness result is not auditable under the archived implementation. The API runner records the requested variant label but always routes the variant-A system prompt. Consequently, the Sonnet A–B comparison and the reported local-versus-hosted stability ratio are invalid unless the authors provide a distinct, hashed runner or rerun the hosted B arm.

### Zorunlu düzeltme ve pozitif kontrol

1. `f4_kos.py`deki B istemlerini API runner’a aynen taşıyın.
2. `PROMPT = {"A": ..., "B": ...}` haritasından `PROMPT[a.varyant][kosul]` seçin.
3. Her satıra en az `system_prompt_sha256`, `user_template_sha256`, `runner_git_commit`, `api_model_snapshot` alanlarını yazın.
4. Koşudan önce pozitif kontrol: A ve B hash’lerinin farklı, aynı varyant içindeki üç koşunun hash’lerinin aynı olduğunu assert edin.
5. Yalnız **Sonnet-B üç koşusunu** yeniden koşmak yeterlidir; geçerli A koşusu korunabilir. Haiku-B ancak hosted model düzeyinde kararlılık karşılaştırması yapılacaksa gerekir.

## 1.3 P0 — P6 scorer hatası ve §4.7’nin çökmesi

Metin P3/P6 için dengeli doğruluk gerektirdiğini söyler. Buna karşın `f4_skor.py` prob özetinde her prob için doğru sayısını toplam commit sayısına bölerek **ordinary accuracy** basar. Tek sınıflı P1/P2/P4/P5 tabakalarında ordinary accuracy zaten sınıf yanlılığıyla karışır; iki sınıflı P6’da ise bu uygulama doğrudan yanlış metrik üretir.

Ham JSONL’den yeniden hesaplama:

- 32 response-valid yerel hücrede P6 BAcc aralığı: **0.3798–0.5696**;
- ≥%90 tek etiket üreten hücre: **15/32**, tümü değil;
- Sonnet E1’de yıl-spesifik iki alt ailedeki **60/60** maddeden kaçınır; toplam 69 kaçınmanın diğer 9’u `degismedi`/`degismedi_dogru` alt ailelerindendir;
- Sonnet E1’de 51 commitment’ın tümü `YANLIS`tır: 28 doğru negatif ve 23 yanlış negatif;
- Sonnet E2 P6 BAcc: **0.5083**;
- Haiku E1 P6 BAcc: **0.4319** (38 commitment), E2: **0.4750**.

Seçilmiş yerel hücreler:

| Model                       | Condition   |   Committed n |   Coverage |   P6 BAcc |   P(TRUE) |   Largest-label share |
|:----------------------------|:------------|--------------:|-----------:|----------:|----------:|----------------------:|
| gemma3:4b                   | E2          |           119 |     0.9917 |    0.3798 |    0.6975 |                0.6975 |
| qwen2.5:7b-instruct-q5_K_M  | E2          |           116 |     0.9667 |    0.3870 |    0.5517 |                0.5517 |
| qwen2.5:7b-instruct-q8_0    | E2          |           106 |     0.8833 |    0.4067 |    0.5566 |                0.5566 |
| gemma3:4b                   | E1          |           120 |     1.0000 |    0.4167 |    0.7333 |                0.7333 |
| qwen2.5:7b-instruct-fp16    | E2          |           116 |     0.9667 |    0.4224 |    0.5776 |                0.5776 |
| llama3.2:3b-instruct-q8_0   | E1          |            75 |     0.6250 |    0.5696 |    0.4533 |                0.5467 |
| llama3.2:3b-instruct-q5_K_M | E1          |            99 |     0.8250 |    0.5449 |    0.5556 |                0.5556 |
| llama3.2:3b-instruct-fp16   | E1          |            75 |     0.6250 |    0.5427 |    0.4533 |                0.5467 |
| qwen2.5:3b-instruct-q4_K_M  | E2          |           120 |     1.0000 |    0.5083 |    0.0250 |                0.9750 |
| qwen2.5:3b-instruct-q5_K_M  | E2          |           120 |     1.0000 |    0.5083 |    0.0083 |                0.9917 |

### Hakem raporuna yazacağım cümle

> Section 4.7 is not supported by the scoring implementation. The script describes balanced accuracy for P6 but reports ordinary accuracy in the per-probe table. Correct recomputation yields local P6 balanced accuracy between 0.380 and 0.570, with only 15 of 32 response-valid cells showing ≥90% single-label commitment. The universal “all systems at 0.50” claim must be withdrawn.

### Doğru yorum

P6 tek bir evrensel başarısızlık kipi göstermiyor. Daha savunulabilir sonuç şudur: **P6 bütün model sınıfları için zordur; fakat modeller bu zorluğu farklı biçimlerde gösterir: kaçınma, tek-etiket çökmesi veya zayıf iki-sınıf ayrımı.** Sonnet’in 60 yıl-spesifik maddede kaçınması güçlü bir örnektir; bunu “69 such items” diye genellemek yanlıştır.

## 1.4 “Hiçbir açık ağırlıklı model şans üstünde değil” iddiası yanlış

Mevcut metin BAcc aralıklarını sunuyor fakat BAcc/J/λ için formal null testleri üretmiyor. Betikte Bonferroni yalnız E1–E2 McNemar ailesine uygulanmıştır. Bu nedenle “none above chance” ya bir betimsel iddia olarak BAcc≈.50 ile sınırlanmalı ya da gerçekten test edilmelidir.

Post hoc audit olarak, her metric-eligible hücrede `prediction ~ gold` binomial GLM kuruldu ve standart hatalar `kaynak_alinti` ile kümelendi. 28 hücrelik aileye karşı tek yönlü Bonferroni uygulandığında dört hücrede pozitif ilişki kaldı:

| Model                | Condition   |   Committed n |   Source clusters |   BAcc |   Cluster-robust one-sided p |   Bonferroni-adjusted p |
|:---------------------|:------------|--------------:|------------------:|-------:|-----------------------------:|------------------------:|
| qwen2.5:32b-instruct | E2          |           473 |               277 | 0.5477 |                       0.0002 |                  0.0049 |
| gemma3:27b           | E1          |           459 |               269 | 0.5729 |                       0.0004 |                  0.0119 |
| qwen2.5:32b-instruct | E1          |            82 |                53 | 0.6423 |                       0.0007 |                  0.0190 |
| gemma3:12b           | E1          |           467 |               275 | 0.5562 |                       0.0011 |                  0.0295 |

Bu test BAcc için birebir bir parametrik test değildir; sınıf ile tahmin arasındaki pozitif ilişkiyi test eder. Yine de kategorik “hiçbiri” cümlesini kesin biçimde çürütür. Ayrıca cluster bootstrap örnekleri şunları verdi:

- `gemma3:27b E1`: BAcc 0.5729, cluster-bootstrap 95% CI [0.5302, 0.6166];
- `qwen2.5:32b E1`: BAcc 0.6423, [0.5625, 0.7182], ancak coverage yalnız 0.173;
- `gemma3:12b E1`: BAcc 0.5562, [0.5211, 0.5914];
- `qwen2.5:32b E2`: BAcc 0.5477, [0.5230, 0.5726].

### Hakem kararı

**Reddedilecek başlık:** “No open-weight model performs above chance.”  
**Kabul edilebilir başlık:** “Local discrimination is weak, modest, and inconsistent.”

E1 sonuçları modelin seçtiği maddelere koşulludur; özellikle Qwen-32B’nin .642 BAcc’si %17.3 kapsamda olduğundan Sonnet’in .70 BAcc / %62 kapsamıyla doğrudan yarıştırılamaz. E2 full-coverage daha temiz karşılaştırmadır: Sonnet yaklaşık .631, en yüksek yerel hücre yaklaşık .548’dir.

## 1.5 λ: sıfıra yakın ortalama, fakat “ölçülemez” ve “prompt-bağışık” değil

28 metric-eligible yerel hücrede λ dağılımı:

- mean 0.0471;
- median 0.0361;
- IQR 0.0213–0.0719;
- minimum −0.0312;
- maximum 0.2057.

Bu, çoğu hücrede ayrımın küçük olduğunu destekler. Fakat `kaynak_alinti` kümeli post hoc ilişki testinde iki hücre Bonferroni-28 sonrasında kaldı:

| Model                | Condition   |   P1+P5 n |   Source clusters |      λ |   Cluster-robust one-sided p |   Bonferroni-adjusted p |
|:---------------------|:------------|----------:|------------------:|-------:|-----------------------------:|------------------------:|
| gemma3:27b           | E1          |       280 |               162 | 0.1375 |                       0.0001 |                  0.0016 |
| qwen2.5:32b-instruct | E2          |       284 |               163 | 0.1020 |                       0.0015 |                  0.0412 |

Dolayısıyla “yerel modellerde λ hiçbir yerde sıfırdan ayırt edilemez” iddiası desteklenmez. Daha da önemlisi, yerel prompt değişiminde göreli değişimler P(TRUE)=1.76, kaçınma=1.56, committed accuracy=0.96 ve **λ=0.92**’dir. Küçük mutlak λ farkı, metrik seviyesinin sıfıra yakın olmasından kaynaklanır; prompt invariance değildir.

### Hakem raporuna yazacağım cümle

> The manuscript correctly retracts the earlier 7.5× absolute-scale comparison, but it still understates λ instability. Relative to its own small magnitude, λ changes almost as much as committed accuracy across the two local prompts. Moreover, two model–condition cells retain positive P1/P5 discrimination after source-clustered, family-wise correction in a post hoc audit. The defensible claim is that most local λ estimates are small and unstable, not that λ is universally null or prompt-invariant.

## 1.6 Çoklu karşılaştırma planı eksik uygulanmış

Tarih damgalı beyan zinciri doğrulayıcı olarak dört aileyi sayıyor: coverage difference, matched accuracy, BAcc/J ve λ. Arşiv scorer’ı yalnız matched accuracy için McNemar p-değeri üretip model sayısına göre Bonferroni uyguluyor. Coverage farkı, BAcc/J ve λ için p-değeri/CI/ailesel düzeltme yoktur.

Bu nedenle makalede şu üç seçenekten biri açıkça seçilmelidir:

1. **Confirmatory yeniden analiz:** dört ayrı hipotez ailesi, her birinin test istatistiği, yönü, aile büyüklüğü ve düzeltmesi önceden tanımlanır; veya
2. **Betimsel raporlama:** BAcc/J/λ için formal üstünlük dili bırakılır, cluster-bootstrap CI verilir; veya
3. **Hiyerarşik model:** model ailesi/temel ağırlık için partial pooling ve az sayıda önceden tanımlı kontrast.

Selectivity p=.0005 ve prompt-variant analizleri mevcut belgelerde exploratory’dir. Sonnet için küçük p-değeri etkileyicidir fakat “confirmatory” diye sunulmamalıdır.

## 1.7 Kaynak kümelenmesi ve pseudoreplication

Aynı kaynak pasajından doğrudan doğru, sayı takaslı ve çapraz-atıf maddeleri üretildiğinde hata yapıları korelasyonludur. Fisher, binomial Wilson ve klasik McNemar’ın item-independent kullanımı standart hataları daraltabilir. Bu yalnız teknik bir ayrıntı değildir; P1/P5 ayrımının tam amacı aynı kaynakta yanıt yanlılığından ayrım ölçmektir.

### İstenen analiz

- Birincil: `kaynak_alinti` cluster bootstrap ile BAcc, J, λ, coverage ve E1–E2 paired difference CI.
- Alternatif/ek: GEE veya random-intercept mixed model (`prediction ~ gold * condition`, cluster=source excerpt).
- P1/P5 için source-matched contrast: aynı kaynak kümesi içindeki P1 ve P5 tahmin farkı.
- Benchmark-sabit estimand için item-level descriptives ayrıca korunabilir; fakat “başka mevzuat pasajlarına genellenme” çıkarımı cluster-aware olmalıdır.

## 1.8 Kaçınma seçiciliği testi kavramsal olarak kirlenmiş

§4.3, E1’de kaçınılan maddeler ile taahhüt edilen maddelerin E2 doğruluğunu karşılaştırıyor. Fakat §4.4 aynı zamanda zorunlu seçimin bazı modellerde kararların %72–80’ini değiştirdiğini gösteriyor. Bu durumda E2 cevabı, E1 altında gözlenmeyen “latent forced guess” değildir; ayrı bir **treatment condition**’dır.

Mevcut testin söylediği şey:

> “E1 abstention status partitions items on which the model later performs differently under the E2 intervention.”

Söyleyemediği şey:

> “The model’s abstention is/is not epistemically selective with respect to the answer it would otherwise have given.”

### En iyi çözüm

Aynı çağrıda modelden `(binary_guess, abstain_flag, confidence)` alın veya sabit bir base predictor üzerine bağımsız rejector kurun. Böylece commitment/abstention, binary prediction’ı değiştirmeden değerlendirilir. Risk–coverage eğrileri, selective risk, AUGRC ve coverage-matched risk raporlanır. Mevcut E1/E2 karşılaştırması exploratory kalabilir ve reversal rate ile birlikte yorumlanmalıdır. Sonnet’in %9 dönüş oranı yorumu daha makul kılar, fakat nedensel tanımlama sağlamaz.

## 1.9 Kapsam farkları nedeniyle E1 BAcc karşılaştırması elma–armut

E1 BAcc, her modelin kendisinin seçtiği commitment alt kümesinde hesaplanır. Coverage %0–99 arasında değiştiği için yüksek BAcc düşük kapsamla satın alınabilir. Qwen-32B’nin .642 BAcc / .173 coverage sonucu bunun tipik örneğidir.

Asgari raporlama:

- risk–coverage curve;
- AUGRC veya AURC ile birlikte explicit metric convention;
- %20, %40, %60 gibi ortak coverage çalışma noktalarında risk;
- E2 full-coverage BAcc/J;
- E1 committed BAcc yalnız “conditional performance” olarak.

Bu yapılmadan “Sonnet–local gap” tek sayı ile verilmemelidir.

## 1.10 Kalibrasyon karşılaştırması tam eşdeğer değil

Üç ayrı sorun vardır:

1. Archived ECE bin başına ortalama güven yerine bin midpoint kullanıyor; bu standard ECE değildir.
2. Hosted çoğunluk-oyunda güven, yalnız çoğunluk etiketini veren koşuların medyanıdır; yerelde tek koşu güvenidir.
3. E1 ECE yalnız commitment’larda ve çok farklı coverage düzeylerinde hesaplanır.

Yeniden hesaplanan hosted değerler:

| Arm    | Model                     | Condition   |   n |   Archived midpoint ECE |   Standard ECE |   Mean confidence |   Accuracy |
|:-------|:--------------------------|:------------|----:|------------------------:|---------------:|------------------:|-----------:|
| haiku  | claude-haiku-4-5-20251001 | E1          | 336 |                  0.2310 |         0.2233 |            0.7524 |     0.5327 |
| haiku  | claude-haiku-4-5-20251001 | E2          | 472 |                  0.2106 |         0.2049 |            0.7621 |     0.5572 |
| sonnet | claude-sonnet-5           | E1          | 291 |                  0.0359 |         0.0388 |            0.7146 |     0.6976 |
| sonnet | claude-sonnet-5           | E2          | 473 |                  0.0714 |         0.0571 |            0.6912 |     0.6364 |

Sonnet’in Haiku ve yerellere göre belirgin kalibrasyon üstünlüğü genel olarak korunuyor; fakat sayı ve karşılaştırma tanımı değişiyor. Final analizde şunlar verilmelidir:

- per-run calibration;
- majority-vote ensemble için vote share ve/veya tüm üç run confidence aggregation;
- standard ECE + Brier score + reliability diagram;
- E2 full-coverage ana kalibrasyon karşılaştırması;
- E1’de coverage ve confidence availability ile birlikte conditional ECE.

## 1.11 Sıfır olay üst sınırları yanlış adlandırılmış

Arşivde 0/150 için 2.50%, 0/58 için 6.2% raporlanıyor. Bunlar z=1.96 ile elde edilen **iki yönlü %95 Wilson aralığının üst uçlarıdır**, “%95 one-sided” değildir.

- n=150: two-sided 95% Wilson upper 2.497%; one-sided 95% Wilson 1.772%; exact one-sided Clopper–Pearson 1.977%.
- n=58: two-sided 95% Wilson upper 6.212%; one-sided 95% Wilson 4.457%; exact one-sided Clopper–Pearson 5.034%.

İki doğru seçenek vardır: mevcut sayıları koruyup “upper endpoint of a two-sided 95% Wilson interval” deyin veya gerçekten one-sided üst sınırı yeniden hesaplayın. Ayrıca 150 maddelik örnekleme tabakalı olduğundan pooled unweighted bound, tüm set için tasarım-ağırlıklı bir üst sınır değildir.

## 1.12 Uzman geçişi: %6.7 ve %8.8 henüz sonuç değil

`sonuclar/gecis2_uzlasi.csv` içindeki sekiz satırın `UZLASI` ve `KURAL_NOTU` alanları boştur. Altı event’ın tamamı iki uzmanın anlaşamadığı satırlardır; dolayısıyla bunlar “found gold errors” değil, **candidate contextual defects**’tir.

Şu anda kabul edilebilir ifade:

> Before adjudication, applying the lenient rule (at least one rater differs from gold) produced a design-weighted candidate-flag estimate of 6.7% in the 138-item frame and an 8.8% two-stage projection to the full claim set. Because all six events are unresolved inter-rater disagreements, these values are not final label-error estimates.

Uzlaşıdan sonra:

- karar kuralının maddeler görülmeden önce kaydedildiğini kanıtlayın;
- her satır için final label / item-quality defect / out-of-frame distinction yapın;
- veri setini v7 olarak mühürleyin;
- hangi maddelerin değiştiğini changelog’da verin;
- ana model sonuçlarını v7 ile yeniden skorlayın veya “labels as originally released / labels after adjudication” sensitivity tablosu verin.

## 1.13 Pozitif kontrol mantığı geçersiz

İkinci geçişte iki seeded item aynı türden değildir:

- ID 291: gerçek gold-label error; mevcut gold `DOGRU`, doğru sonuç `YANLIS`.
- ID 378: gold zaten `YANLIS` ve uzmanlar da `YANLIS` demiştir; sorun atfın 2960→1480 bozulmasıdır. Bu bir **item-quality/manipulation defect**, gold-label-error control değildir.

Dolayısıyla “one of two real gold errors detected” ve bunun üzerinden lenient rule’un empirically üstün olduğunu söylemek yanlıştır. Etiket hatası duyarlılığı için geçerli pozitif kontrol n=1’dir; n=1 iki karar kuralını ampirik olarak seçemez. Lenient/strict karar, benchmarkın hedef tanımına ve hata maliyetlerine dayanarak önceden sabitlenmeli; pozitif kontroller türlerine göre ayrı raporlanmalıdır.

## 1.14 Dejenere hücre paydası yanlış

- Toplam tasarım hücresi: 36;
- response-valid hücre: 32;
- metric-eligible (n commitment ≥30) hücre: 28;
- dejenere hücre: 8.

“8 of 36” teknik olarak tüm tasarımın paydasıdır fakat iki başarısız model ve dört küçük-n hücresini karıştırır. Davranışsal sonuç için **8/28 metric-eligible**; uyum kapısından geçen bütün hücreler için **8/32 response-valid** raporlanmalıdır. Her iki paydayı verip tanımı açıkça yazmak en iyisidir.

## 1.15 Tek-sınıflı tabakalarda “accuracy” model bilgisini ölçmez

P1 tümü `DOGRU`, P2/P4/P5 tümü `YANLIS`tır. Bu tabakalarda accuracy, modelin sınıf eğilimi ile madde bilgisini ayıramaz. λ’nın P1/P5 karşıtlığı bu sorunu kısmen çözmek için iyi bir fikirdir; fakat prob tablolarında P1 accuracy veya P5 accuracy tek başına “knowledge” diye okunmamalıdır.

Önerilen raporlama:

- tek-sınıflı prob için `P(DOGRU)`/commitment label share;
- P1 vs P5 source-matched discrimination;
- iki-sınıflı P3/P6 için BAcc/J;
- tüm set için BAcc/J ve kaynak-kümeli CI.

## 1.16 Model sayısı bağımsız replikasyon sayısı değildir

16 geçerli yerel “model” içinde aynı temel ağırlıkların q4, q5, q8 ve fp16 nicemlemeleri vardır. Bunlar 16 bağımsız model ailesi değildir. Model-name-derived seed ve madde sırası nicemleme karşılaştırmasını da potansiyel olarak seed/order ile karıştırır.

Raporlama düzeyi:

- base checkpoint / family düzeyinde ana özet;
- quantization varyantları nested sensitivity analysis;
- quantization karşılaştırması için aynı seed ve aynı item order;
- “median over 16 models” ifadesi kullanılırsa bağımsız replikasyon olmadığını söyleyin.

## 1.17 Frontier “yetenek eşiği” süreksizliği kanıtlanmış değildir

Haiku aynı sağlayıcı, API biçimi ve majority-vote protokolü için değerli bir kontroldür. Fakat Sonnet–Haiku karşılaştırması şunları kontrol etmez:

- mimari ve eğitim reçetesi;
- eğitim verisinde Türkçe mevzuat maruziyeti;
- model güncelliği ve olası benchmark contamination;
- alignment/abstention policy;
- kapasiteyi temsil eden bağımsız, sürekli bir ölçü.

Tek güçlü hosted model ile “discontinuity, not gradient” nedensel sonucu çıkarılamaz. Doğru dil: **“the observed pattern is consistent with a capability-threshold hypothesis.”** Bunu test etmek için birden çok sağlayıcıdan ara kapasite noktaları, bağımsız capability score ve segmented-regression/model-comparison gerekir.

## 1.18 Yeniden üretilebilirlik ve arşiv bütünlüğü

Güçlü taraflar: ham JSONL’ler, tarihli beyan zinciri, yerel determinism kontrolü, geçersiz frontier koşularının arşivde tutulması, script-generated numbers yaklaşımı.

Eksikler:

- dondurulmuş altı mevzuat belgesinin içerik snapshot’ları/hashi arşivde görünmüyor; hukuki doğruluk bağımsız denetlenemiyor;
- final CSV’de 413 satır `ONAY_BEKLIYOR`, 60 satır `YENI_EK`; “frozen final” statüsüyle uyumsuz terminoloji;
- Methods içinde en az iki `[verify]`/yer tutucu kalmış;
- parser son etiketi ve son 0–100 tam sayıyı alıyor; echoed/verbose output için adversarial test gerekli;
- raw response 160 karaktere kesiliyor; parse audit’i için tam ham response veya content hash saklanmalı;
- Ollama model digest, API snapshot, package versions, git commit ve prompt hash her sonuç dosyasında bulunmalı;
- “preregistered” kullanılmamalı; doğru ifade **“declared before analysis and timestamped in the repository.”**

---

# 2. İddia–kanıt eşleşmesi

Aşağıdaki sınıflandırma “destekleniyor / kısmen / desteklenmiyor / uygulama-geçersiz / adjudication pending” ayrımını kullanır.

| Bölüm | Mevcut iddia | Karar | Gerekçe | Gerekli yeni dil |
|---|---|---|---|---|
| §4.1 | 18×2×473 çağrı; iki model response gate’i geçemedi | **Destekleniyor** | Ham JSONL ve scorer çıktısı uyumlu | Korunabilir; “frontier establishes ceiling” yerine “hosted reference points” |
| §4.2 başlık | Hiçbir açık ağırlıklı model şans üstünde değil | **Desteklenmiyor** | Cluster-aware auditte dört hücre aile düzeltmesi sonrası pozitif association | “Weak, modest, and inconsistent local discrimination” |
| §4.2 | BAcc 0.48–0.64; J −.04–.28 | **Betimsel olarak destekleniyor** | Conditional E1 ve full-coverage E2 karışıyor | Coverage ile birlikte ver; formal chance iddiası yapma |
| §4.2 | λ yalnız 3–9 puanlık bilgi | **Aşırı genelleme** | median küçük; max .206; iki hücre corrected testte pozitif | “Most λ estimates were small; a minority showed modest discrimination” |
| §4.2 | Confidence AUROC .46–.54, completely uninformative | **Kısmen** | Aralık .5’e yakın; CI/test yok | “near chance descriptively; uncertainty intervals required” |
| §4.3 | Kaçınma var, seçicilik yok | **Kısmen / construct-limited** | Mevcut E2 karşılaştırmasında p<.05 yok; E2 intervention cevabı değiştiriyor | “abstention did not stratify E2 accuracy under this exploratory operationalisation” |
| §4.3 | Family/quantization changes abstention, not competence | **Nedensel dil fazla** | Observation var; nested dependencies ve order/seed confounds var | “abstention varied across families and quantizations without monotonic relation to observed BAcc” |
| §4.4 | Forced choice reverses decisions; 72–80% in three Llama quantizations | **Destekleniyor** | Raw paired outcomes uyumlu | Korunabilir; cluster-aware paired CI eklenmeli |
| §4.4 | 8/36 degenerate | **Payda sorunlu** | 28 metric-eligible, 32 response-valid | 8/28 primary; 8/32 secondary |
| §4.4 | McNemar misses bias reversal example | **Örnek destekleniyor** | Accuracy cancellation ile marginal bias değişimi ayrı şey | “can miss” diye yaz; genel theorem gibi sunma |
| §4.5 | Local prompt shifts | **Destekleniyor** | A/B local runner doğru yönlendiriyor | Relative change dördü için de ver; λ invariant deme |
| §4.5 | Hosted Sonnet highly prompt-stable; ~59× gap | **Uygulama-geçersiz** | Hosted runner B istemini göndermemiş | Rerun’a kadar çıkar |
| §4.6 | Sonnet markedly better than Haiku/local | **Variant-A betimsel olarak destekleniyor** | BAcc, ECE, reversal ve selectivity operationalization’ında fark büyük | “observed gap” deyin; threshold causality kurmayın |
| §4.6 | Same family/provider rules out confounds | **Desteklenmiyor** | Aynı provider/protocol bazı confoundları keser; training/model confoundlarını kesmez | Kontrol ettiği ve etmediği değişkenleri ayır |
| §4.6 | Sonnet selectively abstains, p=.0005 | **Exploratory + construct-limited** | Test family correction yok; E2 intervention | “under the study’s exploratory E2-based operationalisation” |
| §4.6/4.7 | Sonnet abstains on 69 year items | **Yanlış** | Year-specific items 60; toplam P6 abstentions 69 | 60 year-specific +9 other P6 |
| §4.7 | Everybody at exactly .50; universal single-label failure | **Yanlış** | P6 scorer error; BAcc .380–.570; 15/32 single-label-like | Heterogeneous failure modes |
| §4.8 | Local temp=0+seed exactly deterministic | **Destekleniyor** | 946/946 duplicate probe | Model/runtime version ve digest ile sınırla |
| §4.8 | Instability worse/better than confidence | **Exploratory** | Aggregation definitions differ; repeated-run coverage limited | Study-specific descriptive comparison |
| §3.6 pass 1 | κ=1; 0/150 | **Destekleniyor** | Internal-consistency instrument | Label validity değil, evidence recoverability diye sınırlamak doğru |
| §3.6 pass 1 | ≤2.50% one-sided | **Etiket yanlış** | Two-sided Wilson upper endpoint | Label fix or true one-sided recalc |
| §3.6 pass 2 | κ=.722; six one-direction disagreements, p=.031 | **Destekleniyor** | Veriler uyumlu | “identifies” değil “is consistent with systematic criterion difference” |
| §3.6 pass 2 | 6.7% / 8.8% contextual defect rate | **Adjudication pending** | Altı event unresolved disagreement | Candidate-flag estimate until adjudication |
| §3.6 | 1/2 real gold errors proves lenient rule | **Yanlış** | İkinci control label-error değil | Controls by defect type; rule substantively prespecified |
| §4.x expert | Any excerpt-derived audit cannot validate labels | **Aşırı evrensel** | Sonuç bu tasarımda circular evidence riskini gösterir | “may fail to validate evidence-dependent labels when audit evidence duplicates generation evidence” |

### En tehlikeli retorik kalıplar

- **“proved / establishes / identifies”** yerine “is consistent with / suggests / under this operationalisation.”
- **“all / none / universal”** yalnız formal family-wise test ve doğru metrikle.
- **“capability-caused”** yerine “observed performance gap.”
- **“gold error rate”** yalnız adjudicated final labels sonrası.
- **“prompt robustness”** yalnız gerçek farklı prompt hash’leriyle.

---

# 3. Hakemin ilk üç itirazı ve en iyi cevap

## İtiraz 1 — “Hosted prompt-stability finding is an implementation artefact.”

**Hakemin güçlü formu:** Varyant-B API koşusu farklı bir istem göndermemiştir; makalenin en çarpıcı stabilite ve ~59× fark sonucu geçersizdir. Bu, yalnız bir yazım hatası değil, experimental condition integrity failure’dır.

**En iyi cevap:** Savunmaya çalışmayın. Hatanın arşiv denetiminde bulunduğunu açıkça yazın; Sonnet-B’yi üç kez doğru runner ile yeniden koşun; satır bazında prompt hash ve runner commit ekleyin; eski koşuları “invalid—variant routing bug” etiketiyle arşivde tutun. Rerun sonucu farklıysa bütün §4.5/4.6 etkilerini güncelleyin.

**Ek veri zorunlu mu?** Evet. Yeni hosted-B run olmadan cevap yoktur.

## İtiraz 2 — “The statistical unit and selective-prediction estimand are misspecified.”

**Hakemin güçlü formu:** Maddeler aynı kaynak pasajlarından üretildiği için bağımsız değildir; E1 BAcc model-selected coverage’a koşulludur; E2 intervention’ı latent E1 guess gibi kullanılmıştır; confirmatory BAcc/J/λ testleri uygulanmamıştır. Bu nedenle chance, selectivity ve threshold anlatıları nominal p-değerleriyle desteklenemez.

**En iyi cevap:** Kaynak-kümeli bootstrap/GEE ile ana etkileri yeniden analiz edin; E1 için risk–coverage/AUGRC ve matched coverage ekleyin; E2 full-coverage’ı ana discrimination karşılaştırması yapın; E1-abstention/E2-accuracy analizini exploratory olarak yeniden adlandırın; future-work olarak joint guess+abstain protocolü verin. Önceden tanımlı ile audit-driven analizleri ayrı tabloda işaretleyin.

**Ek veri zorunlu mu?** Ham veriler yeterli; yeni model çağrısı gerekmiyor. Fakat daha temiz selectivity constructü için yeni deney idealdir ve mevcut makalede sınırlılık olarak kabul edilebilir.

## İtiraz 3 — “The gold standard is unresolved and the reported defect rate is not an error rate.”

**Hakemin güçlü formu:** İkinci geçişteki altı event adjudicate edilmemiştir; bir pozitif kontrol yanlış sınıflandırılmıştır; final set hâlâ `ONAY_BEKLIYOR` statüleri içerir. Model performansı geçici etiketlere göre raporlanmaktadır.

**En iyi cevap:** Önce kuralı yazın, sonra sekiz satırı adjudicate edin; label vs item-quality defect ayrımını yapın; v7’yi hash’leyin; değişen etiketlerde yeniden scoring/sensitivity verin; %6.7/%8.8’i adjudication öncesi candidate rate olarak bırakın veya final karara göre güncelleyin.

**Ek veri zorunlu mu?** Uzman uzlaşısı zorunlu; yeni örnekleme şart değil. Güvenilir CI için daha geniş ikinci-pass örneklemi güçlü bir ek olur fakat mevcut makale bunu sınırlılık olarak taşıyabilir.

### Dördüncü olası itiraz — “Why closed-book memory for an engineering compliance system?”

Bu, JESTECH’te ilk üçe girebilir. Gerçek mühendislik uygulaması mevzuatı retrieve eder; kapalı-kitap hafıza testi tek başına deployment-relevant bir sistem değerlendirmesi değildir. En iyi cevap, çalışmayı **failure-mode benchmark** olarak çerçevelemek ve retrieval-grounded/rule-based bir engineering baseline eklemektir. Baseline eklenmezse bu sınırlılık açıkça yazılmalı ve hedef dergi AI & Law veya LRE’ye kaydırılmalıdır.

---

# 4. Hedef dergi değerlendirmesi

## 4.1 JESTECH: mevcut kapsam uyumu

**Mevcut uygunluk puanı: 4/10.** Derginin resmi kapsamı teknoloji ve mühendisliğin teori ve pratiğini geniş biçimde kapsıyor; ancak mevcut taslak esasen Türkçe legal NLP benchmark ve LLM evaluation methodology makalesi olarak okunuyor. İnşaat, yapı denetimi ve İSG belgeleri yalnız veri kaynağı olarak kalırsa editör “engineering application nerede?” diye sorabilir.

Resmi sayfa 1 August 2026 itibarıyla gold open access APC’yi **USD 2,400**, submission-to-first-decision süresini **57 days**, decision-after-review süresini **112 days** olarak gösteriyor. Bunlar yayınevi metrikleridir; garanti değildir ve “first decision” tam hakemlik süresi değildir.

### JESTECH’e uyumu artıran çerçeve

1. Problemi “legal QA” değil **safety-critical engineering regulatory decision support** olarak kurun: building permitting, structural design, construction inspection, occupational safety.
2. Hata maliyetini mühendislik iş akışına bağlayın: yanlış mevzuat beyanı, yanlış denetim yönlendirmesi, güvenli olmayan tasarım veya gecikmiş insan eskalasyonu.
3. Reject option’ı operasyonel karar politikası yapın: otomatik cevap / uzman incelemesine yönlendirme / kaynak retrieval zorunluluğu.
4. En az bir gerçekçi baseline ekleyin: BM25/RAG, deterministic article lookup veya rule-based claim verification. Kapalı-kitap sonuç, bu uygulamalı baseline’ın “memory-only unsafe lower bound”u olsun.
5. Başlık ve özette “engineering compliance” öne çıksın; generic “capability threshold” geri çekilsin.
6. Dataset belgelerinin sürüm/zaman damgası ve regulatory snapshot mantığı mühendislik yaşam döngüsüyle açıklansın.

**Baseline eklenmezse:** JESTECH desk-reject riski yüksektir. Veri alanının mühendislik olması, metodolojik makaleyi otomatik olarak engineering paper yapmaz.

## 4.2 Alternatif dergiler

| Dergi | Uyum | Neden | Resmi ilk karar metriği | APC durumu (1 Aug 2026) | Koşul |
|---|---:|---|---:|---|---|
| **Artificial Intelligence and Law** | **9/10** | Legal AI systems, datasets, empirical evaluation and auditing techniques kapsamda açıkça yer alıyor | Median 6 days | Hybrid; subscription route no APC; OA USD 3,290 | Teknik katkıyı, gold auditini ve legal-system implications’ı güçlendir |
| **Language Resources and Evaluation** | **8.5/10** | Resource creation, annotation, benchmarking and evaluation yöntemleri doğrudan kapsamda | Median 36 days | Hybrid; subscription route no APC; OA USD 3,590 | Dataset card, licensing, source snapshots, benchmark comparison ve final adjudication şart |
| **Engineering Applications of Artificial Intelligence** | **6.5/10** | Gerçek-world engineering AI application bekler | First decision 85 days; decision after review 207 days | OA APC USD 3,040; subscription/OA seçenekleri submission anında doğrulanmalı | RAG/rule baseline ve engineering workflow evaluation olmadan zayıf |
| **Expert Systems with Applications** | **6/10** | Intelligent/expert systems ve applied evaluation geniş kapsam | First decision 62 days; decision after review 147 days | OA APC USD 3,490; hybrid route koşulları doğrulanmalı | Generic benchmark değil, decision-support system ve deployment policy olarak sunulmalı |

### Hedef sıralaması

- **Mevcut veri ve metodolojiyle en doğal hedef:** Artificial Intelligence and Law.
- **Benchmark/resource makalesi olarak en temiz hedef:** Language Resources and Evaluation.
- **JESTECH/EAAI:** retrieval-grounded engineering baseline ve gerçek iş akışı çerçevesi eklenirse.

## 4.3 İki makaleye bölme kararı

**Evet, bölünebilir; fakat şimdi değil.** Önce uzlaşı, v7 freeze ve ana yeniden analiz tamamlanmalı. Sonra iki makalenin araştırma soruları ve tabloları açık biçimde ayrılmalıdır.

### Makale A — RUHSAT-Bench benchmark paper

Kapsam:

- 473/v7 claims and probe taxonomy;
- E1 vs E2 design;
- open-weight and hosted model evaluation;
- cluster-aware discrimination;
- risk–coverage/AUGRC;
- forced-choice instability;
- corrected prompt sensitivity;
- concise gold-quality summary.

Hedef: **Artificial Intelligence and Law**; engineering baseline eklenirse JESTECH/EAAI.

### Makale B — Evidence-dependent benchmark auditing methodology

Kapsam:

- circular evidence audit problem;
- two-pass audit design;
- quality vs verdict axes;
- decision-rule/adjudication sensitivity;
- positive-control taxonomy;
- model-consensus screening failure;
- design-weighted defect estimation.

Hedef: **Language Resources and Evaluation** veya AI & Law Research Note/full article.

### Bölme koşulları

- Aynı ana sonuç tablosunu iki kez yayımlamayın.
- Benchmark paper gold QA’yı bir paragraf + final estimate ile özetlesin.
- Audit paper model leaderboard ve capability claims’i yeniden yayımlamasın.
- Cross-reference, shared repository ve overlapping sample şeffaf biçimde beyan edilsin.
- Her makale bağımsız novelty ve ayrı primary question taşısın; aksi halde salami slicing görünür.

---

# 5. Eksik bölümler için paragraf düzeyinde İngilizce iskelet

Aşağıdaki metinler tam makale değildir; her paragrafın argüman işlevini ve kullanılabilecek çekirdek cümleyi verir.

## 5.1 Introduction — 7 paragraphs

**P1 — Engineering-regulatory problem.**  
*Engineering decisions in construction permitting, building inspection, structural safety, and occupational health are mediated by dense, frequently amended regulatory texts. Language models could reduce retrieval and triage costs, but a confidently incorrect regulatory statement can redirect an engineer away from the controlling provision.*

**P2 — Why abstention matters.**  
*For such settings, accuracy under forced prediction is an incomplete safety criterion. A useful system should not only distinguish true from false claims but also defer when its internal evidence is insufficient, thereby trading coverage for lower retained-case risk.*

**P3 — Gap in current evaluation.**  
*Most legal and Turkish-language benchmarks emphasise answer accuracy, multiple-choice performance, or broad reasoning coverage. They rarely test whether abstention is selective, whether forced choice changes the underlying verdict, or whether the resulting measurement is stable under semantically equivalent prompt formulations.*

**P4 — Why regulatory benchmarks are difficult to build.**  
*Regulatory evaluation also creates a gold-standard problem: claims are often generated from excerpts whose local wording omits conditions, exceptions, or temporal context carried by the full article. An audit that presents the same excerpt used for label generation may therefore verify internal consistency without validating the label against the governing source.*

**P5 — Study design.**  
*We introduce RUHSAT-Bench, a Turkish engineering-regulation benchmark comprising [final v7 n] claims derived from six construction, building-control, occupational-safety, and seismic documents. Six probe families test direct support, numerical perturbation, enactment chronology, fabricated instruments, cross-reference shifts, and regulatory currentness. Each claim is evaluated under an abstention-permitted condition (E1) and a forced-choice condition (E2).*

**P6 — Research questions, not conclusions.**  
*We ask four questions: (RQ1) do systems discriminate claim truth beyond response-label bias; (RQ2) does abstention concentrate on cases that are difficult under a prespecified operationalisation; (RQ3) how does forced choice alter verdicts and label marginals; and (RQ4) how stable are these measurements across prompt formulations and repeated hosted-model runs? A fifth methodological question examines how evidence access changes expert gold-label audits.*

**P7 — Contributions, cautiously framed.**  
*The study contributes a domain-specific benchmark and audit trail, a paired abstention/forced-choice protocol, source-cluster-aware analyses of discrimination and stability, and a two-pass expert audit that separates excerpt consistency from full-provision validity. The results characterise the evaluated model snapshots and regulatory corpus; they do not establish a universal capability threshold or the safety of deployment without retrieval and human review.*

## 5.2 Related Work — 8 paragraphs

**P1 — Selective prediction and reject options.**  
Introduce Chow’s reject option, selective classification, coverage–risk trade-offs, and contemporary multi-threshold evaluation such as AURC/AUGRC. Explain that RUHSAT-Bench tests a natural-language abstention policy rather than a calibrated rejector over fixed logits.

**P2 — Confidence calibration and LLM self-knowledge.**  
Connect neural calibration, verbalised confidence and self-evaluation. Distinguish calibration conditional on answered items from selective risk over all items. State why ECE alone is insufficient when coverage varies.

**P3 — Prompt and response-format sensitivity.**  
Review evidence that meaning-preserving format changes can alter LLM performance. Position the two prompts as a limited, prespecified probe—not an estimate of the full prompt distribution.

**P4 — Forced choice and response bias.**  
Draw on survey measurement/psychometrics and LLM option-order/acquiescence literature. Explain that unchanged accuracy can coexist with a large change in marginal label bias, motivating direct reversal and label-share analyses.

**P5 — Benchmark label quality and audit circularity.**  
Review test-set label errors, data auditing, and the limits of automated/model-consensus screens. Introduce the distinction between auditing a label against its generation evidence and against the full authoritative source.

**P6 — Legal AI benchmarks and LLM-as-judge.**  
Position LegalBench and related legal NLP evaluations. Explain why an engineering-regulation claim-verification benchmark differs from general legal reasoning tasks and why model consensus is not treated as ground truth.

**P7 — Turkish LLM evaluation.**  
Cover TurkishMMLU, TR-MMLU and TurkBench, then identify the missing combination: engineering regulation, truth/falsehood perturbations, abstention, forced-choice reversals, temporal currentness and expert source audit.

**P8 — Engineering regulatory compliance.**  
Review automated compliance checking, NLP extraction of building regulations, LegalRuleML conversion, construction-safety retrieval, and RAG-based code interpretation. Use this literature to justify the engineering workflow and to explain why closed-book performance is a stress test rather than a recommended deployment architecture.

## 5.3 Discussion — 9 paragraphs

**P1 — Weak but not uniformly chance local discrimination.**  
*The corrected analysis indicates modest and inconsistent local discrimination rather than universal chance performance. A small subset of cells retains a positive gold–prediction association under source-clustered, family-wise correction, while most effects remain close to zero or collapse under forced choice.*

**P2 — Coverage changes the meaning of performance.**  
Discuss why high conditional BAcc at low coverage cannot be equated with high full-task performance. Interpret risk–coverage/AUGRC and E2 results together.

**P3 — Abstention frequency is not abstention quality.**  
Explain that wide abstention rates show policy variability. Under the current exploratory E2-based operationalisation, most local systems do not cleanly stratify subsequent E2 difficulty; acknowledge the treatment contamination.

**P4 — Forced choice manufactures behavioural signal.**  
Describe verdict reversals and label collapse. Emphasise that forced-choice evaluation can change what is measured, not merely reveal a hidden answer. Accuracy-only McNemar analysis may miss large marginal bias shifts.

**P5 — Prompt stability after corrected rerun.**  
After the hosted-B rerun, discuss local and hosted prompt sensitivity using both absolute and relative effects. Do not claim λ invariance. Treat two prompts as two sampled points in a much larger design space.

**P6 — Capability-threshold hypothesis.**  
*Sonnet’s observed advantage over Haiku and the local systems is consistent with a threshold-like pattern across the selected model snapshots, but the design cannot isolate capability from architecture, training exposure, alignment policy, or contamination.*

**P7 — P6 and temporal knowledge.**  
Discuss heterogeneous failure modes: year-specific abstention, single-label collapse, and near-chance two-class separation. Connect this to the need for retrieval against versioned regulatory sources.

**P8 — Gold-standard methodology.**  
Explain why pass 1 establishes recoverability/internal consistency and pass 2 addresses contextual validity. Report only adjudicated defect estimates. Narrow the generalisation to evidence-dependent labels.

**P9 — Engineering deployment implications.**  
*The results argue against using closed-book LLM verdicts as autonomous regulatory advice. A defensible architecture should retrieve versioned provisions, expose citations, employ a calibrated defer-to-expert policy, log the regulatory snapshot, and treat the benchmark as a stress test for the residual failure modes of that pipeline.*

## 5.4 Limitations — 8 paragraphs

**P1 — One jurisdiction and six documents.**  
*RUHSAT-Bench represents one national jurisdiction and six regulatory instruments. The observed behaviours may not transfer to other legal systems, engineering disciplines, document genres, or languages.*

**P2 — P3 structural ceiling.**  
*The chronology probe contains only 19 items because its size is constrained by the number of eligible documents rather than by claim generation capacity. Per-probe estimates for P3 are therefore imprecise and should not support fine-grained model rankings.*

**P3 — Hosted nondeterminism and model coverage.**  
*Hosted-model outputs are not deterministic; majority voting reduces but does not eliminate run variance. The higher-capability comparison includes only one strong hosted model, limiting any inference about a general capability threshold.*

**P4 — Two prompt points.**  
*Prompt robustness is evaluated at two hand-designed formulations. These points cannot estimate the distribution of performance over plausible prompts. Hosted variant-B results must additionally be based on the corrected routing implementation and verified prompt hashes.*

**P5 — Regulatory snapshot and currentness.**  
*TBDY 2018 and the other instruments are evaluated as versioned snapshots. The benchmark does not establish performance on future amendments, consolidated renderings, tables, annexes, or cross-document temporal chains.*

**P6 — Gold quality and contextual-defect estimate.**  
*The second-pass contextual estimate must be reported after adjudication. Until then, 6.7% and 8.8% are candidate-flag estimates rather than final label-error rates. The two-stage sample and source clustering further widen uncertainty beyond a simple item-level interval.*

**P7 — Statistical dependence and selectivity construct.**  
*Claims derived from the same source excerpt are dependent. Source-clustered analyses mitigate but do not remove all template-level dependence. Moreover, E2 is an intervention that can alter the verdict, so the E1-abstention/E2-accuracy comparison is an imperfect proxy for latent epistemic selectivity.*

**P8 — Declaration chain, not preregistration.**  
*The analysis decisions were declared before specified analyses and timestamped in the repository, but the study was not registered in an external preregistration system. Confirmatory, amended, invalidated and audit-driven analyses are therefore distinguished explicitly rather than described collectively as preregistered.*

---

# 6. Kaynak haritası ve doğrulanmış literatür

Aşağıdaki kaynaklar 1 August 2026’da birincil yayın/proceedings/publisher sayfalarından kontrol edilmiştir. Her kaynak, **çalışmanızın verisini doğrulamaz**; yalnız ilgili teorik veya metodolojik iddiayı dayandırır.

| Makaledeki iddia | Kaynak türü | Doğrulanmış başlangıç kaynakları | Nasıl kullanılmalı |
|---|---|---|---|
| Kaçınmalı değerlendirme meşru bir çerçevedir | Selective classification / reject option | Chow (1970); Geifman & El-Yaniv (2017); Traub et al. (2024) | Coverage–risk estimandını kur; E1 doğal-dil abstention ile formal rejector farkını belirt |
| Güven kalibrasyonu ayrı bir özelliktir | Calibration | Guo et al. (2017) | Standard ECE/Brier/reliability; E1 coverage koşulluluğunu tartış |
| LLM’ler ne bildiklerini kısmen tahmin edebilir | LLM self-evaluation | Kadavath et al. (2022) | Sonnet sonucuna öncül; sizin sonuçlarınızın model/saha-spesifik olduğunu vurgula |
| Prompt biçimi ölçümü değiştirebilir | Prompt sensitivity | Sclar et al. (ICLR 2024) | Tek prompt score yerine plausible-format range gerekçesi |
| Benchmark etiketleri hata içerebilir | Dataset auditing | Northcutt, Athalye & Mueller (2021) | Gold QA motivasyonu; sizin iki-pass audit novelty’nizi bunun ötesinde konumlandır |
| LLM judge/consensus yanlı olabilir | LLM-as-judge | Zheng et al. (2023) ve sonraki judge-bias literatürü | Model konsensüsünü gold yerine screening aracı olarak sınırla |
| Hukuki LLM benchmarkları vardır | Legal NLP evaluation | Guha et al., LegalBench (2023) | Task taxonomy ve legal reasoning kapsamı karşılaştırması |
| Türkçe geniş LLM benchmarkları vardır | Turkish NLP benchmark | Yüksel et al., TurkishMMLU (2024); Bayram et al., TR-MMLU (2025 preprint); Toraman et al., TurkBench (2026) | RUHSAT-Bench’in domain/abstention/currentness boşluğunu göster |
| Türkçe değerlendirmede prompt örneği/formatı kararları etkileyebilir | Turkish empirical evaluation | Kara & Yıldırım (2026) | Yerel literatür bağlantısı; doğrudan benchmarkınızla eşdeğer göstermeyin |
| Yapı mevzuatı makinece işlenebilir hale getirilmeye çalışılıyor | Automated compliance checking | Wu, Xue & Zhang (2023); Fuchs et al. (2024) | JESTECH engineering framing’i |
| LLM/RAG inşaat güvenliği ve yapı kodlarında kullanılıyor | Construction regulatory AI | Tran et al. (2024); Yang & Hou (2025); Sun, Luo & Li (2025) | Closed-book stress testin neden deployment architecture olmadığını açıkla |
| κ yorumunda prevalans/paradoks sorunları vardır | Agreement methodology | Cohen (1960); Landis & Koch (1977); Feinstein & Cicchetti (1990) | κ’yı agreement table ve prevalence ile birlikte ver; adjective threshold’ları mekanik kullanma |

## Doğrulanmış çekirdek bibliyografya

1. Chow, C. K. (1970). *On optimum recognition error and reject tradeoff*. IEEE Transactions on Information Theory, 16(1), 41–46.
2. Geifman, Y., & El-Yaniv, R. (2017). *Selective Classification for Deep Neural Networks*. Advances in Neural Information Processing Systems 30.
3. Traub, J., Bungert, T. J., Lüth, C. T., Baumgartner, M., Maier-Hein, K. H., Maier-Hein, L., & Jäger, P. F. (2024). *Overcoming Common Flaws in the Evaluation of Selective Classification Systems*. Advances in Neural Information Processing Systems 37.
4. Guo, C., Pleiss, G., Sun, Y., & Weinberger, K. Q. (2017). *On Calibration of Modern Neural Networks*. Proceedings of ICML, PMLR 70.
5. Kadavath, S., et al. (2022). *Language Models (Mostly) Know What They Know*. arXiv:2207.05221.
6. Sclar, M., Choi, Y., Tsvetkov, Y., & Suhr, A. (2024). *Quantifying Language Models’ Sensitivity to Spurious Features in Prompt Design, or: How I Learned to Start Worrying about Prompt Formatting*. ICLR 2024.
7. Northcutt, C. G., Athalye, A., & Mueller, J. (2021). *Pervasive Label Errors in Test Sets Destabilize Machine Learning Benchmarks*. NeurIPS Datasets and Benchmarks.
8. Zheng, L., et al. (2023). *Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena*. Advances in Neural Information Processing Systems 36.
9. Guha, N., et al. (2023). *LegalBench: A Collaboratively Built Benchmark for Measuring Legal Reasoning in Large Language Models*. NeurIPS Datasets and Benchmarks.
10. Yüksel, A., Köksal, A., Şenel, L. K., Korhonen, A., & Schütze, H. (2024). *TurkishMMLU: Measuring Massive Multitask Language Understanding in Turkish*. Findings of EMNLP 2024.
11. Bayram, M. A., Fincan, A. A., Gümüş, A. S., Diri, B., Yıldırım, S., & Aytaş, Ö. (2025). *Setting Standards in Turkish NLP: TR-MMLU for Large Language Model Evaluation*. arXiv:2501.00593.
12. Toraman, Ç., et al. (2026). *TurkBench: A Benchmark for Evaluating Turkish Large Language Models*. Proceedings of SIGTURK 2026, DOI 10.18653/v1/2026.sigturk-1.12.
13. Kara, A., & Yıldırım, S. (2026). *Evaluating Large Language Models in Turkish Short Answer Scoring: Validity, Reliability, and Fairness Perspectives*. Sakarya University Journal of Computer and Information Sciences, 9(3), 980–994.
14. Wu, J., Xue, X., & Zhang, J. (2023). *Invariant Signature, Logic Reasoning, and Semantic NLP-Based Automated Building Code Compliance Checking (I-SNACC) Framework*. Journal of Information Technology in Construction, 28, 1–18. DOI 10.36680/j.itcon.2023.001.
15. Fuchs, S., Witbrock, M., Dimyadi, J., & Amor, R. (2024). *Using Large Language Models for the Interpretation of Building Regulations*. arXiv:2407.21060.
16. Tran, S. V.-T., et al. (2024). *Leveraging Large Language Models for Enhanced Construction Safety Regulation Extraction*. Journal of Information Technology in Construction, 29. DOI 10.36680/j.itcon.2024.045.
17. Sun, J., Luo, Z., & Li, Y. (2025). *A Compliance Checking Framework Based on Retrieval Augmented Generation*. Proceedings of COLING 2025, 2603–2615.
18. Cohen, J. (1960). *A Coefficient of Agreement for Nominal Scales*. Educational and Psychological Measurement, 20(1), 37–46.
19. Landis, J. R., & Koch, G. G. (1977). *The Measurement of Observer Agreement for Categorical Data*. Biometrics, 33(1), 159–174.
20. Feinstein, A. R., & Cicchetti, D. V. (1990). *High Agreement but Low Kappa: I. The Problems of Two Paradoxes*. Journal of Clinical Epidemiology, 43(6), 543–549.

**Kaynak kullanım uyarısı:** “Literatür X’in mümkün olduğunu gösteriyor” ile “RUHSAT-Bench’te X gözlendi” aynı cümle değildir. İkinci iddia yalnız sizin veriniz ve doğru analizinizle desteklenebilir.

---

# 7. Doğrudan kullanılabilir düzeltme metinleri

## Replacement for Results §4.2

> **Local discrimination was weak but not uniformly indistinguishable from chance.** In a post hoc audit using source-excerpt-clustered association tests, four of 28 metric-eligible model–condition cells retained a positive association between gold and predicted labels after Bonferroni correction. Effect sizes were modest and inconsistent across conditions, and E1 estimates were conditional on model-selected coverage. These results do not support a categorical claim that every open-weight system was at chance.

## Replacement for Results §4.5

> **Local measurements were prompt-sensitive across all four reported quantities.** Across nine local model–condition cells with at least 30 commitments under both prompts, relative changes were 1.76 for P(TRUE), 1.56 for abstention, 0.96 for committed accuracy, and 0.92 for λ. The small absolute change in λ reflects its near-zero level and should not be interpreted as prompt invariance. Hosted prompt-stability results are withheld pending a corrected variant-B run, because the archived API runner recorded the variant label without routing a distinct prompt.

## Replacement for Results §4.6

> **The observed hosted-model gap is consistent with, but does not establish, a capability threshold.** Sonnet exhibited a large observed advantage over Haiku and the local systems across discrimination, calibration, the study’s exploratory abstention-selectivity operationalisation, and verdict stability. Because the comparison contains only one higher-performing hosted model and does not control architecture, training data, Turkish regulatory exposure, alignment policy, or contamination, it cannot identify capability as the causal explanation.

## Replacement for Results §4.7

> **P6 revealed heterogeneous failure modes rather than universal chance performance.** Across response-valid local cells, P6 balanced accuracy ranged from 0.380 to 0.570, and 15 of 32 cells assigned at least 90% of commitments to one label. Sonnet abstained on all 60 year-specific E1 items and on nine additional P6 items; under E2 its P6 balanced accuracy was 0.508. These patterns indicate a mixture of abstention, label collapse, and weak two-class discrimination.

## Replacement for expert-audit estimate

> **Before adjudication**, applying the lenient rule (at least one rater differs from gold) produced a design-weighted candidate-flag estimate of 6.7% in the 138-item frame and an 8.8% two-stage projection to the full claim set. Because all six events are unresolved inter-rater disagreements, these values are not final label-error estimates. Final estimates will be reported after the decision rule is fixed, the eight reconciliation items are adjudicated, and the benchmark version is frozen.

## Replacement for the general audit claim

> When labels are derived from evidence excerpts, an audit that exposes only the same excerpts may verify the recoverability of the generation rule without validating the labels against the full authoritative source. Source-level review is therefore necessary for defect classes involving omitted conditions, exceptions, anaphora, or cross-paragraph context.

---

# 8. Yeniden analiz planı

## Phase A — integrity repair

1. Preserve the current archive unchanged; publish its SHA-256 manifest.
2. Patch hosted variant routing and add prompt hashes.
3. Rerun Sonnet-B three times with thinking disabled; retain old files as invalidated artefacts.
4. Adjudicate the eight expert items after freezing the rule text.
5. Release `uretilen_iddialar_v7_adjudicated.csv`, changelog and hash.

## Phase B — primary statistical rebuild

1. Re-score all local/hosted runs against v7.
2. Define three analysis populations: response-valid, metric-eligible, and full E2.
3. Report source-cluster bootstrap CIs for BAcc, J, λ, coverage, reversal and label share.
4. Apply a transparent multiplicity plan to a small set of primary contrasts.
5. Report risk–coverage curves and AUGRC; include matched-coverage comparisons.
6. Replace P6 prob table with actual BAcc and label-share metrics.
7. Recompute standard ECE, Brier score and reliability diagrams.
8. Report model family/checkpoint as the replication level; quantizations as nested sensitivity.

## Phase C — manuscript and venue

1. Rewrite §4.2, §4.5, §4.6, §4.7 and expert §3.6/4.x.
2. Add the Introduction/Related Work/Discussion/Limitations structures above.
3. For JESTECH/EAAI, add a retrieval-grounded or deterministic engineering-compliance baseline.
4. Otherwise submit the benchmark paper to AI & Law or LRE.
5. Split the audit-methodology paper only after final labels and non-overlapping contribution maps are fixed.

---

# 9. Final pre-submission gate

Do not submit until every box is true:

- [ ] Hosted B prompt hash differs from A and was actually sent.
- [ ] Three corrected Sonnet-B runs and majority output are archived.
- [ ] All eight adjudication rows and the rule note are complete.
- [ ] Final v7 claim set, changelog and SHA-256 are frozen.
- [ ] All manuscript tables identify the exact dataset hash.
- [ ] P6 uses BAcc; single-class probes use label share, not knowledge-language accuracy.
- [ ] Source-cluster dependence is handled.
- [ ] E1 comparisons are coverage-aware; E2 full-coverage is visible.
- [ ] Multiplicity families are explicit.
- [ ] Standard ECE/Brier/reliability are supplied.
- [ ] 8/28 or 8/32 denominator is used, with definition.
- [ ] 0-event intervals are correctly named/calculated.
- [ ] %6.7/%8.8 is final only after adjudication; otherwise “candidate-flag estimate.”
- [ ] “Capability threshold” is hypothesis-consistent language, not causal conclusion.
- [ ] “Preregistered” is replaced by the dated-declaration wording.
- [ ] Frozen legal sources, retrieval dates, versions and hashes are documented.
- [ ] Model digests/API snapshots, prompt hashes, environment and git commit are recorded.
- [ ] No JESTECH submission is made without an engineering-workflow argument; ideally an applied baseline.

---

# Appendix A — Artefact hashes

| Artefact                  | Path                                                                           | SHA-256                                                          |
|:--------------------------|:-------------------------------------------------------------------------------|:-----------------------------------------------------------------|
| Source archive            | /mnt/data/ruhsat-bench_arsiv_20260801.zip                                      | 3acaefd8a086e8979eb84d48b2de7a342fce00bc0eb2e3438a36ff684cd12027 |
| Delivery package          | /mnt/data/RUHSAT-Bench_teslim_paketi.zip                                       | fc343dfc8fb9fc8ea85502b63ceeea14fd196ec16ab3693d2981f0dde6d590da |
| Third-eye prompt          | /mnt/data/UCUNCU_GOZ_PROMPT.md                                                 | 8a91ba91ea4bc2b7753bd5035d9ee2decfa07cd0f8198c976259b8ba7ed92643 |
| Environment note          | /mnt/data/ORTAM.md                                                             | 72934045fbe0b299aea21594a21fe54c11f60ae7c103e95596c0661360449b71 |
| Handover note             | /mnt/data/HANDOVER (3).md                                                      | 2962d6059656f887df52998afd310bb1aeb1ffac925b7c494b17017bd60f4b23 |
| Final claim set v6        | /mnt/data/py_ruhsat_review/archive/iddialar/uretilen_iddialar_v6_onarilmis.csv | 3f2b4b7b31d49c8024c0da284a97dd5090dffab50971ef3d025df848861ab8c9 |
| Local raw JSONL           | /mnt/data/py_ruhsat_review/archive/sonuclar/f4_sonuclar.jsonl                  | cfea2269317717c638698fc3ad0e2996a353f8e3b27b4ec18c47952bbb7b5c3d |
| Sonnet majority JSONL     | /mnt/data/py_ruhsat_review/archive/sonuclar/f4_frontier_cogunluk.jsonl         | 3fd48cb6d7b3f8c9304060b6f03e78b8d930922a3325ff97b8bad9d9129292b7 |
| Haiku majority JSONL      | /mnt/data/py_ruhsat_review/archive/sonuclar/f4_haiku_cogunluk.jsonl            | 11559c6ceb0e19fa3cb3439827628c9d5ccbbdb74276672009cc883c8d85a0c7 |
| Archived API runner       | /mnt/data/py_ruhsat_review/archive/scripts/f4_api.py                           | f76eefc54cfb949b1d85c1f19d7b91d542fc8a0e4d54719a187ff5ed581d214f |
| Archived scorer           | /mnt/data/py_ruhsat_review/archive/scripts/f4_skor.py                          | 5ec63419642a2fb123c7c7db2335750ede4f03a6d9c64032c2ce0ba7d9073470 |
| Pending adjudication file | /mnt/data/py_ruhsat_review/archive/sonuclar/gecis2_uzlasi.csv                  | 1def41b3a32dfede09ca0dd871f543d9ac2fdff7546ebddea8e2de2303a996bc |

# Appendix B — Recomputed audit artefacts

The companion audit bundle contains:

- `audit_recompute.py` and raw output;
- `cluster_robust_tests_v2.py` and result table;
- `cluster_robust_lambda_v2.py` and result table;
- `cluster_bootstrap_fast.py` and output;
- `recompute_ece.py` and output;
- full CSV tables for cell metrics, P6, calibration, clustered association and λ;
- a suggested variant-B API patch and integrity checks;
- SHA-256 manifest.

# Appendix C — Overall reviewer recommendation

**Recommendation: major reanalysis before submission.** The paper’s strongest publishable contribution is not “all local models are at chance” or “a capability threshold has been proven.” It is a more careful and more interesting result: **closed-book regulatory claim evaluation combines weak and unstable discrimination, highly variable deferral policies, forced-choice-induced verdict changes, and gold-standard vulnerabilities that are invisible when the audit repeats the evidence used to generate the label.** That contribution survives, but only after the three P0 failures are repaired and the statistical language is brought back to what the data actually support.
