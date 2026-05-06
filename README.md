# RailTrack Inspector: An Explainable Deep Learning Driven Web Application to Detect Rail Track Defects with Location 

## Abstract

Railways constitute a critical component of global transportation systems; however, existing defect detection methods rely predominantly on manual inspection. Such approaches are inefficient, error-prone, and increasingly inadequate for ensuring safety under growing rail traffic demands. Structural anomalies—including missing fasteners, missing bolts, and rail cracks—often remain undetected through traditional practices, thereby posing significant risks of severe accidents and economic loss.

To address these challenges, this study proposes an explainable deep learning–based web application for automated rail track defect detection with geolocation support. The proposed system employs the Faster R-CNN model, achieving an accuracy of 97%. To enhance interpretability, Gradient-weighted Class Activation Mapping (Grad-CAM) is applied to visualize and validate that the model focuses on meaningful defect regions.

The trained model is integrated into a lightweight web application designed for real-time railway inspection. Data are captured using GPS-enabled cameras mounted on inspection trolleys, enabling real-time inference and location-aware defect mapping. This integration facilitates automated detection, precise localization, and transparent decision support for railway maintenance teams. Although the system is validated on Bangladesh’s railway infrastructure, the proposed framework is scalable and adaptable to global railway networks.

---

## Objectives

* To construct a comprehensive dataset of railway track defects specific to Bangladesh.
* To develop a deep learning–based model capable of detecting multiple rail track defects with geolocation and explainability.
* To design and implement a user-friendly web application for automated defect detection and visualization.

---

## Dataset Description

| Dataset Name                 | Description                                                   | Number of Samples | Image Resolution | Format       |
| ---------------------------- | ------------------------------------------------------------- | ----------------- | ---------------- | ------------ |
| Primary + Secondary          | Combined dataset from multiple sources                        | 3,500             | Random           | JPEG/PNG/JPG |
| Primary Dataset              | Images of defects and non-defects                             | 1,800             | Random           | JPEG/PNG/JPG |
| Secondary Dataset            | Images of defects and non-defects                             | 1,700             | Random           | JPEG/PNG/JPG |
| Defect Images (Combined)     | Only defect images                                            | 1,620             | Random           | JPEG/PNG/JPG |
| Non-Defect Images (Combined) | Only non-defect images                                        | 1,880             | Random           | JPEG/PNG/JPG |
| Augmented Dataset (Defects)  | Augmented images of missing bolts, fasteners, and rail cracks | 3,000             | 640×640          | PNG          |
| Final Dataset                | Combined augmented defect and non-defect images               | 4,880             | Random           | JPEG/PNG/JPG |
| Training Set                 | Dataset used for training                                     | 2,928             | Random           | JPEG/PNG/JPG |
| Validation Set               | Dataset used for validation                                   | 976               | Random           | JPEG/PNG/JPG |
| Test Set                     | Dataset used for testing                                      | 976               | Random           | JPEG/PNG/JPG |

---

## Performance Comparison of Detection Models

A comparative performance analysis was conducted to evaluate the effectiveness of different object detection models for rail track defect detection. The models were assessed using standard evaluation metrics, including Accuracy, Precision, Recall, and F1-score.

| Model        | Accuracy | Precision | Recall | F1-score |
| ------------ | -------- | --------- | ------ | -------- |
| Faster R-CNN | 0.9700   | 0.9814    | 0.9700 | 0.9756   |
| RetinaNet    | 0.8759   | 0.8809    | 0.8759 | 0.8773   |
| YOLO11       | 0.8390   | 0.9720    | 0.8780 | 0.9220   |
| SSD          | 0.7900   | 0.7930    | 0.7900 | 0.7840   |

---

## Dataset-

https://drive.google.com/file/d/1vA4P1DXYCCCl0qE-uZXWvrapMrHqmeEm/view?usp=drive_link
https://drive.google.com/file/d/10CpUquL_zzXQEoAJgRc0_exiWBxHPDXs/view?usp=drive_link

**N.T.** The dataset will be provided upon request.
