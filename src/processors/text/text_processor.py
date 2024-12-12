from config.config_loader import load_ocr_corrections


class TextProcessor:
    def __init__(self):
        # self.text = text
        pass

    def correct_misspelled_word(word):
        ocr_corrections = load_ocr_corrections()
        for key, val in ocr_corrections.items():
            for item in val:
                word = word.replace(item, key)
        return word
