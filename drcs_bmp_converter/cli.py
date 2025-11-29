import glob
from pathlib import Path

from PIL import Image
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .drcs_converter import parse_drcs_bmp


class ArgParse(BaseSettings):
    model_config = SettingsConfigDict(cli_parse_args=True)
    input: str = Field(
        alias="input",
        default="./input/*.bmp",
        description="Input file path (supports glob patterns)",
    )
    output: str = Field(
        alias="output",
        default="./output/",
        description="Output directory",
    )


def convert_single_file(input_path: Path, output_path: Path):
    data = input_path.read_bytes()
    rgba = parse_drcs_bmp(data)
    img = Image.fromarray(rgba, mode="RGBA")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def main():
    args = ArgParse()

    input_path_list = [Path(p) for p in glob.glob(args.input)]
    output_path = Path(args.output)

    for input_file in sorted(input_path_list):
        output_file = output_path / (input_file.stem + ".png")
        convert_single_file(input_file, output_file)
        print(f"[OK] {input_file} -> {output_file}")
