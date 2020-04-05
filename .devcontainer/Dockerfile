FROM ubuntu:20.04

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update

## Meson stuff
RUN apt-get install -y python3-dev python3-pip ninja-build && \
    # Make sure pip is up-to-date
    python3 -m pip install -I pip && \
    ln -s $(which python3) /usr/bin/python
RUN python3 -m pip install meson

## Opencv stuff
# Installing dependencies
RUN apt-get install -y software-properties-common && \
    # for libjasper-dev
    add-apt-repository "deb http://security.ubuntu.com/ubuntu xenial-security main" && \
    apt-get update && \
    apt-get install -y \
        build-essential cmake git pkg-config \
        libjasper-dev libtiff-dev libavcodec-dev libavformat-dev libswscale-dev libdc1394-22-dev \
        libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev libgtk2.0-dev libtbb-dev libatlas-base-dev \
        libfaac-dev libmp3lame-dev libtheora-dev libvorbis-dev libxvidcore-dev libopencore-amrnb-dev \
        libopencore-amrwb-dev libavresample-dev x264 v4l-utils python3-dev python3-numpy libjpeg-dev libpng-dev
# Install opencv proper.
ARG OPENCV_VERSION="4.2.0"
RUN apt-get install -y curl cmake xz-utils && \
    # Download / extract
    mkdir /tmp/opencvstuff && cd /tmp/opencvstuff && \
    curl -sL https://github.com/opencv/opencv/archive/${OPENCV_VERSION}.tar.gz | tar xz -C . && \
    cd opencv-${OPENCV_VERSION} && \
    # Compile and install
    mkdir build && cd build && \
    cmake .. \
        -DBUILD_TYPE=Release \
        -DOPENCV_GENERATE_PKGCONFIG=ON \
        -DBUILD_EXAMPLES=OFF \
        -DBUILD_DOCS=OFF \
        -DBUILD_PERF_TESTS=OFF \
        -DBUILD_TESTS=OFF \
        # Gotta go fast!
        -DWITH_TBB=ON \
        -DWITH_OPENMP=ON \
        -DWITH_IPP=ON  \
        #-DWITH_NVCUVID=ON \
        #-DWITH_CUDA=ON \
        -DWITH_CSTRIPES=ON \
        -DWITH_OPENCL=ON \
        && \
    cmake --build . --target install && \
    # Cleanup
    cd / && rm -r /tmp/opencvstuff

## Qt stuff
# Just install whatever qt5 you can find.
RUN apt-get install -y qt5-default

## So we can use GUIs from the container.
RUN apt-get install -y xorg

## Some more utils
RUN apt-get install -y clang-format

ENV DEBIAN_FRONTEND=dialog
