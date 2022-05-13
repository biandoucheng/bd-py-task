import traceback
from datetime import datetime

class TimeItemErr(Exception):
    """
    时间单元计算异常
    """
    def __init__(self, func_name:str) -> None:
        self.func_name = func_name
    
    def __str__(self):
        tm = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return "TimeItem.%s 执行异常[%s] \n%s" % (self.func_name,tm,traceback.format_exc())