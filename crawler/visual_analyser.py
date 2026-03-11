import os
import json
import base64
import logging
from typing import List, Dict, Optional
from pydantic import SecretStr
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

logger = logging.getLogger("qa_crawler.visual_analyser")

class VisualAnalyser:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.warning("VisualAnalyser: No GEMINI_API_KEY found. Vision features will be disabled.")
            self.model = None
            return

        try:
            self.model = ChatGoogleGenerativeAI(
                model="gemini-2.0-flash",
                google_api_key=SecretStr(self.api_key),
                temperature=0.1
            )
            logger.info("VisualAnalyser initialized with Gemini 2.0 Flash Vision.")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini Vision: {e}")
            self.model = None

    async def identify_interactives(self, screenshot_path: str, url: str) -> List[Dict]:
        """
        Analyzes a screenshot to find interactive elements (buttons, links, inputs).
        Returns a list of dicts with {name, type, x, y, description}.
        """
        if not self.model or not os.path.exists(screenshot_path):
            return []

        try:
            with open(screenshot_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode("utf-8")

            prompt = (
                f"You are a specialized UI QA agent. Look at this screenshot of {url}.\n"
                "Identify every interactive element (Buttons, Links, Inputs, Toggles, Dropdowns).\n"
                "Specifically hunt for ICON-ONLY buttons that have no text labels.\n"
                "Return the results ONLY as a JSON list of objects with the following keys:\n"
                "- 'name': A semantic name for the element (e.g., 'settings_cog', 'search_icon')\n"
                "- 'type': The type of element (button, link, input, etc.)\n"
                "- 'x': The horizontal center of the element in pixels.\n"
                "- 'y': The vertical center of the element in pixels.\n"
                "- 'description': A brief explanation of what this element likely does.\n\n"
                "IMPORTANT: Return ONLY the JSON array. Output nothing else."
            )

            message = HumanMessage(
                content=[
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{image_data}"},
                    },
                ]
            )

            response = await self.model.ainvoke([message])
            raw_content = response.content.strip()
            
            # Basic JSON cleanup in case of markdown blocks
            if "```json" in raw_content:
                raw_content = raw_content.split("```json")[1].split("```")[0].strip()
            elif "```" in raw_content:
                raw_content = raw_content.split("```")[1].split("```")[0].strip()

            elements = json.loads(raw_content)
            logger.info(f"VisualAnalyser: Discovered {len(elements)} elements visually.")
            return elements

        except Exception as e:
            logger.error(f"Visual analysis failed: {e}")
            return []
