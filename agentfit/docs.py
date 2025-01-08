from functools import cached_property
from pathlib import Path

from agentfit.llm import LLMClient

summary_client = LLMClient(
    system="""
I will give you a document from ReadTheDocs.

Shorten the document making the language as concise as possible whilst retaining the original meaning. 
Retain any code snippets in full.

Do not explain the answer. Give only the shortened document.

For example:
```
PyAutoFit recognises the parameters of a class by the constructor arguments of the class which are the arguments passed
into the class's __init__ method. For example, the following class has three parameters, centre, normalization and sigma.

.. code-block:: python

    class Gaussian:

        def __init__(
            self,
            centre=0.0,        # <- PyAutoFit recognises these
            normalization=0.1, # <- constructor arguments are
            sigma=0.01,        # <- the Gaussian's parameters.
        ):
            self.centre = centre
            self.normalization = normalization
            self.sigma = sigma
```

Should be shortened to retain the full code block:

```
PyAutoFit recognises the parameters of a class by its constructor arguments. Below the arguments are centre, 
normalization and sigma.

.. code-block:: python
    
        class Gaussian:
    
            def __init__(
                self,
                centre=0.0,
                normalization=0.1,
                sigma=0.01,
            ):
                self.centre = centre
                self.normalization = normalization
                self.sigma = sigma
    ```
"""
)


class File:
    def __init__(
        self,
        name: str,
        path: Path,
    ):
        """
        A file in the documentation

        Parameters
        ----------
        name
            The name of the file
        path
            The path to the file
        """
        self.name = name
        self.path = path

    def text(self):
        return self.path.read_text()

    def summary(self):
        return summary_client(self.path.read_text())


class Docs:
    def __init__(self, path: Path):
        self.path = path

    @cached_property
    def rst_files(self):
        return [
            File(
                str(path.relative_to(self.path)),
                path,
            )
            for path in self.path.rglob("*.rst")
        ]

    def string(self):
        return "\n\n".join([f"{file.name}\n\n{file.text()}" for file in self.rst_files])

    def summary(self):
        return "\n\n".join(
            [f"{file.name}\n\n{file.summary()}" for file in self.rst_files]
        )

    def __getitem__(self, item):
        path = self.path / item
        if path.is_file():
            return File(
                item,
                path,
            )
        return Docs(self.path / item)
