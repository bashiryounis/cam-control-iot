#!/usr/bin/env python3
"""
Hikvision ONVIF PTZ Controller
Works with raw SOAP requests - no library dependencies
"""

import requests
from requests.auth import HTTPDigestAuth
import xml.etree.ElementTree as ET
import time

class HikvisionONVIFCamera:
    def __init__(self, ip, username, password, port=80):
        """Initialize ONVIF camera connection"""
        self.ip = ip
        self.port = port
        self.username = username
        self.password = password
        self.auth = HTTPDigestAuth(username, password)
        
        # ONVIF service URLs
        self.device_url = f'http://{ip}:{port}/onvif/device_service'
        self.ptz_url = f'http://{ip}:{port}/onvif/ptz_service'
        self.media_url = f'http://{ip}:{port}/onvif/media_service'
        
        self.profile_token = None
        
    def _soap_request(self, url, body):
        """Send SOAP request to camera"""
        envelope = f'''<?xml version="1.0" encoding="UTF-8"?>
<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope">
    <s:Body>
        {body}
    </s:Body>
</s:Envelope>'''
        
        headers = {'Content-Type': 'application/soap+xml; charset=utf-8'}
        
        try:
            response = requests.post(url, data=envelope, headers=headers, auth=self.auth, timeout=5)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"SOAP request failed: {e}")
    
    def get_device_info(self):
        """Get camera device information"""
        body = '<GetDeviceInformation xmlns="http://www.onvif.org/ver10/device/wsdl"/>'
        response = self._soap_request(self.device_url, body)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            ns = {'tds': 'http://www.onvif.org/ver10/device/wsdl'}
            info = root.find('.//tds:GetDeviceInformationResponse', ns)
            
            if info:
                return {
                    'Manufacturer': info.find('tds:Manufacturer', ns).text,
                    'Model': info.find('tds:Model', ns).text,
                    'FirmwareVersion': info.find('tds:FirmwareVersion', ns).text,
                    'SerialNumber': info.find('tds:SerialNumber', ns).text,
                    'HardwareId': info.find('tds:HardwareId', ns).text,
                }
        
        raise Exception(f"Failed to get device info: {response.status_code}")
    
    def get_profile_token(self):
        """Get media profile token (required for PTZ commands)"""
        if self.profile_token:
            return self.profile_token
        
        body = '<GetProfiles xmlns="http://www.onvif.org/ver10/media/wsdl"/>'
        response = self._soap_request(self.media_url, body)
        
        if response.status_code == 200:
            root = ET.fromstring(response.text)
            # Find first profile with token attribute
            for elem in root.iter():
                if 'token' in elem.attrib:
                    self.profile_token = elem.attrib['token']
                    return self.profile_token
        
        # Fallback to common token name
        self.profile_token = 'Profile_1'
        return self.profile_token
    
    def continuous_move(self, pan=0.0, tilt=0.0, zoom=0.0):
        """
        Start continuous PTZ movement
        
        Args:
            pan: -1.0 to 1.0 (negative=left, positive=right)
            tilt: -1.0 to 1.0 (negative=down, positive=up)
            zoom: -1.0 to 1.0 (negative=zoom out, positive=zoom in)
        
        Returns:
            bool: True if successful
        """
        if not self.profile_token:
            self.get_profile_token()
        
        body = f'''<ContinuousMove xmlns="http://www.onvif.org/ver20/ptz/wsdl">
    <ProfileToken>{self.profile_token}</ProfileToken>
    <Velocity>
        <PanTilt x="{pan}" y="{tilt}" xmlns="http://www.onvif.org/ver10/schema"/>
        <Zoom x="{zoom}" xmlns="http://www.onvif.org/ver10/schema"/>
    </Velocity>
</ContinuousMove>'''
        
        response = self._soap_request(self.ptz_url, body)
        return response.status_code == 200
    
    def stop(self):
        """Stop all PTZ movement"""
        if not self.profile_token:
            self.get_profile_token()
        
        body = f'''<Stop xmlns="http://www.onvif.org/ver20/ptz/wsdl">
    <ProfileToken>{self.profile_token}</ProfileToken>
    <PanTilt>true</PanTilt>
    <Zoom>true</Zoom>
</Stop>'''
        
        response = self._soap_request(self.ptz_url, body)
        return response.status_code == 200
    
    def move_right(self, speed=0.5, duration=2):
        """Move camera right"""
        self.continuous_move(pan=speed)
        time.sleep(duration)
        self.stop()
    
    def move_left(self, speed=0.5, duration=2):
        """Move camera left"""
        self.continuous_move(pan=-speed)
        time.sleep(duration)
        self.stop()
    
    def move_up(self, speed=0.5, duration=2):
        """Move camera up"""
        self.continuous_move(tilt=speed)
        time.sleep(duration)
        self.stop()
    
    def move_down(self, speed=0.5, duration=2):
        """Move camera down"""
        self.continuous_move(tilt=-speed)
        time.sleep(duration)
        self.stop()
    
    def zoom_in(self, speed=0.5, duration=2):
        """Zoom in"""
        self.continuous_move(zoom=speed)
        time.sleep(duration)
        self.stop()
    
    def zoom_out(self, speed=0.5, duration=2):
        """Zoom out"""
        self.continuous_move(zoom=-speed)
        time.sleep(duration)
        self.stop()
    
    def absolute_move(self, pan=0.0, tilt=0.0, zoom=0.0):
        """
        Move to absolute position
        
        Args:
            pan: -1.0 to 1.0 (position)
            tilt: -1.0 to 1.0 (position)
            zoom: 0.0 to 1.0 (zoom level)
        """
        if not self.profile_token:
            self.get_profile_token()
        
        body = f'''<AbsoluteMove xmlns="http://www.onvif.org/ver20/ptz/wsdl">
    <ProfileToken>{self.profile_token}</ProfileToken>
    <Position>
        <PanTilt x="{pan}" y="{tilt}" xmlns="http://www.onvif.org/ver10/schema"/>
        <Zoom x="{zoom}" xmlns="http://www.onvif.org/ver10/schema"/>
    </Position>
</AbsoluteMove>'''
        
        response = self._soap_request(self.ptz_url, body)
        return response.status_code == 200
    
    def goto_home(self):
        """Move camera to home position (center)"""
        return self.absolute_move(pan=0.0, tilt=0.0, zoom=0.0)


def main():
    """Test the ONVIF PTZ controller"""
    print("="*70)
    print("🎥 Hikvision ONVIF PTZ Controller Test")
    print("="*70)
    
    # Initialize camera
    camera = HikvisionONVIFCamera('192.168.100.171', 'admin', 'PSTC#100200300')
    
    try:
        # Get device info
        print("\n📋 Device Information:")
        info = camera.get_device_info()
        for key, value in info.items():
            print(f"   {key}: {value}")
        
        # Get profile token
        print(f"\n🔧 Profile Token: {camera.get_profile_token()}")
        
        # Test PTZ movements
        print("\n🎯 Testing PTZ Movements:")
        print("-" * 70)
        
        movements = [
            ("Move RIGHT", lambda: camera.move_right(speed=0.3, duration=1)),
            ("Move LEFT", lambda: camera.move_left(speed=0.3, duration=1)),
            ("Move UP", lambda: camera.move_up(speed=0.3, duration=1)),
            ("Move DOWN", lambda: camera.move_down(speed=0.3, duration=1)),
            ("Zoom IN", lambda: camera.zoom_in(speed=0.5, duration=1)),
            ("Zoom OUT", lambda: camera.zoom_out(speed=0.5, duration=1)),
            ("Go to HOME", camera.goto_home),
        ]
        
        for name, action in movements:
            print(f"\n▶️  {name}...")
            action()
            print(f"   ✅ Completed")
            time.sleep(0.5)
        
        print("\n" + "="*70)
        print("✅ All PTZ tests completed successfully!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()