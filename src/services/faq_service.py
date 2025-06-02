from src.repositories.faq_repository import FaqRepository


class FaqService:
    """
    Service layer for handling FAQ-related business logic.
    Depends on FaqRepository for database access.
    """

    def __init__(self, faq_repo: FaqRepository):
        self._faq_repo = faq_repo

    # async def get_relevant_faqs(self, client_id: str, question_raw: str) -> list[Faq]:
    #     """
    #     Retrieves relevant FAQs for a given client and question.
    #     Orchestrates database lookups and potentially ranking.
    #     """
    #     print(
    #         f"--- FaqService: Processing question: {question_raw} for client: {client_id} ---")

    #     # 1. Clean the question text (replicate Node.js logic)
    #     # Remove non-alphanumeric characters (except space), multiple spaces, leading/trailing spaces
    #     import re
    #     question_cleaned = re.sub(
    #         r'[^\w\s]', ' ', question_raw).replace('  ', ' ').strip()
    #     print(f"--- FaqService: Cleaned question: {question_cleaned} ---")

    #     # 2. Lookup potential Object and Verb IDs in the database
    #     # These lookups also use full-text search in the DB based on the question
    #     object_matches = await self._faq_repo.select_object(client_id, question_cleaned)
    #     verb_matches = await self._faq_repo.select_verb(question_cleaned)

    #     object_ids = [obj.object_id for obj in object_matches]
    #     verb_ids = [verb.verb_id for verb in verb_matches]

    #     print(f"--- FaqService: Found Object IDs: {object_ids} ---")
    #     print(f"--- FaqService: Found Verb IDs: {verb_ids} ---")

    #     potential_faqs_db = await self._faq_repo.select_faq_object_verb(
    #         client_id,
    #         question_cleaned,  # Pass cleaned question for FTS in DB
    #         object_ids,
    #         verb_ids
    #     )

    #     print(
    #         f"--- FaqService: Found {len(potential_faqs_db)} potential FAQs from DB ---")

    #     # 4. Rank the fetched FAQs using Minisearch (replicate Node.js logic)
    #     # Minisearch needs a list of dictionaries. Convert SQLModel instances to dicts.
    #     faqs_data_for_minisearch = [faq.model_dump()
    #                                 for faq in potential_faqs_db]

    #     # Initialize Minisearch index if not already
    #     # For a multi-client bot, you might need a separate index per client
    #     # Or rebuild/reindex on every request (inefficient)
    #     # A better approach: pre-index all FAQs or index per client and cache the index.
    #     # For now, let's create/rebuild the index each time for simplicity in this service method (inefficient but works for development).
    #     # In production, manage the Minisearch index lifecycle (e.g., load from file, update on data changes, per client).

    #     # *** Inefficient but Simple Dev Setup for Minisearch: ***
    #     # This will create a new index on every relevant question query
    #     minisearch_index = MiniSearch(
    #         fields=['object_tag', 'verb_tag', 'additional_tag',
    #                 'question_text', 'stream', 'sub_stream'],
    #         store_fields=['faq_id', 'object_id', 'verb_id',
    #                       'question_text', 'answer_text', 'url', 'stream', 'sub_stream']
    #     )
    #     minisearch_index.add_all(faqs_data_for_minisearch)

    #     # Perform the search and ranking
    #     # Use the original raw question for ranking as Minisearch handles tokenization
    #     ranked_faqs_minisearch = minisearch_index.search(question_raw, {
    #         # Replicate boosting from Node.js
    #         'boost': {
    #             'object_tag': 1000,
    #             'verb_tag': 300,
    #             'additional_tag': 800,
    #             'question_text': 800,
    #             'stream': 100,
    #             'sub_stream': 100
    #         }
    #     })

    #     print(
    #         f"--- FaqService: Ranked {len(ranked_faqs_minisearch)} FAQs with Minisearch ---")
    #     # Optional: Add a score threshold or limit results here

    #     # 5. Fetch Contact Information for the top-ranked FAQs
    #     # The Node.js code fetched contact info in the FaqCard.
    #     # We need to get it here or pass enough info for the Langchain tool/LLM.
    #     # Let's fetch contact info for the top few results if stream/sub_stream are available.

    #     # For the Langchain tool, it's often better to give it the *data* it needs
    #     # to present to the user. So, the service can enrich the FAQ data with contact info.

    #     # Example: Fetch contact for the top 3 results
    #     faqs_with_contact = []
    #     for ranked_faq_match in ranked_faqs_minisearch:
    #         # The match object contains the stored fields
    #         # Get the original stored data
    #         faq_data = ranked_faq_match['document']

    #         # Fetch contact based on stream and sub_stream from the FAQ data
    #         stream = faq_data.get('stream')
    #         sub_stream = faq_data.get('sub_stream')

    #         contacts = []
    #         if stream:
    #             contacts = await self._faq_repo.select_contact(client_id, stream, sub_stream)

    #         # Add contact info to the FAQ data
    #         # If multiple contacts, mark it. If one, add details.
    #         if len(contacts) > 1:
    #             faq_data['multiple_contact'] = True
    #             # You might want to fetch ALL contacts for that stream/sub_stream
    #             # and include them in the data structure passed to the tool.
    #             # Or the tool can call a method to get all contacts for a stream/sub_stream if needed.
    #             # Let's add the list of contacts directly for simplicity in this data structure.
    #             faq_data['contacts'] = [c.model_dump()
    #                                     # Add contact details
    #                                     for c in contacts]
    #         elif len(contacts) == 1:
    #             faq_data['contact_name'] = contacts[0].contact_name
    #             faq_data['contact_email'] = contacts[0].contact_email
    #             faq_data['contact_phone'] = contacts[0].contact_phone
    #             faq_data['multiple_contact'] = False
    #             faq_data['contacts'] = [contacts[0].model_dump()]
    #         else:
    #             faq_data['multiple_contact'] = False
    #             faq_data['contacts'] = []  # No contacts found

    #         # Keep the score for ranking/selection later if needed
    #         faq_data['score'] = ranked_faq_match['score']

    #         faqs_with_contact.append(faq_data)

    #     # 6. Return the enriched, ranked list of FAQs
    #     # This list will be passed to the Langchain FAQ Tool

    #     # Note: Need to replicate the Node.js logic for selecting top results
    #     # (e.g., top 12 or until score drops significantly).
    #     # For now, return the first few as a placeholder.

    #     # Let's return the top 5 for initial testing
    #     return faqs_with_contact[:5]
