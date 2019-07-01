from gensim.models import word2vec
import os
import gensim
# 此函数作用是对初始语料进行分词处理后，作为训练模型的语料

def train_step(cut_file, save_model_name):
    if not os.path.exists(cut_file):    # 判断文件是否存在，参考：https://www.cnblogs.com/jhao/p/7243043.html
        for i in range(5):
            cut_txt('60000'+str(i)+'_2018_TagsKilled.txt', cut_file, True)  # 须注意文件必须先另存为utf-8编码格式
    if not os.path.exists(save_model_name):     # 判断文件是否存在
        model_train(cut_file, save_model_name)
    else:
        print('此训练模型已经存在，不用再次训练')

def check_step(file_name, cut_file, save_model_name):
    target_list = [['董事会', '组成'], ['全年', '收入'], ['股权', '分配']]
    word_list = []
    cut_txt(file_name, cut_file, False)
    read_txt(file_name, word_list)
    check_grade(target_list, word_list,save_model_name)

def cut_txt(old_file, cut_file, is_train):
    import jieba
    # 分词之后保存的文件名
    try:
        fi = open(old_file, 'r', encoding='utf-8')
    except BaseException as e:  # 因BaseException是所有错误的基类，用它可以获得所有错误类型
        print(Exception, ":", e)    # 追踪错误详细信息

    text = fi.read()  # 获取文本内容
    new_text = jieba.cut(text, cut_all=False)  # 精确模式
    str_out = ' '.join(new_text)
    if(is_train):
        f1 = open(cut_file, 'a+', encoding='utf-8')
        f1.write(str_out)
        f1.close()
    else:
        f2 = open(old_file, 'w', encoding='utf-8')
        f2.write(str_out)
        f2.close()

def model_train(train_file_name, save_model_file):  # model_file_name为训练语料的路径,save_model为保存模型名
    from gensim.models import word2vec
    import gensim
    import logging
    # 模型训练，生成词向量
    logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    sentences = word2vec.Text8Corpus(train_file_name)  # 加载语料
    model = gensim.models.Word2Vec(sentences, size=200, sg=1)  # 训练skip-gram模型; 默认window=5
    model.save(save_model_file)
    model.wv.save_word2vec_format(save_model_file + ".bin", binary=True)   # 以二进制类型保存模型以便重用

def read_txt(file_name, word_list):
    with open(file_name, 'r', encoding='utf-8') as f:
        line = f.readline().strip()
        while line:
            word_list += line.split(" ")
            line = f.readline().strip()
    print(word_list)

def check_grade(target_list, word_list, save_model_name):
    # 加载已训练好的模型
    model_1 = word2vec.Word2Vec.load(save_model_name)
    # 计算两个词的相似度/相关程度
    for keys in target_list:
        times = 0
        for key_word in keys:
            for word in word_list:
                try:
                    grade = model_1.wv.similarity(key_word, word)
                except KeyError:
                    pass
                if(grade > 0.7):
                    times += 1
        print("指标"+str(keys)+"匹配的次数为"+str(times))
    print("-------------------------------\n")

def main():
    cut_file = 'CitiCup_cut.txt'
    save_model_name = 'CitiCup.model'
    file_name = '600054_3.txt'
    is_train = False
    if (is_train):
        train_step(cut_file, save_model_name)
    else:
        check_step(file_name, cut_file, save_model_name)

if __name__ == '__main__':
    main()