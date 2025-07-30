from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.agents import initialize_agent, Tool, AgentType
from dotenv import load_dotenv
import os
from api_utils import fetch_news, fetch_stock_prices

# Load environment variables
load_dotenv()

def summarize_news(news_text: str, stock_data: str, llm) -> str:
    """Summarizes news and intraday stock data into 3 financial takeaways."""
    print(f"Debug: Summarizing news and stock data")
    print(f"Debug: News input: {news_text}")
    print(f"Debug: Stock data input: {stock_data}")
    if not news_text or not isinstance(news_text, str):
        print("Debug: Invalid news text")
        return "Error: News text must be a non-empty string."
    if "Error" in news_text or "No recent articles" in news_text:
        print(f"Debug: News error: {news_text}")
        return f"Cannot summarize: {news_text}"
    if not stock_data or not isinstance(stock_data, str):
        print("Debug: Invalid stock data")
        return "Error: Stock data must be a non-empty string."
    if "Error" in stock_data:
        print(f"Debug: Stock data error: {stock_data}")
        return f"Cannot summarize: {stock_data}"
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an investment analyst. Summarize into exactly 3 financial takeaways as bullet points."),
            ("human", "News:\n{news_text}\n\nStock Data:\n{stock_data}")
        ])
        chain = prompt | llm
        response = chain.invoke({"news_text": news_text, "stock_data": stock_data})
        summary = response.content.strip()
        print(f"Debug: Summary response: {summary}")
        
        bullet_points = [line for line in summary.split('\n') if line.strip().startswith('-')]
        if len(bullet_points) != 3:
            print(f"Debug: Invalid summary format, found {len(bullet_points)} bullet points")
            return "Error: Summary must contain exactly 3 bullet points."
        return summary
    except Exception as e:
        print(f"Debug: Error summarizing: {str(e)}")
        return f"Error summarizing: {str(e)}"

def give_advice(summary: str, llm) -> str:
    """Provides investment advice (Buy/Hold/Sell) based on summarized news and stock data."""
    print(f"Debug: Generating advice from summary: {summary}")
    if not summary or not isinstance(summary, str):
        print("Debug: Invalid summary")
        return "Error: Summary must be a non-empty string."
    if "Error" in summary:
        print(f"Debug: Summary error: {summary}")
        return f"Cannot provide advice: {summary}"
    
    try:
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an investment analyst."),
            ("human", "Based on this summary, should the investor Buy, Hold, or Sell? Provide a 2-line reason justifying your decision\nSummary: {summary}")
        ])
        chain = prompt | llm
        response = chain.invoke({"summary": summary})
        advice = response.content.strip()
        print(f"Debug: Advice response: {advice}")
        
        if not any(keyword in advice.lower() for keyword in ["buy", "hold", "sell"]):
            print("Debug: Advice missing Buy/Hold/Sell")
            return "Error: Advice must include Buy, Hold, or Sell."
        return advice
    except Exception as e:
        print(f"Debug: Error providing advice: {str(e)}")
        return f"Error providing advice: {str(e)}"

def create_tools(llm):
    """Creates LangChain tools for the agent."""
    return [
        Tool.from_function(
            name="fetch_news",
            func=fetch_news,
            description="Fetch recent financial news for a company. Input: company name (e.g., 'Tesla')."
        ),
        Tool.from_function(
            name="fetch_stock_prices",
            func=fetch_stock_prices,
            description="Fetch intraday stock price data (5-min interval) for a company. Input: company name (e.g., 'Tesla')."
        ),
        Tool.from_function(
            name="summarize_news",
            func=lambda x: summarize_news(fetch_news(x), fetch_stock_prices(x), llm),
            description="Summarize news and intraday stock data into 3 financial insights. Input: company name."
        ),
        Tool.from_function(
            name="give_advice",
            func=lambda x: give_advice(summarize_news(fetch_news(x), fetch_stock_prices(x), llm), llm),
            description="Provide investment advice (Buy/Hold/Sell) based on news and intraday stock data."
        )
    ]

def initialize_stock_agent():
    """Initializes the LangChain agent with tools and LLM."""
    llm = ChatOpenAI(
        temperature=0,
        model="gpt-3.5-turbo",
        api_key=os.getenv("OPENAI_API_KEY")
    )
    tools = create_tools(llm)
    return initialize_agent(
        tools=tools,
        llm=llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True
    )
