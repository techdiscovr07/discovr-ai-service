"""
Prompt templates for AI analysis
"""

CAMPAIGN_ANALYSIS_PROMPT = """Analyze this campaign brief and provide suggestions for improvement:

Campaign Name: {campaign_name}
Description: {description}
Target Audience: {target_audience}
Goals: {goals}
Brand: {brand_name}

Please evaluate:
1. Campaign title clarity and appeal
2. Description effectiveness
3. Target audience alignment
4. Goal clarity and measurability
5. Call-to-action strength

Provide:
- An improved title
- An improved description
- 3-5 CTA suggestions
- Specific suggestions for improvement
- Strengths and weaknesses
- Overall quality score (0-1)
"""

SCRIPT_REVIEW_PROMPT = """Review this video script against the campaign brief:

CAMPAIGN BRIEF:
Name: {campaign_name}
Description: {campaign_description}
Video Title: {video_title}
Primary Focus: {primary_focus}
Do's: {dos}
Don'ts: {donts}
CTA: {cta}

BRAND GUIDELINES:
{brand_guidelines}

SCRIPT TO REVIEW:
{script_content}

Evaluate the script on:
1. Brand Fit (0-1): Does it align with brand values and campaign goals?
2. Compliance (0-1): Does it follow the do's and don'ts?
3. Quality (0-1): Is it well-written, engaging, clear?
4. Engagement (0-1): Will it capture and hold audience attention?

Provide:
- Scores for each category
- Overall score
- Specific feedback
- Actionable suggestions (improvements, additions, removals)
- Issues found (if any) with severity
- Strengths to highlight
"""

VIDEO_REVIEW_PROMPT = """Review this video content against the campaign brief:

CAMPAIGN BRIEF:
Name: {campaign_name}
Description: {campaign_description}
Video Title: {video_title}
Primary Focus: {primary_focus}
Do's: {dos}
Don'ts: {donts}

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
3. Brand Alignment (0-1): Does it match campaign goals and brand?
4. Compliance (0-1): Follows do's and don'ts?
5. Engagement (0-1): Will it engage the target audience?

Provide:
- Scores for each category
- Overall score
- Timeline analysis with timestamps (issues, strengths, suggestions)
- Key moments to highlight
- Transcript accuracy check
- Specific feedback and recommendations
"""
