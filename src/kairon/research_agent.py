from typing import List, Dict, Any
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.tools import Tool
from langchain_core.messages import HumanMessage, AIMessage
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from tavily import TavilyClient
import os
from dotenv import load_dotenv
from .config import GOOGLE_API_KEY

load_dotenv()

class ResearchState(BaseModel):
    """State for the research process."""
    research_question: str
    gathered_information: List[Dict[str, Any]] = Field(default_factory=list)
    current_focus: str = ""
    iteration_count: int = 0

class ResearchAgent:
    def __init__(self):
        """Initialize the research agent."""
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3,
            convert_system_message_to_human=True
        )
        
        # Initialize Tavily client
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        
        # Create a custom search function
        def tavily_search(query: str) -> str:
            try:
                response = self.tavily_client.search(query)
                return str(response)
            except Exception as e:
                return f"Error in Tavily search: {str(e)}"
        
        self.tools = [
            Tool(
                name="web_search",
                func=tavily_search,
                description="Search the web for relevant information"
            )
        ]
        
        # Combine system and human messages into a single human message
        self.prompt = ChatPromptTemplate.from_messages([
            ("human", """You are a research agent specialized in gathering and analyzing information from the web.
            Your task is to:
            1. Break down complex research questions into smaller, searchable queries
            2. Gather relevant information from web searches
            3. Organize and summarize the findings
            4. Identify gaps in information that need further research
            
            Always maintain focus on the original research question while gathering information.
            
            Current research question: {input}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])
        
        self.agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.tools,
            prompt=self.prompt
        )
        
        self.agent_executor = AgentExecutor(
            agent=self.agent,
            tools=self.tools,
            verbose=True
        )
    
    def research(self, question: str, max_iterations: int = 3) -> ResearchState:
        """Conduct research on a given question."""
        state = ResearchState(research_question=question)
        
        while state.iteration_count < max_iterations:
            # Prepare the research query
            query = f"{state.research_question} {state.current_focus}"
            
            # Execute the research
            result = self.agent_executor.invoke({
                "input": query,
                "chat_history": []
            })
            
            # Update state
            state.gathered_information.append({
                "query": query,
                "result": result["output"]
            })
            
            # Update focus for next iteration
            state.current_focus = self._determine_next_focus(result["output"])
            state.iteration_count += 1
            
            # Check if we have sufficient information
            if self._has_sufficient_information(state):
                break
        
        return state
    
    def _determine_next_focus(self, current_result: str) -> str:
        """Determine what aspect to focus on next based on current results."""
        # This is a simplified version - in practice, you'd want to analyze the results
        # to identify gaps in information
        return ""
    
    def _has_sufficient_information(self, state: ResearchState) -> bool:
        """Determine if we have gathered sufficient information."""
        # This is a simplified version - in practice, you'd want to analyze
        # the quality and completeness of the gathered information
        return len(state.gathered_information) >= 2 