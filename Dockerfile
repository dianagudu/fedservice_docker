FROM python:3.10-slim
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ADD https://github.com/mikefarah/yq/releases/download/v4.31.2/yq_linux_amd64 /bin/yq
RUN chmod +x /bin/yq
ADD https://github.com/moparisthebest/static-curl/releases/download/v7.88.1/curl-amd64 /bin/curl
RUN chmod +x /bin/curl

# Install any needed packages specified in requirements.txt
RUN pip install fedservice & \
    pip install flask

COPY app /app
RUN mkdir /log

WORKDIR /app

EXPOSE 11833
ENTRYPOINT [ "/bin/bash" ]
CMD [ "/app/run.sh" ]