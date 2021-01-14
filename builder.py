#!/usr/bin/env python3

import re, os, csv, tempfile, datetime
from subprocess import call as runcommand

# based on https://tex.stackexchange.com/questions/372807/how-do-i-make-a-full-journal-in-latex

# see https://www.sascha-frank.com/Fonts/Times_New_Roman.html
# see https://tex.stackexchange.com/questions/136742/changing-background-color-of-text-in-latex
# see https://tex.stackexchange.com/questions/46280/how-to-create-a-background-image-on-title-page-with-latex
#
# See the LaTeX book, https://upload.wikimedia.org/wikipedia/commons/2/2d/LaTeX.pdf, for more


# Use paper size good for tablets, recommended in LaTeX book, with 1 inch margins
PAGEWIDTH = 6.0         # inches
PAGEHEIGHT = 9.0        # inches
PAGEASPECT = PAGEWIDTH / PAGEHEIGHT

HEADER1="""
%% journal-style document, indent paragraphs, 12 point text
%% twoside -- printed for binding, openany -- don't wait for an even page to start new article
\\documentclass[12pt,journal,openany]{paper}
%% skip space between paragraphs instead of indenting them
\\usepackage{parskip}
\\usepackage[paperwidth=""" + str(PAGEWIDTH) + """in, paperheight=""" + str(PAGEHEIGHT) + """in]{geometry}
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
"""

COVERIMAGE1="""
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
{\\includegraphics[%(croplimit)s,keepaspectratio,clip]{%(coverimage)s}}%%
\\vfill
}}}
"""

HEADER2="""
%%
%% End of preamble
%%
\\begin{document}
"""

COVERIMAGE2="""
%% Add background picture on title page
\\AddToShipoutPicture*{\\BackgroundPic}
"""

HEADER3="""
\\begin{titlepage}
\\begin{tcolorbox}
\\begin{center}
\\textbf{\\Large \color{%(titlecolor)s} From the\\linebreak\\linebreak Valley of Heart's Delight}
\\end{center}
\\end{tcolorbox}
\\vfill
\\begin{tcolorbox}
\\begin{center}
{\\large Volume %(volume)s, Number %(number)s, %(issuedate)s}
\\end{center}
\\end{tcolorbox}

\\end{titlepage}
"""

MASTHEAD="""
\\thispagestyle{empty}
\\begin{center}
{\\large From the Valley of Heart's Delight}
\\linebreak
{A Literary Journal for the Adult Education Classes of the Silicon Valley}
\\linebreak
\\linebreak
{Copyright \\copyright  %(thisyear)s, Adult Education Press}
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
\\renewcommand*\\rmdefault{tmr}
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

def figure_cover_art_cropping(imagefile, pageaspect):
    from PIL import Image
    size = Image.open(imagefile).size
    aspectratio = float(size[0])/float(size[1])
    return 'width=\\paperwidth' if aspectratio < pageaspect else 'height=\\paperheight'

def build(args):
    db = args['dbfile']
    pdffile = args['output']
    contribs_dir = args['contribs']
    coverimagefile = args['coverart']
    if coverimagefile is not None:
        if not os.path.exists(coverimagefile):
            raise Exception("Specified cover image " + coverimagefile + " does not exist.")
        args['coverimage'] = os.path.abspath(coverimagefile)
        args['croplimit'] = figure_cover_art_cropping(coverimagefile, PAGEASPECT)
    if not os.path.exists(db):
        raise Exception("No database file; should be " + db)
    if not os.path.isdir(contribs_dir):
        raise Exception("Directory of contributions " + contribs_dir + " is not a directory.")
    tempfiles = {}
    with open(db) as csvfile:
        dbreader = csv.DictReader(csvfile)
        for row in dbreader:
            print(row)
            filename = row['filename']
            # index, author, title, email, filename = row
            if not os.path.exists(filename):
                if not os.path.exists(os.path.join(contribs_dir, filename)):
                    raise Exception("Can't find file " + filename)
                else:
                    fullfilename = os.path.abspath(os.path.join(contribs_dir, filename))
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
            tempfiles[row['index']] = {'articleindex': row['index'], 'type': row['type'], 'author': row['author'], 'title': row['title'], 'email': row['email'], 'filename': tempfilename}

    print(tempfiles)

    # Now build the journal.  Assume volume=1, number=1 for now
    with tempfile.NamedTemporaryFile("w+", suffix=".latex") as outputfile:
        args['thisyear'] = datetime.datetime.now().year
        outputfile.write(HEADER1 % args)
        if coverimagefile is not None:
            outputfile.write(COVERIMAGE1 % args)
        outputfile.write(HEADER2 % args)
        if coverimagefile is not None:
            outputfile.write(COVERIMAGE2 % args)
        outputfile.write(HEADER3 % args)
        outputfile.write(MASTHEAD % args)
        outputfile.write(CONTENTSPAGE)
        outputfile.write(CONTRIBUTIONS_HEADER)
        for article in sorted(tempfiles):
            metadata = tempfiles[article]
            if metadata['type'] not in ('story', 'poem'):
                continue
            metadata.update(args)
            outputfile.write(CONTRIBUTION % metadata)
            if metadata['type'] == 'story':
                outputfile.write(open(metadata['filename']).read())
            elif metadata['type'] == 'poem':
                outputfile.write("\\begin{verse}\n")
                for line in open(metadata['filename']).readlines():
                    if line.strip():
                        outputfile.write(line)
                    else:
                        outputfile.write("\\\\\n")
                outputfile.write("\\end{verse}\n")
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
    import sys, traceback, argparse
    parser = argparse.ArgumentParser(description="Build a magazine from submissions using LaTeX")
    parser.add_argument("--dbfile", required=True, help="required, specify spreadsheet file (.CSV format) or DB file to pull metadata from")
    parser.add_argument("--contribs", required=True, help="required, specify directory where contributions are, one per file, DOCX or RTF format")
    parser.add_argument("--output", required=True, help="required, specify PDF output file name")
    parser.add_argument("--issuedate", required=True, help="required, specify date string to use for issue")
    parser.add_argument("--volume", required=True, help="required, which volume of the magazine is it")
    parser.add_argument("--number", required=True, help="required, which number of the volume is it")
    parser.add_argument("--coverart", help="specify file containing cover art, if it exists")
    parser.add_argument("--covercredit", help="who gets credit for the cover art")
    parser.add_argument("--titlecolor", help="specify the color for the title font, from the set of the dvips color names", default="Black")
    args = parser.parse_args()
    try:
        build(vars(args))
    except:
        traceback.print_exc()
        sys.exit(1)
    else:
        sys.exit(0)
