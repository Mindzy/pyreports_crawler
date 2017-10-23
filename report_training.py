import os
from training import layouts_pdf_mining, text_process, jieba_text_word_count_dict, write_file_keywords, \
    keyword_files_to_dict
from toc_parser import find_toc


def main(training_path, keyword_path, fn, toc_page_range):
    training_dir_files = os.listdir(training_path)
    keyword_dir_files = os.listdir(keyword_path)
    if len(training_dir_files) == 0:
        for dict_file in keyword_dir_files:
            os.remove(keyword_path + '/' + dict_file)
        print("No training files exist!")
        return
    try:
        fpr = open("report_training_filename.txt", 'rb')
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
            toc_layouts = layouts_pdf_mining(file_path, toc_page_range)
            pr = find_toc(toc_layouts)
            if pr is None:
                continue
            layouts = layouts_pdf_mining(file_path, pr)
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
    training = "./annualreport_training"
    keywords = "./annualreport_keywords"
    main(training, keywords, jieba_text_word_count_dict, [0, 10])
