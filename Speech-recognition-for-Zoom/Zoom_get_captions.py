"""
Zoom get captions :
 Speech recognition on .m4a audio files and converts them to .txt files.
 Developed to create dataset from distance learning courses audio recording
 By default the program turn pre-recorded Zoom Meetings audios into speech texts but works on any .flac audio files

Developed for the Gentiane Venture's laboratory of Tokyo University of Agriculture and Technology
Author : Bastien Muraccioli
Release date : August 2021
"""

import os
import glob
import time

import speech_recognition as sr
from pydub import AudioSegment
from pydub.silence import split_on_silence


#convert .m4a audio files to flac format for google recognition
# PATH='C:/Users/'+os.getlogin()+'/Documents/Zoom' #ZOOM default path on Windows
#Zoom folders are stored like this : /Zoom/'meeting_name'/'audios_file.m4a'
def m4a_to_flac(PATH='C:/Users/'+os.getlogin()+'/Documents/Zoom' ):
    m4a_files = glob.glob(PATH + '/*/*.m4a')
    if m4a_files:
        for m4a_file in m4a_files:
            ogg_file = os.path.splitext(m4a_file)[0] + '.flac'
            sound = AudioSegment.from_file(m4a_file)
            # Convert stereo to mono to optimize speech recognition
            sound = sound.set_channels(1)
            sound.export(ogg_file, format="flac")
            os.remove(m4a_file)
        return 1
    else:
        print('No .m4a files found')
        return -1

# a function that splits the audio file into chunks
# and applies speech recognition
def silence_based_conversion(PATH='C:/Users/'+os.getlogin()+'/Documents/Zoom', LANGUAGE="en-US"):
    flac_files = glob.glob(PATH + '/*/*.flac')
    if flac_files:
        for flac_file in flac_files:
            # open the audio file stored in the PATH
            sound = AudioSegment.from_file(flac_file)
            fh = open(os.path.splitext(flac_file)[0] + '.txt', "w+", encoding="utf-8")
            tic = time.perf_counter()
            # split track where silence is 0.5 seconds
            # or more and get chunks
            # you can adjust this per requirements
            chunks = split_on_silence(sound,
                                      min_silence_len=500,
                                      silence_thresh=sound.dBFS-14, #mean audio level - 14 dBFS
                                      keep_silence=500 #leave some silence at the beginning and end of the chunks
                                      )
            # create a directory to store the audio chunks
            try:
                os.mkdir('audio_chunks')
            except(FileExistsError):
                pass
            # move into the directory to store the audio files
            os.chdir('audio_chunks')
            i = 0
            # process each chunk for speech recognition
            for audio_chunk in chunks:
                # export audio chunk and save it in the current directory.
                print("saving chunk{0}.flac".format(i))
                audio_chunk.export("./chunk{0}.flac".format(i), format="flac")
                # # the name of the newly created chunk
                filename = 'chunk' + str(i) + '.flac'
                #print("Processing chunk " + str(i))
                # get the name of the newly created chunk
                # in the AUDIO_FILE variable for later use.
                file = filename
                # # create a speech recognition object
                r = sr.Recognizer()
                # recognize the chunk
                with sr.AudioFile(file) as source:
                    r.adjust_for_ambient_noise(source)
                    audio = r.record(source)
                try:
                    # try converting it to text
                    rec = r.recognize_google(audio, language=LANGUAGE)
                    print(rec)
                    # write the output to the file.
                    fh.write(rec + " ")
                # catch any errors.
                except sr.UnknownValueError as e:
                    print("Error:", str(e))
                except sr.RequestError as e:
                    print("Could not request results. check your internet connection")
                # chunks remove after speech recognition
                os.remove("./chunk{0}.flac".format(i))
                i += 1
            #Go back to previous folder
            os.chdir('..')
            print('saving ' + os.path.splitext(flac_file)[0] + '.txt')
            toc = time.perf_counter()
            print(f"Audio convert in {toc - tic:0.4f} seconds")
            # uncomment if you want to delete zoom audio file to release space
            # os.remove(flac_file)
        return 1
    else:
        print('No .flac files found')
        return -1

if __name__ == "__main__":
    print(m4a_to_flac())
    silence_based_conversion()
