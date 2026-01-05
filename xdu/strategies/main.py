import pandas as pd
from .Strategies import TradingStrategy
from .Visualizer import TradingVisualizer
from .Indicators import StockIndicators

def main(df):
    # Load and prepare data
    df = StockIndicators(df).calculate_all_indicators()
    
    # Initialize components
    strategy_engine = TradingStrategy(df)
    visualizer = TradingVisualizer(df)
    
    # Run strategies
    results = {}
    for strategy in ['macd', 'rsi', 'bollinger']:
        strategy_results = strategy_engine.run_strategy(strategy)
        results[strategy] = strategy_results
        visualizer.plot_strategy(strategy_results, strategy)
    
    # Generate report
    report = pd.DataFrame({
        'Strategy': results.keys(),
        'Sharpe Ratio': [r['metrics']['sharpe_ratio'] for r in results.values()],
        'Max Drawdown': [max(r['metrics']['drawdown']) for r in results.values()],
        'Total Trades': [len(r['trades']) for r in results.values()]
    })
    print(report)

if __name__ == "__main__":
    data = pd.read_csv("../data/thesis-data.csv", )
    main(data)