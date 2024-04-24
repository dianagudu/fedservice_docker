FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ADD https://github.com/mikefarah/yq/releases/download/v4.31.2/yq_linux_amd64 /bin/yq
RUN chmod +x /bin/yq
ADD https://github.com/moparisthebest/static-curl/releases/download/v7.88.1/curl-amd64 /bin/curl
RUN chmod +x /bin/curl


COPY deps /lib/deps
WORKDIR /lib/deps

# Install any needed packages
RUN pip install --upgrade pip && \
    pip install ./fedservice && \
    pip install idpyoidc && \
    pip install flask werkzeug

COPY app /app
RUN mkdir /log

WORKDIR /app

EXPOSE 80
ENTRYPOINT [ "/bin/bash" ]
CMD [ "/app/run.sh" ]