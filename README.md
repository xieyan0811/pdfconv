# pdfconv 中文PDF转TXT的实用工具

### 1.  运行环境：

    Python 3

### 2.  依赖工具：

    $ sudo pip install pdfminer3k # PDF格式解析
    $ sudo apt-get install tesseract-ocr # 离线OCR工具tesseract
    $ sudo apt-get install tesseract-ocr-chi-sim # OCR简体中文支持
    $ sudo pip install pytesseract # OCR工具的Python支持包
    $ sudo pip install baidu-aip # 在线OCR：百度提供的字符识别工具。

### 3.  示例:
    $ python pdfconv.py xxxx.pdf
运行之后生成 xxxx.txt

### 2.	一些问题

程序通过百余行代码实现，解析普通的PDF文件问题不大，但仍存在一些问题：
    
(1)	本文中使用的pdfminer库中对pdf文件中数据块的解析不够完美，只支持主流的jpg、bmp格式文件，有一些pdf中的图片无法被识别。

(2)	竖版文字也被识别成横版。

(3)	解析字符型文本时，比较简单粗暴，对于比较特殊的版式不一定按照从上到下，从左到右的顺序解析，有待更进。

(4)	程序目前以支持中文PDF文件为主，支持其它语言需要在代码中稍做调整。
