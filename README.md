# bd-py-task
任务管理

## 任务可选执行次数
+ `单次 once`
+ `重复执行 repeat`

## 执行时间规则
+ `周(0-6) 月(1-12) 日(1-31) 时(0-23) 分(0-59) 秒(0-59)`
+ + `*      每一个单位时间都执行`
+ + `*/n    每n个单位时间执行一次`
+ + `a-b    a-b之间每个单位时间执行一次`
+ + `a-b/n  a-b之间，每n个单位时间执行一次`
+ + `a,b,c  在a,b,c时间点分别执行一次`
