"""
ToxicGuard - Tahmin Fonksiyonları
Eğitilmiş model ile yeni metin tahminleri.
V1/V2 versiyon desteği.
"""

import os
import json
import warnings
# Colab'da farklı versiyon ile eğitilmiş modellerin uyarılarını sustur
warnings.filterwarnings('ignore', category=UserWarning)
warnings.filterwarnings('ignore', message='.*InconsistentVersionWarning.*')
warnings.filterwarnings('ignore', message='.*sklearn.*')

import joblib
import numpy as np
import pandas as pd

from src.utils import LABEL_COLS, LABEL_NAMES_TR, get_toxicity_level, get_path, clean_text


# Mevcut model versiyonları
AVAILABLE_VERSIONS = ['v1', 'v2', 'v3', 'v4', 'v5', 'v5_2', 'v5_02', 'v5_22']

VERSION_INFO = {
    'v1': {
        'name': 'V1 — Temel Model',
        'description': 'İlk eğitim: XGBoost best model, sabit threshold (0.5)',
        'best_model': 'XGBoost',
    },
    'v2': {
        'name': 'V2 — Optimize Model',
        'description': 'Yeniden eğitim: Optimize edilmiş threshold, clean_text_v2',
        'best_model': 'Linear SVM',
    },
    'v3': {
        'name': 'V3 — Transformer (Derin Öğrenme)',
        'description': 'Yeni nesil analiz: Cümle bağlamını ve ironiyi anlayan HuggingFace Transformer',
        'best_model': 'DistilBERT Multi-Label',
    },
    'v4': {
        'name': 'V4 — Çok Dilli (Multilingual) & XAI',
        'description': 'İngilizce + Türkçe karma veri seti ile eğitilmiş evrensel model',
        'best_model': 'XLM-RoBERTa',
    },
    'v5': {
        'name': 'V5 — Sarkazm Destekli (~130K)',
        'description': 'SemEval irony + SARC + Overfit-GM TR ile genişletilmiş, etiket bazlı threshold optimizasyonu',
        'best_model': 'XLM-RoBERTa + Opt. Threshold',
    },
    'v5_2': {
        'name': 'V5.2 — Focal Loss (EN+TR, ~293K) 🏆',
        'description': 'Focal Loss + TweetEval + Toygar TR ile eğitilmiş nihai model. F1-macro: 0.7478',
        'best_model': 'XLM-RoBERTa + Focal Loss',
    },
    'v5_02': {
        'name': 'V5.02 — Cascade Pipeline (Toksisite + Sarkazm) 🔬',
        'description': 'V5.2 toksisite motoru + cardiffnlp/twitter-roberta-base-irony sarkazm modeli. İki aşamalı cascade mimari.',
        'best_model': 'XLM-RoBERTa + RoBERTa-Irony Cascade',
    },
    'v5_22': {
        'name': 'V5.22 — Two-Stage Cascade (Kendi İroni Modelimiz) 🎯',
        'description': 'V5.2 toksisite + SemEval-2018 & SARC Reddit ile eğitilmiş kendi ironi modelimiz. Tam bağımsız cascade mimari.',
        'best_model': 'XLM-RoBERTa (Toksik) + RoBERTa-Irony (Ours)',
    },
}


def get_available_versions():
    """Kullanılabilir model versiyonlarını döndür."""
    models_dir = get_path('models')
    versions = []
    for v in AVAILABLE_VERSIONS:
        v_dir = os.path.join(models_dir, v)
        if v == 'v3':
            v3_path_direct = os.path.join(models_dir, 'toxicguard_v3_transformer')
            v3_path_nested = os.path.join(models_dir, 'v3', 'toxicguard_v3_transformer')
            if (os.path.exists(v3_path_direct) and os.path.exists(os.path.join(v3_path_direct, 'config.json'))) or \
               (os.path.exists(v3_path_nested) and os.path.exists(os.path.join(v3_path_nested, 'config.json'))):
                versions.append(v)
        elif v == 'v4':
            v4_path_direct = os.path.join(models_dir, 'toxicguard_v4_multilingual')
            v4_path_nested = os.path.join(models_dir, 'v4', 'toxicguard_v4_multilingual')
            if (os.path.exists(v4_path_direct) and os.path.exists(os.path.join(v4_path_direct, 'config.json'))) or \
               (os.path.exists(v4_path_nested) and os.path.exists(os.path.join(v4_path_nested, 'config.json'))):
                versions.append(v)
        elif v == 'v5':
            v5_path_direct = os.path.join(models_dir, 'toxicguard_v5_sarcasm')
            v5_path_nested = os.path.join(models_dir, 'v5', 'toxicguard_v5_sarcasm')
            if (os.path.exists(v5_path_direct) and os.path.exists(os.path.join(v5_path_direct, 'config.json'))) or \
               (os.path.exists(v5_path_nested) and os.path.exists(os.path.join(v5_path_nested, 'config.json'))):
                versions.append(v)
        elif v == 'v5_2':
            v5_2_path_direct = os.path.join(models_dir, 'toxicguard_v5_2_focal')
            v5_2_path_nested = os.path.join(models_dir, 'v5_2', 'toxicguard_v5_2_focal')
            if (os.path.exists(v5_2_path_direct) and os.path.exists(os.path.join(v5_2_path_direct, 'config.json'))) or \
               (os.path.exists(v5_2_path_nested) and os.path.exists(os.path.join(v5_2_path_nested, 'config.json'))):
                versions.append(v)
        elif v == 'v5_02':
            # V5.02 = V5.2 mevcut + irony modeli HuggingFace'ten otomatik indirilir
            # V5.2 yoksa V5.02 de gösterilmez
            v5_2_path_direct = os.path.join(models_dir, 'toxicguard_v5_2_focal')
            v5_2_path_nested = os.path.join(models_dir, 'v5_2', 'toxicguard_v5_2_focal')
            if (os.path.exists(v5_2_path_direct) and os.path.exists(os.path.join(v5_2_path_direct, 'config.json'))) or \
               (os.path.exists(v5_2_path_nested) and os.path.exists(os.path.join(v5_2_path_nested, 'config.json'))):
                versions.append(v)
        elif v == 'v5_22':
            # V5.22 = V5.2 + kendi egittigimiz ironi modeli (toxicguard_irony_model_final)
            v5_2_ok = False
            v5_2_path_direct = os.path.join(models_dir, 'toxicguard_v5_2_focal')
            v5_2_path_nested = os.path.join(models_dir, 'v5_2', 'toxicguard_v5_2_focal')
            if (os.path.exists(v5_2_path_direct) and os.path.exists(os.path.join(v5_2_path_direct, 'config.json'))) or \
               (os.path.exists(v5_2_path_nested) and os.path.exists(os.path.join(v5_2_path_nested, 'config.json'))):
                v5_2_ok = True
            irony_ok = os.path.exists(os.path.join(models_dir, 'toxicguard_irony_model_final', 'config.json'))
            if v5_2_ok and irony_ok:
                versions.append(v)
        else:
            if os.path.exists(v_dir) and os.path.exists(os.path.join(v_dir, 'best_model.pkl')):
                versions.append(v)
    return versions


class ToxicityPredictor:
    """Toksisite tahmin sınıfı — versiyon destekli."""
    
    def __init__(self, version='v1', model_name='best_model.pkl', vectorizer_name='tfidf_vectorizer.pkl'):
        """
        Model ve vektorizeri yükle.
        
        Args:
            version: Model versiyonu ('v1' veya 'v2')
            model_name: Model dosya adı
            vectorizer_name: Vektörizer dosya adı
        """
        self.version = version
        models_dir = os.path.join(get_path('models'), version)
        self.label_cols = LABEL_COLS
        self.threshold = 0.5
        self.threshold_config = None
        
        if self.version in ['v3', 'v4', 'v5', 'v5_2']:
            # Transformer yüklemesi
            from transformers import AutoModelForSequenceClassification, AutoTokenizer
            import torch
            
            if self.version == 'v3':
                model_dir_direct = os.path.join(get_path('models'), 'toxicguard_v3_transformer')
                model_dir_nested = os.path.join(get_path('models'), 'v3', 'toxicguard_v3_transformer')
            elif self.version == 'v4':
                model_dir_direct = os.path.join(get_path('models'), 'toxicguard_v4_multilingual')
                model_dir_nested = os.path.join(get_path('models'), 'v4', 'toxicguard_v4_multilingual')
            elif self.version == 'v5':
                model_dir_direct = os.path.join(get_path('models'), 'toxicguard_v5_sarcasm')
                model_dir_nested = os.path.join(get_path('models'), 'v5', 'toxicguard_v5_sarcasm')
            else:  # v5_2
                model_dir_direct = os.path.join(get_path('models'), 'toxicguard_v5_2_focal')
                model_dir_nested = os.path.join(get_path('models'), 'v5_2', 'toxicguard_v5_2_focal')
            
            if os.path.exists(model_dir_nested):
                model_dir = model_dir_nested
            elif os.path.exists(model_dir_direct):
                model_dir = model_dir_direct
            else:
                raise FileNotFoundError(f"{self.version.upper()} Model klasörü bulunamadı.")
            
            self.device = 0 if torch.cuda.is_available() else -1
            self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
            
            # config.json içinde id2label eksik olabilir, bu pipeline kullanarak multi-label çözmek karışabilir.
            # O yüzden raw model import ediyoruz
            self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
            self.is_transformer = True
            
            # V5 / V5.2 için per-label threshold yükle
            if self.version in ['v5', 'v5_2']:
                threshold_file = 'v5_thresholds.json' if self.version == 'v5' else 'v5_2_thresholds.json'
                threshold_path = os.path.join(model_dir, threshold_file)
                if os.path.exists(threshold_path):
                    with open(threshold_path, 'r', encoding='utf-8') as f:
                        self.threshold_config = json.load(f)
                    # Genel threshold = toksik etiketinin threshold'u
                    self.threshold = self.threshold_config.get('toxic', 0.5)
                else:
                    # Fallback: V5.2 eğitim çıktısından bilinen değerler
                    if self.version == 'v5':
                        self.threshold_config = {
                            'toxic': 0.50, 'severe_toxic': 0.35, 'obscene': 0.55,
                            'threat': 0.10, 'insult': 0.45, 'identity_hate': 0.55
                        }
                    else:  # v5_2
                        self.threshold_config = {
                            'toxic': 0.40, 'severe_toxic': 0.30, 'obscene': 0.40,
                            'threat': 0.45, 'insult': 0.40, 'identity_hate': 0.40
                        }
                    self.threshold = self.threshold_config.get('toxic', 0.5)
        else:
            self.is_transformer = False
            model_path = os.path.join(models_dir, model_name)
            vectorizer_path = os.path.join(models_dir, vectorizer_name)
            
            if not os.path.exists(model_path):
                raise FileNotFoundError(f"Model bulunamadı: {model_path}")
            if not os.path.exists(vectorizer_path):
                raise FileNotFoundError(f"Vektörizer bulunamadı: {vectorizer_path}")
            
            self.model = joblib.load(model_path)
            self.vectorizer = joblib.load(vectorizer_path)
            
            # V2 için optimize threshold yükle
            threshold_path = os.path.join(models_dir, 'threshold_config.json')
            if os.path.exists(threshold_path):
                with open(threshold_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                self.threshold = config.get('threshold', 0.5)
                self.threshold_config = config
    
    # ── Context-Aware Modifier ──────────────────────────────────────────
    # Türkçe argo pozitif bağlam (iltifat amaçlı kullanılan argo kelimeler)
    _TR_ARGO       = {'manyak', 'pislik', 'şerefsiz', 'şerefsizim', 'hayvan',
                      'deli', 'çüş', 'vay anasını', 'ulan', 'oğlum', 'lan'}
    _TR_POSITIVE   = {'tebrik', 'helal', 'başardın', 'başarı', 'güzel', 'harika',
                      'efsane', 'süper', 'iyi', 'bravo', 'aferin', 'bitirdin',
                      'kazandın', 'seçildin', 'aldın', 'bildin', 'kaldırdın',
                      'yarattın', 'çizdin', 'atladın', 'yedin', 'koştun',
                      'gülmekten', 'sarıyor', 'lezzetli', 'görünüyorsun'}
    # İngilizce arkadaşça küfür (affective/friendly profanity)
    _EN_FRIENDLY_PROFANITY = {'bastard', 'madman', 'maniac', 'crazy', 'insane',
                               'sick', 'shit', 'bitch', 'fuck', 'damn', 'hell',
                               'bastards', 'son of a bitch', 'son of a gun'}
    _EN_POSITIVE   = {'amazing', 'incredible', 'legend', 'brilliant', 'awesome',
                      'well done', 'pull off', 'managed', 'actually did',
                      'impressed', 'earned', 'thanks', 'delicious', 'beautiful',
                      'good at', 'best', 'won', 'did it', 'epic', 'scored'}
    # ─────────────────────────────────────────────────────────────────────

    def _context_modifier(self, text: str, score: float) -> tuple[float, str]:
        """
        Bağlam tabanlı skor düzeltici.
        Argo/küfür içeren ama aslında arkadaşça / iltifat amaçlı cümleler için
        ham toksisite skorunu aşağı çeker.

        Returns:
            (düzeltilmiş_skor, açıklama_notu)
        """
        text_lower = text.lower()
        words      = set(text_lower.split())

        # Türkçe: argo + pozitif sinyal aynı cümlede
        tr_argo_hit     = bool(words & self._TR_ARGO)
        tr_positive_hit = bool(words & self._TR_POSITIVE)

        # İngilizce: arkadaşça küfür + pozitif sinyal aynı cümlede
        en_prof_hit = any(p in text_lower for p in self._EN_FRIENDLY_PROFANITY)
        en_pos_hit  = any(p in text_lower for p in self._EN_POSITIVE)

        if tr_argo_hit and tr_positive_hit:
            return score * 0.50, "TR argo+pozitif bağlam → skor yarıya indirildi"
        if en_prof_hit and en_pos_hit:
            return score * 0.55, "EN arkadaşça küfür+pozitif bağlam → skor düzeltildi"
        return score, ""

    def predict_text(self, text):
        """
        Tek bir metin için toksisite tahmini yap.
        
        Args:
            text: Analiz edilecek metin
            
        Returns:
            dict: Her etiket için skor ve genel seviye bilgisi
        """
        # Metin temizle
        cleaned = clean_text(text)
        
        if not cleaned.strip():
            return {
                'original_text': text,
                'cleaned_text': '',
                'scores': {col: 0.0 for col in self.label_cols},
                'predictions': {col: 0 for col in self.label_cols},
                'overall_score': 0.0,
                'level': get_toxicity_level(0.0),
                'is_toxic': False,
                'version': self.version,
                'threshold_used': self.threshold,
            }
        
        if self.is_transformer:
            # Transformer Inference
            import torch
            inputs = self.tokenizer(text, return_tensors="pt", padding=True, truncation=True, max_length=128)
            with torch.no_grad():
                outputs = self.model(**inputs)
                logits = outputs.logits
                probs = torch.sigmoid(logits).squeeze().tolist()
                
            if not isinstance(probs, list):
                probs = [probs]
                
            scores = {col: float(probs[i]) for i, col in enumerate(self.label_cols)}
        else:
            # TF-IDF dönüşümü
            X = self.vectorizer.transform([cleaned])
            
            # Olasılık tahminleri
            try:
                probas = self.model.predict_proba(X)
                if isinstance(probas, list):
                    # OneVsRestClassifier bazen list döner
                    scores = {col: float(probas[i][0, 1]) for i, col in enumerate(self.label_cols)}
                else:
                    scores = {col: float(probas[0, i]) for i, col in enumerate(self.label_cols)}
            except AttributeError:
                # predict_proba yoksa decision_function veya binary prediction kullan
                try:
                    decision = self.model.decision_function(X)
                    if hasattr(decision, 'toarray'):
                        decision = decision.toarray()
                    if isinstance(decision, np.ndarray):
                        if decision.ndim == 1:
                            scores = {col: float(1 / (1 + np.exp(-decision[i]))) for i, col in enumerate(self.label_cols)}
                        else:
                            scores = {col: float(1 / (1 + np.exp(-decision[0, i]))) for i, col in enumerate(self.label_cols)}
                    else:
                        scores = {col: 0.0 for col in self.label_cols}
                except AttributeError:
                    preds = self.model.predict(X)
                    scores = {col: float(preds[0, i]) for i, col in enumerate(self.label_cols)}
        
        # Binary tahminler: V5/V5.2 için per-label threshold, diğerleri için tek threshold
        if self.version in ['v5', 'v5_2'] and self.threshold_config:
            predictions = {
                col: int(score >= self.threshold_config.get(col, self.threshold))
                for col, score in scores.items()
            }
        else:
            predictions = {col: int(score >= self.threshold) for col, score in scores.items()}
        
        # Genel skor (en yüksek toksisite skoru)
        overall_score = max(scores.values())

        # V5 / V5.2 için context-aware düzeltme uygula
        context_modified = False
        context_note     = ""
        if self.version in ['v5', 'v5_2']:
            adjusted, context_note = self._context_modifier(text, overall_score)
            if adjusted < overall_score:
                context_modified = True
                overall_score    = adjusted
                # Skorları da orantılı düzelt (görselleştirme için)
                ratio = adjusted / max(max(scores.values()), 1e-9)
                scores = {k: v * ratio for k, v in scores.items()}
                # Tahminleri yeniden hesapla
                if self.threshold_config:
                    predictions = {
                        col: int(score >= self.threshold_config.get(col, self.threshold))
                        for col, score in scores.items()
                    }
                else:
                    predictions = {col: int(score >= self.threshold) for col, score in scores.items()}

        return {
            'original_text': text,
            'cleaned_text': cleaned,
            'scores': scores,
            'predictions': predictions,
            'overall_score': overall_score,
            'level': get_toxicity_level(overall_score),
            'is_toxic': any(v == 1 for v in predictions.values()),
            'version': self.version,
            'threshold_used': self.threshold,
            'context_modified': context_modified,
            'context_note': context_note,
        }
    
    def predict_proba_for_lime(self, texts):
        """
        LIME kütüphanesi için olasılık döndürücü wrapper fonksiyon.
        LIME, metin sınıflandırmasında (n_samples, n_classes) boyutlu
        olasılık listesi dönen bir fonksiyona ihtiyaç duyar.
        
        Transformer modeller (V3/V4) için batched inference kullanır — çok daha hızlı.
        
        NOT: Genel skor hesaplamasında max yerine mean kullanılır.
        max() kullanıldığında, LIME tek bir etiketin yüksek skorunu tüm
        kelimelere atfediyordu ve "your", "stop", "crazy" gibi nötr
        kelimeler de toksik olarak işaretleniyordu.
        mean() ile 6 etiketin ortalaması alınarak daha dengeli ve
        gerçekçi bir toksisite skoru elde edilir.
        """
        if self.is_transformer:
            import torch
            probas = []
            batch_size = 8  # GPU yoksa bile bellek dostu
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                inputs = self.tokenizer(
                    batch,
                    return_tensors="pt",
                    padding=True,
                    truncation=True,
                    max_length=128
                )
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    logits = outputs.logits
                    batch_probs = torch.sigmoid(logits)  # (B, num_labels)
                
                for row in batch_probs:
                    row_list = row.tolist()
                    if not isinstance(row_list, list):
                        row_list = [row_list]
                    # Genel skor = 6 etiketin ortalaması (mean)
                    # max() kullanınca nötr kelimeler yanlış pozitif alıyordu
                    pos_prob = float(np.mean(row_list))
                    probas.append([1.0 - pos_prob, pos_prob])
            return np.array(probas)
        else:
            results = self.predict_batch(texts)
            probas = []
            for r in results:
                # mean of all label scores instead of max
                pos_prob = float(np.mean(list(r['scores'].values())))
                neg_prob = 1.0 - pos_prob
                probas.append([neg_prob, pos_prob])
            return np.array(probas)
    
    def predict_batch(self, texts):
        """
        Birden fazla metin için toplu tahmin yap.
        
        Args:
            texts: Metin listesi
            
        Returns:
            list[dict]: Her metin için tahmin sonucu
        """
        return [self.predict_text(text) for text in texts]
    
    def predict_file(self, file_content, file_type='txt', column_name=None):
        """
        Dosya içeriğinden toplu tahmin yap.
        
        Args:
            file_content: Dosya içeriği (string veya bytes)
            file_type: 'txt' veya 'csv'
            column_name: CSV için yorum sütun adı
            
        Returns:
            pd.DataFrame: Tahmin sonuçları
        """
        if file_type == 'txt':
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            texts = [line.strip() for line in file_content.split('\n') if line.strip()]
        
        elif file_type == 'csv':
            import io
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            df = pd.read_csv(io.StringIO(file_content), sep=None, engine='python')
            
            if column_name and column_name in df.columns:
                texts = df[column_name].dropna().astype(str).tolist()
            else:
                # İlk metin sütununu bul
                text_cols = df.select_dtypes(include='object').columns
                if len(text_cols) == 0:
                    raise ValueError("CSV dosyasında metin sütunu bulunamadı.")
                texts = df[text_cols[0]].dropna().astype(str).tolist()
        else:
            raise ValueError(f"Desteklenmeyen dosya türü: {file_type}")
        
        # Toplu tahmin
        results = self.predict_batch(texts)
        
        # DataFrame'e çevir
        rows = []
        for r in results:
            row = {
                'yorum': r['original_text'][:200],  # Uzun yorumları kırp
                'toksisite_skoru': round(r['overall_score'], 4),
                'seviye': r['level']['label'],
            }
            for col in self.label_cols:
                row[LABEL_NAMES_TR[col]] = round(r['scores'][col], 4)
            rows.append(row)
        
        return pd.DataFrame(rows)


# ─────────────────────────────────────────────────────────────────────────────
# V5.02 — CASCADE PIPELINE: Toksisite (V5.2) + Sarkazm (twitter-roberta-irony)
# ─────────────────────────────────────────────────────────────────────────────

class V502CascadePredictor:
    """
    V5.02 Cascade Pipeline:
      Aşama 1 — ToxicGuard V5.2 (XLM-RoBERTa Focal Loss): 6 etiket toksisite tahmini
      Aşama 2 — cardiffnlp/twitter-roberta-base-irony: İroni/sarkazm tespiti

    Karar Mantığı:
      • Sadece toksik + ironi tespit edilirse → 'Sarkastik Toksisite'
      • Toksik ama ironi yok              → 'Doğrudan Hakaret'
      • İroni var ama toksik değil         → 'Zararsız İroni'
      • İkisi de yok                       → 'Güvenli'
    """

    IRONY_MODEL_NAME = 'cardiffnlp/twitter-roberta-base-irony'
    # İroni etiket endeksleri: 0=non_irony, 1=irony
    IRONY_THRESHOLD = 0.5
    # Modelin LOCAL klasör yolu — HuggingFace'ten indirme yapılmaz
    IRONY_LOCAL_DIR = os.path.join(get_path('models'), 'irony_roberta')

    def __init__(self):
        self.version = 'v5_02'
        self.label_cols = LABEL_COLS

        # ── Aşama 1: V5.2 toxicity predictor ──
        self._tox_predictor = ToxicityPredictor(version='v5_2')
        self.threshold = self._tox_predictor.threshold
        self.threshold_config = self._tox_predictor.threshold_config

        # ── Aşama 2: İroni modeli — SADECE local klasörden yükle ──
        if not os.path.isdir(self.IRONY_LOCAL_DIR) or \
           not os.path.exists(os.path.join(self.IRONY_LOCAL_DIR, 'config.json')):
            raise FileNotFoundError(
                f"V5.02 için ironi modeli bulunamadı.\n"
                f"Lütfen 'cardiffnlp/twitter-roberta-base-irony' modelini manuel olarak indirip\n"
                f"şu klasöre koyun: {self.IRONY_LOCAL_DIR}\n\n"
                f"İndirme adresi: https://huggingface.co/cardiffnlp/twitter-roberta-base-irony/tree/main\n"
                f"İndirilmesi gereken dosyalar: config.json, pytorch_model.bin (veya model.safetensors),\n"
                f"tokenizer_config.json, vocab.json, merges.txt, special_tokens_map.json"
            )

        from transformers import pipeline as hf_pipeline
        import torch
        device = 0 if torch.cuda.is_available() else -1
        self._irony_pipe = hf_pipeline(
            'text-classification',
            model=self.IRONY_LOCAL_DIR,
            tokenizer=self.IRONY_LOCAL_DIR,
            top_k=None,
            device=device,
            truncation=True,
            max_length=128,
        )

    def _get_irony_score(self, text):
        """İroni olasılığını (0-1) döndür."""
        try:
            results = self._irony_pipe(text[:512])
            # results: [[{label, score}, ...]]
            if isinstance(results[0], list):
                results = results[0]
            for item in results:
                lbl = item['label'].lower()
                if 'irony' in lbl and 'non' not in lbl:
                    return float(item['score'])
            return 0.0
        except Exception:
            return 0.0

    def predict_text(self, text):
        """V5.02 cascade tahmin — toksisite + ironi."""
        # Aşama 1: Toksisite
        tox_result = self._tox_predictor.predict_text(text)

        # Aşama 2: İroni
        irony_score = self._get_irony_score(text)
        is_ironic = irony_score >= self.IRONY_THRESHOLD

        # Cascade karar mantığı
        is_toxic = tox_result['is_toxic']
        overall_score = tox_result['overall_score']

        if is_toxic and is_ironic:
            cascade_label = 'Sarkastik Toksisite'
            cascade_emoji = '🎭'
            cascade_color = '#e67e22'
        elif is_toxic and not is_ironic:
            cascade_label = 'Doğrudan Hakaret'
            cascade_emoji = '🔴'
            cascade_color = '#e74c3c'
        elif not is_toxic and is_ironic:
            cascade_label = 'Zararsız İroni'
            cascade_emoji = '😏'
            cascade_color = '#3498db'
        else:
            cascade_label = 'Güvenli'
            cascade_emoji = '🟢'
            cascade_color = '#2ecc71'

        # Sonuç dict — predict_text formatıyla uyumlu (app.py bozulmaz)
        result = dict(tox_result)  # V5.2 çıktısının tamamını koru
        result['version'] = 'v5_02'
        result['irony_score'] = round(irony_score, 4)
        result['is_ironic'] = is_ironic
        result['cascade_label'] = cascade_label
        result['cascade_emoji'] = cascade_emoji
        result['cascade_color'] = cascade_color
        return result

    def predict_batch(self, texts):
        return [self.predict_text(t) for t in texts]

    def predict_proba_for_lime(self, texts):
        """LIME için olasılık döndürücü — toksisite motoru (V5.2) kullanılır."""
        return self._tox_predictor.predict_proba_for_lime(texts)

    def predict_file(self, file_content, file_type='txt', column_name=None):
        """Dosyadan toplu tahmin — predict_file ile uyumlu."""
        import io
        if file_type == 'txt':
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            texts = [line.strip() for line in file_content.split('\n') if line.strip()]
        elif file_type == 'csv':
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            df = pd.read_csv(io.StringIO(file_content), sep=None, engine='python')
            if column_name and column_name in df.columns:
                texts = df[column_name].dropna().astype(str).tolist()
            else:
                text_cols = df.select_dtypes(include='object').columns
                if len(text_cols) == 0:
                    raise ValueError("CSV dosyasında metin sütunu bulunamadı.")
                texts = df[text_cols[0]].dropna().astype(str).tolist()
        else:
            raise ValueError(f"Desteklenmeyen dosya türü: {file_type}")

        results = self.predict_batch(texts)
        rows = []
        for r in results:
            row = {
                'yorum': r['original_text'][:200],
                'toksisite_skoru': round(r['overall_score'], 4),
                'ironi_skoru': round(r['irony_score'], 4),
                'cascade_karar': r['cascade_label'],
                'seviye': r['level']['label'],
            }
            for col in self.label_cols:
                row[LABEL_NAMES_TR[col]] = round(r['scores'][col], 4)
            rows.append(row)
        return pd.DataFrame(rows)



# ─────────────────────────────────────────────────────────────────────────────
# V5.22 — TWO-STAGE CASCADE: V5.2 Toksisite + Kendi Eğittiğimiz İroni Modeli
# ─────────────────────────────────────────────────────────────────────────────

class V522CascadePredictor:
    """
    V5.22 Two-Stage Cascade:
      Aşama 1 — ToxicGuard V5.2 (XLM-RoBERTa): Toksisite tespiti
      Aşama 2 — ToxicGuard-Irony (kendi eğitimimiz): SemEval + SARC ile eğitilmiş

    V5.02'den farkı: ironi modeli hazır değil, kendi eğittiğimiz model.
    Model klasörü: models/toxicguard_irony_model_final/
    """

    IRONY_LOCAL_DIR = os.path.join(get_path('models'), 'toxicguard_irony_model_final')
    IRONY_THRESHOLD = 0.5

    def __init__(self):
        self.version    = 'v5_22'
        self.label_cols = LABEL_COLS

        # ── Aşama 1: V5.2 ──
        self._tox_predictor = ToxicityPredictor(version='v5_2')
        self.threshold       = self._tox_predictor.threshold
        self.threshold_config = self._tox_predictor.threshold_config

        # ── Aşama 2: Kendi İroni Modelimiz ──
        if not os.path.isdir(self.IRONY_LOCAL_DIR) or \
           not os.path.exists(os.path.join(self.IRONY_LOCAL_DIR, 'config.json')):
            raise FileNotFoundError(
                f"V5.22 için ironi modeli bulunamadı.\n"
                f"Önce Colab notebook'u çalıştırın ve modeli şuraya koyun:\n"
                f"{self.IRONY_LOCAL_DIR}\n"
                f"Notebook: otherthings/V5_22_irony_model_colab.ipynb"
            )

        from transformers import pipeline as hf_pipeline
        import torch
        device = 0 if torch.cuda.is_available() else -1
        self._irony_pipe = hf_pipeline(
            'text-classification',
            model=self.IRONY_LOCAL_DIR,
            tokenizer=self.IRONY_LOCAL_DIR,
            top_k=None,
            device=device,
            truncation=True,
            max_length=128,
        )

        # Eğitim bilgilerini yükle
        info_path = os.path.join(self.IRONY_LOCAL_DIR, 'toxicguard_irony_info.json')
        if os.path.exists(info_path):
            with open(info_path, 'r', encoding='utf-8') as f:
                self.irony_info = json.load(f)
                self.IRONY_THRESHOLD = self.irony_info.get('irony_threshold', 0.5)

    def _get_irony_score(self, text):
        """İroni olasılığını (0-1) döndür."""
        try:
            results = self._irony_pipe(text[:512])
            if isinstance(results[0], list):
                results = results[0]
            for item in results:
                if item['label'].lower() == 'irony':
                    return float(item['score'])
            return 0.0
        except Exception:
            return 0.0

    def predict_text(self, text):
        """V5.22 cascade tahmin."""
        tox_result  = self._tox_predictor.predict_text(text)
        irony_score = self._get_irony_score(text)
        is_ironic   = irony_score >= self.IRONY_THRESHOLD
        is_toxic    = tox_result['is_toxic']

        if is_toxic and is_ironic:
            cascade_label, cascade_emoji, cascade_color = 'Sarkastik Toksisite', '🎭', '#e67e22'
        elif is_toxic and not is_ironic:
            cascade_label, cascade_emoji, cascade_color = 'Doğrudan Hakaret', '🔴', '#e74c3c'
        elif not is_toxic and is_ironic:
            cascade_label, cascade_emoji, cascade_color = 'Zararsız İroni', '😏', '#3498db'
        else:
            cascade_label, cascade_emoji, cascade_color = 'Güvenli', '🟢', '#2ecc71'

        result = dict(tox_result)
        result['version']       = 'v5_22'
        result['irony_score']   = round(irony_score, 4)
        result['is_ironic']     = is_ironic
        result['cascade_label'] = cascade_label
        result['cascade_emoji'] = cascade_emoji
        result['cascade_color'] = cascade_color
        return result

    def predict_batch(self, texts):
        return [self.predict_text(t) for t in texts]

    def predict_proba_for_lime(self, texts):
        """LIME için — toksisite motoru kullanılır."""
        return self._tox_predictor.predict_proba_for_lime(texts)

    def predict_file(self, file_content, file_type='txt', column_name=None):
        import io
        if file_type == 'txt':
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            texts = [line.strip() for line in file_content.split('\n') if line.strip()]
        elif file_type == 'csv':
            if isinstance(file_content, bytes):
                file_content = file_content.decode('utf-8', errors='ignore')
            df = pd.read_csv(io.StringIO(file_content), sep=None, engine='python')
            if column_name and column_name in df.columns:
                texts = df[column_name].dropna().astype(str).tolist()
            else:
                text_cols = df.select_dtypes(include='object').columns
                if len(text_cols) == 0:
                    raise ValueError("CSV'de metin sütunu bulunamadı.")
                texts = df[text_cols[0]].dropna().astype(str).tolist()
        else:
            raise ValueError(f"Desteklenmeyen dosya türü: {file_type}")

        results = self.predict_batch(texts)
        rows = []
        for r in results:
            row = {
                'yorum':           r['original_text'][:200],
                'toksisite_skoru': round(r['overall_score'], 4),
                'ironi_skoru':     round(r['irony_score'], 4),
                'cascade_karar':   r['cascade_label'],
                'seviye':          r['level']['label'],
            }
            for col in self.label_cols:
                row[LABEL_NAMES_TR[col]] = round(r['scores'][col], 4)
            rows.append(row)
        return pd.DataFrame(rows)


def predict_single(text, version='v1'):
    """Hızlı tekli tahmin fonksiyonu."""
    predictor = ToxicityPredictor(version=version)
    return predictor.predict_text(text)


if __name__ == '__main__':
    # Test
    for ver in get_available_versions():
        print(f"\n{'='*60}")
        print(f"MODEL VERSİYONU: {ver.upper()}")
        print(f"{'='*60}")
        
        predictor = ToxicityPredictor(version=ver)
        
        test_texts = [
            "You are a wonderful person!",
            "I will kill you, you stupid idiot!",
            "This article needs some improvement.",
            "Go die you worthless piece of garbage",
        ]
        
        for text in test_texts:
            result = predictor.predict_text(text)
            level = result['level']
            print(f"\n{level['emoji']} \"{text[:60]}...\"")
            print(f"   Genel skor: {result['overall_score']:.3f} ({level['label']}) [threshold={result['threshold_used']}]")
            for col in LABEL_COLS:
                score = result['scores'][col]
                pred = '✓' if result['predictions'][col] else '✗'
                print(f"   {LABEL_NAMES_TR[col]:15s}: {score:.3f} [{pred}]")
