EduPal AI - AWS-Powered Study Assistant
EduPal is an intelligent study assistant that leverages AWS AI services to help students and learners process educational materials, generate summaries, create quizzes, and get instant answers to their questions.

🚀 Live Demo
Access the application: EduPal Live App

🛠️ Technologies Used
Frontend
Streamlit - Web application framework

PyPDF2 - PDF text extraction

Backend & AI
AWS Bedrock - Generative AI models (Claude, DeepSeek)

AWS Lambda - Serverless backend functions

API Gateway - REST API endpoints

EC2 - Application hosting

Infrastructure
AWS IAM - Security and permissions

Amazon S3 - File storage (optional)

📋 Features
📁 Document Processing: Upload PDFs and text files

🤖 Q&A Chatbot: Ask questions about your study materials

📄 Smart Summarization: Generate concise study guides

🎯 Quiz Generator: Create practice quizzes automatically

✅ Answer Feedback: Get explanations for quiz answers

🏗️ Architecture
text
Frontend (Streamlit on EC2) → API Gateway → Lambda → Bedrock AI
📥 Installation & Setup
Prerequisites
Python 3.9+

AWS Account with Bedrock access

Git

1. Clone Repository
bash
git clone https://github.com/Omarrhussain/EduPal_APP.git
cd EduPal_APP
2. Install Dependencies
bash
pip install -r requirements.txt
requirements.txt:

txt
streamlit
boto3
requests
PyPDF2

3. AWS Configuration
Enable Bedrock Access:

AWS Console → Amazon Bedrock → Model Access

Request access for: deepseek.r1-v1:0

Configure AWS Credentials:

bash
aws configure
# Enter your AWS Access Key, Secret Key, and Region
4. Run Application
bash
streamlit run app.py

🚀 Deployment
🚀 AWS Elastic Beanstalk Deployment
1. Initialize EB Application
bash
# Install EB CLI
pip install awsebcli

# Initialize Elastic Beanstalk
eb init -p python-3.9 edupal-app --region us-east-2

# Create environment
eb create edupal-prod-env
2. Configuration Files
.ebextensions/streamlit.config:

3. Deploy Application
bash
# Deploy to Elastic Beanstalk
eb deploy

# Open application
eb open
4. Environment Variables
Set in Elastic Beanstalk console:

AWS_ACCESS_KEY_ID

AWS_SECRET_ACCESS_KEY

AWS_DEFAULT_REGION

🔧 API Endpoints
Endpoint	Method	Description
/ai	POST	Main AI processing endpoint
Actions: qa, summarize, quiz, feedback		

💡 Usage
Upload Documents: PDF or text files

Paste Text: Manual text input

Use AI Features:

Ask questions about content

Generate study summaries

Create practice quizzes

Check answers with feedback

🔒 AWS Services Setup
Lambda Function
Runtime: Python 3.9

Permissions: AmazonBedrockFullAccess

Handler: lambda_function.lambda_handler

API Gateway
REST API with CORS enabled

Integration: Lambda proxy

API Key required

Elastic Beanstalk Benefits
✅ Auto-scaling - Handles traffic spikes

✅ Load balancing - Distributes traffic evenly

✅ Health monitoring - Automatic recovery

✅ Easy deployment - Simple update process

✅ Managed infrastructure - No server maintenance

🚀 Deployment Commands
bash
# Deploy updates
eb deploy

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

EduPal AI - Making studying smarter with AWS AI services! 🎓

Deployed on AWS Elastic Beanstalk for scalable, reliable performance


