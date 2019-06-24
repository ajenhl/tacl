from collections import OrderedDict
import csv
import itertools
import re

from tacl import constants, exceptions


class VariantMapping:

    """Class defining a mechanism for normalising and denormalising text.

    The two processes make use of a supplied mapping between each
    variant and its normalised form.

    Because the normalised forms in the mapping may only consist of a
    single token, the normalisation and denormalisation processes are
    not able to handle context. Eg, it is not possible to reflect
    "ABA" -> "ACA", where the surrounding "A"s are themselves able to
    be normalised.

    """

    def __init__(self, mapping_path, tokenizer):
        self._mapping_path = mapping_path
        self._tokenizer = tokenizer
        self._variant_to_normal_map = None
        self._normal_to_variant_map = None
        self._pua_char_code = 57344  # First character in Private Use Area
        self._pua_to_token_map = {}
        self._token_to_pua_map = {}

    def denormalise(self, text):
        """Returns `text` in all possible denormalised forms.

        This can be a very slow operation, and should only be
        performed on short strings.

        :param text: text to denormalise
        :type text: `str`
        :rtype: `list` of `str`

        """
        if self._normal_to_variant_map is None:
            self._generate_mappings()
        mapping = self._normal_to_variant_map.copy()
        joiner = self._tokenizer.joiner
        joiner_length = len(joiner)
        texts = set([self._preprocess_text(text, joiner)])
        for normal_form, variants in mapping.items():
            if normal_form in text:
                texts = self._denormalise(texts, normal_form, variants, joiner)
        denormalised_texts = []
        for text in texts:
            for substitute, variant in self._pua_to_token_map.items():
                text = text.replace(substitute, variant)
            denormalised_texts.append(self._postprocess_text(
                text, joiner_length))
        return denormalised_texts

    def _denormalise(self, texts, normal_form, variants, joiner):
        """Returns all possible variants of the `texts` as formed from
        substituting `variants` for the `normal_form` in all combinations.

        :param texts: texts to denormalise
        :type texts: `set` of `str`
        :param normal_form: normalised form that is to be substituted
        :type normal_form: `str`
        :param variants: variant forms that are substituted for `normal_form`
        :type variants: `list` of `str`
        :param joiner: tokenizer's joining string
        :type joiner: `str`
        :rypte: `set` of `str`

        """
        denormalised_texts = []
        normal_form = '{}{}{}'.format(joiner, normal_form, joiner)
        variants = [normal_form] + ['{}{}{}'.format(joiner, variant, joiner)
                                    for variant in variants]
        for text in texts:
            parts = re.split(r'({})'.format(normal_form), text)
            for idx, part in enumerate(parts):
                if part == normal_form:
                    parts[idx] = variants
                else:
                    parts[idx] = [part]
            denormalised_texts.extend((''.join(part) for part
                                       in itertools.product(*parts)))
        return set(denormalised_texts)

    def _generate_mappings(self):
        """Generates the dictionary mappings used to normalise and denormalise
        text.

        The mappings (from variant to normalised form, and from
        normalised form to possible variants) make use of Private Use
        Area characters to ensure that a form is not used in multiple
        transformation in a single normalisation or denormalisation
        process. Eg, given "AB" -> "CD" and "C" -> "E", the string
        "AB" should become "CD" and not "ED".

        """
        normal_to_variant_map = {}
        variant_to_normal_map = {}
        ordered_map = OrderedDict()
        seen_forms = []
        with open(self._mapping_path, newline='') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                normalised_form = self._get_normalised_form(row, seen_forms)
                variant_forms = self._get_variant_forms(row, normalised_form)
                substitute_forms = self._get_variant_substitute_forms(
                    normalised_form, variant_forms, seen_forms,
                    variant_to_normal_map)
                normal_to_variant_map[normalised_form] = substitute_forms
        sorted_keys = sorted(variant_to_normal_map.keys(),
                             key=lambda x: len(x), reverse=True)
        for variant_form in sorted_keys:
            ordered_map[variant_form] = variant_to_normal_map[variant_form]
        self._normal_to_variant_map = normal_to_variant_map
        self._variant_to_normal_map = ordered_map

    def _get_normalised_form(self, row, seen_forms):
        """Returns the normalised form from `row`.

        Checks that the normalised form is valid (hasn't already been
        specified in the mapping, consists of a single token).

        :param row: mapping row
        :type row: `list` of `str`
        :param seen_forms: forms already specified in the mapping
        :type seen_forms: `list` of `str`
        :rtype: `str`

        """
        tokenized_form = self._tokenizer.tokenize(row[0])
        normalised_form = self._tokenizer.joiner.join(tokenized_form)
        if normalised_form in seen_forms:
            raise exceptions.MalformedNormaliserMappingError(
                normalised_form,
                constants.DUPLICATE_VARIANT_MAPPING_FORM_ERROR)
        normalised_form_token_count = len(tokenized_form)
        if normalised_form_token_count == 0:
            raise exceptions.MalformedNormaliserMappingError(
                ','.join(row), constants.EMPTY_NORMALISED_FORM_ERROR)
        elif normalised_form_token_count > 1:
            raise exceptions.MalformedNormaliserMappingError(
                normalised_form,
                constants.TOO_LONG_NORMALISED_FORM_ERROR)
        seen_forms.append(normalised_form)
        return normalised_form

    def _get_substitute(self, token):
        """Returns the character used as a substitute for `token`.

        These substitutions ensure that a token does not participate
        in multiple transformations within a normalisation or
        denormalisation process.

        The substitute characters are taken from the Unicode Private
        Use Area.

        :param token: token to be given a substitute character
        :type token: `str`
        :rtype: `str`

        """
        char = chr(self._pua_char_code)
        substitute = self._token_to_pua_map.setdefault(token, char)
        if substitute == char:
            self._pua_char_code += 1
            self._pua_to_token_map[char] = token
        return substitute

    def _get_variant_forms(self, row, normalised_form):
        """Returns the variants forms specified in `row`.

        :param row: mapping row
        :type row: `list` of `str`
        :param normalised_form: normalised form specified in this row
        :type normalised_form: `str`
        :rtype: `list` of `str`

        """
        variant_forms = row[1:]
        if not variant_forms:
            raise exceptions.MalformedNormaliserMappingError(
                normalised_form, constants.NO_VARIANTS_DEFINED_ERROR)
        return variant_forms

    def _get_variant_substitute_forms(self, normalised_form, variant_forms,
                                      seen_forms, variant_to_normal_map):
        """Returns a list of substitute forms for `variant_forms`.

        Checks that each variant form is valid (not previously
        specified in the mapping, consisting of one or more tokens).

        :param normalised_form: normalised form for the variants
        :type normalised_form: `str`
        :param variant_forms: variant forms to generate substitutes for
        :type variant_forms: `list` of `str`
        :param seen_forms: forms already specified in the mapping
        :type seen_forms: `list` of `str`
        :param variant_to_normal_map: mapping between variant form and
                                      normalised form
        :type variant_to_normal_map: `dict`
        :rtype: `list` of `str`

        """
        substitute_forms = []
        for variant_form in variant_forms:
            tokenized_form = self._tokenizer.tokenize(variant_form)
            variant_form = self._tokenizer.joiner.join(tokenized_form)
            if variant_form in seen_forms:
                raise exceptions.MalformedNormaliserMappingError(
                    variant_form,
                    constants.DUPLICATE_VARIANT_MAPPING_FORM_ERROR)
            if not tokenized_form:
                raise exceptions.MalformedNormaliserMappingError(
                    normalised_form,
                    constants.EMPTY_VARIANT_FORM_ERROR)
            seen_forms.append(variant_form)
            substitute = self._get_substitute(normalised_form)
            variant_to_normal_map[variant_form] = substitute
            substitute_forms.append(self._get_substitute(variant_form))
        return substitute_forms

    def normalise(self, text):
        """Returns the normalised form of `text`.

        It is assumed that `text` is in the form of tokens separated
        by a token separator, matching the form of the items in the
        mapping supplied to this object.

        :param text: text to normalise
        :type text: `str`
        :rtype: `str`

        """
        if self._variant_to_normal_map is None:
            self._generate_mappings()
        joiner = self._tokenizer.joiner
        text = self._preprocess_text(text, joiner)
        for variant, substitute in self._variant_to_normal_map.items():
            text = text.replace('{}{}{}'.format(joiner, variant, joiner),
                                '{}{}{}'.format(joiner, substitute, joiner))
        for substitute, normal_form in self._pua_to_token_map.items():
            text = text.replace(substitute, normal_form)
        joiner_length = len(joiner)
        return self._postprocess_text(text, joiner_length)

    def _postprocess_text(self, text, joiner_length):
        if joiner_length > 0:
            text = text[joiner_length:][:-joiner_length]
        return text

    def _preprocess_text(self, text, joiner):
        return '{}{}{}'.format(joiner, text, joiner)
