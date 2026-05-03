from query_engine import hf_login, build_collection

hf_login()
collection = build_collection()
# print("Vectorstore built and saved.")