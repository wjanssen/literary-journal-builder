# literary-journal-builder

Code to take a DB of authors and their texts (in docx format) and build a PDF magazine from it

Requires the presence of pandoc (to convert submissions to TeX format) and pdflatex (to build the PDF file).

Note that the masthead literal contains a number of hard-coded names, and the magazine name is also hard-coded (in HEADING1).  They should probably be command-line options.

Produces a PDF file with trade paperback 6x9 inch pages, which works well with tablets.

To use:

```
% python3 builder.py --dbfile <data directory>/db.csv --contribs <data directory> --output /tmp/foo.pdf --coverart <data directory>/cover.jpg --covercredit "John Smith" --volume 1 --number 1 --issuedate "Spring 2021"
% python3 builder.py -h
usage: builder.py [-h] --dbfile DBFILE --contribs CONTRIBS --output OUTPUT --issuedate ISSUEDATE --volume VOLUME --number NUMBER [--coverart COVERART]
                  [--covercredit COVERCREDIT] [--titlecolor TITLECOLOR]

Build a magazine from submissions using LaTeX

optional arguments:
  -h, --help            show this help message and exit
  --dbfile DBFILE       required, specify spreadsheet file (.CSV format) or DB file to pull metadata from
  --contribs CONTRIBS   required, specify directory where contributions are, one per file, DOCX or RTF format
  --output OUTPUT       required, specify PDF output file name
  --coverart COVERART   specify file containing cover art, if it exists.  An image file.
  --covercredit COVERCREDIT
                        who gets credit for the cover art
  --issuedate ISSUEDATE
                        required, specify date string to use for issue
  --volume VOLUME       which volume of the magazine is it
  --number NUMBER       which number of the volume is it
  --titlecolor TITLECOLOR
                        specify the color for the title font, from the set of the dvips color names
%
```
