"""
ToxicGuard — API Tabanlı Baseline Tahminleyiciler

Google Perspective API ve OpenAI Moderation API entegrasyonu.
Model indirmeye gerek yok — doğrudan API çağrısı ile sonuç üretilir.
Her iki API da Türkçe dahil çok dilli metin destekler.
"""

from src.utils import LABEL_COLS, get_toxicity_level


# API Baseline tanımları (UI için meta bilgi)
API_BASELINES = {
    'perspective': {
        'name': 'Google Perspective API',
        'description': 'Google\'ın çok dilli toksisite API\'si. TR dahil 100+ dil destekler.',
        'emoji': '🔍',
        'color': '#4285f4',
        'key_label': 'Google Cloud API Key',
        'key_help': 'console.cloud.google.com → APIs & Services → Credentials',
    },
    'openai': {
        'name': 'OpenAI Moderation API',
        'description': 'OpenAI\'nin içerik moderasyon modeli. Ücretsiz, çok dilli.',
        'emoji': '🤖',
        'color': '#10a37f',
        'key_label': 'OpenAI API Key',
        'key_help': 'platform.openai.com → API Keys',
    },
}


class PerspectiveAPIPredictor:
    """
    Google Perspective API ile toksisite tahmini.

    Ücretsiz kullanım: 1000 istek/gün (ücretsiz kota)
    Türkçe dahil çok dilli.
    API Key almak için: console.cloud.google.com → Perspective API
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze"
        self.model_key = 'perspective'
        self.model_info = API_BASELINES['perspective']

    def predict_text(self, text: str) -> dict:
        """Perspective API ile tek metin analizi."""
        import requests

        payload = {
            "comment": {"text": text},
            # Dili otomatik algıla — Türkçe ve İngilizce her ikisi için çalışır
            "requestedAttributes": {
                "TOXICITY": {},
                "SEVERE_TOXICITY": {},
                "IDENTITY_ATTACK": {},
                "INSULT": {},
                "PROFANITY": {},
                "THREAT": {}
            }
        }

        try:
            response = requests.post(
                self.endpoint,
                params={"key": self.api_key},
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            attrs = data.get("attributeScores", {})
            scores = {
                'toxic':         attrs.get('TOXICITY', {}).get('summaryScore', {}).get('value', 0.0),
                'severe_toxic':  attrs.get('SEVERE_TOXICITY', {}).get('summaryScore', {}).get('value', 0.0),
                'obscene':       attrs.get('PROFANITY', {}).get('summaryScore', {}).get('value', 0.0),
                'threat':        attrs.get('THREAT', {}).get('summaryScore', {}).get('value', 0.0),
                'insult':        attrs.get('INSULT', {}).get('summaryScore', {}).get('value', 0.0),
                'identity_hate': attrs.get('IDENTITY_ATTACK', {}).get('summaryScore', {}).get('value', 0.0),
            }

        except requests.exceptions.HTTPError as e:
            if response.status_code == 400:
                raise RuntimeError(
                    "Perspective API: Dil desteklenmiyor veya metin çok kısa. "
                    "İngilizce veya Türkçe metin giriniz."
                )
            elif response.status_code == 403:
                raise RuntimeError("Perspective API: API Key geçersiz veya Perspective API aktif değil.")
            else:
                raise RuntimeError(f"Perspective API HTTP hatası: {e}")
        except requests.exceptions.Timeout:
            raise RuntimeError("Perspective API: Bağlantı zaman aşımına uğradı.")
        except Exception as e:
            raise RuntimeError(f"Perspective API hatası: {str(e)}")

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
            'version': 'baseline_perspective',
            'threshold_used': 0.5,
            'model_name': 'Google Perspective API',
        }

    def predict_batch(self, texts: list) -> list:
        """Toplu tahmin — rate limit için aralarında kısa bekleme."""
        import time
        results = []
        for text in texts:
            results.append(self.predict_text(text))
            time.sleep(0.2)  # 5 istek/sn üst limit
        return results


class OpenAIModerationPredictor:
    """
    OpenAI Moderation API ile toksisite tahmini.

    Ücretsiz (OpenAI hesabı gerekli).
    Çok dilli. Türkçe destekler.
    API Key almak için: platform.openai.com → API Keys
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.endpoint = "https://api.openai.com/v1/moderations"
        self.model_key = 'openai'
        self.model_info = API_BASELINES['openai']

    def predict_text(self, text: str) -> dict:
        """OpenAI Moderation API ile tek metin analizi."""
        import requests

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {"input": text}

        try:
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()

            result = data['results'][0]
            cats = result.get('category_scores', {})

            # OpenAI kategorilerini Jigsaw etiketlerine map et
            # Not: Birebir eşleme değil, en yakın semantik karşılık kullanıldı
            scores = {
                'toxic':         max(cats.get('harassment', 0.0), cats.get('harassment/threatening', 0.0)),
                'severe_toxic':  cats.get('harassment/threatening', 0.0),
                'obscene':       cats.get('sexual', 0.0),
                'threat':        max(cats.get('violence', 0.0), cats.get('harassment/threatening', 0.0)),
                'insult':        cats.get('harassment', 0.0),
                'identity_hate': max(cats.get('hate', 0.0), cats.get('hate/threatening', 0.0)),
            }
            is_flagged = result.get('flagged', False)

        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise RuntimeError("OpenAI API: API Key geçersiz veya süresi dolmuş.")
            elif response.status_code == 429:
                raise RuntimeError(
                    "OpenAI API: İstek limiti aşıldı (429).\n\n"
                    "Çözüm: OpenAI hesabınıza bir ödeme yöntemi ekleyin → "
                    "platform.openai.com → Billing → Add payment method\n"
                    "(Moderation API ücretsizdir, sadece hesap doğrulaması gerekir)\n\n"
                    "Alternatif olarak Google Perspective API'yi seçebilirsiniz — "
                    "kart gerektirmez, tamamen ücretsizdir."
                )
            else:
                raise RuntimeError(f"OpenAI API HTTP hatası: {e}")
        except requests.exceptions.Timeout:
            raise RuntimeError("OpenAI API: Bağlantı zaman aşımına uğradı.")
        except Exception as e:
            raise RuntimeError(f"OpenAI API hatası: {str(e)}")

        predictions = {col: int(score >= 0.5) for col, score in scores.items()}
        overall_score = max(scores.values()) if scores else 0.0

        return {
            'original_text': text,
            'cleaned_text': text,
            'scores': scores,
            'predictions': predictions,
            'overall_score': overall_score,
            'level': get_toxicity_level(overall_score),
            'is_toxic': is_flagged,
            'version': 'baseline_openai',
            'threshold_used': 0.5,
            'model_name': 'OpenAI Moderation API',
        }

    def predict_batch(self, texts: list) -> list:
        """Toplu tahmin."""
        return [self.predict_text(text) for text in texts]
