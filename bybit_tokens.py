"""
Comprehensive Bybit Futures Token List
Contains all major cryptocurrencies available for futures trading on Bybit
"""

def get_comprehensive_bybit_tokens():
    """Returns comprehensive list of Bybit futures cryptocurrencies"""
    return [
        # Major cryptocurrencies
        {'symbol': 'BTC', 'name': 'Bitcoin', 'category': 'Major'},
        {'symbol': 'ETH', 'name': 'Ethereum', 'category': 'Major'},
        {'symbol': 'BNB', 'name': 'BNB', 'category': 'Major'},
        {'symbol': 'XRP', 'name': 'Ripple', 'category': 'Major'},
        {'symbol': 'ADA', 'name': 'Cardano', 'category': 'Major'},
        {'symbol': 'DOGE', 'name': 'Dogecoin', 'category': 'Major'},
        {'symbol': 'SOL', 'name': 'Solana', 'category': 'Major'},
        {'symbol': 'TRX', 'name': 'Tron', 'category': 'Major'},
        {'symbol': 'DOT', 'name': 'Polkadot', 'category': 'Major'},
        {'symbol': 'MATIC', 'name': 'Polygon', 'category': 'Major'},
        {'symbol': 'LTC', 'name': 'Litecoin', 'category': 'Major'},
        {'symbol': 'SHIB', 'name': 'Shiba Inu', 'category': 'Major'},
        {'symbol': 'AVAX', 'name': 'Avalanche', 'category': 'Major'},
        {'symbol': 'UNI', 'name': 'Uniswap', 'category': 'Major'},
        {'symbol': 'LINK', 'name': 'Chainlink', 'category': 'Major'},
        {'symbol': 'ATOM', 'name': 'Cosmos', 'category': 'Major'},
        {'symbol': 'ETC', 'name': 'Ethereum Classic', 'category': 'Major'},
        {'symbol': 'XLM', 'name': 'Stellar', 'category': 'Major'},
        {'symbol': 'BCH', 'name': 'Bitcoin Cash', 'category': 'Major'},
        {'symbol': 'NEAR', 'name': 'NEAR Protocol', 'category': 'Major'},
        {'symbol': 'LDO', 'name': 'Lido DAO', 'category': 'Major'},
        {'symbol': 'ICP', 'name': 'Internet Computer', 'category': 'Major'},
        {'symbol': 'HBAR', 'name': 'Hedera', 'category': 'Major'},
        {'symbol': 'FIL', 'name': 'Filecoin', 'category': 'Major'},
        {'symbol': 'VET', 'name': 'VeChain', 'category': 'Major'},
        
        # DeFi tokens
        {'symbol': 'AAVE', 'name': 'Aave', 'category': 'DeFi'},
        {'symbol': 'MKR', 'name': 'Maker', 'category': 'DeFi'},
        {'symbol': 'COMP', 'name': 'Compound', 'category': 'DeFi'},
        {'symbol': 'YFI', 'name': 'Yearn Finance', 'category': 'DeFi'},
        {'symbol': 'SUSHI', 'name': 'SushiSwap', 'category': 'DeFi'},
        {'symbol': 'CRV', 'name': 'Curve DAO', 'category': 'DeFi'},
        {'symbol': 'SNX', 'name': 'Synthetix', 'category': 'DeFi'},
        {'symbol': 'BAL', 'name': 'Balancer', 'category': 'DeFi'},
        {'symbol': 'DYDX', 'name': 'dYdX', 'category': 'DeFi'},
        {'symbol': 'GMX', 'name': 'GMX', 'category': 'DeFi'},
        {'symbol': 'INJ', 'name': 'Injective Protocol', 'category': 'DeFi'},
        {'symbol': 'JOE', 'name': 'TraderJoe', 'category': 'DeFi'},
        {'symbol': 'ALPHA', 'name': 'Alpha Finance Lab', 'category': 'DeFi'},
        {'symbol': 'RUNE', 'name': 'THORChain', 'category': 'DeFi'},
        
        # Layer 1 blockchains
        {'symbol': 'FTM', 'name': 'Fantom', 'category': 'Layer 1'},
        {'symbol': 'ALGO', 'name': 'Algorand', 'category': 'Layer 1'},
        {'symbol': 'FLOW', 'name': 'Flow', 'category': 'Layer 1'},
        {'symbol': 'THETA', 'name': 'Theta Network', 'category': 'Layer 1'},
        {'symbol': 'XTZ', 'name': 'Tezos', 'category': 'Layer 1'},
        {'symbol': 'ZEC', 'name': 'Zcash', 'category': 'Layer 1'},
        {'symbol': 'DASH', 'name': 'Dash', 'category': 'Layer 1'},
        {'symbol': 'SUI', 'name': 'Sui', 'category': 'Layer 1'},
        {'symbol': 'APT', 'name': 'Aptos', 'category': 'Layer 1'},
        {'symbol': 'SEI', 'name': 'Sei', 'category': 'Layer 1'},
        {'symbol': 'TIA', 'name': 'Celestia', 'category': 'Layer 1'},
        {'symbol': 'EGLD', 'name': 'MultiversX', 'category': 'Layer 1'},
        {'symbol': 'KAS', 'name': 'Kaspa', 'category': 'Layer 1'},
        {'symbol': 'STX', 'name': 'Stacks', 'category': 'Layer 1'},
        
        # Layer 2 and scaling
        {'symbol': 'ARB', 'name': 'Arbitrum', 'category': 'Layer 2'},
        {'symbol': 'OP', 'name': 'Optimism', 'category': 'Layer 2'},
        {'symbol': 'STRK', 'name': 'Starknet', 'category': 'Layer 2'},
        {'symbol': 'IMX', 'name': 'Immutable X', 'category': 'Layer 2'},
        {'symbol': 'MANTA', 'name': 'Manta Network', 'category': 'Layer 2'},
        
        # Gaming and metaverse
        {'symbol': 'AXS', 'name': 'Axie Infinity', 'category': 'Gaming'},
        {'symbol': 'SAND', 'name': 'The Sandbox', 'category': 'Gaming'},
        {'symbol': 'MANA', 'name': 'Decentraland', 'category': 'Gaming'},
        {'symbol': 'ENJ', 'name': 'Enjin Coin', 'category': 'Gaming'},
        {'symbol': 'GALA', 'name': 'Gala', 'category': 'Gaming'},
        {'symbol': 'APE', 'name': 'ApeCoin', 'category': 'Gaming'},
        {'symbol': 'GMT', 'name': 'STEPN', 'category': 'Gaming'},
        {'symbol': 'CHZ', 'name': 'Chiliz', 'category': 'Gaming'},
        {'symbol': 'ALICE', 'name': 'MyNeighborAlice', 'category': 'Gaming'},
        {'symbol': 'TLM', 'name': 'Alien Worlds', 'category': 'Gaming'},
        {'symbol': 'YGG', 'name': 'Yield Guild Games', 'category': 'Gaming'},
        {'symbol': 'MAGIC', 'name': 'Magic', 'category': 'Gaming'},
        
        # Meme coins
        {'symbol': 'PEPE', 'name': 'Pepe', 'category': 'Meme'},
        {'symbol': 'FLOKI', 'name': 'Floki Inu', 'category': 'Meme'},
        {'symbol': 'BONK', 'name': 'Bonk', 'category': 'Meme'},
        {'symbol': 'WIF', 'name': 'dogwifhat', 'category': 'Meme'},
        {'symbol': 'BOME', 'name': 'Book of Meme', 'category': 'Meme'},
        {'symbol': 'MEME', 'name': 'Memecoin', 'category': 'Meme'},
        {'symbol': '1000SATS', 'name': '1000SATS', 'category': 'Meme'},
        {'symbol': 'ORDI', 'name': 'Ordinals', 'category': 'Meme'},
        {'symbol': 'BABYDOGE', 'name': 'Baby Doge Coin', 'category': 'Meme'},
        
        # AI and tech
        {'symbol': 'RNDR', 'name': 'Render Token', 'category': 'AI'},
        {'symbol': 'FET', 'name': 'Fetch.ai', 'category': 'AI'},
        {'symbol': 'OCEAN', 'name': 'Ocean Protocol', 'category': 'AI'},
        {'symbol': 'TAO', 'name': 'Bittensor', 'category': 'AI'},
        {'symbol': 'AGIX', 'name': 'SingularityNET', 'category': 'AI'},
        {'symbol': 'AI', 'name': 'Sleepless AI', 'category': 'AI'},
        {'symbol': 'WLD', 'name': 'Worldcoin', 'category': 'AI'},
        
        # Trending and new
        {'symbol': 'JUP', 'name': 'Jupiter', 'category': 'Trending'},
        {'symbol': 'PYTH', 'name': 'Pyth Network', 'category': 'Trending'},
        {'symbol': 'JTO', 'name': 'Jito', 'category': 'Trending'},
        {'symbol': 'W', 'name': 'Wormhole', 'category': 'Trending'},
        {'symbol': 'ENA', 'name': 'Ethena', 'category': 'Trending'},
        {'symbol': 'OMNI', 'name': 'Omni Network', 'category': 'Trending'},
        {'symbol': 'REZ', 'name': 'Renzo', 'category': 'Trending'},
        {'symbol': 'PENDLE', 'name': 'Pendle', 'category': 'Trending'},
        
        # NFT and Web3
        {'symbol': 'BLUR', 'name': 'Blur', 'category': 'NFT'},
        {'symbol': 'LOOKS', 'name': 'LooksRare', 'category': 'NFT'},
        {'symbol': 'X2Y2', 'name': 'X2Y2', 'category': 'NFT'},
        
        # Infrastructure and tools
        {'symbol': 'GRT', 'name': 'The Graph', 'category': 'Infrastructure'},
        {'symbol': 'MASK', 'name': 'Mask Network', 'category': 'Infrastructure'},
        {'symbol': 'AR', 'name': 'Arweave', 'category': 'Infrastructure'},
        {'symbol': 'STORJ', 'name': 'Storj', 'category': 'Infrastructure'}
    ]

def get_token_count():
    """Returns total number of supported tokens"""
    return len(get_comprehensive_bybit_tokens())