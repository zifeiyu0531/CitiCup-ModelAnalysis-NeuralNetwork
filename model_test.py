########################
#
# 模型调用过程
# 2019/7/1 v1.0
#
########################
from gensim.models import word2vec

global MODEL_NAME, TARGET_FILE_NAME, TARGET_LIST, WORD_LIST
MODEL_NAME = 'CitiCup.model'            # 模型名
TARGET_FILE_NAME = '600054_3.txt'       # 待分析文件名
TARGET_LIST = [['董事会', '组成'], ['全年', '收入'], ['股权', '分配']]   # 指标列表
WORD_LIST = []                          # 待分析词列表


def test_step():
    cut_txt()
    check_grade()


def cut_txt():
    import jieba
    global TARGET_FILE_NAME, WORD_LIST
    try:
        old_file = open(TARGET_FILE_NAME, 'r', encoding='utf-8')
        old_text = old_file.read()
        cut_text = jieba.cut(old_text, cut_all=False)
        new_text = ' '.join(cut_text)
        WORD_LIST = new_text.split(' ')
        print(WORD_LIST)
        old_file.close()
        new_file = open(TARGET_FILE_NAME, 'w', encoding='utf-8')
        new_file.write(new_text)
        new_file.close()
    except BaseException as e:
        print(Exception, ":", e)


def check_grade():
    global MODEL_NAME, TARGET_LIST, WORD_LIST
    model = word2vec.Word2Vec.load(MODEL_NAME)  # 加载已训练好的模型
    for keys in TARGET_LIST:                    # 计算两个词的相似度/相关程度
        times = 0
        for key_word in keys:
            for word in WORD_LIST:
                try:
                    grade = model.wv.similarity(key_word, word)
                    if grade > 0.7:
                        times += 1
                except KeyError:
                    pass
        print("指标"+str(keys)+"匹配的次数为"+str(times))
    print("-------------------------------\n")


def main():
    test_step()


if __name__ == '__main__':
    main()
