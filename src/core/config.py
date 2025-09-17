import os
from typing import Optional
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings


class OllamaConfig(BaseModel):
    """Configuration for Ollama service."""
    ai_model_id: str = Field(default="llama3.1:latest", description="Ollama model ID to use")
    host: str = Field(default="http://localhost:11434", description="Ollama host URL")
    service_id: str = Field(default="ollama", description="Service identifier for Semantic Kernel")


class AgentConfig(BaseModel):
    """Configuration for individual agents."""
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    instructions: str = Field(..., description="Agent instructions/system prompt")
    max_tokens: int = Field(default=8000, description="Maximum tokens for responses")
    temperature: float = Field(default=0.7, description="Temperature for response generation")


class SalesAssistantConfig(AgentConfig):
    """Configuration for Sales Assistant Agent."""
    name: str = "SalesAssistant"
    description: str = "A sales assistant that handles CRM operations, customer interactions, and proposal generation"
    instructions: str = """You are a sales assistant AI with access to CRM systems, email/calendar tools, product catalogs, and document generation capabilities.

Your responsibilities include:
1. Pulling and analyzing CRM records to understand customer history and preferences
2. Suggesting next best actions based on customer data and sales pipeline
3. Generating customer-facing proposals and quotes
4. Scheduling meetings and managing calendar coordination
5. Accessing product catalogs to provide accurate pricing and specifications

Always be professional, helpful, and focus on providing value to both the sales team and customers."""


class PlannerConfig(AgentConfig):
    """Configuration for Planner Agent."""
    name: str = "TaskPlanner"
    description: str = "A planning agent that breaks down user queries into structured, actionable tasks"
    instructions: str = """You are a task planning AI that analyzes user queries and breaks them down into specific, actionable tasks.

Your responsibilities:
1. Understand the user's intent and requirements
2. Break down complex requests into smaller, manageable tasks
3. Identify the appropriate agent type for each task
4. Determine task dependencies and execution order
5. Estimate task durations and priorities

Always provide structured output with clear task definitions, required tools, and logical sequencing."""


class ApplicationConfig(BaseSettings):
    """Main application configuration."""

    # Ollama configuration (commented out for testing with Gemini)
    # ollama_ai_model_id: str = Field(default="llama3.1:latest", env="OLLAMA_AI_MODEL_ID")
    # ollama_host: str = Field(default="http://localhost:11434", env="OLLAMA_HOST")

    # Gemini configuration for testing (commented out)
    gemini_api_key: str = Field(default="AIzaSyAIdNAyi6Xmt--DIj3QXy50A4xxnTM_zE8", env="GEMINI_API_KEY")
    gemini_model_id: str = Field(default="gemini-2.5-pro", env="GEMINI_MODEL_ID")

    # OpenAI configuration
    openai_api_key: str = Field(default="", env="OPENAI_API_KEY")
    openai_model_id: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL_ID")

    # Agent configurations
    enable_debug_logging: bool = Field(default=False, env="DEBUG_LOGGING")
    max_concurrent_tasks: int = Field(default=3, env="MAX_CONCURRENT_TASKS")
    task_timeout_minutes: int = Field(default=10, env="TASK_TIMEOUT_MINUTES")

    # Chat interface
    chat_history_limit: int = Field(default=50, env="CHAT_HISTORY_LIMIT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    # def get_ollama_config(self) -> OllamaConfig:
    #     """Get Ollama configuration."""
    #     return OllamaConfig(
    #         ai_model_id=self.ollama_ai_model_id,
    #         host=self.ollama_host
    #     )

    def get_gemini_config(self) -> dict:
        """Get Gemini configuration."""
        return {
            "api_key": self.gemini_api_key,
            "ai_model_id": self.gemini_model_id
        }

    def get_openai_config(self) -> dict:
        """Get OpenAI configuration."""
        return {
            "api_key": self.openai_api_key,
            "ai_model_id": self.openai_model_id
        }

    def get_planner_config(self) -> PlannerConfig:
        """Get planner agent configuration."""
        return PlannerConfig()

    def get_sales_assistant_config(self) -> SalesAssistantConfig:
        """Get sales assistant agent configuration."""
        return SalesAssistantConfig()


# Global configuration instance
config = ApplicationConfig()