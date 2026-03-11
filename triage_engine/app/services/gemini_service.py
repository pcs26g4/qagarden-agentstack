import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

# Set up logging
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key)

import base64
from typing import Optional

def generate_bug_report_with_gemini(failure_text: str, screenshot_b64: Optional[str] = None) -> dict:
    """
    Generate a high-quality bug report using Google Gemini AI with Vision support.
    """
    if not api_key:
        return {
            "title": "Gemini API Error",
            "description": "Gemini API key not configured in .env file."
        }

    try:
        # Prioritize 2.0 flash for its superior speed and multimodal capabilities
        model_name = os.getenv("GEMINI_MODEL", 'gemini-2.0-flash')
        model = genai.GenerativeModel(model_name)
        
        prompt = f"""
You are an elite Senior QA Automation Engineer and Bug Triage Specialist.

Read the FAILED TEST DETAILS and analyze the provided visual evidence (if any) to synthesize a high-quality bug report.

STRICT REQUIREMENTS:
1. TITLE: A concise, impactful title (max 80 characters).
2. DESCRIPTION: A detailed, narrative explanation (160-220 words).
3. Do NOT repeat raw stack traces verbatim.
4. Use professional language.
5. Identify Expected vs Actual behavior clearly.
6. Suggest a likely root cause (UI, API, Data, or Infrastructure).
7. If a screenshot is provided, explicitly reference what you see (or don't see) in the UI.

FAILED TEST DETAILS:
{failure_text}

Provide the output in the following format:
TITLE: [Your Title Here]
DESCRIPTION: [Your Detailed Description Here]
"""

        content = [prompt]
        if screenshot_b64:
            try:
                # Prepare the image part for Gemini
                image_data = base64.b64decode(screenshot_b64)
                content.append({
                    "mime_type": "image/jpeg",
                    "data": image_data
                })
            except Exception as e:
                logger.error(f"Failed to decode screenshot: {e}")

        response = model.generate_content(content)
        text = response.text
        
        # Parse title and description
        title = "Automated Test Failure"
        description = text
        
        if "TITLE:" in text and "DESCRIPTION:" in text:
            parts = text.split("DESCRIPTION:", 1)
            title = parts[0].replace("TITLE:", "").strip()
            description = parts[1].strip()
            
        return {
            "title": title,
            "description": description
        }

    except Exception as e:
        print(f"Gemini generation error: {str(e)}")
        raise e
