# teaching-with-vector
Teacher assistant bot for Anki Vector with personalized and auto-generated dataset from distance learning courses audio files.

**Developed for** the *Gentiane Venture's laboratory* of *Tokyo University of Agriculture and Technology*  
**Authors :** *Bastien Muraccioli*  
Release date : August 2021

# Context :
Education was greatly affected during the COVID-19 crisis.
Distance learning courses were implemented and students had to learn from home without the real support of teachers.
This project is an additional support for students during distance learning courses.
It allows students to ask questions to the robot Vector. Vector responds using a state-of-the-art NLP machine learning approach, using the students' course content.

# Description :
Developed on Python 3.7, on Windows 10 with CUDA 11.1, on a GTX1050 Nvidia GPU.
## Speech recognition for Zoom :
Recognize speech on .m4a audio files and converts to .txt files.  
Developed to create dataset from distance learning courses audio recording.
By default the program turns pre-recorded Zoom Meetings audios into speech texts but works on any .flac or .m4a audio files.
If you use Zoom Meetings, you can use the options built into the software to record distance learning courses (See more here : https://support.zoom.us/hc/en-us/articles/201362473-Local-recording). 
Alternatively, you can also use any course recording content that supports Google's speech recognition audio format. 
(See more here : https://cloud.google.com/speech-to-text/docs/encoding)

## Dataset
I don't have any recordings of distance learning courses with Zoom Meetings.
So I used some playlist of Stanford Youtube Chanel videos.
I used loader.to to download Youtube Playlist into .flac format files.
Then, I turned the flac audios into Speech recognition for Zoom program.
I used 2 playlists about robotics, 2 playlists about Natural Language Processing and one about AI.

Playlist that I used : 
 - https://www.youtube.com/playlist?list=PL65CC0384A1798ADF
 - https://www.youtube.com/playlist?list=PLoROMvodv4rMeercb-kvGLUrOq4HR6BZD
 - https://www.youtube.com/playlist?list=PLoROMvodv4rOhcuXMZkNm7j3fVwBBY42z
 - https://www.youtube.com/playlist?list=PLoROMvodv4rObpMCir6rNNUlFAn56Js20
 - https://www.youtube.com/playlist?list=PLoROMvodv4rO1NB9TD4iUZ3qghGEGtqNX

Please, feel free to create your own dataset with your courses content.

## Sensei assistant
Sensei was developed with Haystack, a NLP framework that support state-of-art NLP models.
Sensei use the API Anki Vector as an interface for the Robot but the Sensei's QAmodel can be reuse with just a terminal.

The Sensei dataset is based on speech recognition of course audios. This means that the dataset can evolve and grow, that it talks about different topics, and that it can contain erroneous speech recognition segments.
Furthermore, the dataset does not contain any pre-written questions. The model will generate answers from the textual content only.

Currently, it uses FAISS and Dense Passage Retriever to have an efficient way to search for the contexts of the user's question in all course contents.
It uses also Bart Seq2Seq generator and GenerativeQA pipelines for long-form questions and generate them from the contexts generated before.
This model does not need a powerful GPU to run and it answers different topics in less than a minute. But, it is a bit weak to give a correct answer to a general question that may appear in several lessons in the dataset.

The alternative is to use RetriBERT model as retriever instead of the Dense Passage Retriever. With this method I had good and precize answers on one lesson (the Introduction to Robotics Playlist), you can try it with Sensei_low.py. But, I didn't have enough RAM on my GPU to run all the dataset and try to ask questions with RetriBERT. 

# Get started :
  If you want to use a virtual environment :
  - pipenv shell
  Install requirements:
  - pip install -r requirements.txt
  
  or manual installation :
  - pip install haystack
  - pip install SpeechRecognition
  - pip install pyaudio
  - pip install pydub
  - pip install anki-vector
  
  If you are a Windows user : 
  - install PyTorch 1.8.1 with your CUDA version on pytorch.org website
  - install PyAudio here : https://www.lfd.uci.edu/~gohlke/pythonlibs/
  
  Then, run python Sensei.py
   
The Sensei assistant will introduce itself and initialize the model, this may take a few minutes. When Sensei is ready, Vector will ask you to ask it a question, try it.

Don't forget to connect your Vector with your computer before run Sensei. (py -m anki_vector.configure)
  
  
