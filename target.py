class Target:
    def __init__(self, name: str, value_list: list, type: str, avg_time: list):
        self.name = name
        self.value_list = value_list
        self.type = type
        self.avg_time = avg_time
        self.time_list = []
        self.grade = 0
        self.is_check = True
        self.family = ''


    def append_time_list(self, time_list: list):   # 获取匹配次数
        self.time_list.append(time_list)


    def is_check_func(self):
        for list in self.time_list:
            if min(list) == 0:
                self.is_check = False

    def get_grade(self):
        grade = 0
        for list_index, list in enumerate(self.time_list):
            for index, time in enumerate(list):
                grade += (((self.avg_time[list_index][index] * 2)/time)/len(list))/len(self.time_list)
        self.grade = grade


    def get_family(self, index: int):
        if index == 0:
            self.family = '充分性'
        elif index == 1:
            self.family = '可比性'
        elif index == 1:
            self.family = '准时性'
        elif index == 1:
            self.family = '真实性'
        elif index == 1:
            self.family = '相关性'
        elif index == 1:
            self.family = '易得性'
        else:
            self.family = '未知属性'
        return self.family
