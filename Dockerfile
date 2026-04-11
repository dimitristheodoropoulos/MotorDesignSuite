# Phase3 Fast Dockerfile (Octave + Python only, headless)
FROM python:3.10-slim

WORKDIR /app

# --- Install Octave, gnuplot, fonts, and build tools ---
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        octave \
        octave-dev \
        gnuplot \
        build-essential \
        gfortran \
        liboctave-dev \
        fonts-liberation \
        libxrender1 \
        libjpeg62-turbo \
        fontconfig \
        && rm -rf /var/lib/apt/lists/*

# --- Octave packages directory ---
ENV OCTAVE_PACKAGES=/octave_pkgs
RUN mkdir -p $OCTAVE_PACKAGES

# --- Install required Octave packages ---
RUN octave --no-gui --eval "pkg prefix path '$OCTAVE_PACKAGES'" && \
    octave --no-gui --eval "pkg install -forge -local statistics" && \
    octave --no-gui --eval "pkg install -forge -local io" && \
    octave --no-gui --eval "pkg list"

# --- Python requirements ---
COPY python/requirements.txt /app/python/requirements.txt
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r python/requirements.txt

# --- Copy project ---
COPY . /app

# --- Default entrypoint ---
CMD ["bash"]
