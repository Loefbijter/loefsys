# Pull base image
FROM lambci/lambda:build-python3.12

LABEL maintainer="webcie@loefbijter.nl"
WORKDIR /app

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN pip install -U pip-tools && \
  pip install -U zappa

COPY requirements/* ./
RUN pip install -r production.txt

COPY loefsys /app/loefsys
COPY config /app/config
COPY infra /app/infra
COPY manage.py /app
COPY zappa_settings.json /app
CMD ["bash"]
