import pandas as pd
import re
import string
import nltk

# NLTK kütüphanelerini indirelim (ilk deşifrede sorun çıkmaması için)
# Başlangıçta indirildiğinden emin olun
try:
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))
except:
    nltk.download('stopwords')
    from nltk.corpus import stopwords
    stop_words = set(stopwords.words('english'))

def clean_text(text):
    # 1. Küçük harfe çevirme
    text = str(text).lower()
    
    # 2. HTML etiketlerini ve URL'leri kaldırma
    text = re.sub(r'<.*?>', '', text)
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    
    # 3. İçinde Soru, IP, ID vb. sayılar geçen her türlü kelime grubu ve sayıyı uçur
    text = re.sub(r'\w*\d\w*', '', text)
    
    # 4. Yalnızca İngilizce harfleri tut (Noktalama, sembol ve emojileri boşlukla değiştir)
    text = re.sub(r'[^a-z\s]', ' ', text)
    
    # 5. Yeni satır karakterlerini ve fazladan boşlukları temizleme
    text = re.sub(r'\s+', ' ', text).strip()
    
    # 6. Stopword'leri (gereksiz kelimeleri) çıkarma
    words = text.split()
    words = [word for word in words if word not in stop_words]

    
    # İsteğe bağlı: Stemming / Lemmatization yapılabilir
    
    return " ".join(words)

if __name__ == "__main__":
    print("Veri yükleniyor...")
    # Kaggle veri setinin yolu
    train_path = 'datasset/train.csv'
    
    try:
        df = pd.read_csv(train_path)
    except Exception as e:
        print(f"Hata: {e}")
        exit()
        
    print(f"Toplam kayıt sayısı: {len(df)}")
    
    print("\n--- Tüm Veri (150.000+ Satır) Temizleniyor ---")
    print("Bu işlem bilgisayarının hızına göre birkaç dakika sürebilir, lütfen arkada çalışırken bekle...")
    
    df['cleaned_text'] = df['comment_text'].apply(clean_text)
    
    # Sadece temizlenmiş metin + 6 etiket sütununu tut, id ve orijinal comment_text'i çıkar
    label_columns = ['toxic', 'severe_toxic', 'obscene', 'threat', 'insult', 'identity_hate']
    df_clean = df[['cleaned_text'] + label_columns]
    
    output_file = 'gercek_temizlenmis_veri.csv'
    df_clean.to_csv(output_file, index=False)
    print(f"İşlem tamam! Asıl Kaggle veri setine dokunulmadı.")
    print(f"Temiz veri '{output_file}' dosyasına kaydedildi.")
    print(f"Sütunlar: {list(df_clean.columns)}")
    print(f"İlk 3 satır örnek:")
    print(df_clean.head(3).to_string())

