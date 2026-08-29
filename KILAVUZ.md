# Ali için kılavuz — ne yapacaksın, hangi sırayla

**29 Ağustos 2026.** Bu belge taraflıdır: seçenek sunmuyor, ne yapman gerektiğini
söylüyor. Gerekçeler ölçümlere dayanıyor, dosya adları verili. Katılmadığın yerde
tersini yap — ama o zaman bilerek yapmış olursun.

---

## SIRA 1 — İmzalar. Artık tek engel bu.

**Dosya:** `uzlasi/IMZA_SAYFASI_v7a.md`

**17 vaka kapandı ve sonuç: hiçbiri etiket değişikliği gerektirmiyor.** İmza
sayfası kodlayıcılara *"v7a şimdi mi donsun, önce 17 vaka mı çözülsün"* diye
soruyordu — o sorunun cevabı artık net: **çözüldü, v7a şimdi dondurulabilir.**

Kodlayıcılara iletilmesi gereken bir düzeltme var: 29 Ağustos'ta üç iddia
(278, 426, 444) için "altını YANLIŞ yap" kararı verilmişti, ben o kararları
**geri aldım**. Sebep kendi yargılarında değil, benim tarif ettiğim görevde:
karar kitabında CSV'nin `madde` sütununu iddianın atıf yaptığı yer gibi
sunmuştum. EK-4 §2 tersini söylüyor — o sütun metnin **kaynağını** tutar.
Üç iddia da *"TBDY 2018'e göre..."* diyor, yani **belge düzeyinde** atıf
yapıyor; içerikleri TBDY'de var, sadece başka maddede. EK-4 §9(d) böyle
atıfları belgenin tamamında arar, dolayısıyla iddialar doğrudur.

Bu hatayı **R3 yakaladı**: kural tabanlı taban v7a ile 473/473 verirken
değiştirilmiş altınla 470/473'e düştü ve uyuşmadığı üç id tam olarak bunlardı.

Ayrıca 323 için verilen `degisiklik_yok` kararı **doğruydu** ve duruyor.

**Not — provenans:** doldurulan kitapta `KODLAYICI` alanı "GPT-5.6 Pro"
yazıyordu. İnsan onayı sonradan alındı ama artık bir etiket değişikliği
kalmadığı için bu konu makaleyi etkilemiyor: v7a değişmedi.

## SIRA 2 — Taslağı oku. Ama sadece çerçeveyi.

**Dosya:** `makale/RUHSAT_JESTECH_taslak_tur4.md` (en güncel)

Dört tur denetimden geçti. **Mühendis hakem 4. turda "artık gönderirdim" dedi**;
bilimsel içerikte kalan red gerekçesi yok. Kalan işler biçimsel ve bende. Senden istediğim tek şey **çerçeve onayı**. İki karara bak:

1. **Vargı değişti.** Makale artık "hiçbir şey çalışmıyor" demiyor. Ölçtüğümüz şu:
   kapalı kitapta `qwen2.5:32b` E2'de 0.5493 (şans), ama **yöneten madde
   verildiğinde 0.8615**. Yani makalenin tavsiyesi *"bu araçları kullanma"* değil,
   ***"kapalı kitap kurma, maddeyi getir"***. Bu, mühendislik dergisi için
   dağıtılabilir bir sonuç. Katılıyor musun?

2. **Manşet bulgu sürüm kayması.** Aynı model adı, aynı bütçe, aynı istem, farklı
   tarih → kaçınmanın seçiciliği düştü, **ve bu zorunlu seçim ölçümüyle görünmüyor**.
   Mühendislik diliyle: doğruladığın araç sessizce değişti. Bunu manşet yapmayı
   öneriyorum çünkü mühendis okuyucu kalifikasyon kavramını bilir.

Yöntem ve Bulgular bölümlerini okumana gerek yok, sayıları ben denetletiyorum.

---

## SIRA 3 — JESTECH'e gönder. Kapak mektubunda şunu yaz.

Bu makalenin **tek gerçek red riski** şu: mühendis hakem *"bu bir NLP makalesi,
yanlış dergiye gelmiş"* der. Denetimde bunu açıkça sorduk ve ilk turda hakem
"göndermezdim" dedi; ikinci turda çerçeve düzelince fikrini değiştirdi.

Kapak mektubu bu itirazı **önden karşılamalı**. Öneri:

> Bu çalışma bir dil modeli araştırması değil, Türk yapı denetimi mevzuatı üzerinde
> karar-destek yazılımının **kalifikasyonuna** dair bir ölçümdür. Bulgularımızdan
> biri, aynı ticari model sürümünün altı ay arayla aynı kıyaslama kümesinde farklı
> davrandığı ve bu değişimin standart doğruluk ölçümüyle görünmediğidir. Mühendislik
> pratiğinde bu, doğrulanmış bir aracın bildirimsiz değişmesine karşılık gelir.

Selef makale *"comprehensive"* iddiası yüzünden reddedilmişti. Bu taslakta o sınıfta
tek bir sıfat yok; denetim bunu iki kez taradı.

---

## YAPMANA GEREK OLMAYANLAR (bunlar bitti)

| iş | durum |
|---|---|
| `frontCA32_bugun` API koşusu | ✅ koşuldu, hüküm: sürüm kayması |
| P6 mevzuat.gov.tr doğrulaması | ✅ 20/20 uyuştu |
| F5 dayanaklı kollar (R1/R2/R3bm25) | ✅ koşuldu, 3 tekrar + çoğunluk oyu |
| Atıfların doğrulanması | ✅ 17 atıf sorgulandı, 3 yıl kayması bulundu |
| TF-HPC kurulumu, Ollama | ✅ 17/17 kabul testi geçti |

---

## BENİM SIRADAKİ İŞİM (sen beklemiyorsun)

Beşinci ve son tur. İçindekiler:

* **Ön-kayıtlı birincil hipotezler H1/H2 metne girecek** — hesaplandı, dördü de
  sıfırı dışlıyor. Bunlar EK-4 §4'ün birincil ailesi ve makalede hiç yoktu.
* **Bonferroni ailesi düzeltmesi** — kaçınma kontrastına yanlış aile (Bonferroni-2)
  uygulanmıştı; doğrusu 17 model üzerinden. Sonuç ayakta ama kıl payı: Sonnet
  +0.0678, [+0.0018, +0.1343].
* **Δ aralıkları** — hesaplandı ve bir iddiamı zayıflattı: Δ ekseninde bugün ile
  arşiv ayırt edilemiyor. Sürüm kayması bulgusu BAcc-farkına dayanıyor.
* **EK-6'nın zorunlu tuttuğu ham korpus (1366) duyarlılık kolu** — TF-HPC'de
  koşuyor, ~3 saat. Ön-kayıtta söz verip yapmadığım işti.
* Küçükler: §5.4'teki "aralıklar değiyor" hatası (ayrıklar), EK-7 karar kuralının
  metne yazılması, λ'nın tek tanımı, A_nc/A_abs gösterimi, kaynakça künyeleri,
  Abstract/Keywords/yazar bloğu.

## SANA TARAFLI İKİ TAVSİYE DAHA

**`gemma3:27b` dayanaklı kolunu koşturma.** Yarıda kestim ve iyi ettim. Bir model
(qwen2.5:32b, 3 tekrar, kesilen 0/1524) makalenin ihtiyacı olan her şeyi veriyor.
İkinci model 8 saat daha götürür ve hiçbir hakem sorusunu cevaplamaz.

**Zhang & El-Gohary atfını kovalama.** Taslakta 2016 yazıyor ama tarif edilen çalışma
2013. Doğru 2016 makalesini aramak yerine **2013'ü doğru künyeyle kullan ya da atfı
tamamen çıkar**. O cümle atıfsız da ayakta duruyor.
