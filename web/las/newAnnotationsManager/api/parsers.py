import jsonschema
from rest_framework.exceptions import ParseError
from rest_framework.parsers import JSONParser
 
import funnel_schemas
import newapi_schema
 
 
class FunnelResultParser(JSONParser):
 
    def parse(self, stream, media_type=None, parser_context=None):
        data = super(FunnelResultParser, self).parse(stream, media_type,
                                                   parser_context)
        try:
            jsonschema.validate(data, funnel_schemas.results)
        except ValueError as error:
            raise ParseError(detail=error.message)
        else:
            return data

class GeneticLabDataParser(JSONParser):
 
    def parse(self, stream, media_type=None, parser_context=None):
        data = super(GeneticLabDataParser, self).parse(stream, media_type,
                                                   parser_context)
        try:
            jsonschema.validate(data, funnel_schemas.geneticlab_data)
        except ValueError as error:
            raise ParseError(detail=error.message)
        else:
            return data

class GenesParser(JSONParser):
 
    def parse(self, stream, media_type=None, parser_context=None):
        data = super(GeneParser, self).parse(stream, media_type,
                                                   parser_context)
        try:
            jsonschema.validate(data, newapi_schema.genes)
        except ValueError as error:
            raise ParseError(detail=error.message)
        else:
            return data