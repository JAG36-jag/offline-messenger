class WifiHotspotService:
    def __init__(self):
        self.is_active = False

    def start_hotspot(self):
        self.is_active = True
        print("[Wi-Fi Hotspot Service] Hotspot started.")

    def stop_hotspot(self):
        self.is_active = False
        print("[Wi-Fi Hotspot Service] Hotspot stopped.")