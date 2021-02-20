import spacy
from spacy.matcher import PhraseMatcher
from spacy.tokens import Span
import re
import pt_core_news_lg

nlp = pt_core_news_lg.load()

# https://spacy.io/usage/processing-pipelines#custom-components
class SynonymMatcher(object):
    name = "synonym_matcher"

    def __init__(self, nlp, terms, label):
        patterns = [nlp.make_doc(text) for text in terms]
        self.matcher = PhraseMatcher(nlp.vocab)
        self.matcher.add(label, None, *patterns)

    def __call__(self, doc):
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = Span(doc, start, end, label=match_id)
            doc.ents = list(doc.ents) + [span]
        return doc

def check_regex_pattern(regex_pattern):
    try:
        re.compile(regex_pattern)
        return True
    except re.error:
        return False

def entity_check(entity):
    entity_name = entity.get("entity")
    if entity_name == None:
        return 'Entity must have a name at field "entity"!', 400
    if type(entity_name) != str:
        return 'Entity name must be a string!', 400
    values = entity.get("values")
    if not values:
        return 'There is no values for entity. You need do give at last one value.', 400
    if type(values) != list:
        return 'The "values" field must be a array of objects.', 400
    for index in range(len(values)):
        object = values[index]
        if type(object) != dict:
            return 'The %dº item for the field "values" is not a object.'%(index+1), 400
        type_ = object.get("type")
        if type_ == None:
            return 'The %dº item has no "type" defined. Please, define type as "synonyms" or "patterns".'%(index+1), 400
        if type(type_) != str:
            return 'The data type for the "type" field of the %dº value must be a string!'%(index+1), 400
        if type_ not in  ["synonyms", "patterns"]:
            return 'There is no type "%s". Please, for the %dº item of field "values", define type as "synonyms" or "patterns".'%(type_, index+1), 400
        value = object.get("value")
        if not value:
            return 'The %dº item of field "values" has no value defined for the field "value".'%(index+1), 400
        if type(value) != str:
            return 'The data type for the "value" field of the %dº item in "values" field must be a string!'%(index+1), 400
        if type_ == "synonyms":
            synonyms = object.get("synonyms")
            if synonyms == None:
                return 'The %dº item for the field "values" has no "synonyms" field. If the value %s has no synonyms, set the synonyms field as a empty array.'%(index+1, value), 400
            if type(synonyms) != list:
                return 'The "synonyms" field of the %dº item for the field "values" must be a array of strings.'%(index+1), 400
        if type_ == "patterns":
            patterns = object.get("patterns")
            if patterns == None:
                return 'The %dº item for the field "values" has no "patterns" field.'%(index+1, value), 400
            if type(patterns) != list:
                return 'The "patterns" field of the %dº item for the field "values" must be a array of valid regex strings.'%(index+1), 400
            for regex in patterns:
                valid = check_regex_pattern(regex_pattern=regex)
                if not valid:
                    return 'The regex pattern %s is not valid.'%regex, 400
        return "All right", 200
