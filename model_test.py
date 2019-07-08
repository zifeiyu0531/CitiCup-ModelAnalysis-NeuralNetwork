########################
#
# 模型调用过程
# 2019/7/1 v1.0
#
########################
import gensim
import jieba
import os
from target import Target
from OtherTargets import OtherTargets

global MODEL_NAME, TARGET_LIST, WORD_LIST, TIME_TARGET, OTHER_TARGET, RESULT
MODEL_NAME = 'models\CitiCup_2000.model.bin'    # 模型名
WORD_LIST = []                                  # 待分析词列表
TIME_TARGET = [[]]
OTHER_TARGET = []
RESULT = []
TARGET_LIST = [
    # 充分性
    [
        Target('1公司年报是否披露主要的财务指标', [
            ['资产', '负债率'],
            ['流动', '比率'],
            ['速动', '比率'],
            ['应收', '账款', '周转率'],
            ['存货', '周转率'],
            ['资本金', '利润率'],
            ['销售', '利润率'],
            ['营业', '收入', '利润率'],
            ['成本', '费用', '利润率']
        ], 'struct'),
        Target('2公司年报是否披露其他应收、应付款等带"其他"字样的项目的详细情况', [
            ['其他', '应收款'],
            ['其他', '应付款'],
            ['赔款'],
            ['罚款'],
            ['出租', '包装物', '租金'],
            ['职工', '水电费'],
            ['职工', '医药费'],
            ['租入', '包装物', '押金'],
            ['暂付']
        ], 'struct'),
        Target('3公司是否披露营业外收支的详细情况', [
            ['罚款', '支出'],
            ['捐赠', '支出'],
            ['非常', '损失']
        ], 'struct'),
        Target('4公司是否披露披露募集资金有关项目的进展', [
            ['合同', '完工', '进度'],
            ['累计', '实际', '发生']
        ], 'struct'),
        Target('5投资项目未达到计划进度和收益的，公司是否披露原因', [
            ['项目', '受挫', '原因'],
            ['项目', '失败', '原因'],
            ['未到', '计划', '原因']
        ], 'union'),
        Target('6公司募集资金投资项目变更的是否披露变更原因', [
            ['投资', '变更', '原因'],
            ['放弃', '项目', '原因']
        ], 'union'),
        Target('7公司年报是否说明关联交易的必要性、持续性', [
            ['关联', '交易'],
            ['经营', '租赁'],
            ['融资', '租赁'],
            ['代理', '销售'],
            ['代理', '签订'],
            ['研发', '转移'],
            ['许可', '协议']
        ], 'union'),
        Target('8公司若不存在重大诉讼、仲裁事项，是否在年报中明确声明', [
            ['没有', '诉讼'],
            ['没有', '仲裁'],
            ['申诉', '仲裁'],
            ['权利', '仲裁'],
            ['利益', '仲裁'],
            ['合约', '仲裁']
        ], 'union'),
        Target('9公司是否披露支付的审计费用金额', [
            ['审计','费用']
        ], 'struct'),
        Target('10若不存在任何重大担保合同，公司是否在年报中声明', [
            ['担保', '合同']
        ], 'struct'),
        Target('11公司年报是否披露更换会计事务所的原因', [
            ['会计', '事务所', '变更', '原因']
        ], 'struct'),
        Target('12公司是否披露社会责任报告书', [
            ['社会', '责任', '报告']
        ], 'struct'),
        Target('13公司年报中是否披露重要的会计政策', [
            ['会计', '政策']
        ], 'struct')
    ],
    # 可比性
    [
        Target('1是否未发生会计变更', [
            ['未发生', '会计', '政策', '变更'],
            ['未发生', '会计', '估计', '变更'],
            ['未发生', '会计', '差错', '更正']
        ], 'union'),
        Target('2是否披露发生会计变更原因', [
            ['会计', '变更', '原因']
        ], 'struct')
    ],
    # 准时性
    [
        Target('1是否及时披露董事会、监事会和股东大会的决议报告', [
            ['决议', '刊登', '日期']
        ], 'struct'),
        Target('2公司第一季报是否按法定时间披露', [], 'time_target', []),
        Target('3公司中报是否按法定时间披露', [], 'time_target', []),
        Target('4公司中报是否一个月内披露', [], 'time_target', []),
        Target('5公司第三季报是否按法定时间披露', [], 'time_target', []),
        Target('6年报是否在法定时间披露', [], 'time_target', []),
        Target('7年报是否在会计年度结束后两个月内披露', [], 'time_target', [])
    ],
    # 真实性
    [
        Target('6两职分离能有效地提高监督和控制经理层的能力、维护董事会的独立性、保证会计信息披露质量。', [
            ['两职', '分离'],
            ['两权', '分离']
        ], 'union'),
        Target('7是否有独立董事', [
            ['独立', '董事']
        ], 'struct'),
        Target('8是否有审计委员会', [
            ['审计', '委员会']
        ], 'struct'),
        Target('9公司是否披露内部控制', [
            ['组织', '控制'],
            ['人员', '控制'],
            ['职务', '控制'],
            ['业务', '控制'],
            ['授权', '控制']
        ], 'struct'),
        Target('10是否有审计委员会', [
            ['内部', '控制', '鉴证', '报告']
        ], 'struct'),
        Target('11证监会对于信息披露不按期行为给予公开谴责', [], 'other', []),
        Target('12证监会对于信息披露不真实行为给予公开谴责', [], 'other', []),
        Target('13注册会计师出具的审计报告体现了被审单位信息披露的质量，标准无保留意见', [], 'other', [])
    ],
    # 相关性
    [
        Target('1公司是否根据风险情况，披露拟采取的对策', [
            ['风险', '预防']
        ], 'struct'),
        Target('2公司是否自愿披露经审核的新年度盈利预测', [
            ['盈利', '预测']
        ], 'struct'),
        Target('3公司年报是否披露新年度的经营计划或经营目标', [
            ['经营', '目标']
        ], 'struct'),
        Target('4公司是否对公司战略进行描述', [
            ['战略']
        ], 'struct'),
        Target('5公司是否进行行业未来的发展趋势分析', [
            ['公司', '未来'],
            ['行业', '未来']
        ], 'union'),
        Target('6公司是否对面临的市场竞争格局进行分析', [
            ['市场', '格局'],
            ['市场', '规模'],
            ['市场', '分析'],
            ['竞争', '格局']
        ], 'union'),
        Target('7公司是否对未来公司发展机遇和挑战进行分析', [
            ['机会', '挑战']
        ], 'struct'),
        Target('8公司是否对面临的风险因素进行分析', [
            ['面临', '风险'],
            ['潜在', '威胁']
        ], 'union')
    ],
    # 易得性
    [
        Target('1年报中是否披露公司建有网站', [
            ['本', '公司', '网址']
        ], 'struct')
    ]
]


##########################################
# get_result()
# 验证过程入口函数
##########################################
def get_result(company_id):
    global TIME_TARGET, OTHER_TARGET, RESULT
    other_target = OtherTargets(company_id = company_id)
    TIME_TARGET, OTHER_TARGET = other_target.get_targets()
    file_name_lists = os.listdir('dds/' + company_id)
    dir_path = 'dds/' + company_id
    for index, file_name in enumerate(file_name_lists):
        path = os.path.join(dir_path, file_name)
        cut_txt(path)
        check_grade(index)
        save_grade(file_name)
    print(str(RESULT))
    return RESULT


##########################################
# cut_txt()
# 将待验证文件分词，存入WORD_LIST
##########################################
def cut_txt(path):
    global WORD_LIST
    try:
        old_file = open(path, 'r', encoding='utf-8')
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
def check_grade(time_target_index):
    global MODEL_NAME, TARGET_LIST, WORD_LIST, TIME_TARGET, OTHER_TARGET
    model = gensim.models.KeyedVectors.load_word2vec_format(MODEL_NAME, binary=True)    # 加载已训练好的模型
    for target_index, sub_target_list in enumerate(TARGET_LIST):                        # 计算两个词的相似度/相关程度
        for sub_target_index, target in enumerate(sub_target_list):
            if target.type == "struct":
                for value_list in target.value_list:
                    max_time_list = []
                    for index, lists in enumerate(WORD_LIST):
                        time_list = []
                        for key_word in value_list:
                            time = 0
                            for word in lists:
                                try:
                                    grade = model.wv.similarity(key_word, word)
                                    if grade > 0.7:
                                        time += 1
                                except KeyError:
                                    pass
                            time_list.append(time)
                        if len(max_time_list) == 0:
                            max_time_list = time_list
                        else:
                            for i in range(len(max_time_list)):
                                if max_time_list[i] >= time_list[i]:
                                    break
                                if i == len(max_time_list) - 1 and max_time_list[i] < time_list[i]:
                                    max_time_list = time_list
                    print("指标" + str(value_list) + "在" + str(index + 1) + "段中匹配的最大次数为" + str(max_time_list))
                    target.append_time_list(max_time_list)
                    target.is_check_func()
                target.get_grade()
            elif target.type == "union":
                max_time_list = []
                for value_list in target.value_list:
                    for index, lists in enumerate(WORD_LIST):
                        time_list = []
                        for key_word in value_list:
                            time = 0
                            for word in lists:
                                try:
                                    grade = model.wv.similarity(key_word, word)
                                    if grade > 0.7:
                                        time += 1
                                except KeyError:
                                    pass
                            time_list.append(time)
                        if len(max_time_list) == 0:
                            max_time_list = time_list
                        else:
                            for i in range(len(max_time_list)):
                                if max_time_list[i] >= time_list[i]:
                                    break
                                if i == len(max_time_list) - 1 and max_time_list[i] < time_list[i]:
                                    max_time_list = time_list
                print("指标" + str(value_list) + "在" + str(index + 1) + "段中匹配的最大次数为" + str(max_time_list))
                target.append_time_list(max_time_list)
                target.is_check_func()
                target.get_grade()
            elif type == 'time_target':
                target.is_check = TIME_TARGET[time_target_index][sub_target_index - 1]
                target.grade = target.is_check
            else:
                target.is_check = OTHER_TARGET[sub_target_index - 10]
                target.grade = target.is_check
    WORD_LIST = []


def save_grade(file_name):
    global TARGET_LIST, RESULT
    value_list = []
    for target in TARGET_LIST:
        value = {
            'type' : target.get_family(),
            'name' : target.name,
            'grade' : target.grade,
            'is_check' : target.is_check
        }
        value_list.extend(value)

    temp_value = {
        'year' : file_name[-19:-15],
        'value' : value_list
    }
    RESULT.extend(temp_value)

def main():
    get_result()


if __name__ == '__main__':
    main()
