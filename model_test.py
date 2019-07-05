########################
#
# 模型调用过程
# 2019/7/1 v1.0
#
########################
from gensim.models import word2vec
import openpyxl
import gensim
import jieba
from xlutils.copy import copy

global MODEL_NAME, TARGET_FILE_NAME, TARGET_LIST, WORD_LIST
MODEL_NAME = 'models\CitiCup_1000.model.bin'            # 模型名
TARGET_FILE_NAME = 'test\\600054_3.txt'       # 待分析文件名
TARGET_LIST = []                        # 指标列表
WORD_LIST = []                          # 待分析词列表


##########################################
# test_step()
# 验证过程入口函数
##########################################
def test_step():
    get_targets()
    cut_txt()
    check_grade()


##########################################
# get_targets()
# 获取指标列表TARGET_LIST
##########################################
def get_targets():
    global TARGET_LIST   # 指标列表
    if len(TARGET_LIST) == 0:
        TARGET_LIST = [[],[],[],[]]
        xlsx_file = openpyxl.load_workbook('output\model_1000.xlsx')  # 获取表格文件
        sufficiency_table = xlsx_file.worksheets[0]
        comparability_table = xlsx_file.worksheets[1]
        truth_table = xlsx_file.worksheets[2]
        relativity_table = xlsx_file.worksheets[3]

        sufficiency_list = {
            '1公司年报是否披露主要的财务指标' : '资产负债率、流动比率、速动比率；应收账款周转率、存货周转率；资本金利润率、销售利润率、营业收入利税率、成本费用利润率',
            '2公司年报是否披露其他应收、应付款等带"其他"字样的项目的详细情况' : '其他应收款、其他应付款、赔款、罚款、应收的出租包装物租金、为职工垫付的水电费、应由职工负担的医药费、租入包装物支付的押金、其他各种应收、暂付款项',
            '3公司是否披露营业外收支的详细情况' : '罚款支出，捐赠支出，非常损失',
            '4公司是否披露披露募集资金有关项目的进展' : '合同完工进度、按累计实际发生',
            '5投资项目未达到计划进度和收益的，公司是否披露原因' : '项目进展受挫的原因、项目失败的原因、项目未到计划收益的原因',
            '6公司募集资金投资项目变更的是否披露变更原因' : '投资项目变更的原因、放弃......项目',
            '7公司年报是否说明关联交易的必要性、持续性' : '关联交易、代理、租赁、经营租赁、融资租赁、租赁合同、代理、代理销售货物、代理签订合同、研究与开发转移、许可协议、代表企业或由企业代表另一方进行债务结算、关键管理人薪酬、担保情况、担保、保证、抵押、质押、留置、定金',
            '8公司若不存在重大诉讼、仲裁事项，是否在年报中明确声明' : '没有重大诉讼、没有仲裁事项、申诉或权利仲裁、申诉程序、利益或合约仲裁、公正理由、协商或调节、服从协议',
            '9公司是否披露支付的审计费用金额' : '审计费用',
            '10若不存在任何重大担保合同，公司是否在年报中声明' : '没有重大担保合同',
            '11公司年报是否披露更换会计事务所的原因' : '会计师事务所变更、更换会计事务所的原因',
            '12公司是否披露社会责任报告书' : '社会责任报告书',
            '13年报中是否披露公司建有网站' : '本公司网址',
            '14公司年报中是否披露重要的会计政策' : '主要会计政策',
            '15是否及时披露董事会、监事会和股东大会的决议报告' : '决议刊登披露日期'
        }
        comparability_list = {
            '1是否未发生会计变更' : '报告期内公司未发生重大会计政策变更、报告期内公司未发生重大会计估计变更、报告期内公司未发生重大会计差错更正',
            '2是否披露发生会计变更原因' : '会计变更原因'
        }
        truth_list = {
            '1两职分离能有效地提高监督和控制经理层的能力、维护董事会的独立性、保证会计信息披露质量。' : '两职分离',
            '2是否有独立董事' : '独立董事',
            '3是否有审计委员会' : '审计委员会',
            '4公司是否披露内部控制' : '组织机构控制、人员素质控制、职务分离控制、业务记录控制、授权批准控制',
        }
        relativity_list = {
            '1公司是否根据风险情况，披露拟采取的对策' : '风险预防措施',
            '2公司是否自愿披露经审核的新年度盈利预测 ' : '盈利预测',
            '3公司年报是否披露新年度的经营计划或经营目标' : '下一年经营目标',
            '4公司是否对公司战略进行描述' : '战略',
            '5公司是否进行行业未来的发展趋势分析' : '公司未来，行业未来',
            '6公司是否对面临的市场竞争格局进行分析' : '市场格局，市场规模，市场分析，竞争格局',
            '7公司是否对未来公司发展机遇和挑战进行分析' : '下一年的机会，面临的挑战',
            '8公司是否对面临的风险因素进行分析' : '面临的风险，潜在，威胁'
        }

        for index, key in enumerate(sufficiency_list):
            sufficiency_list[key] = sufficiency_list[key].replace('、', '').replace('；', '').replace('.', '').replace('，', '')
            cut_text = jieba.lcut(sufficiency_list[key], cut_all=False)
            cut_set = set(cut_text)         #消除重复数据
            cut_text = list(cut_set)
            word_index = 0
            while word_index < len(cut_text):
                if len(cut_text[word_index]) < 2:
                    cut_text.pop(word_index)
                word_index = word_index + 1
            TARGET_LIST[0].append(cut_text)
            sufficiency_table.cell(1, index+2, str(cut_text))

        for index, key in enumerate(comparability_list):
            comparability_list[key] = comparability_list[key].replace('、', '').replace('；', '').replace('.', '').replace('，', '')
            cut_text = jieba.lcut(comparability_list[key], cut_all=False)
            cut_set = set(cut_text)         #消除重复数据
            cut_text = list(cut_set)
            word_index = 0
            while word_index < len(cut_text):
                if len(cut_text[word_index]) < 2:
                    cut_text.pop(word_index)
                word_index = word_index + 1
            TARGET_LIST[1].append(cut_text)
            comparability_table.cell(1, index+2, str(cut_text))

        for index, key in enumerate(truth_list):
            truth_list[key] = truth_list[key].replace('、', '').replace('；', '').replace('.', '').replace('，', '')
            cut_text = jieba.lcut(truth_list[key], cut_all=False)
            cut_set = set(cut_text)         #消除重复数据
            cut_text = list(cut_set)
            word_index = 0
            while word_index < len(cut_text):
                if len(cut_text[word_index]) < 2:
                    cut_text.pop(word_index)
                word_index = word_index + 1
            TARGET_LIST[2].append(cut_text)
            truth_table.cell(1, index+2, str(cut_text))

        for index, key in enumerate(relativity_list):
            relativity_list[key] = relativity_list[key].replace('、', '').replace('；', '').replace('.', '').replace('，', '')
            cut_text = jieba.lcut(relativity_list[key], cut_all=False)
            cut_set = set(cut_text)         #消除重复数据
            cut_text = list(cut_set)
            word_index = 0
            while word_index < len(cut_text):
                if len(cut_text[word_index]) < 2:
                    cut_text.pop(word_index)
                word_index = word_index + 1
            TARGET_LIST[3].append(cut_text)
            relativity_table.cell(1, index+2, str(cut_text))

        xlsx_file.save(filename='output\model_1000.xlsx')


##########################################
# cut_txt()
# 将待验证文件分词，存入WORD_LIST
##########################################
def cut_txt():
    global TARGET_FILE_NAME, WORD_LIST
    try:
        old_file = open(TARGET_FILE_NAME, 'r', encoding='utf-8')
        section_list = old_file.read().split('$')               # 分段
        for section in section_list:                            # 将段落分词，存入WORD_LIST
            cut_text = jieba.cut(section, cut_all=False)
            new_text = ' '.join(cut_text)
            new_list = new_text.split(' ')
            WORD_LIST.append(new_list)
        old_file.close()
    except BaseException as e:
        print(Exception, ":", e)


##########################################
# check_grade()
# 相似度检测
##########################################
def check_grade():
    global MODEL_NAME, TARGET_LIST, WORD_LIST
    xlsx_file = openpyxl.load_workbook('output\model_1000.xlsx')         # 获取表格文件
    xlsx_table = xlsx_file.worksheets[0]
    model = gensim.models.KeyedVectors.load_word2vec_format(MODEL_NAME, binary=True)          # 加载已训练好的模型

    for index, lists in enumerate(WORD_LIST):
        for target_index, sub_target_list in enumerate(TARGET_LIST):  # 计算两个词的相似度/相关程度
            for key_index, keys in enumerate(sub_target_list):
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
                xlsx_file.worksheets[target_index].cell(index+2, key_index+2, str(time_list))

    xlsx_file.save(filename='output\model_1000.xlsx')


def main():
    test_step()


if __name__ == '__main__':
    main()
