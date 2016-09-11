import argparse
import re
import textwrap


class ParagraphFormatter (argparse.ArgumentDefaultsHelpFormatter):

    """argparse formatter to maintain paragraph breaks in text, while
    wrapping those blocks.

    Code minimally adapted from the patch at
    http://bugs.python.org/file28091, authored by rurpy2.

    """

    def _split_lines(self, text, width):
        return self._para_reformat(text, width, multiline=True)

    def _fill_text(self, text, width, indent):
        lines = self._para_reformat(text, width, indent, True)
        return '\n'.join(lines)

    def _para_reformat(self, text, width, indent='', multiline=False):
        new_lines = list()
        main_indent = len(re.match(r'( *)', text).group(1))

        def blocker(text):
            """On each call yields 2-tuple consisting of a boolean and
            the next block of text from 'text'.  A block is either a
            single line, or a group of contiguous lines.  The former
            is returned when not in multiline mode, the text in the
            line was indented beyond the indentation of the first
            line, or it was a blank line (the latter two jointly
            referred to as "no-wrap" lines).  A block of concatenated
            text lines up to the next no-wrap line is returned when
            in multiline mode.  The boolean value indicates whether
            text wrapping should be done on the returned text."""
            block = list()
            for line in text.splitlines():
                line_indent = len(re.match(r'( *)', line).group(1))
                isindented = line_indent - main_indent > 0
                isblank = re.match(r'\s*$', line)
                if isblank or isindented:
                    # A no-wrap line.
                    if block:
                        # Yield previously accumulated block of text
                        # if any, for wrapping.
                        yield True, ''.join(block)
                        block = list()
                    # And now yield our no-wrap line.
                    yield False, line
                else:
                    # We have a regular text line.
                    if multiline:
                        # In multiline mode accumulate it.
                        block.append(line)
                    else:
                        # Not in multiline mode, yield it for
                        # wrapping.
                        yield True, line
            if block:
                # Yield any text block left over.
                yield (True, ''.join(block))

        for wrap, line in blocker(text):
            if wrap:
                # We have either a single line or a group of
                # concatented lines.  Either way, we treat them as a
                # block of text and wrap them (after reducing multiple
                # whitespace to just single space characters).
                line = self._whitespace_matcher.sub(' ', line).strip()
                # Textwrap will do all the hard work for us.
                new_lines.extend(textwrap.wrap(text=line, width=width,
                                               initial_indent=indent,
                                               subsequent_indent=indent))
            else:
                # The line was a no-wrap one so leave the formatting
                # alone.
                new_lines.append(line[main_indent:])
        return new_lines
