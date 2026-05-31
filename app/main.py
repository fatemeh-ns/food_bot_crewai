import os
from dotenv import load_dotenv
from crewai import Crew, Task
from app.agent import food_agent

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
load_dotenv()

chat_history = []


def chat():
    print("Food Agent is running... (type 'exit' to quit)")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() == "exit":
            break

        chat_history.append(f"User: {user_input}")
        history_str = "\n".join(chat_history[-10:])

        task = Task(
            description=f"""
Conversation history:
{history_str}

The user's latest message is: "{user_input}"

Instructions:
- Use recommend_food tool to find food based on user preferences
- Use reserve_food tool if the user wants to place an order
- Respond in the same language the user is using (Persian or English)
- Be helpful and suggest specific food items from the database
            """,
            expected_output="A helpful response to the user with food recommendations or order confirmation",
            agent=food_agent
        )

        crew = Crew(agents=[food_agent], tasks=[task], verbose=False)
        result = crew.kickoff()

        answer = str(result)
        print("Agent:", answer)
        chat_history.append(f"Assistant: {answer}")


if __name__ == "__main__":
    chat()
