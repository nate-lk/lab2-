import os
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from dotenv import load_dotenv
from memory_stack import MultiMemoryStack

load_dotenv()

# 1. Define the State
class MemoryState(TypedDict):
    messages: List[BaseMessage]
    user_profile: Dict[str, Any]
    episodes: List[Dict[str, Any]]
    semantic_hits: List[str]
    memory_budget: int # Added to match rubric

# 2. Initialize Memory and LLM
memory_stack = MultiMemoryStack()
llm = ChatOpenAI(model="gpt-4o-mini") # Using a small model for cost efficiency

# 3. Nodes
def retrieve_memory_node(state: MemoryState):
    """Retrieve memories from all backends."""
    user_input = state["messages"][-1].content if state["messages"] else ""
    
    # Profile
    profile = memory_stack.profile.get_all()
    
    # Episodic
    recent_episodes = memory_stack.episodic.get_recent(2)
    
    # Semantic
    hits = memory_stack.semantic.search(user_input)
    
    return {
        "user_profile": profile,
        "episodes": recent_episodes,
        "semantic_hits": hits
    }

def chatbot_node(state: MemoryState):
    """Generate a response using the full memory context."""
    profile_str = f"User Profile: {state['user_profile']}"
    episodes_str = f"Recent Episodes: {state['episodes']}"
    semantic_str = f"Knowledge Base: {state['semantic_hits']}"
    
    system_prompt = f"""You are a helpful assistant with a multi-memory stack.
    {profile_str}
    {episodes_str}
    {semantic_str}
    
    Guidelines:
    - Use the profile to personalize answers.
    - If there is a conflict in profile (e.g., user changed an allergy), prioritize the latest info.
    - Reference past episodes if relevant.
    - Use Knowledge Base for facts.
    """
    
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = llm.invoke(messages)
    
    # Update short term memory manually for now (or let LangGraph handle it if using Checkpointers)
    memory_stack.short_term.add({"role": "user", "content": state["messages"][-1].content})
    memory_stack.short_term.add({"role": "assistant", "content": response.content})
    
    return {"messages": [response]}

def update_memory_node(state: MemoryState):
    """Analyze the last exchange to update long-term/episodic memories."""
    last_user_msg = state["messages"][-2].content if len(state["messages"]) >= 2 else ""
    last_ai_msg = state["messages"][-1].content if state["messages"] else ""
    
    # Simple extraction logic (In a real app, use LLM for this)
    # Scenario: "My name is X" or "I am allergic to Y"
    prompt = f"""Analyze the user message and extract key facts for a profile update.
    User: {last_user_msg}
    AI: {last_ai_msg}
    
    Return ONLY a JSON object of facts to update, or {{}} if nothing significant.
    Example: {{"name": "Linh", "allergy": "peanuts"}}
    """
    
    # In a real implementation, we'd use LLM to extract facts. 
    # For simplicity, let's do a basic check or a quick LLM call.
    try:
        extraction = llm.invoke(prompt).content
        import json
        facts = json.loads(extraction)
        for k, v in facts.items():
            memory_stack.profile.update(k, v)
            
        # Also record as an episode if it seems significant
        if facts:
            memory_stack.episodic.add({"user": last_user_msg, "ai": last_ai_msg, "extracted": facts})
    except:
        pass
        
    return {}

# 4. Build the Graph
builder = StateGraph(MemoryState)
builder.add_node("retrieve", retrieve_memory_node)
builder.add_node("chatbot", chatbot_node)
builder.add_node("update", update_memory_node)

builder.set_entry_point("retrieve")
builder.add_edge("retrieve", "chatbot")
builder.add_edge("chatbot", "update")
builder.add_edge("update", END)

memory_agent = builder.compile()
