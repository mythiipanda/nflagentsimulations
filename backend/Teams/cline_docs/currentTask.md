## Current Objective
Adapt the agent framework to use the Cerebras API

## Context
We are switching from the Gemini API to the Cerebras API for our language model needs. This requires significant changes to the `Agent` class and related components.

## Next Steps
1. Install `cerebras_cloud_sdk` - **Done**
2. Modify `Agent` class to use `Cerebras` client - **Done**
3. Adapt `generate_thought` for Cerebras API calls - **Done**
4. Adjust prompt construction for Cerebras API - **Done**
5. Remove Gemini API key management - **Done**
6. Update or remove `extract_` functions - **Done**
7. Update test suite for Cerebras API - **Done**
8. Remove `rate_limiter.py` and references - **Done**
9. Test the adapted agent framework - **Pending**