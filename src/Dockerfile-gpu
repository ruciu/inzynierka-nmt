FROM tensorflow/tensorflow:latest-gpu-py3

WORKDIR "/jupyter"

COPY requirements.txt .

EXPOSE 8888

RUN apt-get update && apt-get install -y --no-install-recommends \
      bzip2 \
      g++ \
      git \
      graphviz \
      libgl1-mesa-glx \
      libhdf5-dev \
      openmpi-bin \
      wget && \
    rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install jupyter

RUN pip install -r requirements.txt


CMD [ "jupyter", "notebook" , "--ip", "0.0.0.0", "--port", "8888", "--no-browser", "--allow-root"]
