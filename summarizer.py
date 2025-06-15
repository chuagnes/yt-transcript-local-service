import os
import openai

client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

def summarize_to_bullets(text, max_chunk_chars=1000, mode="bullet", custom_prompt=None):
    print("🧠 Running OpenAI GPT-4o summarization...")

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

    summaries = []
    for idx, chunk in enumerate(chunks):
        print(f"🔹 Summarizing chunk {idx + 1}/{len(chunks)}")

        if custom_prompt:
            user_prompt = f"{custom_prompt.strip()}\n\nText:\n{chunk}"
        else:
            if mode == "bullet":
                user_prompt = f"Summarize the following in bullet points:\n\n{chunk}"
            elif mode == "paragraph":
                user_prompt = f"Summarize the following in a single paragraph:\n\n{chunk}"
            elif mode == "tl;dr":
                user_prompt = f"Give a short TL;DR summary of the following:\n\n{chunk}"
            elif mode == "technical":
                user_prompt = f"Summarize the following text using technical language:\n\n{chunk}"
            else:
                user_prompt = f"Summarize this:\n\n{chunk}"

        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful and concise summarization assistant."},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=5000,
                temperature=0.3
            )
            summary = response.choices[0].message.content.strip()
            summaries.append(summary)

        except Exception as e:
            print(f"❌ Error summarizing chunk {idx + 1}: {e}")
            summaries.append("[Summary failed for this section]")

    return "\n\n".join(summaries)