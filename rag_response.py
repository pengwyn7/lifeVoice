from rag_engine import retrieve_context
from utils.groq_client import query

def rag_response(user_query, persona, system_prompt, subpersona=None):
    """
    Combines user query with retrieved context and persona/system prompt,
    then sends to Groq for generation.
    """
    context_docs = retrieve_context(user_query, persona=persona, subpersona=subpersona)
    context_text = "\n\n".join(context_docs) if context_docs else "(no retrieved context)"

    rag_prompt = f"""Use the reference context below when it helps answer the user. Stay in character.

Persona: {persona}
User query: {user_query}

Reference context:
{context_text}

Reply in character to the user query."""

    return query(rag_prompt, system_prompt)
