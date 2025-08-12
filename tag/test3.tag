// 添加调试信息
echo "开始执行TagUI脚本"
echo "正在导航到目标网站..."

https://zwfw.gxzf.gov.cn/banshi/index/
download to D:/辅助打证/test/downloads/

keyboard [alt][space]
keyboard x
click /html/body/div[3]/div[2]/div[2]/ul/li[6]/a
popup eportal
    keyboard [pagedown]
    hover /html/body/div[7]/div[3]/div[1]/div/div[2]/div/div[2]/ul/li[6]/div[2]/p[1]
    click /html/body/div[7]/div[3]/div[1]/div/div[2]/div/div[2]/ul/li[6]/div[2]/a[1]
popup qylogin
    click /html/body/div/div/section/div/div/main/div/div[2]/p[3]/a
popup TopIP
    hover /html/body/div[1]/div/div/div[2]/div[1]/div/div[1]/ul/li[2]/div
    click /html/body/div[3]/ul/li[1]


    co = false
    while !co
        co = present('/html/body/div[1]/div/div/div[1]/div[1]/div[2]/div/div/span')
        echo 1
    hover 食品许可登记
    click 食品经营

popup TopFDOAS
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
