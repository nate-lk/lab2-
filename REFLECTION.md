# Reflection: Privacy & Limitations

## 1. Privacy & PII Risks
- **PII Leakage:** Storing user names, allergies, and locations in `profile.json` as plaintext poses a risk if the file system is compromised.
- **Sensitive Memory:** **Long-term Profile** is the most sensitive because it contains direct personal attributes (PII).
- **Retrieval Risk:** If Semantic Memory retrieves the wrong data (e.g., someone else's medical info in a shared database), it could lead to dangerous misinformation.

## 2. Mitigation Strategies
- **Deletion:** A `delete_user_data()` function should be implemented to wipe `profile.json` and `episodes.json` upon user request.
- **TTL (Time To Live):** Episodic memories should have an expiration date (e.g., 30 days) to comply with data minimization principles.
- **Consent:** The system should explicitly ask for permission before extracting and saving facts to the long-term profile.

## 3. Technical Limitations
- **Scaling:** Using JSON files (`profile.json`) will become slow and cause race conditions when multiple users access the system simultaneously. A real database like Redis or PostgreSQL is needed for production.
- **Keyword Search:** The current Semantic Memory uses keyword matching, which fails to understand synonyms or context (e.g., searching for "refund" won't find "money back"). A Vector Database (FAISS/Chroma) would be a better choice.
- **Extraction Accuracy:** The LLM might occasionally hallucinate or misinterpret facts when updating the profile, leading to "Conflicting Memories."

## 4. Most Helpful Memory Type
- **Long-term Profile** provides the most immediate "wow" factor for personalization, while **Episodic Memory** is crucial for long-running tasks and multi-session consistency.
