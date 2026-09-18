"""Encode/decode Borsh thủ công cho instruction & account data của chương
trình Anchor `history_game` — không phụ thuộc anchorpy/IDL (không cần chạy
`anchor build` để có IDL, chỉ cần khớp đúng thứ tự field trong lib.rs)."""
import hashlib
import struct


def anchor_discriminator(namespace: str, name: str) -> bytes:
    """8 byte đầu của instruction/account data theo chuẩn Anchor.
    namespace: "global" cho instruction, "account" cho account struct."""
    return hashlib.sha256(f"{namespace}:{name}".encode("utf-8")).digest()[:8]


class BorshWriter:
    def __init__(self) -> None:
        self.buf = bytearray()

    def u8(self, v: int) -> "BorshWriter":
        self.buf += struct.pack("<B", v)
        return self

    def u64(self, v: int) -> "BorshWriter":
        self.buf += struct.pack("<Q", v)
        return self

    def i64(self, v: int) -> "BorshWriter":
        self.buf += struct.pack("<q", v)
        return self

    def string(self, s: str) -> "BorshWriter":
        raw = s.encode("utf-8")
        self.buf += struct.pack("<I", len(raw)) + raw
        return self

    def pubkey(self, raw32: bytes) -> "BorshWriter":
        assert len(raw32) == 32
        self.buf += raw32
        return self

    def bytes(self) -> bytes:
        return bytes(self.buf)


class BorshReader:
    def __init__(self, data: bytes, offset: int = 0) -> None:
        self.data = data
        self.offset = offset

    def read_pubkey(self) -> bytes:
        v = self.data[self.offset : self.offset + 32]
        self.offset += 32
        return v

    def read_u8(self) -> int:
        v = self.data[self.offset]
        self.offset += 1
        return v

    def read_u64(self) -> int:
        v = struct.unpack_from("<Q", self.data, self.offset)[0]
        self.offset += 8
        return v

    def read_i64(self) -> int:
        v = struct.unpack_from("<q", self.data, self.offset)[0]
        self.offset += 8
        return v

    def read_string(self) -> str:
        length = struct.unpack_from("<I", self.data, self.offset)[0]
        self.offset += 4
        v = self.data[self.offset : self.offset + length].decode("utf-8")
        self.offset += length
        return v
