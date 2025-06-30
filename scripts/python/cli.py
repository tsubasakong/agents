import typer
from devtools import pprint

from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.connectors.chroma import PolymarketRAG
from polymarket_agents.connectors.news import News
from polymarket_agents.application.trade import Trader
from polymarket_agents.application.executor import Executor
from polymarket_agents.application.creator import Creator
from polymarket_agents.application.enhanced_executor import EnhancedExecutor, run_enhanced_analysis
from polymarket_agents.utils.objects import SimpleMarket

import asyncio
import os

app = typer.Typer()
polymarket = Polymarket()
newsapi_client = News()
polymarket_rag = PolymarketRAG()


@app.command()
def get_all_markets(limit: int = 5, sort_by: str = "liquidity") -> None:
    """
    Query Polymarket's markets
    """
    print(f"limit: int = {limit}, sort_by: str = {sort_by}")
    markets = polymarket.get_all_markets()
    markets = polymarket.filter_markets_for_trading(markets)
    
    # Sort markets based on the specified criteria
    if sort_by == "spread":
        markets = sorted(markets, key=lambda x: x.spread)  # Lower spread is better
    elif sort_by == "liquidity":
        markets = sorted(markets, key=lambda x: x.liquidity, reverse=True)  # Higher liquidity is better
    elif sort_by == "volume":
        markets = sorted(markets, key=lambda x: x.volume, reverse=True)  # Higher volume is better
    
    markets = markets[:limit]
    pprint(markets)


@app.command()
def get_relevant_news(keywords: str) -> None:
    """
    Use NewsAPI to query the internet
    """
    articles = newsapi_client.get_articles_for_cli_keywords(keywords)
    pprint(articles)


@app.command()
def get_all_events(limit: int = 5, sort_by: str = "number_of_markets") -> None:
    """
    Query Polymarket's events
    """
    print(f"limit: int = {limit}, sort_by: str = {sort_by}")
    events = polymarket.get_all_events()
    events = polymarket.filter_events_for_trading(events)
    if sort_by == "number_of_markets":
        events = sorted(events, key=lambda x: len(x.markets), reverse=True)
    events = events[:limit]
    pprint(events)


@app.command()
def create_local_markets_rag(local_directory: str) -> None:
    """
    Create a local markets database for RAG
    """
    polymarket_rag.create_local_markets_rag(local_directory=local_directory)


@app.command()
def query_local_markets_rag(vector_db_directory: str, query: str) -> None:
    """
    RAG over a local database of Polymarket's events
    """
    response = polymarket_rag.query_local_markets_rag(
        local_directory=vector_db_directory, query=query
    )
    pprint(response)


@app.command()
def ask_superforecaster(event_title: str, market_question: str, outcome: str) -> None:
    """
    Ask a superforecaster about a trade
    """
    print(
        f"event: str = {event_title}, question: str = {market_question}, outcome (usually yes or no): str = {outcome}"
    )
    executor = Executor()
    response = executor.get_superforecast(
        event_title=event_title, market_question=market_question, outcome=outcome
    )
    print(f"Response:{response}")


@app.command()
def create_market() -> None:
    """
    Format a request to create a market on Polymarket
    """
    c = Creator()
    market_description = c.one_best_market()
    print(f"market_description: str = {market_description}")


@app.command()
def ask_llm(user_input: str) -> None:
    """
    Ask a question to the LLM and get a response.
    """
    executor = Executor()
    response = executor.get_llm_response(user_input)
    print(f"LLM Response: {response}")


@app.command()
def ask_polymarket_llm(user_input: str) -> None:
    """
    What types of markets do you want trade?
    """
    executor = Executor()
    response = executor.get_polymarket_llm(user_input=user_input)
    print(f"LLM + current markets&events response: {response}")


@app.command()
def enhanced_analysis(market_id: int = None) -> None:
    """
    Run enhanced AI analysis with MCP tools on a specific market or the most liquid market
    """
    print("🚀 Enhanced Market Analysis with MCP Tools")
    
    if market_id:
        print(f"📊 Analyzing specific market ID: {market_id}")
        # TODO: Implement specific market lookup
        market_data = polymarket.get_market_by_id(market_id)
        if not market_data:
            print(f"❌ Market {market_id} not found")
            return
        markets = [market_data]
    else:
        print("📊 Finding most liquid markets for analysis...")
        all_markets = polymarket.get_all_markets()
        markets = polymarket.filter_markets_for_trading(all_markets)
        markets = sorted(markets, key=lambda x: x.liquidity, reverse=True)[:5]
    
    if not markets:
        print("❌ No suitable markets found for analysis")
        return
    
    # Use the first (most liquid) market
    selected_market = markets[0]
    print(f"🎯 Selected: {selected_market.question}")
    print(f"💰 Liquidity: ${selected_market.liquidity:,.2f}")
    
    try:
        # Run enhanced analysis
        result = run_enhanced_analysis(selected_market)
        
        print("\n📋 Enhanced Analysis Results:")
        print("=" * 60)
        print(f"📈 Recommendation: {result.get('recommendation', 'UNKNOWN')}")
        print(f"🎯 Confidence: {result.get('confidence', 0):.1%}")
        print(f"🔗 Trace URL: {result.get('trace_url', 'Not available')}")
        
        reasoning = result.get('reasoning', 'No reasoning provided')
        print(f"\n💭 Analysis Reasoning:")
        print(reasoning[:1000] + "..." if len(reasoning) > 1000 else reasoning)
        
    except Exception as e:
        print(f"❌ Enhanced analysis failed: {e}")


@app.command()
def run_autonomous_trader() -> None:
    """
    Let an autonomous system trade for you using ONLY enhanced MCP analysis.
    """
    trader = Trader()
    trader.one_best_trade()


if __name__ == "__main__":
    app()
