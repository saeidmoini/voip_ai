import azure.cognitiveservices.speech as speechsdk
import asyncio
import os


class AzureTTS:
    def __init__(self, subscription_key, region, path):
        self.subscription_key = subscription_key
        self.region = region
        self.PATH = path

    async def text_to_speech(self, text, file_name):
        speech_config = speechsdk.SpeechConfig(subscription=self.subscription_key, region=self.region)
        audio_config = speechsdk.audio.AudioOutputConfig(filename=os.path.join(self.PATH, "logs", f"{file_name}.mp3"))

        speech_config.speech_synthesis_voice_name = "fa-IR-DaryaNeural"  # Example Persian voice

        synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

        result_future  = synthesizer.speak_text_async(text)
        result = result_future .get()

        if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
            print("Speech synthesized for text.")
        else:
            print(f"Error: {result.reason}")
            if result.reason == speechsdk.ResultReason.Canceled:
                cancellation_details = result.cancellation_details
                print(f"Speech synthesis canceled: {cancellation_details.reason}")
                print(f"Error details: {cancellation_details.error_details}")
