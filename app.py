import requests
import re
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from tqdm import tqdm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode='eventlet')  # Use async_mode='eventlet' for compatibility

def fetch_m3u_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text.splitlines()
    except requests.RequestException as e:
        print(f"Error fetching M3U from URL: {e}")
        return []

def test_iptv_channels(m3u_lines):
    working_channels = []
    failed_channels = []
    channel_info = ""
    total_channels = sum(1 for line in m3u_lines if line.startswith('http'))
    progress = 0
    
    for line in tqdm(m3u_lines, desc="Testing channels", unit="line"):
        line = line.strip()
        if line.startswith('#EXTINF'):
            channel_info = line
        elif line.startswith('http'):
            try:
                response = requests.get(line, timeout=10)
                if response.status_code == 200:
                    channel_name_match = re.search(r',(.+)$', channel_info)
                    if channel_name_match:
                        channel_name = channel_name_match.group(1)
                        working_channels.append({'name': channel_name, 'url': line})
                else:
                    failed_channels.append({'name': channel_name, 'url': line})
            except requests.RequestException as e:
                channel_name_match = re.search(r',(.+)$', channel_info)
                if channel_name_match:
                    channel_name = channel_name_match.group(1)
                    failed_channels.append({'name': channel_name, 'url': line, 'error': str(e)})
            progress += 1
            socketio.emit('progress', {'progress': (progress / total_channels) * 100}, broadcast=True)
    
    return working_channels, failed_channels

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')

@socketio.on('check_channels')
def handle_check_channels(data):
    m3u_url = data['m3u_url']
    m3u_lines = fetch_m3u_from_url(m3u_url)
    if m3u_lines:
        working_channels, failed_channels = test_iptv_channels(m3u_lines)
        emit('channels', {'working_channels': working_channels, 'failed_channels': failed_channels}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=8080, debug=True)  # Adjust the host and port for Vercel
