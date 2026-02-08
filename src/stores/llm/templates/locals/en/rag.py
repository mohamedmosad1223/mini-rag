from string import Template
### RAG Promot
system_prompt=Template("\n".join([
   
    "You are an assistant tasked with generating an answer to the user's query.",
    "You will be provided with a set of documents associated with the user's query.",
    "You must generate the answer based only on the provided documents and ignore all other information.",
    "If the user's question asks about a specific attribute explicitly mentioned in the documents (such as a name), extract and answer it directly.",
    "If the provided documents do not explicitly contain the requested information, do not guess or infer.",
    "In such cases, politely apologize and state that the available documents do not contain the requested information.",
    "The answer must be short, clear, and direct."
]))

document_prompt=Template(
    "\n".join([
    "## Document No $doc_num",
    "### Content: $chunk_text",
])
)

footer_prompt=Template(
    "\n".join(
        [
            "Based only on the above document , please generate an answer.",
            "## Question:",
            "$query",
            "",
            "## Answer:",
        ]
    )
)