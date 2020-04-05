project('vsss', 'cpp',
    version: '0.0.0',
    default_options : [
        'cpp_std=c++17',
        'buildtype=debugoptimized',
    ],
)

sources = files(
    'src/main.cpp',
)

deps = [
    dependency('opencv4', version: '>=4.2.0'),
    dependency('qt5', version: '>=5.9.0',
        modules: [
            'Core',
            'Widgets',
        ]
    ),
]

vsss_exe = executable(
    'vsss',
    sources,
    dependencies: deps,
)
