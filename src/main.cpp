#include <iostream>

#include <opencv2/core/version.hpp>
#include <QtGlobal>

int main()
{
    std::cout << "Using OpenCV: " << CV_VERSION << std::endl;
    std::cout << "Using Qt:     " << qVersion() << std::endl;

    return 0;
}
