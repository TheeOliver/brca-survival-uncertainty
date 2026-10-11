# Exploratory survival-uncertainty reliability comparison

All numbers below are read from saved aggregate evaluation outputs. The original test set has already been used: these comparisons are post hoc and cannot select a newly validated primary method. Frozen primary results remain the reference.

The one-sided method reports **[L, τ] for min(T, τ)**, equivalently a lower survival bound T ≥ L. The upper endpoint τ is a target boundary, not a predicted time by which survival ends. Primary and Qin intervals answer a two-sided question. Ridge addresses numerical stability; it does not repair censoring assumptions or establish clinical utility.

Test sample size(s): 495. Confidence intervals are 95% paired test-patient bootstrap intervals conditional on fitted models, calibration, and the training censoring fit. Observable coverage bounds are identification bounds, **not confidence intervals**. IPCW is assumption-dependent and shown only where supported. † marks intervals conditional on successful bootstrap resamples. Unavailable values are never replaced by zero.

For primary/lower methods, n_cal counts held-out calibration patients. For Qin methods, B counts successful bootstrap pivots; it is not a held-out sample size. All widths and width differences are months. pp denotes percentage points.

## Training diagnostics

Ridge and original Qin use the same training event pool. The unpenalized pilot is a shorter diagnostic run; its denominator differs from the complete original run.

| Endpoint | Features | Original Qin refits | Pilot refits | Ridge refits | Ridge resamples with constant columns | Event-pool effective size |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| Breast-cancer-specific survival | Clinical | 1000/1000 | 100/100 | 1000/1000 | 0 | 12.8 |
| Breast-cancer-specific survival | + PAM50 | 900/1000 | 91/100 | 1000/1000 | 44 | 12.8 |
| Overall survival | Clinical | 998/1000 | 100/100 | 1000/1000 | 1 | 104.5 |
| Overall survival | + PAM50 | 931/1000 | 89/100 | 1000/1000 | 47 | 104.5 |

| Endpoint | Horizon (months) | Training G(tau-) | IPCW support | Training patients observed through horizon | Restricted known-target effective size |
| --- | ---: | ---: | --- | ---: | ---: |
| Breast-cancer-specific survival | 120 | 0.6719 | supported | 471 | 714.9 |
| Breast-cancer-specific survival | 300 | 0.0148 | unsupported | 7 | 28.3 |
| Overall survival | 120 | 0.8243 | supported | 471 | 859.4 |
| Overall survival | 300 | 0.0538 | supported | 7 | 187.7 |

## Original and ridge Cox probability/ranking metrics

These are separately stored estimates and confidence intervals. No paired original-versus-ridge performance difference was computed; overlap of marginal intervals is not a test of a difference. Higher Uno C is better; lower IBS is better.

| Endpoint | Features | Cox fit | Uno C [CI] | IBS [CI] | Integration grid (months) |
| --- | --- | --- | ---: | ---: | ---: |
| Breast-cancer-specific survival | Clinical | Original | 0.686 [0.641, 0.730] | 0.141 [0.129, 0.153] | 28.973 to 120.000 |
| Breast-cancer-specific survival | Clinical | Ridge | 0.686 [0.641, 0.730] | 0.141 [0.128, 0.153] | 28.973 to 120.000 |
| Breast-cancer-specific survival | + PAM50 | Original | 0.696 [0.651, 0.739] | 0.142 [0.129, 0.154] | 28.973 to 120.000 |
| Breast-cancer-specific survival | + PAM50 | Ridge | 0.698 [0.652, 0.741] | 0.140 [0.128, 0.152] | 28.973 to 120.000 |
| Overall survival | Clinical | Original | 0.649 [0.612, 0.687] | 0.170 [0.155, 0.184] | 28.973 to 120.000 |
| Overall survival | Clinical | Ridge | 0.649 [0.612, 0.687] | 0.170 [0.155, 0.184] | 28.973 to 120.000 |
| Overall survival | + PAM50 | Original | 0.652 [0.616, 0.689] | 0.171 [0.157, 0.185] | 28.973 to 120.000 |
| Overall survival | + PAM50 | Ridge | 0.653 [0.617, 0.689] | 0.170 [0.156, 0.184] | 28.973 to 120.000 |

## Coverage, width, and paired comparisons at every registered setting

Method differences are **one-sided lower minus primary two-sided**, or **ridge Qin minus original Qin**, for the same model/feature arm. Positive width differences mean wider candidate intervals. Feature differences are **clinical + PAM50 minus clinical** within the same candidate method. These intervals quantify test resampling uncertainty, not full retraining uncertainty.

### Breast-cancer-specific survival · 120 months · 95% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 95.6 to 97.4 | 97.2 [95.3, 98.6] | 100.3 [100.1, 100.8] | 96.8 to 104.8 |
| Cox | Clinical | One-sided lower | 495 | 96.0 to 97.8 | 97.7 [96.2, 98.9] | 101.1 [100.5, 101.6] | 95.6 to 105.8 |
| Cox | Clinical | Original Qin Cox | 1000 | 96.4 to 98.0 | 97.8 [96.3, 99.1] | 103.3 [101.0, 103.4] | 99.2 to 105.2 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 96.2 to 97.8 | 97.6 [96.0, 98.8] | 103.3 [100.8, 103.3] | 98.9 to 105.2 |
| Cox | + PAM50 | Primary two-sided | 495 | 95.4 to 97.2 | 96.9 [95.2, 98.4] | 100.3 [100.0, 100.6] | 96.1 to 104.8 |
| Cox | + PAM50 | One-sided lower | 495 | 94.9 to 97.2 | 97.0 [95.5, 98.5] | 99.1 [98.1, 99.6] | 92.8 to 103.9 |
| Cox | + PAM50 | Original Qin Cox | 900 | 94.9 to 97.0 | 96.6 [94.8, 98.2] | 98.3 [96.8, 99.0] | 93.0 to 103.3 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 95.4 to 97.2 | 96.9 [95.2, 98.4] | 100.1 [100.0, 100.6] | 96.6 to 104.8 |
| Weibull | Clinical | Primary two-sided | 495 | 98.2 to 99.4 | 99.3 [98.3, 100.0] | 106.5 [106.0, 107.0] | 102.0 to 110.1 |
| Weibull | Clinical | One-sided lower | 495 | 96.0 to 98.0 | 97.9 [96.4, 99.1] | 98.7 [98.0, 99.7] | 90.2 to 105.6 |
| Weibull | + PAM50 | Primary two-sided | 495 | 97.8 to 99.4 | 99.3 [98.3, 100.0] | 107.0 [106.4, 107.4] | 101.8 to 110.6 |
| Weibull | + PAM50 | One-sided lower | 495 | 95.2 to 97.4 | 97.2 [95.7, 98.7] | 98.2 [97.0, 98.9] | 88.4 to 105.1 |
| RSF | Clinical | Primary two-sided | 495 | 96.6 to 98.4 | 98.3 [97.0, 99.4] | 100.3 [97.9, 101.3] | 92.8 to 106.5 |
| RSF | Clinical | One-sided lower | 495 | 96.6 to 98.4 | 98.3 [97.1, 99.4] | 100.8 [99.7, 102.2] | 92.2 to 109.0 |
| RSF | + PAM50 | Primary two-sided | 495 | 96.2 to 98.2 | 98.1 [96.7, 99.2] | 99.5 [98.4, 100.6] | 92.5 to 105.6 |
| RSF | + PAM50 | One-sided lower | 495 | 96.0 to 98.4 | 98.3 [97.0, 99.4] | 99.8 [98.7, 100.9] | 90.4 to 107.4 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +0.4 [-0.4, 1.2] | +0.4 [-0.4, 1.2] | +0.5 [-0.4, 1.5] | +0.8 [0.2, 0.9] |
| Cox ridge | Clinical / Ridge Qin Cox | -0.2 [-0.6, 0.0] | -0.2 [-0.6, 0.0] | -0.2 [-0.7, 0.0] | +0.0 [-2.3, 0.0] |
| Cox | + PAM50 / One-sided lower | -0.4 [-1.2, 0.4] | +0.0 [-0.6, 0.6] | +0.1 [-0.7, 0.9] | -1.1 [-1.8, -1.0] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.4 [0.0, 1.0] | +0.2 [0.0, 0.6] | +0.3 [0.0, 1.0] | +1.8 [1.3, 3.0] |
| Weibull | Clinical / One-sided lower | -2.2 [-3.8, -0.8] | -1.4 [-2.6, -0.4] | -1.4 [-2.8, -0.1] | -7.8 [-8.1, -7.3] |
| Weibull | + PAM50 / One-sided lower | -2.6 [-4.2, -1.2] | -2.0 [-3.2, -0.8] | -2.0 [-3.5, -0.6] | -8.8 [-9.4, -8.4] |
| RSF | Clinical / One-sided lower | +0.0 [-0.8, 0.8] | +0.0 [-0.8, 0.8] | -0.0 [-0.9, 0.8] | +0.5 [-0.0, 1.9] |
| RSF | + PAM50 / One-sided lower | -0.2 [-0.8, 0.4] | +0.2 [0.0, 0.6] | +0.2 [0.0, 0.7] | +0.3 [-0.5, 0.8] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -1.0 [-2.0, -0.2] | -0.6 [-1.4, 0.0] | -0.6 [-1.5, 0.0] | -2.0 [-2.9, -1.8] |
| Cox ridge | Ridge Qin Cox | -0.8 [-1.8, 0.0] | -0.6 [-1.4, 0.0] | -0.6 [-1.5, 0.0] | -3.2 [-3.2, -0.8] |
| Weibull | One-sided lower | -0.8 [-1.6, -0.2] | -0.6 [-1.4, 0.0] | -0.6 [-1.5, 0.0] | -0.5 [-1.6, -0.1] |
| RSF | One-sided lower | -0.6 [-1.6, 0.2] | +0.0 [-0.6, 0.6] | +0.0 [-0.6, 0.7] | -1.0 [-1.6, -0.5] |

### Breast-cancer-specific survival · 120 months · 90% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 92.9 to 95.4 | 95.0 [92.9, 96.8] | 94.5 [93.7, 94.9] | 89.0 to 99.0 |
| Cox | Clinical | One-sided lower | 495 | 89.7 to 94.9 | 94.6 [92.7, 96.4] | 90.1 [89.0, 90.9] | 79.8 to 100.0 |
| Cox | Clinical | Original Qin Cox | 1000 | 92.3 to 94.7 | 94.4 [92.2, 96.3] | 92.7 [92.5, 94.0] | 88.5 to 98.1 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 91.9 to 94.5 | 94.1 [92.0, 96.0] | 92.5 [91.5, 92.7] | 87.7 to 96.8 |
| Cox | + PAM50 | Primary two-sided | 495 | 92.9 to 95.4 | 95.0 [93.0, 96.8] | 94.0 [93.0, 94.5] | 87.6 to 98.8 |
| Cox | + PAM50 | One-sided lower | 495 | 88.9 to 94.7 | 94.4 [92.4, 96.3] | 88.1 [86.7, 89.6] | 75.8 to 99.4 |
| Cox | + PAM50 | Original Qin Cox | 900 | 91.7 to 94.1 | 93.6 [91.4, 95.5] | 91.1 [90.8, 92.1] | 85.0 to 96.1 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 92.1 to 94.5 | 94.1 [92.0, 96.0] | 92.0 [91.1, 92.5] | 86.6 to 97.6 |
| Weibull | Clinical | Primary two-sided | 495 | 93.5 to 96.2 | 95.9 [93.9, 97.4] | 94.5 [93.4, 95.4] | 85.9 to 101.3 |
| Weibull | Clinical | One-sided lower | 495 | 89.7 to 94.5 | 94.2 [92.1, 96.1] | 86.5 [85.1, 88.3] | 70.1 to 99.7 |
| Weibull | + PAM50 | Primary two-sided | 495 | 94.5 to 96.8 | 96.5 [94.8, 98.1] | 95.1 [94.0, 95.8] | 85.3 to 102.0 |
| Weibull | + PAM50 | One-sided lower | 495 | 89.5 to 95.2 | 94.8 [92.8, 96.8] | 86.4 [84.1, 87.8] | 67.3 to 99.8 |
| RSF | Clinical | Primary two-sided | 495 | 92.1 to 95.4 | 95.1 [93.1, 96.8] | 90.8 [89.7, 92.1] | 82.2 to 99.0 |
| RSF | Clinical | One-sided lower | 495 | 88.1 to 93.9 | 93.4 [91.2, 95.6] | 85.5 [83.2, 87.3] | 68.5 to 100.6 |
| RSF | + PAM50 | Primary two-sided | 495 | 91.5 to 95.6 | 95.3 [93.3, 97.1] | 91.4 [90.3, 92.5] | 82.0 to 99.0 |
| RSF | + PAM50 | One-sided lower | 495 | 87.5 to 95.2 | 94.8 [92.8, 96.7] | 87.6 [84.9, 91.8] | 62.4 to 100.9 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | -3.2 [-5.1, -1.4] | -0.4 [-1.4, 0.8] | -0.4 [-1.6, 0.9] | -4.4 [-5.2, -3.8] |
| Cox ridge | Clinical / Ridge Qin Cox | -0.4 [-1.0, 0.0] | -0.2 [-0.6, 0.0] | -0.2 [-0.7, 0.0] | -0.2 [-1.3, -0.1] |
| Cox | + PAM50 / One-sided lower | -4.0 [-5.7, -2.2] | -0.6 [-1.6, 0.4] | -0.6 [-1.8, 0.7] | -5.9 [-6.3, -4.6] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.4 [0.0, 1.0] | +0.4 [0.0, 1.0] | +0.5 [0.0, 1.4] | +0.9 [0.4, 1.0] |
| Weibull | Clinical / One-sided lower | -3.8 [-5.9, -2.0] | -1.6 [-3.0, -0.2] | -1.7 [-3.3, -0.1] | -8.0 [-8.7, -7.0] |
| Weibull | + PAM50 / One-sided lower | -5.1 [-7.1, -3.0] | -1.6 [-3.0, -0.4] | -1.7 [-3.3, -0.2] | -8.8 [-9.9, -8.1] |
| RSF | Clinical / One-sided lower | -4.0 [-6.1, -2.0] | -1.4 [-3.0, 0.0] | -1.6 [-3.4, -0.1] | -5.2 [-6.9, -3.9] |
| RSF | + PAM50 / One-sided lower | -4.0 [-5.9, -2.2] | -0.4 [-1.4, 0.6] | -0.5 [-1.6, 0.6] | -3.8 [-5.8, 0.3] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -0.8 [-2.2, 0.6] | -0.2 [-1.2, 0.6] | -0.2 [-1.3, 0.7] | -1.9 [-2.9, -0.5] |
| Cox ridge | Ridge Qin Cox | +0.2 [-0.4, 1.0] | +0.0 [-0.6, 0.6] | +0.0 [-0.6, 0.6] | -0.5 [-1.0, 0.0] |
| Weibull | One-sided lower | -0.2 [-1.8, 1.2] | +0.6 [-0.4, 1.8] | +0.7 [-0.4, 1.9] | -0.1 [-2.0, 0.7] |
| RSF | One-sided lower | -0.6 [-2.2, 1.0] | +1.2 [0.4, 2.2] | +1.3 [0.4, 2.6] | +2.1 [0.9, 4.7] |

### Breast-cancer-specific survival · 120 months · 80% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 83.8 to 90.5 | 89.8 [87.1, 92.2] | 78.4 [77.4, 79.3] | 68.1 to 87.9 |
| Cox | Clinical | One-sided lower | 495 | 81.6 to 90.5 | 89.6 [87.1, 92.2] | 67.2 [65.7, 71.1] | 32.9 to 95.6 |
| Cox | Clinical | Original Qin Cox | 1000 | 85.7 to 91.3 | 90.7 [88.1, 93.0] | 82.3 [82.0, 83.6] | 73.0 to 89.9 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 85.9 to 91.5 | 90.9 [88.4, 93.1] | 83.0 [82.0, 83.6] | 73.0 to 89.9 |
| Cox | + PAM50 | Primary two-sided | 495 | 82.8 to 90.7 | 90.0 [87.4, 92.3] | 77.3 [75.8, 78.8] | 65.1 to 88.1 |
| Cox | + PAM50 | One-sided lower | 495 | 79.0 to 89.9 | 89.0 [86.4, 91.5] | 63.1 [59.1, 65.0] | 29.2 to 92.9 |
| Cox | + PAM50 | Original Qin Cox | 900 | 83.8 to 90.7 | 89.9 [87.2, 92.3] | 80.2 [77.0, 82.1] | 70.5 to 89.1 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 86.3 to 91.9 | 91.3 [88.7, 93.4] | 82.1 [80.2, 83.0] | 71.6 to 89.9 |
| Weibull | Clinical | Primary two-sided | 495 | 82.4 to 90.1 | 89.3 [86.7, 91.7] | 74.4 [72.3, 76.2] | 58.0 to 87.4 |
| Weibull | Clinical | One-sided lower | 495 | 82.4 to 90.7 | 89.9 [87.4, 92.5] | 65.0 [61.5, 68.6] | 41.4 to 91.0 |
| Weibull | + PAM50 | Primary two-sided | 495 | 82.2 to 89.7 | 88.8 [86.0, 91.3] | 73.1 [70.9, 74.6] | 54.1 to 86.4 |
| Weibull | + PAM50 | One-sided lower | 495 | 81.2 to 90.5 | 89.7 [87.0, 92.2] | 63.2 [59.0, 66.1] | 38.9 to 90.0 |
| RSF | Clinical | Primary two-sided | 495 | 83.6 to 91.1 | 90.4 [87.8, 92.9] | 77.7 [75.4, 79.5] | 60.7 to 92.8 |
| RSF | Clinical | One-sided lower | 495 | 80.4 to 90.7 | 89.7 [87.1, 92.3] | 60.3 [59.3, 65.1] | 26.4 to 96.3 |
| RSF | + PAM50 | Primary two-sided | 495 | 82.4 to 90.9 | 90.2 [87.6, 92.7] | 77.0 [74.3, 81.2] | 51.8 to 90.3 |
| RSF | + PAM50 | One-sided lower | 495 | 80.4 to 90.5 | 89.6 [87.1, 92.0] | 57.9 [54.8, 69.1] | 21.3 to 91.8 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | -2.2 [-4.6, 0.4] | +0.0 [-2.0, 2.0] | -0.2 [-2.5, 2.1] | -11.2 [-11.8, -8.1] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.2 [0.0, 0.6] | +0.2 [0.0, 0.6] | +0.2 [0.0, 0.7] | +0.8 [-0.1, 0.8] |
| Cox | + PAM50 / One-sided lower | -3.8 [-6.3, -1.4] | -0.8 [-2.6, 1.0] | -1.1 [-3.2, 1.0] | -14.1 [-17.1, -13.5] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +2.4 [1.2, 3.8] | +1.2 [0.2, 2.2] | +1.4 [0.3, 2.5] | +1.9 [0.2, 4.2] |
| Weibull | Clinical / One-sided lower | +0.0 [-1.8, 1.8] | +0.6 [-1.0, 2.2] | +0.6 [-1.2, 2.5] | -9.4 [-10.9, -7.4] |
| Weibull | + PAM50 / One-sided lower | -1.0 [-3.0, 1.2] | +0.8 [-0.6, 2.4] | +0.9 [-0.8, 2.7] | -10.0 [-12.0, -8.3] |
| RSF | Clinical / One-sided lower | -3.2 [-5.3, -1.2] | -0.4 [-2.0, 1.0] | -0.6 [-2.4, 1.0] | -17.4 [-18.3, -14.1] |
| RSF | + PAM50 / One-sided lower | -2.0 [-4.0, 0.0] | -0.4 [-2.0, 1.0] | -0.6 [-2.3, 1.0] | -19.1 [-21.2, -9.8] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -2.6 [-4.2, -1.2] | -0.6 [-1.6, 0.2] | -0.6 [-1.7, 0.2] | -4.1 [-7.5, -2.9] |
| Cox ridge | Ridge Qin Cox | +0.4 [-1.0, 1.6] | +0.4 [-0.6, 1.4] | +0.4 [-0.7, 1.5] | -0.9 [-2.0, 0.0] |
| Weibull | One-sided lower | -1.2 [-2.6, 0.4] | -0.2 [-1.2, 0.6] | -0.2 [-1.3, 0.7] | -1.8 [-5.4, 0.2] |
| RSF | One-sided lower | +0.0 [-1.6, 1.6] | -0.2 [-1.2, 0.8] | -0.2 [-1.3, 1.1] | -2.4 [-5.4, 6.9] |

### Breast-cancer-specific survival · 300 months · 95% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 95.6 to 97.4 | unavailable | 280.3 [280.0, 280.6] | 276.6 to 284.8 |
| Cox | Clinical | One-sided lower | 495 | 96.0 to 97.8 | unavailable | 281.1 [280.5, 281.6] | 275.6 to 285.8 |
| Cox | Clinical | Original Qin Cox | 1000 | 94.9 to 98.0 | unavailable | 281.0 [280.6, 283.3] | 278.3 to 284.9 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 94.7 to 97.8 | unavailable | 280.8 [280.3, 283.3] | 278.1 to 284.8 |
| Cox | + PAM50 | Primary two-sided | 495 | 95.2 to 97.2 | unavailable | 280.0 [279.6, 280.3] | 275.9 to 284.8 |
| Cox | + PAM50 | One-sided lower | 495 | 94.9 to 97.2 | unavailable | 279.1 [278.1, 279.6] | 272.8 to 283.9 |
| Cox | + PAM50 | Original Qin Cox | 900 | 92.9 to 97.0 | unavailable | 276.6 [275.9, 278.1] | 272.1 to 280.8 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 93.1 to 97.0 | unavailable | 279.8 [279.2, 280.1] | 275.2 to 283.7 |
| Weibull | Clinical | Primary two-sided | 495 | 98.2 to 99.4 | unavailable | 286.5 [285.7, 286.8] | 281.6 to 290.0 |
| Weibull | Clinical | One-sided lower | 495 | 96.0 to 98.0 | unavailable | 278.7 [278.0, 279.7] | 270.2 to 285.6 |
| Weibull | + PAM50 | Primary two-sided | 495 | 97.8 to 99.4 | unavailable | 286.6 [285.8, 287.1] | 281.4 to 290.4 |
| Weibull | + PAM50 | One-sided lower | 495 | 95.2 to 97.4 | unavailable | 278.2 [277.0, 278.9] | 268.4 to 285.1 |
| RSF | Clinical | Primary two-sided | 495 | 96.6 to 98.4 | unavailable | 280.3 [277.9, 281.3] | 272.8 to 286.5 |
| RSF | Clinical | One-sided lower | 495 | 96.6 to 98.4 | unavailable | 280.8 [279.7, 282.2] | 272.2 to 289.0 |
| RSF | + PAM50 | Primary two-sided | 495 | 96.2 to 98.2 | unavailable | 279.5 [278.4, 280.6] | 272.5 to 285.6 |
| RSF | + PAM50 | One-sided lower | 495 | 96.0 to 98.4 | unavailable | 279.8 [278.7, 280.9] | 270.4 to 287.4 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +0.4 [-0.4, 1.2] | +0.4 [-0.4, 1.2] | unavailable | +0.8 [0.4, 1.2] |
| Cox ridge | Clinical / Ridge Qin Cox | -0.2 [-0.6, 0.0] | -0.2 [-0.6, 0.0] | unavailable | -0.2 [-2.3, 0.0] |
| Cox | + PAM50 / One-sided lower | -0.2 [-1.2, 0.6] | +0.0 [-0.6, 0.6] | unavailable | -0.9 [-1.8, -0.6] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.2 [-0.4, 1.0] | +0.0 [0.0, 0.0] | unavailable | +3.2 [1.9, 3.5] |
| Weibull | Clinical / One-sided lower | -2.2 [-3.8, -0.8] | -1.4 [-2.6, -0.4] | unavailable | -7.7 [-8.0, -7.0] |
| Weibull | + PAM50 / One-sided lower | -2.6 [-4.2, -1.2] | -2.0 [-3.2, -0.8] | unavailable | -8.4 [-9.2, -8.1] |
| RSF | Clinical / One-sided lower | +0.0 [-0.8, 0.8] | +0.0 [-0.8, 0.8] | unavailable | +0.5 [-0.0, 1.9] |
| RSF | + PAM50 / One-sided lower | -0.2 [-0.8, 0.4] | +0.2 [0.0, 0.6] | unavailable | +0.3 [-0.5, 0.8] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -1.0 [-2.0, -0.2] | -0.6 [-1.4, 0.0] | unavailable | -2.0 [-2.9, -1.8] |
| Cox ridge | Ridge Qin Cox | -1.6 [-2.8, -0.6] | -0.8 [-1.6, -0.2] | unavailable | -1.0 [-3.2, -0.7] |
| Weibull | One-sided lower | -0.8 [-1.6, -0.2] | -0.6 [-1.4, 0.0] | unavailable | -0.5 [-1.6, -0.1] |
| RSF | One-sided lower | -0.6 [-1.6, 0.2] | +0.0 [-0.6, 0.6] | unavailable | -1.0 [-1.6, -0.5] |

### Breast-cancer-specific survival · 300 months · 90% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 92.9 to 95.4 | unavailable | 274.4 [273.4, 274.9] | 268.4 to 279.0 |
| Cox | Clinical | One-sided lower | 495 | 89.7 to 94.9 | unavailable | 270.1 [269.0, 270.9] | 259.8 to 280.0 |
| Cox | Clinical | Original Qin Cox | 1000 | 90.5 to 94.7 | unavailable | 272.1 [271.1, 272.6] | 267.4 to 276.6 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 89.9 to 94.5 | unavailable | 271.4 [270.8, 272.1] | 265.7 to 275.7 |
| Cox | + PAM50 | Primary two-sided | 495 | 92.5 to 95.2 | unavailable | 273.1 [272.7, 274.0] | 266.8 to 278.0 |
| Cox | + PAM50 | One-sided lower | 495 | 88.9 to 94.7 | unavailable | 268.1 [266.7, 269.6] | 255.8 to 279.4 |
| Cox | + PAM50 | Original Qin Cox | 900 | 89.3 to 94.1 | unavailable | 270.3 [269.6, 271.0] | 263.2 to 275.2 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 89.7 to 94.3 | unavailable | 270.9 [269.9, 271.5] | 263.6 to 275.7 |
| Weibull | Clinical | Primary two-sided | 495 | 93.5 to 96.2 | unavailable | 274.3 [272.4, 274.6] | 265.1 to 280.8 |
| Weibull | Clinical | One-sided lower | 495 | 89.7 to 94.5 | unavailable | 266.5 [265.1, 268.3] | 250.1 to 279.7 |
| Weibull | + PAM50 | Primary two-sided | 495 | 94.5 to 96.8 | unavailable | 274.3 [272.7, 275.4] | 264.3 to 281.5 |
| Weibull | + PAM50 | One-sided lower | 495 | 89.5 to 95.2 | unavailable | 266.4 [264.1, 267.8] | 247.3 to 279.8 |
| RSF | Clinical | Primary two-sided | 495 | 92.1 to 95.4 | unavailable | 270.8 [269.7, 272.1] | 262.2 to 279.0 |
| RSF | Clinical | One-sided lower | 495 | 88.1 to 93.9 | unavailable | 265.5 [263.2, 267.3] | 248.5 to 280.6 |
| RSF | + PAM50 | Primary two-sided | 495 | 91.5 to 95.6 | unavailable | 271.4 [270.3, 272.5] | 262.0 to 279.0 |
| RSF | + PAM50 | One-sided lower | 495 | 87.5 to 95.2 | unavailable | 267.6 [264.9, 271.8] | 242.4 to 280.9 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | -3.2 [-5.1, -1.4] | -0.4 [-1.4, 0.8] | unavailable | -4.3 [-5.1, -3.1] |
| Cox ridge | Clinical / Ridge Qin Cox | -0.6 [-1.4, 0.0] | -0.2 [-0.6, 0.0] | unavailable | -0.7 [-1.1, -0.4] |
| Cox | + PAM50 / One-sided lower | -3.6 [-5.5, -1.8] | -0.4 [-1.4, 0.6] | unavailable | -5.0 [-6.0, -3.6] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.4 [0.0, 1.0] | +0.2 [0.0, 0.6] | unavailable | +0.6 [0.3, 1.1] |
| Weibull | Clinical / One-sided lower | -3.8 [-5.9, -2.0] | -1.6 [-3.0, -0.2] | unavailable | -7.8 [-8.2, -6.2] |
| Weibull | + PAM50 / One-sided lower | -5.1 [-7.1, -3.0] | -1.6 [-3.0, -0.4] | unavailable | -7.9 [-9.5, -7.3] |
| RSF | Clinical / One-sided lower | -4.0 [-6.1, -2.0] | -1.4 [-3.0, 0.0] | unavailable | -5.2 [-6.9, -3.9] |
| RSF | + PAM50 / One-sided lower | -4.0 [-5.9, -2.2] | -0.4 [-1.4, 0.6] | unavailable | -3.8 [-5.8, 0.3] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -0.8 [-2.2, 0.6] | -0.2 [-1.2, 0.6] | unavailable | -1.9 [-2.9, -0.5] |
| Cox ridge | Ridge Qin Cox | -0.2 [-1.2, 0.8] | -0.2 [-0.8, 0.4] | unavailable | -0.5 [-1.1, 0.0] |
| Weibull | One-sided lower | -0.2 [-1.8, 1.2] | +0.6 [-0.4, 1.8] | unavailable | -0.1 [-2.0, 0.7] |
| RSF | One-sided lower | -0.6 [-2.2, 1.0] | +1.2 [0.4, 2.2] | unavailable | +2.1 [0.9, 4.7] |

### Breast-cancer-specific survival · 300 months · 80% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 83.4 to 90.5 | unavailable | 257.5 [256.2, 259.1] | 246.0 to 266.1 |
| Cox | Clinical | One-sided lower | 495 | 77.8 to 91.1 | unavailable | 251.8 [250.3, 255.8] | 215.9 to 280.3 |
| Cox | Clinical | Original Qin Cox | 1000 | 83.4 to 91.3 | unavailable | 261.2 [257.6, 262.1] | 251.4 to 268.1 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 83.6 to 91.5 | unavailable | 261.2 [257.6, 262.1] | 251.4 to 268.1 |
| Cox | + PAM50 | Primary two-sided | 495 | 81.6 to 90.5 | unavailable | 256.2 [255.0, 257.4] | 242.1 to 266.8 |
| Cox | + PAM50 | One-sided lower | 495 | 73.1 to 89.5 | unavailable | 246.3 [242.2, 248.1] | 207.5 to 276.0 |
| Cox | + PAM50 | Original Qin Cox | 900 | 80.2 to 90.3 | unavailable | 256.8 [255.1, 257.6] | 246.4 to 266.1 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 82.6 to 91.5 | unavailable | 257.6 [256.8, 259.4] | 248.8 to 267.7 |
| Weibull | Clinical | Primary two-sided | 495 | 82.0 to 90.1 | unavailable | 253.7 [250.0, 254.6] | 236.0 to 266.0 |
| Weibull | Clinical | One-sided lower | 495 | 78.6 to 89.9 | unavailable | 246.5 [243.0, 250.1] | 214.2 to 272.5 |
| Weibull | + PAM50 | Primary two-sided | 495 | 81.6 to 89.7 | unavailable | 251.3 [248.1, 253.5] | 231.8 to 264.9 |
| Weibull | + PAM50 | One-sided lower | 495 | 76.6 to 89.9 | unavailable | 244.3 [240.1, 247.3] | 206.4 to 271.1 |
| RSF | Clinical | Primary two-sided | 495 | 83.6 to 91.1 | unavailable | 257.7 [255.4, 259.5] | 240.7 to 272.8 |
| RSF | Clinical | One-sided lower | 495 | 76.6 to 90.5 | unavailable | 242.0 [241.0, 246.8] | 208.1 to 278.0 |
| RSF | + PAM50 | Primary two-sided | 495 | 82.4 to 90.9 | unavailable | 257.0 [254.3, 261.2] | 231.8 to 270.3 |
| RSF | + PAM50 | One-sided lower | 495 | 77.4 to 90.7 | unavailable | 242.5 [239.3, 253.7] | 203.4 to 276.4 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | -5.7 [-8.9, -2.6] | +0.6 [-1.6, 2.8] | unavailable | -5.6 [-6.6, -2.8] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.2 [0.0, 0.6] | +0.2 [0.0, 0.6] | unavailable | +0.0 [-1.0, 0.2] |
| Cox | + PAM50 / One-sided lower | -8.5 [-11.7, -4.8] | -1.0 [-3.2, 1.2] | unavailable | -9.9 [-13.2, -8.5] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +2.4 [1.2, 3.8] | +1.2 [0.4, 2.2] | unavailable | +0.8 [0.2, 2.0] |
| Weibull | Clinical / One-sided lower | -3.4 [-6.1, -0.8] | -0.2 [-2.0, 1.6] | unavailable | -7.2 [-8.2, -4.3] |
| Weibull | + PAM50 / One-sided lower | -5.1 [-7.9, -2.0] | +0.2 [-1.6, 2.0] | unavailable | -7.0 [-9.9, -5.3] |
| RSF | Clinical / One-sided lower | -7.1 [-9.7, -4.6] | -0.6 [-2.2, 1.0] | unavailable | -15.8 [-16.7, -12.5] |
| RSF | + PAM50 / One-sided lower | -5.1 [-7.5, -2.6] | -0.2 [-1.8, 1.4] | unavailable | -14.5 [-16.7, -5.2] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -4.6 [-6.9, -2.6] | -1.6 [-2.8, -0.6] | unavailable | -5.6 [-9.0, -4.4] |
| Cox ridge | Ridge Qin Cox | -1.0 [-2.8, 0.6] | +0.0 [-1.2, 1.2] | unavailable | -3.6 [-4.4, -0.2] |
| Weibull | One-sided lower | -2.0 [-4.2, 0.2] | +0.0 [-1.2, 1.2] | unavailable | -2.2 [-5.8, -0.2] |
| RSF | One-sided lower | +0.8 [-1.0, 2.6] | +0.2 [-0.8, 1.2] | unavailable | +0.5 [-2.5, 9.8] |

### Overall survival · 120 months · 95% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 96.8 to 97.8 | 97.6 [96.0, 98.9] | 105.2 [104.8, 106.3] | 99.8 to 107.3 |
| Cox | Clinical | One-sided lower | 495 | 97.0 to 98.0 | 97.8 [96.4, 99.1] | 105.2 [103.3, 105.9] | 97.4 to 110.3 |
| Cox | Clinical | Original Qin Cox | 998 | 97.2 to 98.0 | 97.8 [96.3, 99.1] | 105.6 [105.3, 105.9] | 103.3 to 109.2 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 97.2 to 98.0 | 97.8 [96.3, 99.1] | 105.6 [105.3, 105.9] | 103.3 to 109.2 |
| Cox | + PAM50 | Primary two-sided | 495 | 96.8 to 97.8 | 97.6 [96.2, 98.9] | 104.9 [104.8, 105.9] | 99.6 to 107.3 |
| Cox | + PAM50 | One-sided lower | 495 | 96.8 to 97.8 | 97.6 [96.1, 98.9] | 103.9 [103.2, 105.4] | 97.5 to 110.5 |
| Cox | + PAM50 | Original Qin Cox | 931 | 96.0 to 97.0 | 96.7 [95.0, 98.2] | 103.2 [101.0, 103.4] | 95.9 to 105.6 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 96.0 to 97.0 | 96.7 [95.0, 98.2] | 103.2 [101.0, 103.4] | 96.1 to 105.6 |
| Weibull | Clinical | Primary two-sided | 495 | 97.2 to 98.0 | 97.8 [96.3, 99.1] | 105.7 [104.9, 106.9] | 100.3 to 109.5 |
| Weibull | Clinical | One-sided lower | 495 | 97.4 to 98.4 | 98.3 [97.0, 99.4] | 106.8 [105.0, 108.2] | 97.4 to 112.6 |
| Weibull | + PAM50 | Primary two-sided | 495 | 96.8 to 97.8 | 97.6 [96.2, 98.9] | 105.3 [104.6, 105.9] | 99.5 to 109.5 |
| Weibull | + PAM50 | One-sided lower | 495 | 96.8 to 97.8 | 97.6 [96.1, 98.9] | 105.6 [104.5, 106.6] | 96.5 to 112.5 |
| RSF | Clinical | Primary two-sided | 495 | 97.4 to 98.4 | 98.3 [97.0, 99.4] | 103.4 [103.2, 104.8] | 95.7 to 107.1 |
| RSF | Clinical | One-sided lower | 495 | 96.6 to 97.6 | 97.4 [95.8, 98.7] | 101.1 [99.1, 101.5] | 93.2 to 108.6 |
| RSF | + PAM50 | Primary two-sided | 495 | 96.8 to 97.8 | 97.6 [96.1, 98.9] | 103.4 [103.2, 104.5] | 95.7 to 107.1 |
| RSF | + PAM50 | One-sided lower | 495 | 96.4 to 97.4 | 97.2 [95.5, 98.5] | 99.8 [97.4, 100.2] | 91.8 to 107.4 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +0.2 [-0.4, 1.0] | +0.2 [-0.4, 1.0] | +0.3 [-0.4, 1.2] | -0.0 [-1.5, 0.1] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.1] |
| Cox | + PAM50 / One-sided lower | +0.0 [-1.0, 1.0] | +0.0 [-1.0, 1.0] | +0.0 [-1.1, 1.2] | -1.1 [-1.6, 0.1] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 1.9] |
| Weibull | Clinical / One-sided lower | +0.2 [-0.8, 1.2] | +0.4 [-0.4, 1.4] | +0.5 [-0.5, 1.6] | +1.1 [0.1, 1.5] |
| Weibull | + PAM50 / One-sided lower | +0.0 [-1.0, 1.0] | +0.0 [-1.0, 1.0] | +0.0 [-1.1, 1.2] | +0.3 [-0.2, 0.8] |
| RSF | Clinical / One-sided lower | -0.8 [-1.6, -0.2] | -0.8 [-1.6, -0.2] | -0.9 [-1.8, -0.2] | -2.4 [-4.3, -2.3] |
| RSF | + PAM50 / One-sided lower | -0.4 [-1.0, 0.0] | -0.4 [-1.0, 0.0] | -0.4 [-1.1, 0.0] | -3.7 [-5.5, -3.5] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -0.2 [-1.0, 0.4] | -0.2 [-1.0, 0.4] | -0.2 [-1.1, 0.4] | -1.3 [-1.8, 0.2] |
| Cox ridge | Ridge Qin Cox | -1.2 [-2.2, -0.4] | -1.0 [-2.0, -0.2] | -1.1 [-2.1, -0.2] | -2.4 [-4.6, -2.3] |
| Weibull | One-sided lower | -0.6 [-1.4, 0.0] | -0.6 [-1.4, 0.0] | -0.6 [-1.5, 0.0] | -1.2 [-2.2, -0.2] |
| RSF | One-sided lower | -0.2 [-1.0, 0.6] | -0.2 [-1.0, 0.6] | -0.2 [-1.1, 0.7] | -1.3 [-1.8, -0.2] |

### Overall survival · 120 months · 90% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 92.9 to 94.3 | 93.9 [91.6, 96.0] | 97.4 [95.9, 98.4] | 90.0 to 102.9 |
| Cox | Clinical | One-sided lower | 495 | 94.1 to 95.8 | 95.4 [93.5, 97.3] | 102.3 [99.4, 103.7] | 88.4 to 110.8 |
| Cox | Clinical | Original Qin Cox | 998 | 96.0 to 97.0 | 96.7 [95.1, 98.3] | 101.0 [100.3, 103.3] | 95.2 to 105.2 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 96.0 to 97.0 | 96.7 [95.1, 98.3] | 100.8 [100.3, 103.3] | 95.2 to 104.9 |
| Cox | + PAM50 | Primary two-sided | 495 | 95.4 to 96.6 | 96.3 [94.6, 97.8] | 99.8 [99.3, 101.8] | 93.2 to 106.8 |
| Cox | + PAM50 | One-sided lower | 495 | 93.3 to 95.4 | 95.0 [93.1, 96.9] | 98.6 [96.1, 101.5] | 86.5 to 109.4 |
| Cox | + PAM50 | Original Qin Cox | 931 | 91.3 to 92.7 | 92.2 [89.7, 94.4] | 93.7 [93.0, 95.2] | 87.3 to 100.3 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 91.3 to 92.7 | 92.2 [89.7, 94.4] | 93.2 [92.6, 95.1] | 85.7 to 100.1 |
| Weibull | Clinical | Primary two-sided | 495 | 94.7 to 96.2 | 95.8 [94.1, 97.5] | 99.5 [98.1, 101.4] | 90.6 to 105.8 |
| Weibull | Clinical | One-sided lower | 495 | 94.1 to 95.6 | 95.2 [93.2, 97.2] | 102.2 [99.3, 104.6] | 86.5 to 112.0 |
| Weibull | + PAM50 | Primary two-sided | 495 | 94.7 to 96.0 | 95.6 [93.8, 97.3] | 99.6 [98.4, 100.6] | 89.9 to 106.4 |
| Weibull | + PAM50 | One-sided lower | 495 | 93.3 to 94.9 | 94.6 [92.5, 96.6] | 97.6 [95.7, 99.4] | 82.4 to 109.1 |
| RSF | Clinical | Primary two-sided | 495 | 94.3 to 95.6 | 95.3 [93.2, 97.0] | 95.6 [93.7, 96.1] | 87.7 to 103.2 |
| RSF | Clinical | One-sided lower | 495 | 91.1 to 93.3 | 92.9 [90.4, 95.1] | 90.3 [88.7, 92.3] | 78.1 to 99.1 |
| RSF | + PAM50 | Primary two-sided | 495 | 93.7 to 95.2 | 94.8 [92.8, 96.7] | 95.7 [93.3, 96.1] | 87.7 to 103.3 |
| RSF | + PAM50 | One-sided lower | 495 | 90.1 to 93.3 | 92.9 [90.4, 95.1] | 90.0 [88.6, 92.0] | 76.2 to 98.6 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +1.2 [-0.4, 2.8] | +1.4 [-0.2, 3.0] | +1.5 [-0.2, 3.3] | +4.8 [3.5, 5.8] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | -0.2 [-1.6, 0.0] |
| Cox | + PAM50 / One-sided lower | -2.0 [-3.4, -0.6] | -1.2 [-2.4, -0.2] | -1.3 [-2.6, -0.1] | -1.2 [-3.3, 0.2] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | -0.4 [-1.5, -0.0] |
| Weibull | Clinical / One-sided lower | -0.6 [-1.8, 0.6] | -0.6 [-1.8, 0.6] | -0.6 [-1.9, 0.7] | +2.7 [1.1, 3.4] |
| Weibull | + PAM50 / One-sided lower | -1.4 [-2.6, -0.4] | -1.0 [-2.2, 0.0] | -1.1 [-2.3, 0.1] | -1.9 [-2.7, -1.1] |
| RSF | Clinical / One-sided lower | -3.2 [-4.6, -1.8] | -2.2 [-3.6, -1.0] | -2.4 [-3.9, -1.1] | -5.3 [-5.5, -3.7] |
| RSF | + PAM50 / One-sided lower | -3.6 [-5.7, -2.0] | -1.8 [-3.0, -0.8] | -2.0 [-3.4, -0.9] | -5.6 [-6.9, -4.4] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -0.8 [-1.6, -0.2] | -0.4 [-1.0, 0.0] | -0.4 [-1.1, 0.0] | -3.7 [-5.1, -1.6] |
| Cox ridge | Ridge Qin Cox | -4.6 [-6.5, -2.8] | -4.2 [-6.1, -2.6] | -4.6 [-6.5, -2.8] | -7.6 [-9.9, -7.2] |
| Weibull | One-sided lower | -0.8 [-1.6, -0.2] | -0.6 [-1.4, 0.0] | -0.6 [-1.5, 0.0] | -4.6 [-6.2, -3.0] |
| RSF | One-sided lower | -1.0 [-2.0, 0.0] | +0.0 [-0.6, 0.6] | -0.0 [-0.7, 0.7] | -0.3 [-1.6, 0.6] |

### Overall survival · 120 months · 80% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 85.3 to 88.5 | 87.6 [84.6, 90.3] | 88.1 [84.8, 89.6] | 74.3 to 96.7 |
| Cox | Clinical | One-sided lower | 495 | 83.8 to 89.1 | 88.2 [85.3, 91.0] | 85.5 [78.8, 89.9] | 51.1 to 102.8 |
| Cox | Clinical | Original Qin Cox | 998 | 86.7 to 88.9 | 88.0 [84.9, 90.7] | 87.3 [84.8, 89.1] | 74.5 to 93.3 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 86.7 to 88.9 | 88.0 [84.9, 90.7] | 87.3 [85.0, 89.1] | 74.5 to 93.3 |
| Cox | + PAM50 | Primary two-sided | 495 | 84.0 to 88.1 | 87.1 [84.1, 89.9] | 84.7 [82.8, 87.4] | 73.2 to 95.9 |
| Cox | + PAM50 | One-sided lower | 495 | 82.8 to 88.3 | 87.3 [84.3, 90.3] | 82.1 [78.6, 87.0] | 50.9 to 103.8 |
| Cox | + PAM50 | Original Qin Cox | 931 | 83.0 to 87.5 | 86.5 [83.5, 89.4] | 79.6 [77.6, 82.2] | 67.7 to 90.8 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 83.0 to 87.5 | 86.5 [83.5, 89.4] | 79.3 [77.4, 82.1] | 66.4 to 90.3 |
| Weibull | Clinical | Primary two-sided | 495 | 85.5 to 88.5 | 87.6 [84.8, 90.4] | 86.3 [84.0, 89.5] | 71.4 to 96.8 |
| Weibull | Clinical | One-sided lower | 495 | 83.4 to 88.3 | 87.4 [84.3, 90.3] | 84.0 [79.1, 88.2] | 57.3 to 100.6 |
| Weibull | + PAM50 | Primary two-sided | 495 | 84.0 to 87.9 | 86.9 [83.8, 89.8] | 84.1 [82.3, 85.9] | 68.0 to 95.6 |
| Weibull | + PAM50 | One-sided lower | 495 | 85.1 to 89.7 | 88.9 [86.0, 91.8] | 84.6 [81.4, 87.7] | 58.6 to 104.3 |
| RSF | Clinical | Primary two-sided | 495 | 88.3 to 91.3 | 90.7 [88.1, 93.1] | 83.7 [82.1, 85.7] | 71.5 to 92.5 |
| RSF | Clinical | One-sided lower | 495 | 84.4 to 89.1 | 88.2 [85.2, 90.8] | 76.2 [72.1, 80.7] | 50.1 to 90.4 |
| RSF | + PAM50 | Primary two-sided | 495 | 86.7 to 90.7 | 90.0 [87.2, 92.5] | 83.6 [82.1, 85.6] | 69.8 to 92.1 |
| RSF | + PAM50 | One-sided lower | 495 | 82.8 to 88.3 | 87.3 [84.2, 89.9] | 73.5 [69.9, 76.5] | 48.4 to 89.1 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | -1.4 [-3.6, 0.8] | +0.6 [-1.2, 2.4] | +0.6 [-1.3, 2.6] | -2.5 [-6.0, 0.3] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.6] |
| Cox | + PAM50 / One-sided lower | -1.2 [-3.4, 0.8] | +0.2 [-1.4, 1.8] | +0.2 [-1.6, 2.0] | -2.6 [-4.8, -0.3] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | -0.3 [-1.8, 0.0] |
| Weibull | Clinical / One-sided lower | -2.0 [-4.0, 0.0] | -0.2 [-1.8, 1.4] | -0.2 [-1.9, 1.5] | -2.2 [-5.0, -1.0] |
| Weibull | + PAM50 / One-sided lower | +1.0 [-0.8, 3.0] | +1.8 [0.2, 3.6] | +2.0 [0.2, 4.0] | +0.5 [-0.9, 2.2] |
| RSF | Clinical / One-sided lower | -3.8 [-5.9, -1.8] | -2.2 [-4.0, -0.6] | -2.5 [-4.4, -0.7] | -7.5 [-10.4, -4.2] |
| RSF | + PAM50 / One-sided lower | -3.8 [-5.5, -2.2] | -2.4 [-3.8, -1.2] | -2.7 [-4.2, -1.3] | -10.1 [-12.6, -7.3] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -1.0 [-2.4, 0.2] | -0.8 [-1.8, 0.2] | -0.9 [-2.0, 0.3] | -3.5 [-5.9, 0.5] |
| Cox ridge | Ridge Qin Cox | -3.6 [-5.1, -2.2] | -1.4 [-2.4, -0.4] | -1.5 [-2.7, -0.5] | -8.0 [-9.7, -6.1] |
| Weibull | One-sided lower | +1.6 [0.6, 2.8] | +1.4 [0.4, 2.6] | +1.5 [0.5, 2.8] | +0.6 [-2.2, 3.2] |
| RSF | One-sided lower | -1.6 [-3.2, 0.0] | -0.8 [-2.4, 0.8] | -0.9 [-2.6, 0.9] | -2.7 [-5.6, -1.2] |

### Overall survival · 300 months · 95% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 96.0 to 99.0 | 98.7 [97.5, 99.8] | 288.8 [288.2, 291.1] | 282.7 to 292.9 |
| Cox | Clinical | One-sided lower | 495 | 97.0 to 98.0 | 97.7 [96.0, 99.1] | 285.2 [283.3, 285.9] | 277.4 to 290.3 |
| Cox | Clinical | Original Qin Cox | 998 | 92.3 to 98.0 | 97.6 [95.9, 99.0] | 284.8 [283.7, 284.9] | 279.6 to 285.9 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 92.3 to 98.0 | 97.6 [95.9, 99.0] | 284.8 [283.4, 284.8] | 279.2 to 285.9 |
| Cox | + PAM50 | Primary two-sided | 495 | 95.6 to 99.2 | 99.0 [97.9, 99.8] | 291.8 [290.9, 293.7] | 284.0 to 295.7 |
| Cox | + PAM50 | One-sided lower | 495 | 96.8 to 97.8 | 97.5 [95.9, 99.0] | 283.9 [283.2, 285.4] | 277.5 to 290.5 |
| Cox | + PAM50 | Original Qin Cox | 931 | 92.7 to 97.0 | 96.5 [94.4, 98.2] | 280.3 [279.6, 280.8] | 272.1 to 284.4 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 92.3 to 97.0 | 96.5 [94.4, 98.2] | 280.3 [279.8, 280.8] | 272.5 to 284.4 |
| Weibull | Clinical | Primary two-sided | 495 | 95.6 to 98.0 | 97.6 [95.9, 99.0] | 284.0 [283.0, 284.7] | 276.6 to 288.0 |
| Weibull | Clinical | One-sided lower | 495 | 97.4 to 98.4 | 98.2 [96.8, 99.3] | 286.8 [285.0, 288.2] | 277.4 to 292.6 |
| Weibull | + PAM50 | Primary two-sided | 495 | 94.7 to 97.8 | 97.4 [95.6, 98.9] | 283.6 [282.9, 284.5] | 276.0 to 287.9 |
| Weibull | + PAM50 | One-sided lower | 495 | 96.8 to 97.8 | 97.5 [95.9, 99.0] | 285.6 [284.5, 286.6] | 276.5 to 292.5 |
| RSF | Clinical | Primary two-sided | 495 | 97.4 to 98.4 | 98.2 [96.7, 99.3] | 283.4 [283.2, 284.8] | 275.7 to 287.1 |
| RSF | Clinical | One-sided lower | 495 | 96.6 to 97.6 | 97.3 [95.4, 98.7] | 281.1 [279.1, 281.5] | 273.2 to 288.6 |
| RSF | + PAM50 | Primary two-sided | 495 | 96.8 to 97.8 | 97.5 [95.7, 98.9] | 283.4 [283.2, 284.5] | 275.7 to 287.1 |
| RSF | + PAM50 | One-sided lower | 495 | 96.4 to 97.4 | 97.1 [95.1, 98.5] | 279.8 [277.4, 280.2] | 271.8 to 287.4 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +1.0 [-0.8, 2.8] | -1.0 [-2.0, 0.0] | -1.0 [-2.4, 0.2] | -3.6 [-5.7, -2.6] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [-0.7, 0.0] |
| Cox | + PAM50 / One-sided lower | +1.2 [-0.6, 3.2] | -1.4 [-2.6, -0.4] | -1.5 [-3.0, -0.1] | -7.9 [-9.7, -6.3] |
| Cox ridge | + PAM50 / Ridge Qin Cox | -0.4 [-1.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [-0.2, 0.3] |
| Weibull | Clinical / One-sided lower | +1.8 [0.4, 3.4] | +0.4 [-0.4, 1.4] | +0.6 [-0.5, 1.9] | +2.8 [1.3, 4.1] |
| Weibull | + PAM50 / One-sided lower | +2.0 [0.4, 3.6] | +0.0 [-1.0, 1.0] | +0.1 [-1.1, 1.4] | +2.0 [0.9, 2.8] |
| RSF | Clinical / One-sided lower | -0.8 [-1.6, -0.2] | -0.8 [-1.6, -0.2] | -0.9 [-1.9, -0.2] | -2.4 [-4.3, -2.3] |
| RSF | + PAM50 / One-sided lower | -0.4 [-1.0, 0.0] | -0.4 [-1.0, 0.0] | -0.5 [-1.2, 0.0] | -3.7 [-5.5, -3.5] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -0.2 [-1.0, 0.4] | -0.2 [-1.0, 0.4] | -0.2 [-1.1, 0.5] | -1.3 [-1.8, 0.2] |
| Cox ridge | Ridge Qin Cox | +0.0 [-1.4, 1.6] | -1.0 [-2.0, -0.2] | -1.1 [-2.3, -0.2] | -4.5 [-4.7, -3.4] |
| Weibull | One-sided lower | -0.6 [-1.4, 0.0] | -0.6 [-1.4, 0.0] | -0.7 [-1.6, 0.0] | -1.2 [-2.2, -0.2] |
| RSF | One-sided lower | -0.2 [-1.0, 0.6] | -0.2 [-1.0, 0.6] | -0.2 [-1.2, 0.8] | -1.3 [-1.8, -0.2] |

### Overall survival · 300 months · 90% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 88.9 to 95.8 | 94.5 [91.7, 96.8] | 274.8 [273.9, 275.6] | 262.0 to 280.6 |
| Cox | Clinical | One-sided lower | 495 | 94.1 to 95.8 | 95.2 [92.8, 97.2] | 282.3 [279.4, 283.7] | 268.4 to 290.8 |
| Cox | Clinical | Original Qin Cox | 998 | 89.5 to 97.0 | 96.5 [94.5, 98.2] | 277.8 [276.8, 278.3] | 269.8 to 283.0 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 89.3 to 97.0 | 96.5 [94.5, 98.2] | 277.8 [276.6, 278.3] | 269.7 to 283.0 |
| Cox | + PAM50 | Primary two-sided | 495 | 89.9 to 96.4 | 95.4 [92.7, 97.6] | 277.2 [275.5, 278.2] | 263.7 to 282.4 |
| Cox | + PAM50 | One-sided lower | 495 | 93.3 to 95.4 | 94.8 [92.3, 96.8] | 278.6 [276.1, 281.5] | 266.5 to 289.4 |
| Cox | + PAM50 | Original Qin Cox | 931 | 85.3 to 92.3 | 90.9 [87.4, 93.7] | 270.3 [268.2, 271.4] | 257.7 to 275.5 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 85.3 to 92.5 | 90.9 [87.4, 93.7] | 269.7 [268.0, 271.0] | 257.6 to 275.2 |
| Weibull | Clinical | Primary two-sided | 495 | 91.1 to 96.2 | 95.6 [93.3, 97.4] | 274.9 [273.3, 276.5] | 262.4 to 282.5 |
| Weibull | Clinical | One-sided lower | 495 | 94.1 to 95.6 | 95.0 [92.5, 97.0] | 282.2 [279.3, 284.6] | 266.5 to 292.0 |
| Weibull | + PAM50 | Primary two-sided | 495 | 91.3 to 95.8 | 94.5 [91.7, 96.8] | 275.6 [273.6, 276.8] | 262.0 to 281.8 |
| Weibull | + PAM50 | One-sided lower | 495 | 93.3 to 94.9 | 94.3 [91.7, 96.6] | 277.6 [275.7, 279.4] | 262.4 to 289.1 |
| RSF | Clinical | Primary two-sided | 495 | 93.3 to 95.6 | 95.0 [92.8, 97.0] | 275.1 [273.2, 275.9] | 267.4 to 280.8 |
| RSF | Clinical | One-sided lower | 495 | 91.1 to 93.3 | 92.5 [89.5, 94.9] | 270.3 [268.7, 272.3] | 258.1 to 279.1 |
| RSF | + PAM50 | Primary two-sided | 495 | 92.9 to 95.2 | 94.6 [92.2, 96.6] | 275.1 [273.2, 276.1] | 267.4 to 283.2 |
| RSF | + PAM50 | One-sided lower | 495 | 90.1 to 93.3 | 92.5 [89.5, 95.0] | 270.0 [268.6, 272.0] | 256.2 to 278.6 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +5.3 [2.8, 7.7] | +0.0 [-1.4, 1.4] | +0.7 [-1.4, 3.1] | +7.5 [4.2, 9.7] |
| Cox ridge | Clinical / Ridge Qin Cox | -0.2 [-0.6, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [-0.2, 0.0] |
| Cox | + PAM50 / One-sided lower | +3.4 [0.8, 6.1] | -1.0 [-2.4, 0.2] | -0.7 [-2.7, 1.7] | +1.4 [-0.8, 4.3] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.2 [0.0, 0.6] | +0.0 [0.0, 0.0] | -0.6 [-0.9, 0.0] |
| Weibull | Clinical / One-sided lower | +3.0 [0.8, 5.3] | -0.6 [-1.8, 0.6] | -0.6 [-2.1, 1.0] | +7.3 [4.5, 9.9] |
| Weibull | + PAM50 / One-sided lower | +2.0 [0.0, 4.0] | -0.8 [-2.0, 0.4] | -0.2 [-2.0, 2.1] | +2.1 [0.2, 4.5] |
| RSF | Clinical / One-sided lower | -2.2 [-4.0, -0.4] | -2.2 [-3.6, -1.0] | -2.5 [-4.2, -1.1] | -4.8 [-5.3, -3.3] |
| RSF | + PAM50 / One-sided lower | -2.8 [-4.8, -1.0] | -1.8 [-3.0, -0.8] | -2.1 [-3.6, -0.9] | -5.1 [-6.4, -3.9] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -0.8 [-1.6, -0.2] | -0.4 [-1.0, 0.0] | -0.5 [-1.2, 0.0] | -3.7 [-5.1, -1.6] |
| Cox ridge | Ridge Qin Cox | -4.0 [-6.5, -1.8] | -4.4 [-6.3, -2.8] | -5.6 [-8.4, -3.2] | -8.1 [-9.4, -7.1] |
| Weibull | One-sided lower | -0.8 [-1.6, -0.2] | -0.6 [-1.4, 0.0] | -0.7 [-1.6, 0.0] | -4.6 [-6.2, -3.0] |
| RSF | One-sided lower | -1.0 [-2.0, 0.0] | +0.0 [-0.6, 0.6] | -0.0 [-0.7, 0.7] | -0.3 [-1.6, 0.6] |

### Overall survival · 300 months · 80% nominal

| Model | Features | Method | n_cal / B | Observable coverage bounds (%) | IPCW coverage (%) [CI] | Median width (months) [CI] | Width IQR (months) |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| Cox | Clinical | Primary two-sided | 495 | 73.1 to 87.5 | 79.1 [69.4, 86.4] | 251.9 [247.2, 256.2] | 224.8 to 263.0 |
| Cox | Clinical | One-sided lower | 495 | 84.4 to 90.3 | 89.0 [85.3, 92.5] | 269.6 [262.8, 273.9] | 235.2 to 286.9 |
| Cox | Clinical | Original Qin Cox | 998 | 78.4 to 88.7 | 86.6 [82.3, 90.2] | 257.7 [256.2, 260.2] | 241.4 to 266.8 |
| Cox ridge | Clinical | Ridge Qin Cox | 1000 | 78.4 to 88.7 | 86.6 [82.3, 90.2] | 257.7 [256.2, 261.2] | 241.9 to 267.1 |
| Cox | + PAM50 | Primary two-sided | 495 | 73.7 to 86.7 | 78.1 [68.4, 85.7] | 248.8 [244.0, 253.9] | 220.1 to 262.0 |
| Cox | + PAM50 | One-sided lower | 495 | 82.2 to 88.1 | 86.5 [82.4, 90.3] | 262.1 [258.6, 267.0] | 230.9 to 283.8 |
| Cox | + PAM50 | Original Qin Cox | 931 | 74.1 to 86.9 | 85.0 [80.3, 88.7] | 250.8 [248.3, 252.5] | 226.8 to 259.6 |
| Cox ridge | + PAM50 | Ridge Qin Cox | 1000 | 74.3 to 87.1 | 85.0 [80.3, 88.7] | 250.6 [248.2, 251.9] | 227.2 to 260.2 |
| Weibull | Clinical | Primary two-sided | 495 | 78.0 to 87.9 | 85.5 [80.8, 89.2] | 252.4 [249.7, 255.1] | 230.8 to 265.2 |
| Weibull | Clinical | One-sided lower | 495 | 85.5 to 90.3 | 89.1 [85.4, 92.4] | 267.2 [262.3, 271.4] | 240.5 to 283.8 |
| Weibull | + PAM50 | Primary two-sided | 495 | 76.4 to 87.1 | 82.7 [76.1, 87.7] | 249.7 [245.3, 252.7] | 226.2 to 262.8 |
| Weibull | + PAM50 | One-sided lower | 495 | 84.2 to 89.7 | 88.4 [84.5, 91.7] | 264.6 [261.4, 267.7] | 238.6 to 284.3 |
| RSF | Clinical | Primary two-sided | 495 | 84.2 to 91.3 | 90.3 [86.8, 93.0] | 256.2 [253.9, 257.6] | 239.7 to 270.3 |
| RSF | Clinical | One-sided lower | 495 | 84.4 to 89.1 | 87.7 [83.6, 90.9] | 256.2 [252.1, 260.7] | 230.1 to 270.4 |
| RSF | + PAM50 | Primary two-sided | 495 | 83.0 to 90.7 | 89.6 [85.9, 92.4] | 256.9 [253.3, 261.2] | 236.2 to 270.3 |
| RSF | + PAM50 | One-sided lower | 495 | 82.6 to 88.3 | 86.8 [82.4, 90.1] | 253.5 [249.9, 256.5] | 228.4 to 269.1 |

Paired method differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | Clinical / One-sided lower | +11.3 [7.7, 15.2] | +2.8 [0.8, 5.1] | +10.0 [2.7, 19.7] | +17.7 [8.6, 25.4] |
| Cox ridge | Clinical / Ridge Qin Cox | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [0.0, 0.0] | +0.0 [-0.5, 0.8] |
| Cox | + PAM50 / One-sided lower | +8.5 [5.3, 11.9] | +1.4 [-0.4, 3.4] | +8.3 [0.7, 18.0] | +13.3 [5.8, 21.5] |
| Cox ridge | + PAM50 / Ridge Qin Cox | +0.2 [0.0, 0.6] | +0.2 [0.0, 0.6] | +0.0 [0.0, 0.0] | -0.2 [-0.7, 1.0] |
| Weibull | Clinical / One-sided lower | +7.5 [4.4, 10.5] | +2.4 [0.8, 4.2] | +3.6 [1.1, 6.6] | +14.8 [9.2, 20.3] |
| Weibull | + PAM50 / One-sided lower | +7.9 [4.8, 11.1] | +2.6 [1.0, 4.6] | +5.7 [1.5, 11.7] | +14.9 [10.4, 20.0] |
| RSF | Clinical / One-sided lower | +0.2 [-2.4, 3.0] | -2.2 [-4.0, -0.6] | -2.6 [-4.8, -0.7] | +0.0 [-3.1, 3.9] |
| RSF | + PAM50 / One-sided lower | -0.4 [-2.8, 2.2] | -2.4 [-3.8, -1.2] | -2.8 [-4.7, -1.3] | -3.4 [-7.4, 0.6] |

Paired feature differences:

| Model | Features / candidate | Δ observable lower (pp) [CI] | Δ observable upper (pp) [CI] | Δ IPCW coverage (pp) [CI] | Δ median width (months) [CI] |
| --- | --- | ---: | ---: | ---: | ---: |
| Cox | One-sided lower | -2.2 [-3.8, -0.8] | -2.2 [-3.4, -1.0] | -2.6 [-4.3, -1.2] | -7.5 [-10.0, -3.5] |
| Cox ridge | Ridge Qin Cox | -4.0 [-6.1, -2.0] | -1.6 [-2.8, -0.6] | -1.6 [-3.0, -0.5] | -7.1 [-9.3, -6.1] |
| Weibull | One-sided lower | -1.2 [-2.6, 0.0] | -0.6 [-1.6, 0.4] | -0.7 [-1.9, 0.5] | -2.6 [-5.4, 0.0] |
| RSF | One-sided lower | -1.8 [-3.4, -0.2] | -0.8 [-2.4, 0.8] | -0.9 [-2.8, 0.9] | -2.7 [-5.6, -1.2] |

## Figures and provenance

- [reliability_coverage_width__disease_specific__horizon120__nominal0.90.pdf](figures/reliability_coverage_width__disease_specific__horizon120__nominal0.90.pdf) ([PNG preview](figures/reliability_coverage_width__disease_specific__horizon120__nominal0.90.png))
- [reliability_coverage_width__disease_specific__horizon300__nominal0.90.pdf](figures/reliability_coverage_width__disease_specific__horizon300__nominal0.90.pdf) ([PNG preview](figures/reliability_coverage_width__disease_specific__horizon300__nominal0.90.png))
- [reliability_coverage_width__overall__horizon120__nominal0.90.pdf](figures/reliability_coverage_width__overall__horizon120__nominal0.90.pdf) ([PNG preview](figures/reliability_coverage_width__overall__horizon120__nominal0.90.png))
- [reliability_coverage_width__overall__horizon300__nominal0.90.pdf](figures/reliability_coverage_width__overall__horizon300__nominal0.90.pdf) ([PNG preview](figures/reliability_coverage_width__overall__horizon300__nominal0.90.png))

Suggested caption: Exploratory comparison on the reused test cohort. The top panel shows observable coverage bounds (thick ranges), IPCW estimates (filled symbols) with bootstrap confidence intervals (thin whiskers), and nominal coverage (grey line). Hollow symbols mark observable bounds where IPCW is unavailable. The lower panel shows median restricted interval width, IQR (thick range), and bootstrap median confidence interval (thin whiskers). One-sided lower bounds retain the horizon as a fixed upper boundary and answer a different question from the two-sided methods. Clinical and +PAM50 use identical patients.

