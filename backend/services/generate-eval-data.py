import os
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.testset.generator import TestsetGenerator
from ragas.testset.evolutions import simple, reasoning, multi_context


class GenerateEvalData:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.loader = PyPDFLoader("../../Life Insurance Handbook (English).pdf")
        self.documents = self.loader.load()
        self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        self.docs = self.text_splitter.split_documents(self.documents)
        self.generator_llm = ChatOpenAI(model="gpt-4o")
        self.critic_llm = ChatOpenAI(model="gpt-4o")
        self.embeddings = OpenAIEmbeddings()
        self.generator = TestsetGenerator.from_langchain(
            self.generator_llm,
            self.critic_llm,
            self.embeddings
        )

    def generate_eval_data(self):

        testset = self.generator.generate_with_langchain_docs(
            self.docs,
            test_size=200,
            distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25}
        )

        df = testset.to_pandas()
        df.to_json("ragas_dataset_200.json", index=False)
        print("Dataset generated and saved to ragas_dataset_200.json")

if __name__ == "__main__":
    generate_eval_data = GenerateEvalData()
    generate_eval_data.generate_eval_data()
# # 2. Load the KB PDF
# loader = PyPDFLoader("../../Life Insurance Handbook (English).pdf")
# documents = loader.load()

# # 3. Split the document into chunks
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# docs = text_splitter.split_documents(documents)

# # 4. Initialize LLMs for generation and criticism
# generator_llm = ChatOpenAI(model="gpt-4o")
# critic_llm = ChatOpenAI(model="gpt-4o")
# embeddings = OpenAIEmbeddings()

# # 5. Initialize Testset Generator
# generator = TestsetGenerator.from_langchain(
#     generator_llm,
#     critic_llm,
#     embeddings
# )

# # 6. Generate 200 QA Pairs
# # Distribute question types to ensure robustness
# testset = generator.generate_with_langchain_docs(
#     docs, 
#     test_size=200,
#     distributions={simple: 0.5, reasoning: 0.25, multi_context: 0.25}
# )

# # 7. Convert to DataFrame and Save
# df = testset.to_pandas()
# df.to_json("ragas_dataset_200.csv", index=False)
# print("Dataset generated and saved to ragas_dataset_200.csv")
