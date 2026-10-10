FROM ubuntu:20.04@sha256:8feb4d8ca5354def3d8fce243717141ce31e2c428701f6682bd2fafe15388214
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git ca-certificates python3 python-is-python3 python2 \
    openjdk-8-jdk flex bison gperf zip unzip curl rsync cpio bc \
    libssl-dev libxml2-utils xsltproc liblz4-tool lzop \
    libncurses5 libncurses5-dev zlib1g-dev lib32z1-dev lib32ncurses5-dev \
    libx11-dev libgl1-mesa-dev gettext fontconfig && \
    rm -rf /var/lib/apt/lists/*
# Package revisions are recorded by the build, but the apt snapshot is not pinned.
ARG BUILD_UID=1000
ARG BUILD_GID=1000
RUN groupadd --gid ${BUILD_GID} utbuilder && useradd --uid ${BUILD_UID} --gid ${BUILD_GID} --create-home utbuilder
WORKDIR /work
