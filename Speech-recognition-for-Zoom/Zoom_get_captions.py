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
from shutil import copy
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
        print('End of m4a conversion')
        return 1
    else:
        print('No .m4a files found')
        return -1

# Split long audio files into chunks and use speech recognition to write captions
# The default path is the Zoom Meeting recordings folder path on Windows
def long_speech_conversion(PATH='C:/Users/'+os.getlogin()+'/Documents/Zoom', LANGUAGE="en-US"):
    flac_files = glob.glob(PATH + '/*/*.flac')
    if flac_files:
        nb_error = 0
        nb_chunk = 0
        for flac_file in flac_files:
            # open the audio file stored in the PATH
            sound = AudioSegment.from_file(flac_file)
            fh = open(os.path.splitext(flac_file)[0] + '.txt', "w+", encoding="utf-8")
            tic = time.perf_counter()
            # you can adjust this per requirements
            chunks = split_on_silence(sound,
                                      min_silence_len=500,          # wait for 500ms silence to split
                                      silence_thresh=sound.dBFS-14, #mean audio level - 14 dBFS
                                      keep_silence=500              #silence at the beginning and the end of the chunk
                                      )
            # create a directory to store the chunks
            try:
                os.mkdir('audio_chunks')
            except(FileExistsError):
                pass
            # move into the directory to store the chunks
            os.chdir('audio_chunks')

            # process each chunk for speech recognition
            i = 0
            for audio_chunk in chunks:
                nb_chunk += 1
                # export audio chunk and save it in the current directory.
                print("saving chunk{0}.flac".format(i))
                audio_chunk.export("./chunk{0}.flac".format(i), format="flac")
                # the name of the newly created chunk
                filename = 'chunk' + str(i) + '.flac'
                # print("Processing chunk " + str(i))
                # get the name of the newly created chunk
                # in the AUDIO_FILE variable for later use.
                file = filename
                # create a speech recognition object
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
                    nb_error += 1
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
            print("Percent of unrecognized speech: ", (nb_error/nb_chunk)*100, '%')
            # uncomment if you want to delete zoom audio file to release space
            # os.remove(flac_file)

        # Copy all captions texts to 'all' folder used by Sensei assistant
        text_files = glob.glob(PATH + '/*/*.txt')
        if not text_files:
            print('No text file found')
        else:
            for text_file in text_files:
                copy(text_file, '../Dataset/all')
                # uncomment if you want to delete text files from the PATH
                # os.remove(text_file)
        return 1
    else:
        print('No .flac files found')
        return -1

if __name__ == "__main__":
    # default used path: 'C:/Users/NAME/Documents/Zoom'
    # Convert m4a files to flac,
    m4a_to_flac()
    # Convert long audio files to captions and extract them to Dataset/all
    long_speech_conversion()


