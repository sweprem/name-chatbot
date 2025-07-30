import os
import time
import requests
import re
from newsapi import NewsApiClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search_ticker(company: str, retries: int = 2, delay: int = 12) -> str:
    """Searches for a company's stock ticker using Alpha Vantage's SYMBOL_SEARCH."""
    print(f"Debug: Starting ticker search for {company}")
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not company or not api_key:
        print("Debug: Validation failed - company or API key is empty")
        return "Error: Company name and API key cannot be empty."
    
    # Remove single or double quotes and convert to lowercase
    company = re.sub(r"['\"]", "", company).lower()
    print(f"Debug: Processed company name: {company}")
    
    for attempt in range(retries + 1):
        try:
            url = f"https://www.alphavantage.co/query?function=SYMBOL_SEARCH&keywords={company}&apikey={api_key}"
            print(f"Debug: API URL: {url.replace(api_key, 'HIDDEN_KEY')}")
            time.sleep(delay)  # Respect rate limit
            response = requests.get(url, timeout=10)
            print(f"Debug: Response status code: {response.status_code}")
            print(f"Debug: Response Content-Type: {response.headers.get('Content-Type', 'Unknown')}")

            content_type = response.headers.get("Content-Type", "")
            if "application/json" not in content_type:
                print(f"Debug: Non-JSON response: {response.text[:200]}")
                return f"Error: Non-JSON response received: {response.text[:200]}"

            data = response.json()
            print(f"Debug: Parsed JSON: {data}")
            if "Information" in data and "limit" in data["Information"].lower():
                print(f"Debug: Rate limit exceeded, retrying ({attempt + 1}/{retries})...")
                if attempt < retries:
                    continue
                return f"Error: Rate limit exceeded after {retries} retries."

            best_matches = data.get("bestMatches", [])
            print(f"Debug: Best matches: {best_matches}")

            if not best_matches:
                print(f"Debug: No matches found for {company}")
                return f"No matches found for {company}."

            print(f"Debug: Selected ticker: {best_matches[0]['1. symbol']}")
            return best_matches[0]["1. symbol"]
        except requests.exceptions.HTTPError as http_err:
            print(f"Debug: HTTP error: {str(http_err)}")
            print(f"Debug: Response text: {response.text[:200]}")
            return f"Error searching ticker for {company}: {str(http_err)}"
        except requests.exceptions.ConnectionError:
            print("Debug: Connection error occurred")
            if attempt < retries:
                print(f"Debug: Retrying ({attempt + 1}/{retries})...")
                continue
            return "Error: Failed to connect to Alpha Vantage API."
        except requests.exceptions.Timeout:
            print("Debug: Request timed out")
            if attempt < retries:
                print(f"Debug: Retrying ({attempt + 1}/{retries})...")
                continue
            return "Error: Request to Alpha Vantage API timed out."
        except ValueError as json_err:
            print(f"Debug: JSON parsing error: {str(json_err)}")
            print(f"Debug: Response text: {response.text[:200]}")
            return f"Error: Failed to parse JSON response: {str(json_err)}"
        except Exception as e:
            print(f"Debug: General error in search_ticker: {str(e)}")
            return f"Error searching ticker for {company}: {str(e)}"

def fetch_news(company: str) -> str:
    """Fetches recent news articles about a given company."""
    print(f"Debug: Fetching news for {company}")
    if not company or not isinstance(company, str) or len(company.strip()) < 1:
        print("Debug: Invalid company name")
        return "Error: Company name must be a non-empty string."
    try:
        api_key = os.getenv("NEWSAPI_API_KEY")
        if not api_key:
            print("Debug: Missing NewsAPI key")
            return "Error: NewsAPI key not set."
        newsapi = NewsApiClient(api_key=api_key)
        articles = newsapi.get_everything(q=company, language="en", sort_by="publishedAt", page_size=5)
        print(f"Debug: News API response: {articles.get('status')}")
        if not articles.get('articles'):
            print(f"Debug: No articles found for {company}")
            return f"No recent articles found for {company}."
        headlines = [f"{a['title']} ({a['source']['name']})" for a in articles['articles']]
        content = "\n".join(headlines)
        print(f"Debug: News headlines: {content}")
        return f"Recent news on {company}:\n{content}"
    except Exception as e:
        print(f"Debug: Error fetching news: {str(e)}")
        return f"Error fetching news for {company}: {str(e)}"

def fetch_stock_prices(company: str) -> str:
    """Fetches intraday stock price data (5-min interval) using Alpha Vantage's TIME_SERIES_INTRADAY."""
    print(f"Debug: Fetching stock prices for {company}")
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        print("Debug: Missing Alpha Vantage API key")
        return "Error: Alpha Vantage API key not set."
    
    ticker = search_ticker(company)
    print(f"Debug: Resolved ticker: {ticker}")
    if not ticker or "Error" in ticker:
        print(f"Debug: Ticker error: {ticker}")
        return f"No stock price data found for {company}: {ticker if ticker else 'No matching ticker found.'}"
    
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={ticker}&interval=5min&apikey={api_key}"
        print(f"Debug: Stock price URL: {url.replace(api_key, 'HIDDEN_KEY')}")
        time.sleep(12)  # Respect Alpha Vantage rate limit
        response = requests.get(url, timeout=10)
        print(f"Debug: Stock price response status: {response.status_code}")
        content_type = response.headers.get("Content-Type", "")
        print(f"Debug: Response Content-Type: {content_type}")
        
        if "application/json" not in content_type:
            print(f"Debug: Non-JSON response: {response.text[:200]}")
            return f"Error: Non-JSON response received: {response.text[:200]}"
        
        response.raise_for_status()
        data = response.json()
        print(f"Debug: Stock price JSON: {data}")
        
        if "Time Series (5min)" not in data or not data["Time Series (5min)"]:
            print(f"Debug: No intraday data for {ticker}")
            return f"No intraday data found for {company}."
        
        time_series = data["Time Series (5min)"]
        latest_timestamp = max(time_series.keys())
        latest_data = time_series[latest_timestamp]
        prev_timestamp = sorted(time_series.keys())[1] if len(time_series) > 1 else latest_timestamp
        prev_data = time_series[prev_timestamp]
        
        close_price = float(latest_data["4. close"])
        prev_close = float(prev_data["4. close"])
        change = close_price - prev_close
        change_percent = (change / prev_close) * 100 if prev_close != 0 else 0
        volume = latest_data["5. volume"]
        
        result = (f"Intraday stock data for {company} ({ticker}) at {latest_timestamp}:\n"
                  f"- Close Price: ${close_price:.2f}\n"
                  f"- Change: ${change:.2f} ({change_percent:.2f}%)\n"
                  f"- Volume: {volume}")
        print(f"Debug: Stock price result: {result}")
        return result
    except requests.exceptions.HTTPError as http_err:
        print(f"Debug: HTTP error: {str(http_err)}")
        print(f"Debug: Response text: {response.text[:200]}")
        return f"Error fetching intraday data for {company}: {str(http_err)}"
    except requests.exceptions.ConnectionError:
        print("Debug: Connection error occurred")
        return "Error: Failed to connect to Alpha Vantage API."
    except requests.exceptions.Timeout:
        print("Debug: Request timed out")
        return "Error: Request to Alpha Vantage API timed out."
    except ValueError as json_err:
        print(f"Debug: JSON parsing error: {str(json_err)}")
        print(f"Debug: Response text: {response.text[:200]}")
        return f"Error: Failed to parse JSON response: {str(json_err)}"
    except Exception as e:
        print(f"Debug: General error fetching intraday data: {str(e)}")
        return f"Error fetching intraday data for {company}: {str(e)}"
