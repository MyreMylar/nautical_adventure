import pygame
import html.parser


class CharStyle:
    def __init__(self, char_style=None):
        if char_style is not None:
            self.bold = char_style.bold
            self.italic = char_style.italic
            self.underline = char_style.underline
        else:
            self.bold = False
            self.italic = False
            self.underline = False


class HTMLTextBlock:
    """
    Class to handle a line of HTML text.
    Supports subset of HTML tags e.g. <b>,<i>,<u>
    """

    class ContextData:

        default_style = {
            'font_name': 'default_font',
            'font_size': 12
        }

        def __init__(self):
            super().__init__()

            self.len_text = 0
            self.element_stack = []
            self.style_stack = []
            self.current_style = {}
            self.next_style = {}
            self.context = TextLineContext()
            self.text_data = ""

            self.char_style = CharStyle()
            self.default_font_name = "default_font"
            self.default_font_size = 12
            self.default_font_color = pygame.color.Color("#FFFFFFFF")
            self.font_name = self.default_font_name
            self.font_size = self.default_font_size
            self.font_color = self.default_font_color

            self.push_style('default_style', self.default_style)

        def push_style(self, key, styles):
            old_styles = {}
            for name in styles.keys():
                old_styles[name] = self.current_style.get(name)
            self.style_stack.append((key, old_styles))
            self.current_style.update(styles)
            self.next_style.update(styles)

        def pop_style(self, key):
            # Don't do anything if key is not in stack
            for match, _ in self.style_stack:
                if key == match:
                    break
            else:
                return

            # Remove all innermost elements until key is closed.
            while True:
                match, old_styles = self.style_stack.pop()
                self.next_style.update(old_styles)
                self.current_style.update(old_styles)
                if match == key:
                    break

        def add_text(self, text):
            self.text_data = self.text_data[:self.len_text] + text + self.text_data[self.len_text:]
            self.len_text += len(text)
            for i in range(0, len(text)):
                self.append_current_style_to_context()

        def append_current_style_to_context(self):
            if 'bold' in self.current_style.keys():
                self.char_style.bold = self.current_style['bold']
                if self.char_style.bold is None:
                    self.char_style.bold = False
            else:
                self.char_style.bold = False
            if 'italic' in self.current_style.keys():
                self.char_style.italic = self.current_style['italic']
                if self.char_style.italic is None:
                    self.char_style.italic = False
            else:
                self.char_style.italic = False
            if 'underline' in self.current_style.keys():
                self.char_style.underline = self.current_style['underline']
                if self.char_style.underline is None:
                    self.char_style.underline = False
            else:
                self.char_style.underline = False
            if 'font_name' in self.current_style.keys():
                self.font_name = self.current_style['font_name']
                if self.font_name is None:
                    self.font_name = self.default_font_name
            else:
                self.font_name = self.default_font_name
            if 'font_size' in self.current_style.keys():
                self.font_size = self.current_style['font_size']
                if self.font_size is None:
                    self.font_size = self.default_font_size
            else:
                self.font_size = self.default_font_size
            if 'font_color' in self.current_style.keys():
                self.font_color = self.current_style['font_color']
                if self.font_color is None:
                    self.font_color = self.default_font_color
            else:
                self.font_color = self.default_font_color
            self.context.append_context(self.font_size,
                                        self.font_name,
                                        CharStyle(self.char_style),
                                        self.font_color)

    class TextHTMLParser(ContextData, html.parser.HTMLParser):

        font_sizes = {
            1: 8,
            1.5: 9,
            2: 10,
            2.5: 11,
            3: 12,
            3.5: 13,
            4: 14,
            4.5: 16,
            5: 18,
            5.5: 20,
            6: 24,
            6.5: 32,
            7: 48
        }

        def __init__(self):
            super().__init__()

        def handle_starttag(self, tag, case_attrs):
            element = tag.lower()

            self.element_stack.append(element)

            attrs = {}
            for key, value in case_attrs:
                attrs[key.lower()] = value

            style = {}
            if element in ('b', 'strong'):
                style['bold'] = True
            elif element in ('i', 'em', 'var'):
                style['italic'] = True
            elif element == 'u':
                style['underline'] = True
            elif element == 'font':
                if 'face' in attrs:
                    font_name = attrs['face']  # .split(',')
                    style["font_name"] = font_name
                if 'size' in attrs:
                    font_size = self.font_sizes[float(attrs['size'])]
                    style["font_size"] = font_size
                if 'color' in attrs:
                    style["font_color"] = pygame.color.Color(attrs['color'])
            if element == 'br':
                self.add_text('\n')  # u'\u2028'

            self.push_style(element, style)

        def handle_endtag(self, tag):
            element = tag.lower()

            if element not in self.element_stack:
                return

            self.pop_style(element)

            while self.element_stack.pop() != element:
                pass

        def handle_data(self, data):
            self.add_text(data)

        def error(self, message):
            pass

    def __init__(self, html_text, rect_or_pos, font_dict, wrap_to_height=False):
        self.html_text = html_text
        self.formatted_text_block = None  # TextLine()
        # if we pass in a rect, text will be wrapped to the rect width (and warn if longer than the height?)
        self.rect_or_pos = rect_or_pos
        self.font_dict = font_dict
        self.wrap_to_height = wrap_to_height
        self.parse_to_context()

    def parse_to_context(self):
        parser = HTMLTextBlock.TextHTMLParser()
        parser.feed(self.html_text)

        self.formatted_text_block = TextBlock(parser.text_data,
                                              self.rect_or_pos,
                                              parser.context,
                                              self.font_dict,
                                              self.wrap_to_height)

    def draw(self, surface):
        self.formatted_text_block.draw(surface)


class FontDictionary:

    def __init__(self):
        self.default_font_size = 12
        self.loaded_fonts = {"default_font_regular_12": pygame.font.Font(None, self.default_font_size)}
        self.known_font_paths = {"default_font": [None, None, None, None]}

    def find_font(self, font_size, font_name, bold=False, italic=False):
        if bold and italic:
            font_style_string = "bold_italic"
        elif bold and not italic:
            font_style_string = "bold"
        elif not bold and italic:
            font_style_string = "italic"
        else:
            font_style_string = "regular"
        font_id = font_name + "_" + font_style_string + "_" + str(font_size)
        if font_id in self.loaded_fonts:  # font already loaded
            return self.loaded_fonts[font_id]
        elif font_name in self.known_font_paths:  # we know paths to this font, just haven't loaded current size/style
            if bold and italic:
                new_font = pygame.font.Font(self.known_font_paths[font_name][3], font_size)
                new_font.set_bold(True)
                new_font.set_italic(True)
                self.loaded_fonts[font_id] = new_font
            elif bold and not italic:
                new_font = pygame.font.Font(self.known_font_paths[font_name][1], font_size)
                new_font.set_bold(True)
                self.loaded_fonts[font_id] = new_font
            elif not bold and italic:
                new_font = pygame.font.Font(self.known_font_paths[font_name][2], font_size)
                new_font.set_italic(True)
                self.loaded_fonts[font_id] = new_font
            else:
                self.loaded_fonts[font_id] = pygame.font.Font(self.known_font_paths[font_name][0], font_size)

            return self.loaded_fonts[font_id]
        else:
            return self.loaded_fonts["default_font_regular_12"]

    def add_font_path(self, font_name, font_path, bold_path=None, italic_path=None, bold_italic_path=None):
        if font_name not in self.known_font_paths:
            if bold_path is None:
                bold_path = font_path
            if italic_path is None:
                italic_path = font_path
            if bold_italic_path is None:
                bold_italic_path = font_path
            self.known_font_paths[font_name] = [font_path, bold_path, italic_path, bold_italic_path]


class StyledChar:

    def __init__(self, font_size, font_name, char, style, color, position, font_dictionary):
        self.style = style
        self.char = char
        self.font_size = font_size
        self.font_name = font_name

        self.font = font_dictionary.find_font(font_size, font_name, self.style.bold, self.style.italic)

        if self.style.underline:
            self.font.set_underline(True)

        self.color = color
        self.position = position

        self.rendered_char = self.font.render(self.char, True, self.color)
        metrics = self.font.metrics(self.char)
        self.ascent = self.font.get_ascent()
        self.width = self.font.size(self.char)[0]
        self.height = self.font.size(self.char)[1]
        if len(metrics[0]) == 5:
            self.advance = metrics[0][4]
        else:
            self.advance = 0
        self.rect = pygame.Rect(self.position, (self.width, self.height))

        self.unset_underline_style()

    def unset_underline_style(self):
        self.font.set_underline(False)


class TextLineContext:
    """
    A class that covers all the states of the text 'options' so we know what
    to apply when rendering a letter.
    """
    def __init__(self):
        self.font_sizes = []
        self.font_names = []
        self.styles = []
        self.colors = []

    def append_context(self, font_size, font_name, style, color):
        self.font_sizes.append(font_size)
        self.font_names.append(font_name)
        self.styles.append(style)
        self.colors.append(color)

    def insert_context(self, index, font_size, font_name, style, color):
        self.font_sizes = self.font_sizes[:index] + [font_size] + self.font_sizes[index:]
        self.font_names = self.font_names[:index] + [font_name] + self.font_names[index:]
        self.styles = self.styles[:index] + [style] + self.styles[index:]
        self.colors = self.colors[:index] + [color] + self.colors[index:]

    def default_fill(self, length, font_size, font_name, style, color):
        for i in range(0, length):
            self.append_context(font_size, font_name, style, color)

    def set_by_index(self, i, font_size, font_name, style, color):
        self.font_sizes[i] = font_size
        self.font_names[i] = font_name
        self.styles[i] = style
        self.colors[i] = color


class TextBlock:

    class TextLine:
        def __init__(self):
            self.characters = []
            self.max_line_char_height = 0
            self.max_line_ascent = 0

    def __init__(self, text, rect_or_pos, context, font_dict, wrap_to_height=False):
        self.characters = text
        if len(rect_or_pos) == 2:
            self.position = rect_or_pos
            self.width = -1
            self.height = -1
        else:
            self.position = (rect_or_pos[0], rect_or_pos[1])
            self.width = rect_or_pos[2]
            if wrap_to_height:
                self.height = rect_or_pos[3]
            else:
                self.height = -1
        self.context = context
        self.line_sprite = None
        self.font_dict = font_dict

        self.lines = []

        self.update()

    def update(self):

        if self.width != -1:
            # wrap text to width by words
            words = self.characters.split(' ')
            i = 0
            current_line_length = 0
            prev_word_len = 0
            prev_word = None
            prev_word_advance = 0
            for word in words:
                word_advance = 0
                if current_line_length > self.width:
                    if prev_word is not None and prev_word[-1] == '\n':
                        current_line_length = 0
                    else:
                        current_line_length = prev_word_advance
                    line_break_i = i-(prev_word_len+1)
                    self.characters = self.characters[:line_break_i] + '\n' + self.characters[line_break_i:]
                    self.context.insert_context(line_break_i,
                                                self.context.font_sizes[line_break_i],
                                                self.context.font_names[line_break_i],
                                                self.context.styles[line_break_i],
                                                self.context.colors[line_break_i])
                    i += 1
                for char in word:
                    if char == '\n':
                        if current_line_length < self.width:
                            current_line_length = 0
                    else:
                        font = self.font_dict.find_font(self.context.font_sizes[i],
                                                        self.context.font_names[i],
                                                        self.context.styles[i].bold,
                                                        self.context.styles[i].italic)
                        metrics = font.metrics(char)

                        advance = metrics[0][4]
                        current_line_length += advance
                        word_advance += advance

                    i += 1
                if i < len(self.characters):
                    font = self.font_dict.find_font(self.context.font_sizes[i],
                                                    self.context.font_names[i],
                                                    self.context.styles[i].bold,
                                                    self.context.styles[i].italic)
                    metrics = font.metrics(' ')
                    advance = metrics[0][4]
                    current_line_length += advance
                    word_advance += advance
                    i += 1  # for the space

                prev_word_len = len(word)
                prev_word_advance = word_advance
                prev_word = word
            if current_line_length > self.width:
                line_break_i = i - (prev_word_len + 1)
                self.characters = self.characters[:line_break_i] + '\n' + self.characters[line_break_i:]
                self.context.insert_context(line_break_i,
                                            self.context.font_sizes[line_break_i],
                                            self.context.font_names[line_break_i],
                                            self.context.styles[line_break_i],
                                            self.context.colors[line_break_i])

        position = [0.0, 0.0]

        styled_chars = []
        max_line_length = 0
        max_line_char_height = 0
        max_line_ascent = 0
        line_height_acc = 0
        line_chars = []
        num_lines = 1
        i = 0
        prev_text_line = None
        while i < len(self.characters):
            if self.characters[i] == '\n':
                if max_line_char_height == 0:
                    if prev_text_line is not None:
                        max_line_char_height = prev_text_line.max_line_char_height
                    else:
                        font = self.font_dict.find_font(self.context.font_sizes[i],
                                                        self.context.font_names[i],
                                                        self.context.styles[i].bold,
                                                        self.context.styles[i].italic)
                        max_line_char_height = font.size('A')[1]
                position[1] += max_line_char_height
                line_height_acc += max_line_char_height
                line_length = position[0]
                if line_length > max_line_length:
                    max_line_length = line_length

                # line_text = self.characters[:i]
                rest_of_text = self.characters[i+1:]
                while rest_of_text.startswith(" "):
                    i += 1
                    rest_of_text = self.characters[i + 1:]
                text_line = TextBlock.TextLine()
                text_line.characters = line_chars
                line_chars = []
                text_line.max_line_char_height = max_line_char_height
                text_line.max_line_ascent = max_line_ascent
                self.lines.append(text_line)
                max_line_char_height = 0
                max_line_ascent = 0
                position[0] = 0.0
                prev_text_line = text_line
                num_lines += 1
            else:
                new_char = StyledChar(self.context.font_sizes[i],
                                      self.context.font_names[i],
                                      self.characters[i],
                                      self.context.styles[i],
                                      self.context.colors[i],
                                      position,
                                      self.font_dict)
                position[0] += new_char.advance
                if new_char.height > max_line_char_height:
                    max_line_char_height = new_char.height
                if new_char.ascent > max_line_ascent:
                    max_line_ascent = new_char.ascent
                styled_chars.append(new_char)
                line_chars.append(new_char)
            i += 1

        position[1] += max_line_char_height
        line_height_acc += max_line_char_height
        line_length = position[0]
        if line_length > max_line_length:
            max_line_length = line_length
        text_line = TextBlock.TextLine()
        text_line.characters = line_chars
        # line_chars = []
        text_line.max_line_ascent = max_line_ascent
        self.lines.append(text_line)

        if self.width == -1:
            surface_width = max_line_length
        else:
            surface_width = self.width
        if self.height == -1:
            surface_height = line_height_acc
        else:
            surface_height = self.height
        surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA, 32)

        for line in self.lines:
            for char in line.characters:
                # need to adjust y start pos based on ascents
                char_rect = char.rect
                adjust = line.max_line_ascent - char.ascent
                char_rect.y += adjust
                surface.blit(char.rendered_char, char_rect)

        self.line_sprite = surface

    def draw(self, surface):
        surface.blit(self.line_sprite, self.position)

    def set_context(self, context):
        self.context = context
        self.update()
