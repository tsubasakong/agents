import json
import os
import time

from langchain_openai import OpenAIEmbeddings
from langchain_community.document_loaders import JSONLoader
from langchain_community.vectorstores.chroma import Chroma

from polymarket_agents.polymarket.gamma import GammaMarketClient
from polymarket_agents.utils.objects import SimpleEvent, SimpleMarket


class PolymarketRAG:
    def __init__(self, local_db_directory=None, embedding_function=None) -> None:
        self.gamma_client = GammaMarketClient()
        self.local_db_directory = local_db_directory
        self.embedding_function = embedding_function

    def load_json_from_local(
        self, json_file_path=None, vector_db_directory="./local_db"
    ) -> None:
        loader = JSONLoader(
            file_path=json_file_path, jq_schema=".[].description", text_content=False
        )
        loaded_docs = loader.load()

        embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

    def create_local_markets_rag(self, local_directory="./local_db") -> None:
        all_markets = self.gamma_client.get_all_current_markets()

        if not os.path.isdir(local_directory):
            os.mkdir(local_directory)

        local_file_path = f"{local_directory}/all-current-markets_{time.time()}.json"

        with open(local_file_path, "w+") as output_file:
            json.dump(all_markets, output_file)

        self.load_json_from_local(
            json_file_path=local_file_path, vector_db_directory=local_directory
        )

    def query_local_markets_rag(
        self, local_directory=None, query=None
    ) -> "list[tuple]":
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        local_db = Chroma(
            persist_directory=local_directory, embedding_function=embedding_function
        )
        response_docs = local_db.similarity_search_with_score(query=query)
        return response_docs

    def events(self, events: "list[SimpleEvent]", prompt: str) -> "list[tuple]":
        # Handle empty events list
        if not events:
            print("Warning: Empty events list provided to PolymarketRAG.events()")
            return []
            
        # create local json file
        local_events_directory: str = "./local_db_events"
        if not os.path.isdir(local_events_directory):
            os.mkdir(local_events_directory)
        local_file_path = f"{local_events_directory}/events.json"
        dict_events = [x.dict() for x in events]
        with open(local_file_path, "w+") as output_file:
            json.dump(dict_events, output_file)

        # create vector db
        def metadata_func(record: dict, metadata: dict) -> dict:

            metadata["id"] = record.get("id")
            metadata["markets"] = record.get("markets")

            return metadata

        loader = JSONLoader(
            file_path=local_file_path,
            jq_schema=".[]",
            content_key="description",
            text_content=False,
            metadata_func=metadata_func,
        )
        loaded_docs = loader.load()
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_db_directory = f"{local_events_directory}/chroma"
        local_db = Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

        # query
        return local_db.similarity_search_with_score(query=prompt)

    def markets(self, markets: "list[SimpleMarket]", prompt: str) -> "list[tuple]":
        # Handle empty markets list
        if not markets:
            print("Warning: Empty markets list provided to PolymarketRAG.markets()")
            return []
            
        # create local json file
        local_events_directory: str = "./local_db_markets"
        if not os.path.isdir(local_events_directory):
            os.mkdir(local_events_directory)
        local_file_path = f"{local_events_directory}/markets.json"
        
        # Convert SimpleMarket objects to dictionaries for JSON serialization
        markets_dict = []
        for market in markets:
            if hasattr(market, 'dict'):
                markets_dict.append(market.dict())
            elif hasattr(market, '__dict__'):
                markets_dict.append(market.__dict__)
            else:
                # Fallback: manually create dict from known attributes
                markets_dict.append({
                    "id": market.id,
                    "question": market.question,
                    "description": market.description,
                    "outcomes": market.outcomes,
                    "outcome_prices": market.outcome_prices,
                    "clob_token_ids": market.clob_token_ids,
                    "spread": market.spread,
                    "liquidity": getattr(market, 'liquidity', 0),
                    "volume": getattr(market, 'volume', 0)
                })
        
        with open(local_file_path, "w+") as output_file:
            json.dump(markets_dict, output_file)

        # create vector db
        def metadata_func(record: dict, metadata: dict) -> dict:

            metadata["id"] = record.get("id")
            metadata["outcomes"] = record.get("outcomes")
            metadata["outcome_prices"] = record.get("outcome_prices")
            metadata["question"] = record.get("question")
            metadata["clob_token_ids"] = record.get("clob_token_ids")

            return metadata

        loader = JSONLoader(
            file_path=local_file_path,
            jq_schema=".[]",
            content_key="description",
            text_content=False,
            metadata_func=metadata_func,
        )
        loaded_docs = loader.load()
        embedding_function = OpenAIEmbeddings(model="text-embedding-3-small")
        vector_db_directory = f"{local_events_directory}/chroma"
        local_db = Chroma.from_documents(
            loaded_docs, embedding_function, persist_directory=vector_db_directory
        )

        # query
        return local_db.similarity_search_with_score(query=prompt)
