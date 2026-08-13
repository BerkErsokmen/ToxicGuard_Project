"""
ToxicGuard — Baseline Model Wrapper
HuggingFace'ten hazır eğitilmiş 'unitary/toxic-bert' modelini kullanarak
kendi modellerimizle bilimsel karşılaştırma yapar.

Neden unitary/toxic-bert?
- Aynı Jigsaw veri seti ile eğitilmiş → apples-to-apples karşılaştırma
- Aynı 6 etiket: toxic, severe_toxic, obscene, threat, insult, identity_hate
- Akademik community'nin kabul görmüş referans noktası (baseline)
- Bizim kendi modelimizin ne kadar iyi olduğunu kanıtlamak için ideal
"""

import os
import numpy as np
import warnings
warnings.filterwarnings('ignore')

from src.utils import LABEL_COLS, LABEL_NAMES_TR, get_toxicity_level

# Proje kökü ve yerel model klasörü
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_SRC_DIR)

# Yerel model yolları
_LOCAL_PATHS = {
    'toxic-bert': os.path.join(_PROJECT_ROOT, 'models', 'baseline_toxic_bert'),
    'multilingual-toxic': os.path.join(_PROJECT_ROOT, 'models', 'baseline_multilingual_toxic')
}

# Baseline model tanımları
BASELINE_MODELS = {
    'toxic-bert': {
        'model_id': 'unitary/toxic-bert',
        'name': 'ToxicBERT (Unitary)',
        'description': 'BERT-base, Jigsaw veri seti ile eğitilmiş endüstri standardı baseline.',
        'paper': 'https://huggingface.co/unitary/toxic-bert',
        'emoji': '🤖',
        'color': '#e67e22',
        'label_map': {
            'toxic': 'toxic',
            'severe_toxic': 'severe_toxic',
            'obscene': 'obscene',
            'threat': 'threat',
            'insult': 'insult',
            'identity_hate': 'identity_hate',
        }
    },
    'multilingual-toxic': {
        'model_id': 'unitary/multilingual-toxic-xlm-roberta',
        'name': 'Multilingual ToxicBERT (Unitary)',
        'description': 'XLM-RoBERTa tabanlı çok dilli baseline — V4 (Çok Dilli) ile birebir karşılaştırma için.',
        'paper': 'https://huggingface.co/unitary/multilingual-toxic-xlm-roberta',
        'emoji': '🌍',
        'color': '#8e44ad',
        'label_map': {
            'toxic': 'toxicity',
            'severe_toxic': 'severe_toxicity',
            'obscene': 'obscene',
            'threat': 'threat',
            'insult': 'insult',
            'identity_hate': 'identity_attack',
        }
    }
}


class BaselinePredictor:
    """
    Hazır eğitilmiş baseline modeli ile tahmin yapar.
    ToxicGuard modelleri ile doğrudan karşılaştırma için tasarlanmıştır.
    """

    def __init__(self, model_key: str = 'toxic-bert'):
        """
        Args:
            model_key: 'toxic-bert' veya 'multilingual-toxic'
        """
        if model_key not in BASELINE_MODELS:
            raise ValueError(f"Geçersiz model_key: {model_key}. Seçenekler: {list(BASELINE_MODELS.keys())}")

        self.model_key = model_key
        self.model_info = BASELINE_MODELS[model_key]
        self.model_id = self.model_info['model_id']
        self.label_map = self.model_info['label_map']
        self._pipeline = None  # Lazy loading

    def _load_model(self):
        """
        Modeli yükle.
        Önce projedeki 'models/baseline_...' klasörüne bakar.
        Orada yoksa HuggingFace'ten indirir VE local'e kaydeder (bir daha inmez).
        """
        if self._pipeline is None:
            from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer

            # Yerel model var mı kontrol et
            local_dir = _LOCAL_PATHS[self.model_key]
            local_config = os.path.join(local_dir, 'config.json')
            if os.path.exists(local_config):
                # ✅ Yerel klasörden yükle — internet gerekmez
                model_source = local_dir
            else:
                # 📥 HuggingFace'ten indir, aynı zamanda local'e kaydet
                model_source = self.model_id
                try:
                    os.makedirs(local_dir, exist_ok=True)
                    _tok = AutoTokenizer.from_pretrained(self.model_id)
                    _tok.save_pretrained(local_dir)
                    _mdl = AutoModelForSequenceClassification.from_pretrained(self.model_id)
                    _mdl.save_pretrained(local_dir)
                    model_source = local_dir  # Artık local'den yükle
                except Exception:
                    model_source = self.model_id  # Kaydedemezsek HF üzerinden devam

            self._pipeline = pipeline(
                "text-classification",
                model=model_source,
                top_k=None,
                truncation=True,
                max_length=512,
                device=-1,
            )
            # Isınma tahmini (ilk çıkarım gecikmesini önle)
            try:
                self._pipeline("warmup", truncation=True)
            except Exception:
                pass
        return self._pipeline


    def predict_text(self, text: str) -> dict:
        """
        Tek metin için baseline tahmin yap.
        Hiçbir zaman donmaz — tüm hatalar yakalanır.
        """
        try:
            pipe = self._load_model()
            raw_output = pipe(text, truncation=True)

            # Pipeline bazen liste içinde liste, bazen düz liste döner
            if raw_output and isinstance(raw_output[0], list):
                raw = raw_output[0]
            else:
                raw = raw_output

            # Tüm label'ları küçük harfe normalize et
            raw_dict = {item['label'].lower(): item['score'] for item in raw}

            scores = {}
            for our_label, baseline_label in self.label_map.items():
                # Önce direkt eşleşmeyi dene, sonra our_label'ı
                bl = baseline_label.lower()
                ol = our_label.lower()
                score = raw_dict.get(bl, raw_dict.get(ol, 0.0))
                scores[our_label] = float(score)

            # Eğer tüm skorlar 0 ise (label eşleşmedi) — raw_dict'i direkt kullan
            if all(s == 0.0 for s in scores.values()) and raw_dict:
                # raw_dict anahtarlarını LABEL_COLS sırasına map et
                raw_values = list(raw_dict.values())
                for i, label in enumerate(LABEL_COLS):
                    scores[label] = float(raw_values[i]) if i < len(raw_values) else 0.0

        except Exception as e:
            # Hata durumunda sıfır skorlu güvenli sonuç döndür — donma yok
            scores = {col: 0.0 for col in LABEL_COLS}

        predictions = {col: int(score >= 0.5) for col, score in scores.items()}
        overall_score = max(scores.values()) if scores else 0.0

        return {
            'original_text': text,
            'cleaned_text': text,
            'scores': scores,
            'predictions': predictions,
            'overall_score': overall_score,
            'level': get_toxicity_level(overall_score),
            'is_toxic': any(v == 1 for v in predictions.values()),
            'version': f'baseline_{self.model_key}',
            'threshold_used': 0.5,
            'model_name': self.model_info['name'],
        }

    def predict_batch(self, texts: list) -> list:
        """Toplu tahmin — bellek dostu batch işleme."""
        return [self.predict_text(t) for t in texts]


def compare_with_baseline(
    our_result: dict,
    baseline_result: dict,
    label_cols: list = None
) -> dict:
    """
    Kendi modelimizin sonucunu baseline ile karşılaştır.

    Args:
        our_result:       ToxicityPredictor.predict_text() çıktısı
        baseline_result:  BaselinePredictor.predict_text() çıktısı
        label_cols:       Karşılaştırılacak etiketler (varsayılan: LABEL_COLS)

    Returns:
        dict: Her etiket için delta, agreement ve genel istatistikler
    """
    if label_cols is None:
        label_cols = LABEL_COLS

    our_scores = our_result['scores']
    base_scores = baseline_result['scores']
    our_preds = our_result['predictions']
    base_preds = baseline_result['predictions']

    label_comparison = {}
    for label in label_cols:
        our_s = our_scores.get(label, 0.0)
        base_s = base_scores.get(label, 0.0)
        our_p = our_preds.get(label, 0)
        base_p = base_preds.get(label, 0)

        label_comparison[label] = {
            'our_score':      our_s,
            'baseline_score': base_s,
            'delta':          our_s - base_s,     # Pozitif → bizim modelimiz daha yüksek tahmin
            'our_pred':       our_p,
            'baseline_pred':  base_p,
            'agreement':      our_p == base_p,    # İkisi de aynı karara mı vardı?
        }

    # Genel anlaşma oranı
    agreement_count = sum(1 for v in label_comparison.values() if v['agreement'])
    agreement_rate = agreement_count / len(label_cols)

    # Ortalama mutlak fark
    mean_abs_delta = np.mean([abs(v['delta']) for v in label_comparison.values()])

    # Risk seviyesi uyumu
    our_level = our_result['level']['label']
    base_level = baseline_result['level']['label']
    level_agreement = our_level == base_level

    return {
        'label_comparison':  label_comparison,
        'agreement_rate':    agreement_rate,          # 0.0 - 1.0
        'mean_abs_delta':    mean_abs_delta,          # Ortalama skor farkı
        'our_overall':       our_result['overall_score'],
        'baseline_overall':  baseline_result['overall_score'],
        'overall_delta':     our_result['overall_score'] - baseline_result['overall_score'],
        'our_level':         our_level,
        'baseline_level':    base_level,
        'level_agreement':   level_agreement,
    }
