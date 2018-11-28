# MBRDNA Speech/Digital Assistant Weekend Task

The file in this repository runs a local webserver, served at http://localhost:5000. It has 2 endpoints, `/queryText` and `/queryAudio`, both of which can support POST requests. `/queryText` can also support GET requests with the argument provided in the URL.

The webserver is run on the Python library Flask, and speech recognition is done using Houndify. News requests are managed using the New York Times "Most Popular" API. 

