import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import redis
import pandas as pd
import time

# --- Configuration ---
REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_KEY = 'bot_counts' # Must match the key in processor.py
# ---------------------

# Initialize Dash app
# Dash will automatically find the 'assets' folder and load 'style.css'
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div(
    # Use minHeight to fill the screen and auto to grow if needed
    # This, combined with the CSS file, fixes the white border
    style={'backgroundColor': '#111111', 'color': '#FFFFFF', 'fontFamily': 'Arial, sans-serif', 'minHeight': '100vh', 'height': 'auto', 'padding': '20px'},
    children=[
        html.H1(
            children='Real-Time Wikipedia Edits',
            style={'textAlign': 'center', 'color': '#AAAAFF'}
        ),

        # This is the new, animated "Data Flow" subtitle
        html.Div(className='data-flow-container', children=[
            html.Span('Wikipedia', className='flow-node'),
            html.Span('->', className='flow-arrow'), # <-- FIX
            html.Span('Kafka', className='flow-node'),
            html.Span('->', className='flow-arrow'), # <-- FIX
            html.Span('Spark', className='flow-node'),
            html.Span('->', className='flow-arrow'), # <-- FIX
            html.Span('Redis', className='flow-node'),
            html.Span('->', className='flow-arrow'), # <-- FIX
            html.Span('Dash', className='flow-node'),
        ]),
        
        # We will create two columns for the layout
        html.Div(className='row', style={'display': 'flex', 'flexWrap': 'wrap'}, children=[
            
            # Column 1: Pie Chart
            # *** LAYOUT FIX HERE ***
            # Use flex: 1 to make columns flexible and a smaller minWidth
            html.Div(style={'flex': 1, 'minWidth': '350px', 'padding': '10px'}, children=[
                dcc.Graph(id='live-pie-chart', style={'height': '60vh'}),
            ]),
            
            # Column 2: Live Text Explanation
            # *** LAYOUT FIX HERE ***
            # Use flex: 1 to make columns flexible and a smaller minWidth
            html.Div(style={'flex': 1, 'minWidth': '350px', 'padding': '20px', 'backgroundColor': '#222222', 'borderRadius': '10px'}, children=[
                html.H3('Live Data Summary', style={'borderBottom': '1px solid #444', 'paddingBottom': '10px'}),
                
                # This Div will be updated by our callback
                html.Div(id='live-update-text', style={'fontSize': '18px', 'lineHeight': '1.6'}),
                
                # This new Div will hold the dynamic summary sentence
                html.Div(id='live-summary-sentence', className='live-summary-text')
            ])
        ]),

        # This component "ticks" every 1000ms (1 second)
        # and triggers the @app.callback function
        dcc.Interval(
            id='interval-component',
            interval=1*1000, # in milliseconds
            n_intervals=0
        )
    ]
)

# This is the "callback" function.
# It is triggered by the 'interval-component'
# We now have THREE Outputs
@app.callback(
    [Output('live-pie-chart', 'figure'),
     Output('live-update-text', 'children'),
     Output('live-summary-sentence', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    try:
        # Connect to our local Redis instance
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        
        # Get the counts from the Redis hash
        data = r.hgetall(REDIS_KEY) # e.g., {'Bot': '123', 'Human': '456'}
        
        if not data:
            # If Redis key is empty, show waiting messages
            waiting_figure = {
                'data': [],
                'layout': go.Layout(
                    title='Waiting for data from Spark...',
                    plot_bgcolor='#111111',
                    paper_bgcolor='#111111',
                    font={'color': '#FFFFFF'}
                )
            }
            waiting_text = "Waiting for the first batch of data from Spark..."
            waiting_summary = ""
            return waiting_figure, waiting_text, waiting_summary

        # --- Create Figure (same as before) ---
        df = pd.DataFrame({
            'Edit Type': data.keys(),
            'Count': [int(c) for c in data.values()]
        })
        
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=df['Edit Type'],
                    values=df['Count'],
                    hole=.3,
                    pull=[0.05 if l == 'Bot' else 0 for l in df['Edit Type']]
                )
            ]
        )
        
        fig.update_layout(
            title_text='Live Bot vs. Human Edits Breakdown',
            template='plotly_dark',
            plot_bgcolor='rgba(0,0,0,0)', # Transparent background
            paper_bgcolor='rgba(0,0,0,0)', # Transparent background
            legend_title_text='Edit Type'
        )
        
        # --- Create New Live Text ---
        bot_count = int(data.get('Bot', 0))
        human_count = int(data.get('Human', 0))
        total_count = bot_count + human_count
        
        bot_percent = (bot_count / total_count * 100) if total_count > 0 else 0
        human_percent = (human_count / total_count * 100) if total_count > 0 else 0

        # We create a list of styled components (html.P, html.Br)
        live_text = [
            html.P(f"Processing Batch: {n}"),
            html.Br(),
            html.P(f"Total Edits Processed: {total_count:,}"),
            html.P(f"Human Edits: {human_count:,} ({human_percent:.1f}%)"),
            html.P(f"Bot Edits: {bot_count:,} ({bot_percent:.1f}%)"),
            html.Br(),
            html.P(f"Last update: {time.strftime('%Y-%m-%d %H:%M:%S')}", style={'fontSize': '14px', 'color': '#888'})
        ]
        
        # --- Create your new dynamic summary sentence ---
        live_summary = f"In the current batch, {total_count} edits are being processed on Wikipedia by {human_count} human(s) and {bot_count} bot(s). These numbers update in real-time."
        
        # Return all three outputs
        return fig, live_text, live_summary

    except Exception as e:
        print(f"Error updating chart: {e}")
        # Return error messages for all outputs
        error_fig = {'data': [], 'layout': go.Layout(title=f'Error: {e}', plot_bgcolor='#111111', paper_bgcolor='#111111', font={'color': 'red'})}
        error_text = f"Error: {e}"
        error_summary = f"Error: {e}"
        return error_fig, error_text, error_summary

# --- Main execution ---
if __name__ == '__main__':
    try:
        # Test Redis connection on startup
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.ping()
        print("Connected to Redis.")
    except Exception as e:
        print(f"CRITICAL: Could not connect to Redis. Is it running in Docker?")
        print(f"Error: {e}")
        exit(1)

    print(f"Starting Dash server on http://127.0.0.1:8050/")
    
    # Use app.run, which is the correct method for this version of Dash
    app.run(debug=True, port=8050)

