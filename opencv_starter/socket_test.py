import requests
import time

# NodeMCU IP address (replace with your NodeMCU's IP)
node_mcu_ip = "http://192.168.10.78"  # Replace with your NodeMCU's local IP

def send_command(command):
    url = f"{node_mcu_ip}/{command}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print(f"Command '{command}' sent successfully")
        else:
            print(f"Failed to send command '{command}'")
    except Exception as e:
        print(f"Error: {e}")
while True:
# Test commands
    send_command("motor1/forward")
    
    send_command("motor2/forward")
    time.sleep(3)
    send_command("stop")
'''   send_command("motor2/forward")
    time.sleep(3)
    send_command("motor2/backward")
    time.sleep(3)
    send_command("stop") '''
