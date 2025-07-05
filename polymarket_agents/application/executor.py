import os
import json
import ast
import re
from typing import List, Dict, Any

import math

from openai import OpenAI

from polymarket_agents.config import get_settings
from polymarket_agents.common.utils import retain_keys, estimate_tokens, divide_list
from polymarket_agents.common.errors import ConfigurationError
from polymarket_agents.polymarket.gamma import GammaMarketClient as Gamma
from polymarket_agents.connectors.chroma import PolymarketRAG as Chroma
from polymarket_agents.utils.objects import SimpleEvent, SimpleMarket
from polymarket_agents.application.prompts import Prompter
from polymarket_agents.polymarket.polymarket import Polymarket
from polymarket_agents.application.base_executor import BaseExecutor

class Executor(BaseExecutor):
    def __init__(self, default_model='gpt-4o', settings=None) -> None:
        # Initialize base executor with settings
        super().__init__(settings)
        
        # Model configuration
        self.default_model = default_model
        max_token_model = {'gpt-3.5-turbo-16k': 15000, 'gpt-4-1106-preview': 95000, 'gpt-4o': 50000}
        self.token_limit = max_token_model.get(default_model, 50000)
        
        # Initialize OpenAI client
        self.openai_client = OpenAI(api_key=self.settings.openai_api_key)
        
        # Initialize connectors
        self.chroma = Chroma()

    def get_llm_response(self, user_input: str) -> str:
        """Get LLM response using direct OpenAI SDK."""
        messages = [
            {"role": "system", "content": str(self.prompter.market_analyst())},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error getting LLM response: {e}")
            raise

    def get_superforecast(
        self, event_title: str, market_question: str, outcome: str
    ) -> str:
        """Get superforecast using direct OpenAI SDK."""
        prompt = self.prompter.superforecaster(
            description=event_title, question=market_question, outcome=outcome
        )
        
        messages = [
            {"role": "system", "content": prompt}
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error getting superforecast: {e}")
            raise


    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using shared utility function."""
        return estimate_tokens(text)

    def process_data_chunk(self, data1: List[Dict[Any, Any]], data2: List[Dict[Any, Any]], user_input: str) -> str:
        """Process data chunk using direct OpenAI SDK."""
        system_content = str(self.prompter.prompts_polymarket_general(data1=data1, data2=data2))
        
        messages = [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_input}
        ]
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=messages,
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error processing data chunk: {e}")
            raise


    def divide_list(self, original_list, i):
        """Divide list using shared utility function."""
        return divide_list(original_list, i)
    
    def get_polymarket_llm(self, user_input: str) -> str:
        data1 = self.gamma.get_current_events()
        data2 = self.gamma.get_current_markets()
        
        combined_data = str(self.prompter.prompts_polymarket_general(data1=data1, data2=data2))
        
        # Estimate total tokens
        total_tokens = self.estimate_tokens(combined_data)
        
        # Set a token limit (adjust as needed, leaving room for system and user messages)
        token_limit = self.token_limit
        if total_tokens <= token_limit:
            # If within limit, process normally
            return self.process_data_chunk(data1, data2, user_input)
        else:
            # If exceeding limit, process in chunks
            chunk_size = len(combined_data) // ((total_tokens // token_limit) + 1)
            print(f'total tokens {total_tokens} exceeding llm capacity, now will split and answer')
            group_size = (total_tokens // token_limit) + 1 # 3 is safe factor
            keys_no_meaning = ['image','pagerDutyNotificationEnabled','resolvedBy','endDate','clobTokenIds','negRiskMarketID','conditionId','updatedAt','startDate']
            useful_keys = ['id','questionID','description','liquidity','clobTokenIds','outcomes','outcomePrices','volume','startDate','endDate','question','questionID','events']
            data1 = retain_keys(data1, useful_keys)
            cut_1 = self.divide_list(data1, group_size)
            cut_2 = self.divide_list(data2, group_size)
            cut_data_12 = zip(cut_1, cut_2)

            results = []

            for cut_data in cut_data_12:
                sub_data1 = cut_data[0]
                sub_data2 = cut_data[1]
                sub_tokens = self.estimate_tokens(str(self.prompter.prompts_polymarket_general(data1=sub_data1, data2=sub_data2)))

                result = self.process_data_chunk(sub_data1, sub_data2, user_input)
                results.append(result)
            
            combined_result = " ".join(results)
            
        
            
            return combined_result
    def filter_events(self, events: "list[SimpleEvent]") -> str:
        """Filter events using direct OpenAI SDK."""
        prompt = self.prompter.filter_events()
        
        try:
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            self.logger.error(f"Error filtering events: {e}")
            raise

    def filter_events_with_rag(self, events: "list[SimpleEvent]") -> str:
        # Handle empty events list
        if not events:
            print("Warning: Empty events list provided to filter_events_with_rag()")
            return []
            
        prompt = self.prompter.filter_events()
        print()
        print("... prompting ... ", prompt)
        print()
        return self.chroma.events(events, prompt)

    def map_filtered_events_to_markets(
        self, filtered_events: "list[SimpleEvent]"
    ) -> "list[SimpleMarket]":
        # Handle empty filtered_events list
        if not filtered_events:
            print("Warning: Empty filtered_events list provided to map_filtered_events_to_markets()")
            return []
            
        markets = []
        for e in filtered_events:
            try:
                data = json.loads(e[0].json())
                market_ids = data["metadata"]["markets"].split(",")
                for market_id in market_ids:
                    market_data = self.gamma.get_market(market_id)
                    if not market_data:  # Handle None or empty dict
                        print(f"Warning: No market data returned for market_id {market_id}")
                        continue
                        
                    formatted_market_data = self.polymarket.map_api_to_market(market_data)
                    if formatted_market_data:  # Check if map_api_to_market returned a valid object
                        markets.append(formatted_market_data)
            except Exception as ex:
                print(f"Error processing event in map_filtered_events_to_markets: {ex}")
        return markets

    def filter_markets(self, markets) -> "list[tuple]":
        # Handle empty markets list
        if not markets:
            print("Warning: Empty markets list provided to filter_markets()")
            return []
            
        prompt = self.prompter.filter_markets()
        print()
        print("... prompting ... ", prompt)
        print()
        return self.chroma.markets(markets, prompt)

    def source_best_trade(self, market_object) -> str:
        # Handle empty or invalid market_object
        if not market_object or not isinstance(market_object, list) or len(market_object) == 0:
            print("Warning: Empty or invalid market_object provided to source_best_trade()")
            return "No trade available, 0.0"
            
        try:
            market_document = market_object[0].dict()
            market = market_document["metadata"]
            outcome_prices = ast.literal_eval(market["outcome_prices"])
            outcomes = ast.literal_eval(market["outcomes"])
            question = market["question"]
            description = market_document["page_content"]

            # Get superforecaster prediction
            prompt = self.prompter.superforecaster(question, description, outcomes)
            print()
            print("... prompting ... ", prompt)
            print()
            
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            content = response.choices[0].message.content

            print("result: ", content)
            print()
            
            # Get trading recommendation
            trade_prompt = self.prompter.one_best_trade(content, outcomes, outcome_prices)
            print("... prompting ... ", trade_prompt)
            print()
            
            response = self.openai_client.chat.completions.create(
                model=self.default_model,
                messages=[{"role": "system", "content": trade_prompt}],
                temperature=self.settings.openai_temperature,
                max_tokens=self.settings.openai_max_tokens
            )
            content = response.choices[0].message.content

            print("result: ", content)
            return content
        except Exception as e:
            print(f"Error in source_best_trade: {e}")
            return "No trade available, 0.0"

    def format_trade_prompt_for_execution(self, best_trade: str) -> float:
        try:
            # Check if best_trade is valid
            if not best_trade or "No trade available" in best_trade:
                print("Warning: No valid trade available in format_trade_prompt_for_execution()")
                return 0.0
                
            data = best_trade.split(",")
            if len(data) < 2:
                print(f"Warning: Invalid best_trade format: {best_trade}")
                return 0.0
                
            # Extract size using regex
            size_matches = re.findall("\d+\.\d+", data[1])
            if not size_matches:
                print(f"Warning: Could not extract size from best_trade: {best_trade}")
                return 0.0
                
            size = size_matches[0]
            usdc_balance = self.polymarket.get_usdc_balance()
            return float(size) * usdc_balance
        except Exception as e:
            print(f"Error in format_trade_prompt_for_execution: {e}")
            return 0.0

    def source_best_market_to_create(self, filtered_markets) -> str:
        # Handle empty or invalid filtered_markets
        if not filtered_markets:
            print("Warning: Empty filtered_markets provided to source_best_market_to_create()")
            return "No market to create"
    
    async def analyze_market(self, market: SimpleMarket) -> Dict[str, Any]:
        """
        Implement the abstract method from BaseExecutor.
        This is a basic implementation using existing LLM methods.
        """
        try:
            context = self.get_market_analysis_context(market)
            
            # Use the superforecaster method for analysis
            if market.outcomes and len(market.outcomes) > 0:
                # Analyze each outcome
                analysis_results = []
                for outcome in market.outcomes:
                    try:
                        forecast = self.get_superforecast(
                            market.description or market.question,
                            market.question,
                            outcome
                        )
                        analysis_results.append({
                            "outcome": outcome,
                            "forecast": forecast
                        })
                    except Exception as e:
                        self.logger.warning(f"Error forecasting outcome {outcome}: {e}")
                        analysis_results.append({
                            "outcome": outcome,
                            "forecast": "Analysis failed",
                            "error": str(e)
                        })
                
                return {
                    "market_id": market.id,
                    "question": market.question,
                    "recommendation": "ANALYZE",  # This executor is for analysis
                    "confidence": 0.7,
                    "reasoning": "Analysis using superforecaster methodology",
                    "analysis_type": "basic_llm",
                    "forecasts": analysis_results,
                    "context": context
                }
            else:
                return {
                    "market_id": market.id,
                    "question": market.question,
                    "recommendation": "HOLD",
                    "confidence": 0.0,
                    "reasoning": "No outcomes available for analysis",
                    "analysis_type": "basic_llm",
                    "context": context
                }
                
        except Exception as e:
            self.logger.error(f"Error analyzing market {market.id}: {e}")
            return {
                "error": str(e),
                "market_id": market.id,
                "recommendation": "HOLD",
                "confidence": 0.0,
                "analysis_type": "error"
                         }
