# from src.services.embedding import embed_text

# sample_text = "This is a test chunk of text to verify Firebase embedding storage."
# chunk_id = "test_doc_chunk_0"
# metadata = {
#     "doc_id": "test_doc",
#     "chunk_index": 0,
#     "source_type": "test",
#     "uploaded_by": "Dev",
#     "position": "tester",
#     "timestamp": "2025-04-19T15:00:00"
# }

# embed_text(sample_text, chunk_id, metadata)

# from src.utils.utils import list_all_doc_ids_firebase

# print("📄 All doc_ids:", list_all_doc_ids_firebase())

from src.utils.utils import delete_document_firebase

delete_document_firebase("test_doc") 
