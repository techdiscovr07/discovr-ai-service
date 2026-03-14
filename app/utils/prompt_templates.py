"""
Prompt templates for AI analysis
"""

CAMPAIGN_STRATEGIST_PROMPT = """You are an elite Influencer Strategist. Convert this campaign objective into a creator plan and execution playbook!

CRITICAL RULES:
1. ONLY utilize the information provided in the Campaign Brief below.
2. If the Campaign Brief is completely empty or generic, DO NOT hallucinate a random product (e.g. sneakers, tech apps). Instead, respond critically that the brief is missing.
3. Your output MUST match the requested JSON schema perfectly.

CAMPAIGN BRIEF:
Name: {campaign_name}
Description: {description}
Target Audience: {target_audience}
Goals: {goals}
Brand: {brand_name}
Target Language: {target_language}
Target Platforms: {target_platforms}
Cultural Context/Nuance: {cultural_context}

Your objective is to generate JSON arrays containing the Strategy Brief, Creator Mix, Content Playbook, Timeline, and Measurement Plan logically stemming from the exact guidelines above.
"""

SCRIPT_REVIEW_PROMPT = """Review this video script against the campaign brief:

CRITICAL RULES:
1. STRICTLY evaluate ONLY the script provided against the specific brief provided.
2. DO NOT hallucinate, assume, or invent products. If the brief or script inputs are empty/generic, immediately flag it as a critical failure in your reasoning and feedback.
3. Conduct rigorous Brand Safety & Claims Checks: explicitly flag disallowed claims, competitor mentions, and missing mandatory disclaimers.

CAMPAIGN BRIEF:
Name: {campaign_name}
Description: {campaign_description}
Video Title: {video_title}
Primary Focus: {primary_focus}
Do's: {dos}
Don'ts: {donts}
CTA: {cta}
Target Language: {target_language}
Target Platforms: {target_platforms}
Cultural Context/Nuance: {cultural_context}

BRAND GUIDELINES & SAFETY:
{brand_guidelines}

SCRIPT TO REVIEW:
{script_content}

Evaluate the script and provide a numerical score (0 to 100) for each of the following:
1. Brand Fit & Safety: Does it align with brand values, avoid competitors, and follow safety claims?
2. Compliance: Does it follow the do's and don'ts?
3. Quality: Is it well-written, engaging, clear?
4. Engagement & Hook Pacing: Will it capture and hold audience attention?

Provide:
- A detailed "reasoning" paragraph analyzing your thoughts before generating output.
- Numerical scores (0-100) for brand fit, compliance, quality, and an overall score.
- Line-by-line feedback (hook, pacing, clarity, CTA strength)
- Platform-fit edits (YouTube vs Reels vs Shorts)
- Brand safety + claims checks (flags for risks)
- Suggested rewrites: “safe”, “bolder”, and “shorter” versions.
- Automated Checks list: provide a strict true/false for the following safety criteria: Brand safety checks, On-screen CTA visuals, Product description accuracy, Face on screen, People-first language, Authentic video environment, No negative phrasing, No mention of competitors.
  For EACH check, you MUST provide:
   * 'details': A 1-sentence summary of the result.
   * 'reasoning': A deep-dive analysis directly quoting the script to explain *why* the check passed or failed.
   * 'recommendation': Specific, actionable next steps for the creator (e.g., "Replace the word 'guaranteed' with 'potential'").

CRITICAL LINGUISTIC INSTRUCTION:
If the Target Language is "Hinglish", you MUST generate your feedback, scripts, and suggested rewrites in a natural mix of Romanized Hindi and English (e.g., "Yeh hook bohot fresh lag raha hai, target audience definitely connect karegi"). Do NOT use formal 'Shuddh Hindi'. Ensure all output text values match the target language and cultural context, but KEEP THE JSON SCHEMA KEYS STRICTLY IN ENGLISH.
"""

VIDEO_REVIEW_PROMPT = """Review this completed video content against the campaign brief:

CRITICAL RULES:
1. DO NOT hallucinate or assume context outside of the provided text.
2. If the brief or video transcript is empty/missing, immediately flag as an issue. Do not fall back to previous memory (e.g. sneakers).

CAMPAIGN BRIEF:
Name: {campaign_name}
Description: {campaign_description}
Video Title: {video_title}
Primary Focus: {primary_focus}
Do's: {dos}
Don'ts: {donts}
Target Language: {target_language}
Target Platforms: {target_platforms}
Cultural Context/Nuance: {cultural_context}

ORIGINAL SCRIPT:
{script_content}

VIDEO TRANSCRIPT:
{transcript}

VIDEO METADATA:
Duration: {video_duration} seconds
Resolution: {video_resolution}

Analyze the video for:
1. Visual Quality (0-1): Lighting, framing, production quality
2. Audio Quality (0-1): Clarity, background noise, music balance
3. Brand Alignment (0-1): Does it match campaign goals and brand tone?
4. Compliance & Disclosures (0-1): Follows do's/don'ts and required assets/disclosures?

Provide:
- "Ready to publish" score + risk flags
- Pass/fail checklist (brief adherence, key messages, brand tone, required assets, disclosure compliance)
- Timestamped issues (what’s wrong + where)
- Fix recommendations (exact edits)

CRITICAL LINGUISTIC INSTRUCTION:
If the Target Language is "Hinglish", you MUST generate your feedback, scripts, and playbooks in a natural mix of Romanized Hindi and English (e.g., "Yeh campaign bohot fresh lag raha hai, target audience definitely connect karegi"). Do NOT use formal 'Shuddh Hindi'. Ensure all output text values match the target language and cultural context, but KEEP THE JSON SCHEMA KEYS IN ENGLISH.
"""
