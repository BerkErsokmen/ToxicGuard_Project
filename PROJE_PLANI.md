# 🛡️ ToxicGuard — Toksisite Tespit Sistemi

## Mezuniyet Projesi Detaylı Yol Haritası

> **Amaç:** Kullanıcıların girdiği yorumların toksiklik seviyesini yapay zeka ile ölçen,  
> ileride duygu analizi modülü ile genişletilebilen, Docker ile paketlenmiş tam bir NLP sistemi.  
> **Veri Seti:** Kaggle Jigsaw Toxic Comment Classification Challenge (~160.000 yorum)  
> **Etiketler:** `toxic`, `severe_toxic`, `obscene`, `threat`, `insult`, `identity_hate`  
> **Problem Tipi:** Multi-label Classification (Çok etiketli sınıflandırma)

---

## 📁 Hedef Proje Klasör Yapısı

```
mezuniyet_proje/
│
├── datasset/                          # Orijinal Kaggle verileri (DOKUNULMAZ)
│   ├── train.csv
│   ├── test.csv
│   └── test_labels.csv
│
├── data/                              # İşlenmiş veriler
│   ├── gercek_temizlenmis_veri.csv    # Temizlenmiş eğitim verisi
│   ├── X_train.pkl                    # Eğitim özellikleri (TF-IDF matrisi)
│   ├── X_test.pkl                     # Test özellikleri
│   ├── y_train.pkl                    # Eğitim etiketleri
│   └── y_test.pkl                     # Test etiketleri
│
├── notebooks/                         # Jupyter Notebook'lar (deney & analiz)
│   ├── 01_eda.ipynb                   # Keşifsel Veri Analizi
│   ├── 02_feature_engineering.ipynb   # Özellik çıkarma
│   ├── 03_model_training.ipynb        # Model eğitimi & karşılaştırma
│   └── 04_model_evaluation.ipynb      # Değerlendirme & metrikler
│
├── src/                               # Python kaynak kodları
│   ├── __init__.py
│   ├── data_cleaning.py               # Veri temizleme pipeline
│   ├── feature_extraction.py          # TF-IDF / embedding çıkarma
│   ├── train.py                       # Model eğitimi
│   ├── predict.py                     # Tahmin fonksiyonları
│   └── utils.py                       # Yardımcı fonksiyonlar
│
├── models/                            # Eğitilmiş modeller
│   ├── tfidf_vectorizer.pkl           # Kaydedilmiş TF-IDF vektörizer
│   ├── logistic_regression.pkl        # Logistic Regression modeli
│   ├── xgboost_model.pkl              # XGBoost modeli
│   └── best_model.pkl                 # Seçilen en iyi model
│
├── app/                               # Streamlit web uygulaması
│   ├── app.py                         # Ana uygulama
│   ├── pages/
│   │   ├── predict.py                 # Tahmin sayfası
│   │   ├── eda.py                     # EDA görselleri sayfası
│   │   └── model_comparison.py        # Model karşılaştırma sayfası
│   └── assets/                        # Logo, görseller
│
├── reports/                           # Çıktılar, grafikler, raporlar
│   ├── eda_plots/                     # EDA grafikleri (PNG)
│   └── model_results/                 # Model sonuç tabloları
│
├── docker/                            # Docker dosyaları
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── requirements.txt                   # Python bağımlılıkları
├── README.md                          # Proje tanıtımı
├── PROJE_PLANI.md                     # Bu dosya
└── .gitignore
```

---

## 🔬 FAZ 1 — Keşifsel Veri Analizi (EDA)

> **Hedef:** Veriyi tanımak, sınıf dağılımını anlamak, modellemeye hazırlık  
> **Çıktı:** `notebooks/01_eda.ipynb` + `reports/eda_plots/` altında grafikler  
> **Tahmini süre:** 1-2 gün

### 1.1 Etiket Dağılım Analizi
```python
# Her bir etiketin kaç kez "1" (toksik) olarak işaretlendiğini bul
label_cols = ['toxic','severe_toxic','obscene','threat','insult','identity_hate']
df[label_cols].sum().plot(kind='bar')
```
- Hangi toksisite türü en yaygın?
- Hangi toksisite türü en nadir? (Muhtemelen `threat` ve `identity_hate`)
- Toplam zararsız yorum yüzdesi nedir?

### 1.2 Sınıf Dengesizliği (Class Imbalance) Tespiti
- Toksik vs zararsız oranı (muhtemelen %90+ zararsız → **dengesiz veri problemi**)
- Bu dengesizlik modelimizi "her şeye zararsız de" demeye itebilir
- **Çözüm stratejileri** (Faz 3'te uygulanacak):
  - `class_weight='balanced'`
  - SMOTE (Synthetic Minority Oversampling)
  - Threshold tuning (karar eşiği optimizasyonu)

### 1.3 Multi-Label Korelasyon Analizi
```python
# Etiketler arası Pearson korelasyonu
import seaborn as sns
sns.heatmap(df[label_cols].corr(), annot=True, cmap='coolwarm')
```
- `obscene` olan yorum genelde `insult` da mıdır?
- `severe_toxic` olan yorum her zaman `toxic` midir?
- Bu korelasyonlar model mimarisini etkileyecek

### 1.4 Metin İstatistikleri
- Ortalama/medyan kelime sayısı (toksik vs zararsız)
- Kelime sayısı dağılım histogramı
- En kısa ve en uzun yorumlar

### 1.5 Kelime Bulutu (WordCloud)
```python
from wordcloud import WordCloud
# Toksik yorumlarda en sık geçen kelimeler
toxic_text = ' '.join(df[df['toxic']==1]['cleaned_text'])
wordcloud = WordCloud(width=800, height=400).generate(toxic_text)
```
- Toksik yorumlar kelime bulutu
- Zararsız yorumlar kelime bulutu
- Fark analizi

### 1.6 Boş/NaN Kontrolü
- `cleaned_text` sütununda boş satır var mı?
- Temizleme sonrası tamamen boşalan yorumlar varsa bunları düşür

---

## 🔧 FAZ 2 — Özellik Çıkarma (Feature Engineering)

> **Hedef:** Metin verisini makine öğrenmesi modellerinin anlayacağı sayısal formata çevirmek  
> **Çıktı:** `src/feature_extraction.py` + `data/` altında pickle dosyaları  
> **Tahmini süre:** 1-2 gün

### 2.1 TF-IDF Vektörizasyonu (Ana Yöntem)

TF-IDF (Term Frequency - Inverse Document Frequency), her kelimenin bir dokümandaki önemini sayısal olarak ifade eder.

```python
from sklearn.feature_extraction.text import TfidfVectorizer

tfidf = TfidfVectorizer(
    max_features=50000,      # En sık 50.000 kelimeyi al
    ngram_range=(1, 2),      # Tek kelime + ikili kelime grupları (bigram)
    min_df=3,                # En az 3 dokümanda geçen kelimeleri al
    max_df=0.95,             # %95'ten fazla dokümanda geçenleri çıkar
    sublinear_tf=True        # Logaritmik TF (büyük verilerde daha iyi)
)

X = tfidf.fit_transform(df['cleaned_text'])
```

**Parametrelerin açıklamaları:**
| Parametre | Değer | Neden? |
|-----------|-------|--------|
| `max_features` | 50000 | Bellek tasarrufu + gürültü azaltma |
| `ngram_range` | (1,2) | "go die" gibi toksik ikili kalıpları yakala |
| `min_df` | 3 | Nadir kelimeleri (yazım hataları vb.) çıkar |
| `max_df` | 0.95 | Çok yaygın, anlamsız kelimeleri çıkar |
| `sublinear_tf` | True | Kelime tekrar sayısının logaritmasını al |

### 2.2 Train/Test Split
```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, 
    df[label_cols], 
    test_size=0.2,           # %20 test, %80 eğitim
    random_state=42,         # Tekrarlanabilirlik
    stratify=df['toxic']     # Toksik/zararsız oranını koru
)
```

### 2.3 Vektörizer ve Verileri Kaydetme
```python
import joblib

joblib.dump(tfidf, 'models/tfidf_vectorizer.pkl')
joblib.dump(X_train, 'data/X_train.pkl')
joblib.dump(X_test, 'data/X_test.pkl')
joblib.dump(y_train, 'data/y_train.pkl')
joblib.dump(y_test, 'data/y_test.pkl')
```

### 2.4 (Opsiyonel) Word Embeddings
- GloVe veya FastText pre-trained embedding'leri
- BERT Tokenizer ile embedding çıkarma (Faz 3.4 için)
- Bu adım sadece derin öğrenme modeli kullanılacaksa gerekli

---

## 🤖 FAZ 3 — Model Tasarımı & Eğitimi

> **Hedef:** Birden fazla model eğitip karşılaştırmak, en iyi modeli seçmek  
> **Çıktı:** `src/train.py` + `models/` altında .pkl dosyaları  
> **Tahmini süre:** 3-5 gün

### ⚠️ Multi-Label Strateji

Bu problem **multi-label** (her yorum birden fazla etikete sahip olabilir). İki yaklaşım var:

| Strateji | Açıklama | Avantaj | Dezavantaj |
|----------|----------|---------|------------|
| **OneVsRestClassifier** | Her etiket için ayrı bir binary model eğit | Basit, hızlı | Etiketler arası ilişkiyi yakalamaz |
| **ClassifierChain** | Etiketleri sıralı bağımlılıkla eğit | Etiket korelasyonunu yakalar | Daha yavaş |

```python
from sklearn.multiclass import OneVsRestClassifier
model = OneVsRestClassifier(base_estimator)
```

### 3.1 Model 1: Logistic Regression (Baseline)

**Neden başlıyoruz?** Hızlı, yorumlanabilir, güçlü bir baseline sağlar.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier

lr_model = OneVsRestClassifier(
    LogisticRegression(
        C=1.0,                    # Regularization gücü
        class_weight='balanced',  # Sınıf dengesizliğini telafi et
        solver='lbfgs',           # Büyük veri için optimize solver
        max_iter=1000,
        random_state=42
    )
)
lr_model.fit(X_train, y_train)
```

**Hiperparametre ayarları:**
- `C`: Regularization parametresi (küçük C = daha fazla regularization)
- `class_weight='balanced'`: Azınlık sınıflarına daha fazla ağırlık verir
- Cross-validation ile en iyi `C` değerini bul

### 3.2 Model 2: Random Forest / SVM

```python
# Random Forest
from sklearn.ensemble import RandomForestClassifier
rf_model = OneVsRestClassifier(
    RandomForestClassifier(n_estimators=200, class_weight='balanced', random_state=42)
)

# Support Vector Machine
from sklearn.svm import LinearSVC
svm_model = OneVsRestClassifier(
    LinearSVC(class_weight='balanced', max_iter=10000)
)
```

### 3.3 Model 3: XGBoost / LightGBM (Gradient Boosting)

**Neden?** Genelde tabular/metin veride en iyi sonucu verir.

```python
import xgboost as xgb

xgb_model = OneVsRestClassifier(
    xgb.XGBClassifier(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.1,
        scale_pos_weight=10,      # Sınıf dengesizliği telafisi
        use_label_encoder=False,
        eval_metric='logloss',
        random_state=42
    )
)
xgb_model.fit(X_train, y_train)
```

### 3.4 (Opsiyonel Bonus) Model 4: DistilBERT Fine-Tuning

> ⚠️ **GPU önerilir.** CPU'da çok yavaş olabilir. Google Colab ücretsiz GPU kullanılabilir.

```python
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification
from transformers import Trainer, TrainingArguments

tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
model = DistilBertForSequenceClassification.from_pretrained(
    'distilbert-base-uncased', 
    num_labels=6,                # 6 etiket
    problem_type='multi_label_classification'
)
```

**BERT avantajı:** Kelimelerin bağlamını anlayarak "you're killing it!" (iltifat) ile "I'll kill you" (tehdit) arasındaki farkı kavrayabilir.

### 3.5 Hiperparametre Optimizasyonu

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    'estimator__C': [0.1, 1, 10],
    'estimator__max_iter': [500, 1000]
}
grid_search = GridSearchCV(lr_model, param_grid, cv=3, scoring='f1_micro')
grid_search.fit(X_train, y_train)
print(f"En iyi parametreler: {grid_search.best_params_}")
```

### 3.6 Sınıf Dengesizliği Çözümleri

| Yöntem | Nasıl Çalışır | Ne Zaman Kullan |
|--------|--------------|-----------------|
| `class_weight='balanced'` | Azınlık sınıfına daha fazla ağırlık verir | İlk deneme |
| **SMOTE** | Azınlık sınıfından sentetik örnek üretir | Çok az toksik veri varsa |
| **Threshold Tuning** | Karar eşiğini 0.5'ten düşür (ör: 0.3) | Recall'ı artırmak istersen |
| **Focal Loss** | Zor örneklere daha fazla odaklanır | Derin öğrenme modelleri |

---

## 📏 FAZ 4 — Model Değerlendirme & Karşılaştırma

> **Hedef:** Modellerin performansını ölçüp en iyisini seçmek  
> **Çıktı:** `notebooks/04_model_evaluation.ipynb` + `reports/model_results/`  
> **Tahmini süre:** 1-2 gün

### 4.1 Metrikler

Her model ve her etiket için ayrı ayrı hesaplanacak:

| Metrik | Ne Ölçer | Neden Önemli |
|--------|----------|-------------|
| **Accuracy** | Genel doğruluk | Dengesiz veride yanıltıcı olabilir |
| **Precision** | Toksik dediğinin kaçı gerçekten toksik | Yanlış alarm oranı |
| **Recall** | Gerçek toksik yorumların kaçını buldu | Kaçırma oranı |
| **F1-Score** | Precision + Recall harmonik ortalaması | **Ana metriğimiz** |
| **ROC-AUC** | Model ayrım gücü | Eşikten bağımsız performans |

```python
from sklearn.metrics import classification_report, roc_auc_score

y_pred = model.predict(X_test)
y_prob = model.predict_proba(X_test)  # Olasılık skorları

# Her etiket için ayrı rapor
print(classification_report(y_test, y_pred, target_names=label_cols))

# ROC-AUC (macro ortalama)
auc_score = roc_auc_score(y_test, y_prob, average='macro')
```

### 4.2 Karşılaştırma Tablosu

| Model | F1 (micro) | F1 (macro) | ROC-AUC | Eğitim Süresi |
|-------|-----------|-----------|---------|--------------|
| Logistic Regression | ? | ? | ? | ? |
| Random Forest | ? | ? | ? | ? |
| XGBoost | ? | ? | ? | ? |
| DistilBERT (opsiyonel) | ? | ? | ? | ? |

### 4.3 Hata Analizi
- En çok yanlış tahmin edilen örnekler (False Positive + False Negative)
- Hangi toksisite türünde model en çok zorlanıyor?
- Confusion Matrix görselleştirme (her etiket için)

### 4.4 En İyi Modeli Kaydet
```python
import joblib
joblib.dump(best_model, 'models/best_model.pkl')
joblib.dump(tfidf, 'models/tfidf_vectorizer.pkl')
```

---

## 🌐 FAZ 5 — Streamlit Web Arayüzü

> **Hedef:** Kullanıcı dostu bir web arayüzü ile toksiklik tahmini  
> **Çıktı:** `app/app.py`  
> **Tahmini süre:** 3-5 gün

### 5.1 Ana Sayfa — Tahmin Arayüzü

**Kullanıcı akışı (2 mod):**

**Mod A — Tekli Yorum Analizi:**
```
[Kullanıcı metin girer] → [NLP Pipeline temizler] → [TF-IDF vektörizer] → [Model tahmin eder] → [Sonuç gösterilir]
```

**Mod B — Dosya Yükleme ile Toplu Analiz:**
```
[Kullanıcı .txt veya .csv yükler] → [Her satır/yorum ayrı ayrı analiz edilir] → [Sonuçlar tablo olarak gösterilir] → [CSV olarak indir]
```

**Dosya yükleme kuralları:**
- `.txt` dosyası: Her satır ayrı bir yorum olarak işlenir
- `.csv` dosyası: Kullanıcıdan yorum sütunu seçmesi istenir
- Maksimum dosya boyutu: 10 MB
- Toplu sonuçlar bir tablo (DataFrame) olarak gösterilir
- "Sonuçları İndir" butonu ile CSV olarak dışa aktarılabilir

**Arayüz bileşenleri:**
- Büyük metin girişi alanı (textarea)
- Dosya yükleme alanı (file_uploader — .txt ve .csv desteği)
- "Analiz Et" butonu
- Her etiket için toksisite skoru (çubuk grafik / gauge)
- Genel toksiklik seviyesi göstergesi (düşük/orta/yüksek)
- Renk kodlu sonuç: 🟢 Güvenli, 🟡 Dikkat, 🔴 Toksik
- Toplu analiz sonuç tablosu + CSV indirme butonu

### 5.2 EDA Sayfası
- Etiket dağılımı grafikleri
- Kelime bulutları
- Veri seti istatistikleri

### 5.3 Model Karşılaştırma Sayfası
- Tüm modellerin F1/AUC skorları
- Confusion matrix'ler
- En iyi model detayları

### 5.4 (Opsiyonel) Duygu Analizi Modülü
- İleride eklenebilecek ikinci bir sekme
- Pre-trained sentiment model (VADER veya TextBlob) ile hızlı entegrasyon
- Pozitif / Negatif / Nötr duygu skoru

---

## 🐳 FAZ 6 — Docker ile Paketleme

> **Hedef:** Projeyi Docker container'ı olarak paketleyip her yerde çalıştırılabilir hale getirmek  
> **Çıktı:** `docker/Dockerfile` + `docker/docker-compose.yml`  
> **Tahmini süre:** 1 gün

### 6.1 Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Bağımlılıkları kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# NLTK verilerini indir
RUN python -c "import nltk; nltk.download('stopwords')"

# Uygulama dosyalarını kopyala
COPY src/ ./src/
COPY models/ ./models/
COPY app/ ./app/

# Streamlit portunu aç
EXPOSE 8501

# Uygulamayı başlat
CMD ["streamlit", "run", "app/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### 6.2 docker-compose.yml

```yaml
version: '3.8'
services:
  toxicguard:
    build:
      context: ..
      dockerfile: docker/Dockerfile
    ports:
      - "8501:8501"
    volumes:
      - ../models:/app/models
    environment:
      - STREAMLIT_SERVER_HEADLESS=true
    restart: unless-stopped
```

### 6.3 Kullanım
```bash
# Image oluştur
docker-compose -f docker/docker-compose.yml build

# Çalıştır
docker-compose -f docker/docker-compose.yml up -d

# Tarayıcıda aç → http://localhost:8501
```

---

## 📝 FAZ 7 — Dokümantasyon & Sunum

> **Tahmini süre:** 3-5 gün

- [ ] Proje raporu hazırla (Giriş, Literatür, Yöntem, Bulgular, Sonuç)
- [ ] README.md yaz (kurulum, çalıştırma, ekran görüntüleri)
- [ ] Sunum (PowerPoint/Canva) hazırla
- [ ] GitHub'a push et (temiz commit geçmişi)
- [ ] Demo videosu çek (Streamlit üzerinden canlı tahmin)

---

## 🔮 FAZ 8 — Gelecek Çalışmalar (V4 Serisi)

> **Hedef:** Sistemi Türkçe argo ve kültürel bağlamı anlayacak şekilde "Kurumsal (Enterprise)" seviyeye taşımak cihaz ve gecikme optimizasyonları yapmak.

### 8.1 Çok Dilli (Multilingual) Model Mimarisine Geçiş
- `DistilBERT` yerine HuggingFace'ten `XLM-RoBERTa` veya `mBERT` mimarisinin temel alınması.
- Anlık çeviri servisleri kullanılmadan (gecikme yaratmadan - zero latency) vektörel uzayda anlamsal eşleşme ile Türkçe mesajların test edilebilmesi.

### 8.2 Karma Veri Seti ile Fine-Tuning (Altın Standart)
- Mevcut **Kaggle Jigsaw (İngilizce)** veri setinin yanına, akademik/güvenilir **Türkçe Argo ve Toksik Yorum** veri setlerinin eklenerek "Karma (Mixed) Veri Seti" oluşturulması.
- Modelin sadece genel toksisiteyi değil, Türkiye'ye özgü yaratıcı hakaretleri, kinayeleri ve kültürel bağlamı da yüksek isabet oranıyla tespit edebilmesi.

### 8.3 Açıklanabilir Yapay Zeka (XAI) Entegrasyonu ve Optimizasyon
- Modeli kör bir kutu (black box) olmaktan çıkarıp, **LIME / SHAP** entegrasyonu ile modelin tam olarak hangi kelime veya heceye takılarak o yoruma "toksik" teşhisi koyduğunu Streamlit arayüzünde renklendirerek göstermek.
- Inference hızı için Model Quantization yapılıp dosya boyutunun düşürülmesi.

---

## 📦 Gerekli Kütüphaneler (requirements.txt)

```
# Temel
pandas==2.2.3
numpy==2.0.2

# NLP & Metin İşleme
nltk==3.9.1
scikit-learn==1.6.1

# Modeller
xgboost==2.1.3
lightgbm==4.5.0

# Görselleştirme
matplotlib==3.10.1
seaborn==0.13.2
wordcloud==1.9.4

# Web Arayüzü
streamlit==1.41.1

# Model Kaydetme
joblib==1.4.2

# Opsiyonel (BERT)
# transformers==4.48.2
# torch==2.6.0
```

---

## ⏱️ Haftalık Zaman Çizelgesi

| Hafta | Faz | Yapılacaklar |
|-------|-----|-------------|
| **1. Hafta** | Faz 1 + 2 | EDA + Feature Engineering (TF-IDF) |
| **2. Hafta** | Faz 3 | Model eğitimi (LR, XGB, RF) + hiperparametre ayarı |
| **3. Hafta** | Faz 4 + 5 | Değerlendirme + Streamlit arayüzü |
| **4. Hafta** | Faz 6 + 7 | Docker + Dokümantasyon + Sunum |

---

## 🚀 ŞİMDİ SONRAKI ADIM

**→ Faz 1: EDA** ile başlayacağız. `notebooks/01_eda.ipynb` oluşturup veri setinin yapısını ve dağılımını analiz edeceğiz.
