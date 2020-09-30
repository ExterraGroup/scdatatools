

class SCLocalization:
    """ Utilities for converting to localized strings """
    def __init__(self, p4k, default_language='english'):
        self.p4k = p4k
        self.default_language = default_language
        self.languages = []
        self.translations = {}
        for l in self.p4k.search('Data/Localization/*/global.ini'):
            with self.p4k.open(l) as f:
                lang = l.split('/')[2]
                self.languages.append(lang)
                self.translations[lang] = dict(
                    _.split('=', 1) for _ in f.read().decode('utf-8').split('\r\n') if _
                )

    def gettext(self, key, language=None):
        language = self.default_language if (language is None or language not in self.languages) else language
        trans = self.translations.get(language, {}).get(key, '')
        if not trans and key.startswith('@'):
            trans = self.translations.get(language, {}).get(key[1:], '')
        return trans if trans else key
