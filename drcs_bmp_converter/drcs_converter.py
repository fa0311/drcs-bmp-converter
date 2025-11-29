from dataclasses import dataclass

import numpy as np


class Seek:
    def __init__(self, data: bytes):
        self.data: bytes = data
        self.length: int = len(data)
        self.offset: int = 0

    def read(self, n: int) -> bytes:
        chunk = self.data[self.offset : self.offset + n]
        self.offset += n
        return chunk

    def read_all(self) -> bytes:
        return self.read(self.length - self.offset)

    def read_le_u16(self) -> int:
        b = self.read(2)
        return int.from_bytes(b, "little", signed=False)

    def read_le_u32(self) -> int:
        b = self.read(4)
        return int.from_bytes(b, "little", signed=False)


@dataclass
class DrcsHeader:
    # ファイルヘッダ
    signature: bytes
    # ファイルサイズ
    declared_size: int
    # 予約領域1
    reserved1: int
    # 予約領域2
    reserved2: int
    # ピクセルデータオフセット
    declared_data_offset: int
    # パディング（2バイト）
    padding: bytes
    # DIBヘッダ
    header_size: int
    # 画像幅
    width: int
    # 画像高さ
    height: int
    # プレーン数
    planes: int
    # ビット数
    bit_count: int
    # 圧縮形式
    compression: int
    # 画像サイズ
    size_image: int
    # 水平解像度（ピクセル/メートル）
    x_pels_per_meter: int
    # 垂直解像度（ピクセル/メートル）
    y_pels_per_meter: int
    # 使用色数
    clr_used: int
    # 重要な色数
    clr_important: int

    @staticmethod
    def expected_drcs_header() -> "DrcsHeader":
        return DrcsHeader(
            signature=b"BM",
            declared_size=55050240,
            reserved1=0,
            reserved2=0,
            declared_data_offset=7864320,
            padding=b"\x00\x00",
            header_size=40,
            width=36,
            height=36,
            planes=1,
            bit_count=4,
            compression=0,
            size_image=720,
            x_pels_per_meter=0,
            y_pels_per_meter=0,
            clr_used=0,
            clr_important=0,
        )


@dataclass
class DrcsBody:
    # 16色パレット
    palette: bytes
    # ピクセルインデックス画像
    pixel_indices: bytes


def parse(seek: Seek) -> tuple[DrcsHeader, DrcsBody]:
    header = DrcsHeader(
        signature=seek.read(2),
        declared_size=seek.read_le_u32(),
        reserved1=seek.read_le_u16(),
        reserved2=seek.read_le_u16(),
        declared_data_offset=seek.read_le_u32(),
        padding=seek.read(2),
        header_size=seek.read_le_u32(),
        width=seek.read_le_u32(),
        height=seek.read_le_u32(),
        planes=seek.read_le_u16(),
        bit_count=seek.read_le_u16(),
        compression=seek.read_le_u32(),
        size_image=seek.read_le_u32(),
        x_pels_per_meter=seek.read_le_u32(),
        y_pels_per_meter=seek.read_le_u32(),
        clr_used=seek.read_le_u32(),
        clr_important=seek.read_le_u32(),
    )
    body = DrcsBody(
        palette=seek.read((1 << header.bit_count) * 4),
        pixel_indices=seek.read_all(),
    )
    return header, body


def build_palette_rgba(header: DrcsHeader, body: DrcsBody) -> np.ndarray:
    num_colors = 1 << header.bit_count
    pal = np.frombuffer(body.palette, dtype=np.uint8)
    pal = pal[: num_colors * 4].reshape((num_colors, 4))
    rgb = pal[:, [2, 1, 0]]
    alpha = np.full((num_colors, 1), 255, dtype=np.uint8)
    pal_rgba = np.concatenate([rgb, alpha], axis=1)
    return pal_rgba


def _decode_indices(header: DrcsHeader, body: DrcsBody) -> np.ndarray:
    bytes_per_row_raw = (header.width + 1) // 2
    bytes_per_row_padded = ((bytes_per_row_raw + 3) // 4) * 4
    rows = np.frombuffer(body.pixel_indices, dtype=np.uint8)
    expected = header.height * bytes_per_row_padded
    rows = rows[:expected].reshape((header.height, bytes_per_row_padded))
    rows = rows[::-1, :bytes_per_row_raw]
    hi = rows >> 4
    lo = rows & 0x0F
    interleaved = np.empty((header.height, bytes_per_row_raw * 2), dtype=np.uint8)
    interleaved[:, 0::2] = hi
    interleaved[:, 1::2] = lo
    indices = interleaved[:, : header.width]
    return indices


def parse_drcs_bmp(data: bytes) -> np.ndarray:
    seek = Seek(data)
    header, body = parse(seek)
    assert header == DrcsHeader.expected_drcs_header(), "Invalid DRCS BMP header"
    pal_rgba = build_palette_rgba(header, body)
    indices = _decode_indices(header, body)
    rgba = pal_rgba[indices]
    return rgba.astype(np.uint8)



