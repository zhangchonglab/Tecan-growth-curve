该文件为Tecan酶标仪进行生长曲线测定的数据后处理说明文件。

需要准备的三个输入文件: rawdata.txt configure.txt prefix

首先，rawdata.txt为原始数据文件，将Tecan酶标仪的数据文件拷贝出来（只需要数据部分，具体见文件夹里的example），新建txt文件，粘贴进去即可得到。一个example请见Tecan文件夹下的rawdata.txt

configure.txt用来描述96（or whatever）孔板和sample的对应关系。一个例子如下：
mnmE-40-pH7     B2,B3,B4
mnmE-63-pH7     B5,B6,B7
sthA-4-pH7      B8,B9,B10
sthA-46-pH7     C2,C3,C4
yneE-13-pH7     C5,C6,C7
yneE-65-pH7     C8,C9,C10
ydhS-26-pH7     D2,D3,D4
ydhS-113-pH7    D5,D6,D7
MCm-NC-pH7      D8,D9,D10
mnmE-40-pH4.5   E2,E3,E4
mnmE-63-pH4.5   E5,E6,E7
sthA-4-pH4.5    E8,E9,E10
sthA-46-pH4.5   F2,F3,F4
yneE-13-pH4.5   F5,F6,F7
yneE-65-pH4.5   F8,F9,F10
ydhS-26-pH4.5   G2,G3,G4
ydhS-113-pH4.5  G5,G6,G7
MCm-NC-pH4.5    G8,G9,G10

其中sample和孔位置的信息用tab(键盘左上)隔开，replicates之间（如B1，B2，B3）用英语的逗号隔开。Tecan文件夹下有一个Configure.txt文件，可以在此基础上进行修改。也可以在Excel的两个column里面分别编辑sample和对应的孔名称，然后粘贴到txt文件。

prefix不是一个文件，只是一个名称，是输出文件名字的前缀，自定义即可。

准备好以上文件之后，将所有文件放到桌面上的Tecan文件夹里面。然后打开Terminal，粘贴以下命令，
cd ~/Desktop/Tecan/

回车之后，粘贴以下命令：
python TecanDataProcessing.py rawdata.txt Configure.txt prefix
其中，相应文件的名字请根据实际情况进行替换。

运行正常，得到两个输出文件：
名字分别是prefix.processedmean.txt 和prefix.processedstd.txt，其中prefix是上一个命令里面自定义的前缀名。mean文件和std文件分别表示一个sample的多孔平均值和标准差（注意，这里使用的是population std,也就是sigma^2/sqrt(n)）。该文件可以直接导入到excel里面进行作图处理（推荐使用plotly，https://plot.ly/plot）
Tecan文件夹下也有两个真实数据处理得到的输出文件。

很简单的程序和使用，一秒钟就可以搞定Tecan输出的冗长excel后处理，hopefully helpful and wish you enjoy:)

If any question, 请联系王天民 wtm0217@gmail.com。
