from .schedule import TimeCourse

class BaseTask:
    # 执行类型-单次
    __RUN_TYPE_ONCE = "once"
    # 执行类型-持续
    __RUN_TYPE_ALWAYS = "repeat"
    
    def __init__(self,name:str,alias:str,describe:str,cron:str):
        """
        初始化一个任务
        
        :param name:     str #任务名称
        :param alias:    str #任务别名
        :param describe: str #任务描述
        :param cron:     str #调度规则 */秒 */分 */时 */天 */月 */周
        :param typ:      str #任务类型 once|repeat
        :param code:     str #任务编码
        :param parent_code: str #父级任务编码，多个编码逗号分隔
        :param relation:
        """
        # 任务名称
        self.__name = ""
        # 执行类型
        self.__run_type = ""
        # 时间规则
        self.__course = ""
        # 时程管理器
        self.__course_instance = TimeCourse.init(course=self.__course)