project('qt5', 'cpp', version: '5.14.1', meson_version: '>=0.53.0')

# This module requires meson >= 0.53.0.
fs = import('fs')

qtpaths = [
    join_paths('5.14.1', 'gcc_64'),
    join_paths('5.14.1', 'msvc2017_64')
]

fullqtpaths = [
    join_paths(meson.current_source_dir(), qtpaths[0]),
    join_paths(meson.current_source_dir(), qtpaths[1]),
]

libpaths = [
    join_paths(fullqtpaths[0], 'lib'),
    join_paths(fullqtpaths[1], 'lib'),
]

pkgconfigpaths = [
    join_paths(libpaths[0], 'pkgconfig'),
    join_paths(libpaths[1], 'pkgconfig'),
]

qt5modules = [
    '3DAnimation',
    '3DQuickInput',
    'Core',
    'Multimedia',
    'PositioningQuick',
    'QuickTemplates2',
    'SerialBus',
    'UiTools',
    'WebView',
    '3DCore',
    '3DQuick',
    'DBus',
    'MultimediaWidgets',
    'PrintSupport',
    'QuickTest',
    'SerialPort',
    'WaylandClient',
    'Widgets',
    '3DExtras',
    '3DQuickRender',
    'Designer',
    'Network',
    'QmlModels',
    'QuickWidgets',
    'Sql',
    'WebChannel',
    'X11Extras',
    '3DInput',
    '3DQuickScene2D',
    'Gamepad',
    'Nfc',
    'Qml',
    'RemoteObjects',
    'Svg',
    'WebEngineCore',
    'XmlPatterns',
    '3DLogic',
    '3DRender',
    'Gui',
    'OpenGLExtensions',
    'QmlWorkerScript',
    'RepParser',
    'Test',
    'WebEngine',
    'Xml',
    '3DQuickAnimation',
    'Bluetooth',
    'Help',
    'OpenGL',
    'QuickControls2',
    'Scxml',
    'TextToSpeech',
    'WebEngineWidgets',
    '3DQuickExtras',
    'Concurrent',
    'Location',
    'Positioning',
    'Quick',
    'Sensors',
    'UiPlugin',
    'WebSockets',
]

foreach module : qt5modules
    args = run_command(
            'pkg-config', 'Qt5' + module, '--cflags-only-other', 
            env: ['PKG_CONFIG_PATH=' + pkgconfigpaths[0] + ':' + pkgconfigpaths[1]]
        ).stdout().strip()
    module_libs = run_command(
            'pkg-config', 'Qt5' + module, '--libs-only-l', 
            env: ['PKG_CONFIG_PATH=' + pkgconfigpaths[0] + ':' + pkgconfigpaths[1]]
        ).stdout().strip().split('-l')
    
    module_deps = []
    foreach module_lib : module_libs
        if module_lib != ''
            module_deps += meson.get_compiler('cpp').find_library(module_lib.strip(), dirs: libpaths)
        endif
    endforeach

    # Meson complains when you pass a non-existent
    # directory to include_directories.
    if fs.exists(qtpaths[0])
        module_as_dep = declare_dependency(
            dependencies: module_deps,
            include_directories: include_directories(
                join_paths(qtpaths[0], 'include'),
                join_paths(qtpaths[0], 'include', 'Qt' + module)
            ),
            compile_args: args,
        )
    else
        module_as_dep = declare_dependency(
            dependencies: module_deps,
            include_directories: include_directories(
                join_paths(qtpaths[1], 'include'),
                join_paths(qtpaths[1], 'include', 'Qt' + module)
            ),
            compile_args: args
        )
    endif

    set_variable(
        'qt5module_' + module,
        module_as_dep
    )
endforeach