#!/usr/bin/env python3

import subprocess
import curses
from requests import get as requests_get
from tempfile import TemporaryDirectory
from os import chmod, stat, mkdir
from functools import partial
from threading import Thread
from platform import system
from zipfile import ZipFile
from hashlib import sha256
from pathlib import Path
from time import sleep

def main(stdscr):
    stdscr.clear()
    # Disable cursor.
    curses.curs_set(0)

    # Split screen horizontally in two windows.
    win1 = curses.newwin(int(curses.LINES * 1/3), curses.COLS, 0, 0)
    win1.scrollok(True)
    win2 = curses.newwin(int(curses.LINES * 2/3), curses.COLS, int(curses.LINES * 1/3), 0)
    win2.scrollok(True)

    scriptpath = Path(__file__).resolve().parent
    projectpath = scriptpath.parent.parent
    depspath = projectpath.joinpath('deps')

    qt_install_thread = Thread(target=install_qt, args=[win1, scriptpath, depspath], daemon=True)
    qt_install_thread.start()

    opencv_install_thread = Thread(target=install_opencv, args=[win2, depspath], daemon=True)
    opencv_install_thread.start()

    stdscr.refresh()
    win1.refresh()
    win2.refresh()

    alive = True
    while alive == True:
        alive = False
        alive = False or qt_install_thread.is_alive()
        alive = alive or opencv_install_thread.is_alive()

        win1.refresh()
        win2.refresh()
        # Let's add a little delay just to go a little lighter on resources.
        sleep(0.5)

    stdscr.getch()

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

def write_qt_installscript(os: str, filepath: str, install_to: str, appendedscriptfilepath: str):
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

def install_qt(out, scriptpath: Path, depspath: Path):
    downloads = {
        # see http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-windows-x86-5.12.7.exe.mirrorlist
        'Windows': {
            'link': 'http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-windows-x86-5.14.1.exe',
            'sha256': '24b6fb28ca07c46a25f40387e591e0484d82cb45ba252f4f5f1fa0ae24aba53b',
        },
        # see http://download.qt.io/official_releases/qt/5.14/5.14.1/qt-opensource-linux-x64-5.12.7.run.mirrorlist
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
        out.addstr('No information on how to download on system "{}", not installing qt!'.format(operatingsystem))
        return 1

    with TemporaryDirectory() as tmpdir:
        url = downloads[operatingsystem]['link']
        installerpath = Path(tmpdir).joinpath(url.split('/')[-1])

        out.addstr('Downloading Qt 5.14.1 offline installer to {}\n'.format(installerpath))
        download_file(url, installerpath, lambda x: out.addstr(out.getyx()[0], 0, x))

        out.addstr(out.getyx()[0] + 1, 0, 'Testing checksum... ')
        expectedchecksum = downloads[operatingsystem]['sha256']
        checksum = file_checksum(installerpath).hexdigest()
        if checksum == expectedchecksum:
            out.addstr('Checksums match! ({})\n'.format(checksum))
        else:
            out.addstr(
                "Checksum mismatch! (expected above, downloaded below)\n{}\n{}\nAborting!"
                .format(expectedchecksum, downloadedchecksum))
            return 1

        installscriptpath = Path(tmpdir).joinpath('installscript.qs.js')
        out.addstr('Writing installscript to {}\n'.format(installscriptpath))
        write_qt_installscript(
            os=operatingsystem,
            filepath=installscriptpath,
            install_to=depspath.joinpath('Qt'),
            appendedscriptfilepath=scriptpath.joinpath('qtinstaller-noninteractive.qs.js'))

        # chmod +x installerpath
        out.addstr('Enabling executable bit in {}\n'.format(installerpath))
        chmod(installerpath, stat(installerpath).st_mode | 0o111)
        qt_command = [
            str(installerpath),
            #'--verbose',
            '--silent',
            '--script',
            str(installscriptpath)]
        out.addstr('Running command {}\n'.format(qt_command))
        subprocess.run(qt_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    out.addstr('--- All donezo! ---')

def install_opencv(out, depspath: Path):
    url = 'https://github.com/opencv/opencv/archive/4.2.0.zip'
    expectedchecksum = '55bd939079d141a50fca74bde5b61b339dd0f0ece6320ec76859aaff03c90d9f'

    with TemporaryDirectory() as tmpdir:
        dlpath = Path(tmpdir).joinpath(url.split('/')[-1])

        out.addstr('Downloading OpenCV-4.2.0 to {}\n'.format(dlpath))
        download_file(url, dlpath, lambda x: out.addstr(out.getyx()[0], 0, x))

        out.addstr(out.getyx()[0] + 1, 0, 'Testing checksum... ')
        checksum = file_checksum(dlpath).hexdigest()
        if checksum == expectedchecksum:
            out.addstr('Checksums match! ({})\n'.format(checksum))
        else:
            out.addstr(
                'Checksum mismatch! (expected above, downloaded below)\n{}\n{}\nAborting!'
                .format(expectedchecksum, downloadedchecksum))
            return 1

        out.addstr('Extracting zip to {}... '.format(tmpdir))
        with ZipFile(dlpath, 'r') as zipped:
            zipped.extractall(tmpdir)
        out.addstr('Success!\n')

        builddir = Path(tmpdir).joinpath('build')
        out.addstr('Making folder build folder at {}\n'.format(builddir))
        mkdir(builddir)

        cmake_command = [
            'cmake',
            '-S{}'.format(Path(tmpdir).joinpath('opencv-4.2.0')), # Path to source
            '-B{}'.format(builddir), # Path to build
            '-DCMAKE_BUILD_TYPE=Release',
            '-DCMAKE_INSTALL_PREFIX={}'.format(depspath.joinpath('OpenCV'))
        ]
        out.addstr('Running command: {}'.format(cmake_command))
        cmake_proc = subprocess.Popen(cmake_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in cmake_proc.stdout:
            out.addstr('\t{}\n'.format(line.decode().strip()))

        make_command = [
            'make',
            'install',
            '-j4',
            '-C', # Where to run make
            str(builddir.joinpath)
        ]
        out.addstr('Running command: {}'.format(make_command))
        make_proc = subprocess.Popen(make_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for line in make_proc.stdout:
            out.addstr('\t{}\n'.format(line.decode().strip()))

    out.addstr('--- All donezo! ---')

if __name__ == "__main__":
    curses.wrapper(main)
