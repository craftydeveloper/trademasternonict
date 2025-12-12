// WebSocket connection handler
let socket;
let isConnected = false;

// Initialize WebSocket connection
function initializeWebSocket() {
    socket = io();
    
    socket.on('connect', function() {
        console.log('Connected to server');
        isConnected = true;
        updateConnectionStatus(true);
        
        // Subscribe to price updates for popular tokens
        socket.emit('subscribe_prices', {
            symbols: ['SOL', 'RAY', 'ORCA', 'STEP', 'COPE', 'MNGO']
        });
        
        // Request initial portfolio data
        if (typeof handlePortfolioUpdate === 'function') {
            socket.emit('get_portfolio');
        }
    });
    
    socket.on('disconnect', function() {
        console.log('Disconnected from server');
        isConnected = false;
        updateConnectionStatus(false);
    });
    
    socket.on('connected', function(data) {
        console.log('Server message:', data.data);
    });
    
    socket.on('price_update', function(data) {
        if (typeof handlePriceUpdate === 'function') {
            handlePriceUpdate(data);
        }
        updateMarketData(data);
    });
    
    socket.on('portfolio_update', function(data) {
        if (typeof handlePortfolioUpdate === 'function') {
            handlePortfolioUpdate(data);
        }
    });
    
    socket.on('trade_result', function(data) {
        if (typeof handleTradeResult === 'function') {
            handleTradeResult(data);
        }
    });
    
    socket.on('connect_error', function(error) {
        console.error('Connection error:', error);
        updateConnectionStatus(false);
    });
}

// Update connection status indicator
function updateConnectionStatus(connected) {
    const statusElement = document.getElementById('connection-status');
    if (statusElement) {
        statusElement.textContent = connected ? 'Connected' : 'Disconnected';
        statusElement.className = connected ? 'badge bg-success' : 'badge bg-danger';
    }
}

// Update market data in tables
function updateMarketData(priceData) {
    const marketDataTable = document.getElementById('market-data');
    if (!marketDataTable) return;
    
    const tokens = Object.keys(priceData);
    if (tokens.length === 0) return;
    
    marketDataTable.innerHTML = tokens.map(symbol => {
        const tokenData = priceData[symbol];
        const changeClass = (tokenData.price_change_24h || 0) >= 0 ? 'text-success' : 'text-danger';
        const changeIcon = (tokenData.price_change_24h || 0) >= 0 ? 'fa-arrow-up' : 'fa-arrow-down';
        
        return `
            <tr>
                <td>
                    <strong>${symbol}</strong>
                    <br>
                    <small class="text-muted">${tokenData.mint_address ? tokenData.mint_address.substring(0, 8) + '...' : ''}</small>
                </td>
                <td>
                    <strong>$${(tokenData.price || 0).toFixed(6)}</strong>
                </td>
                <td class="${changeClass}">
                    <i class="fas ${changeIcon} me-1"></i>
                    ${((tokenData.price_change_24h || 0).toFixed(2))}%
                </td>
                <td>
                    <small>$${formatLargeNumber(tokenData.volume_24h || 0)}</small>
                </td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="openQuickTrade('${symbol}', ${tokenData.price || 0})">
                        Trade
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

// Open quick trade modal
function openQuickTrade(symbol, currentPrice) {
    document.getElementById('trade-symbol').value = symbol;
    document.getElementById('display-symbol').value = symbol;
    document.getElementById('current-price').value = '$' + currentPrice.toFixed(6);
    
    // Set default price
    const priceInput = document.querySelector('#quickTradeModal input[name="price"]');
    if (priceInput) {
        priceInput.value = currentPrice.toFixed(6);
    }
    
    const modal = new bootstrap.Modal(document.getElementById('quickTradeModal'));
    modal.show();
}

// Execute quick trade
function executeQuickTrade() {
    const form = document.getElementById('quick-trade-form');
    const formData = new FormData(form);
    
    const tradeData = {
        symbol: formData.get('symbol'),
        side: formData.get('side'),
        quantity: parseFloat(formData.get('quantity')),
        price: parseFloat(formData.get('price')),
        strategy: 'quick_trade'
    };
    
    // Validate data
    if (!tradeData.symbol || !tradeData.side || !tradeData.quantity || !tradeData.price) {
        showNotification('Please fill in all fields', 'error');
        return;
    }
    
    if (tradeData.quantity <= 0 || tradeData.price <= 0) {
        showNotification('Quantity and price must be positive', 'error');
        return;
    }
    
    // Execute trade via WebSocket
    if (socket && isConnected) {
        socket.emit('execute_trade', tradeData);
    } else {
        // Fallback to HTTP API
        fetch('/api/trade', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(tradeData)
        })
        .then(response => response.json())
        .then(data => {
            handleTradeResult(data);
        })
        .catch(error => {
            console.error('Error executing trade:', error);
            showNotification('Error executing trade', 'error');
        });
    }
    
    // Close modal
    bootstrap.Modal.getInstance(document.getElementById('quickTradeModal')).hide();
}

// Reset portfolio
function resetPortfolio() {
    if (!confirm('Are you sure you want to reset your portfolio? This will delete all positions and trades.')) {
        return;
    }
    
    fetch('/api/reset-portfolio', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Portfolio reset successfully', 'success');
            // Refresh page data
            if (typeof loadPortfolioData === 'function') {
                loadPortfolioData();
            }
            location.reload();
        } else {
            showNotification('Error resetting portfolio: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error resetting portfolio:', error);
        showNotification('Error resetting portfolio', 'error');
    });
}

// Utility functions
function formatLargeNumber(num) {
    if (num >= 1e9) return (num / 1e9).toFixed(1) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(1) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(1) + 'K';
    return num.toFixed(0);
}

function showNotification(message, type = 'info') {
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-danger' : 'alert-info';
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass} alert-dismissible fade show position-fixed`;
    alert.style.cssText = 'top: 80px; right: 20px; z-index: 9999; min-width: 300px;';
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    setTimeout(() => {
        if (alert.parentNode) {
            alert.parentNode.removeChild(alert);
        }
    }, 5000);
}

// Make socket available globally
window.socket = socket;

// Initialize WebSocket when page loads
document.addEventListener('DOMContentLoaded', function() {
    initializeWebSocket();
});
