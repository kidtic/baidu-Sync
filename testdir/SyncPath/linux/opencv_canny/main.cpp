#include <iostream>
#include "opencv2/opencv.hpp"

using namespace std;
using namespace cv;
int main()
{

    VideoCapture cap(0);
    Mat frame;
    if(!cap.isOpened())
    {
        cout<<"error can't open cap"<<endl;
        return 0;
    }
    while (1)
    {
        cap>>frame;
        Mat dst;
        Canny(frame,dst,100,200);
        imshow("out",dst);
        waitKey(20);
    }
    print("!!!!!!");
    /*
    测试百度云同步盘。在编写代码时候，的稳定性。
    在这里，我写一个sADSAF安抚
    os模块包含普遍的操作系统功能。
    注意：函数参数path是文件或目录，filename是文件的路径，dirname是目录路径
    路径可以是相对路径，也可以是绝对路径
    再一次owowowow
    在虚拟机上继续打字！！！！
    在pop0s上测试！！！！！！！
    在pop0s上测试！！！！！！！

    */
    return 0;
}
