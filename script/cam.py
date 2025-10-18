import cv2
import time
import urllib.parse

# Camera credentials and network info
username = "admin"
password = "PSTC#100200300"
ip = "192.168.100.171"
rtsp_port = 554

# URL-encode password (because '#' breaks the URL if not encoded)
encoded_password = urllib.parse.quote(password)

# RTSP main stream URL (channel 101)
rtsp_url = f"rtsp://{username}:{encoded_password}@{ip}:{rtsp_port}/Streaming/Channels/101"

print(f"\n🔍 Testing connection to Hikvision PTZ Camera: {ip}")
print(f"📡 RTSP URL: {rtsp_url}\n")

# Initialize the video capture
cap = cv2.VideoCapture(rtsp_url)

if not cap.isOpened():
    print("❌ Failed to connect to camera stream.")
    print("⚠️ Check network, credentials, or RTSP settings on the camera.")
    exit(1)

print("✅ Connection established successfully!")
print("📸 Receiving video frames... Press Ctrl+C to stop.\n")

frame_count = 0
start_time = time.time()

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("⚠️ Frame not received (stream interrupted or login failed).")
            break

        frame_count += 1
        # Print stats every 30 frames
        if frame_count % 30 == 0:
            elapsed = time.time() - start_time
            fps = frame_count / elapsed
            height, width, _ = frame.shape
            print(f"📈 Frame: {frame_count} | Resolution: {width}x{height} | Avg FPS: {fps:.2f}")

        # Uncomment to preview the stream in a window
        # cv2.imshow("Hikvision Camera Stream", frame)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

except KeyboardInterrupt:
    print("\n🛑 Stream stopped by user.")

finally:
    cap.release()
    cv2.destroyAllWindows()
    print("🔒 Connection closed.\n")
