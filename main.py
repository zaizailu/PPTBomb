from enum import Enum
from typing import TextIO
import re
import os


class PartTypes(Enum):
    Bingpai = 'B'
    Shupai = 'S'
    Duotu = 'D'
    Meitu = 'M'


class BaseObj:
    def __init__(self):
        self.text = ""

    def out(self):
        return self.text


class Picture:
    def __init__(self, caption, path):
        self.caption = caption
        self.path = path


class Page(BaseObj):
    def __init__(self, page_type, page_name):
        super().__init__()
        self.type = page_type
        self.name = page_name
        self.objects = []
        self.pictures = []
        self.ratio = 0.5

    def out(self):
        if (len(self.pictures) == 0 and self.type != PartTypes.Meitu or
                len(self.pictures) > 1 and self.type != PartTypes.Duotu):
            print(self.name, "图片数错误！")
            exit(-1)

        text = r"\begin{frame}{" + self.name + "}\n"

        if self.type == PartTypes.Bingpai:
            text += r'''
            \begin{columns}
            \column{''' + str(self.ratio) + r'''\textwidth}
            \begin{figure}
            \centering \includegraphics[width=0.95\textwidth]{
            ''' + self.pictures[0].path + "}\n"

            text += r"\caption{" + self.pictures[0].caption + "}\n"
            text += r'''
            \end{figure}
            ''' + r'''\column{''' + str(1.0 - self.ratio) + r'''\textwidth}''' + "\n"
        elif self.type == PartTypes.Shupai:
            text += r'''
            \begin{figure}
            \centering \includegraphics[height=''' + str(self.ratio) + r'''\textheight]{
            ''' + self.pictures[0].path + "}\n"

            text += r"\caption{" + self.pictures[0].caption + "}\n"
            text += r'''
            \end{figure}
            ''' + "\n"
        elif self.type == PartTypes.Duotu:
            text += r"\begin{columns}"
            text += "\n"
            for pic in self.pictures:
                text += r"\column{" + str(1/len(self.pictures)) + r"\textwidth}" + "\n"
                text += r'''
                \begin{figure}
                \centering \includegraphics[height=''' + str(self.ratio) + r'''\textheight]{
                ''' + pic.path + "}\n"

                text += r"\caption{" + pic.caption + "}\n"
                text += r'''
                \end{figure}
                ''' + "\n"
            text += r"\end{columns}" + "\n"

        for item in self.objects:
            text += item.out()

        if self.type == PartTypes.Bingpai:
            text += r"\end{columns}" + "\n"
        text += r"\end{frame}" + "\n"
        return text


class Part(BaseObj):
    def __init__(self, part_name):
        super().__init__()
        self.name = part_name
        self.pages = []

    def out(self):
        text = r"\section{" + self.name + "}\n"
        for item in self.pages:
            text += item.out()
        return text


class List(BaseObj):
    def __init__(self, list_with_num: bool):
        super().__init__()
        self.list_with_num = list_with_num
        self.objects = []

    def out(self):
        if self.list_with_num:
            text = r"\begin{enumerate}" + "\n"
        else:
            text = r"\begin{itemize}" + "\n"
        for item in self.objects:
            text += r"\item" + "\n" + item.out() + "\n"
        if self.list_with_num:
            text += r"\end{enumerate}" + "\n"
        else:
            text += r"\end{itemize}" + "\n"
        return text


class Block(BaseObj):
    def __init__(self, name):
        super().__init__()
        self.objects = []
        self.name = name

    def out(self):
        text = r"\begin{block}{" + self.name + "}\n"
        for item in self.objects:
            text += item.out() + "\n"
        text += r"\end{block}" + "\n"
        return text


class WholeFile:
    def __init__(self):
        self.main_title = None
        self.title = None
        self.subtitle = None
        self.main_author = None
        self.has_bib = False
        self.author = []
        self.parts = []
        self.theme = "Berlin"

    def write(self):
        with open("out.tex", "w", encoding='UTF-8') as f:
            f.write(r'''
\documentclass{ctexbeamer}

\usepackage{amsthm}
\usepackage{biblatex}
\addbibresource{reference.bib}
\setbeamertemplate{bibliography item}[text]

\usetheme{''' + self.theme + '}\n')
            if self.title:
                f.write(r"\title")
                if self.main_title:
                    f.write(f"[{self.main_title}]")
                f.write("{%s}\n" % self.title)
            if self.subtitle:
                f.write(r"\subtitle{" + self.subtitle + "}\n")
            if self.author:
                f.write(r"\author")
                if self.main_author:
                    f.write(f"[{self.main_author}]")
                f.write("{")
                f.write(",\\\n".join(self.author))
                f.write("}\n")
            f.write(r'''
\date{\today}

\begin{document}
\begin{frame}
    \titlepage
\end{frame}
            ''' + '\n')
            for item in self.parts:
                f.write(item.out())
            if self.has_bib:
                f.write(r'''
\begin{frame}{参考文献}
    \printbibliography
\end{frame}''')
            f.write(r'''
\end{document}
            ''')


def get_obj(f: TextIO):
    command = f.readline().strip()
    if command == "}":
        return None
    if command.startswith("::picture"):
        tmp = command.split(",")
        try:
            ret = Picture(tmp[1], tmp[2])
            return ret
        except IndexError:
            print(command, "参数不足！")
            exit(-1)

    elif match := re.search(r'_(\w+)\{', command):
        part_name = match.group(1)
        part = Part(part_name)
        while True:
            obj = get_obj(f)
            if not obj:
                return part
            if not isinstance(obj, Page):
                print(command, "错误！这里必须是新页！")
                exit(-1)
            part.pages.append(obj)
    elif match := re.search(r'#(\w+),(\w+)\{', command):
        try:
            page_type = PartTypes(match.group(1))
        except:
            print(command, "页排版类型为未知符号")
            exit(-1)
        page_name = match.group(2)
        page = Page(page_type, page_name)
        while True:
            obj = get_obj(f)
            if not obj:
                return page
            if isinstance(obj, Picture):
                page.pictures.append(obj)
            elif isinstance(obj, BaseObj) and obj.text.startswith("::ratio"):
                try:
                    page.ratio = float(obj.text.split(",")[1])
                except:
                    print(obj.text, "参数错误！")
                    exit(-1)
                if not 0 < page.ratio < 1:
                    print(obj.text, "比例必须是0~1之间的小数！")
                    exit(-1)
            elif isinstance(obj, (List, Block, BaseObj)):
                page.objects.append(obj)
            else:
                print(command, "错误！这里是非法对象！")
                exit(-1)
    elif match := re.search(r'-(.*?)\{', command):
        if match.group(1) == '1':
            lst = List(True)
        elif match.group(1) == '':
            lst = List(False)
        else:
            print(command, "列表类型为未知符号")
            exit(-1)
        while True:
            obj = get_obj(f)
            if not obj:
                return lst
            if isinstance(obj, BaseObj):
                lst.objects.append(obj)
            else:
                print(command, "错误！这里是非法对象！")
                exit(-1)
    elif match := re.search(r'!(\w+)\{', command):
        blk_name = match.group(1)
        blk = Block(blk_name)
        while True:
            obj = get_obj(f)
            if not obj:
                return blk
            if isinstance(obj, (BaseObj, List)):
                blk.objects.append(obj)
            else:
                print(command, "错误！这里是非法对象！")
                exit(-1)
    else:
        obj = BaseObj()
        obj.text = command
        return obj


def main():
    with open("input.tjppt", "r", encoding='UTF-8') as f:
        ppt = WholeFile()
        while True:
            command = f.readline()
            if command == "":
                print("花括号不匹配！")
                exit(-1)
            command = command.strip()
            try:
                if command.startswith("}"):
                    break
                elif command.startswith("::maintitle"):
                    ppt.main_title = command.split(',')[1]
                elif command.startswith("::title"):
                    ppt.title = command.split(',')[1]
                elif command.startswith("::subtitle"):
                    ppt.subtitle = command.split(',')[1]
                elif command.startswith("::mainauthor"):
                    ppt.main_author = command.split(',')[1]
                elif command.startswith("::theme"):
                    ppt.theme = command.split(',')[1]
                elif command.startswith("::author"):
                    ppt.author = command.split(',')[1:]
                elif command.startswith("::bib"):
                    ppt.has_bib = True
                elif command.startswith("content{"):
                    ppt.parts.append(get_obj(f))
                else:
                    print(command, "非法指令！")
                    exit(-1)
            except IndexError:
                print(command, "参数不足！")
        ppt.write()
        os.system(r"latexmk out.tex -halt-on-error -time -xelatex -outdir=. -shell-escape")


if __name__ == '__main__':
    main()
