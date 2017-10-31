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





class AnnualReport(PDFCrawlerFile):
    def __init__(self, pdf_name):
        PDFFile.__init__(self, pdf_name)
        self.laparams = LAParams()

        pass
