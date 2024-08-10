from kivy.uix.screenmanager import Screen
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.clock import Clock
import threading
import speech_recognition as sr
from gtts import gTTS
from playsound import playsound
import os
import tempfile

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super(LoginScreen, self).__init__(**kwargs)

        # Create the main layout
        layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Background image or logo
        logo = Image(source='logo.png', size_hint=(1, 0.4))
        layout.add_widget(logo)

        # Username input
        username_box = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        username_box.add_widget(Label(text="Username:", font_size=20, size_hint=(0.3, 1)))
        self.username_input = TextInput(size_hint=(0.7, 1))
        username_box.add_widget(self.username_input)
        layout.add_widget(username_box)
        
        # Password input
        password_box = BoxLayout(orientation='horizontal', padding=10, spacing=10)
        password_box.add_widget(Label(text="Password:", font_size=20, size_hint=(0.3, 1)))
        self.password_input = TextInput(password=True, size_hint=(0.7, 1))
        password_box.add_widget(self.password_input)
        layout.add_widget(password_box)

        # Buttons for login, back, and audio
        button_box = BoxLayout(orientation='horizontal', padding=10, spacing=10, size_hint=(1, 0.2))
        
        # Repeat button
        repeat_button = Button(text="Repeat Instructions", size_hint=(0.33, 1))
        repeat_button.bind(on_press=self.repeat_instructions)
        button_box.add_widget(repeat_button)
        
        # Login button
        login_button = Button(text="Login", size_hint=(0.33, 1))
        login_button.bind(on_press=self.check_credentials)
        button_box.add_widget(login_button)

        # Speak button
        speak_button = Button(text="Speak", size_hint=(0.33, 1))
        speak_button.bind(on_press=self.start_recording)
        button_box.add_widget(speak_button)

        # Back button
        back_button = Button(text="Back to Home", size_hint=(1, 0.2))
        back_button.bind(on_press=self.go_to_home)
        button_box.add_widget(back_button)

        layout.add_widget(button_box)
        self.add_widget(layout)

        # Initial voice guidance
        self.last_message = "You will have the option to log in through speech. There is a button on the far left to repeat the instructions and an audio button on the far right. Say 'username' to start entering your username, 'password' to start entering your password, 'clear username' or 'clear password' to clear the fields, and 'login' to log in."

        self.input_target = None
        self.username_chars = []
        self.password_chars = []

    def speak(self, text):
        if text:  # Ensure there is text to speak
            tts = gTTS(text=text, lang='en', slow=False)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_file:
                tts.save(temp_file.name)
                playsound(temp_file.name)
            os.remove(temp_file.name)

    def check_credentials(self, instance):
        username = self.username_input.text
        password = self.password_input.text
        if username == 'user123' and password == 'password123':
            self.manager.current = 'visuai'
        else:
            self.show_error_popup()

    def show_error_popup(self):
        popup_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        popup_layout.add_widget(Label(text="Invalid username or password.", font_size=20))
        dismiss_button = Button(text="Dismiss", size_hint=(1, 0.2))
        popup_layout.add_widget(dismiss_button)
        
        popup = Popup(title="Login Error", content=popup_layout, size_hint=(0.8, 0.4))
        dismiss_button.bind(on_press=popup.dismiss)
        popup.open()

    def go_to_home(self, instance):
        self.manager.current = 'home'

    def start_recording(self, instance):
        if self.input_target:
            self.speak("Say a character.")
        else:
            self.speak("Listening...")
        threading.Thread(target=self.record_speech).start()

    def record_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5)
                text = recognizer.recognize_google(audio)
                print(f"You said: {text}")
                # Process speech input in the main thread
                Clock.schedule_once(lambda dt: self.process_speech(text))
            except sr.UnknownValueError:
                print("Sorry, I did not understand that.")
                self.speak("Sorry, I did not understand that.")
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                self.speak("Sorry, there was an error with the audio request.")
            except Exception as e:
                print(f"An error occurred: {e}")
                self.speak("An error occurred during speech recognition.")

    def process_speech(self, text):
        text = text.lower().strip()
        # Check if the speech is a single character or number
        if text in {'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '-', '_', '=', '+', '[', ']', '{', '}', '\\', '|', ';', ':', '\'', '"', ',', '.', '/', '<', '>', '?', '`', '~'}:
            self.append_to_input(text)
        elif text == 'username':
            self.speak("Continue. Say each letter or number for the username.")
            self.input_target = 'username'
        elif text == 'password':
            self.speak("Continue. Say each letter or number for the password.")
            self.input_target = 'password'
        elif text.startswith('clear username'):
            self.username_input.text = ""
            self.username_chars.clear()
            self.speak("Username cleared.")
        elif text.startswith('clear password'):
            self.password_input.text = ""
            self.password_chars.clear()
            self.speak("Password cleared.")
        elif text == 'login':
            self.check_credentials(None)
        elif text.startswith('finish username'):
            self.input_target = None
            self.speak("Finished entering username.")
        elif text.startswith('finish password'):
            self.input_target = None
            self.speak("Finished entering password.")
        elif text == 'repeat username':
            self.speak(" ".join(self.username_chars))
        elif text == 'repeat password':
            self.speak(" ".join(self.password_chars))
        else:
            self.speak("Please say a single character.")

    def append_to_input(self, text):
        if self.input_target == 'username':
            self.username_chars.append(text)
            self.username_input.text = "".join(self.username_chars)
        elif self.input_target == 'password':
            self.password_chars.append(text)
            self.password_input.text = "".join(self.password_chars)

    def repeat_instructions(self, instance):
        self.speak(self.last_message)
