#!/usr/env/bin python3

import downloadutils as dlu

import subprocess
from tempfile import TemporaryDirectory
from zipfile import ZipFile
from pathlib import Path
from os import mkdir

def main():
    scriptpath = Path(__file__).resolve().parent
    projectpath = scriptpath.parent.parent
    installpath = projectpath.joinpath('subprojects', 'opencv4')
    print(f'Installing  OpenCV 4.2.0 to {installpath}')

    install_opencv(installpath)

def install_opencv(installpath: Path):
    url = 'https://github.com/opencv/opencv/archive/4.2.0.zip'
    expectedchecksum = '55bd939079d141a50fca74bde5b61b339dd0f0ece6320ec76859aaff03c90d9f'

    with TemporaryDirectory() as tmpdir:
        dlpath = Path(tmpdir).joinpath(url.split('/')[-1])

        print(f'Downloading OpenCV-4.2.0 to {dlpath}\n')
        dlu.download_file(url, dlpath, dlu.erase_then_print)

        print('Testing checksum... ', end='', flush=True)
        checksum = dlu.file_checksum(dlpath).hexdigest()
        if checksum == expectedchecksum:
            print(f'Checksums match! ({checksum})')
        else:
            print(
                'Checksum mismatch! (expected above, downloaded below)\n' +
                f'{expectedchecksum}\n{downloadedchecksum}\nAborting!')
            return 1

        print(f'Extracting zip to {tmpdir}... ', end='', flush=True)
        with ZipFile(dlpath, 'r') as zipped:
            zipped.extractall(tmpdir)
        print('Success!')

        builddir = Path(tmpdir).joinpath('build')
        print(f'Making build folder at {builddir}')
        mkdir(builddir)

        srcpath = Path(tmpdir).joinpath('opencv-4.2.0')
        cmake_command = [
            'cmake',
            f'-S{srcpath}', # Path to source
            f'-B{builddir}', # Path to build
            '-DCMAKE_BUILD_TYPE=Release',
            f'-DCMAKE_INSTALL_PREFIX={installpath}'
        ]
        print(f'Running cmake with: {cmake_command}')
        cmake_proc = subprocess.run(cmake_command)

        make_command = [
            'make',
            'install',
            '-j4',
            '-C', # Where to run make
            str(builddir)
        ]
        print(f'Running make with: {make_command}')
        make_proc = subprocess.run(make_command)

    print('--- All donezo! ---')

if __name__ == '__main__':
    main()