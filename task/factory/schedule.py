import re,datetime
from .err import TimeItemErr
from dateutil.relativedelta import relativedelta

class TimeCourse:
    """
    时程
    """
    # *
    __TIME_REGX_0 = re.compile(r'^(\*)$')
    # */n
    __TIME_REGX_1 = re.compile(r'^\*/(\d{1,2})$')
    # a-b
    __TIME_REGX_2 = re.compile(r'^(\d{1,2})\-(\d{1,2})$')
    # a-b/n
    __TIME_REGX_3 = re.compile(r'^(\d{1,2})\-(\d{1,2})/(\d{1,2})$')
    # a or a,b,c
    __TIME_REGX_4 = re.compile(r'^(\d{1,2})(\,\d{1,2}){0,30}$')
    
    
    @staticmethod
    def init(course:str,tm:datetime.datetime=None):
        """
        初始化时程信息
        
        :param course: str #时程 * * * * * *
        :param tm:     datetime.datetime # 基础时间
        :return: TimeCourse,bool
        """
        ins = TimeCourse()
        res = ins.parse_time(
            course=course,
            tm=tm
        )
        return ins,res
    
    
    @property
    def course(self,):
        """
        获取时间字符串
        
        :retun: str
        """
        return self.__course
    
    
    def parse_time(self,course:str,tm:datetime.datetime=None):
        """
        初始化时程信息
        
        :param course: str #时程 * * * * * *
        :param tm:     datetime.datetime # 基础时间
        :return: bool
        """        
        # 存储基础时间
        if tm:
            self.__base_time = tm
        else:
            self.__base_time = datetime.datetime.now()
        
        # 不可见字符去除
        self.__course = course.strip()
        
        # 切割时间单元
        course_s = self.__course.split(" ")
        if len(course_s) != 6:
            return False
        
        # 时间解析结果缓存
        parsed_course_s = []
        time_type_s = [
            TimeItem.TIME_TYPE_SECOND,
            TimeItem.TIME_TYPE_MINUTE,
            TimeItem.TIME_TYPE_HOUR,
            TimeItem.TIME_TYPE_DAY,
            TimeItem.TIME_TYPE_MONTH,
            TimeItem.TIME_TYPE_WEEK, 
        ]
        
        # 解析时间单元
        for i in range(len(course_s)):
            it = course_s[i]
            # 格式判断
            vls,vl_typ,ok = self.__parse_time_item(it)
            if not ok:
                return False
            
            # 时间类型
            time_type = time_type_s[i]
            item,ok = TimeItem.init(
                it=it,
                typ=time_type,
                val_typ=vl_typ,
                val=vls
            )
            
            # 时间检查
            if not ok:
                return False
            
            # 存入时间信息
            parsed_course_s.append(item)
        
        # 添加时间信息并保护
        self.__parsed_course_s = tuple(parsed_course_s)
        
        return True
                
    
    def __parse_time_item(self,it:str):
        """
        解析时间单元
        
        :param it:      str   #时间字符串
        :return: tuple,int,bool    # 值，值类型，是否合法
        """
        # *
        res = self.__TIME_REGX_0.match(it)
        if res:
            return (-1,),0,True
        
        # */n
        res = self.__TIME_REGX_1.match(it)
        if res:
            return (int(res.groups()[0]),),1,True
        
        # a-b
        res = self.__TIME_REGX_2.match(it)
        if res:
            return (int(res.groups()[0]),int(res.groups()[1])),2,True
        
        # a-b/n
        res = self.__TIME_REGX_3.match(it)
        if res:
            return (int(res.groups()[0]),int(res.groups()[1]),int(res.groups()[2])),3,True
        
        # a or a,b,c
        res = self.__TIME_REGX_4.match(it)
        if res:
            vls = []
            for v in it.split(','):
                vls.append(int(v.strip(',')))

            return tuple(vls),4,True
        
        return (),-1,False
    
    
    def is_time_hit(self,dt:datetime.datetime=None):
        """
        判断是否到了执行时间
        
        :param tm:     datetime.datetime # 对比时间
        :return: bool
        """
        if not dt:
            if not self.__base_time:
                dt = datetime.datetime.now()
            else:
                dt = self.__base_time
        
        for item in self.__parsed_course_s:
            if not item.is_time_hit(dt=dt):
                return False
        
        return True
    
    def next_hit_time(self,dt:datetime.datetime=None):
        """
        计算下一次触发的时机
        
        :param dt: datetime.datetime #指定时间
        :return: datetime.datetime
        """
        if not dt:
            dt = datetime.datetime.now()
        
        vtm_vals = [dt.second,dt.minute,dt.hour,dt.day,dt.month,dt.weekday()]
        for i in range(len(self.__parsed_course_s)):
            t_val = vtm_vals[i]
            item = self.__parsed_course_s[i]
            plus = item.next_hit_after(t_val)
            
            print("计算加量 >>>",plus)
            
            if plus == 0:
                continue
            
            # 秒
            if i == 0:
                dt = dt + datetime.timedelta(seconds=plus)
                continue
            # 分
            if i == 1:
                dt = dt + datetime.timedelta(minutes=plus)
                dt = self.__rebuild_tm(dt=dt,typ="second",val=self.__parsed_course_s[0].mini_val)
                continue
            # 时
            if i == 2:
                dt = dt + datetime.timedelta(hours=plus)
                dt = self.__rebuild_tm(dt=dt,typ="second",val=self.__parsed_course_s[0].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="minute",val=self.__parsed_course_s[1].mini_val)
                continue
            # 天
            if i == 3:
                dt = dt + datetime.timedelta(days=plus)
                dt = self.__rebuild_tm(dt=dt,typ="second",val=self.__parsed_course_s[0].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="minute",val=self.__parsed_course_s[1].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="hour",val=self.__parsed_course_s[2].mini_val)
                continue
            # 月
            if i == 4:
                dt = dt + relativedelta(month=plus)
                dt = self.__rebuild_tm(dt=dt,typ="second",val=self.__parsed_course_s[0].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="minute",val=self.__parsed_course_s[1].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="hour",val=self.__parsed_course_s[2].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="day",val=self.__parsed_course_s[3].mini_val)
                continue
            # 周
            if i == 5:
                dt = dt + datetime.timedelta(days=plus)
                dt = self.__rebuild_tm(dt=dt,typ="second",val=self.__parsed_course_s[0].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="minute",val=self.__parsed_course_s[1].mini_val)
                dt = self.__rebuild_tm(dt=dt,typ="hour",val=self.__parsed_course_s[2].mini_val)
                continue
        
        return dt

    def __rebuild_tm(self,dt:datetime.datetime,typ:str="",val:int=-1):
        """
        重置时间
        
        :param dt:  datetime.datetime #指定时间
        :param typ: str #时间类型 hour,minute,second
        :return: datetime.datetime
        """
        if val < 0:
            return dt
        
        time_index = {
            "day":2,
            "hour":3,
            "minute":4,
            "second":5
        }
        time_tuple = list(dt.timetuple())[:6]
        if typ not in time_index:
            return dt
        index = time_index[typ]
        time_tuple[index] = val
        
        return datetime.datetime(*time_tuple)

class TimeItem:
    # 时间类型-周
    TIME_TYPE_WEEK   = "week"
    # 时间类型-月
    TIME_TYPE_MONTH  = "month"
    # 时间类型-天
    TIME_TYPE_DAY    = "day"
    # 时间类型-小时
    TIME_TYPE_HOUR   = "hour"
    # 时间类型-分钟
    TIME_TYPE_MINUTE = "minute"
    # 时间类型-秒
    TIME_TYPE_SECOND = "second"
    
    # 时间取值范围
    __TIME_RANGE_MAP = {
        "week":(0,6),
        "month":(1,12),
        "day":(1,31),
        "hour":(0,23),
        "minute":(0,59),
        "second":(0,59),
    }
    # 值类型 *
    __VALUE_TYPE_0 = 0
    # 值类型 */n
    __VALUE_TYPE_1 = 1
    # 值类型 a-b
    __VALUE_TYPE_2 = 2
    # 值类型 a-b/n
    __VALUE_TYPE_3 = 3
    # 值类型 a or a,b,c
    __VALUE_TYPE_4 = 4
    
    @staticmethod
    def init(it:str,typ:int,val_typ:int,val:tuple):
        """
        初始一个时间单元
        
        :param it:      str   #时间字符串
        :param typ:     int   #时间类型
        :param val_typ: int   #值类型 * 0,*/n 1,a-b 2,a-b 3,a or a,b,c 4
        :param val:     tuple #值 tuple[int] * => -1
        :return: TimeItem,bool
        """
        ins = TimeItem()
        res = ins.parse(it=it,typ=typ,val_typ=val_typ,val=val)
        return ins,res
    
    @property
    def course(self,):
        """
        获取时间字符串
        
        :retun: str
        """
        return self.__course
    
    def parse(self,it:str,typ:int,val_typ:int,val:tuple):
        """
        初始一个时间单元
        
        :param it:      str   #时间字符串
        :param typ:     int   #时间类型
        :param val_typ: int   #值类型 */n 1,a-b 2,a-b 3,a or a,b,c 4
        :param val:     tuple #值 tuple[int] * => -1
        :return: bool
        """
        self.__course = it
        self.__type = typ.lower()
        self.__val_type = val_typ
        self.__val = val
        self.__range = () if typ not in self.__TIME_RANGE_MAP else self.__TIME_RANGE_MAP[typ]
        
        return self.check()
    
    def check(self,):
        """
        判断时间单元的值是否正确
        
        :return: bool
        """
        # 值为空
        if not self.__val:
            return False
        
        # 时间类型不合法
        if self.__type not in self.__TIME_RANGE_MAP:
            return False
        
        # 值类型不合法
        if self.__val_type not in [self.__VALUE_TYPE_0,self.__VALUE_TYPE_1,self.__VALUE_TYPE_2,self.__VALUE_TYPE_3,self.__VALUE_TYPE_4]:
            return False
        
        # *
        if self.__val_type == self.__VALUE_TYPE_0:
            self.mini_val = self.__range[0]
            return True
        
        # */n
        if self.__val_type == self.__VALUE_TYPE_1:
            if not (self.__val[0] >= self.__range[0] and self.__val[0] <= self.__range[1]) or self.__val[0] == 0:
                return False

            self.mini_val = self.__val[0]
            return True
        
        # a-b
        if self.__val_type == self.__VALUE_TYPE_2:
            if self.__val[1] <= self.__val[0]:
                return False
            
            if self.__val[0] < self.__range[0] or not (self.__val[1] >= self.__range[0] and self.__val[1] <= self.__range[1]):
                return False

            self.mini_val = self.__val[0]
            return True
        
        # a-b/n
        if self.__val_type == self.__VALUE_TYPE_3:
            if self.__val[1] <= self.__val[0]:
                return False
            
            if self.__val[0] < self.__range[0] or not (self.__val[1] >= self.__range[0] and self.__val[1] <= self.__range[1]):
                return False
            
            if (self.__val[1] - self.__val[0]) < self.__val[2]:
                return False
            
            self.mini_val = self.__val[0]
            return True
        
        # a or a,b,c
        if self.__val_type == self.__VALUE_TYPE_4:
            if len(self.__val) == 1 and self.__val[0] == -1:
                return True
            
            for v in self.__val:
                if not (v >= self.__range[0] and v <= self.__range[1]):
                    return False
            
            self.mini_val = min(self.__val)
            return True
        
        # unknow val type
        return False
    
    def is_time_hit(self,dt:datetime.datetime=None):
        """
        判断当前时间是否命中
        
        :param dt: datetime.datetime #当前时间
        :return: bool
        """
        if not dt:
            dt = datetime.datetime.now()
        
        # 周
        if self.__type == self.TIME_TYPE_WEEK:
            print("周>>>")
            return self.__is_time_val_hit(dt.weekday())
        
        # 月
        if self.__type == self.TIME_TYPE_MONTH:
            print("月>>>")
            return self.__is_time_val_hit(dt.month)
        
        # 日
        if self.__type == self.TIME_TYPE_DAY:
            print("日>>>")
            return self.__is_time_val_hit(dt.day)
        
        # 时
        if self.__type == self.TIME_TYPE_HOUR:
            print("时>>>")
            return self.__is_time_val_hit(dt.hour)
        
        # 分
        if self.__type == self.TIME_TYPE_MINUTE:
            print("分>>>")
            return self.__is_time_val_hit(dt.minute)
        
        # 秒
        if self.__type == self.TIME_TYPE_SECOND:
            print("秒>>>")
            return self.__is_time_val_hit(dt.second)
        
        return False
        
    def __is_time_val_hit(self,val:int):
        """
        判断时间值是否命中
        
        :param val: int #时间值
        :return: bool
        """
        # *
        if self.__val_type == self.__VALUE_TYPE_0:
            return True
        
        # */n
        if self.__val_type == self.__VALUE_TYPE_1:
            return val % self.__val[0] == 0
        
        # a-b
        if self.__val_type == self.__VALUE_TYPE_2:
            return val >= self.__val[0] and val <= self.__val[1]
        
        # a-b/n
        if self.__val_type == self.__VALUE_TYPE_3:
            min_v = self.__val[0]
            max_v = self.__val[1]
            return (val >= min_v and val <= max_v) and ((val - min_v) % self.__val[2] == 0)
        
        # a or a,b,c
        if self.__val_type == self.__VALUE_TYPE_4:
            return val in self.__val
        
        return False
    
    
    def next_hit_after(self,val:int):
        """
        计算下次一命中需要经过的时长
        
        :param val: int #当前时值
        :return: int
        """
         # *
        if self.__val_type == self.__VALUE_TYPE_0:
            return 0
        
         # */n
        if self.__val_type == self.__VALUE_TYPE_1:
            remain = self.__val[0] - val % self.__val[0]
            n_val = val + remain
            
            if n_val <= self.__range[1]:
                return remain
            else:
                return self.__range[1] - val + self.__val[0]
        
        # a-b
        if self.__val_type == self.__VALUE_TYPE_2:
            if val < self.__val[0]:
                return self.__val[0] - val
            
            if val > self.__val[1]:
                return self.__range[1] - val + self.__val[0]
            
            return 0
        
        # a-b/n
        if self.__val_type == self.__VALUE_TYPE_3:
            base_num = 0
            ok = False
            
            while not ok:
                if val > self.__range[1]:
                    val = 0
                
                if (val % self.__val[2]) != 0 or (val < self.__val[0] or val > self.__val[1]):
                    base_num += 1
                    val += 1
                    continue
                
                break
            
            return base_num
        
        # a or a,b,c
        if self.__val_type == self.__VALUE_TYPE_4:
            if val in self.__val:
                return 0
            
            ls_val = list(self.__val)
            sorted(ls_val)
            
            if val < ls_val[0]:
                return ls_val[0] - val
            
            if val > ls_val[-1]:
                return self.__range[1] - val + ls_val[0]
            
            base_val = 0
            while val <= self.__range[1]:
                if val in ls_val:
                    break
                val += 1
                base_val += 1
            
            return base_val
        
        raise TimeItemErr("next_hit_after")