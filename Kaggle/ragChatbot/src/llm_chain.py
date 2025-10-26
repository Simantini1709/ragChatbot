"""
LLM Chain for RAG Chatbot
Handles interaction with Anthropic Claude API to generate answers
"""

from typing import List, Dict, Any, Optional
from anthropic import Anthropic
import sys
import os

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config


class LLMChain:
    """Manages LLM interactions for generating answers from retrieved context"""

    def __init__(self, api_key: str = None, model: str = None):
        """
        Initialize the LLM chain with Anthropic Claude

        Args:
            api_key: Anthropic API key (default from config)
            model: Claude model name (default from config)
        """
        # Validate API key
        self.api_key = api_key or config.ANTHROPIC_API_KEY
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")

        self.model = model or config.LLM_MODEL
        self.client = Anthropic(api_key=self.api_key)

        print(f"LLMChain initialized with model: {self.model}")

    def generate_answer(
        self,
        query: str,
        context: str,
        temperature: float = None,
        max_tokens: int = 1024
    ) -> str:
        """
        Generate an answer based on query and context

        Args:
            query: User's question
            context: Retrieved context from documents
            temperature: Creativity (0.0-1.0, default from config)
            max_tokens: Maximum response length

        Returns:
            Generated answer as string
        """
        temperature = temperature or config.TEMPERATURE
        prompt = self._build_prompt(query, context)

        print(f"Generating answer with {self.model}...")

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract answer from response (FIXED: was missing!)
            answer = response.content[0].text

            print(f"✓ Generated answer ({len(answer)} characters)")
            return answer

        except Exception as e:
            print(f"Error generating answer: {e}")
            raise

    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build RAG prompt with system instructions and context

        Args:
            query: User's question
            context: Retrieved context

        Returns:
            Formatted prompt string
        """
        prompt = f"""You are a helpful assistant for Protobi, a data visualization and survey analysis platform.

Your task is to answer the user's question based ONLY on the context provided below from Protobi's documentation.

IMPORTANT INSTRUCTIONS:
1. Answer based ONLY on the information in the context - review ALL context chunks carefully
2. For questions asking "all" or "list all", provide a COMPLETE and COMPREHENSIVE answer using ALL relevant information from the context
3. When listing items (questions, features, etc.), include EVERY item mentioned in the context, not just a subset
4. If the answer is not in the context, say "I don't have enough information to answer this."
5. Be specific and provide step-by-step instructions when appropriate
6. If you reference specific features or functions, mention which document they come from
7. Do not make up or assume information not present in the context
8. For survey/questionnaire queries, extract and list ALL questions in their complete form with IDs/codes

Context from Protobi Documentation:
{context}

User Question: {query}

Answer (be thorough and comprehensive):"""

        return prompt  # FIXED: was missing return statement!

    def generate_with_sources(
        self,
        query: str,
        context: str,
        sources: List[str],
        temperature: float = None
    ) -> str:
        """
        Generate answer with source citations

        Args:
            query: User's question
            context: Retrieved context
            sources: List of source file paths
            temperature: Creativity level

        Returns:
            Answer with citations
        """
        # Generate base answer
        answer=self.generate_answer(query, context, temperature)
        if sources:
            sources_text="\n\nSources:\n"
            for i, source in enumerate(sources, 1):
                source_display = source.split('/')[-1] if '/' in source else source
                sources_text += f"[{i}] {source_display}\n"
            answer+=sources_text
        return answer

    def chat(
        self,
        query: str,
        context: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = None
    ) -> tuple[str, List[Dict[str, str]]]:
        """
        Generate answer with conversation history support

        Args:
            query: User's question
            context: Retrieved context
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            temperature: Creativity level

        Returns:
            Tuple of (answer, updated_conversation_history)
        """
        temperature=temperature or config.TEMPERATURE
        conversation_history=conversation_history or []
        user_message=f"""Context from documentation:{context}
        Question: {query}"""
        if not conversation_history:
            system_context="""You are a helpful assistant for Protobi documentation.
Answer based on the provided context and conversation history.
If you don't know the answer, say so clearly."""
            conversation_history=[]
        messages=conversation_history + [
            {
                "role" : "user",
                "content" : user_message
            }
        ]
        try:
            response=self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=temperature,
                messages=messages
            )
            answer=response.content[0].text
            updated_history = messages + [
                {"role": "assistant", "content": answer}
            ]
            return answer, updated_history
        except Exception as e:
            print(f"Error in chat: {e}")  # FIXED: added f-string prefix
            raise



    def summarize_context(self, context: str, max_tokens: int = 500) -> str:
        """
        Summarize long context (useful for very large contexts)

        Args:
            context: Text to summarize
            max_tokens: Maximum summary length

        Returns:
            Summarized context
        """
        prompt = f"""Summarize the following documentation context concisely, keeping the most important information:

{context}

Summary:"""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=0.3,  # Lower temperature for factual summary
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            return response.content[0].text

        except Exception as e:
            print(f"Error summarizing context: {e}")
            raise

        
