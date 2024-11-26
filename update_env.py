import requests
import os
from dotenv import load_dotenv

def update_ngrok_url():
    try:
        # Lấy URL ngrok
        ngrok_api = requests.get("http://localhost:4040/api/tunnels").json()
        ngrok_url = ngrok_api["tunnels"][0]["public_url"]
        
        # Đọc file .env
        with open('.env', 'r') as file:
            lines = file.readlines()
        
        # Cập nhật URL
        with open('.env', 'w') as file:
            for line in lines:
                if 'PAYOS_RETURN_URL' in line:
                    file.write(f'PAYOS_RETURN_URL={ngrok_url}/payment/return\n')
                elif 'PAYOS_CANCEL_URL' in line:
                    file.write(f'PAYOS_CANCEL_URL={ngrok_url}/payment/cancel\n')
                else:
                    file.write(line)
                    
        print(f"Đã cập nhật URL ngrok: {ngrok_url}")
    except Exception as e:
        print(f"Lỗi khi cập nhật URL: {str(e)}")

if __name__ == "__main__":
    update_ngrok_url()
