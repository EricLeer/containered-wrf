FROM ubuntu:20.04

ENV DEBIAN_FRONTEND noninteractive
RUN \
    apt-get update \
    && apt-get install -y software-properties-common \
    && add-apt-repository ppa:ubuntugis/ppa \
    && apt-get update \
    && apt-get install -y --allow-unauthenticated \
        gfortran \
        csh \
        build-essential \
        m4 \
        wget \
        ncl-ncarg \
        libgrib2c-dev \
        libjpeg-dev \
        libudunits2-dev \
        python3 \
	python3-pip \
        libsystemd-dev \
        curl \
        imagemagick \
        libjpeg-dev \
        libg2-dev \
        libg20 \
        libx11-6 \
        libxaw7 \
        libmagickwand-dev \
        git \
        autotools-dev \
        autoconf \
	libproj-dev \
        proj-bin \
        libgdal-dev \
        gdal-bin \
	neovim \
    && rm -rf /var/lib/apt/lists/*

ENV PREFIX /home/wrf
WORKDIR /home/wrf
ENV DEBIAN_FRONTEND noninteractive
ENV CC gcc
ENV CPP /lib/cpp -P
ENV CXX g++
ENV FC gfortran
ENV FCFLAGS -m64
ENV F77 gfortran
ENV FFLAGS -m64
ENV NETCDF $PREFIX
ENV NETCDFPATH $PREFIX
ENV WRF_CONFIGURE_OPTION 34
ENV WRF_EM_CORE 1
ENV WRF_NMM_CORE 0
ENV LD_LIBRARY_PATH_WRF $PREFIX/lib/
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH_WRF
ENV NCARG_ROOT=$PREFIX
ENV JASPERLIB=$PREFIX/lib
ENV JASPERINC=$PREFIX/include
ENV GRADS=$PREFIX/grads-2.0.2.oga.2/Contents
ENV GRADDIR=$GRADS/Resources/SupportData
ENV GASCRP=$GRADS/Resources/Scripts
ENV ARW_CONFIGURE_OPTION 3
ENV PYTHONPATH $PREFIX/lib/python2.7/site-packages
ENV PATH $PATH:$PREFIX/bin:$NCARG_ROOT/bin:$GRADS:$GRADS/gribmap:$PREFIX/cnvgrib-1.4.1:$PREFIX/WPS:$PREFIX/WRFV3/test/em_real:$PREFIX/WRFV3/main:$PREFIX/WRFV3/run:$PREFIX/WPS:$PREFIX/ARWpost:$PREFIX
RUN mkdir -p /home/wrf && \
    mkdir -p $PYTHONPATH && \
    useradd wrf -d /home/wrf && \
    chown -R wrf:wrf /home/wrf
RUN ulimit -s unlimited
COPY requirements.txt $PREFIX
RUN pip install --upgrade pip pip
RUN pip install --upgrade pip setuptools
RUN pip install -r requirements.txt
COPY build.sh $PREFIX
USER wrf
RUN ./build.sh


# Install conda and create an environment with the correct variables
# ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && /bin/bash ~/miniconda.sh -b # -p /opt/conda
# ENV PATH=/home/wrf/miniconda3/bin:$PATH

COPY environment.yaml $PREFIX
RUN /home/wrf/miniconda3/bin/conda env create -f environment.yaml

COPY scripts $PREFIX
COPY entrypoint.sh $PREFIX
COPY src $PREFIX
# ENTRYPOINT ["entrypoint.sh"]
# CMD ["bash"]
VOLUME /home/wrf/data
VOLUME /home/wrf/cron
