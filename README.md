# Simulation-game
This is a web application for a choose your own adventure game, except you can write any situation you can think of.


# Install and Setup

### Install - Step 1
  Copy this repository into a directory within the local machine.

### Install - Step 2
  Create a Python 3.10-3.11 environment using virtual environment.
  Install the required libraries via pip.
  - Flask
  - Requests
  - Openai
  - Gunicorn
  - json
    
  Test this works by starting up the microservices using `python3 app.py` and `python3 Microservice.py`.

### Setup - Step 1

  -Create an Openai account and purchase credits that can be used from API calls. 
  This will come in the form of a monthly limit. Locate your API key.
  
  -Create a Stablity.ai account, this should come with a few started credits, or feel
  free to purchase more. Locate your API key.

### Setup - Step 2

  Create two files within the directory with the server files - 'openai-key.txt' and 'stable_key.txt'.
  Copy and paste your Openai key in the 'openai-key.txt', then copy and past your stability.ai key into the
  'stable_key.txt' file.

  You are finished! Visit your site on the local host port where app.py is deployed to.

