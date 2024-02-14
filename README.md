# Manim Code Blocks Redux

`manim-code-blocks-redux` is a library for [Manim](https://github.com/ManimCommunity/manim) that allows animating blocks of code in Manim videos and scenes. 

## Example Usage

```python
from manim import *
from manim_code_blocks import *

class Main(Scene):

    def construct(self):

        java = CodeBlock(
            """
            public class Main {
                public static void main(String[] args) {
                    System.out.println("Hello world");
                }
            }
            """,
            language = Java
        )

        self.play(*java.create(run_time = 3))
```

Outputs:<br>

![](assets/java_demo.gif)

## Problems & Limitations

### Limited Language Support

Currently only the following languages are supported for syntax highlighting:

* C
* C#
* C++
* Java
* JavaScript
* Lua
* Go
* Python
* Rust
* TypeScript

To add language support, submit a pull request to to the [Tokenize-All](https://github.com/NicholasIapalucci/Tokenize-All) module.

### Unintelligent Highlighting

`Manim-Code-Block` uses *syntax* highlighting, not *semantic* highlighting. The source code is only tokenized, not parsed, and as such accurate highlighting can be impossible for certain circumstances. Syntax highlighting is provided by the [Tokenize-All](https://github.com/NicholasIapalucci/Tokenize-All) module, which lacks thorough language support. Additionally many languages have not been thoroughly tested enough for accurate highlighting. If you find an issue in your syntax highlighting, please report it to [the issues thread](https://github.com/NicholasIapalucci/manim-code-blocks/issues).

### Lack of Themes

Currently the only theme supported out of the box is the [One Dark Pro](https://github.com/Binaryify/OneDark-Pro) theme from Atom and used in Visual Studio Code. Adding a custom theme is possible (and simple), however currently this is the only theme supported out of the box.
