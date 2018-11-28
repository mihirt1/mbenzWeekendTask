#!/usr/bin/env python3
import houndify
import sys
import requests
from flask import Flask, request, jsonify
app = Flask(__name__)
import wave
import time
import keyring

#The Client ID and Key grant access to the houndify client that is set up through the houndify interface
CLIENT_ID = keyring.get_password("news", "client_id")
CLIENT_KEY = keyring.get_password("news", "client_key")

"""
This is the route and corresponding function for sending a text query, allowing:
1) a GET request with the text query presented as a URL argument, e.g. http://localhost:5000/queryText?q=Get%20me%20the%20popular%20news
2) a POST request with the text query in the BODY field of the POST request. (The form parameter is "query")
"""
@app.route('/queryText', methods=['GET', 'POST'])
def houndText():
    requestInfo = {}
    if (request.method == "GET"):
        QUERY = request.args["q"]
    else:
        QUERY = request.form["query"]
    client = houndify.TextHoundClient(CLIENT_ID, CLIENT_KEY, "test_user") #connect to houndify server
    response = client.query(QUERY) #process result with given text query
    try:
        retIntent = response["AllResults"][0]["Result"] #if the query was successful, we will see a proper result with a NEWS JSON object
    except KeyError: #otherwise we didn't properly understand the request
        return jsonify({"Error":"It looks like you didn't ask for news... We heard you say: "+response["Disambiguation"]["ChoiceData"][0]["Transcription"]})
    if "NEWS" in retIntent:
        return processTitles(retIntent["NEWS"]) #this returns a JSON list of NYT article titles.
    else:
        return "It doesn't look like you asked for the news..."

"""
This is the route and corresponding function for sending a .wav audio query.
It recieves a .wav file through a POST request, with the file in the body of the POST request,
associated with the key "recording". The WAV file type is required to be 16-bit, 8kHz or 16 kHz, and single channel.
"""
@app.route('/queryAudio', methods=['POST'])
def uploadHandler():
    if request.method == 'POST':
        f = request.files['recording']
        f.save('records/toTranscribe.wav') #save the recording to local server
        response = wavFileProcess("records/toTranscribe.wav")
        try:
            retIntent = response["AllResults"][0]["Result"] #if the query was successful, we will see a proper result with a NEWS JSON object
        except KeyError: #otherwise we didn't properly understand the request
            return jsonify({"Error":"It looks like you didn't ask for news... We heard you say: "+response["Disambiguation"]["ChoiceData"][0]["Transcription"]})
        if "NEWS" in retIntent:
            return processTitles(retIntent["NEWS"])
        else:
            return "It doesn't look like you asked for the news..."

"""
This function takes the full NYT JSON responses and parses out only the titles,
which are added to a JSON list and returned as a json item.
"""
def processTitles(mostType):
    allI = requestNYT(mostType)
    retDict = {}
    if mostType == "Popular":
        mostType = "Viewed"
    heading = "Titles (Most "+mostType+" news)"
    retDict[heading] = []
    for article in allI["results"]:
        retDict[heading].append(article["title"]) #extracts just titles from the NYT json
    return jsonify(retDict)

"""
This helper function is called by both text and audio queries, upon confirmation that
the user is requesting news articles. It accesses the NYT most popular API, and chooses
most{viewed, shared, emailed} depending on the user's request.
"""
def requestNYT(mostType):
    t = "mostviewed"
    if mostType == "Emailed":
        t = "mostemailed"
    elif mostType == "Shared":
        t = "mostshared"
    API_KEY = keyring.get_password("news", "nyt")
    headers = {'api-key': API_KEY}
    URL = "https://api.nytimes.com/svc/mostpopular/v2/"+t+"/all-sections/1.json"
    r = requests.get(URL, headers=headers) #uses NYT API to retreive top news from the last day, in all secions.
    jsonRet = r.json() #convert to json
    return jsonRet

"""
This helper function does the actual audio processing of the given wav file,
using the Houndify service to interpret the .wav file and return a result of its
interpretation.
"""
def wavFileProcess(fileN):
    BUFFER_SIZE = 256

    audio = wave.open(fileN)
    if audio.getsampwidth() != 2:
      print("%s: wrong sample width (must be 16-bit)" % fname)
      sys.exit()
    if audio.getframerate() != 8000 and audio.getframerate() != 16000:
      print("%s: unsupported sampling frequency (must be either 8 or 16 khz)" % fname)
      sys.exit()
    if audio.getnchannels() != 1:
      print("%s: must be single channel (mono)" % fname)
      sys.exit()


    audio_size = audio.getnframes() * audio.getsampwidth()
    audio_duration = audio.getnframes() / audio.getframerate()
    chunk_duration = BUFFER_SIZE * audio_duration / audio_size

    class MyListener(houndify.HoundListener):
        pass

    client = houndify.StreamingHoundClient(CLIENT_ID, CLIENT_KEY, "test_user") #connect to houndify service
    client.setSampleRate(audio.getframerate())

    client.start(MyListener()) #stream audio file to houndify

    while True:
      chunk_start = time.time()

      samples = audio.readframes(BUFFER_SIZE)
      #break if we end the finish the audio sample or the client buffer is full
      if len(samples) == 0: break
      if client.fill(samples): break

    result = client.finish() # returns either final response or error
    return result
