# Görev promptu — JESTECH gönderimi öncesi üçlü denetim

> Bu dosya, makaleyi bağımsız bir okuyucuya/asistana değerlendirtmek için
> yazılmıştır. Aşağıdaki metnin tamamını görev olarak ver; yanına
> "Verilecek dosyalar" bölümündeki dosyaları ekle.

---

## BAĞLAM

Elindeki makale **Engineering Science and Technology, an International Journal**
(JESTECH, Elsevier, açık erişim, Q1) dergisine gönderilecek. Konusu: Türk yapı
denetimi ve iş güvenliği mevzuatı üzerinde çalışan dil-modeli tabanlı karar
destek yazılımının **kalifikasyonu** — yani "bu araca güvenilebilir mi, güvenin
şartı nedir, ne zaman yeniden sınanmalı" sorusu.

Makalenin merkezî iddiası şudur: bu sınıf araç için kabul ölçütü **doğruluk
olamaz**, çünkü doğruluk "bilmiyorum diyebilme" yetisini ölçmez. Bu yüzden her
iddia iki koşulda soruluyor: açık kaçınmaya izin veren (E1) ve ikili seçime
zorlayan (E2).

**Bu projenin selefi, temelsiz bir "kapsamlı" iddiası ve doğrulanmamış/kaymış
atıflar yüzünden reddedildi.** Bu yüzden aşağıdaki üç kural mutlaktır ve
görevinin tamamını yönetir:

1. **Hiçbir sayıyı uydurma, tahmin etme, yuvarlama.** Makaledeki her sayı
   `91_NUMBER_SHEET.txt` içinde bulunabilmelidir. Bulunmayan bir sayı görürsen
   bu bir bulgudur.
2. **Hiçbir atfı doğrulamadan önerme.** Önerdiğin her kaynağın DOI'sini gerçek
   bir kayıttan (Crossref, OpenAlex ya da yayıncı sayfası) teyit et. Teyit
   edemediğini **önerme** — "bulamadım" demek serbesttir ve tercih edilir.
3. **Emin olmadığın bulguyu kurma.** Sınırdaki vakaları otomatik çözme;
   `needs_human_review` diye işaretle ve kararı insana bırak.

Makale altı iç denetim turundan geçti; kolay hatalar temizlenmiş durumda.
Senden beklenen, **kalan zor hataları** bulmak.

---

## GÖREV 1 — EDİTÖR GÖZÜYLE DEĞERLENDİRME

Sen JESTECH'in yayın kurulu editörüsün. Masana gelen bir yazıyı hakeme
göndermeden önce eleyip elemeyeceğine karar veriyorsun. Şunları cevapla:

**1.1 Kapsam uyumu.** JESTECH kendini mühendislik bilimi ve teknolojisi dergisi
olarak tanımlıyor. Bu yazı derginin kapsamına giriyor mu, yoksa bir doğal dil
işleme / makine öğrenmesi makalesi mi? Kararını *makalenin kendi çerçevesine*
göre ver, konusuna göre değil: yazı kendini nasıl konumlandırıyor, bu
konumlandırma metnin geri kalanı tarafından destekleniyor mu?

**1.2 Masadan ret riski.** Bu yazıyı hakeme göndermeden reddetmen için hangi
gerekçeler olabilir? Her gerekçeyi metinden alıntıyla göster. Gerekçe yoksa
"yok" de.

**1.3 Biçimsel eksikler.** Elsevier/JESTECH gönderimi için gerekli olup
eksik ya da hatalı olan ne var? (Başlık sayfası, öz uzunluğu, anahtar kelimeler,
highlights karakter sınırı, çıkar çatışması beyanı, veri erişilebilirliği,
CRediT, üretken yapay zekâ kullanım beyanı, referans biçimi, şekil/tablo
gereksinimleri, kelime sayısı.) Elindeki dosyalarda ne olduğunu **kontrol et**,
varsayma.

**1.4 Başlık ve öz.** Başlık makalenin yaptığını doğru anlatıyor mu, fazla mı
söylüyor? Öz, mühendis okuyucuya ne vaat ediyor ve gövde bunu tutuyor mu?

**1.5 Karar.** Hakeme gönderir miydin? Gerekçesiyle: *masadan ret* / *büyük
revizyon isteyip gönder* / *doğrudan hakeme gönder*.

---

## GÖREV 2 — HAKEM GÖZÜYLE DEĞERLENDİRME (üç ayrı mercek)

Aynı yazıyı üç farklı hakem gibi ayrı ayrı oku. Merceği karıştırma.

**2.1 İnşaat / yapı denetimi mühendisi hakem.**
Makine öğrenmesi uzmanı değilsin. Sorular: Ölçülen şey senin işine yarıyor mu?
Sonuçlar bir yapı denetim kuruluşunun kararını değiştirir mi? Mevzuat
kullanımı doğru mu (3194, 4708, 6331, TBDY 2018, ilgili yönetmelikler)? Yazı
mühendislik pratiği hakkında yanlış bir şey söylüyor mu? Kabul eşiği
tartışması (§2.2, §5.6) sahada anlamlı mı?

**2.2 İstatistik / yöntem hakemi.**
Sorular: Güven aralıkları doğru kurulmuş mu (kümeli bootstrap, küme = kanun +
madde, 183 küme)? Eşli ve eşlenmemiş karşılaştırmalar doğru ayrılmış mı?
Bonferroni aileleri doğru tanımlanmış ve gerekçelendirilmiş mi? Sıfırı içeren
aralıklardan yön iddiası çıkarılıyor mu? Tek sınıflı tabakalarda dengeli
doğruluk yerine "altın sınıfı seçme oranı" kullanılması tutarlı mı? Ön kayıt
disiplini gerçek mi, süs mü — sapmalar beyan edilmiş mi ve sonuçları ölçülmüş
mü? Tekrarlanabilirlik iddiası ayakta mı?

**2.3 NLP / değerlendirme hakemi.**
Sorular: Kıyaslama tasarımı sağlam mı (prob aileleri gerçekten farklı hata
kiplerini ayırıyor mu)? Kaçınma ölçütleri literatürdeki seçici tahmin
çerçevesiyle uyumlu mu? Dayanaklı kollar (R1/R2/R3-BM25) doğru ablasyon mu?
"Sürüm kayması" bulgusu, iddia edilenden fazlasını söylüyor mu? Tek model
üzerinde koşulan dayanaklı merdivenin genellenebilirliği doğru sınırlandırılmış
mı?

**Her mercek için ayrı ayrı ver:** (a) en güçlü üç yön, (b) kabul için
düzeltilmesi ŞART olan kusurlar, (c) isteğe bağlı iyileştirmeler,
(d) tavsiyen (*kabul* / *küçük revizyon* / *büyük revizyon* / *ret*).

---

## GÖREV 3 — ATIF DENETİMİ (iki yönlü, tam)

`01_MANUSCRIPT.md` içindeki **Kaynakça** bölümünde 18 künye var
(17 makale + IEC 61508 standardı). `90_REF_VERIFICATION_RECORD.md` bunların
daha önce OpenAlex'e karşı doğrulandığını iddia ediyor. **O kaydı veri kabul
etme, kendin yeniden doğrula.**

**3.1 Künye doğruluğu.** Her künye için gerçek kayda bak ve şunları karşılaştır:
yazar soyadları, yıl, başlık, dergi/konferans adı, DOI ya da arXiv numarası.
Aşağıdaki tabloyu doldur:

| # | künye (taslaktaki hâli) | DOI/arXiv | yıl doğru mu | başlık doğru mu | dergi doğru mu | HÜKÜM |
|---|---|---|---|---|---|---|

HÜKÜM: `DOĞRULANDI` / `DÜZELTİLECEK (ne)` / `BULUNAMADI`.
Bir künyeyi doğrulayamıyorsan **uydurma**, `BULUNAMADI` yaz.

**3.2 Metin içi atıflar.** Gövdedeki her `(Yazar, yıl)` göndermesini tek tek
kontrol et:
- Gönderme kaynakçada var mı? (yetim atıf)
- Kaynakçadaki her künye gövdede en az bir kez anılıyor mu? (anılmayan künye)
- **Atfın söylediği şeyi o kaynak gerçekten söylüyor mu?** Bu en önemli
  maddedir. Cümlenin iddiası ile kaynağın içeriği uyuşmuyorsa bu bir *atıf
  kayması*dır ve selefi reddettiren kusurun ta kendisidir. Şüphelendiğin her
  atıf için kaynağın özetini oku ve cümleyle karşılaştır.

**3.3 Aşırı/eksik atıf.** Atıf gerektiren ama atıfsız kalmış iddia var mı?
Özellikle §1'in ilgili çalışma paragrafını ve §2.1'in seçici tahmin
soyağacını denetle.

---

## GÖREV 4 — HEDEF DERGİDEN BENZER YAYIN BULMA

JESTECH'te yayımlanmış, bu makaleyle **gerçekten ilgili** çalışmalar bul ve
atıf önerisi yap. Amaç iki yönlü: (a) makalenin derginin kendi literatürüne
bağlanması, (b) editöre kapsam uyumunun gösterilmesi.

**4.1 Arama.** JESTECH'in ISSN'i **2215-0986**. Crossref ya da OpenAlex'te
dergiyi ISSN ile filtreleyip şu temalarda ara:
- otomatik mevzuat/yönetmelik uyum denetimi, yapı denetimi
- inşaat mühendisliğinde karar destek sistemleri
- yapı/deprem yönetmeliği uygulamaları (TBDY, sismik tasarım)
- iş sağlığı ve güvenliği risk değerlendirmesi, otomasyon
- mühendislikte büyük dil modeli / doğal dil işleme uygulamaları
- güvenilirlik, doğrulama-geçerleme (V&V), yazılım kalifikasyonu
- belirsizlik kestirimi, kalibrasyon, güvenilir yapay zekâ

**4.2 Eleme.** Bulduğun her aday için sor: *bu makalede hangi cümleye,
hangi gerekçeyle atıf verilir?* Sadece "aynı dergide yayımlandı" diye atıf
önerme — bu editöre sırıtır ve zarar verir. İlgisi zayıf olanı ele.

**4.3 Çıktı.** Her öneri için:

| künye (tam) | DOI | JESTECH mi (ISSN teyidi) | makalenin HANGİ cümlesine | önerilen atıf cümlesi | gerekçe |
|---|---|---|---|---|---|

**En fazla 6 öneri ver.** Az ve isabetli olsun. Hiçbiri isabetli değilse
"JESTECH'te doğrudan ilgili yayın bulunamadı" demek geçerli ve dürüst bir
cevaptır — o zaman en yakın 2-3 tanesini "zayıf ilgi" etiketiyle listele ve
atıf ÖNERME.

**4.4 Uyarı.** Bu maddede uydurma riski en yüksektir. Bir künyeyi
doğrulayamıyorsan listeleme. DOI'siz öneri kabul edilmez.

---

## ÇIKTI BİÇİMİ

Tek bir belge üret, şu başlıklarla:

1. **YÖNETİCİ ÖZETİ** — 10 satırı geçmeyecek. Gönderilebilir mi, en büyük risk ne?
2. **EDİTÖR DEĞERLENDİRMESİ** (Görev 1)
3. **HAKEM 1 — İNŞAAT MÜHENDİSİ** (Görev 2.1)
4. **HAKEM 2 — İSTATİSTİK/YÖNTEM** (Görev 2.2)
5. **HAKEM 3 — NLP/DEĞERLENDİRME** (Görev 2.3)
6. **ATIF DENETİMİ** (Görev 3) — tablolarla
7. **JESTECH ATIF ÖNERİLERİ** (Görev 4) — tabloyla
8. **BLOKE EDİCİ KUSURLAR** — gönderimden önce mutlaka düzeltilmesi gerekenler,
   önem sırasıyla, her biri için dosya + satır + alıntı + ne yazılmalı
9. **DOĞRULAYAMADIKLARIM** — kontrol etmek isteyip edemediğin her şey. Bu bölüm
   boş bırakılmaz; boşsa "yok" yaz ve nedenini açıkla.

Her bulguda **alıntı ver**. Alıntısız bulgu kabul edilmez.

---

## SANA YASAK OLANLAR

- Doğrulamadığın bir künyeyi önermek
- `91_NUMBER_SHEET.txt` içinde olmayan bir sayıyı makaleye önermek
- "Şunu da eklerseniz iyi olur" tarzı, kanıtsız genel tavsiye
- Sınırdaki bir vakayı kendi başına karara bağlamak
- Makalenin dilini "daha iddialı" yapmayı önermek — bu makale bilerek
  ihtiyatlıdır ve ihtiyat onun savunulabilirliğinin kaynağıdır
