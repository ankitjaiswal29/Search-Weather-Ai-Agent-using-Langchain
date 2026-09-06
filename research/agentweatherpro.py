
import os
import certifi
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain import hub
from langchain.tools import tool
from langchain.agents import create_react_agent, AgentExecutor
import requests
import streamlit as st  # pyright: ignore[reportMissingImports]


# =========================================================
# SSL
# =========================================================

os.environ["SSL_CERT_FILE"] = certifi.where()

load_dotenv()


# =========================================================
# API KEYS
# =========================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
WEATHERSTACK_API_KEY = os.getenv("WEATHERSTACK_API_KEY")


# =========================================================
# STREAMLIT UI
# =========================================================

st.title("🤖 GenAI Agent")

st.write("Ask about latest news, weather, or any web-related question.")


# =========================================================
# WEATHER TOOL
# =========================================================

@tool
def get_weather(city: str) -> str:
    """Fetches the current weather for a given city using the Weatherstack API."""

    url = "https://api.weatherstack.com/current"

    params = {
        "access_key": WEATHERSTACK_API_KEY,
        "query": city
    }

    response = requests.get(url, params=params)

    print("Status:", response.status_code)
    print("Response:", response.text)

    data = response.json()

    if "current" not in data:
        return f"Weather information is not available. API response: {data}"

    return (
        f"The current temperature in {city} is "
        f"{data['current']['temperature']}°C with "
        f"{data['current']['weather_descriptions'][0]}."
    )


# =========================================================
# TOOLS
# =========================================================

search_tool = TavilySearchResults(
    max_results=20
)

tools = [
    search_tool,
    get_weather
]


# =========================================================
# LLM
# =========================================================

llm = ChatOpenAI(
    model_name="gpt-3.5-turbo",
    temperature=0.5,
    api_key=OPENAI_API_KEY
)


# =========================================================
# PROMPT
# =========================================================

prompt = hub.pull("hwchase17/react")


# =========================================================
# CREATE AGENT
# =========================================================

agent = create_react_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)


# =========================================================
# EXECUTOR
# =========================================================

agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)


# =========================================================
# USER INPUT
# =========================================================

user_input = st.text_input(
    "Enter your question:",
    placeholder="Example: latest news of Ghaziabad and current weather"
)


# =========================================================
# BUTTON
# =========================================================

if st.button("Ask Agent"):

    if user_input:

        with st.spinner("Agent is working..."):

            try:

                response = agent_executor.invoke(
                    {
                        "input": user_input
                    }
                )

                result = response["output"]

                st.subheader("Agent Response")

                st.write(result)

            except Exception as e:

                st.error(f"Error: {str(e)}")

    else:

        st.warning("Please enter a question.")

