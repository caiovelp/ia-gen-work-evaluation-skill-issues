You are provided with a GitHub issue in this format:
Title: """the title of the issue"""
Body: """the body of the issue"""

You have to assign it a label.
Possible labels are: bug, feature, neither, discard

The "bug" label (Fix Request) is used if the report...
1) reports a NullpointerException (NPE).
2) the discussion concludes that code had to be changed semantically to perform a corrective maintenance task.
3) fixes runtime or memory issues cause by defects (e.g endless loops).

The "feature" label (Feature Request) is used if the report...
1) requests to implement a new access/getter method.
2) requests to add new functionality.
3) requests to support new object types, specifications, or standards.

The "neither" label is used if the report is an Improvement Request, a Documentation Request, a Refactoring Request, or Other.
An Improvement Request is a report that...
1) discusses resource issues (time, memory) caused by non optimal algorithms or garbage collection strategies.
2) discusses semantics-preserving changes (typos, formatting) to code, log messages, exception messages, or property fields.
3) requests more or fewer log messages.
4) requests changing the content of log messages.
5) requests changing the type and/or the message of Exceptions to be thrown.
6) requests changes supporting new input or output formats (e.g. for backward compatibility or user satisfaction).
7) introduces concurrent versions of already existent functionalities.
8) suggests upgrading or patching third party libraries to overcome issues caused by third party libraries.
9) requests changes that correct/synchronize an already implemented feature according to specification/documentation.
A Documentation Request is a report whose...
1) discussion unveils that the report was filed due to missing, ambiguous, or outdated documentation.
A Refactoring Request is a report that...
1) requests to move code into other packages, classes, or methods.
2) requests to rename variables, methods, classes, packages, or configuration options.
Other is a report that...
1) reports violations of JAVA contracts without causing failures (e.g. "equals() but no hashCode()").
2) complains about compatibility fixes (e.g. "should compile with GCJ").
3) describes a task that does not require changing source or documentation (like packaging, configuration, download, etc.)

The "discard" label is used when you can't decide due to lack of information contained in the issue.

{examples}

Title: """{title}"""
Body: """{body}"""

Answer with a single JSON object and nothing else, in this format:
{"reasoning": "<the reasoning behind the label>", "label": "<one of: bug, feature, neither, discard>"}
