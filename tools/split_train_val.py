import os
import xml.etree.ElementTree as ET
import numpy as np
import sys
import argparse

import random
import shutil

from PIL import Image
import label_xml2txt

parser=argparse.ArgumentParser()
parser.add_argument("--img_path",default="/home/donggua/文档/datasets/needle/images",type=str,help="img path")
parser.add_argument("--xml_path",default='/home/donggua/文档/datasets/needle/labels',type=str,help='xml path')
#parser.add_argument("--label_path",default="/home/donggua/文档/datasets/baolong/labelTxt",type=str,help="label path")
parser.add_argument("--split_ratio",default=0.15,type=float,help="how much ratio split to val")
parser.add_argument('--resaved_data', action='store_true', default=True, help='restore pic')
parser.add_argument("--output_mode",default='angle',type=str,help='point or angle')


#parser.add_argument("--save_path",default='',type=str,help='saved path to txt')


arg=parser.parse_args()


def check_delete_dir(path):
    if os.path.exists(path):
        shutil.rmtree(path)   
    os.mkdir(path)

def check_delete_file(filepath):    
    if(os.path.exists(filepath)):
        os.remove(filepath)


def get_fileName(filepath):
    name=os.path.basename(filepath)
    name=os.path.splitext(name)
    name=name[0]
    return name

def getxmllistFromRootDir(dir):
    allFiles=[]
    for root,dirs,files in os.walk(dir):
        for filespath in files:
            filepath=os.path.join(root,filespath)
            allFiles.append(filepath)
    return allFiles


def check_img_label(imgpath,labelpath):
    #输入img和label路径，输出imglist和labellist
    img_list=[]
    label_list=[]
    if not os.path.exists(imgpath):
        raise "imgpath is not exit!"
    if not os.path.exists(labelpath):
        raise "labelpath is not exit!"
    #获得imgpath内的所有图片名称
    imagenames=getxmllistFromRootDir(imgpath)

    key=lambda x:str(get_fileName(x))
    imagenames=sorted(imagenames,key=key)

    #获得imgparh内的所有label名称
    labelnames=getxmllistFromRootDir(labelpath)
    labelnames=sorted(labelnames,key=key)

    #取出与img对应的label，放入最终list
    for imagename in imagenames:
        #提取出img的名称
        img_name=get_fileName(imagename)
        for labelname in labelnames:
            if os.path.splitext(labelname)[-1]not in ['.xml','.txt']:
                continue
            label_name=get_fileName(labelname)
            if img_name==label_name:
                img_list.append(imagename)
                label_list.append(labelname)
                labelnames.remove(labelname)
                break

    return img_list,label_list


#将分割后的train或者val列表信息保存到txt文件中
def saved_result_to_txt(img_list,label_list,saved_path):
    root=os.path.dirname(saved_path)
    imgtxtpath=os.path.join(root,"imageNums.txt")
    labeltxtpath=os.path.join(root,"labelNums.txt")

    check_delete_file(imgtxtpath)
    check_delete_file(labeltxtpath)
   
    img_file=open(imgtxtpath,'w')
    label_file=open(labeltxtpath,'w')

    lens=len(img_list)
    img_file.write(str(lens)+'\n')
    label_file.write(str(lens)+'\n')

    for i in range(0,lens):
        img_file.write(str(img_list[i])+'\n')
        label_file.write(str(label_list[i])+'\n')
    img_file.close()
    label_file.close()      

#分割trian和val数据集
def split_train_val(imgpath,labelpath,split_ratio,resaved_data):
    #对应imghe和label
    img_list,label_list=check_img_label(imgpath,labelpath)
   
    #判断train和val数量是否有问题
    if len(img_list)==0 or len(label_list)==0 or len(img_list)!=len(label_list):
        raise 'error: train or val sets is not right!'

    #切分train和val数据集
    nums=len(img_list)
    split_nums=int(nums*split_ratio)
    val_img=[]
    val_label=[]
    for i in range(split_nums):
        num=len(img_list)
        random_index=random.randint(0,num)
        val_img.append(img_list[random_index])
        val_label.append(label_list[random_index])
        del(img_list[random_index])
        del(label_list[random_index])
    
    train_img=img_list
    train_label=label_list

    #获得保存路径，创建root文件夹
    root=img_list[0].split(os.sep)
    root=root[:-2]
    root=os.sep.join(root)+os.sep+"result"
    if os.path.exists(root):
        shutil.rmtree(root)
    os.mkdir(root)

    #创建train和val文件夹
    train_path=os.path.join(root,'train')
    val_path=os.path.join(root,'val')
    os.mkdir(train_path)
    os.mkdir(val_path)

    #创建train和val中保存的image和label的文件夹
    train_img_path=os.path.join(train_path,'images')
    train_label_path=os.path.join(train_path,'labelTxt')
    val_img_path=os.path.join(val_path,'images')
    val_label_path=os.path.join(val_path,'labelTxt')

    os.mkdir(train_img_path)
    os.mkdir(train_label_path)
    os.mkdir(val_img_path)
    os.mkdir(val_label_path)

    if resaved_data:
        for imgpath in train_img:
            shutil.copy(imgpath,train_img_path)
            continue

            name=os.path.basename(imgpath)
            savedimg=os.path.join(train_img_path,name)
            img=Image.open(imgpath)
            img.save(savedimg)
            img.close()


        for imgpath in val_img:
            shutil.copy(imgpath,val_img_path)
            continue

            name=os.path.basename(imgpath)
            savedimg=os.path.join(val_img_path,name)
            img=Image.open(imgpath)
            img.save(savedimg)
            img.close()

        for path in train_label:
            shutil.copy(path,train_label_path)

        for path in val_label:
            shutil.copy(path,val_label_path)
    
    #保存train和val转换后的信息，保存为内容是imagepath.txt和labelpath.txt
    saved_result_to_txt(train_img,train_label,train_img_path)
    saved_result_to_txt(val_img,val_label,val_img_path)


if __name__ == "__main__": 
    img_path=arg.img_path
    xml_path=arg.xml_path
    split_ratio=arg.split_ratio
    resaved_data=arg.resaved_data
    output_mode=arg.output_mode

    label_path=label_xml2txt.xml2cocotxt(xml_path,'',output_mode)
    split_train_val(img_path,label_path,split_ratio,resaved_data)

    #saved_to_txt(img_list,label_list)