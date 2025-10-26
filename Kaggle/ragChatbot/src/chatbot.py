from typing import List, Dict, Any, Optional, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import config
class RAGChatbot:
    def __init__(self, retriever, llm_chain):
        self.retriever=retriever
        self.llm_chain=llm_chain
        self.conversation_history=[]
    def ask(self, question:str, top_k:int=None, temperature:float=None,filter_dict: Optional[Dict[str, Any]] = None
    ) -> str:
        print(f"\n{'='*60}")
        print(f"Question:{question}")
        print(f"{'='*60}\n")
        
        context=self.retriever.retrieve(
            query=question,
            top_k=top_k,
            filter_dict=filter_dict
        )
        answer=self.llm_chain.generate_answer(
            query=question,  # FIXED: was 'question=' (wrong parameter name)
            context=context,
            temperature=temperature
        )
        print(f"\n{'='*60}")
        print(f"Answer: {answer}")
        print(f"{'='*60}\n")
        return answer
    def ask_with_sources(self, question:str,top_k:int=None,temperature:float=None)->Tuple[str,List[str]]:
        print(f"\n{'='*60}")
        print(f"Question: {question}")
        print(f"{'='*60}\n") 
        context = self.retriever.retrieve(query=question, top_k=top_k)
        sources=self.retriever.get_relevant_sources(query=question, top_k=top_k)
        answer=self.llm_chain.generate_with_sources(
            query=question,
            context=context,
            sources=sources,
            temperature=temperature
        )
        print(f"\n{'='*60}")
        print(f"Answer:\n{answer}")
        print(f"{'='*60}\n")
        return answer,sources
    def chat(self, question: str, top_k: int = None, temperature: float = None) -> str:  # FIXED: added return type
        print(f"\n{'='*60}")
        print(f"You: {question}")
        print(f"{'='*60}\n")
        context = self.retriever.retrieve(query=question, top_k=top_k)
        answer, updated_history=self.llm_chain.chat(
            query=question,
            context=context,
            conversation_history=self.conversation_history,
            temperature=temperature
        )
        self.conversation_history=updated_history

        # FIXED: Added print for bot's answer
        print(f"\n{'='*60}")
        print(f"Bot: {answer}")
        print(f"{'='*60}\n")

        return answer
    def reset_conversation(self):
        self.conversation_history=[]
        print("✓ Conversation history reset")  # FIXED: typo and added checkmark
    def search_category(self,question:str, category:str, top_k:int=None):
        print(f"\n{'='*60}")
        print(f"Question (searching only in '{category}'): {question}")
        print(f"{'='*60}\n")
        context=self.retriever.search_by_category(
            query=question,
            category=category,
            top_k=top_k
        )
        answer=self.llm_chain.generate_answer(
            query=question,
            context=context
        )
        return answer
    def search_doc_type(self,question:str, doc_type:str, top_k:int=None):
        print(f"\n{'='*60}")
        print(f"Question (searching only in '{doc_type}' docs): {question}")
        print(f"{'='*60}\n")
        context=self.retriever.search_by_doc_type(
            query=question,
            doc_type=doc_type,
            top_k=top_k
        )
        answer=self.llm_chain.generate_answer(
            query=question,
            context=context
        )
        print(f"\n{'='*60}")
        print(f"Answer: {answer}")
        print(f"{'='*60}\n")
        return answer
    def get_conversation_history(self):
        return self.conversation_history
    def interactive_mode(self):
        """Start interactive chat mode in terminal"""
        print("\n" + "="*60)
        print("RAG Chatbot - Interactive Mode")
        print("="*60)
        print("Commands:")
        print("  - Type your question to get an answer")
        print("  - Type 'reset' to clear conversation history")
        print("  - Type 'quit' or 'exit' to stop")
        print("="*60 + "\n")
        while True:
            try:
                user_input=input("You : ").strip()
                if not user_input:
                    continue
                if user_input.lower() in ['quit','exit','q']:
                    break
                if user_input.lower()=='reset':
                    self.reset_conversation()
                    continue
                answer=self.chat(user_input)
            except KeyboardInterrupt:
                print("\n\nGoodbye! 👋\n")  # FIXED: typo =K -> 👋
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")  # FIXED: typo L -> ❌
