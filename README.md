# EduPal AI - AWS-Powered Study Assistant

EduPal AI is an intelligent study assistant developed during the **Manara & AWS GANAI Hackathon**.
It leverages **AWS Generative AI services** to help students and lifelong learners process educational materials, generate summaries, create quizzes, and receive instant answers to their questions — all in one platform.

---

## 🎥 Demo Video  
[![Watch the Demo](https://img.icons8.com/clouds/200/000000/play.png)](https://github.com/mariamalaa76/EduPal_APP/raw/main/Demo_EduPal.mp4)

---

## 🛠️ Technologies Used

### Frontend

* **Streamlit** – Web application framework
* **PyPDF2** – PDF text extraction

### Backend & AI

* **AWS Bedrock** – Generative AI models (Claude, DeepSeek)
* **AWS Lambda** – Serverless backend functions
* **Amazon API Gateway** – REST API endpoints
* **Amazon EC2** – Application hosting

### Infrastructure

* **AWS IAM** – Security and permissions
* **Amazon S3** – File storage (optional)

---

## 📋 Features

* 📁 **Document Processing** – Upload and process PDFs or text files
* 🤖 **Q&A Chatbot** – Ask questions directly about your materials
* 📄 **Smart Summarization** – Generate concise study notes
* 🎯 **Quiz Generator** – Automatically create practice quizzes
* ✅ **Answer Feedback** – Receive explanations and learning insights

---

## 🏗️ Architecture

```
Frontend (Streamlit on EC2) → API Gateway → Lambda → AWS Bedrock AI
```

---

## 📥 Installation & Setup

### Prerequisites

* Python 3.9+
* AWS Account with Bedrock access
* Git

### 1. Clone Repository

```bash
git clone https://github.com/Omarrhussain/EduPal_APP.git
cd EduPal_APP
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

**requirements.txt**

```
streamlit
boto3
requests
PyPDF2
```

### 3. AWS Configuration

* Enable Bedrock Access:

  * Go to **AWS Console → Amazon Bedrock → Model Access**
  * Request access for `deepseek.r1-v1:0`

* Configure AWS Credentials:

```bash
aws configure
# Enter AWS Access Key, Secret Key, and Region
```

### 4. Run Application

```bash
streamlit run app.py
```

---

## 🚀 Deployment

### AWS Elastic Beanstalk

1. **Initialize EB Application**

```bash
pip install awsebcli
eb init -p python-3.9 edupal-app --region us-east-2
eb create edupal-prod-env
```

2. **Deploy Application**

```bash
eb deploy
eb open
```

3. **Environment Variables**
   Set in Elastic Beanstalk console:

* `AWS_ACCESS_KEY_ID`
* `AWS_SECRET_ACCESS_KEY`
* `AWS_DEFAULT_REGION`

---

## 🔧 API Endpoints

| Endpoint | Method | Description                                                         |
| -------- | ------ | ------------------------------------------------------------------- |
| `/ai`    | POST   | Main AI processing endpoint (`qa`, `summarize`, `quiz`, `feedback`) |

---

**EduPal AI – Making studying smarter with AWS Generative AI! 🎓**

---

👉 Do you want me to also **add badges (like GitHub stars, license, Python version, AWS logo)** at the top of your README to make it look even more professional?
