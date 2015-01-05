class LODInfo:
    def __init__(self, batchSize, maxDist, numLevels, minDec, maxDec):
        self.batchSize = batchSize
        self.maxDist = maxDist
        self.numLevels = numLevels
        self.minDec = minDec
        self.maxDec = maxDec
        # TODO: implement actual LOD string generator.
        self.lodOptionString = "500000 0:100:20 20:100:50 0:1000000:200"