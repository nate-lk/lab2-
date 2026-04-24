import sys
from agent import memory_agent
from langchain_core.messages import HumanMessage, AIMessage

def chat():
    print("Multi-Memory Chatbot (type 'exit' or 'quit' to stop)")
    print("-" * 30)
    
    messages = []
    
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["exit", "quit"]:
            break
            
        messages.append(HumanMessage(content=user_input))
        
        # Invoke the agent
        # The agent nodes will handle memory retrieval, chat, and memory updates
        response = memory_agent.invoke({"messages": messages})
        
        # Get the last message from the agent
        ai_message = response["messages"][-1]
        print(f"Assistant: {ai_message.content}")
        
        # Keep track of history for the next turn
        messages.append(ai_message)

if __name__ == "__main__":
    chat()
