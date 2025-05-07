FROM public.ecr.aws/sam/build-python3.11 AS builder

WORKDIR /var/task

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --platform manylinux2014_x86_64 \
    --target python --only-binary=:all: \
    -r requirements.txt

COPY lambda_function.py python/

RUN cd python && zip -r9 /var/task/lambda-genai.zip .
