# MetricGuard Notebook Training Methods

This document outlines the machine learning algorithms, architectures, and training methodologies used across the different MetricGuard notebooks.

---

## 1. MetricGuard-V1.ipynb (Point Anomaly Detection)

**Goal:** Detect instantaneous spikes or drops in standard system metrics (CPU, Memory, Response Time).

* **Algorithm:** Isolation Forest (`sklearn.ensemble.IsolationForest`)
* **Learning Type:** Unsupervised Anomaly Detection
* **Hyperparameters:**
  * `n_estimators=100`: Uses 100 base decision trees in the ensemble.
  * `contamination=0.05`: Assumes a priori that 5% of the dataset consists of anomalies.
  * `random_state=42`: Ensures reproducibility.
* **Training Methodology:**
  1. The model is instantiated and fitted on the entirely scaled dataset (`model.fit(X_scaled)`).
  2. The algorithm builds isolation trees by randomly selecting features and split values. Anomalies are identified by their short average path lengths in the trees (they are easier to isolate).
  3. The model assigns an anomaly label: `1` for normal instances and `-1` for anomalies.
  4. The trained model and the associated feature scaler are serialized using `joblib` for deployment.

---

## 2. MetricGuard-V3.ipynb (Temporal Anomaly Detection)

**Goal:** Detect long-term behavioral drift and anomalous sequences over time across multiple hardware metrics.

* **Algorithm:** LSTM Autoencoder (TensorFlow / Keras)
* **Learning Type:** Unsupervised Deep Learning (Sequence-to-Sequence Reconstruction)
* **Architecture:**
  * **Input:** Sequences spanning 20 time steps with 9 features `(20, 9)`.
  * **Encoder:** Two LSTM layers (128 units $\rightarrow$ 64 units) compressing the sequence into a latent representation.
  * **Bridge:** `RepeatVector(20)` to prepare the latent vector for reconstruction.
  * **Decoder:** Two LSTM layers (64 units $\rightarrow$ 128 units) scaling back up.
  * **Output:** `TimeDistributed(Dense(9))` mapping the sequence back to its original 9 feature dimensions.
* **Hyperparameters:**
  * **Optimizer:** Adam
  * **Loss Function:** Mean Squared Error (MSE)
  * **Epochs:** 50
  * **Batch Size:** 64
  * **Validation Split:** 10%
  * **Shuffle:** `False` (Critical for time-series to maintain temporal sequence order).
* **Training Methodology:**
  1. The autoencoder is trained to map the input sequence to itself (`model.fit(X_train, X_train)`). By doing this, it learns the fundamental patterns of "normal" system behavior.
  2. After training, the Mean Squared Error (MSE) reconstruction loss is calculated for the entire training set.
  3. An **Anomaly Threshold** is statistically determined by finding the 99th percentile of the training reconstruction loss.
  4. During inference (on the test set), any sequence with a reconstruction loss exceeding this threshold is flagged as an anomaly.

---

## 3. MetricGuard-V4.ipynb (Log Anomaly Detection)

**Goal:** Detect unusual patterns in application log events using an event occurrence matrix.

* **Algorithm:** Isolation Forest (`sklearn.ensemble.IsolationForest`)
* **Learning Type:** Unsupervised Anomaly Detection (Evaluated via supervised metrics)
* **Hyperparameters:**
  * `n_estimators=200`: Uses a larger forest (200 trees) due to the higher dimensionality of the log event matrix.
  * `contamination=0.03`: Assumes an anomaly rate of 3%.
  * `random_state=42`: Ensures reproducibility.
* **Training Methodology:**
  1. The data is split into 80% training and 20% testing sets using `train_test_split`.
  2. The Isolation Forest is trained exclusively on the training subset (`model.fit(X_train)`).
  3. The model makes predictions on the unseen test set. The default Isolation Forest outputs (`1` for normal, `-1` for anomaly) are remapped to `0` and `1` to align with the ground truth labels.
  4. Because this specific dataset includes actual labels (`Success` / `Fail`), the unsupervised predictions are robustly evaluated against these ground truth labels using a confusion matrix, accuracy score, and classification report.
  5. The model is saved to `metricguard_log_model.pkl` for backend integration.
