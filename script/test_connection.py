#!/usr/bin/env python3
"""
🔍 ONVIF Camera Discovery & Connection Tester
---------------------------------------------
Performs:
  1. WS-Discovery (find ONVIF cameras on the LAN)
  2. Direct connection test to a known IP and port
  3. Device info, capabilities, and network interfaces

✅ Handles missing WSDL files automatically.
✅ Works with digest-auth cameras (Hikvision, Dahua, etc.).
"""

import os
import time
import sys
from wsdiscovery.discovery import ThreadedWSDiscovery as WSDiscovery
from onvif import ONVIFCamera

# ───────────────────────────────
# Configuration
# ───────────────────────────────
CAMERA_IP = "192.168.100.171"
USERNAME = "admin"
PASSWORD = "PSTC#100200300"
WSDL_DIR = "/home/pstc/onvif_wsdl"
PORTS_TO_TRY = [80, 8000, 8080, 8899, 554]

# ───────────────────────────────
# Ensure WSDL files are available
# ───────────────────────────────
def ensure_wsdl_dir():
    if not os.path.exists(WSDL_DIR) or not any(f.endswith(".wsdl") for f in os.listdir(WSDL_DIR)):
        print(f"📦 WSDL files not found in {WSDL_DIR}")
        print("   → Downloading from GitHub...")
        os.makedirs(WSDL_DIR, exist_ok=True)
        os.system(
            f"git clone https://github.com/FalkTannhaeuser/python-onvif-zeep.git /tmp/onvif_temp && "
            f"cp -r /tmp/onvif_temp/wsdl/* {WSDL_DIR}/ && rm -rf /tmp/onvif_temp"
        )
    if not any(f.endswith(".wsdl") for f in os.listdir(WSDL_DIR)):
        print("❌ Failed to download WSDL files. Please check network connection.")
        sys.exit(1)
    print(f"✅ Using WSDL files from: {WSDL_DIR}")

# ───────────────────────────────
# Step 1: Discover ONVIF devices
# ───────────────────────────────
def discover_devices():
    print("=" * 70)
    print("🔍 ONVIF Device Discovery")
    print("=" * 70)

    try:
        wsd = WSDiscovery()
        wsd.start()
        print("Searching for ONVIF devices (wait 5s)...")
        time.sleep(5)
        services = wsd.searchServices()
        wsd.stop()

        print(f"\n✅ Found {len(services)} device(s):\n")
        for i, s in enumerate(services, 1):
            print(f"📹 Device #{i}:")
            for addr in s.getXAddrs():
                print(f"   URL: {addr}")
            if s.getScopes():
                print(f"   Scopes: {[str(sc) for sc in s.getScopes()]}")
            print()

    except Exception as e:
        print(f"⚠️  Discovery failed: {e}")
        print("   (Discovery may be disabled on the camera)\n")

# ───────────────────────────────
# Step 2: Connect to camera
# ───────────────────────────────
def connect_camera():
    print("=" * 70)
    print("🔌 Testing direct connection")
    print("=" * 70)

    success = False
    for port in PORTS_TO_TRY:
        print(f"\nTrying port {port} ...")
        try:
            cam = ONVIFCamera(CAMERA_IP, port, USERNAME, PASSWORD, wsdl_dir=WSDL_DIR)
            info = cam.devicemgmt.GetDeviceInformation()
            print(f"\n✅ SUCCESS on port {port}!")
            print(f"   Manufacturer : {info.Manufacturer}")
            print(f"   Model        : {info.Model}")
            print(f"   Firmware     : {info.FirmwareVersion}")
            print(f"   Serial       : {info.SerialNumber}")
            print(f"   Hardware ID  : {info.HardwareId}")

            # Capabilities
            print("\n🔧 Capabilities:")
            caps = cam.devicemgmt.GetCapabilities()
            for cap_name in ["PTZ", "Media", "Events", "Imaging"]:
                cap = getattr(caps, cap_name, None)
                print(f"   {cap_name:<8}: {'✅ ' + cap.XAddr if cap else '❌ Not available'}")

            # Network
            print("\n🌐 Network Interfaces:")
            for iface in cam.devicemgmt.GetNetworkInterfaces():
                name = getattr(iface.Info, 'Name', 'Unknown')
                ipv4 = iface.IPv4.Config.Manual[0].Address if iface.IPv4.Config.Manual else "DHCP"
                print(f"   Interface {name}: {ipv4}")

            print("\n" + "=" * 70)
            print(f"🎉 Connected successfully on port {port}")
            print("=" * 70)
            success = True
            break

        except Exception as e:
            err = str(e)
            print(f"   ❌ Failed: {err}")
            if "401" in err or "Unauthorized" in err:
                print("   💡 Authentication failed – check username/password or ONVIF user settings.")
            elif "Connection refused" in err:
                print("   💡 Port closed or ONVIF service not running.")
            elif "timed out" in err:
                print("   💡 Connection timeout – camera not responding on this port.")
            elif "No such file" in err:
                print("   💡 Missing WSDL files. Run this script again to auto-download them.")

    if not success:
        print("\n❌ Could not connect on any tested port.")
        print("💡 Suggestions:")
        print("   1. Verify ONVIF is enabled in the camera web interface.")
        print("   2. Ensure correct ONVIF user credentials.")
        print("   3. Check port number (usually 80, 8000, or 8899).")
        print("   4. Ensure your computer and camera are on the same subnet.")
        print("   5. Reboot the camera after enabling ONVIF.\n")

# ───────────────────────────────
# Run everything
# ───────────────────────────────
if __name__ == "__main__":
    ensure_wsdl_dir()
    discover_devices()
    connect_camera()
    print("\n✅ Test complete!\n")
