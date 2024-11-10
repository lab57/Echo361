import requests
import time
import os
import base64

class ZoomMonitor:
    def __init__(self, account_id, client_id, client_secret):
        self.account_id = account_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.access_token = None
        self.token_expiry = 0
        
    def get_access_token(self):
        """Get or refresh access token"""
        if self.access_token and time.time() < self.token_expiry - 60:
            return self.access_token
            
        auth_url = "https://zoom.us/oauth/token"
        auth_string = f"{self.client_id}:{self.client_secret}"
        auth_bytes = base64.b64encode(auth_string.encode('ascii')).decode('ascii')
        
        headers = {
            'Authorization': f'Basic {auth_bytes}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'account_credentials',
            'account_id': self.account_id
        }
        
        response = requests.post(auth_url, headers=headers, data=data)
        if response.status_code == 200:
            token_data = response.json()
            self.access_token = token_data['access_token']
            self.token_expiry = time.time() + token_data['expires_in']
            return self.access_token
        else:
            raise Exception(f"Token request failed: {response.status_code} - {response.text}")

    def get_meeting_status(self, meeting_id):
        """Check basic meeting status"""
        headers = {
            'Authorization': f'Bearer {self.get_access_token()}',
            'Content-Type': 'application/json'
        }
        
        endpoint = f"https://api.zoom.us/v2/meetings/{meeting_id}"
        print(f"Checking endpoint: {endpoint}")
        
        response = requests.get(endpoint, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Failed to get meeting status: {response.status_code} - {response.text}")
            return None

def main():
    # Load credentials from environment
    account_id = os.getenv('ACTID')
    client_id = os.getenv('CLID')
    client_secret = os.getenv('CLSECRET')
    meeting_id = os.getenv('ZOOM_MEETING_ID')
    
    if not all([account_id, client_id, client_secret, meeting_id]):
        print("Missing required environment variables!")
        print("Please set: ACTID, CLID, CLSECRET, ZOOM_MEETING_ID")
        return
    
    monitor = ZoomMonitor(account_id, client_id, client_secret)
    
    print(f"Starting monitor for meeting {meeting_id}")
    print("Press Ctrl+C to stop")
    
    try:
        # First, let's just see what meeting data we can access
        meeting_data = monitor.get_meeting_status(meeting_id)
        print("\nFull meeting data available:")
        print(meeting_data)
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()