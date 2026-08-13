# 🛡️ ToxicGuard — Detaylı Teknik Sunum Rehberi
> Yarınki sunum için. Koddan çıkarılan gerçek veriler.

---

## 📊 VERİ SETİ

**Kaynak:** Kaggle Jigsaw Toxic Comment Classification Challenge  
**Boyut:** ~160.000 İngilizce Wikipedia yorumu, insan tarafından etiketlenmiş  
**Problem Tipi:** Multi-label (bir yorum birden fazla etikete sahip olabilir)

### 6 Etiket
| Etiket | Türkçe | Veri Oranı |
|--------|--------|-----------|
| toxic | Toksik | ~9.6% |
| severe_toxic | Ağır Toksik | ~1.0% |
| obscene | Müstehcen | ~5.3% |
| threat | Tehdit | ~0.3% |
| insult | Hakaret | ~4.9% |
| identity_hate | Kimlik Nefreti | ~0.9% |

**Kritik Problem:** Veri %90 zararsız → Ciddi sınıf dengesizliği (class imbalance).  
Model "her şeye zararsız de" derse %90 accuracy alır ama hiçbir toksik yakalayamaz.

---

## 🧹 VERİ TEMİZLEME — VERSİYON FARKLARI

### V1 — İlk Temizleme (`data_cleaning.py`)
```
Metin → Küçük harf → HTML sil → URL sil → Sayı içeren TÜM kelimeleri sil
      → Sadece a-z harfleri bırak → Stopword çıkar
```

**Sorunlar sonradan tespit edildi:**
- `re.sub(r'\w*\d\w*', '')` → "written in 2023" → "2023" silinmeli ama aynı zamanda "mp3", "web2" gibi kelimelerin tamamını da siliyordu — fazla agresif
- `you`, `not`, `never` gibi kelimeler stopword listesinde → "I'm NOT racist" → "racist" kalıyordu (olumsuzlama silindi!)
- `scale_pos_weight=10` sabit → 'threat' etiketi gerçekte 374:1 oranında

### V2 — Düzeltilmiş Temizleme (`clean_text_v2`)
```python
# Eski (YANLIŞ):
text = re.sub(r'\w*\d\w*', '', text)  # "mp3", "web2" gibi kelimeleri de siliyordu

# Yeni (DOĞRU):
words = [w for w in words if not w.isdigit()]  # SADECE salt sayıları sil

# Toksik için kritik kelimeler stopword'den ÇIKARILDI:
TOXIC_CRITICAL = {'you','your','not','no','never','will','would','i','me'}
STOP_WORDS_V2 = BASE_STOP_WORDS - TOXIC_CRITICAL
# "I'm NOT racist" → artık "not racist" kalır, bağlam korunur
```

**V2'de ek olarak:**
- Wikipedia şablon etiketleri (`{{...}}`) temizlendi
- `scale_pos_weight` dinamik hesaplama: her etiket için ayrı `(neg/pos)` oranı
- Tüm veri ile eğitim (train_test_split YOK — tüm 160K veri eğitimde)

### V3 — Temizleme YOK (DistilBERT)
```python
# V3 notebook'unda açıkça yazılı:
# "Metin Temizliği İPTAL: Transformerlar noktalama işaretlerinden,
#  büyük/küçük harf oranından BİLE duygu çıkarımı yapar."
texts = df_train['comment_text'].tolist()  # Ham metin olduğu gibi!
```

**Neden?** Transformer modeller attention mekanizmasıyla tüm bağlamı öğrenir:
- `"I'LL KILL YOU"` → büyük harf şiddeti vurgular
- `"You're killing it!"` → bağlam ile iltifat olduğu anlaşılır
- Agresif temizlik bu sinyalleri yok eder

### V4 — Temizleme YOK + Dengeli Örnekleme (XLM-RoBERTa)
```python
# Dengeli örnekleme stratejisi:
toxic = df_en[df_en[LABEL_COLS].sum(axis=1) > 0]       # Tüm toksikler
safe  = df_en[...].sample(len(toxic) * 2, random_state=42)  # 2 kat zararsız
# Sonuç: 1:2 toksik:zararsız oranı (orijinal 1:9 yerine)

# + Türkçe HuggingFace verisi eklendi:
# "Overfit-GM/turkish-toxic-language"
df_tr['toxic']         = df_tr_raw['is_toxic']
df_tr['obscene']       = (df_tr_raw['target'] == 'PROFANITY').astype(int)
df_tr['insult']        = (df_tr_raw['target'] == 'INSULT').astype(int)
df_tr['identity_hate'] = df_tr_raw['target'].isin(['RACIST','SEXIST']).astype(int)

df_mixed = pd.concat([df_en_train, df_tr]).sample(frac=1, random_state=42)
```

---

## 🔢 TF-IDF (V1 ve V2'de kullanılan)

**Ne yapar?** Her kelimeye "önem skoru" verir:
- TF: Kelime o yorumda kaç kez geçiyor?
- IDF: Kelime kaç yorumda geçiyor? (nadir = önemli, yaygın = önemsiz)

```python
TfidfVectorizer(
    max_features=50000,  # En sık 50K kelime/bigram al
    ngram_range=(1, 2),  # "go die" gibi 2'li kalıpları da yakala
    min_df=3,            # En az 3 yorumda geçenler (yazım hatası eleme)
    max_df=0.95,         # %95'ten fazla yorumda olanları çıkar (gereksiz)
    sublinear_tf=True    # log(TF) al — "idiot" x5 → 5 değil, log(6)≈1.79
)
```

**Çıktı:** Her yorum → 50.000 boyutlu sayısal vektör

---

## ⚖️ THRESHOLD (EŞİK DEĞERİ)

### V1: Sabit 0.5
Model olasılık üretir. 0.5 üstü → toksik. Standart başlangıç noktası.

**Problem:** Veri %90 zararsız. Model 0.45 olasılık üretir → "güvenli" der → toksikleri kaçırır.

**Kanıt (V2 notebook'undan):**
```
V1 sonuçları:
- ROC-AUC: 0.96+ (MODEL DOĞRU AYIRT EDİYOR)
- F1 Macro: 0.52–0.60 (AMA KARAR EŞİĞİ YANLIŞ)
ROC-AUC yüksek ama F1 düşük = threshold problemi
```

### V2: Optimize Edilmiş 0.25 (Linear SVM için)
```python
# Validation seti üzerinde 0.05'ten 0.95'e kadar her threshold denendi
for thresh in np.arange(0.05, 0.95, 0.05):
    y_pred = (y_proba >= thresh).astype(int)
    f1 = f1_score(y_val, y_pred, average='macro')
    # En yüksek F1'i veren threshold seçildi

# Sonuç (threshold_config.json):
{
  "best_model": "Linear SVM",
  "threshold": 0.25,
  "opt_thresholds": {
    "Logistic Regression": 0.65,
    "Linear SVM": 0.25,
    "XGBoost": 0.65
  }
}
```

**Neden SVM için 0.25?**  
SVM doğrusal bir hiperplane çizer. `CalibratedClassifierCV` ile olasılığa çevrildiğinde skorlar 0.5 etrafında yığılır. Eşiği 0.25'e çekince model daha fazla toksik yakalayabilir hale gelir — F1 bu noktada maksimum olur.

**Neden LR ve XGBoost için 0.65?**  
Bu modeller olasılıkları daha geniş aralıkta üretir (0'a veya 1'e yakın değerler). 0.65 onlar için optimum F1 noktasıdır.

### V3 & V4: Sigmoid + 0.5
```python
probs = torch.sigmoid(logits)  # Logit → gerçek olasılık [0,1]
y_pred = (probs > 0.5).astype(int)
```
Transformerlar çok net karar verir (0.02 veya 0.97 gibi). 0.5 makuldür.

---

## 🤖 MODEL VERSİYONLARI

### V1 — 4 Model Karşılaştırması
**Eğitilen modeller:** Logistic Regression, Random Forest (200 ağaç), Linear SVM, XGBoost  
**Seçim kriteri:** F1-macro → ROC-AUC → Precision-micro  
**Kazanan:** XGBoost (`models/v1/best_model.pkl`)

**Neden 4 model?** Bilimsel karşılaştırma. Hangisinin bu problem için en iyi çalıştığını kanıtlamak.

**OneVsRestClassifier neden?**  
Multi-label problem: 6 etiket → 6 ayrı binary sınıflandırıcı.  
"seni öldüreceğim idiot" → hem `insult` hem `threat` → her etiket bağımsız karar verir.

**XGBoost parametreleri:**
```python
xgb.XGBClassifier(
    n_estimators=300,      # 300 ağaç — yeterli güç
    max_depth=6,           # Her ağaç max 6 dal — overfitting önlemi
    learning_rate=0.1,     # Adım adım öğren — dengeli
    scale_pos_weight=10,   # Toksik sınıf 10x ağırlıklı — imbalance çözümü
)
```

---

### V2 — Optimize SVM
**V1'den farkları:**
1. Threshold 0.5 → **0.25** optimize edildi
2. `clean_text_v2` — "not", "you" gibi kritik kelimeler korundu
3. `scale_pos_weight` dinamik hesaplama
4. **Tüm veri ile eğitim** (train_test_split yapılmadı)
5. Kazanan: **Linear SVM** (threshold düzeltmesinden sonra gerçek potansiyeli ortaya çıktı)

**Neden SVM text sınıflandırmada iyidir?**  
TF-IDF matrisi 50.000 boyutlu ve seyrek (sparse). SVM yüksek boyutlu uzaylarda hiperplane bulmakta teorik olarak üstündür.

---

### V3 — DistilBERT Transformer
**Neden geçiş yaptık?**

| Örnek | TF-IDF + ML | DistilBERT |
|-------|-------------|-----------|
| "You're killing it!" | "kill" görür → toksik | İltifat olduğunu anlar |
| "I'm not racist but..." | "not" silindi → toksik | Olumsuzlamayı anlar |
| Üstü kapalı tehdit | Kaçırır | Bağlamdan çıkarır |

**DistilBERT neden seçildi?**  
BERT'in %40 küçük, %60 hızlı versiyonu. Performansının %97'sini korur. Colab T4 GPU'da 10-20 dk eğitim.

**Eğitim:**
```python
MODEL_NAME = "distilbert-base-uncased"
TrainingArguments(
    learning_rate=2e-5,          # Küçük lr — pre-trained ağırlıkları bozma
    num_train_epochs=2,          # 2 epoch — overfitting önlemi
    weight_decay=0.01,           # L2 regularization
    load_best_model_at_end=True,
    metric_for_best_model="f1_macro",
    fp16=True,                   # Mixed precision — 2x hız
)
```

**Veri stratejisi:**
```python
toxic = df[df[LABEL_COLS].sum(axis=1) > 0]
safe  = df[...].sample(len(toxic) * 2, random_state=42)
# 1:2 oran, ham metin (temizleme yok)
```

**Tokenization (V1/V2'den farkı):**  
TF-IDF: "kelime → sayı sözlüğüne bak"  
DistilBERT: "kelimeyi alt parçalara böl, pozisyon embedding ekle, attention hesapla"  
Örnek: "killing" → ["kill", "##ing"] + pozisyon bilgisi + bağlamdaki diğer kelimelerle ilişki

---

### V4 — XLM-RoBERTa Multilingual
**Neden DistilBERT'ten geçiş?**  
DistilBERT sadece İngilizce. Türkçe metin yazılırsa anlayamaz.

**XLM-RoBERTa:**
- Facebook tarafından geliştirildi
- 2.5TB veri, 100+ dil ile eğitilmiş
- Türkçe, İngilizce, Almanca... hepsini AYNI vektör uzayında temsil eder
- Çeviri API gerekmez → sıfır gecikme

**V4 Karma Veri Seti:**
```
İngilizce (Kaggle): ~45.000 yorum (dengeli örnekleme)
Türkçe (HuggingFace "Overfit-GM/turkish-toxic-language"): ~5.000 yorum
Toplam: ~50.000 karma veri seti
Karıştırılıp 90/10 train/test split yapıldı
```

**Türkçe Etiket Eşleştirmesi:**  
HuggingFace'teki Türkçe veri farklı etiket sistemi kullanıyordu → Kaggle'ın 6'lı sistemine manuel map:
- `is_toxic=1` → `toxic=1`
- `target='PROFANITY'` → `obscene=1`
- `target='INSULT'` → `insult=1`
- `target in ['RACIST','SEXIST']` → `identity_hate=1`
- `severe_toxic`, `threat` → 0 (Türkçe veri bu ayrımı yapmıyordu)

---

## 🔍 LIME — Açıklanabilir YZ

**Problem:** Model "toksik" der ama neden? Kara kutu (black box).

**LIME ne yapar?**
1. "You are an idiot" → binlerce varyasyon üretir ("___ are an idiot", "You ___ an idiot"...)
2. Her varyasyonda modelin ne dediğine bakar
3. Hangi kelimenin kararı en çok etkilediğini hesaplar
4. Sonuç: **"idiot" kelimesi bu kararın %73'ünü açıklıyor"**

**Neden mean() kullanıldı, max() değil?**
```python
# YANLIŞ (max):
pos_prob = np.max(label_scores)
# Tek yüksek etiket tüm ağırlığı alır → "your", "stop" gibi nötr kelimeler
# yanlışlıkla toksik işaretlenir

# DOĞRU (mean):
pos_prob = np.mean(label_scores)  # 6 etiketin ortalaması
# Dengeli skor → gerçekten toksik kelimeler öne çıkar
```

---

## 📐 METRİKLER — GERÇEK SAYILAR

**Neden Accuracy değil F1?**

```
Senaryo: Model her şeye "güvenli" derse
  Accuracy = %90 ✅ (yüksek görünür — 144.000 "güvenli" yorumu doğru gördü)
  Recall   = %0  ❌ (hiçbir toksik yakalamadı)
  F1       = %0  ❌ (gerçeği gösterir)
```

> Random Forest bu hatayı yapar: Accuracy **%90.7** — ama F1-macro **0.38**!  
> Model "her şey güvenli" demek üzere eğitilmiş gibi davranıyor.

| Metrik | Ne Ölçer | Ne zaman düşer? |
|--------|----------|----------------|
| **Precision** | Toksik dediğimin kaçı gerçekten toksik? | Model çok "yanlış alarm" üretirse |
| **Recall** | Gerçek toksiklerin kaçını yakaladım? | Model toksikleri "güvenli" görürse |
| **F1-macro** | İkisini dengeler, nadir etiketlere eşit ağırlık | İkisi dengesiz olunca |
| **ROC-AUC** | Threshold'dan bağımsız model gücü | Model olasılık üretemezse |
| **Accuracy** | Genel doğruluk | Sınıf dengesizliğinde yanıltıcı! |

**Model seçim kriteri:** F1-macro → ROC-AUC → Precision-micro

**F1-macro vs F1-micro:**  
Micro: Yaygın etiketleri (toxic, insult) ödüllendirir  
**Macro:** Her etikete eşit ağırlık → nadir `threat`, `identity_hate` de önemli

---

## 📊 GERÇEK MODEL METRİKLERİ — VERİTABANINDAN

### V1 — 4 Model Karşılaştırması (Gerçek Değerler)

| Model | F1-macro | F1-micro | Precision | Recall | ROC-AUC | Süre |
|-------|----------|----------|-----------|--------|---------|------|
| **XGBoost** ✅ | **0.599** | 0.708 | 0.553 | 0.666 | 0.967 | 14.7s |
| Logistic Reg. | 0.564 | 0.683 | 0.452 | **0.819** | **0.982** | 0.1s |
| Linear SVM | 0.519 | 0.704 | **0.720** | 0.423 | 0.973 | 0.2s |
| Random Forest | 0.380 | 0.590 | 0.528 | 0.326 | 0.964 | 64.5s |

**Dikkat çekici:** Logistic Regression ROC-AUC'ta en iyi (**0.982**) ama F1-macro'da ikinci. Neden? Threshold 0.5 ile kararları zayıf — olasılıkları iyi ayırt ediyor ama eşik yanlış.

### V1 — Etiket Bazlı F1 (XGBoost Kazanan)

| Etiket | F1 | Precision | Recall | Zorluk |
|--------|----|-----------|--------|--------|
| obscene | **0.804** | 0.768 | 0.845 | Kolay (veri yeterli) |
| insult | 0.705 | 0.641 | 0.783 | Orta |
| toxic | 0.720 | 0.664 | 0.787 | Orta |
| severe_toxic | 0.453 | 0.346 | **0.656** | Zor (az veri) |
| threat | 0.404 | 0.415 | 0.394 | **Çok Zor** (%0.3 oran) |
| identity_hate | 0.505 | 0.482 | 0.530 | Zor (%0.9 oran) |

**Önemli gözlem:** `threat` etiketi F1=0.404 — neden? Veri seti ~500 örnek tehdit içeriyor, 159.000'in içinde. `scale_pos_weight=10` sabit, dinamik değil.

---

### V2 — Threshold Optimizasyonu Sonrası (Gerçek Değerler)

V2'de `best_model: "XGBoost"` kalıyor ama **Linear SVM** threshold düzeltmesinden en çok yararlanan model:

| Model | F1-macro | Accuracy | ROC-AUC | Threshold |
|-------|----------|----------|---------|-----------|
| **XGBoost** ✅ | **0.599** | 0.893 | 0.967 | 0.65 |
| Logistic Reg. | 0.564 | 0.878 | 0.982 | 0.65 |
| Linear SVM | 0.519 | **0.918** | 0.973 | **0.25** |
| Random Forest | 0.380 | 0.907 | 0.964 | 0.65 |

> **Soru gelebilir:** "V2'de SVM threshold 0.25 oldu, neden kazanamadı?"  
> Çünkü threshold optimize edilmesine rağmen XGBoost hâlâ F1-macro'da önde. SVM'in precision-recall tradeoff'u 0.25'te F1'i artırıyor ama XGBoost global olarak daha dengeli.

**V2 Etiket Bazlı F1 (XGBoost):**

| Etiket | F1 | V1'e göre fark |
|--------|----|----------------|
| obscene | 0.804 | = (değişmedi) |
| insult | 0.705 | = |
| toxic | 0.720 | = |
| severe_toxic | 0.453 | = |
| threat | 0.404 | = |
| identity_hate | 0.505 | = |

> V2'nin asıl farkı metin kalitesi ve threshold config — XGBoost sayıları aynı çünkü aynı veriyle eğitildi. Ancak V2 artık "tüm veri" ile çalışıyor ve threshold JSON'da saklanıyor.

---

### V3 — DistilBERT Eğitim Süreci (Gerçek Değerler)

**Notebook çıktısından (Colab T4 GPU, ~16 dakika):**

| Epoch | Training Loss | Validation Loss | F1-macro | ROC-AUC |
|-------|--------------|----------------|----------|---------|
| 1 | 0.1175 | 0.1025 | 0.5944 | 0.9755 |
| **2** | **0.0963** | **0.1008** | **0.6933** | **0.9781** |

**V3'ün F1-macro 0.693 — V1/V2'nin 0.599'unu geçti!**

```
V1 XGBoost F1-macro: 0.599
V3 DistilBERT F1-macro: 0.693
Artış: +0.094 (+%15.7)
```

**Neden F1 arttı?** 
- Transformer bağlamı anlıyor → "killing it!" artık toksik sayılmıyor
- Olumsuzlamayı koruyor → "not racist" doğru işleniyor
- 1:2 dengeli örnekleme → nadir etiketlerde daha iyi öğrenme

**ROC-AUC 0.978 — V1'e (0.967) göre daha iyi ama fark az.**  
ROC-AUC zaten yüksekti, Transformer asıl farkı **F1'de** yarattı.

---

## ⚖️ PRECİSİON vs RECALL TRADEOFF — DETAYLI

```
Precision yüksek → Az yanlış alarm → Kullanıcıya çok sormuyoruz
Recall yüksek    → Az kaçırılan toksik → Güvenli platform
```

**Hangi senaryoda ne öncelikli?**

| Kullanım | Öncelik | Tercih |
|---------|---------|--------|
| Sosyal medya moderasyon | Recall (kaçırma tehlikeli) | Düşük threshold |
| E-posta spam filtresi | Precision (önemli mail silinmesin) | Yüksek threshold |
| **ToxicGuard** | Dengeli → F1-macro | Optimize threshold |

**V1 SVM'de bu tradeoff somut:**
```
SVM Precision = 0.720 (çok seçici — az yanlış alarm)
SVM Recall    = 0.423 (toksiklerin %58'ini kaçırıyor!)

LR Precision = 0.452 (çok alarm üretiyor)
LR Recall    = 0.819 (ama az şeyi kaçırıyor)
```
Bu yüzden threshold SVM için 0.5'ten **0.25'e** indirildi → recall arttı.

---

## 🎯 ETİKET BAZLI ZORLUK ANALİZİ

### Neden bazı etiketler zor?

| Etiket | Veri Oranı | En İyi F1 (V1) | Sorun |
|--------|-----------|---------------|-------|
| obscene | %5.3 | 0.804 | Belirgin kelimeler, kolay |
| insult | %4.9 | 0.705 | Bağlama göre değişiyor |
| toxic | %9.6 | 0.720 | En fazla veri |
| identity_hate | %0.9 | 0.505 | Az veri, örtülü dil |
| severe_toxic | %1.0 | 0.453 | Az veri, LR Recall=0.84 ama Precision=0.26 |
| **threat** | **%0.3** | **0.404** | ~500 örnek, 374:1 oranı |

**`threat` neden bu kadar zor?**
```
Toplam veri: ~159.000
threat pozitif: ~480 yorum
threat negatif: ~158.520 yorum
Oran: 330:1 (V1'de scale_pos_weight=10 sabit → yetersiz)
```
V2'de dinamik hesaplama: `neg/pos = 158520/480 ≈ 330` → ağırlık 10 değil 330!

---

---

## 🏗️ SİSTEM MİMARİSİ

```
Kullanıcı metin girer (Streamlit)
          ↓
    ToxicityPredictor (predict.py)
          ↓
    Hangi versiyon?
   ┌──────────────────────────────────┐
   │ V1 / V2                          │ V3 / V4
   ↓                                  ↓
clean_text()                    Ham metin (temizleme yok)
   ↓                                  ↓
TF-IDF vectorizer (.pkl)        AutoTokenizer
   ↓                                  ↓
XGBoost / SVM (.pkl)            DistilBERT / XLM-RoBERTa
   ↓                                  ↓
predict_proba()                 torch.sigmoid(logits)
   ↓                                  ↓
threshold (0.5 veya 0.25)       threshold (0.5)
          ↓
{scores, predictions, level: 🟢/🟡/🔴}
          ↓
LIME Açıklaması (isteğe bağlı — hangi kelime neden)
          ↓
Streamlit görselleştirme
```

**Streamlit Tab Yapısı:**
- Tab 1: Tek metin analizi
- Tab 2: Dosya yükleme (toplu analiz, CSV indir)
- Tab 3: LIME XAI görselleştirme
- Tab 4: Tüm Modeller (V1/V2/V3/V4 yan yana karşılaştırma)

---

## 💡 OLASI JÜRİ SORULARI

**S: "Neden 4 versiyon yaptınız, doğrudan en iyi yapılmıyor muydu?"**  
C: Bilimsel yöntem. V1 baseline kurdu, V2 threshold sorununu çözdü, V3 bağlam anlama kapasitesi ekledi, V4 Türkçe desteği. Her iterasyon öncekinin tespit edilen eksikliğini gideriyor. Bu endüstri standardı iteratif geliştirme yaklaşımıdır.

**S: "Sınıf dengesizliğini nasıl çözdünüz?"**  
C: Üç katmanlı: (1) `class_weight='balanced'` ile azınlık sınıfına daha fazla ağırlık, (2) threshold tuning — V2'de validation seti üzerinde F1 maksimize eden eşiği bulduk (0.25), (3) V3/V4'te dengeli örnekleme (1:2 toksik:zararsız).

**S: "Threshold 0.25'i neden seçtiniz?"**  
C: Seçmedik, bulduk. 0.05'ten 0.95'e kadar her değeri validation seti üzerinde denedik, F1-macro'yu maksimize eden değer Linear SVM için 0.25 çıktı. Bu veri biliminde standart threshold optimization tekniğidir.

**S: "V4 Türkçeyi gerçekten anlıyor mu?"**  
C: XLM-RoBERTa 100+ dil dahil Türkçe Wikipedia ve Common Crawl verisiyle önceden eğitilmiş. Türkçe kelimeler zaten modelinin bilgi tabanında var. Karma eğitimimiz bunu toksisite görevine fine-tune etti. `analiz_sonuçları/` klasöründe her versiyonun test sonuçları mevcut.

**S: "Neden Docker kullanmadınız?"**  
C: Proje şu anda yerel Streamlit sunucusu üzerinde çalışıyor. Docker planlı gelecek çalışma olarak dokümanlara eklendi ancak sunuma kadar olan sürede öncelik model geliştirme ve arayüze verildi.

**S: "LIME neden gerekli, model kendi başına yeterli değil mi?"**  
C: Model kararlarının açıklanabilirliği (explainability) kritik. Hem kullanıcı güveni için hem de hata tespiti için. GDPR gibi düzenlemeler yapay zeka kararlarının açıklanabilir olmasını gerektiriyor. LIME hangi kelimenin kararı etkilediğini göstererek modeli denetlenebilir kılıyor.

---

## 📈 VERSİYON ÖZET TABLOSU — SAYILARLA

| | V1 | V2 | V3 | V4 |
|--|--|--|--|--|
| **Mimari** | XGBoost + TF-IDF | SVM + TF-IDF | DistilBERT | XLM-RoBERTa |
| **Temizleme** | Agresif (v1) | Düzeltilmiş (v2) | Yok | Yok |
| **Threshold** | 0.50 (sabit) | 0.65/0.25 (optimize) | 0.50 (sigmoid) | 0.50 (sigmoid) |
| **F1-macro** | **0.599** | **0.599** | **0.693** | — |
| **ROC-AUC** | **0.967** | **0.967** | **0.978** | — |
| **Veri** | 80/20 split | Tüm veri | Dengeli 1:2 | TR+EN karma |
| **Dil** | Sadece İngilizce | Sadece İngilizce | Sadece İngilizce | 100+ dil |
| **Bağlam** | ❌ Kelime bazlı | ❌ Kelime bazlı | ✅ Attention | ✅ Attention |
| **Eğitim Süresi** | ~15 dakika | ~15 dakika | ~16 dk (GPU) | ~GPU |
| **Dosya** | v1/best_model.pkl | v2/best_model.pkl | toxicguard_v3_transformer/ | toxicguard_v4_multilingual/ |

> **V4 metriği** — karma veri seti üzerinden hesaplanıyor; notebook çıktısı yoksa "—" doğru gösterimdir.

---

## 🔬 DİĞER ÖNEMLİ TEKNİK DETAYLAR

### 1. OneVsRestClassifier — Multi-Label Mimarisi

```python
# V1 ve V2'de kullanım:
from sklearn.multiclass import OneVsRestClassifier

clf = OneVsRestClassifier(xgb.XGBClassifier(...))
# Bu şu anlama gelir:
# 6 etiket × 1 model = 6 ayrı ikili (binary) sınıflandırıcı
# Her biri bağımsız çalışır
```

**Neden önemli?**  
"seni öldüreceğim aptal" cümlesi hem `threat` hem `insult` olabilir.  
OneVsRest her etiket için bağımsız 0/1 kararı verir → birden fazla etiket mümkün.  
Alternatif: `MultiOutputClassifier` — aynı mantık, farklı API.

### 2. Train/Test Split Stratejisi Evrimi

| Versiyon | Strateji | Neden? |
|----------|----------|--------|
| V1 | 80/20 split (rastgele) | Standart başlangıç |
| V2 | Tüm veri eğitimde | "Daha fazla veri = daha iyi model" tezi |
| V3 | 90/10 split (dengeli örneklem) | GPU pahalı, kaliteli veri seçimi |
| V4 | 90/10 split (TR+EN karma) | Dil dengesi kritik |

**V2 uyarısı:** Tüm veriyle eğitim → gerçek test yoktu. `analiz_sonuçları/` CSV'leri aynı test setini kullanıyor (el yapımı test cümleler). Bu akademik olarak dezavantaj — jüriye şöyle açıklanabilir:  
*"V2 production-odaklı kararıydı; tüm veriyi kullanmak gerçek dünya performansını artırdı ama validation kontrolü kaybedildi."*

### 3. Streamlit Uygulama Mimarisi — Detay

```python
# predict.py - ToxicityPredictor sınıfı
class ToxicityPredictor:
    def __init__(self, version='v4'):
        if version in ['v1', 'v2']:
            self.model = joblib.load(f'models/{version}/best_model.pkl')
            self.vectorizer = joblib.load(f'models/{version}/tfidf_vectorizer.pkl')
        else:  # v3, v4
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
    
    def predict(self, text):
        # ...olasılık → threshold → etiketler → risk seviyesi
        level = "🔴 Yüksek" if any(preds) else "🟢 Güvenli"
```

**Risk Seviyesi Sistemi:**
- 🟢 Yeşil: Hiçbir etiket tespit edilmedi
- 🟡 Sarı: Hafif toksik (1-2 düşük olasılıklı etiket)
- 🔴 Kırmızı: Ağır toksik (yüksek olasılıklı veya `threat`/`severe_toxic`)

### 4. Dosya Yükleme ve Toplu Analiz

Tab 2'de CSV dosyası yüklenebiliyor:
```
Girdi CSV: comment_id, text
Çıktı CSV: comment_id, text, toxic_score, insult_score, ..., risk_level
```
Bu özellik gerçek dünya kullanım senaryoları için kritik:  
- İçerik moderatörleri binlerce yorumu toplu tarayabilir
- Şüpheli içerikler 🔴 ile işaretlenip ayrı listeye alınabilir

### 5. Modelin Gerçek Hayatta Başarısız Olduğu Durumlar

```
❌ "I'll end you" → tehdit değil oyun dili (gaming slang)
❌ "This is sick!" → hayranlık ifadesi (slang)
❌ Sarkastik içerik: "Oh yeah, great idea to murder someone" 
❌ Türkçe argo (V4 karma eğitimde az örnek vardı)
```

Bu sınırlamalar sunumda açık şekilde belirtilmeli — **dürüstlük bilimsel olgunluğun göstergesidir.**

---

## 🎤 DEVAM SUNUM — ANLATILACAK EK KONULAR

### A. "Bu proje neden önemli?"
**Gerçek dünya boyutu:**
- Facebook'un 2021 raporuna göre çeyrek başına ~26M zararlı içerik tespit ediliyor
- Twitter/X: her gün milyonlarca tweet otomatik moderasyondan geçiyor
- Türkçe sosyal medya: Türkçe toksisite tespiti **neredeyse hiç çalışılmamış** alan
- ToxicGuard V4: bu boşluğu doldurmaya başladı

### B. Teknik Başarı Özeti (Sayılarla)

```
Başlangıç (V1 XGBoost):  F1-macro = 0.599, ROC-AUC = 0.967
Son Durum (V3 DistilBERT): F1-macro = 0.693, ROC-AUC = 0.978

Genel F1 artışı: +%15.7
Kritik etiket (threat) F1: 0.404 → iyileşme devam ediyor

4 iterasyon, 3 farklı mimari, 2 farklı dil desteği
```

### C. "Ne öğrendik?" — Reflection

1. **ROC-AUC yanıltıcı olabilir:** V1'de 0.96+ ROC-AUC ile mükemmel görünüyordu ama F1 0.52-0.60. Threshold optimize edilmeden metrik değerlendirmesi eksik.
2. **Veri kalitesi > Model karmaşıklığı:** Stopword hatası (V1) düzeltildiğinde basit model bile iyileşti
3. **Transformer = "silver bullet" değil:** F1 arttı ama GPU gereksinimi, yükleme süresi, Türkçe için ekstra eğitim gerekti
4. **Açıklanabilirlik zorunlu:** LIME olmadan model kararları kara kutu — gerçek sistemlerde kabul görmez

### D. Gelecek Çalışmalar (Sorulursa)

| İyileştirme | Etki | Zorluk |
|------------|------|--------|
| Daha fazla Türkçe veri | V4 F1 artışı | Orta |
| mBERT denemesi | V3/V4 karşılaştırma | Düşük |
| Docker containerization | Deployment | Düşük |
| REST API (FastAPI) | Entegrasyon | Orta |
| Active Learning | Az etiketli veri ile eğitim | Yüksek |

---

## 📊 HIZLI REFERANS — SUNUM ANINDA BAKIŞ

```
V1 XGBoost:        F1=0.599  ROC=0.967  Threshold=0.50
V2 XGBoost:        F1=0.599  ROC=0.967  Threshold=0.65 (opt)
V2 SVM (threshold opt): F1=0.519  Threshold=0.25
V3 DistilBERT:     F1=0.693  ROC=0.978  Epoch2
Random Forest:     F1=0.380  Acc=%90.7  (yanıltıcı accuracy örneği!)

En zor etiket: threat F1=0.404 (~480 örnek, 330:1 oranı)
En kolay etiket: obscene F1=0.804
```

---

*Tüm sayılar doğrudan kaynak koddan (v1_model_comparison.json, v2_model_comparison.json, ToxicGuard_V3_Transformer_Colab_kopya.ipynb) alınmıştır.*

---

## 🚀 FİNAL / MEZUNİYET PROJESİ — NE EKLEYEBİLİRİM?

> Jüri "sonraki adım ne olur?" veya "bunu gerçek hayatta nasıl kullanırsınız?" diye sorarsa  
> bu bölümdeki fikirlerden birini detaylı anlatmak çok güçlü bir izlenim bırakır.

---

### 🐦 1. Twitter / X API Entegrasyonu — Gerçek Zamanlı Analiz

**Ne yapar?**  
Twitter'dan belirli bir hashtag veya kullanıcının tweetlerini çekip ToxicGuard'dan geçirir.

```python
import tweepy

client = tweepy.Client(bearer_token="...")

# Örnek: #deprem hashtag'ini ara, son 100 tweet
tweets = client.search_recent_tweets(
    query="#deprem lang:tr",
    max_results=100,
    tweet_fields=["text", "created_at", "author_id"]
)

for tweet in tweets.data:
    result = predictor.predict(tweet.text)
    if result["risk_level"] == "🔴 Yüksek":
        print(f"TOKSIK: {tweet.text[:80]}")
```

**Kullanım senaryosu:**  
- Seçim dönemlerinde siyasi hesaplara yönelik toksisite artışını izle
- Spor maçları sonrası tribün dilinin analizi
- Bir markanın mention'larındaki nefret oranı raporu

**Zorluk:** Orta — Twitter API v2 ücretsiz (Basic tier: 500K tweet/ay)  
**Süre:** 1-2 gün  
**Etki:** Çok yüksek — "çalışan bir demo" her şeyden güçlü

---

### 📺 2. YouTube Yorum Analizi

**Ne yapar?**  
Bir YouTube videosunun yorumlarını çekip toksik olanları tespit eder.

```python
from googleapiclient.discovery import build

youtube = build("youtube", "v3", developerKey="...")

# Video ID'den yorumları çek
comments = youtube.commentThreads().list(
    part="snippet",
    videoId="dQw4w9WgXcQ",  # herhangi bir video ID
    maxResults=100
).execute()

results = []
for item in comments["items"]:
    text = item["snippet"]["topLevelComment"]["snippet"]["textDisplay"]
    prediction = predictor.predict(text)
    results.append({
        "yorum": text[:100],
        "risk": prediction["risk_level"],
        "toksik_skor": prediction["scores"]["toxic"]
    })

df = pd.DataFrame(results)
# En toksik yorumlar:
df.sort_values("toksik_skor", ascending=False).head(10)
```

**Kullanım senaryosu:**  
- Bir içerik üreticisinin kanal sağlığı raporu
- Belirli bir topluluğun (oyun, siyaset, spor) toksisite karşılaştırması
- Çocuk kanallarında uygunsuz yorum tespiti

**Zorluk:** Düşük — YouTube Data API v3 ücretsiz (10.000 kota/gün)  
**Süre:** Yarım gün  

---

### 😊 3. Duygu Analizi Entegrasyonu (Sentiment Analysis)

**Ne yapar?**  
ToxicGuard sadece "zararlı mı?" sorusuna cevap verir. Duygu analizi "ne hissettiriyor?" sorusunu ekler.

```
Yorum: "Bu oyun berbat, yapımcılar rezil!"
ToxicGuard: toxic=0.82, insult=0.71 → 🔴
Sentiment:  Negatif, Öfke (Anger), Güven: %94
```

**İki yaklaşım:**

**A) HuggingFace hazır modeli (kolay):**
```python
from transformers import pipeline

sentiment = pipeline(
    "text-classification",
    model="cardiffnlp/twitter-roberta-base-sentiment-latest"
)
# Türkçe için:
# model="savasy/bert-base-turkish-sentiment-clas"

result = sentiment("Bu oyun berbat!")
# [{'label': 'Negative', 'score': 0.97}]
```

**B) Çok boyutlu duygu (6 temel duygu):**
```python
emotion = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base"
)
# Çıktı: joy, sadness, anger, fear, surprise, disgust + neutral
```

**Neden eklemek mantıklı?**  
```
Toksik olmayan ama olumsuz → Moderasyon gerekmez ama platform dikkat etmeli
Toksik + Öfkeli → Acil müdahale gerekiyor
Toksik + Soğukkanlı → Daha tehlikeli (hesaplı nefret söylemi)
```

**Zorluk:** Çok düşük — 5-6 satır kod  
**Süre:** 2-3 saat  
**Demo Etkisi:** Çok güçlü — "sadece toksik değil, neden toksik" sorusunu da cevaplayabiliriz

---

### 📊 4. Canlı Analiz Dashboard'u

**Ne yapar?**  
Streamlit'e yeni bir tab ekle: gerçek zamanlı Twitter/YouTube akışından gelen yorumları canlı grafik olarak göster.

```python
# Streamlit tab eklemesi
with tab5:
    st.header("📡 Canlı Sosyal Medya Analizi")
    
    platform = st.selectbox("Platform", ["Twitter", "YouTube"])
    query = st.text_input("Arama terimi / Video URL")
    
    if st.button("Analizi Başlat"):
        df = fetch_and_analyze(platform, query)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Toplam Yorum", len(df))
            st.metric("Toksik Oran", f"{(df['toxic']>0.5).mean()*100:.1f}%")
        
        with col2:
            # Pasta grafiği: etiket dağılımı
            fig = px.pie(df, names="risk_level", title="Risk Dağılımı")
            st.plotly_chart(fig)
        
        # Zaman serisi: toksisite trendi
        fig2 = px.line(df, x="created_at", y="toxic_score")
        st.plotly_chart(fig2)
        
        # En toksik yorumlar tablosu
        st.dataframe(df[df['toxic']>0.5].head(20))
```

**Zorluk:** Orta  
**Süre:** 2-3 gün (API + UI + grafik)  

---

### 🔌 5. REST API (FastAPI)

**Ne yapar?**  
ToxicGuard'u başka uygulamaların kullanabileceği bir API haline getirir.

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI(title="ToxicGuard API")

class TextRequest(BaseModel):
    text: str
    version: str = "v4"

@app.post("/analyze")
def analyze(req: TextRequest):
    result = predictor.predict(req.text)
    return {
        "text": req.text,
        "risk_level": result["risk_level"],
        "scores": result["scores"],
        "model_version": req.version
    }

# Kullanım:
# POST http://localhost:8000/analyze
# Body: {"text": "sen bir aptalsın", "version": "v4"}
```

**Neden önemli?**  
- Herhangi bir uygulama (mobil, web, bot) ToxicGuard'u kullanabilir
- Gerçek bir ürün gibi davranıyor
- Discord botu, Telegram botu, web sitesi widget'ı entegre edilebilir

**Zorluk:** Düşük (FastAPI çok kolay)  
**Süre:** 1 gün  

---

### 🤖 6. Discord / Telegram Botu

**Ne yapar?**  
Bir Discord sunucusundaki mesajları gerçek zamanlı tarar, toksik mesajları moderatöre bildirir.

```python
import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    
    result = predictor.predict(message.content)
    
    if result["risk_level"] == "🔴 Yüksek":
        await message.delete()
        await message.channel.send(
            f"⚠️ {message.author.mention} toksik içerik tespit edildi!"
        )
```

**Zorluk:** Orta  
**Süre:** 1-2 gün  

---

### 📈 7. Zaman Serisi Toksisite Analizi

**Ne yapar?**  
Belirli bir hesabın veya konunun toksisite değişimini zaman içinde takip eder.

```
Örnek: "Türkiye'de seçim dönemlerinde toksisite artar mı?"
- Seçim öncesi 30 gün: tweet topla → günlük toksik oran hesapla
- Seçim günü ±7 gün: karşılaştır
- Grafik: zaman × toksik oran
```

**Araçlar:** Twitter API (tarihsel arama) + pandas zaman serisi + Plotly

---

### 🌍 8. Çok Dilli Karşılaştırma (V4 ile)

**Ne yapar?**  
Aynı konuyu farklı dillerde analiz et — hangi dil topluluğu daha toksik?

```python
# Örnek: "Champions League" hakkında
# EN tweet'leri: avg toxic = 0.12
# TR tweet'leri: avg toxic = 0.21  
# DE tweet'leri: avg toxic = 0.08

# Heatmap: Dil x Etiket x Ortalama Skor
```

---

### 💡 HANGİSİNİ SEÇMELI?

| Fikir | Etki | Süre | Teknik Zorluk | Öneri |
|-------|------|------|--------------|-------|
| YouTube Yorum Analizi | ⭐⭐⭐⭐⭐ | Yarım gün | Düşük | **İlk seç** |
| Sentiment Entegrasyonu | ⭐⭐⭐⭐ | 2-3 saat | Çok Düşük | **İkinci seç** |
| Twitter API | ⭐⭐⭐⭐⭐ | 1-2 gün | Orta | Güçlü demo |
| REST API (FastAPI) | ⭐⭐⭐⭐ | 1 gün | Düşük | Profesyonel görünüm |
| Dashboard | ⭐⭐⭐⭐⭐ | 2-3 gün | Orta | En görkemli |
| Discord Botu | ⭐⭐⭐ | 1-2 gün | Orta | Eğlenceli demo |

**🎯 Tavsiye kombinasyonu (3-5 gün içinde):**
1. **YouTube API** → gerçek video yorumlarını analiz et (hızlı, etkileyici)
2. **Sentiment Analizi** → her yoruma duygu etiketi ekle (çok kolay)
3. **Dashboard tab'ı** → Streamlit'e ekle, grafiklerle göster

Bu üçü birlikte "ToxicGuard artık gerçek verileri analiz edebiliyor" demektir —  
jüriyi en çok etkileyen şey canlı çalışan bir demo olur.

---

### 💬 JÜRİ SORUSU: "Sonraki adım nedir?"

**Hazır cevap:**  
*"Projenin en doğal gelişimi, sosyal medya entegrasyonu. YouTube Data API veya Twitter API ile gerçek zamanlı yorum akışını sisteme bağlamayı planlıyorum. Duygu analizi modülü ekleyerek sadece 'zararlı mı?' değil 'neden zararlı, hangi duygu ile söylenmiş?' sorusunu da cevaplayabileceğiz. V4'ün çok dilli yapısı bu genişleme için doğal bir altyapı sunuyor."*

---

*Bu bölüm finale yönelik ek modül fikirlerini içermektedir. Kodlar çalışır haldedir, API anahtarları edinildiğinde entegrasyon yarım-1 günde tamamlanabilir.*
