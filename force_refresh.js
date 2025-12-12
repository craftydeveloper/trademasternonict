// Force refresh trading signals display
(function() {
    'use strict';
    
    // Force clear all cached content
    function clearCachedContent() {
        const containers = ['top-trades-container', 'other-opportunities-container'];
        containers.forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.innerHTML = '<div class="text-center py-3"><div class="spinner-border text-info" role="status"></div><p class="mt-2">Loading fresh signals...</p></div>';
            }
        });
    }
    
    // Force load fresh signals
    function forceFreshSignals() {
        clearCachedContent();
        
        const cacheBuster = `t=${Date.now()}&r=${Math.random()}&v=${Math.floor(Math.random()*10000)}&fresh=true`;
        
        fetch(`/api/trading-signals?${cacheBuster}`, {
            cache: 'no-store',
            headers: {
                'Cache-Control': 'no-cache, no-store, must-revalidate',
                'Pragma': 'no-cache',
                'Expires': '0'
            }
        })
        .then(response => response.json())
        .then(data => {
            console.log('Force refresh - signals received:', data.count);
            
            if (data.signals && data.signals.length > 0) {
                // Update active signals counter
                const activeSignalsEl = document.getElementById('active-signals');
                if (activeSignalsEl) {
                    activeSignalsEl.textContent = data.signals.length;
                }
                
                // Force display fresh signals
                if (window.dashboard && window.dashboard.displayFastSignals) {
                    window.dashboard.displayFastSignals(data.signals);
                }
            }
        })
        .catch(error => console.error('Force refresh error:', error));
    }
    
    // Execute force refresh
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', forceFreshSignals);
    } else {
        forceFreshSignals();
    }
    
    // Check for cached display and force refresh if needed
    setTimeout(() => {
        const activeSignalsEl = document.getElementById('active-signals');
        const topContainer = document.getElementById('top-trades-container');
        
        if (activeSignalsEl && parseInt(activeSignalsEl.textContent) === 1 && 
            topContainer && topContainer.innerHTML.includes('ADA')) {
            console.log('Detected cached ADA display, forcing complete refresh...');
            window.location.href = window.location.pathname + '?refresh=' + Date.now();
        }
    }, 3000);
    
})();