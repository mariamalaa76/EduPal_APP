"""
EduPal AI Backend - AWS Lambda Function
"""
import json
import boto3
import io
import base64
from typing import Dict, Any, Optional
import PyPDF2

class PDFProcessor:
    """Handles PDF file processing and text extraction"""
    @staticmethod
    def extract_text_from_pdf(pdf_base64: str) -> str:
        """
        Extract text from base64 encoded PDF file
        Args:
            pdf_base64: Base64 encoded PDF data   
        Returns:
            Extracted text from PDF    
        Raises:
            Exception: If PDF processing fails
        """
        try:
            if not pdf_base64:
                raise ValueError("Empty PDF data provided")
            pdf_bytes = base64.b64decode(pdf_base64)
            # Create PDF reader and extract text
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
            text = ""
            for page_num, page in enumerate(pdf_reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += f"Page {page_num + 1}:\n{page_text}\n\n"
            if not text.strip():
                raise ValueError("No extractable text found in PDF")    
            return text.strip()    
        except Exception as e:
            raise Exception(f"PDF processing failed: {str(e)}")

class AIResponseHandler:
    """Handles AI model interactions and response generation"""
    def __init__(self):
        self.bedrock = boto3.client('bedrock-runtime')
        self.model_id = 'deepseek.r1-v1:0'
    
    def _invoke_model(self, messages: list, max_tokens: int = 300) -> str:
        """
        Invoke the Bedrock AI model with given messages
        Args:
            messages: List of message dictionaries
            max_tokens: Maximum tokens in response   
        Returns:
            AI generated response text
        """
        try:
            response = self.bedrock.invoke_model(
                modelId=self.model_id,
                body=json.dumps({
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.1
                })
            )
            response_body = json.loads(response['body'].read())
            return response_body['choices'][0]['message']['content']   
        except Exception as e:
            raise Exception(f"AI model invocation failed: {str(e)}")
    
    def handle_question_answer(self, context: str, question: str) -> str:
        """Generate answer for question based on context"""
        messages = [
            {
                "role": "user",
                "content": f"""Answer this question based on the text below.
Text: {context}
Question: {question}
Provide a concise and accurate answer."""
            }
        ]
        return self._invoke_model(messages, max_tokens=300)
    
    def generate_summary(self, text: str) -> str:
        """Generate bullet point summary from text"""
        messages = [
            {
                "role": "user",
                "content": f"""Create a well-structured bullet point summary of this text:
{text}
Focus on key concepts and main ideas."""
            }
        ]
        return self._invoke_model(messages, max_tokens=400)
    
    def generate_quiz(self, text: str) -> str:
        """Generate formatted quiz questions from text"""
        messages = [
            {
                "role": "user",
                "content": f"""Create 3 multiple-choice questions about this text:
        {text}
        Format each question EXACTLY like this:
        Q1. [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]

        Q2. [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]

        Q3. [Question text]
        A) [Option A]
        B) [Option B]
        C) [Option C]
        D) [Option D]

        Ensure each question starts with Q1., Q2., Q3. and options use A), B), C), D) format."""
            }
        ]
        return self._invoke_model(messages, max_tokens=600)
    
    def handle_feedback(self, question: str, user_answer: str, correct_answer: str) -> str:
        """Provide feedback on quiz answers with better context"""
        messages = [
            {
                "role": "user",
                "content": f"""Please provide feedback on this quiz answer:

    Question: {question}

    User's Answer: {user_answer}
    Expected Correct Answer: {correct_answer}

    Provide constructive feedback that:
    1. First states whether the user's answer matches the expected answer
    2. Explains why the expected answer is correct
    3. Provides educational insights about the topic
    4. Is encouraging and helpful for learning
    Keep the feedback concise but informative."""
            }
        ]
        return self._invoke_model(messages, max_tokens=300)


class ResponseBuilder:
    """Builds standardized API responses"""
    @staticmethod
    def build_success_response(data: Any, action: str) -> Dict[str, Any]:
        """
        Build successful API response
        Args:
            data: Response data to include
            action: Action that was performed    
        Returns:
            Formatted API response
        """
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': True,
                'action': action,
                'response': data,
                'timestamp': json.dumps(str(Any))
            })
        }
    
    @staticmethod
    def build_error_response(message: str, status_code: int = 400) -> Dict[str, Any]:
        """
        Build error API response
        Args:
            message: Error message
            status_code: HTTP status code   
        Returns:
            Formatted error response
        """
        return {
            'statusCode': status_code,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'success': False,
                'error': message,
                'timestamp': json.dumps(str(Any))
            })
        }


class EduPalAIService:
    """Main service class orchestrating EduPal AI functionality"""
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.ai_handler = AIResponseHandler()
        self.response_builder = ResponseBuilder()
    
    def process_request(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process incoming API requests and route to appropriate handlers
        Args:
            event: Lambda event object  
        Returns:
            Formatted API response
        """
        try:
            body = self._parse_request_body(event)
            action = body.get('action', '').lower()
            # Route to appropriate handler
            if action == 'process_pdf':
                return self._handle_pdf_processing(body)
            elif action in ['qa', 'summarize', 'quiz', 'feedback']:
                return self._handle_ai_actions(action, body)
            else:
                return self.response_builder.build_error_response(
                    f"Invalid action: {action}. Supported actions: process_pdf, qa, summarize, quiz, feedback"
                )        
        except Exception as e:
            #debugging
            print(f"Error processing request: {str(e)}")
            return self.response_builder.build_error_response(f"Internal server error: {str(e)}", 500)
    
    def _parse_request_body(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and validate request body"""
        if 'body' in event:
            return json.loads(event['body'])
        return event
    
    def _handle_pdf_processing(self, body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle PDF processing requests"""
        pdf_data = body.get('pdf_data', '')
        if not pdf_data:
            return self.response_builder.build_error_response("No PDF data provided")
        extracted_text = self.pdf_processor.extract_text_from_pdf(pdf_data)
        return self.response_builder.build_success_response(extracted_text, 'process_pdf')
    
    def _handle_ai_actions(self, action: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """Handle AI-powered feature requests"""
        text = body.get('text', '')[:5000]
        if not text.strip():
            return self.response_builder.build_error_response("No text content provided")
        # Route to specific AI action
        if action == 'qa':
            question = body.get('input', '')
            if not question:
                return self.response_builder.build_error_response("No question provided")
            result = self.ai_handler.handle_question_answer(text, question)   
        elif action == 'summarize':
            result = self.ai_handler.generate_summary(text)    
        elif action == 'quiz':
            result = self.ai_handler.generate_quiz(text)    
        elif action == 'feedback':
            question = body.get('question', '')
            user_answer = body.get('user_answer', '')
            correct_answer = body.get('correct_answer', '')
            if not all([question, user_answer, correct_answer]):
                return self.response_builder.build_error_response(
                    "Missing required fields for feedback: question, user_answer, correct_answer"
                )
            result = self.ai_handler.provide_feedback(question, user_answer, correct_answer)
        return self.response_builder.build_success_response(result, action)

edupal_service = EduPalAIService()

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda entry point for EduPal AI backend
    Args:
        event: Lambda event object
        context: Lambda context object   
    Returns:
        Formatted API response
    """
    print(f"Received event: {json.dumps(event)}")
    try:
        return edupal_service.process_request(event)  
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        print(error_msg)
        return ResponseBuilder.build_error_response(error_msg, 500)