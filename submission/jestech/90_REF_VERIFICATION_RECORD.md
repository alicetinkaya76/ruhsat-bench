# Atıf doğrulama — RUHSAT-Bench (JESTECH taslağı)

**Tarih:** 2026-08-29 · **Kaynak:** OpenAlex API (`api.openalex.org`), tarayıcı üzerinden

> Selef makale kısmen **doğrulanmamış ve kaymış atıflar** yüzünden reddedildi.
> Taslaktaki her atıf tek tek sorgulandı. Aşağıdaki künyeler OpenAlex kaydından
> alınmıştır; doğrulanmayan hiçbir atıf makaleye girmez.

## Doğrulandı — künye ve yıl doğru (13)

| atıf | tam künye | DOI |
|---|---|---|
| Chow 1970 | On optimum recognition error and reject tradeoff. *IEEE Trans. Inf. Theory* | 10.1109/tit.1970.1054406 |
| Eastman et al. 2009 | Automatic rule-based checking of building designs. *Automation in Construction* | 10.1016/j.autcon.2009.07.002 |
| Solihin & Eastman 2015 | Classification of rules for automated BIM rule checking development. *Automation in Construction* | 10.1016/j.autcon.2015.03.003 |
| El-Yaniv & Wiener 2010 | On the Foundations of Noise-free Selective Classification. *JMLR* | 10.5555/1756006.1859904 |
| Naeini et al. 2015 | Obtaining Well Calibrated Probabilities Using Bayesian Binning. *AAAI* | 10.1609/aaai.v29i1.9602 |
| Guo et al. 2017 | On Calibration of Modern Neural Networks. *ICML* | arXiv 1706.04599 |
| Geifman & El-Yaniv 2017 | Selective Classification for Deep Neural Networks | arXiv 1705.08500 |
| Robertson & Zaragoza 2009 | The Probabilistic Relevance Framework: BM25 and Beyond. *FnTIR* | 10.1561/1500000019 |
| Jiang et al. 2021 | How Can We Know When Language Models Know? *TACL* | 10.1162/tacl_a_00407 |
| Kadavath et al. 2022 | Language Models (Mostly) Know What They Know | arXiv 2207.05221 |
| Lin et al. 2022 | Teaching Models to Express Their Uncertainty in Words | arXiv 2205.14334 |
| Dahl et al. 2024 | Large Legal Fictions: Profiling Legal Hallucinations in LLMs. *J. Legal Analysis* | 10.1093/jla/laae003 |
| Magesh et al. 2025 | Hallucination-Free? Assessing the Reliability of Leading AI Legal Research Tools. *J. Empirical Legal Studies* | 10.1111/jels.12413 |

## DÜZELTİLECEK — yıl kayması (3)

| taslakta | GERÇEK | ne yapılmalı |
|---|---|---|
| **Zhou & El-Gohary 2017** | *Ontology-based automated information extraction from building energy conservation codes*, **2016**, Automation in Construction, 10.1016/j.autcon.2016.09.004 | yıl **2016** olacak |
| **Zhang & El-Gohary 2016** | Taslağın tarif ettiği çalışma (*Semantic NLP-Based Information Extraction from Construction Regulatory Documents*) **2013**, J. Comput. Civ. Eng., 10.1061/(asce)cp.1943-5487.0000346 | ya yıl **2013** yapılacak ya da gerçekten 2016 tarihli farklı bir Zhang & El-Gohary çalışması bulunup künyesi yazılacak. **Şu hâliyle kullanılamaz** |
| **Xiong et al. 2024** | arXiv sürümü **2023** (2306.13063); ICLR sürümü 2024 | Hangi sürüme atıf yapıldığı **seçilip tutarlı** kullanılacak |

## [ATIF GEREKLİ] boşlukları için bulunan aday (1)

Taslakta *"[ATIF GEREKLI: LLM-based automated compliance checking in construction, 2023–2025]"*
işareti vardı. Doğrulanmış aday:

- **Chen et al. 2024** — *Automated Building Information Modeling Compliance Check
  through a Large Language Model Combined with Deep Learning*, **Buildings** 14(7),
  10.3390/buildings14071983

İkinci boşluk — *"risk-based acceptance thresholds for decision-support software in
construction"* — için doğrulanmış kaynak **BULUNAMADI**. Uydurulmadı; makalede
kabul eşiği konusunun literatürde yerleşik olmadığı zaten yazılıyor, o boşluk
atıfsız bırakılabilir ya da kaldırılabilir.

## Standart

- **IEC 61508** — Functional safety of electrical/electronic/programmable electronic
  safety-related systems. Bir dergi makalesi değil, standart; künyesi standart
  biçiminde verilmeli. IEC kataloğundan **doğrulanmadı** (OpenAlex kapsamı dışında).
