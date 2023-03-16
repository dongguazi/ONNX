import os
import xml.etree.ElementTree as ET
import numpy as np
import json
import sys
from tqdm import tqdm
import argparse

parser=argparse.ArgumentParser()
parser.add_argument("--json_path",default='/home/donggua/文档/my_utils/instances_val2017.json',type=str,help='json from coco datasets')
parser.add_argument("--save_path",default='/home/donggua/下载/txt',type=str,help='saved path to txt')
arg=parser.parse_args()

def convert(size, box):
    dw = 1. / (size[0])
    dh = 1. / (size[1])
    x = box[0] + box[2] / 2.0
    y = box[1] + box[3] / 2.0
    w = box[2]
    h = box[3]

    x = x * dw
    w = w * dw
    y = y * dh
    h = h * dh
    return (x, y, w, h)

def json2cocotxt(json_file,txtpath):

    #处理输出文件，删除之前文件夹内的文件
    if(os.path.exists(txtpath)):
        for root,dirs,files in os.walk(txtpath):
            for filespath in files:
                filepath=os.path.join(root,filespath)
                os.remove(filepath)
        os.rmdir(txtpath)
    os.mkdir(txtpath)

    #read json
    datas = json.load(open(json_file, 'r', encoding='utf-8'))
    
    #对coco数据集的id进行重新映射，原数据集是从1-80，现在为0-79
    id_map = {}  # coco数据集的id不连续！重新映射一下再输出！
    for i, category in enumerate(datas['categories']):
        id_map[category['id']] = i

    #找出最大图像的数量
    max_id=0
    for img in datas['images']:
        max_id=max(max_id,img['id'])

     #处理annotations,通过提前建表减少时间复杂度。通过imageid查询annotations的索引位置，在找到对应的数据
     #同一个image_id的数据索引加入到该列表，方便以后通过索引找到对应的数据
     #一个image_id可能对应着多个标注的数据，通过索引可以拿到这些标注的数据
     #image_id————indexes————  data[index]  for index in indexes
    ann_dict=[[] for i in range(max_id+1)]
    for i,anno in enumerate(datas['annotations']):
        ann_dict[anno['image_id']].append(i)

    for img in tqdm(datas['images']):
        filename=img['file_name']
        img_height=img['height']
        img_width=img['width']
        img_id=img['id']
        head,tail=os.path.splitext(filename)
        txt_name=os.path.join(txtpath,head+'.txt')
        f_txt=open(txt_name,'w')

         #通过image_id，找到多个对应的index，再通过index拿到标注的数据内容
        for ann_id in ann_dict[img_id]:
            ann=datas['annotations'][ann_id]
            bbox=convert((img_width,img_height),ann['bbox'])
            f_txt.write('%s %s %s %s %s\n'%(id_map[ann["category_id"]],bbox[0],bbox[1],bbox[2],bbox[3]))
            #f_txt.write("%s %s %s %s %s\n" % (id_map[ann["category_id"]], box[0], box[1], box[2], box[3]))
        f_txt.close()


if __name__ == '__main__':
    json_file = arg.json_path  # COCO Object Instance 类型的标注
    txtpath = arg.save_path  # 保存的路径
    json2cocotxt(json_file,txtpath)






    

