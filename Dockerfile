FROM b.gcr.io/tensorflow/tensorflow-full

RUN apt-get update
RUN pip install -U pip setuptools

CMD bash

