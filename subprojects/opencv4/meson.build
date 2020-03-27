project('opencv4', 'cpp', version: '4.2.0')

libs = [
    'calib3d',
    'core',
    'dnn',
    'features2d',
    'flann',
    'gapi',
    'highgui',
    'imgcodecs',
    'imgproc',
    'ml',
    'objdetect',
    'photo',
    'stitching',
    'videoio',
    'video',
]
libdir = join_paths(meson.current_source_dir(), 'lib')

libs_as_deps = []
foreach lib : libs
    libs_as_deps += meson.get_compiler('cpp').find_library(
        'opencv_' + lib, 
        dirs: libdir)
endforeach

opencv = declare_dependency(
    dependencies: libs_as_deps,
    include_directories: include_directories('include/opencv4')
)