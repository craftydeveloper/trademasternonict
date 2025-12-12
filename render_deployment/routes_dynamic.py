"""
Dynamic coin analysis routes
Handles custom coin searches and analysis
"""

from flask import Blueprint, request, jsonify, render_template
from dynamic_coin_analyzer import DynamicCoinAnalyzer, analyze_custom_coin, search_and_analyze_coins

dynamic_bp = Blueprint('dynamic', __name__)

@dynamic_bp.route('/search-coin', methods=['GET', 'POST'])
def search_coin():
    """Search for coins by name, symbol, or contract address"""
    
    if request.method == 'POST':
        data = request.get_json()
        query = data.get('query', '').strip()
    else:
        query = request.args.get('q', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    analyzer = DynamicCoinAnalyzer()
    results = analyzer.search_coin(query)
    
    return jsonify({
        'query': query,
        'results': results,
        'count': len(results)
    })

@dynamic_bp.route('/analyze-coin', methods=['POST'])
def analyze_coin():
    """Analyze any coin by search query"""
    
    data = request.get_json()
    query = data.get('query', '').strip()
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    try:
        analysis = analyze_custom_coin(query)
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

@dynamic_bp.route('/analyze-multiple', methods=['POST'])
def analyze_multiple():
    """Analyze multiple coins at once"""
    
    data = request.get_json()
    queries = data.get('queries', [])
    
    if not queries or not isinstance(queries, list):
        return jsonify({'error': 'Queries array required'}), 400
    
    if len(queries) > 10:
        return jsonify({'error': 'Maximum 10 coins per request'}), 400
    
    try:
        results = search_and_analyze_coins(queries)
        return jsonify({
            'results': results,
            'analyzed_count': len([r for r in results.values() if 'error' not in r])
        })
    except Exception as e:
        return jsonify({'error': f'Batch analysis failed: {str(e)}'}), 500

@dynamic_bp.route('/trending')
def get_trending():
    """Get trending coins"""
    
    limit = request.args.get('limit', 20, type=int)
    limit = min(limit, 50)  # Cap at 50
    
    analyzer = DynamicCoinAnalyzer()
    trending = analyzer.get_trending_coins(limit)
    
    return jsonify({
        'trending': trending,
        'count': len(trending)
    })

@dynamic_bp.route('/quick-signals', methods=['POST'])
def quick_signals():
    """Generate signals for custom coin list"""
    
    data = request.get_json()
    symbols = data.get('symbols', [])
    
    if not symbols:
        return jsonify({'error': 'Symbols array required'}), 400
    
    analyzer = DynamicCoinAnalyzer()
    signals = []
    
    for symbol in symbols[:20]:  # Limit to 20 symbols
        try:
            # Get current data for the symbol
            search_results = analyzer.search_coin(symbol)
            if search_results:
                coin = search_results[0]
                current_data = analyzer.get_coin_data(coin['id'], coin['source'])
                
                if current_data:
                    # Create signal data format
                    signal_input = {
                        symbol.upper(): {
                            'price': current_data['price'],
                            'change_24h': current_data['change_24h'],
                            'volume': current_data['volume_24h']
                        }
                    }
                    
                    coin_signals = analyzer.signal_generator.generate_fast_signals(signal_input)
                    if coin_signals:
                        signals.extend(coin_signals)
        except Exception as e:
            print(f"Signal generation error for {symbol}: {e}")
    
    return jsonify({
        'signals': signals,
        'count': len(signals)
    })

@dynamic_bp.route('/coin-dashboard')
def coin_dashboard():
    """Custom coin analysis dashboard"""
    return render_template('dynamic_dashboard.html')