#!/usr/bin/env python3
"""
Example MCP Server for Cryptocurrency Price Data
Provides tools for getting current and historical crypto prices
"""

import asyncio
import json
import os
from typing import Any, Dict

import httpx
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


class CryptoPriceServer:
    def __init__(self):
        self.coingecko_api_key = os.getenv("COINGECKO_API_KEY")
        self.base_url = "https://api.coingecko.com/api/v3"
        
    async def get_current_price(self, coin_id: str, vs_currency: str = "usd") -> Dict[str, Any]:
        """Get current price of a cryptocurrency"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "ids": coin_id,
                    "vs_currencies": vs_currency,
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true",
                    "include_market_cap": "true"
                }
                
                if self.coingecko_api_key:
                    params["x_cg_demo_api_key"] = self.coingecko_api_key
                
                response = await client.get(f"{self.base_url}/simple/price", params=params)
                response.raise_for_status()
                
                data = response.json()
                if coin_id in data:
                    return {
                        "coin": coin_id,
                        "price": data[coin_id][vs_currency],
                        "price_change_24h": data[coin_id].get(f"{vs_currency}_24h_change", 0),
                        "volume_24h": data[coin_id].get(f"{vs_currency}_24h_vol", 0),
                        "market_cap": data[coin_id].get(f"{vs_currency}_market_cap", 0),
                        "currency": vs_currency
                    }
                else:
                    return {"error": f"Coin {coin_id} not found"}
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def get_historical_data(self, coin_id: str, days: int = 30, vs_currency: str = "usd") -> Dict[str, Any]:
        """Get historical price data"""
        try:
            async with httpx.AsyncClient() as client:
                params = {
                    "vs_currency": vs_currency,
                    "days": str(days),
                    "interval": "daily"
                }
                
                if self.coingecko_api_key:
                    params["x_cg_demo_api_key"] = self.coingecko_api_key
                
                response = await client.get(f"{self.base_url}/coins/{coin_id}/market_chart", params=params)
                response.raise_for_status()
                
                data = response.json()
                
                # Calculate simple statistics
                prices = [point[1] for point in data["prices"]]
                if prices:
                    current_price = prices[-1]
                    min_price = min(prices)
                    max_price = max(prices)
                    avg_price = sum(prices) / len(prices)
                    
                    return {
                        "coin": coin_id,
                        "days": days,
                        "current_price": current_price,
                        "min_price": min_price,
                        "max_price": max_price,
                        "avg_price": avg_price,
                        "price_change_period": ((current_price - prices[0]) / prices[0]) * 100,
                        "is_near_ath": current_price > (max_price * 0.95),
                        "is_near_atl": current_price < (min_price * 1.05),
                        "currency": vs_currency
                    }
                else:
                    return {"error": "No price data available"}
                    
        except Exception as e:
            return {"error": str(e)}
    
    async def get_market_data(self, coin_id: str) -> Dict[str, Any]:
        """Get comprehensive market data"""
        try:
            async with httpx.AsyncClient() as client:
                params = {}
                if self.coingecko_api_key:
                    params["x_cg_demo_api_key"] = self.coingecko_api_key
                
                response = await client.get(f"{self.base_url}/coins/{coin_id}", params=params)
                response.raise_for_status()
                
                data = response.json()
                market_data = data.get("market_data", {})
                
                return {
                    "coin": coin_id,
                    "name": data.get("name"),
                    "symbol": data.get("symbol"),
                    "current_price": market_data.get("current_price", {}).get("usd"),
                    "market_cap": market_data.get("market_cap", {}).get("usd"),
                    "total_volume": market_data.get("total_volume", {}).get("usd"),
                    "price_change_24h": market_data.get("price_change_percentage_24h"),
                    "price_change_7d": market_data.get("price_change_percentage_7d"),
                    "price_change_30d": market_data.get("price_change_percentage_30d"),
                    "ath": market_data.get("ath", {}).get("usd"),
                    "ath_date": market_data.get("ath_date", {}).get("usd"),
                    "atl": market_data.get("atl", {}).get("usd"),
                    "atl_date": market_data.get("atl_date", {}).get("usd"),
                    "market_cap_rank": market_data.get("market_cap_rank")
                }
                
        except Exception as e:
            return {"error": str(e)}


async def main():
    server = Server("crypto-price-server")
    price_service = CryptoPriceServer()
    
    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name="get_current_price",
                description="Get current price and 24h data for a cryptocurrency",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "CoinGecko coin ID (e.g., bitcoin, ethereum)"
                        },
                        "vs_currency": {
                            "type": "string", 
                            "description": "Currency to compare against (default: usd)",
                            "default": "usd"
                        }
                    },
                    "required": ["coin_id"]
                }
            ),
            Tool(
                name="get_historical_data", 
                description="Get historical price data and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "CoinGecko coin ID"
                        },
                        "days": {
                            "type": "integer",
                            "description": "Number of days of historical data (default: 30)",
                            "default": 30
                        },
                        "vs_currency": {
                            "type": "string",
                            "description": "Currency to compare against (default: usd)", 
                            "default": "usd"
                        }
                    },
                    "required": ["coin_id"]
                }
            ),
            Tool(
                name="get_market_data",
                description="Get comprehensive market data including ATH, market cap, etc.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "coin_id": {
                            "type": "string",
                            "description": "CoinGecko coin ID"
                        }
                    },
                    "required": ["coin_id"]
                }
            )
        ]
    
    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        if name == "get_current_price":
            result = await price_service.get_current_price(
                arguments["coin_id"],
                arguments.get("vs_currency", "usd")
            )
        elif name == "get_historical_data":
            result = await price_service.get_historical_data(
                arguments["coin_id"],
                arguments.get("days", 30),
                arguments.get("vs_currency", "usd")
            )
        elif name == "get_market_data":
            result = await price_service.get_market_data(arguments["coin_id"])
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async with stdio_server() as streams:
        await server.run(*streams)


if __name__ == "__main__":
    asyncio.run(main())