import speech_recognition as srg
from gtts import gTTS
import os
import pyttsx3

def voice2text():
    file_name="machine-learning_speech-recognition_16-122828-0002.wav"
    r=srg.Recognizer()

    with srg.AudioFile(file_name) as source:
        audio_data=r.record(source)
        text=r.recognize_google(audio_data)
        print(text)

def text2voice():
  
    # initialisation
    engine = pyttsx3.init()
    
    # testing
    engine.say("My first code on text-to-speech")
    engine.say("Thank you, Geeksforgeeks")
    engine.runAndWait()

def try_voice2text():
    #Initiаlize  reсоgnizer  сlаss  (fоr  reсоgnizing  the  sрeeсh)
    r = srg.Recognizer()
    # Reading Audio file as source
    #  listening  the  аudiо  file  аnd  stоre  in  аudiо_text  vаriаble
    with srg.AudioFile('machine-learning_speech-recognition_16-122828-0002.wav') as source:
        audio_text = r.listen(source)
    # recoginize_() method will throw a request error if the API is unreachable, hence using exception handling
        try:
            # using google speech recognition
            text = r.recognize_google(audio_text)
            print('Converting audio transcripts into text ...')
            print(text)
        except:
            print('Sorry.. run again...')

if __name__=="__main__":
    # voice2text()
    # text2voice()
    try_voice2text()