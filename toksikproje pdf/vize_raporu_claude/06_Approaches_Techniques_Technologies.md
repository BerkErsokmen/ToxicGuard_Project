# 5. APPROACHES, TECHNIQUES, AND TECHNOLOGIES TO BE USED

## 5.1 Programming Language and Core Ecosystem

The ToxicGuard system is implemented entirely in **Python 3**, the dominant programming language in the machine learning and data science ecosystem. Python's design philosophy emphasizes readability and rapid iteration, and its scientific computing ecosystem — Pandas, NumPy, Scikit-learn, Matplotlib, Seaborn, and the Hugging Face Transformers library — provides a comprehensive, well-maintained toolkit covering every stage of the pipeline from raw data ingestion through deployed model serving. All project dependencies are managed through a versioned `requirements.txt` file to ensure full reproducibility of results across different development environments.

## 5.2 Data Ingestion and Exploratory Data Analysis

Raw dataset ingestion uses **Pandas** DataFrames providing efficient in-memory tabular data management with vectorized column operations and grouped statistical aggregation. The initial pipeline phase devotes substantial effort to structured **Exploratory Data Analysis (EDA)**: computing label distributions across all six toxicity categories visualized as bar charts; calculating inter-label Pearson correlation coefficients to understand co-occurrence patterns; generating descriptive statistics and distribution histograms for comment length stratified by toxicity label; and producing word cloud visualizations comparing the most frequent vocabulary in toxic versus non-toxic comments. EDA findings directly inform downstream preprocessing decisions, class-imbalance strategy selection, and TF-IDF vectorizer hyperparameter configuration.

## 5.3 Text Preprocessing Pipeline

A rigorous multi-stage preprocessing pipeline normalizes raw user-generated text before feature extraction. The pipeline executes the following sequential transformations: (1) **Lowercase normalization** — all characters converted to lowercase to prevent vocabulary duplication; (2) **HTML removal** — residual markup tags stripped via BeautifulSoup and regular expressions; (3) **URL and special character removal** — hyperlinks and non-alphanumeric characters with no toxicity signal removed using Python's `re` module; (4) **Tokenization** — strings split into token arrays using NLTK's `word_tokenize`; (5) **Stop word removal** — high-frequency function words eliminated using NLTK's English stop word list; (6) **Lemmatization** — morphologically variant forms reduced to canonical dictionary roots using NLTK's WordNetLemmatizer.

For the Transformer-based DistilBERT model, aggressive preprocessing is bypassed: Transformer tokenizers operate on lightly cleaned raw text using subword Byte-Pair Encoding vocabularies that handle morphological variation implicitly, making lemmatization and stop word removal counterproductive.

## 5.4 Feature Engineering: TF-IDF Vectorization

The primary feature engineering technique for the classical ML pathway is **TF-IDF vectorization** [15] implemented via Scikit-learn's `TfidfVectorizer`. Rather than simply counting raw token occurrences — which biases models toward ubiquitous stop words — TF-IDF calculates a composite weight reflecting each token's frequency within a specific comment and inverse rarity across the corpus, amplifying the discriminative signal of toxicity-indicative vocabulary. The vectorizer extracts unigrams, bigrams, and trigrams simultaneously, capturing contextual modifier relationships that single-token features miss — "not hate speech" is semantically inverse to "hate speech," and "kill yourself" carries coordinated toxicity that its constituent unigrams do not individually convey. Key hyperparameters include `max_features` (50,000–100,000 most informative token types), `min_df` (minimum 2–5 document occurrences), and `sublinear_tf=True` (logarithmic term frequency scaling).

## 5.5 Class Imbalance Mitigation

Given extreme class imbalance in the Jigsaw dataset — non-toxic comments comprising ~90% of samples, with the rarest categories below 1% — two primary mitigation approaches are evaluated:

**Dynamic Class Weighting:** Classifiers are trained with `class_weight='balanced'`, automatically adjusting per-class loss contribution inversely proportional to class frequency. This up-weights the training signal from rare toxic examples without altering the data distribution.

**SMOTE (Synthetic Minority Over-sampling Technique):** Implemented via the `imbalanced-learn` library, SMOTE generates synthetic minority-class training instances by interpolating between existing minority examples in feature space [2]. Effectiveness is validated against stratified cross-validation folds to prevent data leakage.

Both approaches are complemented by **per-label decision threshold optimization**: an exhaustive threshold search over [0.1, 0.9] guided by the F1-score metric on the validation set identifies the optimal operating point balancing precision and recall for each specific toxicity category.

## 5.6 Machine Learning Models

Four classical ML families are systematically trained and evaluated. **Logistic Regression** serves as the interpretable baseline — its learned coefficient vector directly reveals which vocabulary items most strongly drive toxicity predictions. **Support Vector Machine** provides non-linear classification capacity via linear and RBF kernel configurations. **Random Forest** is tuned via RandomizedSearchCV across `n_estimators`, `max_depth`, and `min_samples_leaf`. **XGBoost** [3] leverages iterative gradient boosting with `scale_pos_weight` for built-in imbalance handling. All models are wrapped in Scikit-learn `Pipeline` objects chaining preprocessing transformations and classifiers, preventing target leakage and ensuring reproducible experiment management.

## 5.7 Transformer-Based Model: DistilBERT

The V3 iteration introduces a **DistilBERT**-based Transformer model, implemented using the **Hugging Face Transformers** library and **PyTorch**. DistilBERT [13] retains 97% of BERT's [5] language understanding capability at 40% fewer parameters and significantly reduced inference cost. Fine-tuning appends a multi-label classification head (linear layer with sigmoid activations, one output per toxicity category) to the pre-trained encoder. Training uses the `AdamW` optimizer with a linear learning rate warmup schedule, binary cross-entropy loss with per-class weighting for imbalance correction, and early stopping guided by validation Macro F1-Score. Input is tokenized with DistilBERT's WordPiece tokenizer at a maximum sequence length of 128 tokens with uniform padding and truncation. Training is conducted on Google Colab Pro with NVIDIA T4 GPU acceleration.

## 5.8 Model Explainability: LIME

The system integrates **LIME (Local Interpretable Model-Agnostic Explanations)** [12] via the `lime` Python library. LIME generates post-hoc local explanations by perturbing input text — randomly masking individual tokens — and fitting a locally weighted linear surrogate model to the resulting prediction probability changes, identifying which specific tokens most strongly influenced the classification for each individual input. Token-level attribution scores are rendered as highlighted text in the Streamlit interface with color intensity indicating contribution strength, enabling moderators to verify whether predictions are based on genuine toxicity signals or spurious correlations and providing an evidentiary basis for appeals in the human-in-the-loop governance model.

## 5.9 Deployment: Streamlit Application

Finalized models are deployed within a **Streamlit** application providing a bilingual (English/Turkish) interface with a real-time single-comment analysis mode including LIME explanation visualization, a batch processing mode accepting CSV uploads and returning annotated output files, and a multi-version model selector enabling side-by-side comparison of V1 through V5 outputs. Classical ML models are serialized via **joblib**; the DistilBERT model uses Hugging Face's `save_pretrained` format. Lazy loading architecture minimizes startup time and memory consumption, enabling deployment on standard hardware without GPU requirements for the classical modeling pathway.
