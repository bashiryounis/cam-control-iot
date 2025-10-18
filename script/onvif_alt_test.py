#!/usr/bin/env python3
from onvif import ONVIFCamera
import os

print("Testing alternative ONVIF configurations...\n")

# Test configurations
configs = [
    {"port": 80, "wsdl_dir": None, "desc": "Default WSDL"},
    {"port": 80, "wsdl_dir": "/usr/local/lib/python3.13/dist-packages/wsdl", "desc": "Explicit WSDL path"},
    {"port": 8000, "wsdl_dir": None, "desc": "Port 8000 Default"},
]

for i, config in enumerate(configs, 1):
    print(f"\n[Test {i}] {config['desc']}")
    print(f"  Port: {config['port']}")
    print(f"  WSDL: {config['wsdl_dir'] or 'default'}")
    
    try:
        if config['wsdl_dir']:
            cam = ONVIFCamera(
                '192.168.100.171',
                config['port'],
                'admin',
                'PSTC#100200300',
                config['wsdl_dir']
            )
        else:
            cam = ONVIFCamera(
                '192.168.100.171',
                config['port'],
                'admin',
                'PSTC#100200300'
            )
        
        # Try simple capability check first
        print("  Attempting GetCapabilities...")
        caps = cam.devicemgmt.GetCapabilities()
        print(f"  ✅ GetCapabilities SUCCESS")
        
        # Now try device info
        print("  Attempting GetDeviceInformation...")
        info = cam.devicemgmt.GetDeviceInformation()
        
        print(f"\n  🎉 SUCCESS!")
        print(f"  Model: {info.Model}")
        print(f"  Firmware: {info.FirmwareVersion}")
        break
        
    except Exception as e:
        print(f"  ❌ Failed: {str(e)[:100]}")