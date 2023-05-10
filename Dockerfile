FROM python:3.7-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ADD https://github.com/mikefarah/yq/releases/download/v4.31.2/yq_linux_amd64 /bin/yq
RUN chmod +x /bin/yq
ADD https://github.com/moparisthebest/static-curl/releases/download/v7.88.1/curl-amd64 /bin/curl
RUN chmod +x /bin/curl

COPY fedservice /lib/fedservice
WORKDIR /lib/fedservice

# Install any needed packages specified in requirements.txt
RUN pip install --upgrade pip && \
    pip install deps/oidcop-2.4.3.tar.gz && \
    pip install -r requirements.txt && \
    pip install flask && \
    pip install .

COPY app /app
RUN mkdir /log

WORKDIR /app

EXPOSE 11833
ENTRYPOINT [ "/bin/bash" ]
CMD [ "/app/run.sh" ]