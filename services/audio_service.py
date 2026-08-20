class AudioService:
    def __init__(self):
        self.is_recording = False

    def start_recording(self, output_path):
        self.is_recording = True
        print(f"[Audio Service] Recording started: {output_path}")

    def stop_recording(self):
        self.is_recording = False
        print("[Audio Service] Recording stopped.")