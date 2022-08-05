from vosk_api.python.example.test_microphone import Microphone

class AudioDetection:
    def __init__(self):
        mic = Microphone()
        mic.get_text()
        
if __name__ == '__main__':
    driver = AudioDetection()

