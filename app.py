"""
EduPal AI - Streamlit Application
"""
import streamlit as st
import requests
import json
import re
import base64
import io
from typing import Optional, Dict, Any
from PyPDF2 import PdfReader


class Config:
    """Application configuration and constants"""
    API_URL = "https://65t9tjsps7.execute-api.us-west-2.amazonaws.com/edupal_stage1/ai"
    API_KEY = "nuW2OzPpPr3Kv2acZZxez86LAAx45KS34U8gDET0"
    
    # UI Constants
    PAGE_TITLE = "🎓 EduPal - AWS-Powered AI Study Assistant"
    PAGE_LAYOUT = "wide"
    
    # File processing
    SUPPORTED_FILE_TYPES = ['pdf', 'txt']
    MAX_FILE_SIZE_MB = 10


class ResponseCleaner:
    """Handles cleaning and formatting of AI responses"""
    
    @staticmethod
    def clean_response(text: str) -> str:
        """
        Remove reasoning tags and extract only clean text from AI responses
        Args:
            text: Raw AI response text   
        Returns:
            Cleaned and formatted text
        """
        if not text or not isinstance(text, str):
            return text
        patterns_to_remove = [
            (r'<thinking>.*?</thinking>', ''), 
            (r'<reasoning>.*?</reasoning>', ''),  
            (r'</?[a-z_]+>', ''),
            (r'^(Here( is| are|’s)|Based on|The answer is|In summary)[:\s]*', ''),
        ]
        cleaned_text = text
        for pattern, replacement in patterns_to_remove:
            cleaned_text = re.sub(pattern, replacement, cleaned_text, flags=re.DOTALL | re.IGNORECASE)
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        if cleaned_text and cleaned_text[0].islower():
            cleaned_text = cleaned_text[0].upper() + cleaned_text[1:]
            
        return cleaned_text


class FileProcessor:
    """Handles file uploads and text extraction"""
    @staticmethod
    def extract_text_from_pdf(uploaded_file) -> Optional[str]:
        """
        Extract text content from uploaded PDF file
        Args:
            uploaded_file: Streamlit file uploader object   
        Returns:
            Extracted text or None if failed
        """
        try:
            pdf_reader = PdfReader(uploaded_file)
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"Page {page_num + 1}:\n{page_text}\n\n"
            return text.strip() if text.strip() else None    
        except Exception as e:
            st.error(f"❌ Error reading PDF: {str(e)}")
            return None
    @staticmethod
    def extract_text_from_txt(uploaded_file) -> Optional[str]:
        """
        Extract text content from uploaded text file
        Args:
            uploaded_file: Streamlit file uploader object   
        Returns:
            Extracted text or None if failed
        """
        try:
            text_content = str(uploaded_file.read(), "utf-8")
            return text_content.strip() if text_content.strip() else None
        except Exception as e:
            st.error(f"❌ Error reading text file: {str(e)}")
            return None
    
    @staticmethod
    def get_file_details(uploaded_file) -> Dict[str, str]:
        """
        Get formatted file details for display
        Args:
            uploaded_file: Streamlit file uploader object   
        Returns:
            Dictionary of file details
        """
        return {
            "Filename": uploaded_file.name,
            "File size": f"{uploaded_file.size / 1024:.2f} KB",
            "File type": uploaded_file.type
        }


class APIClient:
    """Handles communication with the backend API"""
    def __init__(self):
        self.api_url = Config.API_URL
        self.headers = {
            "x-api-key": Config.API_KEY,
            "Content-Type": "application/json"
        }
        self.cleaner = ResponseCleaner()
    
    def call_backend(self, action: str, text: str = "", user_input: str = "") -> str:
        """
        Make API call to backend Lambda function
        Args:
            action: AI action to perform (qa, summarize, quiz, feedback)
            text: Input text for processing
            user_input: Additional user input (questions, answers, etc.)   
        Returns:
            Cleaned AI response or error message
        """
        payload = {
            "action": action,
            "text": text,
            "input": user_input
        }
        try:
            response = requests.post(self.api_url, json=payload, headers=self.headers, timeout=30)
            if response.status_code == 200:
                response_data = response.json()
                raw_response = self._extract_response_data(response_data)
                return self.cleaner.clean_response(raw_response)
            else:
                return f"🚨 API Error {response.status_code}: {response.text}"      
        except requests.exceptions.Timeout:
            return "⏰ Request timeout - please try again"
        except requests.exceptions.ConnectionError:
            return "🔌 Connection error - check your internet connection"
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    def _extract_response_data(self, response_data: Dict) -> str:
        """Extract response data from different API response formats"""
        if 'body' in response_data:
            body_content = json.loads(response_data['body'])
            return body_content.get('response', 'No response found')
        else:
            return response_data.get('response', 'No response found')


class UIManager:
    """Manages Streamlit UI components and layout"""
    def __init__(self):
        self.api_client = APIClient()
        self.setup_page()
    def setup_page(self):
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title=Config.PAGE_TITLE,
            layout=Config.PAGE_LAYOUT,
            initial_sidebar_state="expanded"
        )
        st.title(Config.PAGE_TITLE)
    
    def render_file_upload_section(self):
        """Render file upload section with PDF and text file support"""
        st.header("📁 Upload Document")
        
        uploaded_file = st.file_uploader(
            "Choose a PDF or text file",
            type=Config.SUPPORTED_FILE_TYPES,
            help="Upload PDF documents or text files for AI analysis"
        )
        if uploaded_file is not None:
            self._process_uploaded_file(uploaded_file)
    
    def _process_uploaded_file(self, uploaded_file):
        """Process uploaded file and extract text content"""
        file_details = FileProcessor.get_file_details(uploaded_file)
        st.write("**File Details:**", file_details)
        extracted_text = None
        #process based on file type
        if uploaded_file.type == "application/pdf":
            with st.spinner("📄 Extracting text from PDF..."):
                extracted_text = FileProcessor.extract_text_from_pdf(uploaded_file)
        elif uploaded_file.type == "text/plain":
            extracted_text = FileProcessor.extract_text_from_txt(uploaded_file)

        if extracted_text:
            st.session_state.extracted_text = extracted_text
            st.session_state.current_text = extracted_text
            st.success(f"✅ Document processed successfully! Extracted {len(extracted_text)} characters")
            with st.expander("👁️ View Document Content"):
                st.text_area("Extracted Content", extracted_text, height=200, key="preview")
        else:
            st.error("❌ Could not extract text from the uploaded file")
    
    def render_text_input_section(self):
        """Render manual text input section"""
        st.header("📝 Or Paste Text")
        
        manual_text = st.text_area(
            "Enter text manually:",
            height=200,
            placeholder="Type or paste your study material, notes, or textbook content here...",
            help="Paste any text content you want to analyze with AI"
        )
        
        if manual_text:
            st.session_state.current_text = manual_text
            st.success(f"✅ Text ready for analysis! ({len(manual_text)} characters)")
    
    def render_ai_features_section(self):
        """Render AI-powered features section"""
        st.markdown("---")
        st.header("🤖 AI Study Features")
        if 'current_text' not in st.session_state or not st.session_state.current_text:
            st.info("👆 Please upload a document or paste text above to get started!")
            return
        current_text = st.session_state.current_text
        tab1, tab2, tab3 = st.tabs(["💬 Q&A Chatbot", "📄 Summary Generator", "🎯 Quiz & Feedback"])
        with tab1:
            self._render_qa_chatbot(current_text)
        with tab2:
            self._render_summary_generator(current_text)
        with tab3:
            self._render_quiz_features(current_text)
    
    def _render_qa_chatbot(self, text: str):
        """Render Q&A chatbot interface"""
        st.subheader("Ask Questions About Your Document")
        question = st.text_input(
            "Enter your question:",
            placeholder="What would you like to know about this content?",
            key="qa_question"
        )
        if st.button("Get Answer", key="qa_button") and question:
            with st.spinner("🤔 AI is analyzing your question..."):
                answer = self.api_client.call_backend("qa", text, question)
                st.success("**Answer:**")
                st.write(answer)
    
    def _render_summary_generator(self, text: str):
        """Render text summarization interface"""
        st.subheader("Generate Study Guide")
        if st.button("Create Summary", key="summary_button"):
            with st.spinner("📚 Creating your study guide..."):
                summary = self.api_client.call_backend("summarize", text)
                st.success("**Study Guide:**")
                st.write(summary)
    
    def _render_quiz_features(self, text: str):
        """Render quiz generation and feedback interface"""
        st.subheader("Practice Quiz")
        if st.button("Generate Quiz", key="quiz_button"):
            with st.spinner("🎯 Creating quiz questions..."):
                quiz = self.api_client.call_backend("quiz", text)
                st.session_state.quiz = quiz
                st.session_state.quiz_questions = self._parse_quiz_questions(quiz)
                st.success("**Quiz Generated!**")
        if 'quiz' in st.session_state and st.session_state.quiz:
            st.markdown("---")
            st.subheader("📝 Generated Quiz")
            st.write(st.session_state.quiz)
            st.markdown("---")
            st.subheader("✅ Check Your Answers")
            col1, col2 = st.columns([2, 1])
            with col1:
                if 'quiz_questions' in st.session_state and st.session_state.quiz_questions:
                    question_options = list(st.session_state.quiz_questions.keys())
                    selected_question = st.selectbox(
                        "Select a question to check:",
                        options=question_options,
                        key="question_selector"
                    )
                    question_text = st.text_input(
                        "Question:",
                        value=selected_question,
                        key="feedback_question",
                        disabled=True
                    )
                else:
                    question_text = st.text_input(
                        "Enter the question:",
                        placeholder="Copy and paste the question from above...",
                        key="feedback_question"
                    )
                user_answer = st.text_input(
                    "Your answer (A/B/C/D):",
                    placeholder="Enter A, B, C, or D",
                    key="user_answer"
                ).upper().strip()   
            with col2:
                correct_answer = st.text_input(
                    "Correct answer (A/B/C/D):",
                    placeholder="Enter correct letter",
                    key="correct_answer"
                ).upper().strip()
                
                st.markdown("---")
                check_button = st.button(
                    "🎯 Check Answer", 
                    key="feedback_button",
                    type="primary",
                    use_container_width=True
                )
            if check_button:
                if not all([question_text, user_answer, correct_answer]):
                    st.error("❌ Please fill in all fields: question, your answer, and correct answer")
                elif user_answer not in ['A', 'B', 'C', 'D']:
                    st.error("❌ Please enter a valid answer (A, B, C, or D)")
                elif correct_answer not in ['A', 'B', 'C', 'D']:
                    st.error("❌ Please enter a valid correct answer (A, B, C, or D)")
                else:
                    with st.spinner("🔍 Analyzing your answer..."):
                        feedback_data = {
                            "question": question_text,
                            "user_answer": user_answer,
                            "correct_answer": correct_answer
                        }
                        feedback = self.api_client.call_backend("feedback", "", json.dumps(feedback_data))
                        
                        # Display feedback with appropriate styling
                        if user_answer == correct_answer:
                            st.success(f"✅ **Correct!**\n\n{feedback}")
                        else:
                            st.error(f"❌ **Incorrect**\n\n{feedback}")

    def _parse_quiz_questions(self, quiz_text: str) -> dict:
        """
        Parse quiz text to extract individual questions for dropdown
        Args:
            quiz_text: Raw quiz text from AI 
        Returns:
            Dictionary of question_number: question_text
        """
        questions = {}
        try:
            lines = quiz_text.split('\n')
            current_question = ""
            question_number = 1
            for line in lines:
                line = line.strip()
                if line and (line.startswith(f'{question_number}.') or line.startswith(f'{question_number} ')):
                    if current_question:
                        questions[f"Q{question_number}"] = current_question.strip()
                        question_number += 1
                        current_question = line
                    else:
                        current_question = line
                elif current_question and line:
                    current_question += " " + line
            if current_question:
                questions[f"Q{question_number}"] = current_question.strip()        
        except Exception as e:
            st.warning(f"Note: Could not parse quiz questions for dropdown. Error: {str(e)}")
        return questions
    
    def render_sidebar(self):
        """Render application sidebar"""
        with st.sidebar:
            st.title("ℹ️ About EduPal")
            st.markdown("""
            **EduPal** is an AI-powered study assistant that helps you:
            -  Understand complex documents
            -  Get instant answers to questions  
            -  Create study guides
            -  Test your knowledge with quizzes
            """)
            st.markdown("### 🔧 AWS Services Used:")
            st.markdown("""
            - **Amazon Bedrock** (AI Models)
            - **AWS Lambda** (Backend Processing)
            - **API Gateway** (REST API)
            - **EC2** (Web Application)
            """)
            # debugging
            with st.expander("Technical Details"):
                if 'current_text' in st.session_state:
                    st.write(f"**Text length:** {len(st.session_state.current_text)} characters")
                
                if st.button("Test API Connection"):
                    with st.spinner("Testing..."):
                        result = self.api_client.call_backend("qa", "AI is artificial intelligence", "What is AI?")
                        st.write(f"**Test Result:** {result}")

class EduPalApp:
    """Main application class orchestrating the EduPal AI interface"""
    def __init__(self):
        self.ui_manager = UIManager()
    def run(self):
        """Main application entry point"""
        try:
            col1, col2 = st.columns([1, 1])
            with col1:
                self.ui_manager.render_file_upload_section()
            with col2:
                self.ui_manager.render_text_input_section()
            self.ui_manager.render_ai_features_section()
            self.ui_manager.render_sidebar()  
        except Exception as e:
            st.error(f"Application error: {str(e)}")
            st.info("Please refresh the page and try again.")

# Application entry point
if __name__ == "__main__":
    app = EduPalApp()
    app.run()