# DRCS-BMP Converter

日本のデジタル放送（ARIB）に含まれる DRCS 外字（Dynamic Resolution Character Set）
を収録した 独自 BMP 形式（DRCS-BMP） を RGBA PNG に変換するツールです。

```bash
docker run -v $(pwd)/config/drcs:/app/input -v $(pwd)/config/drcspng:/app/output ghcr.io/fa0311/drcs-bmp-converter/drcs-bmp-converter-docker:latest -i /app/input/*.bmp -o /app/output/
```
