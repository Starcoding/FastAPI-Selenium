FROM python:3.11.1

## install google chrome
#RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
#RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
#RUN apt-get -y update
#RUN apt-get install -y google-chrome-stable
#
## install chromedriver
#RUN apt-get install -yqq unzip
#RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
#RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
#
RUN apt-get -y update
RUN apt-get install -y xvfb


RUN echo "deb http://deb.debian.org/debian/ unstable main contrib non-free" >> /etc/apt/sources.list.d/debian.list
RUN apt-get -y update
RUN apt-get install -y --no-install-recommends firefox
RUN wget https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
RUN tar -xvzf geckodriver-v0.30.0-linux64.tar.gz
RUN chmod +x geckodriver
RUN mv geckodriver /usr/local/bin/

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED 1
ENV GRPC_PYTHON_BUILD_SYSTEM_OPENSSL=1
ENV GRPC_PYTHON_BUILD_SYSTEM_ZLIB=1

RUN apt-get update && apt-get install -y git \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . /opt/project/app

WORKDIR /opt/project/app
RUN chmod a+x ./entrypoint.sh

EXPOSE 8000

ENTRYPOINT /opt/project/app/entrypoint.sh