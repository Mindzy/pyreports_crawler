import os
import re
from training import layouts_pdf_mining, layout_text_extract, get_keyword_dict, context_cleaning, \
    jieba_text_word_count_dict


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


def find_toc(layouts):
    # to find toc in first 10 pages and return page_range
    rc = re.compile("( )*(\.(\.)+|(\.)+\.)( )*")
    for layout in layouts[:10]:
        dots_condition = 0
        toc_condition = 0
        for l_obj in layout._objs:
            l_obj_text = l_obj.get_text().encode("utf-8").strip()
            if rc.search(l_obj_text) is not None:
                dots_condition += 1
            if "\xe7\x9b\xae\xe5\xbd\x95" in l_obj_text:
                toc_condition += 1
        if dots_condition >= 3 and toc_condition >= 2:
            # find the page number of Directors' report in this page if true
            return __get_page_range(layout)
    return None


def __get_page_range(layout):
    rd = re.compile("(\d)+")
    page_start = 0
    page_end = -1
    l_objs = layout._objs
    for i in range(len(l_objs)):
        l_obj_text = l_objs[i].get_text().encode("utf-8").strip().replace(' ', '')
        if "\xe7\xbb\x8f\xe8\x90\xa5\xe6\x83\x85\xe5\x86\xb5" in l_obj_text \
                or "\xe8\x91\xa3\xe4\xba\x8b\xe4\xbc\x9a\xe6\x8a\xa5\xe5\x91\x8a" in l_obj_text:
            page_start_l = rd.findall(l_obj_text)
            if len(page_start_l) != 0:
                page_start = int(page_start_l[-1]) - 1
            l_obj_text2 = l_objs[i + 1].get_text().encode("utf-8").strip().replace(' ', '')
            page_end_l = rd.findall(l_obj_text2)
            if len(page_end_l) != 0:
                page_end = int(page_end_l[-1]) - 1
        if page_start != 0 and page_end != -1:
            break
    return [page_start, page_end]


def sentence_compare(sentence, keyword_dict):
    # sentence score: ss
    ss = float()
    for k in keyword_dict.keys():
        if k.encode("utf-8") in sentence:
            # sentence score is summed by keywords' weight
            ss += float(keyword_dict[k])
    return ss


def crawl_all(dir_path, page_range, pdf_pwd):
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
            layouts = layouts_pdf_mining(file_path, page_range, pdf_pwd)
            result_sentence_sorted = report_text_process(layouts, keyword_dict)
            fpw = open(pdf_file + ".txt", 'w')
            for k, v in result_sentence_sorted:
                fpw.write(str(v) + '\t' + k + "\n")
            fpw.close()


def main(dir_path, toc_page_range, pdf_pwd):
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
            # find toc in first
            toc_layouts = layouts_pdf_mining(file_path, toc_page_range, pdf_pwd)
            toc_pr = find_toc(toc_layouts)
            layouts = layouts_pdf_mining(file_path, toc_pr, pdf_pwd)
            jieba_text_word_count_dict()


if __name__ == "__main__":
    path = "./annualreport"
    # main(path, [0, -1], '')
    main(path, [0, 10], '')
