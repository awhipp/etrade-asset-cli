"""
This module implements a web UI for the SPY strategy using Flask.
It displays call and put option metrics, and straddle details with auto-refresh.
"""

import threading
import time
import webbrowser
import json
from flask import Flask, render_template, jsonify
from flask_cors import CORS

class StrategyWebUI:
    """
    A class to implement the web UI for displaying SPY strategy results
    """
    
    def __init__(self, spy_strategy):
        """
        Initialize the web UI with the SPY strategy
        
        Args:
            spy_strategy: An instance of SpyStrategy
        """
        self.spy_strategy = spy_strategy
        self.app = Flask(__name__, template_folder='templates')
        CORS(self.app)
        self.data_lock = threading.Lock()
        self.latest_data = None
        self.running = False
        self.refresh_interval = 10  # seconds
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register Flask routes"""
        
        @self.app.route('/')
        def index():
            """Render the main UI page"""
            return render_template('spy_strategy.html')
        
        @self.app.route('/api/strategy-data')
        def get_strategy_data():
            """API endpoint to get the latest strategy data"""
            with self.data_lock:
                if self.latest_data:
                    return jsonify(self.latest_data)
                return jsonify({"status": "initializing"})
    
    def _update_strategy_data(self):
        """Update strategy data at regular intervals"""
        while self.running:
            try:
                # Run the strategy to get fresh data
                data = self.spy_strategy.run_strategy()
                
                # Convert to a JSON-serializable format
                formatted_data = self._format_data_for_json(data)
                
                # Update the latest data
                with self.data_lock:
                    self.latest_data = formatted_data
            except Exception as e:
                print(f"Error updating strategy data: {e}")
            
            # Wait for the next update
            time.sleep(self.refresh_interval)
    
    def _format_data_for_json(self, data):
        """Format strategy data for JSON serialization"""
        if not data:
            return {"status": "error", "message": "No data available"}
        
        # Create a deep copy to avoid modifying the original data
        formatted = {
            "timestamp": int(time.time()),
            "spy_price": self.spy_strategy.spy_price,
            "expiry_date": data.get("expiry_date", "Unknown"),
            "days_to_expiry": data.get("days_to_expiry", "Unknown"),
            "call": data.get("call", {}),
            "put": data.get("put", {}),
            "straddle": data.get("straddle", {})
        }
        
        return formatted
    
    def start(self, port=5000):
        """
        Start the web UI server
        
        Args:
            port: The port to run the server on
        """
        self.running = True
        
        # Start the data update thread
        update_thread = threading.Thread(target=self._update_strategy_data)
        update_thread.daemon = True
        update_thread.start()
        
        # Open the browser
        webbrowser.open(f"http://localhost:{port}/")
        
        # Start the Flask app
        try:
            self.app.run(debug=False, host='localhost', port=port)
        finally:
            self.running = False