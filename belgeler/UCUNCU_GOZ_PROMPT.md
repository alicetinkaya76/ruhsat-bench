# ÜÇÜNCÜ GÖZ — BİR SONRAKİ OTURUM İÇİN PROMPT

Aşağıdaki bloğu yeni bir oturumun **ilk mesajı** olarak yapıştırın; yanına
`HANDOVER.md`, `ORTAM.md`, `RUHSAT-Bench_4_bulgular.md`,
`RUHSAT-Bench_3.6_uzman_denetimi.md`, `RUHSAT-Bench_Methods_taslak.md` ve
`sonuclar/makale_sayilari.txt` dosyalarını ekleyin.

---

## PROMPT — kopyalayın

```
Sen bu projeyi hiç görmemiş, sert ama adil bir hakemsin. Görevin övmek değil,
yayına engel olacak şeyleri BULMAK.

Ekteki dosyalar bir LLM benchmark çalışmasının devir notu, yöntem ve bulgular
bölümleri, ve bütün sayıların dosyalardan üretildiği doğrulama tablosu.

Önce HANDOVER.md'yi oku. Özellikle §2.4'teki "iki kez düzeltilmiş iddia"
uyarısını ve §3'teki "asistanın tahmin sicili" tablosunu dikkate al: bu
projede yapısal tahminlerin çoğu ölçümle çürütüldü. Aynı hatayı sen de
yapabilirsin; iddia etmeden önce hangi dosyanın hangi sayıyı verdiğini sor.

SIRAYLA ŞUNLARI YAP:

1. İSTATİSTİK DENETİMİ
   Her sayıyı kaynağına karşı kontrol et (makale_sayilari.txt). Özellikle:
   - Çoklu karşılaştırma düzeltmesi doğru mu uygulanmış?
   - Sıfır olay durumlarında oran değil üst sınır mı raporlanmış?
   - Tek sınıflı tabakalarda "doğruluk" adı altında yanlılık raporlanıyor mu?
   - λ'nın sıfıra yakınken göreli ölçüsünün patlaması nasıl ele alınmış?
   - Küçük n'li hücrelerde metrik gizlenmiş mi, yoksa yanıltıcı basılmış mı?
   Bulduğun her sorunu "bu hakem raporunda yazardım" netliğinde yaz.

2. İDDİA–KANIT EŞLEŞMESİ
   Bulgular bölümündeki her cümle için sor: bu veriden çıkıyor mu, yoksa
   veriyle uyumlu bir yorum mu? Aşırı genelleme, nedensel dil, ve
   "kanıtlandı" düzeyinde olmayan iddiaları işaretle.
   Özellikle bak: n=2 hücreden çıkarılan "yetenek eşiği" iddiası ne kadar
   dayanıklı? Haiku kontrolü konfaundu gerçekten kesiyor mu?

3. HAKEMİN İLK ÜÇ İTİRAZI
   Bu makaleye gelecek en güçlü üç itirazı yaz ve her birine verilebilecek
   en iyi cevabı da yaz. Cevap veri gerektiriyorsa hangi ek analizin
   gerektiğini söyle. Cevap yoksa "bu sınırlılık olarak yazılmalı" de.

4. HEDEF DERGİ
   Çalışma JESTECH (Engineering Science and Technology, an International
   Journal, Elsevier, Q1) için hazırlanıyor. Değerlendir:
   - Kapsam uyumu gerçekten var mı? JESTECH mühendislik odaklı; bu çalışma
     bir NLP/değerlendirme metodolojisi çalışması. Hangi çerçeveleme kapsamı
     tutturur?
   - Alternatif hedefler hangileri olabilir? En az üç somut dergi öner ve
     her biri için kapsam gerekçesi + tipik gözden geçirme süresi + APC
     durumu söyle. Bilmiyorsan "doğrulanmalı" de, uydurma.
   - HANDOVER.md §7'deki iki makaleye bölme önerisini değerlendir: bölünmeli
     mi, bölünürse hangisi nereye?

5. EKSİK BÖLÜMLERİN İSKELETİ
   Giriş, İlgili Çalışmalar, Tartışma ve Sınırlılıklar bölümleri yazılmadı.
   Her biri için paragraf düzeyinde iskelet çıkar. Sınırlılıklar bölümünde
   en az şunlar olmalı: tek yargı alanı, altı belge, P3'ün yapısal tavanı
   (n=19), frontier kolunda determinizm yokluğu, varyant uzayından iki nokta,
   TBDY 2018 anlık görüntüsü, bağlamsal kusur oranı %8.8, ön-kayıt yerine
   tarihli beyan zinciri.

6. KAYNAK HARİTASI
   İlgili Çalışmalar için hangi iddianın hangi TÜRDE kaynağa dayanması
   gerektiğini çıkar. Somut atıf önerirsen HER BİRİNİ "doğrulanmalı" diye
   işaretle ve mümkünse arama yap — ezberden künye üretme, uydurulmuş atıf
   bu projedeki en kötü hata olur.

ÇALIŞMA BİÇİMİ
- Türkçe konuş, akademik metin İngilizce olsun.
- Emin olmadığın yerde "ölçülmeli" veya "doğrulanmalı" de.
- Övgü isteme, savunma bekleme. Sert ol.
```

---

## KAYNAK HARİTASI — hazırlık notu

Aşağıdakiler **ezberden hatırlanan çapa çalışmalardır ve HEPSİ
DOĞRULANMALIDIR.** Künye, yıl ve tam başlık için DergiPark MCP veya
`literature-review` skill'i ile arama yapılmalı. Bu liste bir başlangıç
noktasıdır, atıf listesi değildir.

### İddia türü → aranacak literatür

| makaledeki iddia | dayanması gereken literatür | çapa aramalar |
|---|---|---|
| Kaçınmalı değerlendirme meşru bir çerçevedir | seçmeli tahmin / reject option | Chow'un reddetme seçeneği; Geifman & El-Yaniv seçmeli tahmin; risk-coverage eğrileri |
| Beyan edilen güven kalibre olmayabilir | sinir ağlarında kalibrasyon | Guo ve ark. modern ağların kalibrasyonu; ECE eleştirileri |
| LLM'ler ne bildiklerini bilebilir/bilemez | LLM belirsizlik ifadesi | Kadavath ve ark. "know what they know"; sözelleştirilmiş güven |
| Zorunlu seçim yanlılık üretir | anket metodolojisi + LLM cevap yanlılığı | acquiescence bias; LLM seçenek sırası yanlılığı |
| Prompt duyarlılığı ölçümü bozar | prompt hassasiyeti | prompt varyansı çalışmaları, format duyarlılığı |
| Benchmark etiketleri hatalı olabilir | veri kümesi etiket kalitesi | Northcutt ve ark. test kümesi etiket hataları; veri kümesi denetim yöntemleri |
| LLM-as-judge güvenilirliği sınırlı | yargılayıcı model geçerliliği | Zheng ve ark. LLM-as-a-judge; yargılayıcı yanlılıkları |
| Kodlayıcılar arası uyum ölçütü | κ ve yorumu | Cohen κ; Landis & Koch eşikleri; κ paradoksları |
| Hukuk alanında LLM değerlendirmesi | hukuki NLP benchmark'ları | LegalBench; hukuki soru-cevap değerlendirmeleri |
| Türkçe LLM değerlendirmesi | Türkçe NLP kaynakları | **DergiPark taraması şart** — Türkçe benchmark, Türkçe LLM değerlendirme |
| Mevzuat/uyum alanında yapay zekâ | inşaat & İSG'de AI | mevzuat uyumu otomasyonu, yapı denetimi bilişim |

### Aramada dikkat
1. **Türkçe literatür ayrı taranmalı.** DergiPark MCP bağlı; JESTECH Türk
   menşeli bir dergi ve yerel atıf beklentisi olabilir.
2. **Kendi önceki JESTECH yayınınıza** atıf, kapsam uyumunu göstermek için
   işe yarar.
3. **Negatif sonuçların literatürü zayıf** — model konsensüsünün etiket
   denetçisi olarak çalışmaması için doğrudan bir öncül bulamayabilirsiniz.
   Bu bir zayıflık değil, katkı gerekçesi.

---

## SONRAKİ OTURUMDA İLK ÜÇ İŞ

1. **Uzlaşı gelmişse** → `gecis2_uzlasi_isle.py` koş, 3.6'daki yer tutucuyu doldur.
2. **Bölüm 4.5'i revize et** — `HANDOVER.md` §2.4'teki üç düzeltmeye göre.
   Şu anki metinde ×7.5 ve "λ prompt-bağışık" ifadeleri **yanlış**.
3. **Kaynak taramasını başlat** — İlgili Çalışmalar bölümü buna bağlı ve
   tarama olmadan yazılamaz.
