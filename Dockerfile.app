# Dockerfile.app

#base image, could use like ubuntu or whatever, 
#but this is small debian based python image good for this
FROM python:3.11-slim

#set default base directory for running CMD as seen bottom of script
WORKDIR /app
COPY .env .

#This stops python from writing pyc cache file, not needed but stops a bunch of clutter
ENV PYTHONDONTWRITEBYTECODE=1
#forces output, good for catching errors IG?s
ENV PYTHONUNBUFFERED=1

#COPY <local source> <container destination>
#grab requirements into image for setup
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#now copy the app code into the file too
#we put this down here, so it caches it last, and when app/ changes, it only goes back this far to rerun docker container
#       if it was before the install command above, then that would have to be redone too every time app/ dir updates
COPY backend ./backend

#this is just kinda documentation that its open on port 45454, doesnt do anything real.
#not actually needed, but standard
EXPOSE 45454
#need to call    docker run -p 45454:45454 myimage. for it to actually open the port

# Start FastAPI (frontend)
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "45454"]