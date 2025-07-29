# name-chatbot
An intelligent chatbot that provides investment insights by summarizing company news ,fetching historical stock data and offering actionable advice using LLM agents.

# Investor Assistant Bot

## Project Overview

The **Investor Assistant Bot** is a Python script (`chatbot.py`) that uses the Alpha Vantage API to fetch stock ticker symbols and prices, the NewsAPI to retrieve recent news articles, and LangChain with OpenAI's GPT-3.5-turbo to summarize financial data and provide investment advice (Buy/Hold/Sell). The script integrates four tools:
1. **Fetch News**: Retrieves recent news articles for a company.
2. **Fetch Stock Prices**: Fetches real-time stock price data using a dynamically resolved ticker.
3. **Summarize News**: Generates three financial takeaways from news and stock data.
4. **Give Advice**: Provides investment advice based on the summary.

The script uses LangChain's agent framework to chain these tools and deliver a cohesive analysis for a user-specified company. It includes debugging output to diagnose issues, such as the `'Response' object has no attribute 'get'` error, and respects API rate limits.

This project is ideal for developers building financial analysis tools or learning to integrate APIs with AI-driven summarization.

## Prerequisites

Before setting up the project, ensure you have the following:

- **Python 3.8 or higher**: Check with `python --version` or `python3 --version`.
- **pip**: Python’s package manager, included with Python.
- **API Keys**:
  - **Alpha Vantage API Key**: Obtain a free key from [Alpha Vantage](https://www.alphavantage.co/support/#api-key) (5 calls/minute limit for free tier).
  - **NewsAPI Key**: 
  - **OpenAI API Key**: 


## Installation Steps

Follow these steps to set up the project locally:

1. **Create the Project Directory**:
   - Create a directory for the project:
     ```bash
     mkdir investor-bot
     cd chatbot
     ```
   - Alternatively, if using Git, clone the repository (if hosted):
     ```bash
     git clone <repository-url>
     cd chatbot
     ```

2. **Set Up a Virtual Environment** (Recommended):
   - Create a virtual environment to isolate dependencies:
     ```bash
     python -m venv venv
     ```
   - Activate the virtual environment:
     - On Windows:
       ```bash
       venv\Scripts\activate
       ```
     - On macOS/Linux:
       ```bash
       source venv/bin/activate
       ```
     - Verify activation (you should see `(venv)` in your terminal prompt).

3. **Install Python Dependencies**:
   - Install required libraries:
     ```bash
     pip install requests newsapi-python langchain langchain-openai
     ```
   - Verify installation:
     ```bash
     pip show requests newsapi-python langchain langchain-openai
     ```
     You should see details for each package.

4. **Save the Script**:
   - Create a file named `chatbot.py` in the project directory.
   - Configure API Keys:
	Set environment variables for security (recommended):
	On Windows (Command Prompt):
	-set OPENAI_API_KEY=your_openai_api_key
	-set ALPHA_VANTAGE_API_KEY=your_alpha_vantage_api_key
	
**Run the Script**

	Execute the script:
	- python chatbot.py
	When prompted, enter a company name (e.g., Tesla).
	The script will:
	-Fetch news and stock prices.
	-Summarize data into three financial takeaways.
	-Provide investment advice (Buy/Hold/Sell) with a two-line justification.
