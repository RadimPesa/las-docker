import argparse, numpy, operator, random, datetime


def filterByRange(data, minr, maxr):
    for k, v in data.items():
        if v <minr or v > maxr:
            del data[k]
    #print 'Filter data by range'
    #print data, len (data)


def filterByWindow(data, nel, th, minavg, maxavg):
    sortedData = sorted(data.iteritems(), key=operator.itemgetter(1))
    #print sortedData
    window = {}
    for x in range(0, len(sortedData)-nel+1):
        #print x, sortedData[x:x+nel]
        window[x] = numpy.absolute( th - numpy.mean([y[1] for y in sortedData[x:x+nel]]) )
    sorted_win = sorted(window.iteritems(), key=operator.itemgetter(1))
    #print 'Sliding windows values (Fist is the best one)'
    #print sorted_win
    meanRange = numpy.mean ( [x[1] for x in sortedData[sorted_win[0][0]:sorted_win[0][0]+nel]] )
    if meanRange > maxavg or meanRange < minavg:
        return False

    newRange = (sortedData[ sorted_win[0][0] ][1], sortedData[ sorted_win[0][0]+nel-1 ][1])
    #print 'Selected range'
    #print newRange
    filterByRange(data, newRange[0], newRange[1])
    return True





def defineBuckets(data, nel, ngroups):
    sortedData = sorted(data.iteritems(), key=operator.itemgetter(1))
    buckets = {}
    #print sortedData
    for x in range(nel):
        seq = range(ngroups)
        for i in range(ngroups):
            j = random.choice(seq)
            # print x, i, j, (x*ngroups)+j, sortedData[x*ngroups+j]
            if not buckets.has_key(i):
                buckets[i] = {'mean':None, 'std':None, 'coeffVar':None, 'elements':[]}
            buckets[i]['elements'].append(sortedData[(x*ngroups)+j])
            seq.remove(j)
    #print buckets
    distAvg = []
    for k, v in buckets.items():
        #print k, numpy.mean( [el[1] for el in v ] ), numpy.std( [el[1] for el in v ] )
        mval = numpy.mean( [el[1] for el in v['elements'] ] )
        stdval = numpy.std( [el[1] for el in v['elements'] ] )
        buckets[k]['mean'] = mval
        buckets[k]['std'] = stdval
        buckets[k]['coeffVar'] = stdval/mval
        distAvg.append( mval )
    #print distAvg
    return buckets, numpy.mean(distAvg), numpy.std(distAvg), numpy.std(distAvg)/numpy.mean(distAvg)


def randomizeGroups(data, th, minr, maxr, minavg, maxavg, ngroups, nel, resampling):
    #print 'Initial data'
    #print data, len(data)
    filterByRange(data, minr, maxr)
    
    buckets = []
    if (len(data) >= ngroups * nel):
        if not filterByWindow(data, ngroups * nel, th, minavg, maxavg):
            return []
        for i in range(resampling):
            b, mval, stdval, coeffVar = defineBuckets(data, nel, ngroups)
            buckets.append({'buckets':b, 'coeffVar':coeffVar, 'mean':mval, 'std': stdval})
        print 'Best solution:'
        sortedBuckets = sorted(buckets, key=operator.itemgetter('coeffVar'))
        #print sortedBuckets[0]
        print 'Global mean: ' + str(sortedBuckets[0]['mean'])
        print 'Global std: ' +str(sortedBuckets[0]['std'])
        print 'Global coeff Var: ' +str(sortedBuckets[0]['coeffVar'])
        print 
        print '+++++Buckets+++++'
        for k, v in sortedBuckets[0]['buckets'].items():
            print 'Bucket Id: ' + str(k) + ':'
            print 'Mean: ' +str(v['mean'])
            print 'Std: ' +str(v['std'])
            print 'Coeff Var: ' +str(v['coeffVar'])
            print '-----Elements-----'
            for val in v['elements']:
                print str(val[0]) + ' with value ' + str(val[1])
            print '******************'
            print 

        return sortedBuckets[0]
    else:
        return []



if __name__=='__main__':
    parser = argparse.ArgumentParser(description='Randomize group of elements with the same average')
    parser.add_argument('--input', type=str, help='Input file')
    parser.add_argument('--th', type=float, help='Threshold')
    parser.add_argument('--minr', type=float, help='Min value range')
    parser.add_argument('--maxr', type=float, help='Max value range')
    parser.add_argument('--arms', type=int, help='Number of arms')
    parser.add_argument('--nmice', type=int, help='Number of mice per arm')
    parser.add_argument('--resampling', type=int, help='Number of iterations')
    parser.add_argument('--minavg', type=int, help='Min range average')
    parser.add_argument('--maxavg', type=int, help='Max range average')
    args = parser.parse_args()
    fin = open (args.input)
    data = {}
    for line in fin:
        tokens = line.strip().split('\t')
        data[tokens[0]] = float(tokens[1])
    fin.close()
    #print 'Initial data'
    #print data, len(data)
    start = datetime.datetime.now()
    bucket = randomizeGroups(data, args.th, args.minr, args.maxr, args.minavg, args.maxavg, args.arms, args.nmice, args.resampling)
    print datetime.datetime.now()-start
    