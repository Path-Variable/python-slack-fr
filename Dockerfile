FROM python:3.9

WORKDIR /opt/build

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update 
RUN apt-get install -y \
        build-essential \
        cmake \
        git \
        wget \
        unzip \
        yasm \
        pkg-config \
        libswscale-dev \
        libtbbmalloc2 \
        libtbb-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libopenjp2-7-dev \
        libavformat-dev \
        libpq-dev
RUN pip install numpy
RUN wget  https://github.com/opencv/opencv/archive/refs/tags/4.8.0.zip -O opencv.zip
RUN unzip -qq opencv.zip -d /opt
RUN rm -rf opencv.zip
RUN cmake \
        -D BUILD_TIFF=ON \
        -D BUILD_opencv_java=OFF \
        -D WITH_CUDA=OFF \
        -D WITH_OPENGL=ON \
        -D WITH_OPENCL=ON \
        -D WITH_IPP=ON \
        -D WITH_TBB=ON \
        -D WITH_EIGEN=ON \
        -D WITH_V4L=ON \
        -D BUILD_TESTS=OFF \
        -D BUILD_PERF_TESTS=OFF \
        -D CMAKE_BUILD_TYPE=RELEASE \
        -D CMAKE_INSTALL_PREFIX=$(python3.9 -c "import sys; print(sys.prefix)") \
        -D PYTHON_EXECUTABLE=$(which python3.9) \
        -D PYTHON_INCLUDE_DIR=$(python3.9 -c "from distutils.sysconfig import get_python_inc; print(get_python_inc())") \
        -D PYTHON_PACKAGES_PATH=$(python3.9 -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())") \
        /opt/opencv-4.8.0
RUN make -j$(nproc)
RUN make install
RUN rm -rf /opt/build/*
RUN rm -rf /opt/openv-4.8.0
RUN rm -rf /var/lib/apt/lists/*
RUN apt-get -qq autoremove
RUN apt-get -qq clean

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . .

EXPOSE 5000

CMD [ "python3", "-m" , "flask", "--app", "main", "run", "--host=0.0.0.0"]