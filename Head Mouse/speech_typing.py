import speech_recognition as sr
import pyautogui
import pyttsx3
import os
import webbrowser
import requests
import json
from groq import Groq

# Initialize speech engine once at the beginning
engine = pyttsx3.init()

def speak(text):
    """Helper function to speak text"""
    print(text)
    engine.say(text)
    engine.runAndWait()

def recognize_speech(recognizer, microphone):
    """Recognize speech from microphone input"""
    with microphone as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("Listening timed out. No speech detected.")
            return None

    try:
        print("Recognizing...")
        text = recognizer.recognize_google(audio)
        print("You said:", text)
        return text.lower()  # Return lowercase for consistent processing
    except sr.UnknownValueError:
        print("Sorry, could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Error with speech recognition service: {e}")
        return None

def ask_groq(question):
    """Optimized Groq API query with faster model"""
    try:
        client = Groq(api_key="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")
        
        # Use a faster model (llama2 is typically quick)
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": question}],
            model="llama-3.3-70b-versatile",  # Fast and reliable
            max_tokens=500,  # Limit response length
            temperature=0.7,  # Balance creativity/speed
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {str(e)}"

def type_answer(answer):
    """Try fast typing, fallback to clipboard if available"""
    try:
        # First try very fast typing
        pyautogui.PAUSE = 0.005
        pyautogui.write(answer, interval=0.02)
        pyautogui.PAUSE = 0.1
    except Exception:
        # Fallback to clipboard if typing fails
        try:
            import pyperclip
            pyperclip.copy(answer)
            pyautogui.hotkey('ctrl', 'v')
        except:
            # Final fallback to slower typing
            pyautogui.write(answer)

def open_app(app_name):
    """Open an application by name (including Microsoft Word)"""
    app_paths = {
        'word': '"C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Microsoft Office 2013/Word 2013.lnk"',
        'world': '"C:/ProgramData/Microsoft/Windows/Start Menu/Programs/Microsoft Office 2013/Word 2013.lnk"',
        'excel': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\EXCEL.EXE',
        'powerpoint': 'C:\\Program Files\\Microsoft Office\\root\\Office16\\POWERPNT.EXE',
        'notepad': 'notepad.exe',
        'calculator': 'calc.exe',
        'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'spotify': os.path.expanduser('~\\AppData\\Roaming\\Spotify\\Spotify.exe'),
    }
    
    # Check if the app is in the predefined list
    if app_name.lower() in app_paths:
        path = app_paths[app_name.lower()]
        try:
            os.startfile(path)
            speak(f"Opening {app_name}")
        except Exception as e:
            speak(f"Failed to open {app_name}. Error: {str(e)}")
    else:
        speak(f"Application '{app_name}' not configured. Please add it to the list.")

def open_website(site_name):
    """Open a predefined website"""
    websites = {
        'youtube': 'https://www.youtube.com',
        'amazon': 'https://www.amazon.in',
        'google': 'https://www.google.com',
        'github': 'https://www.github.com',
        'facebook': 'https://www.facebook.com',
        'twitter': 'https://www.twitter.com',
    }

    if site_name in websites:
        speak(f"Opening {site_name}")
        webbrowser.open(websites[site_name])
    else:
        speak(f"Website '{site_name}' not configured. Please add it to the list.")

def main():
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    speak("Voice recognition is active. You can give commands like type, clear all, scroll, click, or ask questions.")

    while True:
        text = recognize_speech(recognizer, microphone)
        if not text:
            continue

        try:
            if "exit" in text or "quit" in text:
                speak("Exiting program.")
                pyautogui.press('esc')
                break

            elif "answer the question" in text:
                question = text.split("answer the question", 1)[-1].strip()
                if question:
                    speak(f"Fetching answer for: {question}")
                    answer = ask_groq(question)
                    speak(answer)
                else:
                    speak("No question detected.")

            elif "type the answer" in text:
                question = text.split("type the answer", 1)[-1].strip()
                if question:
                    speak(f"Fetching answer for: {question}")
                    answer = ask_groq(question)
                    type_answer(answer)
                else:
                    speak("No question detected.")

            elif "clear all" in text:
                speak("Clearing all text.")
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')

            elif "type" in text:
                speak("Typing your text.")
                filtered_text = text.split("type", 1)[-1].strip()
                if filtered_text:
                    pyautogui.write(filtered_text)

            elif "scroll up" in text:
                speak("Scrolling up.")
                pyautogui.scroll(500)

            elif "scroll down" in text:
                speak("Scrolling down.")
                pyautogui.scroll(-500)

            elif "right click" in text:
                speak("Performing right-click.")
                pyautogui.rightClick()

            elif "double click" in text:
                speak("Performing double-click.")
                pyautogui.doubleClick()

            elif "enter" in text:
                speak("Pressing Enter.")
                pyautogui.press('enter')

            elif "select all" in text:
                speak("Selecting all text.")
                pyautogui.hotkey('ctrl', 'a')

            elif "copy" in text:
                speak("Copying text.")
                pyautogui.hotkey('ctrl', 'c')

            elif "paste" in text:
                speak("Pasting text.")
                pyautogui.hotkey('ctrl', 'v')

            elif "close window" in text:
                speak("Closing window.")
                pyautogui.hotkey('alt', 'f4')

            elif "open app" in text:
                app_name = text.split("open app", 1)[-1].strip()
                if app_name:
                    open_app(app_name)

            elif "open web" in text or "open website" in text:
                site_name = text.split("open", 1)[-1].replace("web", "").replace("website", "").strip()
                if site_name:
                    open_website(site_name)

            else:
                speak("Command not recognized. Please try again.")

        except Exception as e:
            speak(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()