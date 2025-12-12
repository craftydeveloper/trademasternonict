from app import app
from routes import *

# Add health check endpoint for Render
@app.route('/healthz')
def health_check():
    return {'status': 'healthy', 'message': 'TradePro bot is running'}, 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
