<!--
 * @Author: liu kang
 * @Date: 2026-03-23 00:01:00
 * @LastEditors: Automation
 * @LastEditTime: 2026-03-23 00:11:00
 * @FilePath: /my_llm_api_server/configOpenclaw.md
 * @Description: 
 * 
 * Copyright (c) 2026 by ${git_name_email}, All Rights Reserved. 
-->
# 目标
oepnclaw 可以调用本地api server,也就是[text](README.md)提供的本地服务，注意是openclaw调用的是本地转发的api服务，而不是直接智谱，qwen等厂商直接的api
## 用于测试的例子
远程api相关信息在这个文档[text](api.md)
### 测试过程
1.先测试本地api服务正常
2.配置到openclaw进行测试
3.openclaw 使用http://localhost:8000 能够正常输出内容
## 参考
1.openclaw的路径为/opt/homebrew/bin/openclaw