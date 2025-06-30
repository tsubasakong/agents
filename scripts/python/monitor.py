from polymarket_agents.application.trade import Trader
import time
import argparse

class Monitor:
    def __init__(self, interval_seconds=3600):
        self.trader = Trader()
        self.interval_seconds = interval_seconds
    
    def monitor_markets(self):
        """
        Continuously monitors markets without executing trades.
        This function runs the analysis part of one_best_trade but skips the actual trading.
        """
        try:
            self.trader.pre_trade_logic()

            events = self.trader.polymarket.get_all_tradeable_events()
            print(f"1. FOUND {len(events)} EVENTS")
            
            if not events:
                print("No events found. Skipping further analysis.")
                return

            filtered_events = self.trader.agent.filter_events_with_rag(events)
            print(f"2. FILTERED {len(filtered_events)} EVENTS")
            
            if not filtered_events:
                print("No events passed filtering. Skipping further analysis.")
                return

            markets = self.trader.agent.map_filtered_events_to_markets(filtered_events)
            print()
            print(f"3. FOUND {len(markets)} MARKETS")
            
            if not markets:
                print("No markets found. Skipping further analysis.")
                return

            print()
            filtered_markets = self.trader.agent.filter_markets(markets)
            print(f"4. FILTERED {len(filtered_markets)} MARKETS")

            if filtered_markets:
                market = filtered_markets[0]
                best_trade = self.trader.agent.source_best_trade(market)
                print(f"5. CALCULATED TRADE {best_trade}")

                amount = self.trader.agent.format_trade_prompt_for_execution(best_trade)
                print(f"6. WOULD TRADE {amount} (Trading disabled)")
            else:
                print("No suitable markets found for trading")

        except Exception as e:
            print(f"Error: {e}")
    
    def start_continuous_monitoring(self):
        """
        Starts continuous monitoring with the specified interval.
        Press Ctrl+C to stop.
        """
        print(f"Starting continuous market monitoring (interval: {self.interval_seconds} seconds)")
        print("Press Ctrl+C to stop")
        
        try:
            while True:
                print("\n" + "=" * 50)
                print(f"Market analysis at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                print("=" * 50)
                
                self.monitor_markets()
                
                print(f"\nSleeping for {self.interval_seconds} seconds...")
                time.sleep(self.interval_seconds)
        except KeyboardInterrupt:
            print("\nMonitoring stopped by user")

def parse_arguments():
    parser = argparse.ArgumentParser(description='Monitor Polymarket markets without trading')
    parser.add_argument('--interval', type=int, default=3600,
                        help='Interval between market checks in seconds (default: 3600)')
    parser.add_argument('--once', action='store_true',
                        help='Run the monitor only once instead of continuously')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    # Create monitor with specified interval
    monitor = Monitor(interval_seconds=args.interval)
    
    if args.once:
        # Run the monitor just once
        print("Running market analysis once...")
        monitor.monitor_markets()
    else:
        # Start continuous monitoring
        monitor.start_continuous_monitoring()