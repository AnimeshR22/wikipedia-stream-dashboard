import requests
import json
import time

STREAM_URL = 'https://stream.wikimedia.org/v2/stream/recentchange'

# We must identify ourselves to Wikipedia's servers
USER_AGENT = 'MyDataProject/1.0 (Python-Requests; student-project)'
HEADERS = {
    'User-Agent': USER_AGENT,
    'Accept': 'application/json' 
}

print(f"Attempting to connect to Wikipedia stream at {STREAM_URL}...")
print("This will test your network connection directly.")

try:
    # Use requests.get with stream=True to open a persistent connection
    with requests.get(STREAM_URL, headers=HEADERS, stream=True, timeout=10) as r:
        
        # Check for connection errors (like 403, 404, 500)
        r.raise_for_status() 
        
        print("\nSUCCESS! Connection established. Waiting for data...")
        print("(If you see this, your connection is working. Lines will appear below.)\n")
        
        # iter_lines() will wait for new data to arrive on the stream
        for line in r.iter_lines():
            if line:
                # The raw line is a 'bytes' object, so we decode it
                line_str = line.decode('utf-8')
                
                # Real data lines start with 'data: '
                if line_str.startswith('data: '):
                    print(f"RECEIVED DATA: {line_str[:150]}...") # Print first 150 chars
                else:
                    # Other lines are comments or keep-alives (like ':')
                    print(f"Received non-data line: {line_str}")

except requests.exceptions.Timeout:
    print(f"\n--- ERROR: Connection Timed Out ---")
    print("The connection was made, but no data was received for 10 seconds.")
    print("This strongly points to a FIREWALL, ANTIVIRUS, or VPN blocking the stream.")
except requests.exceptions.RequestException as e:
    print(f"\n--- ERROR ---")
    print(f"Failed to connect: {e}")
    print("This could be a firewall, antivirus, or VPN issue blocking the initial connection.")
except KeyboardInterrupt:
    print("\nStream test stopped by user.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")
