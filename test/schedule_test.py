from datetime import datetime
import os,sys,datetime
sys.path.append(os.path.abspath(".."))
from task.factory import schedule


"""
`*      每一个单位时间都执行`
`*/n    每n个单位时间执行一次`
`a-b    a-b之间每个单位时间执行一次`
`a-b/n  a-b之间，每n个单位时间执行一次`
`a,b,c  在a,b,c时间点分别执行一次`
"""
tn = datetime.datetime.now()
course_s = [
    "* * * * * *",
    "*/3 * * * * %s" % str(tn.weekday()),
    "10-40/5 * * * * %s" % str(tn.weekday() + 1),
    "1,14,35,56 * * * * */%s" % '2',
    "* * * * * */%s" % '3',
    "* * * * * %s-%s/%s" % ('0',str(tn.weekday()),'2'),
    "* * * * * %s-%s/%s" % ('0',str(tn.weekday()),'3'),
    " * * * * * 1,3,5"
]

for course in course_s:
    schedu,ok = schedule.TimeCourse.init(course=course)
    if not ok:
        print("时间字符串不合法")
        print(course)
        break
    
    print(schedu.course)
    print(schedu.is_time_hit())
    print(schedu.next_hit_time())
    print("___________________________________")