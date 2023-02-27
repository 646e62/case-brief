# case-brief

Generates a FIRAC-style case brief from a reported decision


## What is a case brief?


In countries like Canada that use the common law system, reported court cases are an important legal source. This is because common-law courts use *precedent* as an authoritative source. The underlying idea is that judicial decisions should be consistent with one another, such that similarly-situated litigants are treated similarly under the law. Because reported cases are records of how a court treated a particular litigant, they are a valuable source of insight for this purpose. Reported decisions are also records of how courts apply legal principles, and very often follow a hierarchy that allows "higher" courts to overturn decisions made by "lower" courts.

Case briefs are short high-level case summaries that distill the precedential value from a reported decision. This precedential value can include the factual, legal, and analytical components of other cases.


## What is FIRAC?

FIRAC is an initialism that stands for **F**acts, **I**ssues, **R**ules, **A**nalysis/Application, and **C**onclusion. It is one of several common ways to break reported decisions into conceptual components, and in my experience, the most effective. I summarize these different conceptual components below. For a more detailed explanation of these components, see [FIRAC: An ELEMENTary Approach § 1.1 - An overview of the FIRAC approach](http://www.daveguenther.com/firac/firacintro.html).

### Facts

To the end that parties in similar circumstances be treated similarly, the facts underlying reported decisions are a very useful way to compare and contrast litigants to identify similarities and difference sbetween them.


### Issues

At the heart of every reported decision is a legal issue, absent which there would be no legal case to write about. So-called "issue spotting" is the primary skill tested on most law school exams, and a key part of real life legal analysis. Legal arguments are built around issues and any legal case analysis must be able to identify issues in order to be useful.

Fortunately, most reported decisions make issue spotting a relatively straightforward enterprise, as issues are often clearly identified as such. Where they aren't clearly identified, they must be inferred by applying legal rules to the factual matrix.

### Rules

Where facts help identify similarly-situated litigants, the rules inform courts how such litigants should be treated. Where facts and issues are case-specific, legal rules are theoretically universal. Identifying a case's legal rule or rules is one of a case brief's primary goals.

### Analysis/application

The analysis portion of a case applies rules to facts in order to address the issues the parties raised. Broken down in this way, the analysis describes the underlying logic used to apply each element together, demonstrates how rules apply to facts, and provides the rationale for resolving legal issues. Where cases with similar facts and similar issues end with different results, the difference is often in the analysis.


### Conclusion

The conclusion briefly identifies the successful party and any judicial findings made or remedies awarded. It summarizes a case's outcome.


## Why is this useful?

In practice, lawyers are very frequently required to read and be familiar with a lot of written information. Case briefs are useful in this respect, as they provide almost all of a case's precedential value to a reader without having to wade through dozens of pages of dense text, procedural history, and explication. This provides the reader with the requisite familiarity more efficiently. To the extent that case briefs cut down on the amount of actual reading a lawyer has to do, they save time and money, and may reduce human error.

In law school, briefing cases is an essential activity that occupies an inordinate amount of time. A program capable of reliably separating the FIRAC elements from one another would assist with both generating these briefs faster and helping the user understand these components when they next see them in a case. As with many things, sometimes seeing the answer can help a student "reverse engineer" the correct method. Properly sorted FIRAC elements and appropriately summarized case briefs may assist with this.

## How does this program create case briefs?

This project operates on the hypothesis that these five elements can reliably be found and identified in most reported decisions using NLP techniques. It adopts David Guenther's premise, outlined in [FIRAC: An ELEMENTary Approach § 2.1 - An introduction to understanding judicial opinions](http://www.daveguenther.com/firac/judicialopinionsintro.html), that different linguistic components in reported cases (sentences, paragraphs, key words, etc) can be thought of as FIRAC elements, and proposes to apply this approach programmatically.

To do this, I first run a written decision through a text classification model I've trained to identify the five FIRAC elements (as well as document headings and procedural history, the latter of which is a somewhat special subset of the analysis). The model is under development but already showing promise. Once a decision's sentences have been thus classified, they get sorted into the FIRAC categories. Local summarization functions extract key information which then gets fed to GPT-3 for further summary and analysis. The end result is the case brief.
