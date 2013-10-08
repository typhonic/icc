#! /usr/bin/env python

# compare blocks in two icc print files for changes
# parse foxboro ICC dump
# get a list of records
# oldfieldvalues is a list of parameter values
# newfieldvalues is a list of parameter values
# fieldnames is a list of parameter names

# this program will determine and print the following reports
# deleted blocks
# new blocks
# modified compounds
# modified blocks
# modified parameters

import fileinput

# the lists of old and new filenames should be in the same order
oldpath = 'C:/Users/data'
oldICCfilenamelist = [oldpath + '/file1.txt']
newpath = oldpath
newICCfilenamelist = [newpath + '/file2.txt']

def parseiccprint(lines):
    """
    Collect the field values in one list and the names in another.

    """
    # if this list includes equal signs use parseiccprint2
    if '=' in lines[0]:
        fieldnames, fieldvalues = parseiccprint2(lines)
    else:
        fieldnames, fieldvalues = parseiccprint1(lines)
    return fieldnames, fieldvalues

def parseiccprint1(lines):
    """
    Collect the field values in one list and the names in another.

    There are three lines of file header information
    Blank lines separate the records
    There is no blank line following the final record
    A blank line separates the COMPOUND:BLOCK from the rest of the record

    If the iccprint file has equal signs then it follows a different layout.
    In that case, call parseiccprint2().
    """

    # initialization
    fieldnames=[]
    fieldvalues=[]
    namelist=[]
    valuelist=[]
    blocktype=""
    fieldname=""
    firstblank = True

    # there is no blank line following the final record
    # so append one to make life easier
    lines.append('')
    # start at line 5
    for line in lines[5:]:
        # check for first blank
        if ((not line.strip()) and firstblank):
            # this is the first blank line, after the COMPOUND:BLOCK
            firstblank = False
        elif not line.strip():
            # this is the second blank and end of the record
            firstblank = True
            fieldvalues.append(valuelist)
            fieldnames.append(namelist)
            valuelist=[]
            namelist=[]
        elif (line.strip() and firstblank):
            # this is the COMPOUND:BLOCK
            namelist=[]
            valuelist=[]
            namelist.append(line.strip())
            valuelist.append(line.strip())
        else:
            # this is a field record
            # get the header information which includes the parameter names
            fieldname = line.split()[0:1]
            namelist.append(fieldname[0])

            # get the block type
            if fieldname[0]=='TYPE':
                # replace the first field in the namelist
                # with the block type name
                blocktype=line.split()[1:]
                namelist[0] = blocktype[0]

            # get the parameter value
            # use split to drop the field name
            catstr=""
            for y in line.split()[1:]:
                catstr = catstr + y.strip() + " "
            valuelist.append(catstr.strip())
    return fieldnames, fieldvalues

def parseiccprint2(lines):
    # parse print file
    # collect the field values in one list and the names in another
    # every line has an equal except the 'end' of each record
    # each record ends with 'END'
    # there are no blank lines

    # initialization
    fieldnames=[]
    fieldvalues=[]
    namelist=[]
    valuelist=[]
    blocktype=''
    fieldname=''

    # start at line 0
    for line in lines:
        # check for END
        if line == 'END':
            # close out and save this record
            # replace the first field in the namelist with the type
            namelist[0] = valuelist[1]
            # insert the blockname at 1
            valuelist.insert(1, valuelist[0].partition(':')[2])
            fieldvalues.append(valuelist)
            fieldnames.append(namelist)
            valuelist=[]
            namelist=[]
        else:
            # this is a field record
            # get the header information which includes the parameter names
            fieldname = line.partition('=')[0].strip()
            namelist.append(fieldname)
            # get the parameter value
            catstr = line.partition('=')[2].strip()
            catstr = ' '.join(catstr.split())
            valuelist.append(catstr)
    # add NAME at 1
    for y in fieldnames:
        y.insert(1, 'NAME')
    return fieldnames, fieldvalues

def make_list_unique(seq):
    # make list unique
    # order preserving
    checked = []
    for e in seq:
        if e not in checked:
            checked.append(e)
    return checked

def finddeletedblocks(oldfieldvalues, newfieldvalues):
    # find deleted blocks list
    # these are blocks which only occur in the first list
    deletedblocks = []
    for y in oldfieldvalues:
        foundmatch = False
        for z in newfieldvalues:
            if y[0] == z[0]:
                foundmatch = True
                break
        if not foundmatch:
            deletedblocks.append(y[0])
    return deletedblocks

def printlist(header, plist):
    # print list
    print
    print header
    for y in plist:
        print y

def findmodifiedparameters(oldfieldvalues, newfieldvalues):
    # find modified parameters
    modifiedparameters = []    
    for y in oldfieldvalues:
        for z in newfieldvalues:
            if y[0] == z[0]:
                # these have the same block name
                if not y == z:
                    # these blocks have some differences
                    for i in range(0,len(y)):
                        # compare each block parameter-by-parameter
                        if y[i] != z[i]:
                            # there is a difference
                            # find the current parameter name 
                            for w in fieldnames:
                                if w[0] == y[2]:
                                    # w is the field name for the data in y, that is, the blocktypes are a match
                                    # i is the number of the particular parameter we are looking at now
                                    parametername = w[i]
                                    break
                            # save changes to print
                            modifiedparameters.append(y[0]+', '+parametername+', '+y[i]+', '+z[i])
    modifiedparameters[:] = sorted(modifiedparameters)
    return modifiedparameters

for fileindex in range(0,len(newICCfilenamelist)):
    # initialization
    fieldnames=[]
    fieldnamestemp=[]
    oldfieldvalues=[]
    newfieldvalues=[]
    lines=[]

    print 'Comparing:'
    print oldICCfilenamelist[fileindex] + ' old to:'
    print newICCfilenamelist[fileindex] + ' new'
    
    # open the old ICCPrint file to read
    openfile = open(oldICCfilenamelist[fileindex], 'r')
    lines = openfile.readlines()
    openfile.close()

    # delete extra end of line characters
    lines[:] = [line.strip() for line in lines]

    # parse parameter names and parameter values
    fieldnamestemp[:], oldfieldvalues[:] = parseiccprint(lines)
            
    # append blocks from all print files that are read
    fieldnames.extend(fieldnamestemp)

    # make unique list of block type headers
    fieldnames[:] = make_list_unique(fieldnames)

    # open the new ICCPrint file to read
    openfile = open(newICCfilenamelist[fileindex], 'r')
    lines = openfile.readlines()
    openfile.close()

    # delete extra end of line characters
    lines[:] = [line.strip() for line in lines]

    # parse parameter names and parameter values
    fieldnamestemp[:], newfieldvalues[:] = parseiccprint(lines)

    # append block headers from all print files that are read
    fieldnames.extend(fieldnamestemp)

    # make unique list of block type headers
    fieldnames[:] = make_list_unique(fieldnames)

    # sort the list of field names
    fieldnames[:] = sorted(fieldnames)

    # this is where the search for changes begins --------------------------------
    deletedblocks= finddeletedblocks(oldfieldvalues, newfieldvalues)
    printlist('Deleted Blocks', deletedblocks)
    
    newblocks = finddeletedblocks(newfieldvalues, oldfieldvalues)
    printlist('Added Blocks', newblocks)

    modifiedparameters = findmodifiedparameters(oldfieldvalues, newfieldvalues)

    # find modified blocks before printing the modified parameters
    modifiedblocks = []
    modifiedblocks[:] = [y.partition(',')[0] for y in modifiedparameters]
    modifiedblocks[:] = make_list_unique(modifiedblocks)
    modifiedblocks[:] = sorted(modifiedblocks)
    
    # print a list of modified blocks from the list of modified parameters
    printlist('Modified Blocks', modifiedblocks)

    # find modified compounds from the list of modified blocks
    modifiedcompounds = []
    modifiedcompounds[:] = [y.partition(':')[0] for y in modifiedblocks]
    modifiedcompounds[:] = make_list_unique(modifiedcompounds)
    modifiedcompounds[:] = sorted(modifiedcompounds)

    # print a list of modified blocks from the list of modified parameters
    printlist('Modified Compounds', modifiedcompounds)

    print
    print 'Modified Parameters'
    if True and modifiedparameters:
        # print modified parameters
        print 'Block, Parameter, Old_Value, New_Value'
        # keep track of the blockname in the first field
        # and print a blank line between groups of changed parameters
        # initialize previousblock
        previousblock = modifiedparameters[0].partition(',')[0]
        # z1 is a list blocks derived from the list of block.params
        for y in modifiedparameters:
            if previousblock != y.partition(',')[0]:
                # this block is different from the previous one
                # so print a blank line
                print
                # reset previousblock to match the current block
                previousblock = y.partition(',')[0]
            print y
    print '------------------------------------------------------------'
print 'done'
