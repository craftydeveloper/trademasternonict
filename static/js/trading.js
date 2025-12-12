// Trading page JavaScript
let currentChart;
let selectedSymbol = '';
let currentPrices = {};

document.addEventListener('DOMContentLoaded', function() {
    initializeTradingPage();
    setupFormHandlers();
    loadCurrentPrices();
    
    // Initialize price chart
    initializePriceChart();
});

function initializeTradingPage() {
    // Load portfolio balance
    fetch('/api/portfolio/summary')
        .then(response => response.json())
        .then(data => {
            document.getElementById('available-balance').textContent = formatCurrency(data.cash_balance || 0);
        })
        .catch(error => {
            console.error('Error loading balance:', error);
        });
    
    // Load recent trades
    loadTradeHistory();
}

function setupFormHandlers() {
    const tradingForm = document.getElementById('trading-form');
    const symbolSelect = document.getElementById('symbol-select');
    const quantityInput = document.querySelector('input[name="quantity"]');
    const priceInput = document.querySelector('input[name="price"]');
    
    // Handle symbol selection
    symbolSelect.addEventListener('change', function() {
        selectedSymbol = this.value;
        if (selectedSymbol && currentPrices[selectedSymbol]) {
            const currentPrice = currentPrices[selectedSymbol].price;
            document.getElementById('current-price').textContent = '$' + currentPrice.toFixed(6);
            priceInput.value = currentPrice.toFixed(6);
            updateChart(selectedSymbol);
        }
        updateOrderValue();
    });
    
    // Handle quantity and price changes
    quantityInput.addEventListener('input', updateOrderValue);
    priceInput.addEventListener('input', updateOrderValue);
    
    // Handle form submission
    tradingForm.addEventListener('submit', function(e) {
        e.preventDefault();
        executeTrade();
    });
}

function loadCurrentPrices() {
    fetch('/api/tokens/prices')
        .then(response => response.json())
        .then(data => {
            currentPrices = data;
            updatePriceDisplays();
        })
        .catch(error => {
            console.error('Error loading prices:', error);
        });
}

function updatePriceDisplays() {
    if (selectedSymbol && currentPrices[selectedSymbol]) {
        const price = currentPrices[selectedSymbol].price;
        document.getElementById('current-price').textContent = '$' + price.toFixed(6);
        document.getElementById('price-input').value = price.toFixed(6);
        updateOrderValue();
    }
    
    // Update order book (simulated)
    updateOrderBook();
}

function updateOrderValue() {
    const quantity = parseFloat(document.querySelector('input[name="quantity"]').value) || 0;
    const price = parseFloat(document.querySelector('input[name="price"]').value) || 0;
    const total = quantity * price;
    
    document.getElementById('order-value').value = formatCurrency(total);
}

function useCurrentPrice() {
    if (selectedSymbol && currentPrices[selectedSymbol]) {
        const currentPrice = currentPrices[selectedSymbol].price;
        document.getElementById('price-input').value = currentPrice.toFixed(6);
        updateOrderValue();
    }
}

function executeTrade() {
    const form = document.getElementById('trading-form');
    const formData = new FormData(form);
    
    const tradeData = {
        symbol: formData.get('symbol'),
        side: formData.get('side'),
        quantity: parseFloat(formData.get('quantity')),
        price: parseFloat(formData.get('price')),
        strategy: 'manual'
    };
    
    // Validate
    if (!tradeData.symbol) {
        showNotification('Please select a symbol', 'error');
        return;
    }
    
    if (tradeData.quantity <= 0) {
        showNotification('Quantity must be greater than 0', 'error');
        return;
    }
    
    if (tradeData.price <= 0) {
        showNotification('Price must be greater than 0', 'error');
        return;
    }
    
    // Show loading state
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.innerHTML;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Executing...';
    submitBtn.disabled = true;
    
    // Execute trade
    fetch('/api/trade', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(tradeData)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showTradeResult(data);
            form.reset();
            loadTradeHistory();
            initializeTradingPage(); // Refresh balance
        } else {
            showNotification('Trade failed: ' + data.error, 'error');
        }
    })
    .catch(error => {
        console.error('Error executing trade:', error);
        showNotification('Error executing trade', 'error');
    })
    .finally(() => {
        submitBtn.innerHTML = originalText;
        submitBtn.disabled = false;
    });
}

function showTradeResult(result) {
    const trade = result.trade;
    const modal = document.getElementById('tradeConfirmModal');
    const content = document.getElementById('trade-result-content');
    
    const pnlDisplay = trade.pnl !== 0 ? `
        <div class="mb-2">
            <strong>P&L:</strong> 
            <span class="${trade.pnl >= 0 ? 'text-success' : 'text-danger'}">
                ${formatCurrency(trade.pnl)}
            </span>
        </div>
    ` : '';
    
    content.innerHTML = `
        <div class="alert alert-success">
            <h6><i class="fas fa-check-circle me-2"></i>Trade Executed Successfully</h6>
        </div>
        <div class="mb-2"><strong>Symbol:</strong> ${trade.symbol}</div>
        <div class="mb-2"><strong>Side:</strong> 
            <span class="badge ${trade.side === 'BUY' ? 'bg-success' : 'bg-danger'}">
                ${trade.side}
            </span>
        </div>
        <div class="mb-2"><strong>Quantity:</strong> ${formatNumber(trade.quantity)}</div>
        <div class="mb-2"><strong>Price:</strong> ${formatCurrency(trade.price)}</div>
        <div class="mb-2"><strong>Total Value:</strong> ${formatCurrency(trade.total_value)}</div>
        <div class="mb-2"><strong>Fee:</strong> ${formatCurrency(trade.fee)}</div>
        ${pnlDisplay}
        <div class="mb-2"><strong>Status:</strong> 
            <span class="badge bg-success">${trade.status.toUpperCase()}</span>
        </div>
    `;
    
    const bootstrapModal = new bootstrap.Modal(modal);
    bootstrapModal.show();
}

function loadTradeHistory() {
    fetch('/api/trades?limit=10')
        .then(response => response.json())
        .then(trades => {
            const tbody = document.getElementById('trade-history');
            if (!tbody) return;
            
            if (trades.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No trades yet</td></tr>';
                return;
            }
            
            tbody.innerHTML = trades.map(trade => `
                <tr>
                    <td><small>${formatDateTime(trade.executed_at)}</small></td>
                    <td>
                        <span class="badge ${trade.side === 'BUY' ? 'bg-success' : 'bg-danger'}">
                            ${trade.side}
                        </span>
                    </td>
                    <td>${formatNumber(trade.quantity)}</td>
                    <td>${formatCurrency(trade.price)}</td>
                    <td>${formatCurrency(trade.total_value)}</td>
                </tr>
            `).join('');
        })
        .catch(error => {
            console.error('Error loading trade history:', error);
        });
}

function initializePriceChart() {
    const ctx = document.getElementById('price-chart').getContext('2d');
    currentChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Price',
                data: [],
                borderColor: 'rgba(13, 110, 253, 1)',
                backgroundColor: 'rgba(13, 110, 253, 0.1)',
                fill: false,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toFixed(6);
                        }
                    }
                }
            },
            plugins: {
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return 'Price: $' + context.parsed.y.toFixed(6);
                        }
                    }
                }
            }
        }
    });
}

function updateChart(symbol) {
    if (!currentChart) return;
    
    fetch(`/api/market-data/${symbol}`)
        .then(response => response.json())
        .then(data => {
            if (data.length === 0) {
                // If no historical data, create a simple chart with current price
                const currentPrice = currentPrices[symbol]?.price || 0;
                const now = new Date();
                const labels = [];
                const prices = [];
                
                for (let i = 9; i >= 0; i--) {
                    const time = new Date(now.getTime() - i * 60000); // 1 minute intervals
                    labels.push(time.toLocaleTimeString());
                    prices.push(currentPrice + (Math.random() - 0.5) * currentPrice * 0.01); // Add small random variation
                }
                
                currentChart.data.labels = labels;
                currentChart.data.datasets[0].data = prices;
                currentChart.data.datasets[0].label = `${symbol} Price`;
            } else {
                currentChart.data.labels = data.map(d => new Date(d.timestamp).toLocaleTimeString());
                currentChart.data.datasets[0].data = data.map(d => d.price);
                currentChart.data.datasets[0].label = `${symbol} Price`;
            }
            
            currentChart.update();
        })
        .catch(error => {
            console.error('Error loading chart data:', error);
        });
}

function updateOrderBook() {
    // Simulate order book data
    if (!selectedSymbol || !currentPrices[selectedSymbol]) return;
    
    const currentPrice = currentPrices[selectedSymbol].price;
    const spread = currentPrice * 0.001; // 0.1% spread
    
    // Generate simulated bids and asks
    const bidsData = document.getElementById('bids-data');
    const asksData = document.getElementById('asks-data');
    
    if (bidsData && asksData) {
        let bidsHtml = '';
        let asksHtml = '';
        
        // Generate 5 bid levels
        for (let i = 0; i < 5; i++) {
            const bidPrice = currentPrice - spread - (i * spread * 0.5);
            const bidQuantity = Math.random() * 1000 + 100;
            bidsHtml += `
                <div class="d-flex justify-content-between">
                    <span class="text-success">$${bidPrice.toFixed(6)}</span>
                    <span>${bidQuantity.toFixed(0)}</span>
                </div>
            `;
        }
        
        // Generate 5 ask levels
        for (let i = 0; i < 5; i++) {
            const askPrice = currentPrice + spread + (i * spread * 0.5);
            const askQuantity = Math.random() * 1000 + 100;
            asksHtml += `
                <div class="d-flex justify-content-between">
                    <span class="text-danger">$${askPrice.toFixed(6)}</span>
                    <span>${askQuantity.toFixed(0)}</span>
                </div>
            `;
        }
        
        bidsData.innerHTML = bidsHtml;
        asksData.innerHTML = asksHtml;
    }
}

function calculatePositionSize() {
    const riskPercentage = parseFloat(document.getElementById('risk-percentage').value) || 2;
    const stopLossPercentage = parseFloat(document.getElementById('stop-loss-percentage').value) || 5;
    
    // Get portfolio balance
    fetch('/api/portfolio/summary')
        .then(response => response.json())
        .then(data => {
            const balance = data.cash_balance || 0;
            const riskAmount = balance * (riskPercentage / 100);
            
            if (selectedSymbol && currentPrices[selectedSymbol]) {
                const currentPrice = currentPrices[selectedSymbol].price;
                const stopLossPrice = currentPrice * (1 - stopLossPercentage / 100);
                const riskPerToken = currentPrice - stopLossPrice;
                const suggestedQuantity = riskAmount / riskPerToken;
                
                document.getElementById('position-size-result').innerHTML = `
                    <div class="text-success">
                        <strong>Suggested Quantity: ${suggestedQuantity.toFixed(6)}</strong>
                        <br>
                        <small>Risk Amount: ${formatCurrency(riskAmount)}</small>
                        <br>
                        <small>Stop Loss: ${formatCurrency(stopLossPrice)}</small>
                    </div>
                `;
                
                // Auto-fill the quantity field
                document.querySelector('input[name="quantity"]').value = suggestedQuantity.toFixed(6);
                updateOrderValue();
            }
        })
        .catch(error => {
            console.error('Error calculating position size:', error);
        });
}

function changeTimeframe(timeframe) {
    // Update active button
    document.querySelectorAll('.btn-group .btn').forEach(btn => {
        btn.classList.remove('active');
    });
    event.target.classList.add('active');
    
    // In a real implementation, you would fetch different timeframe data
    if (selectedSymbol) {
        updateChart(selectedSymbol);
    }
}

// Handle price updates from WebSocket
function handlePriceUpdate(priceData) {
    currentPrices = { ...currentPrices, ...priceData };
    updatePriceDisplays();
    
    // Update chart if symbol is selected
    if (selectedSymbol && priceData[selectedSymbol]) {
        // Add new price point to chart
        const chart = currentChart;
        if (chart && chart.data.labels.length > 0) {
            const now = new Date().toLocaleTimeString();
            const newPrice = priceData[selectedSymbol].price;
            
            // Keep only last 50 points
            if (chart.data.labels.length >= 50) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }
            
            chart.data.labels.push(now);
            chart.data.datasets[0].data.push(newPrice);
            chart.update('none');
        }
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
    return new Date(dateString).toLocaleString();
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
