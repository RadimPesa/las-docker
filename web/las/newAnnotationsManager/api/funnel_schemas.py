results = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Funnel - Submit Experiment Results",
    "description": "A batch of experiment results",
    "type": "object",
    "properties": {
        "results": {
            "description": "An array of results",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "source": {
                        "description": "The source sending the results",
                        "type": "string"
                    },
                    "childBarcode": {
                        "description": "The barcode of the analysed sample",
                        "type": "string"
                    },
                    "experimentType": {
                        "description": "A keyword defining the type of the experiment",
                        "type": "string"
                    },
                    "reportId": {
                        "description": "The id of the experiment report including the results (on the sender's side)",
                        "type": "string"
                    },
                    "rawURLs": {
                        "description": "An array of URLs from which the raw experiment data shall be retrieved",
                        "type": "array",
                        "minItems": 0,
                        "items": {
                            "type": "string"
                        }
                    },
                    "dataURLs": {
                        "description": "An array of URLs from which the structured experiment data shall be retrieved",
                        "type": "array",
                        "minItems": 0,
                        "items": {
                            "type": "string"
                        }
                    }
                },
                "required": ["source", "childBarcode", "experimentType", "reportId", "rawURLs", "dataURLs"]
            }
        }
    },
    "required": ["results"]
}

geneticlab_data = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Funnel - Interchange Format for Genetic Results",
    "description": "A batch of genetic results stored in a file",
    "type": "object",
    "properties": {
        "results": {
            "description": "An array of results",
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "geneId": {
                        "description": "The id of the analysed gene",
                        "type": "string"
                    },
                    "validity": {
                        "description": "A boolean flag indicating whether the analysis of the current mutation was successful or not",
                        "type": "boolean"
                    },
                    "result": {
                        "description": "The genetic result of the test",
                        "type": "string"
                    },
                    "fraction": {
                        "description": "The fraction of the sample affected by the mutation (optional)",
                        "type": "number"
                    }
                },
                "required": ["geneId", "validity", "result"]
            }
        }
    },
    "required": ["results"]    
}

results_exampleData = {
    "results": [{
        "source": "GeneticLab",
        "childBarcode": "001",
        "experimentType": "FUN-CUST",
        "reportId": "r001",
        "rawURLs": ["http://data.org/raw/001_1", "http://data.org/raw/001_2"],
        "dataURLs": ["http://data.org/data/001_1"]
        },
        {
        "source": "GeneticLab",
        "childBarcode": "002",
        "experimentType": "FUN-CUST",
        "reportId": "r002",
        "rawURLs": ["http://data.org/raw/002_1"],
        "dataURLs": ["http://data.org/data/002_1"]
        }
    ]
}

geneticResults_exampleData = {
    "results": [
        { 
            "geneId" : "KRAS",
            "validity" : True,
            "result" : "abc",
            "fraction" : 0.25
        },
        {
            "geneId" : "KRAS",
            "validity" : False,
            "result" : "def",
            "fraction" : 0.75
        },
        {
            "geneId" : "BRAF",
            "validity" : True,
            "result" : "abc"
        }
    ]
}
