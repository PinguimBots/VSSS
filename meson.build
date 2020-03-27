project('vsss', 'cpp', default_options : ['cpp_std=c++17'], version: '0.0.1')
deps = []

opencv = dependency('opencv', version: '>=4.2', fallback: ['opencv4', 'opencv'])
deps += opencv

qt_modules = ['Core']
qt = dependency('qt5', modules: qt_modules, required: false)
if not qt.found()
    qt = []
    qt_subproj = subproject('qt5')

    foreach module : qt_modules
        qt += qt_subproj.get_variable('qt5module_' + module)
    endforeach
endif
deps += qt

executable(
    'vsss',
    'src/main.cpp',
    dependencies: deps,
    cpp_args: ['-fPIC'])