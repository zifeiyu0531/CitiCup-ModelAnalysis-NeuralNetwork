########################
#
# 模型调用过程
# 2019/7/1 v1.0
#
########################
from gensim.models import word2vec
import xlrd
from xlutils.copy import copy

global MODEL_NAME, TARGET_FILE_NAME, TARGET_LIST, WORD_LIST
MODEL_NAME = 'CitiCup_500.model'            # 模型名
TARGET_FILE_NAME = '600054_3.txt'       # 待分析文件名
TARGET_LIST = [['董事会', '组成'], ['全年', '收入'], ['股权', '分配']]   # 指标列表
WORD_LIST = []                          # 待分析词列表


##########################################
# test_step()
# 验证过程入口函数
##########################################
def test_step():
    cut_txt()
    check_grade()


##########################################
# cut_txt()
# 将待验证文件分词，存入WORD_LIST
##########################################
def cut_txt():
    import jieba
    global TARGET_FILE_NAME, WORD_LIST
    try:
        old_file = open(TARGET_FILE_NAME, 'r', encoding='utf-8')
        section_list = old_file.read().split('$')               # 分段
        for section in section_list:                            # 将段落分词，存入WORD_LIST
            cut_text = jieba.cut(section, cut_all=False)
            new_text = ' '.join(cut_text)
            new_list = new_text.split(' ')
            WORD_LIST.append(new_list)
        print(WORD_LIST)
        old_file.close()
    except BaseException as e:
        print(Exception, ":", e)


##########################################
# check_grade()
# 相似度检测
##########################################
def check_grade():
    global MODEL_NAME, TARGET_LIST, WORD_LIST
    xlsx_file = xlrd.open_workbook('model_500.xls')         # 获取表格文件
    xlsx_file_copy = copy(xlsx_file)
    xlsx_table = xlsx_file_copy.get_sheet(0)
    model = word2vec.Word2Vec.load(MODEL_NAME)          # 加载已训练好的模型
    for index, lists in enumerate(WORD_LIST):
        for key_index, keys in enumerate(TARGET_LIST):  # 计算两个词的相似度/相关程度
            time_list = []
            for key_word in keys:
                time = 0
                for word in lists:
                    try:
                        grade = model.wv.similarity(key_word, word)
                        if grade > 0.7:
                            time += 1
                    except KeyError:
                        pass
                time_list.append(time)
            print("指标"+str(keys)+"在第"+str(index+1)+"段中匹配的次数为"+str(time_list))
            xlsx_table.write(index+1, key_index+1, str(time_list))
    print("-------------------------------\n")
    xlsx_file_copy.save('model_500.xls')


def main():
    test_step()


if __name__ == '__main__':
    main()
