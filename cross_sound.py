import multiprocessing as mp
import speech_recognition as sr
import threading


def _recognize_loop(q_out):
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Mic calibrated. Listening...")

    def recognize_from_mic():
        while True:
            with mic as source:
                print("Listening...")
                audio = recognizer.listen(source)
            try:
                text = recognizer.recognize_google(audio, language="en")
                print(f"Recognized: {text}")
                q_out.put(text)
            except sr.UnknownValueError:
                print("Could not understand audio.")
            except sr.RequestError as e:
                print(f"Request failed: {e}")

    thread = threading.Thread(target=recognize_from_mic, daemon=True)
    thread.start()
    thread.join()


def start_recognition():
    """
    Starts a background process for continuous speech recognition.
    Returns a multiprocessing.Queue where transcribed texts will be posted.
    """
    q = mp.Queue()
    p = mp.Process(target=_recognize_loop, args=(q,), daemon=True)
    p.start()
    return q