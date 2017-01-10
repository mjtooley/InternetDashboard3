class Asn:
    def __index__(self):
        self.asn = dict()
        self.asn['7922'] = 'Comcast'
        self.asn['22773'] = 'Cox'
        self.asn['20115'] = 'Charter'
        self.asn['6128'] = 'AlticeUSA'
        self.asn['30036'] = 'Mediacom'
        self.asn['10796'] = 'Charter'
        self.asn['11351'] = 'Charter'
        self.asn['11426'] = 'Charter'
        self.asn['11427'] = 'Charter'
        self.asn['12271'] = 'Charter'
        self.asn['20001'] = 'Charter'
        self.asn['19108'] = 'AlticeUSA'
        self.asn['7018'] = 'ATT'
        self.asn['20057'] = 'ATT'
        self.asn['701'] = 'Verizon'
        self.asn['702'] = 'Verizon'
        self.asn['22394'] = 'Verizon Wireless'
        self.asn['209'] = 'CenturyLink'
        self.asn['22561'] = 'CenturyLink'
        self.asn['26868'] = 'NCTA'
        self.asn['6939'] = 'Hurricane Electric'
        self.asn['174'] = 'Cogent'
        self.asn['3549'] = 'Level 3'
        self.asn['5650'] = 'Frontier'
        self.asn['11492'] = 'CableOne'

    def getNetworkName(self,asn):
        if asn in dict:
            name = self.asn[asn]
        else:
            name = 'unknown'
        return name


asn = {}
asn[7922] = 'Comcast'
asn[22773] = 'Cox'
asn[20115] = 'Charter'
asn[6128] = 'AlticeUSA'
asn[30036] = 'Mediacom'
asn[10796] = 'Charter'
asn[11351] = 'Charter'
asn[11426] = 'Charter'
asn[11427] = 'Charter'
asn[12271] = 'Charter'
asn[20001] = 'Charter'
asn[19108] = 'AlticeUSA'
asn[7018] = 'ATT'
asn[20057] = 'ATT'
asn[701] = 'Verizon'
asn[702] = 'Verizon'
asn[22394] = 'Verizon Wireless'
asn[209] = 'CenturyLink'
asn[22561] = 'CenturyLink'
asn[26868] = 'NCTA'
asn[6939] = 'Hurricane Electric'
asn[174] = 'Cogent'
asn[3549] = 'Level 3'
asn[5650] = 'Frontier'
asn[11492] = 'CableOne'

if source_asn in dict:
    name = asn[source_asn]
else:
    name = 'unknown'
return name