import spacy
from spacy.matcher import Matcher

class KGExtractor:
    def __init__(self, model="en_core_web_sm"):
        try:
            self.nlp = spacy.load(model)
        except OSError:
            print(f"Downloading {model}...")
            from spacy.cli import download
            download(model)
            self.nlp = spacy.load(model)

    def extract_entities(self, text):
        """
        Extract named entities from text.
        """
        doc = self.nlp(text)
        entities = []
        for ent in doc.ents:
            entities.append({
                "text": ent.text,
                "label": ent.label_,
                "start": ent.start_char,
                "end": ent.end_char
            })
        return entities

    def extract_relations(self, text):
        """
        Extract relations (triples) using dependency parsing.
        Heuristic: Subject -> Verb -> Object
        """
        doc = self.nlp(text)
        triples = []

        for sent in doc.sents:
            # Simple Subject-Verb-Object extraction
            for token in sent:
                if token.dep_ in ("nsubj", "nsubjpass"):  # Subject
                    subj = token
                    verb = token.head
                    
                    # Find object
                    obj = None
                    for child in verb.children:
                        if child.dep_ in ("dobj", "attr", "prep", "pobj"):
                            obj = child
                            break
                    
                    if obj:
                        # Expand subject and object to full phrases
                        subj_text = self._get_compound(subj)
                        obj_text = self._get_compound(obj)
                        relation = verb.lemma_
                        
                        triples.append({
                            "head": subj_text,
                            "type": relation,
                            "tail": obj_text
                        })
        return triples

    def _get_compound(self, token):
        """
        Helper to get the full compound phrase for a token.
        """
        phrase = [token]
        for child in token.children:
            if child.dep_ == "compound":
                phrase.append(child)
        phrase.sort(key=lambda x: x.i)
        return " ".join([t.text for t in phrase])

    def extract_kg(self, text):
        """
        Extract both entities and relations.
        """
        entities = self.extract_entities(text)
        relations = self.extract_relations(text)
        return {
            "entities": entities,
            "relations": relations
        }
