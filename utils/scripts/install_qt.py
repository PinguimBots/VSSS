#!/usr/bin/env python3

import downloadutils as dlu

import subprocess
from tempfile import TemporaryDirectory
from platform import system
from os import chmod, stat
from pathlib import Path

def main():
    scriptpath = Path(__file__).resolve().parent
    projectpath = scriptpath.parent.parent
    installpath = projectpath.joinpath('subprojects', 'qt5')
    print(f'Installing  Qt 5.14.1 to {installpath}')

    install_qt(scriptpath, installpath)

def write_qt_installscript(os: str, filepath: str, install_to: str, appendedscriptfilepath: str):
    with open(filepath, "wb") as f:
        f.truncate(0) # Erase previous contents

        f.write('var InstallComponents = ['.encode())
        f.write('\"qt.qt5.5141.qtwebengine\",'.encode())
        if (os == 'Linux'):
            f.write('\"qt.qt5.5141.gcc_64\"'.encode())
        elif (os == 'Windows'):
            f.write('\"qt.qt5.5141.win64_msvc2017_64\"'.encode())

        f.write(f'];var InstallPath = String.raw`{install_to}`;'
                # Write is expecting a bytes object and not a str.
                .encode())

        with open(appendedscriptfilepath, 'rb') as asf:
            f.write(asf.read())

def install_qt(scriptpath: Path, installpath: Path):
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
        print(f'No information on how to download on system "{operatingsystem}", not installing qt!')
        return 1

    with TemporaryDirectory() as tmpdir:
        url = downloads[operatingsystem]['link']
        installerpath = Path(tmpdir).joinpath(url.split('/')[-1])

        print(f'Downloading Qt 5.14.1 offline installer to {installerpath}\n')
        dlu.download_file(url, installerpath, dlu.erase_then_print)

        print('Testing checksum... ', end='', flush=True)
        expectedchecksum = downloads[operatingsystem]['sha256']
        checksum = dlu.file_checksum(installerpath).hexdigest()
        if checksum == expectedchecksum:
            print(f'Checksums match! ({checksum})')
        else:
            print(
                "Checksum mismatch! (expected above, downloaded below)\n" +
                f"{expectedchecksum}\n{downloadedchecksum}\nAborting!")
            return 1

        installscriptpath = Path(tmpdir).joinpath('installscript.qs.js')
        print(f'Writing installscript to {installscriptpath}')
        write_qt_installscript(
            os=operatingsystem,
            filepath=installscriptpath,
            install_to=installpath,
            appendedscriptfilepath=scriptpath.joinpath('qtinstaller-noninteractive.qs.js'))

        # chmod +x installerpath
       	print(f'Enabling executable bit in {installerpath}')
        chmod(installerpath, stat(installerpath).st_mode | 0o111)
        qt_command = [
            str(installerpath),
            '--verbose',
            '--script',
            str(installscriptpath)]
        print(f'Running qt install wizard with: {qt_command}')
        subprocess.run(qt_command)

    print('--- All donezo! ---')

if __name__ == "__main__":
    main()