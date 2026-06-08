import requests

urls = [
    "https://piston.kalkis.me/api/v2/execute",
    "https://execution.piston.engineer/api/v2/execute",
    "https://piston.sh/api/v2/execute",
    "https://api.pylex.me/piston/v2/execute"
]

payload = {
    "language": "python",
    "version": "3.10.0",
    "files": [{"content": "print('test')"}]
}

for url in urls:
    try:
        print(f"Testing {url}...")
        response = requests.post(url, json=payload, timeout=5)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print(f"Success! Result: {response.text}")
            break
    except Exception as e:
        print(f"Failed: {e}")
