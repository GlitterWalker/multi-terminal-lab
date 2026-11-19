FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3 python3-pip docker.io curl nano \
    && pip3 install boto3 && rm -rf /var/lib/apt/lists/*
RUN useradd -m student
WORKDIR /home/student
COPY quiz.py /home/student/quiz.py
ENV AWS_DEFAULT_REGION=ap-south-1
CMD ["python3", "/home/student/quiz.py"]