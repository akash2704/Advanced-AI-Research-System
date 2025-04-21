from typing import List, Dict, Any
from langchain.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel, Field
from .config import GOOGLE_API_KEY

class QualityCheck(BaseModel):
    """Results of quality checks."""
    fact_accuracy: float = 0.0
    consistency_score: float = 0.0
    bias_detected: bool = False
    readability_score: float = 0.0
    issues: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)

class QualityAgent:
    def __init__(self):
        """Initialize the quality control agent."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        self.fact_check_prompt = ChatPromptTemplate.from_messages([
            ("human", """Analyze the following content for factual accuracy and consistency:

Content: {content}

Research Sources: {sources}

Please identify any factual inaccuracies or inconsistencies and provide a confidence score (0-1) for the overall accuracy."""),
        ])
        
        self.bias_check_prompt = ChatPromptTemplate.from_messages([
            ("human", """Analyze the following content for potential biases:

Content: {content}

Please identify any potential biases in language, perspective, or source selection."""),
        ])
        
        self.readability_prompt = ChatPromptTemplate.from_messages([
            ("human", """Evaluate the readability of the following content:

Content: {content}

Please provide a readability score (0-1) and suggestions for improvement."""),
        ])
    
    def check_content(self, content: str, sources: List[Dict[str, Any]]) -> QualityCheck:
        """Perform comprehensive quality checks on the content."""
        check = QualityCheck()
        
        # Check factual accuracy
        fact_check = self.llm.invoke(
            self.fact_check_prompt.format_messages(
                content=content,
                sources=str(sources)
            )
        )
        check.fact_accuracy = self._extract_score(fact_check.content)
        
        # Check for biases
        bias_check = self.llm.invoke(
            self.bias_check_prompt.format_messages(content=content)
        )
        check.bias_detected = "bias detected" in bias_check.content.lower()
        
        # Check readability
        readability_check = self.llm.invoke(
            self.readability_prompt.format_messages(content=content)
        )
        check.readability_score = self._extract_score(readability_check.content)
        
        # Extract issues and suggestions
        check.issues.extend(self._extract_issues(fact_check.content))
        check.suggestions.extend(self._extract_suggestions(readability_check.content))
        
        return check
    
    def _extract_score(self, text: str) -> float:
        """Extract a numerical score from the LLM response."""
        try:
            # Look for a number between 0 and 1 in the text
            import re
            match = re.search(r'(\d+\.?\d*)', text)
            if match:
                score = float(match.group(1))
                return min(max(score, 0.0), 1.0)
        except:
            pass
        return 0.5  # Default score if extraction fails
    
    def _extract_issues(self, text: str) -> List[str]:
        """Extract issues from the LLM response."""
        issues = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['issue', 'problem', 'inaccuracy', 'inconsistent']):
                issues.append(line.strip())
        return issues
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract suggestions from the LLM response."""
        suggestions = []
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in ['suggest', 'recommend', 'improve', 'consider']):
                suggestions.append(line.strip())
        return suggestions 