import os
import io
import struct
import builtins
from collections import namedtuple
from typing import Union, Optional

chunk_info_names = ('signature', 'size', 'align', 'skip', 'start', 'datapos')
ChunkInfo = namedtuple('ChunkInfo', chunk_info_names)

class ILFFReader:
    def __init__(self, stream: Union[io.BytesIO, io.BufferedReader]):
        self._stream = stream
        self._chunks = []

        # Seek to end of stream and save position (stream size)
        self._stream.seek(0, os.SEEK_END)
        size = self._stream.tell()
        #print(f"Total size: {size}")

        # Seek to begin of stream and try to read ILFF header
        self._stream.seek(0, os.SEEK_SET)
        try:
            temp = struct.unpack('=4s3I4s', self._stream.read(20)) #Read first 4 bytes as string, 3 pairs of 4 as positive integer and 4 bytes as string again
            #print(temp)
        except struct.error as e:
            raise ValueError("Invalid ILFF header structure") from e

        self._signature = temp[0]
        self._size = temp[1]
        self._align = temp[2]
        self._skip = temp[3]
        self._formatsig = temp[4]

        if self._signature != b'ILFF':
            raise ValueError(f"Signature must be b'ILFF', found {self._signature}")
        if self._size != size:
            raise ValueError("File size mismatch")
        if self._align != 4:
            raise ValueError("Align must be 4")
        if self._skip != 0:
            raise ValueError("Skip must be 0")

        pos = self._stream.tell()

        if pos != 20:
            raise ValueError("Incorrect stream position after header")

        while True:
            chunk_start = self._stream.tell()
            #print(f"Chunk Starts: {chunk_start}")
            try:
                temp = struct.unpack('=4s3I', self._stream.read(16))
                #print(temp)
            except struct.error as e:
                raise ValueError("Invalid chunk header structure") from e

            chunk_signature, chunk_size, chunk_align, chunk_skip = temp
            chunk_datapos = self._stream.tell()
            #print(f"Chunk_signature: {chunk_signature}")
            #print(f"Chunk_datapos: {chunk_datapos}")


            self._chunks.append((chunk_signature, chunk_size, chunk_align,
                                 chunk_skip, chunk_start, chunk_datapos))

            #print(self._chunks[-1])

            pos = self._stream.seek(pos + chunk_skip, os.SEEK_SET)
            #print(pos)

            if chunk_skip == 0:
                self._stream.seek(pos + 16 + chunk_size, os.SEEK_SET)
                break

        # Check if nothing remained
        if self._stream.read():
            raise ValueError("Parsing failed, extra data found")

    def close(self):
        self._stream.close()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def signatures(self):
        return [item[0] for item in self._chunks]

    def find(self, chunk_signature: bytes) -> bool:
        return chunk_signature in self.signatures()

    def seek(self, chunk_signature: bytes, skipone: bool = False) -> Optional[ChunkInfo]:
        skiped = False

        for item in self._chunks:
            if item[0] == chunk_signature:
                if skipone and not skiped:
                    skiped = True
                    continue
                self._stream.seek(item[5])
                return ChunkInfo(*item)
        return None

    def read(self, chunk_signature: bytes, skipone: bool = False) -> Optional[bytes]:
        chunk_info = self.seek(chunk_signature, skipone)
        if chunk_info:
            return self._stream.read(chunk_info.size)
        return None

    def info(self, chunk_signature: bytes, skipone: bool = False) -> Optional[ChunkInfo]:
        skiped = False
        for item in self._chunks:
            if item[0] == chunk_signature:
                if skipone and not skiped:
                    skiped = True
                    continue
                return ChunkInfo(*item)
        return None

def open_ilff(filepath: Union[str, io.BytesIO], mode: Optional[str] = None) -> ILFFReader:
    if isinstance(filepath, str):
        print("Opening ILFF")
        return ILFFReader(builtins.open(filepath, 'rb'))
    elif isinstance(filepath, io.BytesIO):
        return ILFFReader(filepath)
    else:
        raise ValueError("Expected a file path or BytesIO object")