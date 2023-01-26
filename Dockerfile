FROM python:3.9.16-slim-buster

WORKDIR /app

RUN apt-get update \
  && apt-get install -y build-essential curl \
  && curl -sL https://deb.nodesource.com/setup_14.x | bash - \
  && apt-get install -y nodejs --no-install-recommends \
  && rm -rf /var/lib/apt/lists/* /usr/share/doc /usr/share/man \
  && apt-get clean \
  && useradd --create-home python \
  && chown python:python -R /app

USER python

ENV DEBUG="${DEBUG}" \
    PYTHONUNBUFFERED="true" \
    PATH="${PATH}:/home/python/.local/bin" \
    USER="python"

COPY --chown=python:python . .

RUN pip install .

RUN python manage.py tailwind install --no-input
RUN python manage.py tailwind build --no-input
RUN python manage.py collectstatic --no-input

ENTRYPOINT ["python", "manage.py"]
CMD ["--help"]
