# UZLAŞI KILAVUZU — RUHSAT-Bench

Toplam 12 madde, iki farklı karar türü. Tahmini süre: **TANIM** için
45–60 dakika birlikte, **OLGU** için 20–30 dakika.

---

## Kitabın yapısı

`data\iddialar\uzlasi_kitabi.xlsx` — dört sayfa:

| sayfa | n | karar türü |
|---|---|---|
| **KURAL** | — | önce doldurulur, TANIM sayfası için |
| **TANIM** | 5 | tanım sorusu — kural gerektirir |
| **OLGU** | 7 | olgu sorusu — iki metni karşılaştırıp teyit |
| **KONTROLLER** | 2 | **dokunulmaz** |

İkisi bağımsız. OLGU sayfası kuralı beklemeden doldurulabilir.

---

## A. TANIM sayfası (5 madde)

### Neden özel bir protokol

Bu maddelerde iki uzman **aynı yönde** ayrıştı: inşaat mühendisi YANLIŞ,
İSG uzmanı DOĞRU. Tek yönlü bir örüntü ölçüm gürültüsü değildir; iki
uzman etiketin ne anlama geldiğine dair farklı bir ölçüt kullanıyor.

Sonucu: ortalama almak, oy çokluğu aramak veya üçüncü bir hakem getirmek
işe yaramaz. Ölçüt yazılmadan madde açılırsa, ölçüt maddelere bakılarak
seçilmiş olur ve denetim bağımsızlığını kaybeder.

### Sıra

**1. Kural — birlikte, maddeler kapalı.**
`UZLASI_KURAL_NOTU.md` açılır. Orada beş maddenin olgu türleri ve atıf
durumu özetlenmiştir; iddia metinleri ve kimin ne dediği o belgede
yoktur, çünkü kural onlara bakılmadan yazılmalıdır. Dört seçenekten biri
seçilir veya kendi ifadeniz yazılır, gerekçe ilkeye dayalı kaydedilir,
iki taraf imzalar. Kitabın KURAL sayfasına da geçirilir.

**2. Maddeler.** TANIM sayfası açılır. `UZLASI` sütunu: `DOGRU`,
`YANLIS` veya `CERCEVE_DISI`. `UZLASI_GEREKCE`: kararın kuralın hangi
maddesinden çıktığı.

Her satırda iddia metni, altın etiket, iki uzmanın kararı ve gerekçesi,
iddianın atıf yaptığı birim, o birimin **korpustan tam metni**, ve
cümlenin korpusta gerçekte nerede geçtiği var.

---

## B. OLGU sayfası (7 madde)

### Bunlar tanım sorusu değil

Korpus taraması, TBDY ayrıştırıcısında bir kusur buldu: bazı bent
başlıkları sınır olarak tanınmamış, o bentlerin metni bir önceki bendin
gövdesine yığılmış. Sonuç olarak üreteç bazı cümleleri **yanlış bende**
atfetmiş.

Bu, ikinci geçişte `364` maddesinde inşaat mühendisinin elle yakaladığı
şeyin ta kendisi. Tarama aynı hatanın altı örneğini daha buldu.

### Sizden istenen tek şey

Her satırda iki metin yan yana: **kayıtlı bendin metni** ve **gerçek
bendin metni**. İddianın içeriği hangisinde geçiyor, bakın.

İddia bendi açıkça söylüyor ("… 2.1.2 numaralı bendine göre …") ve içerik
o bentte değilse, iddia yanlıştır. Bu, `P5_capraz` probunun kasten
ürettiği hatanın aynısı — sadece bu kez kazara olmuş.

`TEYIT` sütunu: `ONAY`, `RET` veya `KARARSIZ`.
`ONAY` → altın DOĞRU'dan YANLIŞ'a döner.
`RET` → değişmez; gerekçesini yazın.

**Kural gerekmez.** Bu bir tanım tartışması değil, iki metnin
karşılaştırılması.

### Kapsam dışı

Tarama beş madde daha buldu ama onlarda iddia bent belirtmiyor
("TBDY 2018'e göre…"). İçerik TBDY'de gerçekten var, sadece kayıttaki
bentte değil — yani iddia doğru, düzeltilecek olan kaynak kaydı. Bunlar
sizin sayfanızda yok.

---

## Kontrol maddeleri

`K291` ve `K378` ekilmiş kontrollerdir; doğru cevapları tasarım gereği
bilinir ve uzlaşıya girmezler. Denetimin **duyarlılığını** ölçmek için
oradalar — uzlaşıya sokulurlarsa o ölçü yok olur.

`K291`'de inşaat mühendisi ekilmiş hatayı yakaladı, İSG uzmanı
yakalamadı. Bu bir başarısızlık kaydı değil, denetim yönteminin ne kadar
hassas olduğunun ölçüsü ve makalede öyle raporlanacak.

---

## Sık sorulan

**"İkimiz de fikir değiştirmezsek?"**
TANIM'da kural karar veriyor, kişiler değil. Kural yazıldıktan sonra iki
taraf da aynı kuralı aynı maddeye uygulayıp aynı sonuca varmalı.
Varamıyorsa kural belirsizdir; netleştirin.

**"Altın etiketi değiştirmek veriyi bozmaz mı?"**
Hayır. Makalede iki sonuç yan yana verilecek: orijinal etiketlerle ve
uzlaşı sonrası etiketlerle. Değişimin kendisi bir bulgu.

**"CERCEVE_DISI ne zaman kullanılır?"**
İddia DOĞRU/YANLIŞ ikilisiyle sorulacak biçimde kurulmamışsa. O madde
kümeden düşer, n azalır, etiket zorlanmamış olur. Meşru bir sonuçtur;
sık kullanılırsa üretim şablonunda sorun var demektir ve bu da rapor
edilir.

**"Bu düzeltmeler sonucu ne kadar değiştiriyor?"**
473 maddede en fazla 12 etiket, yani %2,5. Niteliksel sonucun değişmesi
beklenmiyor. Amaç sonucu kurtarmak değil, kaydın doğru olması.

---

## İşleme (araştırmacı tarafı)

```powershell
python scripts\gecis2_uzlasi_isle.py --dosyalar data\iddialar\uzlasi_kitabi.xlsx
```
