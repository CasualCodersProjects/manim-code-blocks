from manim import *
import tokenize_all

import json
import re as regex
from abc import ABC as abstract
from urllib.request import urlopen
from typing import Callable

class Theme:
    """A theme used to syntax highlight a `CodeBlock`."""
    
    colors: dict[str, list[str | Callable]]
    """
    The colors of this theme represented as a dictionary. The keys of the dictionary are hexidecimal colors (such as `"#FFFFFF"`), and the values are lists of token types that should be colored with that color (such as `["keyword", "operation"]`).
    """

    group_matchers: list[str]

    def __init__(self, colors: dict[str, list[str | Callable]], group_matchers: list[str]):
        """
        Creates a new `Theme` with the specified `colors`. See the `colors` field for specification.
        """
        self.colors = colors
        self.group_matchers = group_matchers

    def color_for(self, token: tokenize_all.Token) -> str:
        """Returns the color for the given token as specified by this theme, or `"#FFFFFF"` if none is specified."""
        for key, value in self.colors.items():
            if token.type in value:
                return key
        return "#FFFFFF"


OneDark = Theme(
    colors = {
        "#C678DD": ["keyword", "directive"], # Purple
        "#61AFEF": ["function"], # Blue
        "#E06C75": ["identifier"], # Red
        "#98C379": ["string"], # Green
        "#56B6C2": ["symbol"], # Cyan
        "#D19A66": ["number", "keyword literal"], # Orange
        "#E5C07B": ["class name"], # Yellow
        GRAY_C: ["comment"] # Gray
    },

    group_matchers = [
        "#D19A66", # Orange
        "#C678DD", # Purple
        "#56B6C2" # Cyan
    ]
)
"""The 'One Dark' theme from the `Atom` text editor."""


language_colors = json.loads(urlopen("https://raw.githubusercontent.com/ozh/github-colors/master/colors.json").read())
"""The `JSON` object representing colors for the various languages, fetched from https://raw.githubusercontent.com/ozh/github-colors/master/colors.json. """


class ProgrammingLanguage(abstract):
    """A programming language used to render `CodeBlocks`."""

    name: str
    """The name of the programming language. The name is displayed on the title card above the code block."""

    color: str
    """
    The color of the programming language. The color is used when displaying the name in the title card above the code block. by default, the official GitHub language colors are used for supported languages, see https://github.com/ozh/github-colors/blob/master/colors.json.
    """
    
    language: tokenize_all.TokenizableLanguage
    """
    The `TokenizableLanguage` of the language. 
    """

    def __init__(self, name: str, tokenize_name: str | None = None):
        self.name = name
        self.language = getattr(tokenize_all, tokenize_name if tokenize_name else name)
        self.color = language_colors[name]["color"]

        if self.color == None: print(f"Warning: no color found for {name}")
        if self.language == None: print(f"Warning: no tokenization found for {name}")


class CodeBlock(VGroup):
    """
    A block of code. By default code blocks are rendered as `MarkupText` objects with `BackgroundRectangles` behind them. Furthermore, a title with the name and color of the language is rendered above the code block on the left-hand side. Syntax highlighting is done using `TextMates` by extracting `.tmLanguage.json` files from `microsoft/vscode`. See https://github.com/microsoft/vscode/tree/main/extensions.
    """

    code: MarkupText
    """The primary `MarkupText` object that makes up the code block. Equivalent to indexing at `[1]`."""

    title: MarkupText
    """
    The title `MarkupText` object that makes up the langauge name title at the top of the code block. Equivalent to indexing at `[3]
    """

    code_background: BackgroundRectangle
    """The `BackgroundRectangle` for the code block markup object. Equivalent to indexing at `[0]`."""

    title_background: BackgroundRectangle
    """
    The `BackgroundRectangle` for the `title` object that lists the language name above the code block. Equivalent to indexing at `[2]`.
    """

    def __init__(
            self, 
            text: str, 
            language: ProgrammingLanguage | None = None, 
            theme: Theme = OneDark,
            font: str = "consolas",
            **kwargs: object
        ):
        """
        Creates a new `CodeBlock`.

        ### Parameters
        - `text [str]`:
            - The source code to render.
        - `language [ProgrammingLanguage]`:
            - The programming language to use when rendering the code. The language determines the text and color of the title of the code block, as well as the syntax highlighting of the code block.
        - `theme [Theme]`:
            - The theme to highlight the code in. `OneDark` by default.
        - `font [str]`: 
            - The font to render the code in. `Consolas` by default.
        - `**kwargs [Any]`:
            - Additional arguments passed to `VGroup`.
        """

        if language:
            lines = text.split("\n")
            group_count = 0
            finished: list[str] = []
            for line in lines:
                tokens = language.language.tokenize(line)
                for token in tokens:
                    if token.type.startswith('left'):
                        finished.append('<span foreground="' + theme.group_matchers[group_count % len(theme.group_matchers)] + '">' + token.value + '</span>')
                        group_count += 1
                    elif token.type.startswith('right'):
                        group_count -= 1
                        finished.append('<span foreground="' + theme.group_matchers[group_count % len(theme.group_matchers)] + '">' + token.value + '</span>')
                    elif token.type == "whitespace": 
                        finished.append(token.value)
                    else: 
                        safe_value = regex.sub("&", "&amp;", token.value)
                        safe_value = regex.sub("<", "&lt;", safe_value)
                        safe_value = regex.sub(">", "&gt;", safe_value)
                        finished.append('<span foreground="' + theme.color_for(token = token) + '">' + safe_value + '</span>')
                finished.append("\r")

            finished_text = "".join(finished)
        else:
            finished_text = '<span foreground="#FFFFFF">' + text + "</span>"

        markup = MarkupText(f'<span font="{font}">' + finished_text + '</span>', z_index = 3).scale(0.4)
        background_rect = BackgroundRectangle(
            markup, 
            color = "#282C34", 
            buff = 0.2, 
            fill_opacity = 1
        )

        if language:
            lang_name = MarkupText(
                f'<span font="{font}">{language.name}</span>',
                z_index = 3
            ).next_to(background_rect, UP).set_color(language.color)
            lang_name.scale(0.3, about_point=lang_name.get_corner(DOWN + LEFT))

            lang_background = BackgroundRectangle(lang_name, color="#282C34", buff=0.15, fill_opacity=1)
            pos = background_rect.get_corner(UP + LEFT) + np.array([lang_background.width/2, lang_background.height/2 - 0.005, 0])

            VGroup(lang_name, lang_background).move_to(pos)

            self.title = lang_name
            self.title_background = lang_background

            super().__init__(background_rect, markup, lang_background, lang_name, **kwargs)
        else: 
            self.title = None
            self.title_background = None
            super().__init__(background_rect, markup, **kwargs)

        self.code = markup
        self.code_background = background_rect

    def create(self, **kwargs) -> tuple[FadeIn, AddTextLetterByLetter, FadeIn, AddTextLetterByLetter]:
        """
        Return a tuple of animations for creating the code block. Use such as:\n
        ```
        python = CodeBlock('print("Hello World!")', language = Python)
        self.play(*python.create())
        ```
        By default the animation will `FadeIn` the `background` and `title_background`, and `AddTextLetterByLetter` the `code` and `title`. 
        """
        if getattr(self, 'title', None) and getattr(self, 'title_background', None): return (
            FadeIn(self.code_background, **kwargs), 
            AddTextLetterByLetter(self.code, **kwargs), 
            FadeIn(self.title_background, **kwargs), 
            AddTextLetterByLetter(self.title, **kwargs)
        )

        return (
            FadeIn(self.code_background, **kwargs), 
            AddTextLetterByLetter(self.code, **kwargs), 
        )

    def uncreate(self, **kwargs):
        """
        Return a tuple of animations for uncreating the code block. Use such as:
        ```
        python = CodeBlock('print("Hello World!")', language = Python)
        self.play(*python.uncreate())
        ```
        By default the animation will `FadeOut` the `background` and `title_background`, and `Uncreate` the `code` and `title`. 
        """
        if getattr(self, 'title', None) and getattr(self, 'title_background', None): return (
            FadeOut(self.code_background, **kwargs), 
            Uncreate(self.code, **kwargs), 
            FadeOut(self.title_background, **kwargs), 
            Uncreate(self.title, **kwargs)
        )

        return (
            FadeOut(self.code_background, **kwargs), 
            Uncreate(self.code, **kwargs), 
        )


C = ProgrammingLanguage("C")
"""The `C` programming language, used to render `C` code in `CodeBlocks`"""

Cpp = ProgrammingLanguage("C++", tokenize_name="Cpp")
"""The `C++` programming language, used to render `C++` code in `CodeBlocks`."""

CSharp = ProgrammingLanguage("C#", tokenize_name="CSharp")
"""The `C#` programming language, used to render `C#` code in `CodeBlocks`."""

Fortran = ProgrammingLanguage("Fortran")
"""The `Fortran` programming language, used to render Fortran code in `CodeBlocks`."""

Go = ProgrammingLanguage("Go")
"""The `Go` programming language, used to render `Go` code in `CodeBlocks`."""

Haskell = ProgrammingLanguage("Haskell")
"""The `Haskell` programming language, used to render `Haskell` code in `CodeBlocks`."""

Java = ProgrammingLanguage("Java")
"""The `Java` programming language, used to render `Java` code in `CodeBlocks`."""

JavaScript = ProgrammingLanguage("JavaScript")
"""The `JavaScript` programming language, used to render `JavaScript` code in `CodeBlocks`."""

Lua = ProgrammingLanguage("Lua")
"""The `Lua` programming language, used to render `Lua` code in `CodeBlocks`. """

Python = ProgrammingLanguage("Python")
"""The `Python` programming language, used to render `Python` code in `CodeBlocks`."""

Ruby = ProgrammingLanguage("Ruby")
"""The `Ruby` programming language, used to render `Ruby` code in `CodeBlocks`."""

Rust = ProgrammingLanguage("Rust")
"""The `Rust` programming language, used to render `Rust` code in `CodeBlocks`."""

SQL = ProgrammingLanguage("SQL")
"""The `SQL` programming language, used to render `SQL` code in `CodeBlocks`."""

TypeScript = ProgrammingLanguage("TypeScript")
"""The `TypeScript` programming language, used to render `TypeScript` code in `CodeBlocks`"""
