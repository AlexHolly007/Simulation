# Simulation-game

This is a web application was created to explore the api use of openai. This game works by letting the user make up a story through an open ended user prompt. Openai models will respond with events that happen in your story and provide images describing the situation created. You will be able to respond on how the story continues in any way through the prompt.
Trying to acheive a maximum open ended choose your own adventure.



# Install and Setup

### Install - Step 1

Copy this repository into a directory within the local machine.

### Install - Step 2

Create a Python 3.11+ environment.
Install the required libraries via pip.

```
pip install -r requirements.txt
```

Test this works by starting up the microservices using `python3 app.py` and `python3 Microservice.py`. These will need to be down for the next step.

### Setup - Step 1

-Create an Openai Platform account, and receive your API key.

There may be some starting credits, but i had to buy some for 5$. This was more than enough for many trails.

### Setup - Step 2

Create a .env file with the contents below to allow openai to access your credits.

```
OPENAI_API_KEY=<Open ai key given>
```

### Setup - Step 3

Run with Gunicorn

```

```
