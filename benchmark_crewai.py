import os
import time
import warnings
from dotenv import load_dotenv
from crewai import Agent, Crew, Task, LLM
from app.tools.recommend_tool import recommend_food
from app.tools.reserve_tool import reserve_food

os.environ["CREWAI_DISABLE_TELEMETRY"] = "true"
warnings.filterwarnings("ignore")
load_dotenv()

llm = LLM(
    model="openai/gpt-4o-mini",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    temperature=0
)


# ─────
agent_with_tools = Agent(
    role="Food Ordering Assistant",
    goal="Help users find and order food based on their preferences and budget. Always use the recommend_food tool to find food and reserve_food tool to place orders.",
    backstory="You are a helpful food ordering assistant. You use tools to find food from the database and place orders.",
    tools=[recommend_food, reserve_food],
    llm=llm,
    verbose=False
)

agent_no_tools = Agent(
    role="Food Ordering Assistant",
    goal="Help users find and order food based on their preferences and budget.",
    backstory="You are a helpful food ordering assistant.",
    tools=[],
    llm=llm,
    verbose=False
)

# ──────
TEST_INPUT = "غذای گیاهی میخوام، بودجه‌ام ۲۵۰ هزار تومنه"

NUM_RUNS = 5


def run_benchmark(agent, label: str):
    print(f"\n{'='*55}")
    print(f"  {label}")
    print(f"{'='*55}")

    latencies = []

    for i in range(NUM_RUNS):
        task = Task(
            description=f"""The user says: "{TEST_INPUT}" Use recommend_food tool to find matching food items and respond helpfully.""",
            expected_output="A helpful response with food recommendations",
            agent=agent
        )
        crew = Crew(agents=[agent], tasks=[task], verbose=False)

        start = time.time()
        result = crew.kickoff()
        elapsed = round(time.time() - start, 2)
        latencies.append(elapsed)

        answer = str(result)[:80].replace("\n", " ")
        print(f"  Run {i+1}: {elapsed}s  →  {answer}...")

    avg = round(sum(latencies) / len(latencies), 2)
    mn = round(min(latencies), 2)
    mx = round(max(latencies), 2)

    print(f"\nمیانگین : {avg}s")
    print(f"کمترین  : {mn}s")
    print(f"بیشترین : {mx}s")

    return {"label": label, "avg": avg, "min": mn, "max": mx}


if __name__ == "__main__":
    print("\nشروع بنچمارک CrewAI Food Agent")
    print(f"   تسک: {TEST_INPUT}")
    print(f"   تعداد اجرا: {NUM_RUNS}")

    r1 = run_benchmark(agent_with_tools, "با Tool Calling")
    r2 = run_benchmark(agent_no_tools,   "بدون Tool Calling")

    print(f"\n{'='*55}")
    print("نتیجه نهایی مقایسه")
    print(f"{'='*55}")
    print(f"  با Tool    → میانگین: {r1['avg']}s")
    print(f"  بدون Tool  → میانگین: {r2['avg']}s")
    diff = round(r1['avg'] - r2['avg'], 2)
    if diff > 0:
        print(f"\nTool calling  {diff}s کندتر بود (به خاطر اجرای tool)")
    else:
        print(f"\nبدون tool  {abs(diff)}s کندتر بود")
