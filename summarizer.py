from transformers import pipeline

# Load once globally
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

def summarize_to_bullets(text, max_chunk_chars=1000):
    print("🧠 Running local summarization model...")

    # Step 1: Chunk input if too long
    chunks = []
    current_chunk = ""
    for sentence in text.split(". "):
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_chars:
            current_chunk += sentence + ". "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + ". "
    if current_chunk:
        chunks.append(current_chunk.strip())

    bullet_points = []
    for idx, chunk in enumerate(chunks):
        print(f"🔹 Summarizing chunk {idx + 1}/{len(chunks)}")
        try:
            result = summarizer(chunk, max_length=120, min_length=30, do_sample=False)
            summary = result[0]['summary_text']

            # Step 2: Post-process to bullet points
            for sentence in summary.split(". "):
                sentence = sentence.strip().strip(".")
                if sentence:
                    bullet_points.append(f"• {sentence}.")
        except Exception as e:
            print(f"❌ Summarization failed for chunk {idx + 1}: {e}")
            bullet_points.append("• [Summary failed for this section]")

    return "\n".join(bullet_points)