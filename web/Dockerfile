FROM django-example-shortcut:latest

# TODO: Should the db url be built here instead of the compose yml?
#ARG _DB_HOST
#ARG _DB_PORT
#ARG _DB_NAME
#ARG _DB_USER
#ARG _DB_PASSWORD
#ENV DATABASE_URL="postgres://${_DB_USER}:${_DB_PASSWORD}@${_DB_HOST}:${_DB_PORT}/${_DB_NAME}"

EXPOSE 8000
ENTRYPOINT ["python", "manage.py"]
CMD ["runserver", "0.0.0.0:8000"]

# Allow nonroot to use port 80?
# RUN setcap CAP_NET_BIND_SERVICE=+eip /path/to/binary

# Create a non-root user to run the app
RUN useradd --create-home appuser
USER appuser

COPY --chown=appuser . /app

WORKDIR /app
