import translators as ts


# 翻译函数(python三方库)
def translate_by_python(text, source_lang, target_lang):
    result = ts.translate_text(text, from_language=source_lang, to_language=target_lang)
    return result
