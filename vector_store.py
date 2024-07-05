# import json
# import os
# import uuid
# from pathlib import Path
#
# from dotenv import load_dotenv
# from langchain_openai import OpenAI
#
# from langchain_openai.embeddings import OpenAIEmbeddings
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.vectorstores import Cassandra
# from langchain.indexes.vectorstore import VectorStoreIndexWrapper
# from langchain.text_splitter import CharacterTextSplitter
# from langchain_community.document_loaders import JSONLoader
#
# from cassandra.cluster import Cluster, DCAwareRoundRobinPolicy
# from cassandra.auth import PlainTextAuthProvider
#
# load_dotenv()
#
#
# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# ASTRA_DB_CLIENT = os.getenv("ASTRA_CLIENT_ID")
# ASTRA_DB_SECRET = os.getenv("ASTRA_CLIENT_SECRET")
#
# cloud_config = {
#     'secure_connect_bundle': './Bilimai connection.zip'
# }
#
# auth_provider = PlainTextAuthProvider(ASTRA_DB_CLIENT, ASTRA_DB_SECRET)
# cluster = Cluster(cloud=cloud_config, auth_provider=auth_provider)
# cluster.load_balancing_policy = DCAwareRoundRobinPolicy(local_dc='US-EAST1')
# session = cluster.connect()
#
# session.execute("""
#     CREATE TABLE IF NOT EXISTS bilimai.books (
#         row_id TEXT PRIMARY KEY,
#         vector VECTOR<FLOAT, 1536>,
#         body_blob TEXT,
#         metadata_s MAP<TEXT, TEXT>,
#     )
# """)
#
# # session.execute("""
# #     CREATE CUSTOM INDEX IF NOT EXISTS idx_vector_vacancies ON bilimai.books (vector)
# #     USING 'org.apache.cassandra.index.sai.StorageAttachedIndex'
# #     WITH OPTIONS = {'similarity_function' : 'cosine'};
# # """)
#
#
# llm = OpenAI(openai_api_key=OPENAI_API_KEY)
# embedding = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
#
# cassandra_vectorstore = Cassandra(
#     embedding=embedding,
#     session=session,
#     keyspace='bilimai',
#     table_name='books'
# )
#
#
# vector_index = VectorStoreIndexWrapper(vectorstore=cassandra_vectorstore)
#
#
# def get_test(query: str):
#     try:
#         answer = vector_index.query(query,llm=llm).strip()
#         print(answer)
#     except Exception as e:
#         print(e)
#
# def save_in_db(filename: str = None):
#     loader = JSONLoader(file_path=filename, jq_schema='.',
#                         text_content=False)
#     collection = loader.load()
#     for data in collection:
#         data_vector = embedding.embed_query(f"{data}")
#         body_blob = str(data)
#         session.execute("""
#                             INSERT INTO bilimai.books (row_id, vector, body_blob)
#                             VALUES (%s, %s, %s)
#                         """, (
#             str(uuid.uuid4()),
#             list(data_vector),
#             body_blob))
#
#
# get_test("уровнение")


"""Generate a test with 20 question for 5-6 graders on the topic: {topic} на Русском"
                  f"[{'question': 'Найдите отношение 21:49.',
                    'correct_answer': '3:7'',
                    'incorrect_answers': ['7:3', '1:7', '7:1],
                    "difficulty": "A",
                     "topic": "Отношение двух чисел"}, ..etc}]"""