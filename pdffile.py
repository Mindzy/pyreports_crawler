# -*- coding: utf-8 -*-
import os
import re
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage, PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBoxHorizontal, LTTextBoxVertical
from utils import determine_obj_text, context_cleaning


class PDFFile:
    def __init__(self, pdf_name):
        self.pdf_name = pdf_name
        self.pdf_path = "./"
        self.pdf_password = ''
        return

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.pdf_name)

    def set_pdf_path(self, pdf_path):
        if not os.path.isdir(pdf_path):
            return
        if pdf_path[-1] != '/':
            self.pdf_path = pdf_path + '/'
        else:
            self.pdf_path = pdf_path
        return

    def set_pdf_password(self, pdf_password):
        self.pdf_password = pdf_password
        return


class PDFCrawlerFile(PDFFile):
    def __init__(self, pdf_name):
        PDFFile.__init__(self, pdf_name)
        self.__parser = None
        self.__pdf_doc = None
        self.__pdf_resource_mgr = None
        self.__pdf_device = None
        self.__pdf_interpreter = None
        self.__page_obj_list = None
        self.__laparms = LAParams()
        # need flush before processing
        self.__layouts = None
        self.__pages_context = None # pages_context contains page_text, page_text
        return

    def __repr__(self):
        return '<%s %s>' % (self.__class__.__name__, self.pdf_name)

    # must run before processing
    def layout_mining_init(self):
        pdf_file = self.pdf_path + self.pdf_name
        try:
            fp = open(pdf_file, 'r')
        except IOError:
            """If the file doesn't exist"""
            # TODO edit needed
            return
        self.__parser = PDFParser(fp)
        self.__pdf_doc = PDFDocument(self.__parser, self.pdf_password)
        if not self.__pdf_doc.is_extractable:
            raise PDFTextExtractionNotAllowed
        # Connect the parser and document
        self.__parser.set_document(self.__pdf_doc)
        # Create a PDF resource manager object and device object
        self.__pdf_resource_mgr = PDFResourceManager()
        # Create a PDF page aggregator object.
        self.__pdf_device = PDFPageAggregator(self.__pdf_resource_mgr, laparams=self.__laparms)
        # Create a PDF interpreter object
        self.__pdf_interpreter = PDFPageInterpreter(self.__pdf_resource_mgr, self.__pdf_device)
        # Get page object list from pdf document
        self.__page_obj_list = list(PDFPage.create_pages(self.__pdf_doc))
        return

    def __layout_mining(self, page_range):
        if self.__parser is None:
            raise RuntimeError("Run layout_mining_init() first!")
        """Open the pdf document, and apply the function, returning the results"""
        layouts = []
        page_start = page_range[0]
        page_end = page_range[-1]
        if page_end == -1:
            page_end = len(self.__page_obj_list)
        for page in self.__page_obj_list[page_start: page_end]:
            self.__pdf_interpreter.process_page(page)
            layouts.append(self.__pdf_device.get_result())
            self.__layouts = layouts
        return

    def __layout_text_extract(self):
        pages_context = []
        for layout in self.__layouts:
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
        self.__pages_context = pages_context
        return

    def text_process(self, fn):

        sentence_list = []
        for page_text in self.__pages_context:
            # clean text and split by full stop
            # sentence_list stores all sentences in the file
            sentence_list += context_cleaning(''.join(page_text)).split('\xe3\x80\x82')
        keywords = []
        if fn.__name__ == "__jieba_text_rank":
            keywords = fn('\n'.join(sentence_list))
        elif fn.__name__ == "__jieba_text_word_count_dict":
            keywords = fn(sentence_list)
        return
