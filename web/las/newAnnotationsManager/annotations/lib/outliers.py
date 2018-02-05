'''
outliers library

It consists of five different classifiers (test_outliers_xx -- see each function for details) based on diverse methodologies (statistical, clustering-based).
Each classifier classifies a set of single-dimensional points as normal or outliers.
The input to each function is a list of points, the output is a boolean-valued list where the i-th entry will be 1 if the i-th element in the input list has been classified as an outlier, and 0 viceversa.

The library might be used by making a single call to the test_outliers function, which will in turn call each of the classifiers. For each point, the result returned by test_outliers is based on a majority rule (i.e., each point will be assigned the label that was assigned to it by most classifiers)
'''

import numpy as np

def test_outliers_1(data, k=None):
    # approach #1 (statistical)
    # assume normal distribution, use z-score as outlier score
    k = k or 2
    d = np.array(data)
    return [1 if x else 0 for x in (np.abs(d - np.mean(d))/np.std(d, ddof=1) > k)]


def test_outliers_2(data, k=None):
    # approach #2 (statistical)
    # no assumption about distribution, use median absolute deviation (MAD) as indicator of statistical dispersion (more resilient to outliers)
    k = k or 2
    d = np.array(data)
    median = np.median(d)
    distanceToMedian = np.abs(d - median)
    medianDistanceToMedian = np.median(distanceToMedian)
    return [1 if x else 0 for x in (distanceToMedian/medianDistanceToMedian > k)]


def test_outliers_3(data, k=None):
    # approach #3 (statistical)
    # use inter-quartile range (IQR) as indicator of statistical dispersion
    # outliers are values that do not lie within 1.5 IQR from the first and third quartiles
    k = k or 1.5
    d = np.array(data)
    q75, q25 = np.percentile(d, [75, 25])
    iqr = q75 - q25
    return [1 if x or y else 0 for x, y in zip(list(d < q25 - 1.5 * iqr), list(d > q75 + 1.5 * iqr))]

def test_outliers_3b(data, k=None):
    # approach #3 (statistical)
    # use inter-quartile range (IQR) as indicator of statistical dispersion
    # outliers are values that do not lie within 1 IQR from the second quartile
    # (more restrictive)
    k = k or 1.5
    d = np.array(data)
    q75, q50, q25 = np.percentile(d, [75, 50, 25])
    iqr = q75 - q25
    return [1 if x else 0 for x in (np.abs(d - q50) > iqr)]


def test_outliers_4(data, k=None, s=None):
    # approach #4 (density-based with average relative density)
    # implementation of algorithm 10.2 in Tan, Steinbach, Kumar. Introduction to data mining
    if len(data) < 3:
        return None
    k = min(k, len(data)-1) if k else min(5, len(data) - 1)
    s = s or 0.6
    neighbours = [None for i in xrange(0, len(data))]
    distance_to_neighbours = [None for i in xrange(0, len(data))]
    density = [None for i in xrange(0, len(data))]
    avg_rel_density = [None for i in xrange(0, len(data))]
    for i,p in enumerate(data):
        distances = sorted([(abs(q-p), j) for j,q in enumerate(data) if j != i])
        distance_to_neighbours[i] = [x[0] for x in distances[:k]]
        neighbours[i] = [x[1] for x in distances[:k]]
        density[i] = k / sum(distance_to_neighbours[i])
    for i,p in enumerate(data):
        avg_rel_density[i] = k * density[i] / sum([density[j] for j in neighbours[i]])
    outlier_score = 1/np.array(avg_rel_density)
    norm_score = (outlier_score - np.min(outlier_score))/(np.max(outlier_score)-np.min(outlier_score))
    return [1 if x else 0 for x in (norm_score > s)]

def test_outliers(data):
    perc_vote = 0.5
    classifiers = [test_outliers_1, test_outliers_2, test_outliers_3, test_outliers_3b, test_outliers_4]
    thresh = np.ceil(len(classifiers) * perc_vote)
    scores = []
    for c in classifiers:
        scores.append(c(data))
    s = np.array(scores)
    s = s.sum(axis=0)
    return list(s >= thresh)