# 17 açık vaka — kararlar ve BAĞIMSIZ DOĞRULAMA
**Tarih:** 2026-08-29

## 1. PROVENANS UYARISI — ÖNCE BU OKUNMALI

Doldurulmuş kitapta `KODLAYICI` alanı **"GPT-5.6 Pro"** yazıyor; yani bu 17 karar
bir **dil modeli** tarafından verilmiştir, insan uzman tarafından değil.

Bu, kararların ne olduğunu değiştirir:

* Makalenin altın etiket bölümü iki **insan** kodlayıcıya ve ölçülmüş κ değerlerine
  dayanıyor (KARAR κ=1.000, KALİTE κ=0.860, n=150). Bu 17 karar o zincirin
  parçası **değildir**.
* Bu çalışma LLM'lerin Türk mevzuatını yargılama yetisini ölçüyor. Altın
  etiketlerin bir kısmını bir LLM koyarsa, o maddelerde ölçülen şey kısmen
  "başka bir LLM ile uyuşma" olur — **dairesellik**.

Bu belge kararları **kayda geçirir ve içeriklerini bağımsız olarak doğrular**,
ama onları uzman kararı olarak **ilan etmez**. İnsan onayı gelene kadar bu 4
etiket değişikliği duyarlılık kolu olarak tutulmalıdır.

## 2. Karar dağılımı

| sayfa | satır | karar |
|---|---|---|
| 2_ONAY_YETER | 13 | hepsi `onay` (değişiklik yok) — bu satırlar altını DEĞİŞTİRMİYOR |
| 3_KARAR_GEREK | 4 | 3 × `altin_YANLIS_yap`, 1 × `degisiklik_yok` |

## 3. Dört kararın BAĞIMSIZ doğrulaması

Aşağıdaki kanıt asistan tarafından, kararı veren modelden bağımsız olarak,
`data/korpus_v2/korpus.jsonl` üzerinde dizgi sayımıyla toplanmıştır.

| id | karar | gerekçenin sınanabilir çekirdeği | ÖLÇÜM | hüküm |
|---|---|---|---|---|
| **323** | değişiklik yok | 16.11.1 Tablo 16.6'ya gönderme yapıyor | 16.11.1 metni harfiyen: *"...zemin basınçları ( )p Tablo 16.6'da tanımlanmıştır"* | **DESTEKLENİYOR** — alıntının 16.6'da bulunması atıftır, yanlış isnat değil |
| **278** | altın YANLIŞ | %15 düşey rijitlik koşulu 14.15.4'te | "%15" → 14.5'te **0**, 14.15.4'te **2** geçiş | **DESTEKLENİYOR** |
| **426** | altın YANLIŞ | bilgi düzeyi sınıflandırması 15.2.2'de | "bilgi düzeyi" → 15.2.1.3'te **0**, 15.2.2'de **2** geçiş | **DESTEKLENİYOR** |
| **444** | altın YANLIŞ | katsayılara bölünmeme kuralı 15.2.12'de | "katsayı/bölünme" → 15.2.11.3'te **0**, 15.2.12'de **4** geçiş | **DESTEKLENİYOR** |

Dördü de metinsel kanıtla tutarlıdır. **Sorun kararların isabeti değil,
provenansıdır.**

## 4. İnsan onayı için gereken

Yukarıdaki tablo, onaylayacak kişinin işini "metinleri karşılaştır"dan
"dört satırı oku ve katılıyorsan imzala"ya indirir. Onay gelirse:

1. `uzlasi/ACIK_17_VAKA_karar_kitabi_DOLDURULDU.xlsx` içindeki `KODLAYICI`
   alanı insan adıyla güncellenir,
2. v7a'dan v7c üretilir (3 etiket DOĞRU→YANLIŞ: 278, 426, 444),
3. R3 ve bütün hücreler v7c ile yeniden puanlanır,
4. Makale sayı çizelgesi güncellenir.

Onay gelmezse bu 3 değişiklik **duyarlılık kolu** olarak raporlanır ve birincil
altın v7a olarak kalır.
