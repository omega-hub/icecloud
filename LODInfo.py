class LODInfo:
    def __init__(self, batchSize, maxDist, numLevels, minDec, maxDec):
        self.batchSize = batchSize
        self.maxDist = maxDist
        self.numLevels = numLevels
        self.minDec = minDec
        self.maxDec = maxDec
        # TODO: implement actual LOD string generator.
        self.lodOptionString = "500000 1000:1000000:50 200:1000:10 0:200:2"