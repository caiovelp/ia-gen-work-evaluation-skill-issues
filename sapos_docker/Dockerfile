# Ambiente de teste do SAPOS (ADR 0011). RUBY_VERSION = a da época do commit base.
ARG RUBY_VERSION=3.4.10
FROM ruby:${RUBY_VERSION}-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends \
      sqlite3 libsqlite3-dev libyaml-dev build-essential git firefox-esr nodejs chromium chromium-driver \
    && rm -rf /var/lib/apt/lists/*
# Bases antigas fixam Chrome nos specs de tela; o Selenium Manager não consegue baixar o Chrome
# pela rede do minikube. Usa o Chromium local, sem download, com --no-sandbox (container roda como root).
RUN printf '#!/bin/sh\nexec /usr/bin/chromium --no-sandbox "$@"\n' > /usr/local/bin/google-chrome \
    && chmod +x /usr/local/bin/google-chrome && ln -sf /usr/bin/chromedriver /usr/local/bin/chromedriver
ENV RAILS_ENV=test BUNDLE_PATH=/bundle BUNDLE_WITHOUT=production SECRET_KEY_BASE=chave_falsa_apenas_para_a_suite \
    SELENIUM_BROWSER=chrome SE_OFFLINE=true
WORKDIR /sapos
