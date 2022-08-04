import speech_recognition

class AudioDetection:
    def __init__(self):
        self.tracking_color = None
        self.recognizer = speech_recognition.Recognizer()

    def detect_audio(self):
        text = None

        with speech_recognition.Microphone() as source:
            audio = self.recognizer.listen(source)

        try:
            text = self.recognizer.recognize_sphinx(audio)
            print(text)
        except speech_recognition.UnknownValueError:
            print('audio could not be determined')
        except speech_recognition.RequestError as e:
            print(e)

        if text is not None:
            print(text)
            words = text.split()
            index = words.rfind('track')
            if index != -1:
                self.tracking_color = words[index + 1]

if __name__ == '__main__':
    driver = AudioDetection()
    driver.detect_audio()

