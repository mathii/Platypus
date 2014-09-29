import logging
'''
Helper functions for the aDNA pipeline.
'''

ENDS=["5","3"]
CpG=["CpG", "noCpG"]
BASES=["A","C","G","T"]

def damageProfileCallback(option, opt_str, infile, parser): 
    '''
    Parse the damage profile. This is defined as follows. Column headings [CpG]_[end]_[base] 
    where CpG and end are optional. Each row has phred scores for the probability that the base 
    that distance from the end is incorrect. If a column just has a base then it will fill in all
    the CpG and end categories. Rightwards columns replace leftwards ones. First column is ignored. 
    :param infile:
    '''

    # Create a logger
    logger = logging.getLogger("ATemporaryLog")
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    ch.setLevel(logging.DEBUG)
    logger.setLevel(logging.DEBUG)

    inlines=open(infile)
    maxbase=sum(1 for line in inlines)-1
    inlines.seek(0) 

    header=inlines.next()
    bits=header.split()[1:]
    keys=[[] for x in bits]

    for i,bit in enumerate(bits):
        key=bit.split("_")
        if len(key)==1 and key[0] in BASES:
            for cpg in CpG:
                for end in ENDS:
                    keys[i].append([cpg,end,key[0]])
        elif len(key)==2 and key[0] in ENDS and key[1] in BASES:
            for cpg in CpG:
                keys[i].append([cpg, key[0], key[1]])
        elif len(key)==2 and key[0] in CpG and key[1] in BASES:
            for end in ENDS:
                keys[i].append([key[0], end, key[1]])
        elif len(key)==3 and key[0] in CpG and key[1] in ENDS and key[2] in BASES:
            keys[i].append(key)
        else:
            logger.warning("Ignoring damage profile column "+bit)

    profile={}
    for cpg in CpG:
        profile[cpg]={}
        for end in ENDS:
            profile[cpg][end]={}
            for base in BASES:
                profile[cpg][end][base]=[0.0]*maxbase
                
    for l,line in enumerate(inlines):
        bits=[float(x) for x in line.split()[1:]]
        for i,bit in enumerate(bits):
            for key in keys[i]:
                profile[key[0]][key[1]][key[2]][l]=bits[i]

    logger.info("Read damage profile as follows")
    for k0,v0 in profile.items():
        for k1,v1 in v0.items():
            for k2,v2 in v1.items():
                logger.info(k0+"_"+k1+"_"+k2+" : "+",".join([str(x) for x in v2]))
    parser.values.damageProfile=profile
        
    
    