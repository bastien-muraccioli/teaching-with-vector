"""
Sensei is a vocal assistant for Anki Vector Robot
When Vector ears 'Hey sensei' he waits for a question from user's courses content and answers.

Developed for the Gentiane Venture's laboratory of Tokyo University of Agriculture and Technology
Author : Bastien Muraccioli
Release date : August 2021
"""
import time
# Vector modules
import anki_vector
# Speech_recognition modules
import speech_recognition as sr
# Question Answering system modules
from haystack.pipeline import GenerativeQAPipeline
from haystack.document_store.faiss import FAISSDocumentStore
from haystack.preprocessor.cleaning import clean_wiki_text
from haystack.preprocessor.utils import convert_files_to_dicts
from haystack.generator.transformers import Seq2SeqGenerator
from haystack.retriever.dense import DensePassageRetriever
from torch import cuda

USE_GPU = cuda.is_available()


# Input a question and the pipe and return a long-form answer extracted from courses content dataset
def QAmodel(question, pipe):
    tic = time.perf_counter()
    # pipe.run return a dict object with the question and the answer values
    result = pipe.run(query=question, top_k_retriever=1, top_k_generator=1)
    toc = time.perf_counter()
    print(f"Question answered in {toc - tic:0.4f} seconds")
    answer = str(result['answers'])
    return answer[3:len(answer) - 2]  # Reformat text before sending


# Initialize the personalized QA model, can take few minutes...
# Features :
# - FAISS document store - DensePassageRetriever to optimize research in the documents
# - Bart Seq2Seq generator and GenerativeQA pipeline for long-form questions
def init_QAmodel():
    """
    Set-up or update the document_store :
    All courses texts are stored in a FAISS document store.
    FAISS is a library for efficient similarity search on a cluster of dense vectors
    It is used to quickly find the context of questions on large documents such as courses.
    """
    dataset_dir = "../Dataset/all"
    # Use "HNSW" for faster search at the expense of some accuracy or "Flat" better accuracy but lower
    document_store = FAISSDocumentStore(faiss_index_factory_str="Flat")
    # Clean & load the dataset into the document store
    dicts = convert_files_to_dicts(dir_path=dataset_dir, clean_func=clean_wiki_text, split_paragraphs=True)
    # The dataset is add to the document store
    document_store.write_documents(dicts)
    """
    Use Dense Passage Retriever to select the passage used by the generator
    Initialize retriever and generator for Long-Form answers.
    Then initialize generative QA Pipeline
    """
    retriever = DensePassageRetriever(document_store=document_store,
                                      query_embedding_model="facebook/dpr-question_encoder-single-nq-base",
                                      passage_embedding_model="facebook/dpr-ctx_encoder-single-nq-base",
                                      max_seq_len_query=64,
                                      max_seq_len_passage=256,
                                      batch_size=24,
                                      use_gpu=USE_GPU,
                                      embed_title=True,
                                      use_fast_tokenizers=True)
    # This a retribert retriever, it has better results but need a lot of memory to work on all documents
    # Please try this retriever if you have a powerful machine
    # Or try it on one course folder only as dataset, for example dataset_dir = "../Dataset/Introduction_to_Robotics"
    #
    # from haystack.retriever.dense import EmbeddingRetriever
    # retriever = EmbeddingRetriever(document_store=document_store,
    #                                embedding_model="yjernite/retribert-base-uncased",
    #                                model_format="retribert")

    # Add retriever
    document_store.update_embeddings(retriever)
    # Add generator, you can use GPU if you have a powerful one
    generator = Seq2SeqGenerator(model_name_or_path="yjernite/bart_eli5", use_gpu=False)
    # Initialize pipeline
    pipe = GenerativeQAPipeline(generator, retriever)
    return pipe


"""
Initialize Vector and Microphone for speech recognizer
"""
# Config Vector Robot
args = anki_vector.util.parse_command_args()  # connection to Vector

# The Anki Vector SDK does not provides access to Vector microphones
# Please use your computer microphone
device_id = 1
r = sr.Recognizer()
mic = sr.Microphone(device_index=device_id)


# Get Vector to say something and animate its body
# Please see Anki Vector SDK for the list of animation trigger for anim_choice parameter
def say_anim(text='Hello', anim=None, anim_choice='GreetAfterLongTime'):
    try :
        with anki_vector.Robot(args.serial) as robot:
            if anim == 'before':
                robot.anim.play_animation_trigger(anim_choice)
            print("Sensei said: '" + text + "'")
            robot.behavior.say_text(text)
            if anim == 'after':
                robot.anim.play_animation_trigger(anim_choice)
    except :
        print("Can't access to Vector, please retry.")


# Use Google Speech Recognizer with the user's microphone to speak with Vector
# the API does not provide access to the Vector's microphones
def listen(pipe):
    say_anim('Please ask me a question about your courses', 'before', 'KnowledgeGraphSearchingGetIn')
    with mic as source:
        audio = r.listen(source)
        time.sleep(0.7)
    try:
        results = r.recognize_google(audio, language='en-US')
        print("User said : '" + results + "'")
        say_anim('Well, let me see...', 'after', 'KnowledgeGraphSearching')
        answer = QAmodel(question=results, pipe=pipe)
        say_anim('The answer of ' + results + ' is, ' + answer, 'before', 'TakeAPictureFocusing')

    except sr.RequestError as e:
        say_anim("I can not access to Google Speech Recognition service. "
                 "Please, check your internet connection.", 'before', 'KnowledgeGraphSearchingFail')
        results = ""
    except sr.UnknownValueError as e:
        say_anim("Sorry, I didn't understand", 'before', 'KnowledgeGraphSearchingGetOutSuccess')
        results = listen(pipe)
    return results


# main program
def hey_sensei():
    nosay_sensei = True
    # Introduce itself to the user
    say_anim("Hello I'm Sensei, your personal assistant for answering questions!", 'after',
             'OnboardingReactToFaceHappy')
    say_anim("I'm going to read your courses, I'll come back after", 'after', 'GoToSleepGetIn')
    pipe = init_QAmodel()
    say_anim('I finish to read your courses, You can call me by saying "Hey Sensei"', 'before', 'GoToSleepOff')
    # Waiting for 'Hey Sensei' said by the user
    while nosay_sensei:
        with mic as source:
            audio = r.listen(source)
        try:
            results = r.recognize_google(audio, language='jp-JP')  # Japanese recognition for sensei word
            print(results)
            if results == 'hey sensei':
                listen(pipe)
        except sr.RequestError as e:
            say_anim("I can not access to Google Speech Regognition service. "
                     "Please, check your internet connection.")
            results = ""
        except sr.UnknownValueError as e:
            # say("Sorry, I didn't understand")
            results = ""


if __name__ == "__main__":
    hey_sensei()
