"""
ToxicGuard - Yardımcı Fonksiyonlar
Proje genelinde kullanılan ortak fonksiyonlar.
"""

import os
import re
import string
import pandas as pd
import numpy as np
import nltk

# NLTK stopwords yükleme
try:
    from nltk.corpus import stopwords
    STOP_WORDS = set(stopwords.words('english'))
except LookupError:
    nltk.download('stopwords', quiet=True)
    from nltk.corpus import stopwords
    STOP_WORDS = set(stopwords.words('english'))

# Proje kök dizini
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Etiket sütunları
LABEL_COLS = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']

# Etiket Türkçe karşılıkları
LABEL_NAMES_TR = {
    'toxic': 'Toksik',
    'severe_toxic': 'Ağır Toksik',
    'obscene': 'Müstehcen',
    'threat': 'Tehdit',
    'insult': 'Hakaret',
    'identity_hate': 'Kimlik Nefreti'
}

# Toksisite seviyeleri
TOXICITY_LEVELS = {
    'safe': {'label': 'Güvenli', 'emoji': '🟢', 'color': '#2ecc71', 'threshold': 0.3},
    'warning': {'label': 'Dikkat', 'emoji': '🟡', 'color': '#f39c12', 'threshold': 0.6},
    'danger': {'label': 'Toksik', 'emoji': '🔴', 'color': '#e74c3c', 'threshold': 1.0}
}


def get_path(*parts):
    """Proje kök dizinine göre dosya yolu oluştur."""
    return os.path.join(PROJECT_ROOT, *parts)


def clean_text(text):
    """
    Metin temizleme pipeline.
    
    Adımlar:
    1. Küçük harfe çevirme
    2. HTML etiketlerini ve URL'leri kaldırma
    3. Sayı içeren kelimeleri uçurma
    4. Sadece İngilizce harfleri tutma
    5. Fazla boşlukları temizleme
    6. Stopword'leri çıkarma
    """
    text = str(text).lower()
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Sadece küçük harf ve Türkçe karakterleri tutma (ığüşöç)
    text = re.sub(r'[^a-z\sığüşöç]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    words = [w for w in text.split() if w not in STOP_WORDS]
    return " ".join(words)


def get_toxicity_level(score):
    """Toksisite skoruna göre seviye belirle."""
    if score < TOXICITY_LEVELS['safe']['threshold']:
        return TOXICITY_LEVELS['safe']
    elif score < TOXICITY_LEVELS['warning']['threshold']:
        return TOXICITY_LEVELS['warning']
    else:
        return TOXICITY_LEVELS['danger']


def load_clean_data():
    """Temizlenmiş veri setini yükle."""
    path = get_path('data', 'gercek_temizlenmis_veri.csv')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Temizlenmiş veri bulunamadı: {path}")
    df = pd.read_csv(path)
    # Boş satırları düşür
    df = df.dropna(subset=['cleaned_text'])
    df = df[df['cleaned_text'].str.strip() != '']
    df = df.reset_index(drop=True)
    return df


def load_raw_data():
    """Orijinal Kaggle eğitim verisini yükle."""
    path = get_path('datasset', 'train.csv')
    if not os.path.exists(path):
        raise FileNotFoundError(f"Eğitim verisi bulunamadı: {path}")
    return pd.read_csv(path)
