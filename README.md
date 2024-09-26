# PPTBomb PPT生成器
该软件用于快速构建PPT。将SBPL语言（Structured Bomb PPT Language， 又作SBPPT Language，是为制作该软件打造的描述性语言）自动转换成Latex语言，再转换成PPT。
## 使用说明
1. 安装好Latex和Python环境
2. 用SBPL编辑input.tjppt文件
3. 运行main.py
4. out.pdf即为输出后的ppt。
## SBPL快速上手
以下是附带的input.tjppt的内容。其中，::表示命令。命令用法参考下面的代码。content命令是必须的。要显示的ppt内容全部放在content命令中。   
由于没有用任何的语法解析器，逗号和花括号前后不要有空格，花括号不要换行写。   
特别，::bib表示有用到注释，::theme表示要用的主题（参考 https://latex.artikel-namsu.de/english/themes/uebersicht_beamer.html ），默认为Berlin。
```commandline
::maintitle,主标题
::title,标题
::subtitle,分标题
::mainauthor,主作者
::author,作者1,作者2
::theme,CambridgeUS
::bib
content{
    _测试部分{
        #M,无图片测试页{
            你可以用“\#M,页标题”命令创建一个没图片的页面。（M意思是没图）
            !测试板块{
                你可以用“!板块标题”命令创建一个板块。
                -{
                    你可以用“-”命令创建一个无序列表
                    列表项\cite{involution}
                    你可以用“cite”命令进行引用（需要配置好bib文件，并在content命令前使用过“::bib”命令）
                }
                -1{
                    你可以用“-1”命令创建一个无序列表
                    序列表项2
                }
                $$
                T' = \dfrac{M}{m} + \dfrac{9999}{m} \times t < Mt, \quad if\ m > \dfrac{1}{t} + \dfrac{9999}{M}
                $$
                插入数学公式与latex完全兼容
            }
        }
        #B,图文并排版面测试{
            ::ratio,0.45
            你可以用“\#B,页标题”命令创建一个图片与文字并排的页面。（B意思是并排）
            用“::ratio,比例”命令调整图片占整个页面的比例。
            -{
                列表项1
                列表项2
            }
            ::picture,并排测试图,figure/picture1.jpg
            你可以用"::picture,图片标题,图片路径"命令插入图片。（图文并排版面只允许一张图）
        }
        #S,图文竖排版面测试{
            ::ratio,0.45
            你可以用“\#S,页标题”命令创建一个图片与文字竖排的页面。（S意思是Shupai）\\
            ::picture,竖排测试图,figure/picture2.jpg
            你可以用"::picture,图片标题,图片路径"命令插入图片。（图文竖排版面只允许一张图）
        }
        #D,多图版面测试{
            ::ratio,0.4
            你可以用“\#D,页标题”命令创建一个有多张的页面。（D意思是多图DuoTu）
            -1{
                列表项1
                列表项2
                列表项3
            }
            ::picture,竖排测试图,figure/picture3.jpg
            ::picture,竖排测试图,figure/picture4.jpg
            你可以用"::picture,图片标题,图片路径"命令插入图片。
        }
    }
}
```
## SBPL详细说明
SBPL中，一切都是对象，对象可能有属性，属性可能有值。对象间可以由特殊规则嵌套。    
对象从小到大总表如下：
- 普通文本BaseObj
- 列表List
- 块Block
- 页Page
- 部分Part
- 内容Content
- 整个文件WholeFile
除普通文本和整个文件对象外，对象的定义方式为：
```commandline
对象名{
    对象内容
}
```
对象中可以定义属性。属性的定义方式为：
```commandline
::属性,值1,值2...
```
以下分别进行介绍。
### 普通文本BaseObj
文件的每一行，如果不是对象或属性的声明，那就是普通文本。普通文本会原封不动放进生成的latex文件中。

### 列表List
列表的对象名为"-"（无序列表）或"-1"（有序列表）。列表可嵌套普通文本对象。

### 块Block
块的对象名为"!块名"，块可嵌套列表对象或普通文本对象。

### 页Page
页的对象名为“#排版方式,页名”。页可嵌套普通文本对象、块对象、列表对象。
页的属性：
- ratio：有一个值，表示图片占整个页面的比例。
- picture：表示图片。这个属性一页可以有多个。有2个值，为图片的标题和路径。

### 部分Part
部分的对象名为“_部分名”。只能嵌套页对象。

### 内容Content
表示文件中所包含的内容。只能嵌套Part对象。

### 整个文件WholeFile
表示整个PPT文件。程序会自动进行定义，无须手动声明。必须嵌套一个Content对象。
整个文件的属性：
- maintitle：主标题，即显示在每一页上的标题名称，有1个值。
- title：标题，即显示在封面上的标题，有1个值。
- subtitle：分标题，即封面上的分标题，有1个值。
- mainauthor：主作者，即显示在每一页上的作者，有1个值。
- author：作者，即显示在封面上的作者，可以有多个值。
- theme：主题，见前一部分给出的连接，有1个值。
- bib：是否有引用。如定义这个属性，则会插入一个reference.bib文件定义的引用页面
