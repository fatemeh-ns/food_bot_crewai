from app.tools.reserve_tool import reserve_food
from app.tools.recommend_tool import recommend_food
import os
from dotenv import load_dotenv
from crewai import Agent, LLM

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
load_dotenv()

llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)


food_agent = Agent(
    role="Food Ordering Assistant",
    goal="Help users find and order food based on their preferences and budget. Always use the recommend_food tool to find food and reserve_food tool to place orders.",
    backstory="You are a helpful food ordering assistant. You understand Persian and English. You use tools to find food from the database and place orders.",
    tools=[recommend_food, reserve_food],
    llm=llm,
    verbose=False
)
