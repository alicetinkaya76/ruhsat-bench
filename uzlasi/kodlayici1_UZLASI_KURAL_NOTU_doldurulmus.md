# RUHSAT-Bench — UZLAŞI KURAL NOTU

**Doldurulma sırası: BU BELGE ÖNCE. Maddeler sonra.**

Kitapta iki ayrı karar türü var ve karıştırılmamalı:

| sayfa | n | ne gerekir |
|---|---|---|
| **TANIM** | 5 | **Bu kural notu.** Etiketin ne anlama geldiğine dair tanım sorusu. |
| **OLGU** | 7 | Kural gerekmez. İki metni karşılaştırıp teyit yeter. |

Bu belge yalnızca **TANIM** sayfası içindir. OLGU sayfası bağımsız
doldurulabilir ve kuralı beklemez.

İkinci geçişteki altı uyuşmazlıktan biri (`364`) korpus taramasıyla
olgusal olarak çözüldü ve OLGU sayfasına taşındı. Ayrıntı:
`sonuclar/F4_on_kayit_ek5.txt`.

---

## 1. Karara bağlanacak soru

> Kaynak metinde birebir geçen bir cümle, uygulanma koşulundan veya
> anlamını taşıyan bağlamından koparılarak iddia hâline getirildiğinde,
> bu iddia **DOĞRU** mudur **YANLIŞ** mıdır?

Beş madde iki olguya ayrılıyor.

**(A) Kapsam koşulu düşürülmüş** — cümle kaynakta belirli bir kapsam
altında geçiyor, iddia genel kural gibi sunuyor.

- `115` TBDY 17.2.4 — 30 m / oran 4 sınırları Bölüm 17 kapsamındaki
  binalar için (BKS=3, basitleştirilmiş tasarım)
- `122` TBDY 2.5.2.1 — aynı ölçek katsayısı şartı 2.5.2.1(b)'deki üç
  boyutlu hesaba ait
- `315` TBDY 15.2.4.2 — varsayım sınırlı bilgi düzeyi kapsamında

**(B) Anafora çözülmemiş** — cümle önceki cümleye geri gönderme yapan
bir ifade içeriyor; iddiada öncül yok.

- `213` "dinamik kuvvet" = önceki cümlede tanımlanan dinamik toprak
  basıncı bileşkesi
- `417` "bu paralar" = önceki fıkrada sözü edilen tahsilatlar

---

## 2. Gözden kaçmış eksen: iddia atıf taşıyor mu

| kod | olgu | atıf | iddianın açılışı |
|---|---|---|---|
| 115 | kapsam | **var** | "TBDY 2018'in 17.2.4 numaralı bendine göre…" |
| 122 | kapsam | **var** | "TBDY 2018'in 2.5.2.1 numaralı bendine göre…" |
| 213 | anafora | **var** | "TBDY 2018'in 16.12.2.8 numaralı bendine göre…" |
| 315 | kapsam | **yok** | "TBDY 2018'e göre…" |
| 417 | anafora | **yok** | "3194 sayılı Kanun'a göre…" |

Ayrım maddi: **atıf varsa** okur kapsamı getirilebilir bir yerde bulur ve
iddia "şu bent şunu söyler" biçiminde okunur. **Atıf yoksa** iddia tek
başına duran bir önerme hâline gelir, dayandığı koşul hiçbir yerde
görünmez.

Korpus taraması belirsizlik olmadığını doğruladı: `315`'in cümlesi yalnız
15.2.4.2'de, `417`'ninki yalnız 3194/23'te geçiyor. "Hangi hükümden
bahsediyor" sorusu yok; soru saf haliyle tanım sorusu.

---

## 3. Seçenekler

### Seçenek 1 — Metinsel varlık yeter
Cümle kaynakta birebir geçiyorsa iddia DOĞRU'dur. Kapsam ve anafora
okurun sorumluluğundadır.
→ Beşi de DOĞRU. Altın değişmez.

### Seçenek 2 — Koşuldan koparma yanlıştır
Uygulanma koşulu düşürülmüş veya öncülü olmayan anaforik ifade taşıyan
iddia YANLIŞ'tır; birebir alıntı olması durumu değiştirmez.
→ Beşi de YANLIŞ. Beş altın döner.

### Seçenek 3 — Atıf ayrımı yapılır
Belirli birime atıf yapan iddia DOĞRU (kapsam getirilebilir); atıfsız
iddia YANLIŞ (önerme tek başına doğru değil).
→ 115, 122, 213 DOĞRU; 315, 417 YANLIŞ. İki altın döner.

### Seçenek 4 — Çerçeve dışı
Bu maddeler DOĞRU/YANLIŞ ikilisiyle sorulacak biçimde kurulmamıştır;
kümeden çıkarılır.
→ Beş madde düşer, n azalır, etiket zorlanmaz.

---

## 4. Kararın ne etkilediğini bilerek seçin

Beşi de `P1_dogrudan` ve λ = doğruluk(P1) + doğruluk(P5) − 1, yani
makalenin ana metriğinin yarısı P1'e dayanıyor.

Ölçek ise küçük: 473 maddede en fazla beş etiket, %1'in biraz üstü.
Hangi seçenek seçilirse seçilsin niteliksel sonucun değişmesi
beklenmiyor. **Bu bir rahatlatıcıdır, gerekçe değildir.**

Hangi seçeneğin kaç etiketi çevirdiği yukarıda yazıyor; bu bilgiyi
gizlemek mümkün değil. Şart şu: gerekçe *"koşuldan koparılmış bir cümle
ne anlama gelir"* sorusuna cevap versin, *"hangisi daha iyi sonuç
verir"* sorusuna değil.

Seçim ne olursa olsun makalede duyarlılık analizi verilecek: orijinal ve
uzlaşı sonrası etiketlerle hesaplanmış iki sonuç yan yana.

---

## 5. Kural metni

**Seçilen seçenek:** ☐ 1 ☐ 2 ☒ 3 ☐ 4 ☐ diğer

**Kuralın tam ifadesi:**

> Bir bent ya da madde numarasına açıkça atıf yapan iddia, cümle o
> birimde aynen geçiyor ve eksik bırakılan kapsam koşulu veya anaforik
> öncül aynı birimin yakın bağlamından açıkça tamamlanabiliyorsa
> **DOĞRU** kabul edilir. Yalnız belgeye atıf yapan ya da belirli birim
> atfı taşımayan iddiada uygulanma koşulu veya anaforik öncül çıkarılmışsa
> ve önerme bu hâliyle genelleşiyor ya da belirsiz kalıyorsa **YANLIŞ**
> kabul edilir.

**Gerekçe (ilkeye dayalı, madde sonuçlarına değil):**

> Bent numarası verilen iddialarda okur, cümlenin bağlı olduğu koşulu
> veya öncülü aynı yerde görebilir. Yalnız belge adı verilen iddialarda
> ise eksik bırakılan unsur geri getirilemez; cümle tek başına
> genelleşir ya da belirsiz kalır. Ayrım, sonuç dağılımına değil iddianın
> kendi hâliyle denetlenebilir olmasına dayanır.

**Kapsam koşulu ile anafora aynı muameleyi görecek mi?** ☒ evet ☐ hayır

Her ikisinde de ölçüt, eksik unsurun iddiadaki açık birim atfından geri
getirilebilir olup olmamasıdır.

| | ad | tarih | imza |
|---|---|---|---|
| İnşaat mühendisi |  | 02.08.2026 |  |
| İSG uzmanı |  | 02.08.2026 |  |

---

## 6. Bundan sonra

1. Bu belge imzalanır, `sonuclar/` altına konur, git'e işlenir.
2. Kitabın TANIM sayfası açılır, `UZLASI` sütunu doldurulur.
3. Bir satırın kararı kuralla çelişiyorsa kural eksiktir. Satırı
   zorlamayın; kuralı revize edin, revizyonu tarihiyle kaydedin.
   Kayda geçmiş revizyon sorun değildir; kayda geçmemiş olan sorundur.
4. OLGU sayfası ayrıca doldurulur (bkz. kılavuz).
5. `gecis2_uzlasi_isle.py` çalıştırılır; çıkan iki sayı Bölüm 3.6'daki
   yer tutucuyu doldurur.
