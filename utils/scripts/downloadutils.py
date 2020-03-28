#!/usr/bin/env python3

from requests import get as requests_get
from functools import partial
from hashlib import sha256
from sys import stdout

def download_file(url: str, filepath: str, printfunc):
    bytes_to_mb = lambda x: x / float(1 << 20)

    with requests_get(url, stream = True) as r:
        downloaded = 0
        try:
            filesize = int(r.headers['Content-length']) # In bytes.
            filesize = bytes_to_mb(filesize)
        except KeyError:
            filesize = 0

        with open(filepath, 'wb') as f:
            for chunk in r.iter_content(chunk_size=4096):
                if not chunk: # To filter out keep-alive chunks.
                    continue

                downloaded += len(chunk)
                printfunc(
                    '\t{:.02f} mB / {:.02f} mB'
                    .format(bytes_to_mb(downloaded), filesize))
                f.write(chunk)

def file_checksum(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        checksum = sha256()

        for chunk in iter(partial(f.read, 4096), b''):
            checksum.update(chunk)

        return checksum
    return ''

def erase_then_print(to_be_printed):
    stdout.write('\x1b[1A') # Go to previous line, then
    stdout.write('\x1b[2K') # clear current line.
    print(to_be_printed)