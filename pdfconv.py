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

import fitz
import time
import re
import os
import sys
import numpy as np

TMPDIR = 'tmp/'
PARSEIMG = True
OCR_ONLINE = False

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

# 写入文件
def write_file(path, text, ftype, debug=False):
    with open(path, ftype) as f:
        if debug:
            print("write", len(text))
        f.write(text)
        f.close()

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

    t0 = time.clock()
    doc = fitz.open(inpath)
    lenXREF = doc.xrefLength()
    print("文件名:{}, 页数: {}, 对象: {}".format(inpath, len(doc), lenXREF - 1))

    imgcount = 0
    for i,page in enumerate(doc):
        t1 = time.clock()
        # 文字
        text = page.get_text()
        if len(text) > 0:
             write_file(outpath, text, 'a')
        # 图片        
        imglist = page.get_images() # 解析该页中图片
        for item in imglist:
            xref = item[0]
            pix = fitz.Pixmap(doc, xref)
            new_name = "{}.png".format(imgcount)
            # 如果pix.n<5,可以直接存为PNG
            path = os.path.join(TMPDIR, new_name)
            if pix.n < 5:
                pix.writePNG(path)
            # 否则先转换CMYK
            else:
                pix0 = fitz.Pixmap(fitz.csRGB, pix)
                pix0.writePNG(path)
                pix0 = None
            pix = None
            if OCR_ONLINE:
                text = img_to_str_baidu(path)
            else:
                text = img_to_str_tesseract(path)
            print("img->text", text)
            write_file(outpath, text, 'a')
            write_file(outpath, '\n' + '-----------' + '\n', 'a')
            imgcount += 1
        print("page {} 运行时间:{}s".format(i, {t1 - t0}))

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("请将pdf文件路径作为参数")
        sys.exit(-1)
    pdffile = sys.argv[1]
    tmpfile = pdffile.replace('pdf','tmp')
    txtfile = pdffile.replace('pdf','txt')
    parse(pdffile, tmpfile)
    adjust(tmpfile, txtfile)
