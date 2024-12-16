FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

ADD https://github.com/mikefarah/yq/releases/download/v4.31.2/yq_linux_amd64 /bin/yq
RUN chmod +x /bin/yq
ADD https://github.com/moparisthebest/static-curl/releases/download/v7.88.1/curl-amd64 /bin/curl
RUN chmod +x /bin/curl
RUN apt-get update && apt-get install -y gcc libgraphviz-dev

COPY deps /lib/deps
WORKDIR /lib/deps

# Install any needed packages
RUN pip install --upgrade pip && \
    pip install flask werkzeug && \
    pip install ofcli && \
    pip install ./fedservice && \
    pip install ./idpy-oidc

COPY app /app
RUN mkdir /log

WORKDIR /app

EXPOSE 80
ENTRYPOINT [ "/bin/bash" ]
CMD [ "/app/run.sh" ]
