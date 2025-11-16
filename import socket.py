import socket
import cv2
import numpy as np
import time

UDP_IP = "192.168.0.110"  # Your PC IP
UDP_PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((UDP_IP, UDP_PORT))

frame_data = bytearray()

recording = False
video_writer = None

while True:
    data, addr = sock.recvfrom(1500)
    frame_data.extend(data)

    # End of JPEG frame (last packet < 1400 bytes)
    if len(data) < 1400:
        nparr = np.frombuffer(frame_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if img is not None:
            cv2.imshow("ESP32 Camera Stream", img)

            # --- SAVE VIDEO FRAME IF RECORDING ---
            if recording:
                video_writer.write(img)

        frame_data = bytearray()

    key = cv2.waitKey(1) & 0xFF
    
    # Quit
    if key == ord('q'):
        break

    # Start Recording
    if key == ord('r') and not recording:
        print("➡️ Recording started")
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        filename = f"esp32_record_{int(time.time())}.mp4"
        video_writer = cv2.VideoWriter(filename, fourcc, 20.0, (img.shape[1], img.shape[0]))
        recording = True

    # Stop Recording
    if key == ord('s') and recording:
        print("⏹ Recording stopped")
        recording = False
        video_writer.release()

cv2.destroyAllWindows()
sock.close()
