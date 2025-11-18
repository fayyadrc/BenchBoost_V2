import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import create_agent as create_langchain_agent
from langchain_core.messages import AIMessage, HumanMessage

from .tools import all_tools
from .prompt import SYSTEM_PROMPT
from .memory import save_chat_history

def create_agent():
    "Initialize and returns the runnable LangChain agent."

    print("Initializing agent...")
    llm = ChatGoogleGenerativeAI(
        model = "gemini-1.5-flash",
        temperature = 0,
        convert_system_message_to_human=True # Helps with some models
    )

    #create agent
    agent_executor = create_langchain_agent(llm, tools=all_tools, system_prompt=SYSTEM_PROMPT)

    print("Agent initialized successfully")

    return agent_executor

def run_chat_loop(agent_executor, chat_history):
    """
    Runs the main interactive chat loop.
    """
    print("\n--- BenchBoost FPL Chatbot ---")
    print("Ask me anything about FPL! (Type 'exit' to quit or 'clear' to reset memory)")

    while True:
        try:
            query = input("\nYou: ")
            
            if query.lower() in ["exit", "quit"]:
                print("Goodbye! Good luck in your gameweek.")
                break
            
            if query.lower() == "clear":
                chat_history.clear()
                save_chat_history(chat_history)
                print("✨ Memory cleared! Starting fresh.")
                continue

            #invoke the agent
            result = agent_executor.invoke({
                "input": query,
                "chat_history": chat_history
            })

            response = result.get("output", "I'm sorry, I ran into an error.")

            #update chat history
            chat_history.append(HumanMessage(content=query))
            chat_history.append(AIMessage(content=response))
            
            # Auto-save after each exchange
            save_chat_history(chat_history)

            print(f"\nBenchBoost: {response}")

        except KeyboardInterrupt:
            print("\n\nInterrupted. Saving conversation...")
            save_chat_history(chat_history)
            print("Goodbye!")
            break
        except Exception as e:
            import traceback
            print(f"\nAn error occurred: {e}\n")
            print(traceback.format_exc())
            print("Let's try that again.")

