FROM mcr.microsoft.com/presidio-analyzer@sha256:286e3fa7f3a7426e775e8564fe1870f1ba8f999d3ab8bbb8cc46a44355d9d6e9

USER root

COPY default.yaml /app/presidio_analyzer/conf/default.yaml
COPY default_analyzer.yaml /app/presidio_analyzer/conf/default_analyzer.yaml
COPY default_recognizers.yaml /app/presidio_analyzer/conf/default_recognizers.yaml

ENV NLP_CONF_FILE=presidio_analyzer/conf/default.yaml
ENV ANALYZER_CONF_FILE=presidio_analyzer/conf/default_analyzer.yaml

RUN python -m spacy download pt_core_news_lg

USER 1001

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:3000/health || exit 1
