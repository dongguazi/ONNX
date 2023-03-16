标注注意事项：
  --1.使用rolabelme进行带旋转框的目标检测的标注格式:
  [cx,cy,w,h,angel],
  ---2.label_xml2txt.py转换后的格式:
  [x1,y1,x2,y2,x3,y3,x4,y4,class,difculty]

  ---3.split_train_val.py将数据集按照比例分割成train和val，其中每个文件里有images和labelTxt两个文件夹。