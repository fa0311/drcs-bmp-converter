FROM python:3.13-slim

WORKDIR /app

# Install package and dependencies
COPY pyproject.toml requirements.txt ./
COPY drcs_bmp_converter/ ./drcs_bmp_converter/

# Install the package
RUN pip install --no-cache-dir -e .

ENTRYPOINT ["drcs-bmp-converter"]
