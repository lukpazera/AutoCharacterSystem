

import os
import lx
import rs


def countLines(pythonPaths, cppPaths, title):
    rs.log.out('---')
    rs.log.out(title)
    rs.log.out('---')
    lineCount = countPython(pythonPaths)
    lineCount += countCPP(cppPaths)
    rs.log.out('Total lines: %d' % lineCount)
    rs.log.out('---')
    
def countCPP(paths):
    if paths is None or not paths:
        return
    
    files = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for f in filenames:
                files.append(os.path.join(dirpath, f))

    cppFiles = []
    for filename in files:
        if filename.endswith('.cpp') or filename.endswith('.hpp'):
            cppFiles.append(filename)

    lineCount = 0
    docstringLineCount = 0
    commentLineCount = 0
    blankLineCount = 0
    codeLineCount = 0
    for fname in cppFiles:
        with open(fname) as f:
            lines = f.readlines()
            fileLineCount = len(lines)
            docstring = False
            for line in lines:
                if line.find('/*') >= 0:
                    docstring = True
                elif line.find('*/') >= 0:
                    docstring = False

                if docstring:
                    docstringLineCount += 1
                elif len(line) <= 4:
                    blankLineCount += 1
                elif line.find('//') >= 0:
                    commentLineCount += 1
                else:
                    codeLineCount += 1
        lineCount += fileLineCount

    codePercent = (float(codeLineCount) / float(lineCount) * 100.0)
    docstringPercent = (float(docstringLineCount) / float(lineCount) * 100.0)
    commentPercent = (float(commentLineCount) / float(lineCount) * 100.0)
    blanksPercent = (float(blankLineCount) / float(lineCount) * 100.0)
    
    rs.log.out('C++ codebase breakdown:')
    rs.log.startChildEntries()
    rs.log.out('Source files: %d' % len(cppFiles))
    rs.log.out('Source lines: %d' % lineCount)
    rs.log.out('Code lines: %d (%.1f %%)' % (codeLineCount, codePercent))
    rs.log.out('Comment lines: %d (%.1f %%)' % (docstringLineCount + commentLineCount, docstringPercent + commentPercent))
    rs.log.out('Blank lines: %d (%.1f %%)' % (blankLineCount, blanksPercent))
    rs.log.stopChildEntries()

    return lineCount

def countPython(paths):
    if paths is None or not paths:
        return
 
    files = []
    for path in paths:
        for (dirpath, dirnames, filenames) in os.walk(path):
            for f in filenames:
                files.append(os.path.join(dirpath, f))

    pythonFiles = []
    for filename in files:
        if filename.endswith('.py'):
            pythonFiles.append(filename)

    lineCount = 0
    docstringLineCount = 0
    commentLineCount = 0
    blankLineCount = 0
    codeLineCount = 0
    for fname in pythonFiles:
        with open(fname) as f:
            lines = f.readlines()
            fileLineCount = len(lines)
            docstring = False
            for line in lines:
                if line.find('"""') >= 0:
                    docstring = not docstring

                if docstring:
                    docstringLineCount += 1
                elif len(line) <= 4:
                    blankLineCount += 1
                elif line.find(' #') >= 0:
                    commentLineCount += 1
                else:
                    codeLineCount += 1
        lineCount += fileLineCount

    codePercent = (float(codeLineCount) / float(lineCount) * 100.0)
    docstringPercent = (float(docstringLineCount) / float(lineCount) * 100.0)
    commentPercent = (float(commentLineCount) / float(lineCount) * 100.0)
    blanksPercent = (float(blankLineCount) / float(lineCount) * 100.0)
    
    rs.log.out('Python codebase breakdown:')
    rs.log.startChildEntries()
    rs.log.out('Source files: %d' % len(pythonFiles))
    rs.log.out('All source lines: %d' % lineCount)
    rs.log.out('Code lines: %d (%.1f %%)' % (codeLineCount, codePercent))
    rs.log.out('Docstring and comment lines: %d (%.1f %%)' % (docstringLineCount + commentLineCount, docstringPercent + commentPercent))
    rs.log.out('Blank lines: %d (%.1f %%)' % (blankLineCount, blanksPercent))
    rs.log.stopChildEntries()

    return lineCount