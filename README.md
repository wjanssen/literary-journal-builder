# literary-journal-builder

Code to take a DB of authors (a spreadsheet in CSV format) and their texts (in docx format) and build a PDF magazine from it

Requires the presence of pandoc (to convert submissions to TeX format) and pdflatex (to build the PDF file).

Note that the masthead literal contains a number of hard-coded names, and the magazine name is also hard-coded (in HEADING1).  They should probably be command-line options.

Produces a PDF file with trade paperback 6x9 inch pages, which works well with tablets.

The DB file should be a comma-separated-value file with the following
columns: index, type, author, title, email, filename.  Each column
should have the name of the column at the top, in the first row.
"index" specifies an ordinal value, the sort position of the article
in the journal.  "type" must currently be a string, either "poem" or
"story".  "author" is the name the author wants to be known by, will
be printed under the article title.  "email" is the email address of
the author, and will be used as a unique ID.  "filename" is the
filename of an either ".docx" or ".rtf" file containing the article
text, but not a title or author's name.  "filename" may be specified
relative to the location of the DB file.

Here's an example with only two articles:

```
index,type,author,title,email,filename
1,poem,John Doe,My Brilliant Poem,john337@does.org,mybrillant.rtf
2,story,Jane Roe,A Likely Story,jane1008@authoress.com,likelystory.docx
...
```


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
