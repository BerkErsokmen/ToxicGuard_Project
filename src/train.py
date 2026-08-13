"""
ToxicGuard - Model Eğitimi
Birden fazla model eğitip karşılaştırma.
"""

import os
import time
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import LinearSVC
from sklearn.multiclass import OneVsRestClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    classification_report, roc_auc_score, f1_score,
    precision_score, recall_score, accuracy_score
)

from src.utils import LABEL_COLS, get_path


def select_best_result(results):
    """Best modeli deterministik sec: f1_macro, sonra roc_auc, sonra precision_micro."""
    def score_key(item):
        roc_auc = item.get('roc_auc')
        if roc_auc is None:
            roc_auc = -1.0
        return (
            item.get('f1_macro', -1.0),
            roc_auc,
            item.get('precision_micro', -1.0),
        )

    return max(results, key=score_key)


def load_train_test_data():
    """Eğitim ve test verilerini yükle."""
    data_dir = get_path('data')
    X_train = joblib.load(os.path.join(data_dir, 'X_train.pkl'))
    X_test  = joblib.load(os.path.join(data_dir, 'X_test.pkl'))
    y_train = joblib.load(os.path.join(data_dir, 'y_train.pkl'))
    y_test  = joblib.load(os.path.join(data_dir, 'y_test.pkl'))
    return X_train, X_test, y_train, y_test


def train_logistic_regression(X_train, y_train):
    """Logistic Regression modeli eğit (Baseline)."""
    print("\n📊 Model 1: Logistic Regression (Baseline)")
    print("-" * 50)
    
    model = OneVsRestClassifier(
        LogisticRegression(
            C=1.0,
            class_weight='balanced',
            solver='lbfgs',
            max_iter=1000,
            random_state=42
        ),
        n_jobs=-1
    )
    
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    print(f"  Eğitim süresi: {train_time:.1f}s")
    
    return model, train_time


def train_random_forest(X_train, y_train):
    """Random Forest modeli eğit."""
    print("\n🌲 Model 2: Random Forest")
    print("-" * 50)
    
    model = OneVsRestClassifier(
        RandomForestClassifier(
            n_estimators=200,
            class_weight='balanced',
            max_depth=None,
            random_state=42,
            n_jobs=-1
        )
    )
    
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    print(f"  Eğitim süresi: {train_time:.1f}s")
    
    return model, train_time


def train_svm(X_train, y_train):
    """Support Vector Machine modeli eğit (CalibratedClassifierCV ile olasılık desteği)."""
    print("\n⚡ Model 3: Linear SVM")
    print("-" * 50)
    
    # Her etikette ayri kalibrasyon uygulayarak multi-label uyumlu olasilik uret.
    calibrated_svc = CalibratedClassifierCV(
        estimator=LinearSVC(
            class_weight='balanced',
            max_iter=10000,
            random_state=42
        ),
        cv=3
    )
    model = OneVsRestClassifier(calibrated_svc, n_jobs=-1)
    
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    print(f"  Eğitim süresi: {train_time:.1f}s")
    
    return model, train_time


def train_xgboost(X_train, y_train):
    """XGBoost modeli eğit."""
    print("\n🚀 Model 4: XGBoost")
    print("-" * 50)
    
    try:
        import xgboost as xgb
    except ImportError:
        print("  ⚠️ XGBoost yüklü değil, atlanıyor.")
        return None, 0
    
    model = OneVsRestClassifier(
        xgb.XGBClassifier(
            n_estimators=300,
            max_depth=6,
            learning_rate=0.1,
            scale_pos_weight=10,
            use_label_encoder=False,
            eval_metric='logloss',
            random_state=42,
            n_jobs=-1,
            verbosity=0
        )
    )
    
    start = time.time()
    model.fit(X_train, y_train)
    train_time = time.time() - start
    print(f"  Eğitim süresi: {train_time:.1f}s")
    
    return model, train_time


def evaluate_model(model, X_test, y_test, model_name):
    """Model performansını değerlendir."""
    y_pred = model.predict(X_test)
    
    metrics = {
        'model': model_name,
        'accuracy': accuracy_score(y_test, y_pred),
        'f1_micro': f1_score(y_test, y_pred, average='micro', zero_division=0),
        'f1_macro': f1_score(y_test, y_pred, average='macro', zero_division=0),
        'precision_micro': precision_score(y_test, y_pred, average='micro', zero_division=0),
        'recall_micro': recall_score(y_test, y_pred, average='micro', zero_division=0),
    }
    
    # ROC-AUC (olasılık varsa)
    try:
        y_prob = model.predict_proba(X_test)
        if isinstance(y_prob, list):
            y_prob = np.array(y_prob)
            if y_prob.ndim == 3:
                y_prob = y_prob[:, :, 1].T
        metrics['roc_auc'] = roc_auc_score(y_test, y_prob, average='macro', multi_class='ovr')
    except Exception:
        metrics['roc_auc'] = None
    
    # Etiket bazlı detaylı rapor
    per_label = {}
    for i, col in enumerate(LABEL_COLS):
        per_label[col] = {
            'f1': f1_score(y_test[col], y_pred[:, i], zero_division=0),
            'precision': precision_score(y_test[col], y_pred[:, i], zero_division=0),
            'recall': recall_score(y_test[col], y_pred[:, i], zero_division=0),
        }
    metrics['per_label'] = per_label
    
    return metrics


def save_model(model, filename):
    """Modeli kaydet."""
    models_dir = get_path('models')
    os.makedirs(models_dir, exist_ok=True)
    path = os.path.join(models_dir, filename)
    joblib.dump(model, path)
    print(f"  Model kaydedildi: {path}")


def load_model_if_exists(filename):
    """Model dosyasi varsa yukle, yoksa None don."""
    models_dir = get_path('models')
    path = os.path.join(models_dir, filename)
    if os.path.exists(path):
        print(f"  Mevcut model bulundu, yeniden egitim atlandi: {path}")
        return joblib.load(path)
    return None


def run_training():
    """Tüm model eğitim pipeline'ını çalıştır."""
    print("=" * 60)
    print("FAZ 3: MODEL EĞİTİMİ & KARŞILAŞTIRMA")
    print("=" * 60)
    
    # Veriyi yükle
    X_train, X_test, y_train, y_test = load_train_test_data()
    print(f"Eğitim seti: {X_train.shape}")
    print(f"Test seti:   {X_test.shape}")
    
    results = []
    models = {}
    
    # Model 1: Logistic Regression
    lr_start = time.time()
    lr_model = load_model_if_exists('logistic_regression.pkl')
    if lr_model is None:
        lr_model, _ = train_logistic_regression(X_train, y_train)
        save_model(lr_model, 'logistic_regression.pkl')
    lr_time = time.time() - lr_start
    lr_metrics = evaluate_model(lr_model, X_test, y_test, 'Logistic Regression')
    lr_metrics['train_time'] = lr_time
    results.append(lr_metrics)
    models['logistic_regression'] = lr_model
    
    # Model 2: Random Forest
    rf_start = time.time()
    rf_model = load_model_if_exists('random_forest.pkl')
    if rf_model is None:
        rf_model, _ = train_random_forest(X_train, y_train)
        save_model(rf_model, 'random_forest.pkl')
    rf_time = time.time() - rf_start
    rf_metrics = evaluate_model(rf_model, X_test, y_test, 'Random Forest')
    rf_metrics['train_time'] = rf_time
    results.append(rf_metrics)
    models['random_forest'] = rf_model
    
    # Model 3: SVM
    svm_start = time.time()
    svm_model = load_model_if_exists('svm_model.pkl')
    if svm_model is None:
        svm_model, _ = train_svm(X_train, y_train)
        save_model(svm_model, 'svm_model.pkl')
    svm_time = time.time() - svm_start
    svm_metrics = evaluate_model(svm_model, X_test, y_test, 'Linear SVM')
    svm_metrics['train_time'] = svm_time
    results.append(svm_metrics)
    models['svm'] = svm_model
    
    # Model 4: XGBoost
    xgboost_skipped = False
    xgb_start = time.time()
    xgb_model = load_model_if_exists('xgboost_model.pkl')
    if xgb_model is None:
        xgb_model, _ = train_xgboost(X_train, y_train)
        if xgb_model is not None:
            save_model(xgb_model, 'xgboost_model.pkl')
    xgb_time = time.time() - xgb_start
    if xgb_model is not None:
        try:
            xgb_metrics = evaluate_model(xgb_model, X_test, y_test, 'XGBoost')
            xgb_metrics['train_time'] = xgb_time
            results.append(xgb_metrics)
            models['xgboost'] = xgb_model
        except Exception as exc:
            print(f"⚠️ XGBoost degerlendirme hatasi, model atlandi: {exc}")
            xgboost_skipped = True
    else:
        xgboost_skipped = True
    
    # En iyi modeli sec (f1_macro, roc_auc, precision_micro tie-break)
    best = select_best_result(results)
    best_name = best['model'].lower().replace(' ', '_')
    
    # Model isim eşleştirmesi
    name_map = {
        'logistic_regression': 'logistic_regression',
        'random_forest': 'random_forest',
        'linear_svm': 'svm',
        'xgboost': 'xgboost'
    }
    best_key = name_map.get(best_name, best_name)
    best_model = models[best_key]
    save_model(best_model, 'best_model.pkl')
    
    # Sonuçları yazdır
    print("\n" + "=" * 60)
    print("MODEL KARŞILAŞTIRMA SONUÇLARI")
    print("=" * 60)
    
    comparison_data = []
    for r in results:
        comparison_data.append({
            'Model': r['model'],
            'F1 (micro)': f"{r['f1_micro']:.4f}",
            'F1 (macro)': f"{r['f1_macro']:.4f}",
            'ROC-AUC': f"{r['roc_auc']:.4f}" if r['roc_auc'] else 'N/A',
            'Süre (s)': f"{r['train_time']:.1f}",
        })
    
    comparison_df = pd.DataFrame(comparison_data)
    print(comparison_df.to_string(index=False))
    
    print(f"\n🏆 En iyi model: {best['model']} (F1 macro: {best['f1_macro']:.4f})")
    if xgboost_skipped:
        print("ℹ️ XGBoost atlandi, egitim 3 model ile tamamlandi.")
    
    # Sonuçları dosyaya kaydet
    results_dir = get_path('reports', 'model_results')
    os.makedirs(results_dir, exist_ok=True)
    
    # Per-label sonuçları kaydet
    serializable_results = []
    for r in results:
        sr = {k: v for k, v in r.items() if k != 'per_label'}
        sr['per_label'] = r['per_label']
        serializable_results.append(sr)

    metadata = {
        'best_model': best['model'],
        'selection_rule': 'f1_macro > roc_auc > precision_micro',
        'xgboost_skipped': xgboost_skipped,
        'total_models_trained': len(results),
    }
    
    with open(os.path.join(results_dir, 'model_comparison.json'), 'w', encoding='utf-8') as f:
        json.dump({'metadata': metadata, 'results': serializable_results}, f, indent=2, ensure_ascii=False)
    
    comparison_df.to_csv(os.path.join(results_dir, 'model_comparison.csv'), index=False)
    print(f"\nSonuçlar reports/model_results/ altına kaydedildi.")
    
    return results, models


if __name__ == '__main__':
    run_training()
