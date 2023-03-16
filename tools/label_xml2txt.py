
import os
import xml.etree.ElementTree as ET
import numpy as np
import sys
import argparse


parser=argparse.ArgumentParser()
parser.add_argument("--xml_path",default='/home/donggua/文档/datasets/baolong/labels',type=str,help='xml path')
parser.add_argument("--save_path",default='',type=str,help='saved path to txt')
parser.add_argument("--output_mode",default='angle',type=str,help='point or angle')

arg=parser.parse_args()


def getxmllistFromRootDir(dir):
    allFiles=[]
    for root,dirs,files in os.walk(dir):
        for filespath in files:
            filepath=os.path.join(root,filespath)
            allFiles.append(filepath)
    return allFiles

def angle2points(input):
    if len(input)==5:
         cx,cy,w,h,angle=input[0],input[1],input[2],input[3],input[4]
        
        #下算法是基于h>=w进行的计算，h必须大于w，当小于时互换，角度去补角
         if h<w:
            temp=h
            h=w
            w=temp
            angle=angle+np.pi/2
         
         h=h/2
         w=w/2

         #计算两个短边的中点坐标
         c1x=cx+h*np.sin(np.pi-angle)
         c1y=cy+h*np.cos(np.pi-angle)
         c2x=cx+h*np.sin(-angle)
         c2y=cy+h*np.cos(-angle)


         #计算短边1的两个顶点坐标
         yw=w*np.sin(angle)
         xw=w*np.cos(angle)
         p1x=c1x-xw
         p1y=c1y-yw
         p2x=c1x+xw
         p2y=c1y+yw

         #算短边2的两个顶点坐标

         p3x=c2x-xw
         p3y=c2y-yw
         p4x=c2x+xw
         p4y=c2y+yw

         return [p1x,p1y,p2x,p2y,p3x,p3y,p4x,p4y]

    else :
        print("input counts error:"+len(input))
        return None

def check_dir(dir):
    if(os.path.exists(dir)):
        for root,dirs,files in os.walk(dir):
            for filespath in files:
                filepath=os.path.join(root,filespath)
                os.remove(filepath)
        os.rmdir(dir)
    os.mkdir(dir)
     

def xml2cocotxt(xmlpath, txtpath,mode):
    #check输出文件夹是否存在，存在删除内所有文件及文件夹，保留该父文件夹
    if txtpath=='':
        txtpath=os.path.dirname(xmlpath)
        txtpath =os.path.join(txtpath,'labelTxt')
    
    check_dir(txtpath)

    #得到文件夹内的所有文件
    filelist=getxmllistFromRootDir(xmlpath)

    #将xml转换为txt
    for xmlfile in  filelist:
        name=os.path.basename(xmlfile)
        name=os.path.splitext(name)
        name=name[0]
        out_file=open(os.path.join(txtpath,name+".txt"),'w')
        tree=ET.parse(xmlfile)
        root=tree.getroot()
        for obj in root.iter('object'):
            cls=obj.find('name')
            if cls==None:
                continue
            cls=cls.text
            difficult=obj.find('difficult')
            difficult= int(difficult.text) if difficult !=None else 0

            if difficult<2:
                robndbox=obj.find('robndbox')
                if robndbox ==None:
                    continue
                if mode=='point':
                    robndbox=[float(robndbox.find(x).text) for x in ['cx','cy','w','h','angle']]
                    out_file.write(" ".join([str(a) for a in(*robndbox,cls,difficult)])+'\n')
                elif mode=='angle':
                    robndbox=[float(robndbox.find(x).text) for x in ['cx','cy','w','h','angle']]
                    robndbox=angle2points(robndbox)
                    robndbox=[float('%.1f'%a) for a in robndbox]
                    out_file.write(" ".join([str(a) for a in(*robndbox,cls,difficult)])+'\n')
        out_file.close()
    return txtpath

if __name__ == "__main__":
    
    
    xmlpath=arg.xml_path
    txtpath=arg.save_path
    outputmode=arg.output_mode
    xml2cocotxt(xmlpath,txtpath,outputmode)