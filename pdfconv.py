######################################
# tesseract OCR

from PIL import Image
import pytesseract

def img_to_str_tesseract(image_path, lang='chi_sim'):
    return pytesseract.image_to_string(Image.open(image_path), lang)
  
######################################
# 百度 OCR

from aip import AipOcr

config = {
    'appId': '',
    'apiKey': '',
    'secretKey': ''
}
client = AipOcr(**config)

def img_to_str_baidu(image_path):
    with open(image_path, 'rb') as fp:
        image = fp.read()
        result = client.basicGeneral(image)
        if 'words_result' in result:
            return '\n'.join([w['words'] for w in result['words_result']])
    return ""

######################################
# 解析PDF文件

from pdfminer.pdftypes import LITERALS_DCT_DECODE, LITERALS_FLATE_DECODE
from pdfminer.pdfcolor import LITERAL_DEVICE_GRAY, LITERAL_DEVICE_RGB
from pdfminer.pdfparser import PDFParser,PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LTTextBoxHorizontal, LAParams, LTFigure, LTImage, LTChar, LTTextLine
from pdfminer.pdfinterp import PDFTextExtractionNotAllowed
import os
import sys
import numpy as np
import importlib
importlib.reload(sys)

TMPDIR = 'tmp/'
PARSEIMG = True
OCR_ONLINE = False

# 保存图片
def write_image(image, outdir):
    stream = image.stream
    filters = stream.get_filters()
    if len(filters) == 1 and filters[0] in LITERALS_DCT_DECODE:
        ext = '.jpg'
        data = stream.get_rawdata()
    elif image.colorspace is LITERAL_DEVICE_RGB:
        ext = '.bmp'
        data = create_bmp(stream.get_data(), stream.bits*3, image.width, image.height)
    elif image.colorspace is LITERAL_DEVICE_GRAY:
        ext = '.bmp'
        data = create_bmp(stream.get_data(), stream.bits, image.width, image.height)
    else:
        ext = '.img'
        data = stream.get_data()
    name = image.name+ext
    path = os.path.join(outdir, name)
    fp = open(path, 'wb')
    fp.write(data)
    fp.close()
    return path, len(data)

# 写入文件
def write_file(path, text, ftype, debug=False):
    with open(path, ftype) as f:
        if debug:
            print("write", len(text))
        f.write(text)

# 去掉文中多余的回车
def adjust(inpath, outpath):
    f = open(inpath)
    lines = f.readlines()
    arr = [len(line) for line in lines]
    length = np.median(arr) # 行字符数中值
    
    string = ""
    for line in lines:
        if len(line) >= length and line[-1]=='\n':
            string += line[:-1] # 去掉句尾的回车
        elif line == '-----------\n':
            pass
        else:
            string += line
    write_file(outpath, string, 'w')
    return

# 解析每个数据块
def parse_section(layout, outpath, debug = False):
    for x in layout:
        if (isinstance(x, LTTextBoxHorizontal)): # 文本
            write_file(outpath, x.get_text(), 'a')
        elif (isinstance(x, LTFigure)):
            parse_section(x, outpath)
        elif (isinstance(x, LTImage)) and PARSEIMG: # 图片
            path,length = write_image(x, TMPDIR)
            if length > 0:
                if OCR_ONLINE:
                    write_file(outpath, img_to_str_baidu(path), 'a')
                else:
                    write_file(outpath, img_to_str_tesseract(path), 'a')
                write_file(outpath, '\n' + '-----------' + '\n', 'a')

# 删除文件  
def remove(path):
    if not os.path.exists(path):
        return
    if os.path.isfile(path):
        os.remove(path)
        return
    dirs = os.listdir(path)
    for f in dirs:
        file_name = os.path.join(path, f)
        if os.path.isfile(file_name):
            os.remove(file_name)
        else:
            remove(file_name)
    os.rmdir(path)

# 解析PDF文件
def parse(inpath, outpath):
    remove(TMPDIR) # 清除临时目录 
    os.mkdir(TMPDIR)
    remove(outpath) # 清除输出文件
    fp = open(inpath, 'rb')
    praser = PDFParser(fp) # pdf文档分析器
    doc = PDFDocument() # 创建一个PDF文档
    praser.set_document(doc) # 连接分析器与文档对象
    doc.set_parser(praser)
    doc.initialize()
    
    if not doc.is_extractable: # 是否提供txt转换
        raise PDFTextExtractionNotAllowed
    else:
        rsrcmgr = PDFResourceManager() # 创建PDF资源管理器
        laparams = LAParams() 
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device) # 创建PDF解释器对象
                
        for idx,page in enumerate(doc.get_pages()): # 获取page列表
            interpreter.process_page(page)
            layout = device.get_result()
            print("parse", idx)
            parse_section(layout, outpath)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("请将pdf文件路径作为参数")
        sys.exit(-1)
    pdffile = sys.argv[1]
    tmpfile = pdffile.replace('pdf','tmp')
    txtfile = pdffile.replace('pdf','txt')
    parse(pdffile, tmpfile)
    adjust(tmpfile, txtfile)


