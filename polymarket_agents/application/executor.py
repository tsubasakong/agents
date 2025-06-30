import os
import json
import ast
import re
from typing import List, Dict, Any

import math

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from polymarket_agents.polymarket.gamma import GammaMarketClient as Gamma
from polymarket_agents.connectors.chroma import PolymarketRAG as Chroma
from polymarket_agents.utils.objects import SimpleEvent, SimpleMarket
from polymarket_agents.application.prompts import Prompter
from polymarket_agents.polymarket.polymarket import Polymarket

def retain_keys(data, keys_to_retain):
    if isinstance(data, dict):
        return {
            key: retain_keys(value, keys_to_retain)
            for key, value in data.items()
            if key in keys_to_retain
        }
    elif isinstance(data, list):
        return [retain_keys(item, keys_to_retain) for item in data]
    else:
        return data

class Executor:
    def __init__(self, default_model='gpt-3.5-turbo-16k') -> None:
        load_dotenv()
        max_token_model = {'gpt-3.5-turbo-16k':15000, 'gpt-4-1106-preview':95000}
        self.token_limit = max_token_model.get(default_model)
        self.prompter = Prompter()
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model=default_model, #gpt-3.5-turbo"
            temperature=0,
        )
        self.gamma = Gamma()
        self.chroma = Chroma()
        self.polymarket = Polymarket()

    def get_llm_response(self, user_input: str) -> str:
        system_message = SystemMessage(content=str(self.prompter.market_analyst()))
        human_message = HumanMessage(content=user_input)
        messages = [system_message, human_message]
        result = self.llm.invoke(messages)
        return result.content

    def get_superforecast(
        self, event_title: str, market_question: str, outcome: str
    ) -> str:
        messages = self.prompter.superforecaster(
            description=event_title, question=market_question, outcome=outcome
        )
        result = self.llm.invoke(messages)
        return result.content


    def estimate_tokens(self, text: str) -> int:
        # This is a rough estimate. For more accurate results, consider using a tokenizer.
        return len(text) // 4  # Assuming average of 4 characters per token

    def process_data_chunk(self, data1: List[Dict[Any, Any]], data2: List[Dict[Any, Any]], user_input: str) -> str:
        system_message = SystemMessage(
            content=str(self.prompter.prompts_polymarket(data1=data1, data2=data2))
        )
        human_message = HumanMessage(content=user_input)
        messages = [system_message, human_message]
        result = self.llm.invoke(messages)
        return result.content


    def divide_list(self, original_list, i):
        # Calculate the size of each sublist
        sublist_size = math.ceil(len(original_list) / i)
        
        # Use list comprehension to create sublists
        return [original_list[j:j+sublist_size] for j in range(0, len(original_list), sublist_size)]
    
    def get_polymarket_llm(self, user_input: str) -> str:
        data1 = self.gamma.get_current_events()
        data2 = self.gamma.get_current_markets()
        
        combined_data = str(self.prompter.prompts_polymarket(data1=data1, data2=data2))
        
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
                sub_tokens = self.estimate_tokens(str(self.prompter.prompts_polymarket(data1=sub_data1, data2=sub_data2)))

                result = self.process_data_chunk(sub_data1, sub_data2, user_input)
                results.append(result)
            
            combined_result = " ".join(results)
            
        
            
            return combined_result
    def filter_events(self, events: "list[SimpleEvent]") -> str:
        prompt = self.prompter.filter_events(events)
        result = self.llm.invoke(prompt)
        return result.content

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

            prompt = self.prompter.superforecaster(question, description, outcomes)
            print()
            print("... prompting ... ", prompt)
            print()
            result = self.llm.invoke(prompt)
            content = result.content

            print("result: ", content)
            print()
            prompt = self.prompter.one_best_trade(content, outcomes, outcome_prices)
            print("... prompting ... ", prompt)
            print()
            result = self.llm.invoke(prompt)
            content = result.content

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
            
        try:
            prompt = self.prompter.create_new_market(filtered_markets)
            print()
            print("... prompting ... ", prompt)
            print()
            result = self.llm.invoke(prompt)
            content = result.content
            return content
        except Exception as e:
            print(f"Error in source_best_market_to_create: {e}")
            return "No market to create"
