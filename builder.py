#!/usr/bin/env python3

import re, os, csv, tempfile, datetime
from subprocess import call as runcommand

# based on https://tex.stackexchange.com/questions/372807/how-do-i-make-a-full-journal-in-latex

# see https://www.sascha-frank.com/Fonts/Times_New_Roman.html
# see https://tex.stackexchange.com/questions/136742/changing-background-color-of-text-in-latex
# see https://tex.stackexchange.com/questions/46280/how-to-create-a-background-image-on-title-page-with-latex
#
# See the LaTeX book, https://upload.wikimedia.org/wikipedia/commons/2/2d/LaTeX.pdf, for more


HEADER="""
%% journal-style document, indent paragraphs, 12 point text
%% twoside -- printed for binding, openany -- don't wait for an even page to start new article
\\documentclass[12pt,journal,indent,openany]{paper}
%% Use paper size good for tablets, recommended in LaTeX book, with 1 inch margins
\\usepackage[paperwidth=6.125in, paperheight=9.25in]{geometry}
%% English main language
\\usepackage[english]{babel}
\\usepackage{microtype}
%% allow use of colors, using dvips names for colors (see LaTeX book)
\\usepackage[dvipsnames]{xcolor}
%% give more control over page headers
\\usepackage{fancyhdr}
\\pagestyle{fancy}
%% \\usepackage{lipsum} %% for dummy text only
%% Use different colors for hyperlinks
\\usepackage[colorlinks,linkcolor=blue!50!black]{hyperref}
%% allow images
\\usepackage{graphicx}
%% for boxes behind text
\\usepackage[most]{tcolorbox}
%% for transparency
\\usepackage{transparent}
%% for images
\\usepackage{eso-pic}
\\newcommand\\BackgroundPic{%%
\\put(0,0){%%
\\parbox[b][\\paperheight]{\\paperwidth}{%%
\\vfill
\\centering
%% {\\transparent{0.4} \\includegraphics[width=\\paperwidth,height=\\paperheight,%%
{\\includegraphics[width=\\paperwidth,height=\\paperheight,keepaspectratio,clip]{%(coverimage)s}}%%
\\vfill
}}}
%%
%% End of preamble
%%
\\begin{document}
%% Add background picture on title page
\AddToShipoutPicture*{\BackgroundPic}
\\begin{titlepage}
\\begin{tcolorbox}
\\begin{center}
\\textbf{\\Large \color{Magenta} Valley of Heart's Delight %%
\\linebreak%%
\\linebreak%%
Literary Journal}
\\end{center}
\\end{tcolorbox}
\\vfill
\\begin{tcolorbox}
\\begin{center}
{\\large Volume %(volume)s, Number %(number)s, %(date)s}
\\end{center}
\\end{tcolorbox}

\\end{titlepage}
"""

MASTHEAD="""
\\thispagestyle{empty}
\\begin{center}
{\\large Valley of Heart's Delight Literary Journal}
\\linebreak
{A Literary Journal for the Adult Education Classes of the Silicon Valley}
\\linebreak
\\linebreak
{\\copyright %(year)s, Adult Education Press}
\\vfill
{Editor-in-chief: James Swenson}
\\linebreak
{Contributing Editors: John Doe, Jane Roe}
\\vfill
{Cover illustration: %(covercredit)s}
\\vfill
{Publisher's Representative: William C. Janssen}
\linebreak
{\\sc Published periodically by Adult Education Press.}
\\end{center}
%%
%% End of front matter
%% 
\\setcounter{page}{0}
\\newpage
"""

CONTENTSPAGE="""
\\pagestyle{empty}
\\journalcontents
"""

CONTRIBUTIONS_HEADER="""
\\journalpart[]{}
\\renewcommand*\\rmdefault{ppl}
\\pagestyle{fancy}
\\fancyhf{}
"""

CONTRIBUTION="""

%% ARTICLE %(articleindex)s

\\newpage
\\title{%(title)s}
\\author{%(author)s}
\\shortauthor{%(author)s}
\\maketitle
\\bigskip
%% make the header include the story title
\\fancyhead{}
\\fancyhead[RE,LO]{\\textit{%(title)s}}
\\fancyhead[LE,RO]{\\thepage}
"""

ILLUSTRATION="""
\\newpage
\\title{%(title)s}
\\author{%(author)s}
\\maketitle
\\bigskip
\\begin{figure}[b!]
\\includegraphics[width=\\linewidth]{%(filename)s}
\\caption{%(caption)s}
\\end{figure}
"""

FOOTER="""
\\end{document}
"""

## assume the data directory is the first arg

def build(dbdir, pdffile, coverimgfile):
    if not os.path.isdir(dbdir):
        raise Exception("Data directory given, " + dbdir + ", is not a directory")
    db = os.path.join(dbdir, "db.csv")
    if not os.path.exists(db):
        raise Exception("No database file; should be " + db)
    tempfiles = {}
    with open(db) as csvfile:
        dbreader = csv.DictReader(csvfile)
        for row in dbreader:
            print(row)
            filename = row['filename']
            # index, author, title, email, filename = row
            if not os.path.exists(filename):
                if not os.path.exists(os.path.join(dbdir, filename)):
                    raise Exception("Can't find file " + filename)
                else:
                    fullfilename = os.path.abspath(os.path.join(dbdir, filename))
            else:
                fullfilename = os.path.abspath('filename')
            print(row['title'], fullfilename)
            # convert file to latex
            handle, tempfilename = tempfile.mkstemp(".latex")
            os.close(handle)
            command = ("pandoc", "--to=latex", "--output="+tempfilename, fullfilename)
            print(command)
            status = runcommand(command)
            print("converted " + tempfilename + " with status " + str(status))
            if status != 0:
                raise Exception("Can't convert " + fullfilename + " to latex")
            tempfiles[row['index']] = {'articleindex': row['index'], 'author': row['author'], 'title': row['title'], 'email': row['email'], 'filename': tempfilename}

    print(tempfiles)

    # Now build the journal.  Assume volume=1, number=1 for now
    with tempfile.NamedTemporaryFile("w+", suffix=".latex") as outputfile:
        if coverimgfile is None or not os.path.exists(coverimgfile):
            coverimgfile = "data/cover.jpg"
        thisyear = datetime.datetime.now().year
        outputfile.write(HEADER % {'date': "Spring 2021", 'volume': 1, 'number': 1, 'coverimage': os.path.abspath(coverimgfile)})
        outputfile.write(MASTHEAD % {'year': thisyear, 'covercredit': "Bill Janssen"})
        outputfile.write(CONTENTSPAGE)
        outputfile.write(CONTRIBUTIONS_HEADER)
        for article in sorted(tempfiles):
            metadata = tempfiles[article]
            outputfile.write(CONTRIBUTION % metadata)
            outputfile.write(open(metadata['filename']).read())
        outputfile.write(FOOTER)
        outputfile.flush()
        # figure out the TeX jobname
        directory, filename = os.path.split(pdffile)
        jobname, extension = os.path.splitext(filename)
        command = ("pdflatex", "-jobname=" + jobname, "-output-directory="+directory, os.path.abspath(outputfile.name))
        # we need to run it twice to get the cross refs right
        runcommand(command)
        runcommand(command)
        # clean up individual latex files
        outputfile.seek(0)
        print(outputfile.read())
        for article in tempfiles.values():
            os.unlink(article['filename'])


if __name__ == "__main__":
    import sys, traceback
    try:
        if len(sys.argv) < 3:
            raise Exception("Not enough args")
        build(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    except:
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
