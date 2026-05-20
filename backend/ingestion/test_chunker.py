from ingestion.chunker import chunk_text


sample_text = """
Bananas are rich in potassium and fiber.
They help digestion and heart health.
They also provide antioxidants and energy.
""" * 20


chunks = chunk_text(sample_text)


print(f"\nTotal Chunks: {len(chunks)}\n")


for index, chunk in enumerate(chunks):

    print(f"\n--- Chunk {index + 1} ---\n")

    print(chunk)