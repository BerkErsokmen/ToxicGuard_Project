# 4. STANDARDS TO BE USED

The development and deployment of ToxicGuard adheres to several recognized engineering and software quality standards:

**IEEE 730 — Software Quality Assurance:** Governs the validation and verification processes across the development lifecycle, mandating documented test protocols for accuracy, latency, and failure recovery across model versions.

**PEP 8 — Python Style Guide:** All Python source code strictly conforms to PEP 8 conventions for indentation, naming, and code layout, enforced via automated static analysis tools. Compliance ensures long-term readability and maintainability for external reviewers or contributing developers.

**W3C WCAG 2.1 — Web Accessibility Guidelines:** The Streamlit application targets Level AA conformance, ensuring sufficient color contrast ratios in both light and dark display modes, descriptive labels for all form elements, and keyboard-accessible navigation for all interface components.

**ISO/IEC 25010 — Software Quality Model:** Model evaluation adheres to the SQuaRE quality framework, assessing Functional Suitability via Macro F1-Score and per-label AUC-ROC metrics, and Performance Efficiency via measured inference latency targets (under 200 ms for classical models; under 2 seconds for DistilBERT) under realistic operational load conditions.

**Scikit-learn API Conventions:** All pipeline components implement standard `fit`/`transform`/`predict` interfaces, ensuring full compatibility with Scikit-learn's Pipeline abstraction and enabling clean experiment management.
