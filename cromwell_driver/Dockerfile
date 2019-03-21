FROM ubuntu:xenial
MAINTAINER John Garza <johnegarza@wustl.edu>
LABEL \
    description="Initial image that basespace jobs land in before executing workflows"

RUN apt-get update -y && apt-get install -y \
    default-jdk \
    python \
    python-pip \
    wget

#set up cwltool
RUN pip install --upgrade pip
RUN pip install 'setuptools>=18.5'
RUN pip install cwltool
RUN pip install 'ruamel.yaml==0.14.2'

#install docker, instructions from https://docs.docker.com/install/linux/docker-ce/ubuntu/#install-using-the-repository
RUN apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg-agent \
    software-properties-common

RUN curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -

RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/ubuntu \
   $(lsb_release -cs) \
   stable"

RUN apt-get update

RUN apt-get install -y docker-ce

#install cromwell
WORKDIR /opt/
RUN wget https://github.com/broadinstitute/cromwell/releases/download/36/cromwell-36.jar

#a place for files too large for github that must be packaged in this initial image and then mounted 
#in child containers spawned by cromwell
RUN mkdir /persist
WORKDIR /persist

COPY all_sequences.fa.gz /persist/all_sequences.fa.gz
COPY basespace_cromwell.config /opt/basespace_cromwell.config
COPY Chromoseq.v8.cromwell34.hg38.wdl /opt/Chromoseq.v8.cromwell34.hg38.wdl

COPY configManta.hg38.py.ini /persist/configManta.hg38.py.ini
COPY ChromoSeq.hg38.bed /persist/ChromoSeq.hg38.bed
COPY GeneRegions.bed /persist/GeneRegions.bed
COPY ChromoSeq.translocations.fixed.v2.sorted.hg38.bedpe /persist/ChromoSeq.translocations.fixed.v2.sorted.hg38.bedpe
COPY hg38.blacklist.merged.bed /persist/hg38.blacklist.merged.bed
COPY B38.callset.public.bedpe.gz /persist/B38.callset.public.bedpe.gz
COPY GeneCoverageRegions.bed /persist/GeneCoverageRegions.bed
COPY ChromoSeq.translocations.qc.bed /persist/ChromoSeq.translocations.qc.bed 
COPY nextera_hg38_500kb_median_normAutosome_median.rds_median.n9.rds /persist/nextera_hg38_500kb_median_normAutosome_median.rds_median.n9.rds
COPY all_sequences.dict /persist/all_sequences.dict
COPY all_sequences.fa.bed.gz /persist/all_sequences.fa.bed.gz
COPY all_sequences.fa.fai /persist/all_sequences.fa.fai
