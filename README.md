# pyreports_crawler

## 版本
v0.2

## 运行环境

Python 2.7

[pdfminer](https://github.com/euske/pdfminer)

[jieba](https://github.com/fxsjy/jieba)

## 功能

- 从研报和年报获取正文
- 利用TextRank算法从研报中提取带有权重的关键词
- 用研报关键词提取年报关键句子并标权重

## 改进空间

- [x] ~~文件夹导入~~
- [x] ~~从结果里去除特殊标点~~
- [x] ~~训练集文件夹和年报文件夹内无文件时报错~~
- [x] ~~如果训练集变动,对关键词词典进行更新~~
- [ ] 按行业分类将分析报告和年报分类
- [ ] 从结果中排除冗余文字
   - [ ] 改进LTTextBox的比较条件
   - [ ] *创建冗余项排除列表*
   - [ ] 找到合适的统计学习模型来检测冗余项
- [ ] 从正文提取含有关键数据的句子
- [ ] 排除页眉页脚
- [ ] 提取图片
- [ ] 修改为面向对象性编程
- [ ] *训练自定义jieba分词词典*
   - [ ] *为自定义jieba词典的新单词标注词性*
- [ ] 从正文提取关键词和对应数据并导入数据库
- [ ] *使用 [Tesseract](https://github.com/tesseract-ocr/tesseract) 或者 [ABBYY FineReader Engine](https://www.abbyy.com/en-us/ocr-sdk-windows/)进行OCR*

## 其他需求

- [x] ~~从年报里提取关键词~~
   - [ ] TextRank权重
   - [x] ~~词频~~
- [x] ~~优先提取“董事会报告”或“经营情况讨论分析”~~

## Version
v0.2

## Requirements

Python 2.7

[pdfminer](https://github.com/euske/pdfminer)

[jieba](https://github.com/fxsjy/jieba)

## Feature

- Extract context from analytic reports and annual reports.
- Use TextRank to extract keywords with weight from analytic reports.
- Use keywords from analytic reports to extract context in annual reports.

## Room for improvement

- [x] ~~Processing in directory.~~
- [x] ~~Clean some special Chinese marks from result.~~
- [x] ~~Raise ERROR if there is nothing in training and report directory.~~
- [x] ~~Update keywords dictionary if training set is changed.~~
- [ ] Classify analytic reports and annual reports by sectors.
- [ ] Exclude redundant text from result.
   - [ ] Improve comparison conditions in LTTextBox (determine_obj_text()).
   - [ ] *Create exclusion list for redundant keywords.*
   - [ ] Find and use ML model to detect redundant.
- [ ] Extract sentences those contain important data from context.
- [ ] Page header and page footer excludes.
- [ ] Image Extraction.
- [ ] OOP.
- [ ] *Train a custom jieba dictionary for text segmentation.*
   - [ ] *Add POS to new words in the custom jieba dictionary.*
- [ ] Extract keywords and data from context and import to database.
- [ ] *OCR by using [Tesseract](https://github.com/tesseract-ocr/tesseract) or [ABBYY FineReader Engine](https://www.abbyy.com/en-us/ocr-sdk-windows/).*

## Other Requests

- [x] ~~Extract keywords from annaul report~~
  - [ ] TextRank weight
  - [x] ~~Word count~~
- [x] ~~Extract 'Directors' Report' or 'Business Conditions Analysis' first.~~