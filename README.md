# 🌱 AgriScan - AI-Powered Agricultural Ecosystem

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white)

AgriScan is a comprehensive, full-stack **MCA Major Project** designed to empower farmers with Artificial Intelligence. It is not just an AI scanner; it is a complete agricultural ecosystem that includes disease detection, expert consultations, an e-commerce marketplace, and real-time weather alerts.

## ✨ Key Features

### 🧑‍🌾 Farmer Portal

- **AI Disease Detection:** Upload a leaf image, and a trained TensorFlow (MobileNetV2) model will diagnose the disease.
- **Explainable AI (Grad-CAM):** Generates a visual heatmap highlighting the exact spots on the leaf that triggered the AI's diagnosis, building user trust.
- **Severity Assessment:** Analyzes and displays the percentage of the leaf surface affected by the disease.
- **AI Agronomist Chatbot:** A floating conversational agent to answer quick follow-up questions about dosages, weather, or treatments.
- **Smart E-Commerce:** Buy recommended fertilizers and pesticides through a fully functional marketplace with a mock payment gateway and SMS receipts.
- **Expert Consultations:** Book 1-on-1 video calls with certified agronomists.
- **Community Forum:** Ask questions and share knowledge with other farmers.
- **Weather Alerts:** Integrated with OpenWeatherMap to warn farmers about high humidity or heatwaves that accelerate disease spread.

### 👨‍🔬 Expert (Agronomist) Portal

- **Case Escalation Inbox:** A triage dashboard showing cases where AI confidence dropped below 70%.
- **Diagnostic Interface:** Side-by-side view of the farmer's uploaded image, the AI Heatmap, and environmental metadata (Soil pH, humidity, etc.).
- **Digital Prescription Pad:** Experts can write confirmed diagnoses, organic cures, chemical cures, and preventative practices.
- **Tele-medicine:** Integrated Jitsi Meet for live video consultations.

### 🏪 Seller Portal

- **Analytics Dashboard:** Visual revenue tracking, top-selling products chart (Chart.js), and low-stock alerts.
- **Inventory Management:** Add, update, and track products in the marketplace.

### 🛡️ Admin Portal

- **Platform Analytics:** Bird's-eye view of total AI scans, registered users, and orders, with a Chart.js graph of the most detected diseases.
- **Django Admin:** Complete control over 16+ database tables.

---

## 💻 Tech Stack

- **Backend:** Python 3, Django 5/6
- **Machine Learning:** TensorFlow, Keras (MobileNetV2), NumPy
- **Computer Vision:** OpenCV (for Grad-CAM heatmap generation)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap 5, Chart.js
- **Database:** SQLite (Development)
- **Third-Party APIs:** OpenWeatherMap (Weather), Jitsi Meet (Video Calls), ReportLab (PDF Generation)

---

## 🚀 Local Installation Guide

1. **Clone the repository:**

   ```bash
   git clone https://github.com/your-username/agriscan.git
   cd agriscan

   ```

2. **Create a virtual environment:**

   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Mac/Linux
   source venv/bin/activate

   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt

   ```

4. **Set up the database:**

  ```bash
  python manage.py makemigrations
  python manage.py migrate

  ```

5. **Train the AI Model(Optional - if ```crop_disease_model.h5``` is not present):**
Download the PlantVillage dataset from Kaggle.

Place the color folder in the root directory and rename it to PlantVillage.

Run python train_model.py or python fast_train.py.

6. **Seed the Database(Populate with dummy products and experts):**
  
   ```bash
   python manage.py shell
   # Run the provided seed scripts for experts, products, and diseases.
   ```
7. Run the server:
 
   ```bash
   python manage.py runserver
   ```
  Open ```http://127.0.0.1:8000``` in your browser.

  ---

## 🔑 Demo Credentials

To test the different roles of the platform, use the following accounts. *(Password for all test accounts is `pass12345`)*.

| Role | Username | Password | Key Features to Test |
| :--- | :--- | :--- | :--- |
| 🧑‍🌾 **Farmer** | `farmer_raj` | `pass12345` | Scan leaves, view heatmaps, buy products, book experts. |
| 👨‍🔬 **Agronomist** | `dr_smith` | `pass12345` | Review escalated AI cases, write digital prescriptions. |
| 🏪 **Seller** | `seller1` | `pass12345` | View revenue charts, manage product inventory. |
| 🛡️ **Admin** | `riya` | `pass12345` | View platform analytics, access Django Admin. |

---
---

## 🧠 How the AI Works

1. **Transfer Learning:** We use a pre-trained **MobileNetV2** base model, fine-tuned on the PlantVillage dataset (54,000+ images across 38 classes).
2. **Grad-CAM (Explainable AI):** When an image is classified, the gradients of the target class are computed with respect to the final convolutional layer. This generates a heatmap showing which pixels (e.g., brown spots) contributed most to the prediction, building farmer trust.
3. **Fallback Mechanism:** 
   - If the AI confidence is **below 60%**, the system flags it as an "Unknown" image to prevent false positives.
   - If it is between **60% and 70%**, the system automatically escalates the case to a human expert via the **Triage Inbox**.

---

