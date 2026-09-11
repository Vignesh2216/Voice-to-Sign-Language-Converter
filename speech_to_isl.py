import os
import re
import nltk
from nltk.stem import WordNetLemmatizer
from nltk.tree import Tree, ParentedTree
from conf import JAR_DIR

try:
    from nltk.parse.stanford import StanfordParser
except Exception:
    StanfordParser = None

os.environ['STANFORD_PARSER'] = JAR_DIR
os.environ['STANFORD_MODELS'] = JAR_DIR
# Stanford parsing is optional. Use JAVA_HOME only when the environment provides it.
if os.environ.get('JAVA_HOME'):
    os.environ['JAVAHOME'] = os.environ['JAVA_HOME']

try:
    nltk.download('wordnet', quiet=True)
except Exception:
    pass

STOP_WORDS = {'a', 'an', 'am', 'are', 'be', 'been', 'being', 'for', 'from', 'is', 'it', 'my', 'of', 'the', 'to', 'was', 'were'}
SYNONYM_MAP = {
    'glad': 'happy',
    'happy': 'happy',
    'joyful': 'happy',
    'cheerful': 'happy',
    'hello': 'hello',
    'hi': 'hello',
    'hey': 'hello',
    'greet': 'hello',
    'greeting': 'hello',
    'name': 'name',
    'named': 'name',
    'call': 'name',
    'called': 'name',
    'google': 'google',
    'go': 'go',
    'going': 'go',
    'went': 'go',
    'come': 'come',
    'coming': 'come',
    'came': 'come',
}


def filter_stop_words(words):
    return [word for word in words if word not in STOP_WORDS]


def lemmatize_tokens(token_list):
    lemmatizer = WordNetLemmatizer()
    lemmatized_words = []
    for token in token_list:
        token = lemmatizer.lemmatize(token)
        lemmatized_words.append(lemmatizer.lemmatize(token, pos='v'))
    return lemmatized_words


def label_parse_subtrees(parent_tree):
    tree_traversal_flag = {}
    for sub_tree in parent_tree.subtrees():
        tree_traversal_flag[sub_tree.treeposition()] = 0
    return tree_traversal_flag


def handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    if tree_traversal_flag[sub_tree.treeposition()] == 0 and tree_traversal_flag[sub_tree.parent().treeposition()] == 0:
        tree_traversal_flag[sub_tree.treeposition()] = 1
        modified_parse_tree.insert(i, sub_tree)
        i = i + 1
    return i, modified_parse_tree


def handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree):
    for child_sub_tree in sub_tree.subtrees():
        if child_sub_tree.label() == 'NP' or child_sub_tree.label() == 'PRP':
            if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                tree_traversal_flag[child_sub_tree.treeposition()] = 1
                modified_parse_tree.insert(i, child_sub_tree)
                i = i + 1
    return i, modified_parse_tree


def modify_tree_structure(parent_tree):
    tree_traversal_flag = label_parse_subtrees(parent_tree)
    modified_parse_tree = Tree('ROOT', [])
    i = 0
    for sub_tree in parent_tree.subtrees():
        if sub_tree.label() == 'NP':
            i, modified_parse_tree = handle_noun_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)
        if sub_tree.label() == 'VP' or sub_tree.label() == 'PRP':
            i, modified_parse_tree = handle_verb_prop_clause(i, tree_traversal_flag, modified_parse_tree, sub_tree)

    for sub_tree in parent_tree.subtrees():
        for child_sub_tree in sub_tree.subtrees():
            if len(child_sub_tree.leaves()) == 1:
                if tree_traversal_flag[child_sub_tree.treeposition()] == 0 and tree_traversal_flag[child_sub_tree.parent().treeposition()] == 0:
                    tree_traversal_flag[child_sub_tree.treeposition()] = 1
                    modified_parse_tree.insert(i, child_sub_tree)
                    i = i + 1

    return modified_parse_tree


def convert_eng_to_isl(input_string):
    if not input_string or len(input_string.split()) <= 1:
        return [token for token in re.split(r'\s+', input_string.strip()) if token]

    if StanfordParser is None:
        return re.split(r'\s+', input_string.strip())

    try:
        parser = StanfordParser()
        possible_parse_tree_list = [tree for tree in parser.parse(input_string.split())]
        parse_tree = possible_parse_tree_list[0]
        parent_tree = ParentedTree.convert(parse_tree)
        modified_parse_tree = modify_tree_structure(parent_tree)
        return modified_parse_tree.leaves()
    except Exception:
        return re.split(r'\s+', input_string.strip())


def normalize_gloss_tokens(tokens):
    normalized = []
    for token in tokens:
        token = re.sub(r'[^a-z]', '', token.lower())
        if not token:
            continue
        token = SYNONYM_MAP.get(token, token)
        token = token.strip()
        if not token or token in STOP_WORDS:
            continue
        normalized.append(token)
    return normalized


def pre_process(sentence):
    words = list(sentence.split())
    final_string = ''
    for word in words:
        cleaned = re.sub(r'[^a-z]', '', word.lower())
        if not cleaned:
            continue
        if cleaned not in SYNONYM_MAP:
            final_string += ' ' + cleaned
        else:
            final_string += ' ' + SYNONYM_MAP[cleaned]
    return final_string.strip()


def isl(text):
    input_string = (text or '').strip()
    if not input_string:
        return ''

    parsed_tokens = convert_eng_to_isl(input_string)
    lemmatized_tokens = lemmatize_tokens(parsed_tokens)
    filtered_tokens = filter_stop_words(lemmatized_tokens)
    gloss_tokens = normalize_gloss_tokens(filtered_tokens)

    if not gloss_tokens:
        gloss_tokens = normalize_gloss_tokens([token for token in re.split(r'\s+', input_string.lower()) if token])

    isl_text_string = ' '.join(gloss_tokens).lower()
    print('ISL:{' + isl_text_string + '}')
    return isl_text_string

