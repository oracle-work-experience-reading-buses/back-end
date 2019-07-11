FROM oraclelinux:7-slim
RUN yum install -y python36-devel python36-pip gcc libssl-devel libffi-devel openssl-devel pip python3-setuptools python-pip python-requests && \
pip install --upgrade pip && \
easy_install pip && \
pip3 install Flask==1.1.1

WORKDIR /app

COPY . /app

ENTRYPOINT [ "python" ]
CMD [ "app.py" ]
