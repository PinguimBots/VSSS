#!/usr/bin/env python3

import tempfile
import requests
import sys
import subprocess
import stat
from functools import partial
from platform import system
from pathlib import Path
from hashlib import sha256
from os import chmod, stat as os_stat

def bytes_to(bytes: int, unit: str) -> float:
    units = {
        'kB': float(1 << 10),
        'mB': float(1 << 20),
        'gB': float(1 << 30),
    }

    if unit in units: return bytes / units[unit]
    else: return bytes

def erase_last_lines(n: int = 1):
    for _ in range(n):
        sys.stdout.write('\x1b[1A') # Go to previous line, then
        sys.stdout.write('\x1b[2K') # clear current line.

def download_file(url: str, filepath: str):
    with requests.get(url, stream = True) as r:
        filesize = int(r.headers['Content-length']) # In bytes.
        filesize = bytes_to(filesize, 'mB')

        # Empty print because of the erase_last_lines call later.
        print()

        with open(filepath, 'wb') as f:
            downloaded = 0 # In bytes.
            for chunk in r.iter_content(chunk_size=4096):
                if not chunk: # To filter out keep-alive chunks.
                    continue

                downloaded += len(chunk)
                f.write(chunk)
                erase_last_lines(1)

                print(
                    '\t{:.02f} mB / {:.02f} mB'
                    .format(bytes_to(downloaded, 'mB'), filesize))

def file_checksum(filepath: str) -> str:
    with open(filepath, 'rb') as f:
        checksum = sha256()

        for chunk in iter(partial(f.read, 4096), b''):
            checksum.update(chunk)

        return checksum
    return ''

def write_installscript(os: str, filepath: str, install_to: str, appendedscriptfilepath: str):
    with open(filepath, "wb") as f:
        f.truncate(0) # Erase previous contents

        f.write('var InstallComponents = ['.encode())
        f.write('\"qt.qt5.5141.qtwebengine\",'.encode())
        if (os == 'Linux'):
            f.write('\"qt.qt5.5141.gcc_64\"'.encode())
        elif (os == 'Windows'):
            f.write('\"qt.qt5.5141.win64_msvc2017_64\"'.encode())

        f.write('];var InstallPath = String.raw`{}`;'
                .format(install_to)
                # Write is expecting a bytes object and not a str.
                .encode())

        with open(appendedscriptfilepath, 'rb') as asf:
            f.write(asf.read())

def main():
    downloads = {
        # see http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-windows-x86-5.14.1.exe.mirrorlist
        'Windows': {
            'link': 'http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-windows-x86-5.14.1.exe',
            'sha256': '24b6fb28ca07c46a25f40387e591e0484d82cb45ba252f4f5f1fa0ae24aba53b',
        },
        # see http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-linux-x64-5.14.1.run.mirrorlist
        'Linux': {
            'link': 'http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-linux-x64-5.14.1.run',
            'sha256': '66ef5e8b776daa5d1e3dbf66298f1019b5e48c3bc8418c71ab7e9e290d7783e7',
        },
        # see http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-mac-x64-5.14.1.dmg.mirrorlist
        #'Darwin': {
        #    'link': 'http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-mac-x64-5.14.1.dmg',
        #    'sha256': '08acfa9fcff68e0213b35a30159a94bd663cfa02cca530ac15626d03b1d71459'
        #}
    }

    operatingsystem = system()
    if operatingsystem not in downloads:
        print('No information on how to download on system "{}", aborting!'.format(operatingsystem))
        return 1

    scriptpath = Path(__file__).resolve().parent
    projectpath = scriptpath.parent.parent
    depspath = projectpath.joinpath('deps')
    print('Detected:\n\tscriptpath  = {}\n\tprojectpath = {}\n\tdepspath    = {}'
        .format(scriptpath, projectpath, depspath))

    with tempfile.TemporaryDirectory() as downloaddir:
        expectedchecksum = downloads[operatingsystem]['sha256']
        url = downloads[operatingsystem]['link']
        installerfilename = url.split('/')[-1]
        installerpath = Path(downloaddir).joinpath(installerfilename)

        print('Downloading Qt 5.14.1 offline installer to {}'.format(installerpath))
        download_file(
            url=url,
            filepath=installerpath)

        print('Testing checksum... ', end='', flush=True)
        checksum = file_checksum(installerpath).hexdigest()
        if checksum == expectedchecksum:
            print('Checksums match! ({})'.format(checksum))
        else:
            print(
                "Checksum mismatch! (expected above, downloaded below)\n{}\n{}"
                .format(expectedchecksum, downloadedchecksum))
            print('Aborting!')
            return 1

        installscriptpath = Path(downloaddir).joinpath('installscript.qs.js')
        print('Writing installscipt to {}'.format(installscriptpath))
        write_installscript(
            os=operatingsystem,
            filepath=installscriptpath,
            install_to=depspath.joinpath('Qt'),
            appendedscriptfilepath=scriptpath.joinpath('qtinstaller-noninteractive.qs.js'))

        # chmod +x installerpath
        chmod(installerpath, os_stat(installerpath).st_mode | 0o111)
        subprocess.run([
            installerpath,
            #'--verbose',
            '--script',
            installscriptpath])

if __name__ == "__main__":
    main()
