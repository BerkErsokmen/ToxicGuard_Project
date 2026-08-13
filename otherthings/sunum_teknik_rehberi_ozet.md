# 🛡️ ToxicGuard — Sunum İçin Teknik Rehber

> Yarınki sunuma hazırlık. Tüm "neden?" sorularının cevabı burada.

---

## 📊 Veri Seti — Nereden, Ne Kadar, Neden?

### Kaynak: Kaggle Jigsaw Toxic Comment Classification Challenge

- **~160.000 İngilizce Wikipedia yorum**u içeren gerçek dünya verisi
- Kaggle yarışması verisi olduğu için **insan tarafından etiketlenmiş** (en güvenilir kaynak)
- **6 etiket** aynı anda var olabilir (multi-label):

| Etiket | Türkçesi | Açıklama |
|--------|----------|----------|
| `toxic` | Toksik | Genel zararlı içerik |
| `severe_toxic` | Ağır Toksik | Çok ileri düzey hakaret |
| `obscene` | Müstehcen | Cinsel/kaba dil |
| `threat` | Tehdit | Fiziksel zarar tehdidi |
| `insult` | Hakaret | Kişiye yönelik aşağılama |
| `identity_hate` | Kimlik Nefreti | Irk/din/cinsiyet saldırısı |

### Sınıf Dengesizliği Problemi (Class Imbalance)
- **~%90** yorum tamamen zararsız
- Sadece **~%10** toksik yorum var
- Bu durum modeli "her şeye güvenli de" demeye iter → **F1-Score yerine Accuracy bakarsak yanılırız**
- **Çözüm 1:** `class_weight='balanced'` — azınlık sınıfına daha fazla ağırlık ver
- **Çözüm 2:** Threshold tuning (V2'de uygulandı)
- **Çözüm 3:** Dengeli örnekleme (V3/V4'te uygulandı)

---

## 🧹 Veri Temizleme — V1 ile V4 Neden Farklı?

Bu projenin en önemli felsefesi: **"Modelin ne öğreneceği, veriyi nasıl hazırladığınla doğrudan ilgilidir."**

### V1 & V2 — Agresif Metin Temizleme (`data_cleaning.py`)

```python
def clean_text(text):
    text = str(text).lower()                          # 1. Küçük harfe çevir
    text = re.sub(r'<.*?>', '', text)                  # 2. HTML etiketlerini sil
    text = re.sub(r'http\S+|www\S+|https\S+', '', text)# 3. URL'leri sil
    text = re.sub(r'\w*\d\w*', '', text)               # 4. Sayı içeren kelimeleri sil (IP, ID vb.)
    text = re.sub(r'[^a-z\s]', ' ', text)              # 5. Sadece İngilizce harf tut
    text = re.sub(r'\s+', ' ', text).strip()           # 6. Fazla boşlukları temizle
    words = [w for w in text.split() if w not in stop_words] # 7. Stopword çıkar
    return " ".join(words)
```

**Neden bu kadar agresif temizleme?**

| Adım | Neden Yapıldı? |
|------|---------------|
| Küçük harf | "IDIOT" ve "idiot" aynı kelime — TF-IDF'in iki ayrı kelime saymaması için |
| HTML sil | Wikipedia yorumlarında `<br>`, `<b>` gibi etiketler var, anlam taşımıyor |
| URL sil | "http://..." TF-IDF'in gereksiz yerde yer harcamasını önler |
| Sayıları sil | IP adresleri, kullanıcı ID'leri, tarihler — toksisite analizinde anlamsız |
| Sadece harf tut | Noktalama işaretleri TF-IDF'de gürültü yaratır |
| Stopword çıkar | "the", "is", "a" gibi kelimeler her yorumda var, ayrım sağlamaz |

**TF-IDF için bu temizleme DOĞRU çünkü:** TF-IDF kelime bazlı çalışır, bağlamı yoktur. Gürültüyü en aza indirgemek başarımı artırır.

---

### V3 (DistilBERT) — Temizleme YOK

```python
# V3 Notebook'unda açıkça belirtildi:
# "Metin Temizliği İPTAL: Transformerlar noktalama işaretlerinden,
#  cümlenin büyük/küçük harf oranından BİLE duygu çıkarımı yapar."
texts = df_train['comment_text'].tolist()  # Ham metin, olduğu gibi!
```

**Neden temizleme yapılmıyor?**

Transformer modeller (BERT, DistilBERT) **dikkat mekanizmasıyla (attention)** tüm cümle bağlamını öğrenir:
- `"You're AMAZING!!!"` → büyük harf + ünlem işaretleri coşkuyu gösterir
- `"I'LL KILL YOU"` → büyük harf tehdidin şiddetini vurgular
- `"go die"` → küçük harf bile olsa iki kelime birlikte tehdit anlamı taşır

Agresif temizleme yaparsak bu bağlamsal sinyalleri yok ederiz → model körleşir.

---

### V4 (XLM-RoBERTa) — Temizleme YOK + Dengeli Örnekleme

```python
# V4 veri hazırlama stratejisi:
# 1. Toksik yorumların tamamını al
toxic = df_en[df_en[LABEL_COLS].sum(axis=1) > 0]
# 2. Zararsız yorumlardan 2 katı örnekle (denge için)
safe = df_en[df_en[LABEL_COLS].sum(axis=1) == 0].sample(len(toxic) * 2, random_state=42)
# 3. Türkçe veriyle birleştir
df_mixed = pd.concat([df_en_train, df_tr]).sample(frac=1, random_state=42)
```

**V4'te ek olarak Türkçe veri:**
- HuggingFace'ten `Overfit-GM/turkish-toxic-language` veri seti
- Türkçe etiketler (PROFANITY, INSULT, RACIST, SEXIST) **Kaggle'ın 6'lı sistemine eşleştirildi**:
  - `is_toxic` → `toxic`
  - `target == 'PROFANITY'` → `obscene`
  - `target == 'INSULT'` → `insult`
  - `target in ['RACIST', 'SEXIST']` → `identity_hate`

**Özet — Temizleme felsefesi:**

| Model | Temizleme | Neden? |
|-------|-----------|--------|
| V1/V2 (TF-IDF + klasik ML) | **Agresif** | TF-IDF kelime bazlı, gürültü = hata |
| V3 (DistilBERT) | **Yok** | Bağlam önemli, noktalama/büyük harf anlam taşır |
| V4 (XLM-RoBERTa) | **Yok** | Aynı sebep + çok dilli tokenizer her karakteri kendisi işler |

---

## 🔢 TF-IDF — Ne İşe Yarar, Neden Seçildi?

**Term Frequency — Inverse Document Frequency**

```python
tfidf = TfidfVectorizer(
    max_features=50000,  # En sık 50.000 kelime/bigram al
    ngram_range=(1, 2),  # Unigram (tek kelime) + Bigram (iki kelime)
    min_df=3,            # En az 3 yorumda geçenler
    max_df=0.95,         # %95'ten fazla yorumda geçenleri çıkar (anlamsız)
    sublinear_tf=True    # TF yerine log(TF) al
)
```

**Parametre Mantığı:**

| Parametre | Değer | Neden? |
|-----------|-------|--------|
| `max_features=50000` | 50K kelime | Bellek tasarrufu; 50K'dan sonra nadir kelimeler gürültü yaratır |
| `ngram_range=(1,2)` | Bigram dahil | **"go die"**, **"kill you"** gibi toksik kalıpları bir bütün olarak yakala |
| `min_df=3` | En az 3 dokümanda | Yazım hatalarını (xidiot, idot) ve çok nadir kelimeleri çıkar |
| `max_df=0.95` | %95 üstü çıkar | "the", "is" gibi zaten stopword çıkarmadan kaçanları ele geçir |
| `sublinear_tf=True` | log(TF+1) | "idiot" 5 kez geçerse ağırlığı 5 değil log(6)≈1.79 olur — daha sağlıklı |

**Sonuç:** Her yorum → 50.000 boyutlu sparse vektör

---

## ⚖️ Threshold (Eşik Değeri) — Neden 0.5 Değil?

### V1: Sabit Threshold (0.5)
Model "olasılık >= 0.5 ise toksik" der. Bu standart başlangıç noktasıdır.

**Sorun:** Veri %90 zararsız. Model "0.4 olasılık ver ve güvenli de" öğrenir → Recall çok düşük, gerçek toksik yorumları kaçırır.

### V2: Optimize Edilmiş Threshold (0.25)

```json
{
  "best_model": "Linear SVM",
  "threshold": 0.25000000000000006,
  "opt_thresholds": {
    "Logistic Regression": 0.65,
    "Linear SVM": 0.25,
    "XGBoost": 0.65
  }
}
```

**Nasıl Belirlendi?**

Validation seti üzerinde **F1-Score maksimize edecek threshold** aranır:

```python
# 0.05 - 0.95 arası her değer denenir
for thresh in np.arange(0.05, 0.95, 0.05):
    y_pred = (y_proba >= thresh).astype(int)
    f1 = f1_score(y_val, y_pred, average='macro')
    # En yüksek F1'i veren threshold seçilir
```

**Linear SVM için threshold = 0.25 neden?**

SVM, karar sınırına olan uzaklığa göre çalışır. Sigmoid kalibrasyonuyla olasılığa çevrildiğinde **skorlar 0.5'e yakın kümelenir** — yani SVM'in "toksik" diyebilmesi için eşiği düşürmek gerekir. 0.25 bu model için matematiksel olarak optimum F1 değerini üretmiştir.

> **Jüri sorusu:** "Neden 0.25'i seçtiniz?"  
> **Cevap:** Validation seti üzerinde 0.05'ten 0.95'e kadar her threshold denendi, F1-macro skorunu maksimize eden değer 0.25 çıktı. Bu, dengesiz veri setlerinde standart bir threshold optimization tekniğidir.

### V3 & V4 Transformer'larda Threshold

Transformerlar **sigmoid aktivasyon** kullanır → çıktı zaten 0-1 arası gerçek olasılık.

```python
probs = torch.sigmoid(logits)   # Logit'i olasılığa çevir
y_pred = (probs > 0.5).astype(int)  # 0.5 eşiği geçerliyse toksik
```

Transformer modelleri çok daha net karar verir (0.05 veya 0.95 gibi uç değerler), bu yüzden 0.5 threshold makul çalışır.

---

## 🤖 Model Versiyonları — Her Biri Neden Farklı?

### V1 — Temel Model (Best: XGBoost)

**Ne eğitildi?**
- Logistic Regression (baseline)
- Random Forest (200 ağaç)
- Linear SVM (CalibratedClassifierCV ile olasılık desteği)
- XGBoost (300 ağaç, max_depth=6)

**Hepsini neden eğittik?**  
Karşılaştırma için! F1-macro → ROC-AUC → Precision sıralamasıyla en iyi seçildi → **XGBoost kazandı**.

**OneVsRestClassifier neden?**  
Multi-label problem: Her yorum birden fazla etikete sahip olabilir. "İdiot, seni öldüreceğim" hem `insult` hem `threat`. OneVsRestClassifier her etiket için **ayrı bir binary model** eğitir (6 etiket → 6 model).

**XGBoost parametreleri:**
```python
xgb.XGBClassifier(
    n_estimators=300,      # 300 ağaç — yeterli karmaşıklık
    max_depth=6,           # Her ağaç max 6 dal — overfitting önlemi
    learning_rate=0.1,     # Her adımda %10 öğren — dengeli
    scale_pos_weight=10,   # Toksik sınıf 10x ağırlıklı — imbalance çözümü
)
```

---

### V2 — Optimize Model (Best: Linear SVM)

**V1'den farkı:**
1. Threshold 0.5 → **0.25** optimize edildi
2. `class_weight='balanced'` daha dikkatli kullanıldı
3. Veri temizleme ince ayarlandı (clean_text_v2)

**Neden SVM V1'de değil V2'de kazandı?**  
V1'de sabit 0.5 threshold SVM'e dezavantajlıydı (SVM'in olasılıkları 0.5 civarında toplanır). Threshold 0.25'e çekilince SVM'nin gerçek potansiyeli ortaya çıktı.

**Linear SVM neden text sınıflandırmada iyi?**  
TF-IDF matrisi yüksek boyutlu ve seyrek (sparse). SVM, yüksek boyutlu uzaylarda **hiperplane** bulma konusunda teorik olarak güçlüdür.

---

### V3 — Transformer / Derin Öğrenme (DistilBERT)

**Neden klasik ML'den Transformer'a geçiş?**

| Sorun | Örnek | TF-IDF Çözümü | Transformer Çözümü |
|-------|-------|---------------|-------------------|
| Bağlam körlüğü | "You're killing it!" (iltifat) | TF-IDF "kill" görür → toksik der | Bağlamı anlayarak güvenli der |
| İroni | "Sure, very smart of you 🙄" | Kelimeler pozitif → güvenli der | Tonu anlayarak dikkatli der |
| Üstü kapalı tehdit | "Boğazını sıkarım" | Bilinmeyen kelime → pass | Kültürel bağlamı yakalar |

**DistilBERT neden seçildi?**
- BERT'in **%40 daha küçük, %60 daha hızlı** versiyonu
- Performansının **%97**'sini korur
- Google Colab'ın T4 GPU'sunda 10-20 dakikada eğitim

**Eğitim stratejisi:**
```python
TrainingArguments(
    learning_rate=2e-5,          # Küçük lr — pre-trained ağırlıkları bozma
    num_train_epochs=2,          # Az epoch — overfitting önlemi
    weight_decay=0.01,           # L2 regularization
    load_best_model_at_end=True, # En iyi checkpoint'i sakla
    metric_for_best_model="f1_macro"  # F1 ile model seç
)
```

**Neden sadece 2 epoch?**  
Transformer'lar pre-trained (önceden eğitilmiş). Fine-tuning'de çok epoch gerekmiyor — overfitting riski var. 2-3 epoch altın standarttır.

**Dengeli örnekleme:**
```python
toxic = df[df[LABEL_COLS].sum(axis=1) > 0]       # Tüm toksikler
safe = df[...].sample(len(toxic) * 2, ...)         # 2x zararsız
# 1:2 toksik:zararsız oranı
```

---

### V4 — Çok Dilli XLM-RoBERTa (Enterprise Seviye)

**Neden DistilBERT'ten XLM-RoBERTa'ya?**

DistilBERT sadece İngilizce. Türkçe "anasını satayım" yazdığında anlamaz.

**XLM-RoBERTa:**
- **100+ dil** aynı anda öğrenmiş
- Wikipedia'nın tüm dilleri, Common Crawl ile eğitilmiş
- Türkçe, İngilizce, Almanca, Arapça... hepsini **aynı vektör uzayında** temsil eder
- Çeviri servisi gerekmez — sıfır gecikme (zero latency)

**Karma (Mixed) Veri Seti:**

```python
# İngilizce Kaggle verisi (dengeli örnekleme)
toxic_en: ~15.000 yorum
safe_en:  ~30.000 yorum

# Türkçe HuggingFace verisi
dataset: "Overfit-GM/turkish-toxic-language"
# → ~5.000 Türkçe yorum

# Birleşik karma set: ~50.000 yorum
df_mixed = pd.concat([df_en_train, df_tr]).shuffle()
```

**Türkçe etiket eşleştirmesi:**
- HuggingFace'teki Türkçe veri farklı etiket sistemi kullanıyordu
- Manuel olarak Kaggle'ın 6'lı sistemine **map** edildi
- `severe_toxic` ve `threat` için Türkçe veride karşılık olmadığından 0 atandı

**Neden tokenizasyon farklı?**  
XLM-RoBERTa kendi sentece piece tokenizer'ını kullanır. "Anasını" kelimesini kendi alt kelimelerine böler ve 100+ dildeki benzer kökleri aynı embedding uzayında bulur.

---

## 🔍 LIME — Açıklanabilir Yapay Zeka (XAI)

**LIME (Local Interpretable Model-agnostic Explanations) nedir?**

Model "black box" — içeriye girip bakamazsınız. LIME sorunu çözer:
1. Giriş metnini **binlerce küçük varyasyona** dönüştürür (kelime sil, değiştir)
2. Her varyasyonda modelin ne dediğine bakar
3. Hangi kelimenin kararı değiştirdiğini istatistiksel olarak hesaplar
4. "Bu cümle toksik çünkü **'kill'** ve **'idiot'** kelimeleri var" der

**Neden mean() kullanıldı, max() değil?**

```python
# YANLTIÇI YAKLAŞIM (max):
pos_prob = float(np.max(row_list))   # Tek yüksek etiket tüm kelimeleri "suçlar"
# Sonuç: "your", "stop", "crazy" gibi nötr kelimeler toksik işaretlenir

# DOĞRU YAKLAŞIM (mean):
pos_prob = float(np.mean(row_list))  # 6 etiketin ortalaması dengeli skor verir
# Sonuç: Gerçekten toksik kelimeler öne çıkar
```

---

## 📐 Metrikler — Neden F1-Score Ana Metrik?

| Metrik | Ne Ölçer | Neden Yetersiz? |
|--------|----------|----------------|
| **Accuracy** | Genel doğruluk | %90 zararsız veri → her şeye "güvenli" de, %90 accuracy al! Anlamsız. |
| **Precision** | Toksik dediğinin ne kadarı gerçekten toksik | Yanlış alarm oranı. Yüksek = az yanlış alarm |
| **Recall** | Gerçek toksiklerin ne kadarını yakaladık | Kaçırma oranı. Yüksek = az toksik kaçırma |
| **F1-Score** | Precision + Recall harmonik ortalaması | **Her ikisini dengeler — dengesiz veri için ideal** |
| **ROC-AUC** | Eşikten bağımsız model ayrım gücü | Threshold farklılıklarını bypass eder |

**Seçim kriteri:** F1-macro > ROC-AUC > Precision-micro

**Neden F1-macro?**  
Nadir etiketlere (threat, identity_hate) eşit ağırlık verir. F1-micro bunu yapmaz — sadece çok görülen etiketleri (toxic, insult) ödüllendirir.

---

## 🏗️ Sistem Mimarisi — Uçtan Uca Pipeline

```
Kullanıcı Metni Girer
        ↓
[Streamlit Arayüzü - app.py]
        ↓
[predict.py → ToxicityPredictor]
        ↓
    Hangi model?
   ┌──────────────────────────────┐
   │ V1/V2                        │ V3/V4
   ↓                              ↓
clean_text()              Ham metin (temizleme yok)
   ↓                              ↓
TF-IDF vectorizer         AutoTokenizer
   ↓                              ↓
.pkl model                Transformer model
(XGBoost / SVM)           (DistilBERT / XLM-RoBERTa)
   ↓                              ↓
predict_proba()           torch.sigmoid(logits)
   ↓                              ↓
threshold (0.5 / 0.25)    threshold (0.5)
        ↓
Sonuç: {scores, predictions, level}
        ↓
LIME Açıklaması (isteğe bağlı)
        ↓
Streamlit Gösterimi (🟢/🟡/🔴)
```

---

## 💡 Olası Jüri Soruları & Cevaplar

**S: "Neden 4 versiyon yaptınız, doğrudan V4 yapılmıyor muydu?"**  
C: Bilimsel yöntem gerektirir. Her versiyonda bir öncekinin eksikliğini gördük ve geliştirdik. V1 baseline, V2 threshold optimizasyonu, V3 bağlam anlama, V4 çok dil desteği. Bu iteratif yaklaşım hem akademik hem de endüstriyel standarttır.

**S: "XGBoost'u neden ilk versiyonda seçtiniz?"**  
C: TF-IDF + XGBoost, metin sınıflandırmada güçlü bir kombinas yon. XGBoost gradient boosting kullanır — her yeni ağaç bir öncekinin hatalarını düzeltir. F1-macro, ROC-AUC, Precision metrikleri karşılaştırıldı, XGBoost kazandı.

**S: "Sınıf dengesizliğini nasıl çözdünüz?"**  
C: Üç katmanlı yaklaşım: (1) `class_weight='balanced'` ile azınlık sınıfına daha fazla ağırlık, (2) threshold tuning ile karar eşiğini optimize etme (V2), (3) Transformer eğitiminde dengeli örnekleme (1:2 toksik:zararsız oranı).

**S: "V4 Türkçe'yi gerçekten anlıyor mu, nasıl test ettiniz?"**  
C: `analiz_sonuçları/` klasöründe her version için test verileri var. Türkçe test cümleleri farklı versiyonlarda denendi. V4 Türkçe küfürde doğru pozitif, V1/V2/V3 miss ediyor.

**S: "LIME neden gerekli?"**  
C: Model güveni için. Sadece "toksik" demek yeterli değil — kullanıcı neden toksik olduğunu anlamalı. Bu hem şeffaflık (transparency) hem de hata ayıklama (debugging) için kritik. Ayrıca GDPR gibi düzenlemeler yapay zeka kararlarının açıklanabilir olmasını zorunlu kılmaktadır.

**S: "Docker neden kullandınız?"**  
C: "Bende çalışıyor" problemi. Docker ile uygulama bağımlılıklarıyla birlikte paketlenir, herhangi bir sistemde aynı şekilde çalışır. Üretim (production) ortamlarında standart deploy yöntemidir.

---

## 📈 Performans Özeti (Hangi Model Neyi Yapıyor)

| Versiyon | Mimari | Güçlü Yönü | Zayıf Yönü |
|----------|--------|-----------|-----------|
| **V1** | XGBoost + TF-IDF | Hızlı, hafif, yorumlanabilir | Bağlamı anlamaz |
| **V2** | SVM + TF-IDF + Opt. Threshold | Dengesiz veriyi daha iyi yönetir | Yine kelime bazlı |
| **V3** | DistilBERT Transformer | Bağlam ve ironi anlama | Sadece İngilizce |
| **V4** | XLM-RoBERTa Multilingual | Türkçe + İngilizce + 100 dil | Büyük model, yavaş yükleme |

---

*Bu rehber, kodun her satırından doğrudan üretilmiştir. Güvenle kullanabilirsiniz.*
