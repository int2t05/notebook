需求文档：
https://clouddocs.huawei.com/wapp/share/6ff20252-b8f3-4c4a-91ad-3250bf5d8fe9
PR表：
https://onebox.huawei.com/v/1feac43a65b3597d9132146afc61d53d?type=1

测试用例参考：
https://gitcode.com/toljr/notebook_my/blob/flink_test/install_script/OmniStream/install_step.sh

黄区参考wiki:
https://wiki.huawei.com/domains/20973/wiki/246664/WIKI2026040910720150
https://wiki.huawei.com/domains/20973/wiki/246664/WIKI202601179837962

开源仓库账号
涉及fork PR MR
https://gitcode.com/dashboard

服务器环境：
两个文件
动态验证码申请：朱天伟

远程服务器信息
前置软件：UniVpn Xshell

密码
omni1234
ssh root@193.65.4.2

硬件配置：
系统
openEuler 22.03 (LTS-SP3)
cpu
Kunpeng 920 7270Z
内存
2G + 254G + 128G + 128G + 256G = 768G
硬盘
8.7（NVMe） + 134.4566（机械）= 143.1566 TB

开发问题咨询： 李嘉荣
其他问题咨询pl: 朱天伟

表达式开发涉及三个主要仓库：
Adaptor:A
Operator:O
Stream: S

实习生已开发的需求：
IFNULL  已合入A 完成

LEFT/RIGHT 已合入O  待解决A(等待重构)
(NOT)  BETWEEN 已提O 待提A
(NOT) LIKE 待提A
(NOT) SIMILAR 已提O 待提A
(NOT)  IN 待提A
EXIST 已提S 待提A


本地fork这三个仓库
加载适配skill 验证后
init开发环境（待验证）
表达式开发开新分支（自己fork仓库的远程分支） 
