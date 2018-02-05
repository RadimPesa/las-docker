from annotations.models import *
from annotations.lib.graph_utils import *
from django.db.models import Q

def runAnnotationQuery(source, criteria, genes, samples):
    if criteria == []:
        for l in LabelTerm.objects.filter(fatherLabel=None):
            criteria.append({'technology': '0', 'domain': l.id })

    if source == '0':
        return runDbQuery(criteria, genes, samples, True)
    elif source == '1':
        return runDbQuery(criteria, genes, samples, False)
    else:
        raise Exception("Invalid annotation source")

def runDbQuery(criteria, genes, samples, inGraph=False):
    relevant_analyses = selectRelevantAnalyses(criteria)
    print "Relevant analyses:", relevant_analyses
    annotations = {}

    # retrieve gene coordinates and build Q predicate
    gene_Q = {}
    if genes != []:
        ggu = GenomeGraphUtility()
        gene_infos = ggu.getGeneInfo_byUuid(uuid_list=genes)
        # build a different Q object for each LabelTerm involved in the query
        # (this is because different genomic models have different attributes,
        # for instance chrom/transcript depending e.g. on whether they involve gDNA or cDNA )
        for labelTerm_id in relevant_analyses.keys():
            labelTerm_model = LabelTerm.objects.get(pk=labelTerm_id).getAnnotationModel()
            # Q(chrom=x[3],start__gte=x[4],end__lte=x[5])
            Q_predicates = [Q(**labelTerm_model.getFilteringParams(gene_uuid=x[0],gene_symbol=x[1],chrom=x[3],start=x[4],end=x[5])) for x in gene_infos]
            gene_Q[labelTerm_id] = reduce(lambda a,b: a | b, Q_predicates, Q())
    else:
        for labelTerm_id in relevant_analyses.keys():
            gene_Q[labelTerm_id] = Q()

    # build Q predicate for samples
    if samples != []:
        Q_predicates = [Q(id_sample__regex=s) for s in [x.replace('-', '.') for x in samples]]
        sample_Q = reduce(lambda a,b: a | b, Q_predicates, Q())
    else:
        sample_Q = Q()

    # build Q predicate for inGraph condition
    if inGraph == True:
        inGraph_Q = ~Q(annot_graph_uuid=None)
    else:
        inGraph_Q = Q()

    failed = Q(failed=False)

    # retrieve annotations for each domain of interest
    for labelTerm_id, analysis_list in relevant_analyses.iteritems():
        try:
            labelTerm = LabelTerm.objects.get(pk=labelTerm_id)
        except Exception as e:
            print e
            continue
        # analysis predicate
        analysis_Q = Q(id_analysis__in=analysis_list)
        annotationModel = labelTerm.getAnnotationModel()
        annotations[labelTerm_id] = annotationModel.objects.filter(analysis_Q & gene_Q[labelTerm_id] & sample_Q & inGraph_Q & failed)
    
    print "Annotations:", annotations
    return annotations

def selectRelevantAnalyses(criteria):
    relevant_analyses = {k:[] for k in set([x['domain'] for x in criteria])}
    for cr in criteria:
        if cr['technology'] == '0':
            relevant_analyses[cr['domain']].extend(Analysis.objects.filter(refSet__expTypeHasLabelTerm__labelTerm_id=cr['domain']))
        else:
            relevant_analyses[cr['domain']].extend(Analysis.objects.filter(refSet__expTypeHasLabelTerm__labelTerm_id=cr['domain'], refSet__expTypeHasLabelTerm__expType_id=cr['technology']))
            
    for domain in relevant_analyses.keys():
        relevant_analyses[domain] = list(set(relevant_analyses[domain]))
    return relevant_analyses
