import speech_recognition as sr
import pyautogui
import time
import pyttsx3

def recognize_speech(recognizer, microphone):
    with microphone as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=2, phrase_time_limit=2)
        except sr.WaitTimeoutError:
            print("Listening timed out while waiting for phrase to start")
            return None

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text
    except sr.UnknownValueError:
        print("Sorry, could not understand audio.")
        return None
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))
        return None

def main():
    # Initialize text-to-speech engine
    engine = pyttsx3.init()
    engine.say("Opening voice recognition")
    engine.runAndWait()

    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    while True:
        start_time = time.time()
        while time.time() - start_time < 1:  # Run listening function for 1 second
            text = recognize_speech(recognizer, microphone)
            if text:
                if "type" in text.lower():
                    print("Executing main code...")
                    filtered_text = text.lower().split("type", 1)[-1].strip()
                    if filtered_text:
                        pyautogui.write(filtered_text)
        time.sleep(1)

if __name__ == "__main__":
    main()
