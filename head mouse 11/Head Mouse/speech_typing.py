import speech_recognition as sr
import pyautogui
import pyttsx3
import os
import webbrowser
import requests
import json
from groq import Groq

class AssistiveApp:
    def __init__(self):
        # Initialize components
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.client = Groq(api_key="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")
        
        # Configuration
        self.websites = {
            'youtube': 'https://www.youtube.com',
            'amazon': 'https://www.amazon.com',
            'google': 'https://www.google.com',
            'github': 'https://www.github.com'
        }
        
        # Settings
        self.voice_feedback = True
        self.pyautogui_pause = 0.1
    
    def speak(self, text):
        """Output text both verbally and to console"""
        print(text)
        if self.voice_feedback:
            self.engine.say(text)
            self.engine.runAndWait()
    
    def recognize_speech(self):
        """Capture and recognize speech from microphone"""
        with self.microphone as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            try:
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
            except sr.WaitTimeoutError:
                print("Listening timed out.")
                return None

        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio).lower()
            print("You said:", text)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio.")
            return None
        except sr.RequestError as e:
            print(f"Speech recognition error: {e}")
            return None
    
    def query_groq(self, question):
        """Get response from Groq API"""
        try:
            response = self.client.chat.completions.create(
                messages=[{"role": "user", "content": question}],
                model="llama-3.3-70b-versatile",
                max_tokens=500,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error: {str(e)}"
    
    def type_response(self, text):
        """Type out text with fallback mechanisms"""
        try:
            pyautogui.PAUSE = 0.005
            pyautogui.write(text, interval=0.02)
            pyautogui.PAUSE = self.pyautogui_pause
        except Exception:
            try:
                import pyperclip
                pyperclip.copy(text)
                pyautogui.hotkey('ctrl', 'v')
            except:
                pyautogui.write(text)
    
    def open_application(self, app_name):
        """Launch an application"""
        try:
            os.startfile(app_name)
            self.speak(f"Opening {app_name}")
        except Exception as e:
            self.speak(f"Failed to open {app_name}: {str(e)}")
    
    def open_website(self, site_name):
        """Open a configured website"""
        site_name = site_name.lower()
        if site_name in self.websites:
            self.speak(f"Opening {site_name}")
            webbrowser.open(self.websites[site_name])
        else:
            self.speak(f"Website '{site_name}' not configured.")
    
    def execute_command(self, text):
        """Process and execute voice commands"""
        if not text:
            return
        
        try:
            if "exit" in text:
                self.speak("Exiting program.")
                pyautogui.press('esc')
                return False
            
            elif "answer the question" in text:
                question = text.split("answer the question", 1)[-1].strip()
                if question:
                    answer = self.query_groq(question)
                    self.speak(answer)
            
            elif "type the answer" in text:
                question = text.split("type the answer", 1)[-1].strip()
                if question:
                    answer = self.query_groq(question)
                    self.type_response(answer)
            
            elif "clear all" in text:
                self.speak("Clearing all text.")
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.press('backspace')
            
            elif "type" in text:
                self.speak("Typing your text.")
                filtered_text = text.split("type", 1)[-1].strip()
                if filtered_text:
                    pyautogui.write(filtered_text)
            
            elif "scroll up" in text:
                self.speak("Scrolling up.")
                pyautogui.scroll(500)
            
            elif "scroll down" in text:
                self.speak("Scrolling down.")
                pyautogui.scroll(-500)
            
            elif "right click" in text:
                self.speak("Performing right-click.")
                pyautogui.rightClick()
            
            elif "double click" in text:
                self.speak("Performing double-click.")
                pyautogui.doubleClick()
            
            elif "enter" in text:
                self.speak("Pressing Enter.")
                pyautogui.press('enter')
            
            elif "select all" in text:
                self.speak("Selecting all text.")
                pyautogui.hotkey('ctrl', 'a')
            
            elif "copy" in text:
                self.speak("Copying text.")
                pyautogui.hotkey('ctrl', 'c')
            
            elif "paste" in text:
                self.speak("Pasting text.")
                pyautogui.hotkey('ctrl', 'v')
            
            elif "close window" in text:
                self.speak("Closing window.")
                pyautogui.hotkey('alt', 'f4')
            
            elif "open app" in text:
                app_name = text.split("open app", 1)[-1].strip()
                if app_name:
                    self.open_application(app_name)
            
            elif "open web" in text or "open website" in text:
                site_name = text.split("open", 1)[-1].replace("web", "").replace("website", "").strip()
                if site_name:
                    self.open_website(site_name)
            
            else:
                self.speak("Command not recognized.")
        
        except Exception as e:
            self.speak(f"An error occurred: {str(e)}")
        
        return True
    
    def run(self):
        """Main application loop"""
        self.speak("Voice recognition is active. How can I help you?")
        
        running = True
        while running:
            text = self.recognize_speech()
            running = self.execute_command(text)

if __name__ == "__main__":
    app = AssistiveApp()
    app.run()