genes = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "title": "Genes",
    "description": "Get (gene id, gene symbol) pairs where gene symbol matches the given prefix",
    "type": "object",
    "properties": {
        "q": {
            "description": "A query prefix to be matched against gene symbols",
            "type": "string"
        }
    },
    "required": ["q"]
}