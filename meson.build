project('vsss', 'cpp',
    version: '0.0.0',
    default_options : [
        'cpp_std=c++17',
        'buildtype=debugoptimized',
    ]
)

deps = []
args = []

deps += dependency('opencv4', version: '>=4.2.0')
deps += dependency('qt5', version: '>=5.9.0',
    modules: [
        'Core',
        'Widgets',
    ]
)

executable(
    'vsss',
    'src/main.cpp',
    dependencies: deps,
    cpp_args: args)
