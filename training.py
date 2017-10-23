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


def layouts_pdf_mining(pdf_file, page_range, pdf_pwd='', *args):
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
    page_start = page_range[0]
    page_end = page_range[-1]
    if page_end == -1:
        page_end = len(page_objs)
    for page in page_objs[page_start: page_end]:
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
    keywords = []
    if fn.__name__ == "jieba_text_rank":
        keywords = fn('\n'.join(sentence_list))
    elif fn.__name__ == "jieba_text_word_count_dict":
        keywords = fn(sentence_list)
    return keywords


def jieba_text_rank(sentences):
    # use TextRank to get topK keywords in file
    tr = jieba.analyse.textrank(
        sentences, topK=50, withWeight=True, allowPOS=('n', 'v'))
    # return list of tuples
    return tr


def jieba_text_word_count_dict(sentence_list):
    wd = {}
    accepted_chars = re.compile(u"[\u4E00-\u9FD5]+")
    for sentence in sentence_list:
        # determine whether sentence is needed
        if re_determine_sentence(sentence):
            # jieba.cut_for_search return keywords with duplicated characters
            jieba_sentence_list = list(jieba.cut_for_search(sentence))
            for js_word in jieba_sentence_list:
                if accepted_chars.match(js_word) is None or len(js_word) <= 1:
                    continue
                try:
                    wd[js_word] += 1
                except KeyError:
                    wd[js_word] = 1
    return wd.items()


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


def get_keyword_dict(keyword_dict, keyword_dict_file):
    try:
        fpr = open(keyword_dict_file, 'rb')
        ks = fpr.read().strip().decode("utf-8")
        key_val = ks.split(b"\r\n")
        for kv in key_val:
            k, v = kv.split(b' ')
            if k in keyword_dict.keys():
                keyword_dict[k] += float(v)
            else:
                keyword_dict[k] = float(v)
    except ValueError:
        pass
    except IOError:
        pass
    return keyword_dict


def keyword_files_to_dict(keywords_dir):
    keyword_dict = {}
    # keywords receive the (word, count) tuple
    dir_files = os.listdir(keywords_dir)
    for keywords_file in dir_files:
        keyword_dict = get_keyword_dict(keyword_dict, keywords_dir + '/' + keywords_file)
    write_file_keywords(keyword_dict.items(), "keyword_dict.txt")


def write_file_keywords(keywords, file_name):
    fpw = open(file_name, 'w')
    for k, v in keywords:
        fpw.write(k.encode("utf-8") + ' ' + str(v) + "\n")
    fpw.close()


def main(training_path, keyword_path, fn, page_range):
    training_dir_files = os.listdir(training_path)
    keyword_dir_files = os.listdir(keyword_path)
    if len(training_dir_files) == 0:
        for dict_file in keyword_dir_files:
            os.remove(keyword_path + '/' + dict_file)
        print("No training files exist!")
        return
    try:
        fpr = open("training_filename.txt", 'rb')
        trained = fpr.read().strip()
        trained_files = trained.split(b"\r\n")
        fpr.close()
    except IOError:
        trained_files = []
    # if there are files have been deleted in training directory
    # remove corresponding keyword_dict file in keyword directory
    if len(trained_files) != 0 and len(trained_files[0]) != 0:
        # condition needs to be edited
        for trained_file in trained_files:
            if trained_file not in training_dir_files:
                keyword_dict_file = keyword_path + '/' + trained_file + ".txt"
                os.remove(keyword_dict_file)
    for pdf_file in training_dir_files:
        if pdf_file not in trained_files:
            file_path = training_path + '/' + pdf_file
            layouts = layouts_pdf_mining(file_path, page_range)
            keywords = text_process(fn, layouts)
            write_file_keywords(keywords, keyword_path + '/' + pdf_file + ".txt")
    keyword_files_to_dict(keyword_path)
    # write trained files
    trained_files = os.listdir(training_path)
    fpw = open("training_filename.txt", 'w')
    for trained_file in trained_files:
        fpw.write(trained_file + "\n")
    fpw.close()
    return


if __name__ == "__main__":
    training = "./training"
    keyword = "./keywords"
    main(training, keyword, jieba_text_rank, [0, 1])
    # main(annualreport, annualreport_keywords, jieba_text_word_count_dict, )
