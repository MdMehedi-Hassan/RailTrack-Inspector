# RailTrack Inspector: An Explainable Deep Learning Driven Web Application for Rail Track Defect Detection with Geolocation

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

## Methodology Workflow

### Proposed System Workflow

<img width="350" height="500" alt="Flow-chart drawio" src="https://github.com/user-attachments/assets/96c5bd78-b657-4637-80ae-e89ef7046841" />

---

## Comparison of Inspection Approaches

### Traditional Railway Inspection Process

<img width="600" height="600" alt="4" src="https://github.com/user-attachments/assets/0ffe84a7-c3ee-4591-a20a-28e15bf57caf" />

### Proposed Automated Inspection System

<img width="1033" height="275" alt="5" src="https://github.com/user-attachments/assets/050545b1-a383-4c62-bb55-bff94aeb0ec1" />

---

## Performance Comparison of Detection Models

A comparative performance analysis was conducted to evaluate the effectiveness of different object detection models for rail track defect detection. The models were assessed using standard evaluation metrics, including Accuracy, Precision, Recall, and F1-score.

| Model        | Accuracy | Precision | Recall | F1-score |
| ------------ | -------- | --------- | ------ | -------- |
| Faster R-CNN | 0.9700   | 0.9814    | 0.9700 | 0.9756   |
| RetinaNet    | 0.8759   | 0.8809    | 0.8759 | 0.8773   |
| YOLO11       | 0.8390   | 0.9720    | 0.8780 | 0.9220   |
| SSD          | 0.7900   | 0.7930    | 0.7900 | 0.7840   |

### Analysis

The results indicate that **Faster R-CNN** outperforms all other models across all evaluation metrics, achieving the highest accuracy (97%) and F1-score (0.9756). This demonstrates its superior capability in both detecting defects and maintaining a balance between precision and recall.

Although **YOLO11** achieves a notably high precision (0.9720), its comparatively lower accuracy suggests a tendency to miss certain defect instances, indicating a trade-off between detection speed and reliability.

**RetinaNet** exhibits balanced performance across all metrics but does not surpass Faster R-CNN in any category. Meanwhile, **SSD** shows the lowest overall performance, particularly in terms of F1-score, indicating limitations in handling complex defect detection scenarios.

Overall, Faster R-CNN is selected as the optimal model for this study due to its consistently superior and reliable performance.

---

## Explainable Artificial Intelligence (XAI) with Grad-CAM

Gradient-weighted Class Activation Mapping (Grad-CAM) is a widely adopted Explainable Artificial Intelligence (XAI) technique used to interpret and visualise the predictions of convolutional neural networks (CNNs). It generates intuitive visual explanations by highlighting the regions of an input image that contribute most significantly to a model’s decision for a specific target class. Importantly, Grad-CAM operates without requiring any modification to the original model architecture, making it highly practical for real-world applications.

Deep learning models are often regarded as “black boxes” due to their limited interpretability. In safety-critical domains such as railway infrastructure monitoring, it is essential to ensure that model predictions are based on meaningful and relevant visual features rather than spurious background patterns. To address this challenge, XAI techniques were integrated into the proposed Faster R-CNN–based defect detection framework.

Grad-CAM is employed in this study to enhance the transparency, interpretability, and trustworthiness of the developed model. By producing visual explanations, it enables a clear understanding of why the model makes specific predictions. This not only validates that the network focuses on relevant defect regions but also facilitates model debugging by revealing incorrect attention patterns, which may indicate dataset bias or potential causes of misclassification. Furthermore, the visual evidence generated by Grad-CAM improves user confidence and supports reliable deployment in real-world railway inspection systems. Notably, Grad-CAM can be applied to pre-trained CNN models without requiring retraining or architectural modifications.

Grad-CAM explains the decision-making process of CNN-based models by leveraging class-specific gradient information. The process begins with an input image passed through a convolutional backbone (e.g., ResNet50), where hierarchical feature maps are extracted while preserving spatial information.

Following feature extraction, the network produces prediction scores for different classes. Grad-CAM then focuses on a selected target class and computes the gradients of the corresponding class score with respect to the feature maps of the final convolutional layer. These gradients indicate the importance of different spatial regions for the target class.

Next, the gradient information is spatially averaged to obtain importance weights for each feature map. These weights are used to compute a weighted combination of the feature maps, resulting in a class-discriminative localization map. A ReLU activation function is subsequently applied to eliminate negative contributions, ensuring that only features positively influencing the prediction are retained.

Finally, the resulting activation map is upsampled to match the original image resolution and overlaid on the input image as a heatmap. In this visualisation, high-importance regions are typically represented in red, while low-importance regions appear in blue, providing an intuitive understanding of the model’s focus.

In this research, Grad-CAM was applied to the Faster R-CNN–based railway defect detection framework to interpret model predictions visually. The generated heatmaps demonstrate that the model consistently attends to relevant defect regions, including missing bolts, missing fasteners, and rail cracks, while effectively ignoring irrelevant background areas.

This observation confirms that the model has learned meaningful feature representations and is making reliable decisions based on defect-specific visual cues. Consequently, the integration of Grad-CAM strengthens the interpretability and credibility of the proposed system, supporting its suitability for deployment in real-world railway inspection and maintenance operations.

## Explainability with Grad-CAM

<img width="200" height="500" alt="3" src="https://github.com/user-attachments/assets/2f50bfb7-404e-4cec-83d1-b1361e1984b4" />

---

## Web Application Development

The proposed web application was developed from scratch using Python Streamlit and integrated with the Faster R-CNN–based railway track defect detection model to support practical field deployment. Railway line videos were captured using two GoPro HERO5 cameras mounted on an inspection trolley, with GPS metadata embedded at the time of acquisition. These videos are processed within the web application, enabling real-time automated detection and localisation of railway track defects.

<img width="1920" height="1080" alt="17" src="https://github.com/user-attachments/assets/55253cd0-9c19-477f-b024-f7e8c937dc57" />

Figure 4.16 illustrates the login interface of the web application, which ensures secure and controlled access for authorised inspection personnel. Upon successful authentication, users are redirected to the home dashboard (Figure 4.17), where uploaded videos, processing status, and overall detection summaries are presented through a clean and intuitive interface.

<img width="976" height="471" alt="image" src="https://github.com/user-attachments/assets/47ec0479-6339-48a9-a8d5-326bdab4c3ed" />

After video processing is completed, detected defects—including missing bolts, missing fasteners, and rail cracks—are automatically visualised alongside their corresponding geographical locations. Figure 4.18 presents the map-based visualisation interface, where defect locations are displayed along railway tracks using GPS coordinates. This spatial representation enables maintenance teams to rapidly identify defect-prone segments and prioritise inspection and repair activities.

<img width="922" height="418" alt="image" src="https://github.com/user-attachments/assets/de4e958d-4c1e-4543-acca-79ebf6cab49f" />

All defect-related information is systematically recorded and made accessible for further analysis and decision support. As shown in Figure 4.19, the application provides detailed detection results in a structured tabular format. For each processed image, the system records the image name, detection status, number of detected defects, average confidence score, GPS availability, latitude and longitude, and processing time. This comprehensive presentation allows inspection personnel to efficiently review outcomes, evaluate prediction reliability, and correlate detected defects with precise geographic locations.

<img width="907" height="388" alt="image" src="https://github.com/user-attachments/assets/8abd47c4-3980-45a6-bfae-3a3ecbd4021c" />

Furthermore, Figure 4.20 illustrates a snapshot of the MongoDB database, where all detection records are securely stored in a structured format. Each record includes detection identifiers, timestamps, defect categories, confidence scores, and GPS coordinates. The application also generates an overall summary report of detected defects, facilitating data-driven maintenance planning and long-term infrastructure monitoring.

<img width="931" height="490" alt="image" src="https://github.com/user-attachments/assets/d45f7aaf-0c44-4def-93c4-b41e77283f87" />

By integrating automated defect detection, geolocation capabilities, interactive visualisation, explainability-ready outputs, and persistent data storage, the proposed web application provides a comprehensive, scalable, and deployable solution for intelligent railway track inspection and maintenance operations.

---

## Conclusion

This study presented Rail-Track Inspector, an explainable deep learning–based, locationaware web application for automated railway track defect detection and localization. The framework addresses limitations of traditional manual inspection, which is labor-intensive, time-consuming, and susceptible to human error, particularly under increasing rail traffic and ageing infrastructure. A Faster R-CNN object detection model was developed as the core detection engine and compared with baseline models under identical training conditions. Experimental results showed that Faster R-CNN achieved superior performance, attaining approximately 97% accuracy with improved precision, recall, and F1-score, thereby reducing false detections and missed defects.

To enhance transparency and reliability, Explainable Artificial Intelligence techniques were applied using Grad-CAM, confirming that the model focused on structurally relevant defect regions rather than background features. The validated model was subsequently integrated into a lightweight web application developed using Streamlit, enabling real-time video processing, defect visualization, and geolocation through GPS-enabled GoPro cameras. Detected defects, including confidence scores, timestamps, and geographic coordinates, were stored in a MongoDB database and visualized via an interactive mapping interface.

The proposed framework provides an integrated and deployable solution combining accurate defect detection, geolocation, explainability, and practical system implementation. Although validated using railway infrastructure data from Bangladesh, the approach remains scalable and adaptable to broader global railway networks, supporting safer and more efficient railway maintenance operations.

---
