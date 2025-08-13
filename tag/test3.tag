// 添加调试信息
echo "开始执行TagUI脚本"
echo "正在导航到目标网站..."

https://tyrz.zwfw.gxzf.gov.cn/am/auth/login?service=initService&goto=aHR0cHM6Ly90eXJ6Lnp3ZncuZ3h6Zi5nb3YuY24vYW0vb2F1dGgyL2F1dGhvcml6ZT9zZXJ2aWNlPWluaXRTZXJ2aWNlJmNsaWVudF9pZD16cnl0aHh0JnJlZGlyZWN0X3VyaT1odHRwcyUzQSUyRiUyRnpoamcuc2NqZGdsai5neHpmLmdvdi5jbiUzQTYwODclMkZUb3BJUCUyRnNzbyUyRm9hdXRoMiUzRmF1dGhUeXBlJTNEendmd19ndWFuZ3hpJnJlc3BvbnNlX3R5cGU9Y29kZSZzY29wZT11aWQrY24rdXNlcmlkY29kZSt1c2VydHlwZSttYWlsK3RlbGVwaG9uZW51bWJlcitpZGNhcmRudW1iZXIraWRjYXJkdHlwZSt1bml0bmFtZStvcmdhbml6YXRpb24rbG9naW5pbmZvK3Rva2VuaWQrc3ViamVjdCt1cGRhdGVUaW1lJnN0YXRlPXd0Wk5hNA==
download to D:/辅助打证/test/downloads/

co = false
while !co
    co = present('/html/body/div[1]/div/div/div[1]/div[1]/div[2]/div/div/span')
    echo 1

https://zhjg.scjdglj.gxzf.gov.cn:10001/TopFDOAS/topic/homePage.action?currentLink=foodOp
co = false
while !co
    co = present('//*[@id="tab-second"]')
    echo 2
click /html/body/div[1]/div[2]/div/div[1]/div[2]/div/div[1]/div/div/div/div[2]
click //*[@id="pane-second"]/div/div/div[2]/div/div[3]/table/tbody/tr/td[7]/div/div/div/button/span

//click 证照下载
click /html/body/ul/li[2]/button

// 添加额外等待时间确保文件完全下载
echo "下载完成，等待文件写入..."
wait 3

// 脚本执行完成标记
echo "TagUI脚本执行完成！"
echo "文件下载已完毕，可以进行后续处理"
