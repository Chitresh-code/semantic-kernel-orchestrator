#!/usr/bin/env python3
"""
Simple test for OpenAI integration
"""
import asyncio
import sys
import os

# Add src to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion, OpenAIChatPromptExecutionSettings
from semantic_kernel.contents import ChatHistory

async def test_openai():
    """Simple test of OpenAI connectivity"""
    print("Testing OpenAI connectivity...")

    try:
        # Initialize OpenAI service
        chat_service = OpenAIChatCompletion(
            ai_model_id="gpt-4o-mini",  # Use the correct model name
            api_key="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"
        )

        # Simple test query
        chat_history = ChatHistory()
        chat_history.add_user_message("Say hello")

        # Create execution settings
        settings = OpenAIChatPromptExecutionSettings(
            max_tokens=100,
            temperature=0.7
        )

        # Get response
        response = await chat_service.get_chat_message_contents(
            chat_history=chat_history,
            settings=settings
        )

        if response and response[0].content:
            print(f"Success! Response: {response[0].content}")
            return True
        else:
            print("No response received")
            return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_openai())
    sys.exit(0 if success else 1)