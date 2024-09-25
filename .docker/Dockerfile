FROM ubuntu:20.04

LABEL maintainer="Robin Röper <rr@linux.com>"

# Make sure we don't get interactive prompts
ENV DEBIAN_FRONTEND=noninteractive

# Set service type
ENV POLYAXON_SERVICE=cli

# Set other environment variables
ENV LANG=C.UTF-8 \
    PATH=/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin \
    PYTHON_VERSION=3.11.9 \
    PYTHON_GPG_KEY=CFDCA245B1043CF2A5F97865FFE87404168BD847 \
    PYTHON_PIP_VERSION=24.0 \
    PYTHON_SETUPTOOLS_VERSION=65.5.1 \
    PYTHON_GET_PIP_URL=https://github.com/pypa/get-pip/raw/def4aec84b261b939137dd1c69eff0aabb4a7bf4/public/get-pip.py \
    PYTHON_GET_PIP_SHA256=bc37786ec99618416cc0a0ca32833da447f4d91ab51d2c138dd15b7af21e8e9a

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    ca-certificates \
    curl \
    dirmngr \
    dumb-init \
    git \
    gnupg \
    iproute2 \
    libpcre3 \
    libpcre3-dev \
    libxml2-dev \
    libxmlsec1-dev \
    libxmlsec1-openssl \
    netbase \
    socat \
    openssl \
    pkg-config \
    tzdata \
    vim \
    wget \
    xz-utils \
    zlib1g-dev \
    libbz2-dev \
    libssl-dev \
    libffi-dev \
    libsqlite3-dev \
    && apt-get clean \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

# Install Python
ADD https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz /usr/src/python/
ADD https://www.python.org/ftp/python/${PYTHON_VERSION%%[a-z]*}/Python-$PYTHON_VERSION.tar.xz.asc /usr/src/python/

WORKDIR /usr/src/python

RUN set -ex \
    && export GNUPGHOME="$(mktemp -d)" \
    && gpg --batch --keyserver hkps://keyserver.ubuntu.com --recv-keys ${PYTHON_GPG_KEY} \
    && gpg --batch --verify Python-$PYTHON_VERSION.tar.xz.asc Python-$PYTHON_VERSION.tar.xz \
    && { command -v gpgconf > /dev/null && gpgconf --kill all || :; } \
    && rm -rf "$GNUPGHOME" Python-$PYTHON_VERSION.tar.xz.asc

RUN tar -xJC /usr/src/python --strip-components=1 -f Python-$PYTHON_VERSION.tar.xz \
    && rm Python-$PYTHON_VERSION.tar.xz \
    && cd /usr/src/python \
    && ./configure --enable-optimizations --enable-loadable-sqlite-extensions \
    && make -j "$(nproc)" \
    && make install \
    && ldconfig \
    && find /usr/local -depth \
    \( \
    \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
    -o \
    \( -type f -a \( -name '*.pyc' -o -name '*.pyo' \) \) \
    \) -exec rm -rf '{}' + \
    && rm -rf /usr/src/python \
    && python3 --version

# Set up Python symlinks
RUN for src in idle3 pydoc3 python3 python3-config; do \
    dst="$(echo "$src" | tr -d 3)"; \
    [ -s "/usr/local/bin/$src" ] && [ ! -e "/usr/local/bin/$dst" ] && ln -svT "$src" "/usr/local/bin/$dst"; \
    done

# Install pip
RUN set -ex \
    && wget -O get-pip.py "$PYTHON_GET_PIP_URL" \
    && echo "$PYTHON_GET_PIP_SHA256 *get-pip.py" | sha256sum -c - \
    && python3 get-pip.py \
    --disable-pip-version-check \
    --no-cache-dir \
    "pip==$PYTHON_PIP_VERSION" \
    "setuptools==$PYTHON_SETUPTOOLS_VERSION" \
    wheel \
    && rm -f get-pip.py \
    && pip --version

# Upgrade pip and clean up
RUN pip install --no-cache-dir -U pip \
    && apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY /cli /cli
COPY /cmd /usr/local/bin

# Set the working directory
WORKDIR /cli/cli

# Install the dependencies
RUN pip install --no-cache-dir -r requirements/requirements.txt
RUN pip install --no-cache-dir -r requirements/prod.txt

ENV PYTHONPATH="${PYTHONPATH}:/core/core"

# Build the package 
RUN python -m build

# Install the package
RUN pip install --no-cache-dir dist/*.whl

# Set the user
RUN groupadd -r nobody && useradd -r -g nobody nobody
USER nobody

# Set the entrypoint
ENTRYPOINT ["polyaxon"]