# syntax=docker/dockerfile:1.7
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

WORKDIR /app

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml uv.lock ./

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project

COPY saveweb_search.py ./
COPY templates ./templates

EXPOSE 8077

CMD ["python", "saveweb_search.py"]
