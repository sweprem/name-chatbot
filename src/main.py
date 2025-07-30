import os
from dotenv import load_dotenv
from agent import initialize_stock_agent

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("Please set the OPENAI_API_KEY environment variable.")
    if not os.getenv("ALPHA_VANTAGE_API_KEY"):
        raise ValueError("Please set the ALPHA_VANTAGE_API_KEY environment variable.")
    if not os.getenv("NEWSAPI_API_KEY"):
        raise ValueError("Please set the NEWSAPI_API_KEY environment variable.")
    
    agent = initialize_stock_agent()
    company = input("Enter a company name: ")
    result = agent.run(f"Analyze {company}, fetch its intraday stock data and news, and tell me if I should invest.")
    print("\n Final Advice:\n", result)
