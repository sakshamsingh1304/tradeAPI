import os
import logging
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Initialize Groq client
# expects GROQ_API_KEY environment variable to be set
client = Groq()

async def analyze_market_data(sector: str, search_context: str) -> str:
    """
    Uses the Groq API to act as a financial analyst.
    Takes the search snippets as context and generates a structured Markdown report.
    """
    logger.info(f"Generating LLM report for sector: {sector}")
    
    system_prompt = (
        "You are an expert financial analyst focusing on Indian markets. "
        "Your task is to analyze the provided search engine context regarding a specific sector "
        "and output a highly structured, professional market analysis report entirely in Markdown format. "
        "The report should include sections like 'Executive Summary', 'Current Market Trends', 'Key Trade Opportunities in India', "
        "'Challenges & Risks', and 'Future Outlook'. "
        "Do not include generic advice outside of the context provided, but analyze the context deeply to find business opportunities. "
        "If the context lacks information, state so professionally within the report."
    )
    
    user_prompt = f"Sector: {sector}\n\nSearch Context:\n{search_context}\n\nPlease generate the analysis report based only on the context."

    try:
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            temperature=0.3,
            max_tokens=2048,
        )
        return completion.choices[0].message.content
    except Exception as e:
        logger.error(f"Error during Groq LLM completion: {e}")
        return f"### Error Generating Report\nAn error occurred while analyzing the data: {str(e)}"
