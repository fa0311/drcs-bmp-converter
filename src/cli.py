#!/usr/bin/env python3
import argparse
import glob
from pathlib import Path

from PIL import Image

from drcs_converter import parse_drcs_bmp


def convert_single_file(input_path: Path, output_path: Path):
    data = input_path.read_bytes()
    rgba = parse_drcs_bmp(data)
    img = Image.fromarray(rgba, mode="RGBA")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(output_path)


def main():
    parser = argparse.ArgumentParser(description="Convert DRCS BMP files to PNG")
    parser.add_argument("input", help="Input file or glob pattern")
    parser.add_argument("output", help="Output directory or file")
    args = parser.parse_args()
    
    input_files = glob.glob(args.input)
    
    input_path_list = [Path(p) for p in input_files]
    output_path = Path(args.output)
    
    for input_file in sorted(input_path_list):
        output_file = output_path / (input_file.stem + ".png")
        convert_single_file(input_file, output_file)
        print(f"[OK] {input_file} -> {output_file}")
    
