def createUPhaseData (uPhaseType, time, operator, uPhaseId, dictionary):
    uPhaseDataDict = {}
    uPhaseDataDict['uPhase'] = uPhaseType
    uPhaseDataDict['startTimestamp'] = uPhaseDataDict['endTimestamp'] = time
    uPhaseDataDict['startOperator'] = uPhaseDataDict['endOperator'] = operator
    uPhaseDataDict['uPhaseId'] = uPhaseId
    uPhaseDataDict['module'] = 'appPathologyManagement'
    return uPhaseDataDict