# RailTrack Inspector: An Explainable Deep Learning Driven Web Application to Detect Rail Track Defects with Location 

## Abstract

Railways constitute a critical component of global transportation, yet existing defect detection methods rely predominantly on manual inspection, which is inefficient, error-prone, and increasingly inadequate for ensuring safety under growing rail traffic. Structural anomalies such as missing or fasteners, missing bolts, and rail cracks frequently remain undetected through traditional practices, posing risks of severe accidents and economic loss. To address this challenge, we proposed a deep learning-based web application to detect rail track defects with Location. We deployed the proposed Faster R-CNN model, achieving 97% accuracy. Gradient-weighted Class Activation Mapping (Grad-CAM) was applied to the test data to interpret model predictions and verify that meaningful defect features were learned. The model was integrated into a lightweight web application within the railway inspection system. Railway track data are captured using GPS-enabled cameras mounted on the trolley, enabling real-time inference, geolocation-based defect mapping. This integration not only enables automated detection and precise localization of defects but also provides transparent decision support to railway maintenance teams. While validated on Bangladesh’s railway infrastructure, the framework is scalable and adaptable to global railway networks too.

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

https://drive.google.com/drive/folders/1107xzZFMBYmAMAam4TqvKzr7ynqcpdW4?usp=drive_link

---

## Contact-
**Email:** mh191867@gmail.com

---

**N.T.** The dataset will be provided upon request.
