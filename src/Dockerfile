FROM ubuntu:22.04

# Set Timezone
RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold -y upgrade
RUN DEBIAN_FRONTEND=noninteractive apt-get -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold -y install tzdata
RUN ln -sf /usr/share/zoneinfo/Asia/Tokyo /etc/localtime
RUN echo "Asia/Tokyo" > /etc/timezone


# Build and Install poppler (Probably installation is not necessary)
WORKDIR /
RUN apt install -y build-essential cmake wget software-properties-common
RUN apt install -y \
    libfreetype6 \
    gobject-introspection \
    libpcre2-dev \
    libfontconfig1-dev \
    libboost-all-dev \
    libnss3 \
    libnss3-dev \
    libcairo2-dev \
    libjpeg-dev \
    libgif-dev \
    libblkid-dev \
    e2fslibs-dev \
    libboost-all-dev \
    libaudit-dev \
    libopenjp2-7-dev

RUN wget https://poppler.freedesktop.org/poppler-22.02.0.tar.xz \
	&& tar -xvf poppler-22.02.0.tar.xz
RUN mv poppler-22.02.0/ poppler/
RUN mkdir poppler/build
RUN apt update

WORKDIR /poppler/build
RUN cmake  -DCMAKE_BUILD_TYPE=Release   \
    -DCMAKE_INSTALL_PREFIX=/usr  \
    -DTESTDATADIR=$PWD/testfiles \
    -DENABLE_UNSTABLE_API_ABI_HEADERS=ON \
    ..
RUN make 
RUN make install


# Install Tesseract OCR
WORKDIR /
RUN add-apt-repository -y ppa:alex-p/tesseract-ocr5
RUN apt-get update
RUN apt install -y tesseract-ocr

# Copy SwapVid backend server source code
COPY . /swapvid_backend

# Install python modules 
# **REQUIRED** pyocr, pdf2image, pillow, websockets
RUN apt install -y pip
RUN apt update
WORKDIR /swapvid_backend/
# RUN pip install -r requirements.txt
RUN pip install pyyaml pyocr pdf2image pillow websockets