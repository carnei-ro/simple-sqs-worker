FROM python:3.7-alpine3.13 AS compile_image

# hadolint ignore=DL3013
RUN apk add --no-cache build-base \
    && pip install -U setuptools pip \
    && python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONASYNCIODEBUG=1

COPY requirements.txt .
RUN pip install -r requirements.txt

FROM python:3.7-alpine3.13

LABEL \
    maintainer="SRE Team" \
    br.com.ifood.type="worker" \
    br.com.ifood.name="SQS Worker" \
    br.com.ifood.vcs-ref="https://github.com/carnei-ro/simple-sqs-worker"

# gosu & tini

ARG gosu_version=1.12
ARG tini_version=0.19.0

RUN set -ex \
 && wget -q -O /sbin/gosu "https://github.com/tianon/gosu/releases/download/${gosu_version}/gosu-amd64" \
 && wget -q -O /sbin/tini "https://github.com/krallin/tini/releases/download/v${tini_version}/tini-static-amd64" \
 && chmod -v 755 /sbin/gosu /sbin/tini \
 && gosu --version \
 && tini --version

# Application

ENV APP_DIR=/app \
    APP_USER=worker \
    PATH="/opt/venv/bin:$PATH"

RUN set -ex \
 && addgroup -g 673 "$APP_USER" \
 && adduser -D -u 673 -G "$APP_USER" "$APP_USER"

COPY --from=compile_image /opt/venv /opt/venv

COPY worker "$APP_DIR"

COPY entrypoint.sh /sbin/entrypoint.sh

WORKDIR /app

EXPOSE 8081

ENTRYPOINT ["tini", "--", "/sbin/entrypoint.sh"]

CMD ["app:run"]
