from typing import List, Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from kairon.research_agent import ResearchState
from .config import GOOGLE_API_KEY

class DraftState(BaseModel):
    """State for the drafting process."""
    research_state: ResearchState = Field(default_factory=lambda: ResearchState(research_question=""))
    current_draft: str = ""
    revision_count: int = 0

    class Config:
        arbitrary_types_allowed = True

class DraftAgent:
    def __init__(self):
        """Initialize the draft agent."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # Combine system and human messages into a single human message
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a drafting agent specialized in creating clear, concise, and well-structured content.
            Your task is to:
            1. Synthesize research findings into coherent narratives
            2. Maintain accuracy and relevance to the original research question
            3. Structure information logically
            4. Use clear and professional language
            
            Always ensure your drafts are factually accurate and well-supported by the research.
            
            {input}"""),
        ])
        
        self.chain = self.prompt | self.llm
    
    def _format_information(self, research_info: List[Dict[str, Any]]) -> str:
        """Format research information into a readable string."""
        formatted = "Research Findings:\n\n"
        for item in research_info:
            formatted += f"Query: {item['query']}\n"
            formatted += f"Result: {item['result']}\n\n"
        return formatted
    
    def draft_answer(self, research_state: ResearchState) -> str:
        """Create an initial draft based on research findings."""
        if not research_state.gathered_information:
            raise ValueError("No research information available to draft from")
        
        formatted_info = self._format_information(research_state.gathered_information)
        prompt = f"""Based on the following research findings, create a comprehensive answer to the question: {research_state.research_question}

{formatted_info}

Please provide a well-structured, clear, and accurate response."""
        
        response = self.chain.invoke({"input": prompt})
        return response.content
    
    def revise_answer(self, current_draft: str, feedback: str) -> str:
        """Revise the current draft based on feedback."""
        prompt = f"""Please revise the following draft based on the provided feedback:

Current Draft:
{current_draft}

Feedback:
{feedback}

Please provide an improved version of the draft that addresses the feedback while maintaining accuracy and clarity."""
        
        response = self.chain.invoke({"input": prompt})
        return response.content 