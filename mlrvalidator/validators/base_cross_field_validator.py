
class BaseCrossFieldValidator:
    '''
    Extends validate to add an argument for the existing_document. Typically for an add this will be empty.
    '''

    def __init__(self):
        self._errors = {}

    def validate(self, document, existing_document):
        self.document = document
        if None == existing_document:
            existing_document = {}
        self.existing_document = existing_document
        self.merged_document = existing_document.copy()
        self.merged_document.update(document)

        self._errors = {}

        return True

    @property
    def errors(self):
        return self._errors

    def _any_fields_in_document(self, keys):
        '''

        :param list of str keys:
        :return: boolean
        '''
        document_keys = self.document.keys()
        return any(key in self.document for key in keys)




