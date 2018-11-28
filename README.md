# MBRDNA Speech/Digital Assistant Weekend Task

The file in this repository runs a local webserver, served at http://localhost:5000. It has 2 endpoints, `/queryText` and `/queryAudio`, both of which can support POST requests. `/queryText` can also support GET requests with the argument provided in the URL.

The webserver is run on the Python library Flask, and speech recognition is done using Houndify. News requests are managed using the New York Times "Most Popular" API. The user can ask for the most popular news, or popular news sorted by most shared, emailed, or viewed. If none is specified in the user's query, the most viewed news will be displayed.

In this repo, you will find the main python file, named `weekendTask.py`. Additionally, there are example .wav files for testing the audio functionality.
