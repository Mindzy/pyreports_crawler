# -*- coding: utf-8 -*-
import os
import re
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTTextBoxVertical
import jieba
import jieba.analyse


def layouts_pdf_mining(pdf_file, pages_num=1, pdf_pwd='', *args):
    """Open the pdf document, and apply the function, returning the results"""
    try:
        fp = open(pdf_file, 'rb')
    except IOError:
        """If the file doesn't exist"""
        # edit needed
        pass
    laparams = LAParams()
    parser = PDFParser(fp)
    pdf_doc = PDFDocument(parser, pdf_pwd)
    # if not pdf_doc.is_extractable:
    #     raise PDFTextExtractionNotAllowed
    # Connect the parser and document
    parser.set_document(pdf_doc)
    # Create a PDF resource manager object and device object
    pdf_resource_mgr = PDFResourceManager()
    # Create a PDF page aggregator object.
    pdf_device = PDFPageAggregator(pdf_resource_mgr, laparams=laparams)
    # Create a PDF interpreter object
    pdf_interpreter = PDFPageInterpreter(pdf_resource_mgr, pdf_device)
    # Use a list to store LTPage objects created from each page
    layouts = []
    page_objs = list(PDFPage.create_pages(pdf_doc))
    if pages_num == 0:
        pages_num = len(page_objs)
    for page in page_objs[:pages_num]:
        pdf_interpreter.process_page(page)
        layouts.append(pdf_device.get_result())
    return layouts


def text_process(fn, layouts):
    # pages_context contains page_text, page_text
    pages_context = layout_text_extract(layouts)
    sentence_list = []
    for page_text in pages_context:
        # clean text and split by full stop
        # sentence_list stores all sentences in the file
        sentence_list += context_cleaning(''.join(page_text)).split('\xe3\x80\x82')
    keyword_dict = {}
    if fn.__name__ == "jieba_text_rank":
        keyword_dict = fn('\n'.join(sentence_list))
    elif fn.__name__ == "jieba_text":
        keyword_dict = fn(sentence_list)
    return keyword_dict


def get_keyword_dict(keyword_dict_file):
    keyword_dict = {}
    try:
        fpr = open(keyword_dict_file, 'rb')
        ks = fpr.read().strip()
        key_val = ks.split("\r\n")
        for kv in key_val:
            k, v = kv.split(' ')
            keyword_dict[k] = float(v)
    except IOError:
        pass
    return keyword_dict


def keywords_to_dict(keywords, keyword_dict):
    # keywords recieves the (word, count) tuple
    if keywords is None:
        return
    for w, c in keywords:
        if w in keyword_dict:
            keyword_dict[w] += c
        else:
            keyword_dict[w] = c
    fpw = open("keyword_dict.txt", 'w')
    for k in keyword_dict:
        fpw.write(k.encode("utf-8") + ' ' + str(keyword_dict[k]) + "\n")
    fpw.close()
    print("keyword_dict.txt saved")
    return keyword_dict


def jieba_text_rank(sentences):
    # use TextRank to get topK keywords in file
    tr = jieba.analyse.textrank(
        sentences, topK=50, withWeight=True, allowPOS=('n'))
    return tr


def jieba_text(sentence_list):
    jieba_sentence_list = []
    for sentence in sentence_list:
        # determine whether sentence is needed
        if re_determine_sentence(sentence):
            # jieba.cut_for_search return keywords with duplicated characters
            jieba_sentence = list(jieba.cut_for_search(sentence))
            jieba_sentence_list.append(jieba_sentence)
    return jieba_sentence_list


# improvement needed
def re_determine_sentence(jieba_sentence):
    # Use regular expression to search if the sentence contains any digitals
    rec = re.compile(r'\d+')
    for word in jieba_sentence:
        if re.search(rec, word) is not None:
            return True
    return False


def layout_text_extract(layouts):
    pages_context = []
    for layout in layouts:
        # Use a list to store text on one page
        page_text = []
        for l_obj in layout._objs:
            if type(l_obj) == LTTextBoxHorizontal or type(l_obj) == LTTextBoxVertical:
                l_obj_text = l_obj.get_text().encode("utf-8")
                if determine_obj_text(l_obj_text):
                    page_text.append(l_obj_text)
        pages_context.append(page_text)
    # pages_context is a list contains several page_text lists
    # page_text is a list contains several l_obj_text
    return pages_context


# improvement needed
def determine_obj_text(l_obj_text):
    # Determine whether text is context or not
    if l_obj_text.count('\n') * 10 * 3 < len(l_obj_text):
        return True
    return False


def context_cleaning(context):
    context = context.replace("\n", '')
    context = context.replace("\t", '')
    context = context.replace(' ', '')
    context = context.replace("\xef\x81\xae", '')
    context = context.replace("\xef\xbc\x89", ')')
    context = context.replace("\xef\xbc\x88", '(')
    context = context.replace("\xef\xbc\x9a", ':')
    context = context.replace("\xef\xbc\x8c", ',')
    context = context.replace("\xe2\x80\x94", '-')
    # replace pause mark
    context = context.replace("\xe3\x80\x81", '/')
    return context


def main(dir_path, fn, pages_num):
    keyword_dict = {}
    trained = ''
    try:
        fpr = open("training_filename.txt", 'rb')
        trained = fpr.read().strip()
        trained_files = trained.split("\r\n")
        fpr.close()
    except IOError:
        trained_files = []
    dir_files = os.listdir(dir_path)
    fpw = open("training_filename.txt", 'w')
    if len(trained_files) != 0:
        fpw.write(trained + "\n")
    for pdf_file in dir_files:
        if pdf_file not in trained_files:
            fpw.write(pdf_file + "\n")
            file_path = dir_path + '/' + pdf_file
            layouts = layouts_pdf_mining(file_path, pages_num)
            keywords = text_process(fn, layouts)
            keyword_dict = keywords_to_dict(keywords, keyword_dict)


if __name__ == "__main__":
    path = "./training"
    main(path, jieba_text_rank, 1)
