// Dashboard-specific JavaScript
let portfolioData = {};
let marketPrices = {};

// Initialize dashboard
document.addEventListener('DOMContentLoaded', function() {
    loadDashboardData();
    
    // Set up periodic data refresh
    setInterval(loadDashboardData, 30000); // Refresh every 30 seconds
});

// Load all dashboard data
function loadDashboardData() {
    // Load portfolio summary
    fetch('/api/portfolio/summary')
        .then(response => response.json())
        .then(data => {
            portfolioData = data;
            updatePortfolioOverview(data);
            updatePositionsDisplay(data.positions || []);
            updateRecentTrades(data.recent_trades || []);
        })
        .catch(error => {
            console.error('Error loading portfolio data:', error);
            showNotification('Error loading portfolio data', 'error');
        });
    
    // Load market prices
    fetch('/api/tokens/prices')
        .then(response => response.json())
        .then(data => {
            marketPrices = data;
            updateMarketData(data);
        })
        .catch(error => {
            console.error('Error loading market data:', error);
        });
}

// Update portfolio overview cards
function updatePortfolioOverview(data) {
    if (!data.portfolio) return;
    
    document.getElementById('total-value').textContent = formatCurrency(data.total_value || 0);
    document.getElementById('cash-balance').textContent = formatCurrency(data.cash_balance || 0);
    
    const totalPnlElement = document.getElementById('total-pnl');
    const totalReturnElement = document.getElementById('total-return');
    
    const totalPnl = (data.portfolio.total_pnl || 0) + (data.unrealized_pnl || 0);
    const totalReturn = data.total_return || 0;
    
    totalPnlElement.textContent = formatCurrency(totalPnl);
    totalReturnElement.textContent = totalReturn.toFixed(2) + '%';
    
    // Update colors based on profit/loss
    totalPnlElement.className = totalPnl >= 0 ? 'text-success' : 'text-danger';
    totalReturnElement.className = totalReturn >= 0 ? 'text-success' : 'text-danger';
}

// Update positions display
function updatePositionsDisplay(positions) {
    const tbody = document.getElementById('positions-data');
    const noPositions = document.getElementById('no-positions');
    
    if (!positions || positions.length === 0) {
        tbody.innerHTML = '';
        if (noPositions) noPositions.style.display = 'block';
        return;
    }
    
    if (noPositions) noPositions.style.display = 'none';
    
    tbody.innerHTML = positions.map(position => {
        const pnlClass = position.unrealized_pnl >= 0 ? 'text-success' : 'text-danger';
        const pnlPercentClass = position.pnl_percentage >= 0 ? 'text-success' : 'text-danger';
        
        return `
            <tr>
                <td><strong>${position.symbol}</strong></td>
                <td>${formatNumber(position.quantity)}</td>
                <td>${formatCurrency(position.avg_entry_price)}</td>
                <td>${formatCurrency(position.current_price)}</td>
                <td>${formatCurrency(position.market_value)}</td>
                <td class="${pnlClass}">
                    ${formatCurrency(position.unrealized_pnl)}
                </td>
                <td class="${pnlPercentClass}">
                    ${position.pnl_percentage.toFixed(2)}%
                </td>
            </tr>
        `;
    }).join('');
}

// Update recent trades display
function updateRecentTrades(trades) {
    const tbody = document.getElementById('recent-trades');
    const noTrades = document.getElementById('no-trades');
    
    if (!trades || trades.length === 0) {
        tbody.innerHTML = '';
        if (noTrades) noTrades.style.display = 'block';
        return;
    }
    
    if (noTrades) noTrades.style.display = 'none';
    
    tbody.innerHTML = trades.map(trade => {
        const sideClass = trade.side === 'BUY' ? 'text-success' : 'text-danger';
        const pnlClass = trade.pnl >= 0 ? 'text-success' : 'text-danger';
        
        return `
            <tr>
                <td><small>${formatDateTime(trade.executed_at)}</small></td>
                <td><strong>${trade.symbol}</strong></td>
                <td class="${sideClass}">
                    <strong>${trade.side}</strong>
                </td>
                <td>${formatNumber(trade.quantity)}</td>
                <td>${formatCurrency(trade.price)}</td>
                <td>${formatCurrency(trade.total_value)}</td>
                <td class="${pnlClass}">
                    ${formatCurrency(trade.pnl)}
                </td>
            </tr>
        `;
    }).join('');
}

// Handle price updates from WebSocket
function handlePriceUpdate(priceData) {
    marketPrices = { ...marketPrices, ...priceData };
    updateMarketData(marketPrices);
}

// Handle portfolio updates from WebSocket
function handlePortfolioUpdate(data) {
    portfolioData = data;
    updatePortfolioOverview(data);
    updatePositionsDisplay(data.positions || []);
    updateRecentTrades(data.recent_trades || []);
}

// Handle trade results
function handleTradeResult(result) {
    if (result.success) {
        showNotification(`Trade executed successfully: ${result.trade.side} ${result.trade.quantity} ${result.trade.symbol}`, 'success');
        // Refresh dashboard data
        loadDashboardData();
    } else {
        showNotification(`Trade failed: ${result.error}`, 'error');
    }
}

// Utility functions
function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        minimumFractionDigits: 2,
        maximumFractionDigits: 6
    }).format(value || 0);
}

function formatNumber(value) {
    return new Intl.NumberFormat('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 6
    }).format(value || 0);
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}
