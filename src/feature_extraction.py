"""
ToxicGuard - Özellik Çıkarma (Feature Extraction)
TF-IDF vektörizasyonu ve train/test split.
"""

import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split

from src.utils import LABEL_COLS, get_path, load_clean_data


def create_tfidf_features(df, max_features=50000):
    """
    TF-IDF vektörizasyonu uygula.
    
    Args:
        df: cleaned_text sütunu içeren DataFrame
        max_features: Maksimum kelime sayısı
    
    Returns:
        X: TF-IDF sparse matrix
        tfidf: Fit edilmiş TfidfVectorizer
    """
    print(f"TF-IDF vektörizasyonu başlıyor (max_features={max_features})...")
    
    tfidf = TfidfVectorizer(
        max_features=max_features,
        ngram_range=(1, 2),      # Unigram + bigram
        min_df=3,                # En az 3 dokümanda geçenler
        max_df=0.95,             # %95'ten fazla dokümanda geçenleri çıkar
        sublinear_tf=True        # Logaritmik TF
    )
    
    X = tfidf.fit_transform(df['cleaned_text'])
    print(f"TF-IDF matrisi oluşturuldu: {X.shape}")
    print(f"Kelime sayısı: {len(tfidf.vocabulary_)}")
    
    return X, tfidf


def split_and_save(df, X, test_size=0.2, random_state=42):
    """
    Train/test split yap ve pickle olarak kaydet.
    
    Args:
        df: Etiketleri içeren DataFrame
        X: TF-IDF feature matrisi
        test_size: Test oranı
        random_state: Rastgelelik tohumu
    
    Returns:
        X_train, X_test, y_train, y_test
    """
    y = df[LABEL_COLS]
    
    print(f"Train/Test split yapılıyor (test_size={test_size})...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=test_size,
        random_state=random_state,
        stratify=df['toxic']  # toxic sütununa göre stratify
    )
    
    print(f"Eğitim seti: {X_train.shape[0]} örnek")
    print(f"Test seti:   {X_test.shape[0]} örnek")
    
    # Kaydet
    data_dir = get_path('data')
    os.makedirs(data_dir, exist_ok=True)
    
    joblib.dump(X_train, os.path.join(data_dir, 'X_train.pkl'))
    joblib.dump(X_test,  os.path.join(data_dir, 'X_test.pkl'))
    joblib.dump(y_train, os.path.join(data_dir, 'y_train.pkl'))
    joblib.dump(y_test,  os.path.join(data_dir, 'y_test.pkl'))
    print("Train/test verileri data/ altına kaydedildi.")
    
    return X_train, X_test, y_train, y_test


def save_vectorizer(tfidf):
    """TF-IDF vektorizeri kaydet."""
    models_dir = get_path('models')
    os.makedirs(models_dir, exist_ok=True)
    path = os.path.join(models_dir, 'tfidf_vectorizer.pkl')
    joblib.dump(tfidf, path)
    print(f"TF-IDF vektörizer kaydedildi: {path}")


def run_feature_extraction():
    """Tam özellik çıkarma pipeline'ını çalıştır."""
    print("=" * 60)
    print("FAZ 2: ÖZELLİK ÇIKARMA (FEATURE EXTRACTION)")
    print("=" * 60)
    
    # Veriyi yükle
    df = load_clean_data()
    print(f"Yüklenen veri: {len(df)} satır")
    
    # TF-IDF
    X, tfidf = create_tfidf_features(df)
    
    # Vektorizeri kaydet
    save_vectorizer(tfidf)
    
    # Train/test split
    X_train, X_test, y_train, y_test = split_and_save(df, X)
    
    print("\n✅ Özellik çıkarma tamamlandı!")
    return X_train, X_test, y_train, y_test, tfidf


if __name__ == '__main__':
    run_feature_extraction()
