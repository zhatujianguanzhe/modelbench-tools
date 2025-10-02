**modelbench模型优化套件 & blockbench模型逐面转箱式进而转为mimodel**

我将逐一介绍三个exe文件的功能与使用教程:

**1️⃣.mimodelUV合并工具.exe**

❓你的单主的模型是不是有十八张贴图而且完全不知道谁对谁?

❓你的多贴图模型在转换上是否有诸多不便?

✅快来试试这个软件吧! 它可以将多张贴图的模型**转换为单贴图**,并且贴图内**所有图像完全不变**,连相对位置都不变,你可以理解为将每个贴图横向排布,然后修改了对应uv的偏移.

<img src="file:///C:/Users/86138/AppData/Roaming/marktext/images/2025-10-01-23-46-59-image.png" title="" alt="" width="294">

                                图1-1

如图1-1所示,按照顺序选择文件并点击"开始"按钮,随后会出现图1-2提示.

<img src="file:///C:/Users/86138/AppData/Roaming/marktext/images/2025-10-01-23-50-06-image.png" title="" alt="" width="299">

                                图1-2

如图1-2,一般情况下直接点击"确定"即可.如果你的贴图文件不在这里,则应按照与小窗口标题相匹配的贴图文件,将对应的贴图文件路径填入.

<img src="file:///C:/Users/86138/AppData/Roaming/marktext/images/2025-10-01-23-52-01-image.png" title="" alt="" width="305">

                                图1-3

如图1-3,完成了!

------------------------

有一些常见的报错如下:

<img title="" src="file:///C:/Users/86138/AppData/Roaming/marktext/images/2025-10-01-23-53-51-image.png" alt="" width="303">

                                图1-4

如图1-4,提示xxx已存在说明想要保存的文件是一个已经存在的文件.为了保证防误删重要文件,程序会禁止覆盖已有的文件.换成一个不存在的文件名就可以了.



**2️⃣.mimodelUV分离与整理.exe**

❓即使你的模型的UV,它是否同样无比混乱?

❓混合颜色选项在obj中可能出问题?

✅快来试试这个软件吧! 它可以将一个模型的贴图重新整理好,有序排布,并将颜色设定直接经过运算后得出最终颜色并运用到贴图上.

**⚠仅支持单贴图模型**,多贴图必须先用工具1转换.

**⚠开始之前必须备份你的模型和贴图!**

**⚠程序无响应时绝对不要强制关闭程序!**

眼见为实,看个例子:

从图2-1-1转化为图2-1-2



<img src="file:///D:/!文档/Orignal_DISK_E(DO_NOT_DELETE)/Python项目库/Mine-imator工具/mimodelUV合并工具/新建文件夹/Skin_HongLan.png" title="" alt="Skin_HongLan.png" width="170">

<img src="file:///D:/!文档/Orignal_DISK_E(DO_NOT_DELETE)/Python项目库/Mine-imator工具/mimodelUV合并工具/新建文件夹/Texture_Maid_Clothes_Short.png" title="" alt="Texture_Maid_Clothes_Short.png" width="185">

                       图2-1-1

<img title="" src="file:///D:/!文档/Orignal_DISK_E(DO_NOT_DELETE)/Python项目库/Mine-imator工具/mimodelUV合并工具/测试/1.png" alt="1.png" width="191" data-align="inline">

                     图2-1-2





<img src="file:///C:/Users/86138/AppData/Roaming/marktext/images/2025-10-02-00-07-20-image.png" title="" alt="" width="299">

                        图2-2

在开始之前,**务必备份你的文件**,原因后面讲.

如图2-2,软件的初始页面如此.先将前四行的文件填好.

"新贴图宽""新贴图高"表示整理后的贴图的大小.由于程序限制,不得不这样做.你只需要填写一个比较正常的值即可.

"保留mb颜色属性"表示你不希望程序将颜色的混合直接运算并应用到贴图上,而是将自由权给予modelbench软件内设定.

"保留mb透明度属性"表示你不希望程序将透明度直接应用到贴图上.这是"保留mb颜色属性"的一个子选项.我推荐将他勾选是因为mb对半透明材质的支持度很低,各种问题都会出.



随后点击"开始"按钮.如果你的模型体量比较大可能会产生无响应的情况,此时**绝对不要关闭程序**,否则你的贴图可能会损坏.处理时间可能会长达数分钟.



完毕后会弹出提示框如图1-3所示.回到modelbench后请记得**将模型主纹理设置为程序产生的那个文件**.

-------------------------------------------

一些常见报错如下:

如图1-4类似报错不再赘述.



<img src="file:///C:/Users/86138/AppData/Roaming/marktext/images/2025-10-02-00-26-43-image.png" title="" alt="" width="387">

                                     图2-3

如图2-3,这说明贴图宽高不足,你可以给他们各加一两百试试.



**3️⃣逐面2箱式.exe**

❓blockbench模型导入米`modelbench时总**不支持逐面UV**?

✅试试逐面2箱式.exe,它可以将bbmodel从逐面UV转换为箱式UV,随后你可以通过插件导出为mimodel.

**⚠仅支持<u>通用</u>格式,且所有部件均为箱式UV.**

**⚠仅支持单贴图模型.**

**⚠不允许OBJ部件.**

**⚠不支持逐面UV的拉伸!!!**



此工具用法与1相似,不再赘述.





