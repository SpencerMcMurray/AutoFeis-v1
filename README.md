# AutoFeis

A Python 3 Flask-based website. AutoFeis manages the creation, registration,
and tabulation of Irish Dance competitions, it also allows for creators to
manage their competition.

Its distinguishing factor is tabulation. It uses computer vision and a neural network
to provide very fast tabulation of results from Irish Dancing competitions.

Its worth noting that the tabulation could be easily be extended to other judged 
sports with handwritten marks as well.

## Dependencies

* Flask
* pymysql
* tensorflow
* numpy
* cv2

## Author

*Spencer McMurray*, Computer Science student at The University of Toronto

## Acknowledgments

* Convolutional neural network is altered from [this repo](https://github.com/Hvass-Labs/TensorFlow-Tutorials)
* Digit reading was built upon [this](https://stackoverflow.com/questions/51867834/recognizing-handwritten-digits-off-a-scanned-image) answer

