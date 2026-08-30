FROM python:3.11-slim

WORKDIR /app

# Install deps first so this layer is cached across code changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && python -m spacy download en_core_web_sm

COPY light_bulb.py .
COPY cli.py .
COPY spacy_parser.py .
COPY lightbulb_cli ./lightbulb_cli

# The CLI is an interactive REPL reading from stdin, so run the container
# with `-it` (see docker-compose.yml, which sets this up for you).
ENTRYPOINT ["python", "-m", "cli"]
