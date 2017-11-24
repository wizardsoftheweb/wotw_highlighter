"""This file provides a class to highlight code"""

# from pygments import highlight
# from pygments.lexers import get_lexer_for_filename, guess_lexer
# from pygments.formatters import HtmlFormatter
# from pygments.util import ClassNotFound

from wotw_highlighter.block_options import BlockOptions


class BlockHighlighter(BlockOptions):
    """
    This class provides a collection of methods to highlight blocks of code
    """

    def validate(self):
        if not self.blob:
            raise ValueError('No blob passed to highlighter')
