AND   = 0
IN    = 1
OR    = 2
NOTIN = 3
GB    = 4
GENID = 5
QE    = 6
DISTINCT = 7
STAR = 8
MIN = 9
MAX = 10
AVG = 11
TEMPLATE = 12
EXTEND = 13
BASKET = 14

PK_TYPE = 10

phi = [MIN, MAX, AVG]

HANDLE_KEY_ATTR = 'id'

GETDBSCHEMA_API = "getdbschema/"
RUNQUERY_API    = "runquery/"
CLEANUP_API     = "cleanupquery/"
MAKE_PHI = "makephi/"

OUT_FMT_PATH = "_caQuery"

TRANSLATOR_BASE_QUERY = {
    "1": {
        "button_id": 8,
        "parameters": [],
        "outputs": [],
        "query_path_id": [None],
        "w_in": ["start"],
        "w_out": ["2.0"],
        "button_cat": "op",
        "output_type_id": None,
        "offsetX": 164.5,
        "offsetY": 127.75,
        "src_table_name": None,
        "src_pk_name": None
    },
    "2": {
        "button_id": 6,
        "parameters": [],
        "outputs": [],
        "query_path_id": [],
        "w_in": ["1"],
        "w_out": ["end"],
        "button_cat": "op",
        "output_type_id": None,
        "offsetX": 424.5,
        "offsetY": 191.75,
        "template_id": None
    },
    "start": {
        "parameters": None,
        "query_path_id": [None],
        "w_out": ["1.0"],
        "offsetX": -343.5,
        "offsetY": -173.25
    },
    "end": {
        "parameters": None,
        "query_path_id": [None],
        "w_in": ["2"],
        "offsetX": -343.5,
        "offsetY": -173.25,
        "translators": []
    }
} 