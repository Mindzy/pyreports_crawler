import re
from pdfminer.layout import LTTextBoxHorizontal, LTTextBoxVertical


def find_toc(layouts):
    # to find toc in first 10 pages and return page_range
    rc = re.compile("( )*(\.(\.)+|(\.)+\.)( )*")
    for layout in layouts[:10]:
        dots_condition = 0
        toc_condition = 0
        for l_obj in layout._objs:
            if type(l_obj) == LTTextBoxHorizontal or type(l_obj) == LTTextBoxVertical:
                l_obj_text = l_obj.get_text().encode("utf-8").strip()
                if rc.search(l_obj_text) is not None:
                    dots_condition += 1
                if re.search("\xe7\x9b\xae\xe5\xbd\x95", l_obj_text) is not None:
                    toc_condition += 1
        if dots_condition >= 3 and toc_condition >= 2:
            # find the page number of Directors' report in this page if true
            return __get_page_range(layout)
    return None


def __get_page_range(layout):
    rd = re.compile("\d+")
    page_start = 0
    page_end = -1
    l_objs = layout._objs
    for i in range(len(l_objs)):
        # TODO edit
        if type(l_objs[i]) == LTTextBoxHorizontal or type(l_objs[i]) == LTTextBoxVertical:
            l_obj_text = l_objs[i].get_text().encode("utf-8").strip().replace(' ', '')
            if "\xe7\xbb\x8f\xe8\x90\xa5\xe6\x83\x85\xe5\x86\xb5" in l_obj_text \
                    or "\xe8\x91\xa3\xe4\xba\x8b\xe4\xbc\x9a\xe6\x8a\xa5\xe5\x91\x8a" in l_obj_text:
                page_start_l = rd.findall(l_obj_text)
                if len(page_start_l) != 0:
                    page_start = int(page_start_l[-1]) - 1
                l_obj_text2 = l_objs[i + 1].get_text().encode("utf-8").strip().replace(' ', '')
                page_end_l = rd.findall(l_obj_text2)
                if len(page_end_l) != 0:
                    page_end = int(page_end_l[-1]) - 2
            if page_start != 0 and page_end != -1:
                break
    return [page_start, page_end]
