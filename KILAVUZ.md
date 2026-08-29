# Ali için kılavuz — ne yapacaksın, hangi sırayla

**29 Ağustos 2026.** Bu belge taraflıdır: seçenek sunmuyor, ne yapman gerektiğini
söylüyor. Gerekçeler ölçümlere dayanıyor, dosya adları verili. Katılmadığın yerde
tersini yap — ama o zaman bilerek yapmış olursun.

---

## SIRA 1 — 17 vakayı çöz. İmzalardan ÖNCE.

**Dosya:** `uzlasi/ACIK_17_VAKA_karar_kitabi.xlsx`

**Neden önce bu:** Bu 17'nin **12'si**, uzmanların zaten düzelttiği bir iddiayla
**birebir aynı korpus kaymasını** paylaşıyor. Örnek: `TBDY/7.2.1.4 → 7.2.4`
kaymasındaki 5 iddiadan 2'si (304, 382) düzeltilmiş, 3'ü (25, 123, 211) değil.

Bir hakem bunu görürse soracağı soru şu: *"Aynı kaymada iki iddiayı düzeltip üçünü
neden bırakmışsınız?"* Cevabın yoksa bu, altın etiketlerin tutarsız olduğu anlamına
gelir ve makalenin dayanağını yıkar.

**Benim önerim** (kitapta satır satır gerekçesiyle var): düzeltilmiş bir iddiayla
aynı kaymayı paylaşan 12'sinde **aynı kararı uygula**. Kalan 5'i ayrı bak — onlar
hiç düzeltme almamış kaymalarda ve gerçekten tek tek değerlendirme istiyor.

**Süre:** 12'si mekanik (tutarlılık kararı), 5'i düşünmek gerektirir. Bir oturum.

---

## SIRA 2 — İmzaları al. Ama 17'den sonra.

**Dosya:** `uzlasi/IMZA_SAYFASI_v7a.md`

İmza sayfası kodlayıcılara şunu soruyor: *"v7a şimdi mi donsun, önce 17 vaka mı
çözülsün?"* Sıra 1'i yaparsan bu soru kendiliğinden cevaplanmış olur ve imza tek
turda alınır. Ters sırada yaparsan iki kez imza toplarsın.

**Ben imza atamam.** Kodlayıcı adına imza, olmayan bir insan beyanı üretmek olur —
ve makalenin altın etiketlerinin dayandığı şey tam olarak o beyandır.

---

## SIRA 3 — Taslağı oku. Ama sadece çerçeveyi.

**Dosya:** `makale/RUHSAT_JESTECH_taslak_tur2.md`

**Bu taslak gönderilemez** ve sayılarında bilinen hatalar var — onları ben
düzelteceğim. Senden istediğim tek şey **çerçeve onayı**. İki karara bak:

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

## SIRA 4 — JESTECH'e gönder. Kapak mektubunda şunu yaz.

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

Üçüncü tur yazım: Δ'nın **keşifsel** diye etiketlenmesi (ön-kayıtlı değil, ben yanlış
söylemiştim), Bonferroni manşeti (4 model değil **2**), kapsam-eşiği iddiasının
kaldırılması, ön-kayıt sapmasının beyanı, F5 sonuçlarının girmesi, üç atıf yılının
düzeltilmesi, 17 vaka için gerekçeli öneriler.

---

## SANA TARAFLI İKİ TAVSİYE DAHA

**`gemma3:27b` dayanaklı kolunu koşturma.** Yarıda kestim ve iyi ettim. Bir model
(qwen2.5:32b, 3 tekrar, kesilen 0/1524) makalenin ihtiyacı olan her şeyi veriyor.
İkinci model 8 saat daha götürür ve hiçbir hakem sorusunu cevaplamaz.

**Zhang & El-Gohary atfını kovalama.** Taslakta 2016 yazıyor ama tarif edilen çalışma
2013. Doğru 2016 makalesini aramak yerine **2013'ü doğru künyeyle kullan ya da atfı
tamamen çıkar**. O cümle atıfsız da ayakta duruyor.
