import os
import re
from training import layouts_pdf_mining, layout_text_extract, get_keyword_dict, context_cleaning


def report_text_process(layouts, keyword_dict):
    # pages_context contains page_text, page_text
    pages_context = layout_text_extract(layouts)
    sentence_list = []
    rs = []
    for page_text in pages_context:
        # clean text and split by full stop
        # sentence_list stores all sentences in the file
        sentence_list += context_cleaning(''.join(page_text)).split('\xe3\x80\x82')
    for s in sentence_list:
        ss = sentence_compare(s, keyword_dict)
        if ss:
            rs.append((s, ss))
    rss = sorted(rs, key=lambda item: (item[1], item[0]))
    return rss


def sentence_compare(sentence, keyword_dict):
    # sentence score: ss
    ss = float()
    for k in keyword_dict.keys():
        if k in sentence:
            # sentence score is summed by keywords' weight
            ss += float(keyword_dict[k])
    return ss


def main(dir_path, pages_num, pdf_pwd):
    try:
        fpr_filename = open("annual_report_filename.txt", "rb")
        r = fpr_filename.read().strip()
        reports_list = r.split(b"\r\n")
        fpr_filename.close()
    except IOError:
        reports_list = []
    fpw_filename = open("annual_report_filename.txt", 'w')
    keyword_dict = get_keyword_dict({}, "keyword_dict.txt")
    dir_files = os.listdir(dir_path)
    for pdf_file in dir_files:
        if pdf_file not in reports_list:
            fpw_filename.write(pdf_file + "\n")
            file_path = dir_path + '/' + pdf_file
            layouts = layouts_pdf_mining(file_path, pages_num, pdf_pwd)
            result_sentence_sorted = report_text_process(layouts, keyword_dict)
            fpw = open(pdf_file + ".txt", 'w')
            for k, v in result_sentence_sorted:
                fpw.write(str(v) + '\t' + k + "\n")
            fpw.close()


if __name__ == "__main__":
    path = "./annualreport"
    main(path, 0, '')
