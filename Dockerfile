FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

ENV VIRTUAL_ENV="/opt/venv"
RUN uv venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --all-extras

COPY . .

EXPOSE 8000

CMD ["uv", "run", "--active", "main.py"]