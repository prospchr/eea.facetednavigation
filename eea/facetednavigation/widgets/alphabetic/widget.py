""" Alphabet widget
"""
from Products.Archetypes.public import Schema
from Products.Archetypes.public import BooleanField
from Products.Archetypes.public import StringWidget
from Products.Archetypes.public import SelectionWidget
from Products.Archetypes.public import BooleanWidget
from eea.facetednavigation.widgets.field import StringField

from zope.app.pagetemplate.viewpagetemplatefile import ViewPageTemplateFile
from alphabets import unicode_character_map
from eea.facetednavigation.widgets.widget import CountableWidget

EditSchema = Schema((
    StringField('index',
        schemata="default",
        required=True,
        vocabulary_factory='eea.faceted.vocabularies.AlphabeticCatalogIndexes',
        widget=SelectionWidget(
            format='select',
            label='Catalog index',
            label_msgid='faceted_criteria_index',
            description='Catalog index to use for search',
            description_msgid='help_faceted_criteria_index',
            i18n_domain="eea.facetednavigation"
        )
    ),
    BooleanField('count',
        schemata="countable",
        widget=BooleanWidget(
            label='Count results',
            label_msgid='faceted_criteria_count',
            description='Display number of results per letter',
            description_msgid='help_faceted_criteria_alphabetic_count',
            i18n_domain="eea.facetednavigation"
        )
    ),
    BooleanField('hidezerocount',
        schemata="countable",
        widget=BooleanWidget(
            label='Hide items with zero results',
            label_msgid='faceted_criteria_emptycounthide',
            description='This option works only if "count results" is enabled',
            description_msgid='help_faceted_criteria_criteria_emptycounthide',
            i18n_domain="eea.facetednavigation"
        )
    ),
    StringField('default',
        schemata="default",
        widget=StringWidget(
            size=3,
            maxlength=1,
            label='Default value',
            label_msgid='faceted_criteria_default',
            description='Default letter to be selected',
            description_msgid='help_faceted_criteria_default',
            i18n_domain="eea.facetednavigation"
        )
    ),
))

class Widget(CountableWidget):
    """ Widget
    """
    # Widget properties
    widget_type = 'alphabetic'
    widget_label = 'Alphabetic'
    view_js = '++resource++eea.facetednavigation.widgets.alphabets.view.js'
    edit_js = '++resource++eea.facetednavigation.widgets.alphabets.edit.js'
    view_css = '++resource++eea.facetednavigation.widgets.alphabets.view.css'
    edit_css = '++resource++eea.facetednavigation.widgets.alphabets.edit.css'

    index = ViewPageTemplateFile('widget.pt')
    edit_schema = CountableWidget.edit_schema + EditSchema

    def after_query(self, brains, form):
        """ Filter brains
        """
        wid = self.data.getId()
        index = self.data.get('index', '')

        if self.hidden:
            letter = self.default
        else:
            letter = form.get(wid, '')

        if isinstance(letter, str):
            letter = letter.decode('utf-8', 'replace')

        for brain in brains:
            if not (index and letter):
                yield brain
                continue

            if letter.lower() in [u'all', 'all']:
                yield brain
                continue

            xval = getattr(brain, index, None)
            if xval is None:
                continue

            if type(xval) not in (str, unicode):
                continue

            if isinstance(xval, str):
                xval = xval.decode('utf-8', 'replace')

            if not xval.lower().startswith(letter.lower()):
                continue
            yield brain

    # Widget custom API
    def getAlphabet(self, lang):
        """ Get language alphabet
        """
        #TODO: also to implement 0-9 and Other on the alphabet listing
        return unicode_character_map[lang]

    def count(self, brains):
        """ Intersect results
        """
        res = {}
        lang = self.request.get('LANGUAGE', 'en')
        sequence = [item[0] for item in self.getAlphabet(lang)]
        if not sequence:
            return res

        index_id = self.data.get('index')
        if not index_id:
            return res

        for brain in brains:
            xval = getattr(brain, index_id, None)
            if not xval:
                continue
            if type(xval) not in (str, unicode):
                continue
            if isinstance(xval, str):
                xval = xval.decode('utf-8', 'replace')
            letter = xval[0].upper()
            count = res.get(letter, 0)
            res[letter] = count + 1
        res['all'] = len(brains)
        return res
