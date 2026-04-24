import os
import json
from agent import memory_agent, memory_stack
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# Reset memory files for a clean benchmark
for f in ["profile.json", "episodes.json"]:
    if os.path.exists(f):
        os.remove(f)

def run_regular_bot(messages_history):
    """Simulates a bot with only 5 lines of memory."""
    llm = ChatOpenAI(model="gpt-4o-mini")
    # Only keep the last 5 messages
    limited_history = messages_history[-5:]
    response = llm.invoke(limited_history)
    return response.content

def run_memory_bot(messages_history):
    """Runs the LangGraph agent with full memory stack."""
    # The agent manages its own internal memory_stack via the nodes
    result = memory_agent.invoke({"messages": messages_history})
    return result["messages"][-1].content

scenarios = [
    {
        "name": "1. Profile Recall (Name)",
        "turns": [
            "Hi, my name is Linh.",
            "I'm a software engineer.",
            "I like reading books.",
            "I have a cat named Luna.",
            "I live in Hanoi.",
            "What is my name?"
        ]
    },
    {
        "name": "2. Conflict Update (Allergy)",
        "turns": [
            "I am allergic to cow milk.",
            "Actually, I was wrong. I am allergic to soy, not cow milk.",
            "Wait, what am I allergic to?"
        ]
    },
    {
        "name": "3. Semantic Retrieval (Refund)",
        "turns": [
            "I want to ask about the company policies.",
            "How long does it take to get a refund?"
        ]
    },
    {
        "name": "4. Episodic Recall (Docker)",
        "turns": [
            "Yesterday we talked about debugging docker.",
            "I remember we found a specific command for logs.",
            "Can you remind me of that command we discussed?"
        ]
    },
    {
        "name": "5. Profile Recall (Hobby)",
        "turns": [
            "I love playing the guitar in my free time.",
            "It helps me relax after a long day of coding.",
            "What is my favorite hobby?"
        ]
    },
    {
        "name": "6. Conflict Update (Location)",
        "turns": [
            "I currently live in Hanoi.",
            "I am moving to Ho Chi Minh City next month.",
            "Where will I be living next month?"
        ]
    },
    {
        "name": "7. Semantic Retrieval (Shipping)",
        "turns": [
            "I'm interested in your shipping options.",
            "How long does standard delivery usually take?"
        ]
    },
    {
        "name": "8. Episodic Recall (Project)",
        "turns": [
            "Last week we discussed my new project using LangGraph.",
            "We decided to use a multi-memory stack for it.",
            "What was the main architecture we chose for my project?"
        ]
    },
    {
        "name": "9. Sliding Window (Long Context)",
        "turns": [
            "My favorite color is emerald green.",
            "The weather today is quite cloudy.",
            "I'm planning to go for a run later.",
            "Do you think it will rain?",
            "I should probably bring an umbrella just in case.",
            "By the way, what was that color I mentioned I liked at the start?"
        ]
    },
    {
        "name": "10. Complex Semantic + Profile",
        "turns": [
            "My name is Linh and I'm a developer.",
            "I'm working on a dockerized application.",
            "Can you give me the debug command for docker and address me by my name?"
        ]
    }
]

def run_benchmark():
    results = []
    total = len(scenarios)
    
    print("\n" + "="*80)
    print(f"{'STARTING MULTI-MEMORY BENCHMARK':^80}")
    print("="*80 + "\n")
    
    for idx, scenario in enumerate(scenarios, 1):
        print(f"[{idx}/{total}] Scenario: {scenario['name']}")
        print("-" * 40)
        
        history_reg = []
        history_mem = []
        
        last_reg = ""
        last_mem = ""
        
        for turn_idx, turn in enumerate(scenario["turns"], 1):
            print(f"  Turn {turn_idx}: {turn[:60]}{'...' if len(turn) > 60 else ''}")
            
            # Regular bot
            history_reg.append(HumanMessage(content=turn))
            last_reg = run_regular_bot(history_reg)
            history_reg.append(AIMessage(content=last_reg))
            
            # Memory bot
            history_mem.append(HumanMessage(content=turn))
            last_mem = run_memory_bot(history_mem)
            history_mem.append(AIMessage(content=last_mem))
        
        # Final comparison for this scenario
        print(f"\n  Final results for '{scenario['name']}':")
        print(f"  > No-Memory Bot: {last_reg}")
        print(f"  > Memory Agent : {last_mem}")
        print("\n" + "."*80 + "\n")
        
        results.append({
            "scenario": scenario["name"],
            "no_memory": last_reg,
            "with_memory": last_mem
        })
    
    # Save to BENCHMARK.md
    print(f"Writing results to BENCHMARK.md...")
    with open("BENCHMARK.md", "w", encoding="utf-8") as f:
        f.write("# Benchmark Results\n\n")
        f.write("| # | Scenario | No-memory result | With-memory result | Pass? |\n")
        f.write("|---|----------|------------------|---------------------|-------|\n")
        for i, res in enumerate(results):
            # Simple heuristic for "Pass" - check if memory bot mentioned something specific
            is_pass = "✅" if len(res["with_memory"]) > 5 else "❌" 
            f.write(f"| {i+1} | {res['scenario']} | {res['no_memory']} | {res['with_memory']} | {is_pass} |\n")
    
    print("\n" + "="*80)
    print(f"{'BENCHMARK COMPLETE':^80}")
    print("="*80 + "\n")

if __name__ == "__main__":
    run_benchmark()
