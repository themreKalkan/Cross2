import time
import json
import re
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage, TextContentItem, ImageContentItem, ImageUrl, ImageDetailLevel,AssistantMessage
from azure.core.credentials import AzureKeyCredential
from cross_sound import start_recognition
from cross_cam import take_img
from cross_int import get_best_result_snippet
from cross_tts import play_tts
from cross_tts import stop_tts

import threading

# Global flag to indicate when TTS is active
is_playing = threading.Event()
is_playing.set()


# JSON ayıklayıcı: mesaj içindeki JSON fragmentini döner
def extract_json(text):
    try:
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None
    return None

# Fonksiyon simülasyonları

def scan_environment(args=None):
    """Kameraya bakıp çevreyi tarar ve analiz eder"""
    invoke_photo()
    # Örnek analiz: en basit haliyle onay mesajı
    return "Çevre tarandı ve analiz edildi."


def search_internet(args):
    """İnternette araştırma yapar ve özet snippet döner"""
    query = args.get("query", "")
    return get_best_result_snippet(query)


def get_weather(args):
    """Belirtilen şehir için hava durumu döner"""
    location = args.get("location", "")
    return get_best_result_snippet(location)

# Azure GPT config
github_token = "GITHUB API"
endpoint = "https://models.github.ai/inference"
model_name = "openai/gpt-4o-mini"
client = ChatCompletionsClient(endpoint=endpoint, credential=AzureKeyCredential(github_token))

def invoke_photo(tx3):
    take_img()
    response = client.complete(
        messages=[
            SystemMessage("Do what user says."),
            UserMessage(
                content=[
                    TextContentItem(text=tx3),
                    ImageContentItem(
                        image_url=ImageUrl.load(
                            image_file="imgExy.png",
                            image_format="png",
                            detail=ImageDetailLevel.HIGH)
                    ),
                ],
            ),
        ],
        model=model_name,
    )
    return response.choices[0].message.content

# Thread-safe speak function that can be interrupted by user input
def speak(text, recog_queue):
    # Stop any ongoing TTS
    if is_playing.is_set():
        stop_tts()
    # Clear queued inputs to avoid self-recognition
    while not recog_queue.empty():
        try:
            recog_queue.get_nowait()
        except Exception:
            break
    is_playing.set()
    play_tts(text)
    is_playing.clear()



def main_loop():
    # Yapay function çağırma formatını tanımlayan sistem mesajı
    system_msg = SystemMessage(
        content=(
            "You are Cross, a helpful assistant. When the user asks for weather information, environmental scanning, or internet search, "
            "you must respond ONLY with a JSON object like: {\"action\": \"get_weather\", \"parameters\": {\"location\": \"Istanbul\"}}.\n\n"
            "Available actions:\n"
            "- scan_environment: Use this if the user says things like \"Can you see this?\", \"Look around\", or \"Can you analyze this?\".\n"
            "- search_internet: Use this if the user asks questions like \"Who is Atatürk?\", \"What time is the game today?\".\n"
            "If no action is needed, respond normally in English. For example user says normal things. If you dont need to internet or camera(If you can respond without active functions) just respond normally(without JSON)."
        )
    )


    history = [system_msg]
    history.append(UserMessage(content="Hello Cross"))
    recog_queue = start_recognition()
    print("Assistant started. Listening...")

    while True:
        # Kullanıcının sesi algıl

            # Get user input
        user_input = str(input(": "))
        history.append(UserMessage(content=user_input))

        # Özel komut: kamera analizi

        # ChatGPT çağrısı
        response = client.complete(
            messages=history,
            model=model_name,
            temperature=1,
            max_tokens=200,
            top_p=1
        )
        assistant_msg = response.choices[0].message.content
        print(f"Assistant: {assistant_msg}")


        # JSON ile yapılacak eylem var mı kontrol et
        fn_json = extract_json(assistant_msg)
        if fn_json:
            action = fn_json.get("action")
            params = fn_json.get("parameters", {})

            if action == "scan_environment":
                result = invoke_photo(user_input)
            elif action == "search_internet":
                result = search_internet(params)
            elif action == "get_weather":
                result = get_weather(params)
            else:
                result = "Üzgünüm, bu işlemi gerçekleştiremiyorum."

            print(f"[Fonksiyon Cevabı]: {result}")
            speak(result,recog_queue)
            history.append(AssistantMessage(content=f"Fonksiyon sonucu: {result}"))
            continue
        else:
            speak(assistant_msg, recog_queue)

        # Normal asistan cevabını geçmişe ekle
        history.append(AssistantMessage(content=assistant_msg))

        # Çıkış kontrolü
        if user_input.lower() in ["exit", "quit", "kapat"]:
            print("Session ended.")
            break


if __name__ == '__main__':
    main_loop()
