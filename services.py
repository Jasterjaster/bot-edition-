import requests
import json
import time
import os
import uuid
from io import BytesIO
from PIL import Image

# --- الإعدادات ---
API_KEYS = [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")]
# ❗️❗️❗️ التوكن الخاص بـ Digen API - قم بتحديثه إذا انتهت صلاحيته ❗️❗️❗️
DIGEN_TOKEN = "4d6574614147492e47656e495863207c18fe61ba104a5e27bbb63c1656:1776520:1761356827"

GEMINI_API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}"
GENERATION_CONFIG = {"temperature": 1, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192}
SAFETY_SETTINGS = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
SESSION = requests.Session()

PROMPT_ENHANCER_INSTRUCTION = {
    "parts": [{"text":'''You are a professional prompt engineer for an AI image and video generator. Your task is to take a user's simple idea and expand it into a detailed, rich, and effective prompt in English. The prompt should include details about the subject, Subject: [Detailed description of the subject or main character with 15+ attributes, including appearance, clothing, age, emotional state]

Action: [Specific action the subject is performing, with details on gestures, timing, and micro-expressions]

Scene: [Detailed description of the environment, location, lighting setup, weather, time of day, and props]

Style: [Visual style, camera shot type, angle, movement, color palette, and depth of field]

Dialogue: [Spoken dialogue (if any), specifying tone and delivery. Use a colon (:) to prevent subtitles]
(Character Name): "Dialogue text here"
(Tone: emotional descriptor)

Sounds: [Precise specification of all sounds: ambient noise, sound effects (SFX), music, natural sounds, background hum]

Technical (Negative Prompt): [Elements to strictly avoid: subtitles, captions, watermarks, on-screen text, low quality, artifacts, unnatural motion, distorted hands'. Your output should ONLY be the final English prompt, with no additional text or explanation.example 
Convert the entire image to black and white, keeping all elements in black, white, and gray tones while preserving original details and textures. Add multiple splashes and streaks of thick, glossy orange paint over the subject’s body — on the shoulders, chest, arms, and parts of the face — as if the paint was poured and splattered, naturally dripping and flowing with realistic highlights, Roller coaster photo perspective, subject sitting alone in front row, first row has only the subject with empty seats on both sides showing visible safety harnesses and bars, both hands firmly gripping black safety bar, black safety shoulder harness clearly visible, expression excited or nervous. 2-3 rows of passengers behind with diverse races including Caucasian, Black, Latino and other Western ethnicities, each person is a unique individual (different genders, ages, skin tones, hair colors, clothing colors, hairstyles), everyone with both hands gripping safety bars or resting on lap, normal sitting position no waving, natural expressions. Blue and yellow/orange roller coaster seats, distant background features Disney castle, Ferris wheel, roller coaster tracks, background moderately blurred, natural daylight, authentic roller coaster photo style, high-definition quality,
Ignore the original background completely, extract only the main subject and place it in a brand new scene: subject sitting relaxed on simple wooden chair with casual posture, create flat 2D cartoon-style burning room around the subject, left side has window with flames bursting around it, right side has window also engulfed by fire, background center has huge orange-yellow-red flame wall rising from floor to ceiling, dense flames covering walls everywhere, floor edges have prominent fire, thick gray smoke clouds at ceiling top, all in flat color blocks with black outlines, brown wooden floor with fire reflections, simple round table with coffee cup beside subject, subject calm with slight smile, Japanese anime or American cartoon hand-drawn style, saturated bright colors, pure 2D illustration effect
Keep the subject’s identity and main appearance consistent, but switch the camera to a third-person player perspective, positioned directly in front of the character so that the entire front view of the full body is visible. The character walks or runs forward along a street, occupying about 40% of the lower central area of the frame. Completely remove the original background and replace it with a new scene depicting a 1990s West Coast American city street in a Los Santos style, featuring rows of palm trees, low old buildings, retro cars, street signs, and a straight road extending forward. The overall image should reproduce the authentic texture of a 2004 PS2 game screenshot: the character appears coarse and low-polygon, clearly showing a GTA-style game model rather than realistic human details. Use high color saturation, flat artificial lighting, and minimal shading to recreate the vintage PS2 aesthetic. Overlay GTA-style game interface elements: a circular radar mini-map in the bottom left corner, white police-star icons in the top right, the money display “$169802” below the stars, and a red horizontal health bar beneath the money display. The final result should look exactly like a 2004 PS2 Grand Theft Auto: San Andreas screenshot, with the character rendered in a rough, low-polygon, cartoonish PS2-era style
Four-panel comic. Panel 1: subject fist pump, bubble \"Starting diet today!\", motivated face. Panel 2: subject sweating, bubble \"10 minutes workout\", exhausted look. Panel 3: subject checking phone, bubble \"Burned 5 calories\", shocked face. Panel 4: subject eating fried chicken, bubble \"Reward myself 2000 cal\", satisfied smile. Keep look, black borders, silly style
Transform the main subject into a 3D collectible bobblehead figure with an oversized head (2:1 head-to-body ratio), keep the exact appearance from the original image including all facial/body features, hair/fur, skin/coat color, and overall look, do not change species or character type, compact Q-version body wearing soccer uniform (jersey, shorts, socks), visible jersey number, standing on green soccer field with a soccer ball nearby, blurred stadium background, photorealistic 3D rendered collectible figure texture with professional lighting
Remove original background. Close shot, 70% frame. RELAXED natural surfing pose: legs casually bent 150-160°, weight shifted slightly to one side for natural asymmetry, one arm extended more forward at 45° angle and other arm back at 30° angle (NOT horizontal T-pose), elbows soft and slightly bent, wrists loose, fingers naturally separated and curved, body with slight twist showing dynamic movement, shoulders relaxed not tense, overall posture organic and flowing not stiff. No ankle strap. IMPORTANT: Surfing on CLOUDS in sky NOT ocean, white fluffy clouds beneath surfboard, surfboard 1/3 in clouds with mist spray. Pink-orange dreamy sky background with cloud layers. Warm tones, soft natural lighting
Transform the original subject into card design, card center displays the complete subject from original image, card has \"Victory\" text written on it, no traditional suit symbols. The right hand holding this custom victory card towards camera, luxury casino poker table background, green felt, poker chips, formally dressed players, chandelier, depth of field
Keep the original subject’s upper body and pose intact, without distorting proportions. Naturally and seamlessly extend the missing lower body and legs to create a complete, realistic figure. The subject should sit naturally on a burning couch with correct perspective and proportional balance between body and furniture. Flames should be photorealistic and physically accurate, with natural orange and yellow lighting, proper rim light, and subtle heat distortion in the air. The sunset wheat field background should remain detailed and consistent with natural depth and texture. Ensure realistic shadows and reflections on the couch and ground. Maintain unified warm lighting and seamless integration with no cutout effect — professional photographic realism throughout
3D software viewport effect. Complete full body view, head to toe visible, subject at 50-55% of frame, standing on dark gray grid floor. 35-40 degree overhead angle. Complete UI: blue Y-axis left, RGB axis top-right, preview window bottom-left, top toolbar. Professional lighting, clear details, clear grid. Blender viewport style'''}]
}

PROMPT_ENHANCER_WITH_IMAGE_INSTRUCTION = {
    "parts": [{"text":'''you are a professional prompt engineer for an AI video generator. Your task is to analyze the provided image and the user's simple text idea. Based on both, create a detailed, rich, and effective prompt in English that describes a video scene. The prompt should animate the contents of the image according to the user's idea, follows this rules Subject: [Detailed description of the subject or main character with 15+ attributes, including appearance, clothing, age, emotional state]

Action: [Specific action the subject is performing, with details on gestures, timing, and micro-expressions]

Scene: [Detailed description of the environment, location, lighting setup, weather, time of day, and props]

Style: [Visual style, camera shot type, angle, movement, color palette, and depth of field]

Dialogue: [Spoken dialogue (if any), specifying tone and delivery. Use a colon (:) to prevent subtitles]
(Character Name): "Dialogue text here"
(Tone: emotional descriptor)

Sounds: [Precise specification of all sounds: ambient noise, sound effects (SFX), music, natural sounds, background hum]

Technical (Negative Prompt): [Elements to strictly avoid: subtitles, captions, watermarks, on-screen text, low quality, artifacts, unnatural motion, distorted hands]'. Your output should ONLY be the final English prompt, with no additional text or explanation. IMPORTANT RULE: keep your response short, don't make it long'''}]
}

IMAGE_DESCRIBER_INSTRUCTION = {
    "parts": [{"text": "You are an expert art analyst. Your task is to describe the provided image in comprehensive detail. Cover the main subject, background, setting, color palette, lighting, composition, mood, and potential artistic style. Your description should be clear, objective, and informative. Respond in Arabic."}]
}

BASEDLABS_HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    'Content-Type': "application/json",
    'origin': "https://www.basedlabs.ai",
    'referer': "https://www.basedlabs.ai/generate",
    # --- [ تم التحديث ] --- تم تحديث الكوكي لتصحيح خطأ رفع الصور للفيديو
    'Cookie': "_ga=GA1.1.1481592877.1761543536; _gcl_au=1.1.858473141.1761543536; wooTracker=hmuCqdt5aCnU; __stripe_mid=b2e8127c-4af7-48e7-afa1-5ece90f7ed4bd735a1; __Host-next-auth.csrf-token=ca91b91e2f52bdf913eff83161d7646a5ad6ebe91b119ec684c59b9d1963f470%7C8f71c5cea95ca2de40919ecb6da40893fc210523d79b93db51295f603f1abef6; _clck=ognrxy%5E2%5Eg0p%5E0%5E2126; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.basedlabs.ai%2Fgenerate%2Fcmhe53d2h04tq03crn78sk5dc; _ga_W69KQFDMG6=GS2.1.s1762169448$o13$g1$t1762169485$j23$l0$h0; __Secure-next-auth.session-token.0=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..dBSphsALM6DjtHda.Toi3SnmDBNHYDHZh2nVf9apGW0vLTEH-a-_IM1Nkm6bg_V3HG1LuB25zw1wwj3UBjnhDM3cS1tQCH6sbW1GXJ4WvM3o-YYK1mVxWo0XwoppGmWDtJdDCRv6t19hFs4Ru6fGfPKnP137xV0FWBQyt_Mw1YxzQDgwGsEmjMURrgMxKQyev0Ur1WA1e6s7qs91ast6DushkT4-IhMZtt4c3pCasywAyNQ1YJtBCaCjRmXHbQRk4wuB90xwd9yVX7s9YNdigQiOIwSR34Fs59zZqSq5D_Nt6HkmYtNodxcNYZrCNVKjS_P1eJMyChbYTWBePANAtOYfzinChEzpxGXOCN3YkVRzIYHtmO04esaHU1wOjHGN5Vj0hiFHWIuLQNyxh57ig3Bd_nTGSbhHA7_SunYN5eWVmMxwKVebyjHAwTS2vbJzrCCl_AA2I63SvTRPyKv0rQ4hkjesSk9LnYGpT_Y_wwYJhwDPWm79wM9GaSXWD17YVfjBOzPK_sdLdjNmQGTa5JnFGAT2fixOMn6-CfcjzAFkxMQDo0nH6RqOXZgOu5RTBWuCSU6Cc_od9fffgYiYf3g6ieC0p7DERfHNFRcskM_Y-KfJNBt1BOF3u-0ZF6EHYZgiiUI0hp55yo8E1kHOGWKVSt9RcNjOYdaZ7o420-pKke6A7iZf6KcjFA11vvTF4NIdYiq0F3klh-jPSUO2fc2GWVbe4ysQixxD1iqdBCcW8mmDM7x3Bhu1HNPKyGEZ45ixAXKDrGeOYxaDslRxO-teSJpG1iWaz5dhuTyxmu3XL61N1FJJaOMNd4Ul7jxK_aeJL8nC8bXwfWLL0IdVJUiUbY5Y7ORJm4Sm_aSu7YNbrf4Ml5QJJ9XG6mZtnqZO4dGET4_vjb2fnUe-M_EYS2aOx0uDiXNNxgQWKrnAqnpk2N4UlCpxO_MIwywm8St60WIkWgCEOhg5j5GQ5vQPwyGezznAgupxfMQVjy3OlBh5pRG5y8H8j7DIK8ga3lc4TAEgr_ND4uQo0nKHU4zZocibm_Q7Yf1AiKwrwGvsUJ157oKAbu-pxJF5zkJqxchT2Ny4BMFmZGMgFtDH2EyPytFuzXLpbb6d6PFdei0fHc1G-ay3ZtsHJ9DlYy1bu5vvejosXvgzrPluegXkadjIfkH6scDtm_ZZHaEvZ7TKYZY6nsBRYzc73WYMhWNpLfV2--crcV5MxTEgavidJ55NKKLkcBdQse4-Hq7lg3y0qZdyxWzRSh_-rVn0Zyw-gmRYPe8gJoSvuPf7QK_CKFYxcdlR5OPfcVrQmKqTLDZOZqQEAyaG13sF3zS_r-cCwg5s2vUt7MMerCmv600HaLV1re5A7bWYgenrpqOuKzc2U9-Tuxe64_K28efecS0MZT80WdAbsOHyMcVTMvpoH1uRou1KIeVsPdyecbddgv-cA0GMPrgOQjJxnwBuVg8VL_mHR4axATaepK9Gm-EjHBr5X_KGhlGLvBaWl4yUIZZSHXYdI3qJGEXLOKz94Gmk0qEzDaCP41YbkwMn7MU2yGZg0EA0ELVqdZriVnnOt-zNoMe_X6xgmYgTR6PcabrRkR_zOilF5cdrgIPN8Pn5mNLFWg6Ik2o6QN4xRmKjzcDL98wd1vqjaA01Lk4pwRORKC4IE-3mX7BTXLsQDMCDWQ37SqDOeK00moUzrFwkgpJ6dVjNhoMGiYtEkgnYX8jhGW95CN9scWuFz5lW7FtCRt5Qt63JCY7d5jy1Y_JJ4yFmt_Oy6kqGEbsG-E7_QOoNrLt-v6HuvRIs7hgS3Fxm3uzlf2Tj9Fg7c06xDiCUlkF_X8n9XFoq5-Yi2mQI6mNms6UhYVYOIIRKtJEfGOUZuz1YPP_0DfORO_Vvz3ZY4FjaiqDjx7b9BI1ZLxpxIaDYdUXKqo1AaDtUNUNz0P60bPrM6gz3Eo3A-c50G5ERHFRibZhUK3tXN_2DA5sGLY6moOHn5po5d9aes-r4swr_UZANiWMxsqSxX1UzGE1prraU25ZxYRg5-rIIETh3T2LZvhx50lWuhJ-poyK_gpwx4xwShBiLxVRTI_Dv3z6C81O0rTIJPMgIZhp5K7beJ-4ts6So5bDHJweb_h4wS6SofdzrdDw7OcLYH9aBHx6LNo5N6C1Zcjzgv-RidkRXixio37J9Ih_Vh7lGfejZLjiX7CZmOaEEhPzyxoiVKzqIJx_l3IrRR75HkgKhTOEILC999HSDZXSUQx1IMG4oLXuj1AdMZw1CHnfDtJM95OgY9CWmjjlid0ep8uGuXQgyscVfxzzIKyQuygZO0hN3cvbSjlqACtpBvr4koNLBTle26tIvQrr_5FC6s1u6r3letjqs8YlAy5Q-yK0e5Fu-KnsBwtmTjL3xkpIG06PRBuo-5nUG2e1zSCd6dWx8kDZ6zzlv417lyotED75ecwu7cn65fnukZ3VSelOQy_5ZM-4nrrTYzPlZweg9cxBoY_f8pwuAsGUEngqAVdzw-TGGV2UoWwmSmP3uQ8uM9zU5OqexejML405xWB4gUD9ySleb9mJNQvrtSxnF8oos7ubYvwKpowGL3KYyMQ33CrwCuWTKLrdr68tTi5uiTNmwFnDpRPul8Vb7YztPAMVLqyYlAooQWRM88YLPdnJGLvylk-XmU-b03-VUT_E60z0JvIJW1M1bowegGG0_cDK8DX-J39SnPANuYW5o7LlLsTJa6S2sEsY76TP3-V_JG4LZ7Jl4-5REfgfxsF866qV9wzEaF8Njqp8IUNP6DpuW6qoDcnP-gB2Crozf_arTXMu0lxNVjPF1MFOVWYniTatfmh65mYwtOuFHdKPkix5-EwTwLS7zOweJuvrqiEwfOQ_kmbyzX9fSwwyo53D-J7csTzheh7iuiB7YXLnAAksZPNeacAJq97Dj0yRg-HssiuVAIgCMeDONOj2KBbNN8lFrXdInCOT6LkA9rutNlCTSTiZkg9z0Gy6meU6NsnIdDOEsnsK7Y8a82LVnCMzbppPhcYzX-WpwvS8GrU7-9m8oDYO__JmXyVi28tLa7HiQ04uyYBMm8kqmBuRMM0xyaqZwOeIBjgg_6WEZJX2Vdw7sh9L2Ty6ZcOyWfAl2aPE-lfpcPdJJgAhZlKbh6TUXKNb-tCeG22-HJdPDcc5TrHDi_t5AAoAWsblI2yD9kXOymwVb1IKBKPUSIFA8SPHl03jFuPsRVNjdwoyqGJq9ZwL_wi-GMyrQ-qw0tjOT7aGIBha3NfQhNC4xq2J9xMZSyTcf2SLjzEvnewKXZLy8_DodCeuHXC4e11hfi3difJwUoeLkLYG0R0rkBPsn6hzlPcz7HOqq9fFiJMAnd1Mcn3xQnZduLcN-LpHwujVuk4dWUwMV9HE15oE4td_Gbea9QQW4xGisbwtOV_X6ByMufP1q4eKYRsTx_FaLrU-anCnH0mVMd6s23FX6uk1-Swothf-2O39hVuvtt-Jkq1uwzVzdi3ovEqUOK6am3qqx9eI8eytf8XJgjnKIoiC0DAjmx-t97Lqw-3uFnKLySX-l0ADfXqGEwXEgO9201U6RdcpVxscxg3hu-KnnNmyhDSHhClvtIGunYObvTQffs9TDLjcRmpClEOA3vk46blyVlSbp4KIdqVsfdvmVzQ_MVy1g29GBgHpdtBYuSubIEwQ5-tnoEjjHUMPWBbUEZ-Nqk_dNUSyF0MQYN0dFcAoU3GIfXzTFi_pE5dxNJAXeOSkBPLGqfn6Qy_kUL3cUPOUklfdxoUEnAU0SlZ8mAJGNvJp3v9vvTAlwWlIhHruiK6ycS9m6zBkwR9HvuVT5m9baOAyP1PX4CoPwBCw1arfsBWRpBCPFQqgFZeDcbMHCmarpaJcpkLf_Mxq684DcHSj-Po53etrn; __Secure-next-auth.session-token.1=Bb6wGRBCVUYf2o2X30sch9yHWo0RmBWk8sr-440iflI93kEaftm0iXiVHLSS4Ai5EOhYYNwtd7-h3PEHM3T8ixkWOboerFSil3HqvpeipPoQuYUeTP3YiC4JDsojFSh6mkkcUKyxkghQ-OoSFg-BMjX_cV4cV-QkE1L0ChjaasJiAoqc8syGZEGiawxKhN1zODwvGDlejnO6mbe9_oznpNjZmgS2d0kCwFf23jftED7xLU23AGCpZVVWRhAJ5Ab32goPlEp4DZOTkl8W0hvdvADFawXCe8lpF15j6TmA6t0LW4Go_EDUdNxcEtw5UCmG1OkRZSru-vNVf3-JgUo_xhq00Wzzr-w.6TTn2KAS86y9fu5c0-z3xw; _clsk=1t7ah87%5E1762169487822%5E2%5E1%5Ez.clarity.ms%2Fcollect; ph_phc_XWjgbcoHTiX3FlNDwmxBS48kFNh2ecuGsUzkut6aVPX_posthog=%7B%22distinct_id%22%3A%22440855%22%2C%22%24sesid%22%3A%5B1762169537917%2C%22019a497b-ed74-7e40-b809-3c6027d34a55%22%2C1762169449844%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22https%3A%2F%2Fwww.basedlabs.ai%2Fauth-complete%22%2C%22u%22%3A%22https%3A%2F%2Fwww.basedlabs.ai%2Fgenerate%2Fcmhe53d2h04tq03crn78sk5dc%22%7D%7D"
}

# --- خدمات Gemini ---
def generate_gemini_response(chat_history, prompt_text, image_base64=None, system_instruction=None):
    parts = [{"text": prompt_text}] if prompt_text else []
    if image_base64: parts.append({"inline_data": {"mime_type": "image/jpeg", "data": image_base64}})
    contents = [{"role": "user", "parts": parts}]
    data = {"contents": contents, "generationConfig": GENERATION_CONFIG, "safetySettings": SAFETY_SETTINGS}
    if system_instruction: data["system_instruction"] = system_instruction
    for api_key in API_KEYS:
        try:
            response = SESSION.post(GEMINI_API_URL_TEMPLATE.format(api_key), json=data, timeout=60)
            if response.status_code == 200:
                response_json = response.json()
                if "candidates" in response_json and response_json['candidates'] and 'parts' in response_json['candidates'][0]['content']:
                    return response_json['candidates'][0]['content']['parts'][0]['text'], response_json['candidates'][0]['content']
                else: 
                    print(f"Response BLOCKED or invalid: {response_json}")
                    return "تم حظر الاستجابة.", None
            else: 
                print(f"GEMINI API ERROR: Status {response.status_code} with key ...{api_key[-4:]} - Response: {response.text}")
        except requests.exceptions.RequestException as e: 
            print(f"NETWORK ERROR to Gemini with key ...{api_key[-4:]}: {e}")
    return "خطأ في الاتصال بالخدمة.", None

def generate_enhanced_prompt(simple_prompt):
    return generate_gemini_response([], simple_prompt, system_instruction=PROMPT_ENHANCER_INSTRUCTION)

def generate_enhanced_prompt_with_image(simple_prompt, image_base64):
    return generate_gemini_response([], simple_prompt, image_base64=image_base64, system_instruction=PROMPT_ENHANCER_WITH_IMAGE_INSTRUCTION)

def describe_image_with_gemini(image_base64):
    return generate_gemini_response([], "", image_base64=image_base64, system_instruction=IMAGE_DESCRIBER_INSTRUCTION)

# --- خدمات BasedLabs (إنشاء الصور) ---
def generate_image_from_prompt(prompt, image_count=1):
    start_url = "https://www.basedlabs.ai/api/generate/image/v2"
    payload = { "prompt": prompt, "negative_prompt": "", "num_outputs": str(image_count), "width": 1024, "height": 1024, "guidance_scale": 7.5, "num_inference_steps": 50, "selectedModel": {"id": 128, "versionInfo": {"modelPath": "fal-ai/imagen4/preview/ultra"}}, "model": "imagen3"}
    try:
        response_start = SESSION.post(start_url, data=json.dumps(payload), headers=BASEDLABS_HEADERS, timeout=20)
        if response_start.status_code != 200: 
            print(f"BasedLabs Error starting job: {response_start.status_code} - {response_start.text}")
            return []
        start_data = response_start.json(); request_id = start_data.get("request_id"); history_id = start_data.get("historyId")
        if not request_id or not history_id: 
            print(f"BasedLabs Could not get request_id or history_id: {start_data}")
            return []
        poll_url = f"https://www.basedlabs.ai/api/generate/image/v2/{request_id}"; poll_payload = {"historyId": history_id}
        for _ in range(30):
            response_poll = SESSION.post(poll_url, data=json.dumps(poll_payload), headers=BASEDLABS_HEADERS, timeout=20)
            if response_poll.status_code == 200:
                poll_data = response_poll.json(); status = poll_data.get("status")
                if status == "COMPLETED":
                    images_data = poll_data.get('history', {}).get('prediction', {}).get('images', [])
                    if images_data: return [img['url'] for img in images_data if 'url' in img]
            time.sleep(5)
        print("BasedLabs Job timed out."); return []
    except requests.exceptions.RequestException as e: 
        print(f"BasedLabs An error occurred during API call: {e}"); return []

# --- خدمات تعديل الصور (Digen API) ---
def _digen_upload_photo(image_path: str) -> str or None:
    print(f"Digen: Starting image upload: {image_path}")
    try:
        headers_presign = {
            'User-Agent': "Mozilla/5.0", 'Accept': "application/json, text/plain, */*",
            'digen-platform': "web", 'digen-language': "en", 'digen-sessionid': str(uuid.uuid4()),
            'digen-token': DIGEN_TOKEN, 'origin': "https://digen.ai", 'referer': "https://digen.ai/"
        }
        response_presign = SESSION.get("https://api.digen.ai/v1/element/priv/presign?format=jpeg", headers=headers_presign)
        response_presign.raise_for_status()
        upload_url = response_presign.json()['data']['url']

        with open(image_path, 'rb') as image_file:
            response_upload = SESSION.put(upload_url, data=image_file.read(), headers={'Content-Type': 'image/jpeg'})
        response_upload.raise_for_status()

        headers_sync = {
            'User-Agent': "Mozilla/5.0", 'Accept': "application/json, text/plain, */*",
            'Content-Type': "application/json", 'digen-platform': "web", 'digen-language': "en",
            'digen-sessionid': str(uuid.uuid4()), 'digen-token': DIGEN_TOKEN,
            'origin': "https://digen.ai", 'referer': "https://digen.ai/"
        }
        file_name = os.path.basename(image_path)
        payload_sync = {"url": upload_url.split('?')[0], "thumbnail": upload_url.split('?')[0], "fileName": file_name}
        response_sync = SESSION.post("https://api.digen.ai/v1/element/priv/sync", data=json.dumps(payload_sync), headers=headers_sync)
        response_sync.raise_for_status()
        
        final_image_url = response_sync.json()['data']['url']
        print(f"Digen: Image uploaded successfully. URL: {final_image_url}")
        return final_image_url
    except Exception as e:
        print(f"Digen: An error occurred during upload: {e}")
        return None

def _digen_submit_task(prompt: str, reference_image_url: str) -> str or None:
    print("Digen: Submitting generation task for Job ID...")
    headers = {
        'User-Agent': "Mozilla/5.0", 'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json", 'digen-platform': "web", 'digen-language': "en",
        'digen-sessionid': str(uuid.uuid4()), 'digen-token': DIGEN_TOKEN,
        'origin': "https://digen.ai", 'referer': "https://digen.ai/"
    }
    payload = {
        "image_size": "1024x1024", "width": 1024, "height": 1024, "prompt": prompt,
        "batch_size": 1, "strength": "0.9", "activity_id": "3",
        "reference_images": [{"image_url": reference_image_url}]
    }
    try:
        response = SESSION.post("https://api.digen.ai/v2/tools/text_to_image", data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        job_id = response.json().get('data', {}).get('id')
        if job_id:
            print(f"Digen: Task submitted successfully. Job ID: {job_id}")
            return job_id
        else:
            print(f"Digen: Job ID not found in response: {response.text}")
            return None
    except Exception as e:
        print(f"Digen: An error occurred while submitting the task: {e}")
        return None

def _digen_check_status(job_id: str) -> str or None:
    print(f"Digen: Starting to check status for job: {job_id}")
    url = "https://api.digen.ai/v6/video/get_task_v2"
    payload = {"jobID": job_id}
    headers = {
        'User-Agent': "Mozilla/5.0", 'Accept': "application/json, text/plain, */*",
        'Content-Type': "application/json", 'digen-platform': "web", 'digen-language': "en",
        'digen-sessionid': str(uuid.uuid4()), 'digen-token': DIGEN_TOKEN,
        'origin': "https://digen.ai", 'referer': "https://digen.ai/"
    }
    for attempt in range(40): # Poll for up to 2 minutes
        try:
            response = SESSION.post(url, data=json.dumps(payload), headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json().get('data', {})
            status = data.get('status')
            print(f"Digen: Attempt {attempt + 1}/40 for job {job_id}: Status is {status}")
            if status == 4: # 4 = Completed
                image_url = data.get('resource_urls', [{}])[0].get('image')
                if image_url:
                    print(f"Digen: Task {job_id} completed! Image URL found.")
                    return image_url
                else:
                    print(f"Digen: Status is 4 but no image URL found for job {job_id}! Response: {data}")
                    return None
            time.sleep(3)
        except Exception as e:
            print(f"Digen: Error checking task status for job {job_id}: {e}")
            time.sleep(3)
    print(f"Digen: Polling timed out for job {job_id}.")
    return None

def edit_image_with_digen(image_path, prompt):
    reference_url = _digen_upload_photo(image_path)
    if not reference_url:
        return None
    job_id = _digen_submit_task(prompt, reference_url)
    if not job_id:
        return None
    final_image_url = _digen_check_status(job_id)
    return final_image_url

# --- خدمات الفيديو العامة والخاصة ---
def upload_image_for_video(image_bytes, file_name):
    try:
        img = Image.open(BytesIO(image_bytes)); width, height = img.size
        content_type = Image.MIME.get(img.format, 'image/jpeg')
        signed_url_payload = {"fileName": file_name, "contentType": content_type, "fileSize": len(image_bytes), "uploadTool": "generate2-drag-drop"}
        signed_url_response = SESSION.post("https://www.basedlabs.ai/api/upload/signed-url", data=json.dumps(signed_url_payload), headers=BASEDLABS_HEADERS)
        signed_url_response.raise_for_status(); upload_data = signed_url_response.json()
        SESSION.put(upload_data['signedUrl'], data=image_bytes, headers={'Content-Type': content_type}).raise_for_status()
        complete_payload = {"uploadId": upload_data['uploadId'], "cdnUrl": upload_data['cdnUrl'], "fileName": file_name, "contentType": content_type, "fileSize": len(image_bytes), "uploadTool": "generate2-drag-drop", "width": width, "height": height, "key": upload_data['key']}
        SESSION.post("https://www.basedlabs.ai/api/upload/complete", data=json.dumps(complete_payload), headers=BASEDLABS_HEADERS).raise_for_status()
        return {"cdnUrl": upload_data['cdnUrl'], "width": width, "height": height, "uploadId": upload_data['uploadId']}
    except Exception as e:
        print(f"Image upload for video failed: {e}"); return None

def _start_video_job(api_url, payload):
    try:
        response = SESSION.post(api_url, data=json.dumps(payload), headers=BASEDLABS_HEADERS)
        response.raise_for_status()
        data = response.json()
        request_id, history_id = data.get("request_id"), data.get("historyId")
        if not all([request_id, history_id]): 
            print(f"Video start failed, missing IDs. Response: {data}")
            return None
        return {"request_id": request_id, "history_id": history_id}
    except Exception as e:
        print(f"Video generation start failed: {e}"); return None

# --- دوال خاصة بكل موديل ---

def start_veo_text_to_video_job(prompt):
    print("Starting VEO TEXT-TO-VIDEO generation...")
    payload = { "prompt": prompt,    "selectedModel": { "id": 84, "label": "Veo3", "purpose": "Video", "type": "Checkpoint", "description": "veo 3 is effectively acting as a camera operator, set designer, and editor that gets your script – following stage directions about characters and camera angles with newfound accuracy.", "baseModel": "Veo3", "versionInfo": { "id": 97, "index": None, "name": "1.0 Text", "description": None, "modelId": 84, "trainedWords": [], "steps": None, "epochs": None, "clipSkip": None, "vaeId": None, "createdAt": "2025-06-18T06:40:31.421Z", "updatedAt": "2025-09-09T03:16:59.081Z", "publishedAt": None, "status": "Published", "trainingStatus": None, "trainingDetails": None, "inaccurate": False, "baseModel": "Veo3", "baseModelType": None, "meta": {}, "earlyAccessTimeFrame": 0, "requireAuth": False, "settings": None, "availability": "Public", "creditCost": 300, "creditCostConfig": { "8": 300 }, "isActive": True, "modelPath": "fal-ai/veo3", "baseModelSetType": None, "type": "TextToVideo", "uploadType": "Created", "files": [] }, "checkpoint": "" }, "width": 1280, "height": 720, "duration": 5, "aspect_ratio": "16:9", "mediaId": "cmfu0511e0468ypgv5rab1h67", "fps": 24, "advanced": { "videoDuration": 5, "videoAspectRatio": "16:9" } }
    return _start_video_job("https://www.basedlabs.ai/api/generate/text-to-video", payload)

def start_veo_image_to_video_job(prompt, image_url, media_id):
    print("Starting VEO IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt, "image_url": image_url, "model": { "id": 84, "label": "Veo3", "purpose": "Video", "type": "Checkpoint", "description": "veo 3 is effectively acting as a camera operator, set designer, and editor that gets your script – following stage directions about characters and camera angles with newfound accuracy.", "baseModel": "Veo3", "versionInfo": { "id": 144, "index": None, "name": "1.0 Image", "description": None, "modelId": 84, "trainedWords": [], "steps": None, "epochs": None, "clipSkip": None, "vaeId": None, "createdAt": "2025-08-02T02:10:24.730Z", "updatedAt": "2025-09-09T03:15:45.253Z", "publishedAt": None, "status": "Published", "trainingStatus": None, "trainingDetails": None, "inaccurate": False, "baseModel": "Veo3", "baseModelType": None, "meta": {}, "earlyAccessTimeFrame": 0, "requireAuth": False, "settings": None, "availability": "Public", "creditCost": 300, "creditCostConfig": { "8": 300 }, "isActive": True, "modelPath": "fal-ai/veo3/image-to-video", "baseModelSetType": None, "type": "ImageToVideo", "uploadType": "Created", "files": [] }, "checkpoint": "", "version": "1.0 Image" }, "width": 1024, "height": 1024, "duration": 8, "mediaId": "cmgfopat300laz6e9n9h4uxja", "sourceMedia": image_url, "motion_bucket_id": 60, "generate_audio": True, "resolution": "1080p", "aspect_ratio": "auto" }
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def start_sora_text_to_video_job(prompt):
    print("Starting SORA TEXT-TO-VIDEO generation...")
    payload = {"prompt": prompt,"selectedModel": {"id": 136,"label": "Sora","purpose": "Video","type": "Checkpoint","description": "This video generation model is more physically accurate, realistic, and more controllable than prior systems. It also features synchronized dialogue and sound effects.","baseModel": "sora","versionInfo": {"id": 169,"name": "2","modelId": 136,"createdAt": "2025-10-06T20:58:42.562Z","updatedAt": "2025-10-06T21:52:35.411Z","status": "Published","baseModel": "sora","creditCost": 40,"creditCostConfig": {"4": 40,"8": 80,"12": 120},"isActive": True,"modelPath": "fal-ai/sora-2/text-to-video","type": "TextToVideo"},"checkpoint": ""},"width": 1280,"height": 720,"duration": 12,"aspect_ratio": "16:9","resolution": "720p","mediaId": "cmh8pnlhu06ne0rfh6sw7zyd9","fps": 24,"advanced": {"videoDuration": 12,"videoAspectRatio": "16:9"}}
    return _start_video_job("https://www.basedlabs.ai/api/generate/text-to-video", payload)

def start_sora_image_to_video_job(prompt, image_url, media_id):
    print("Starting SORA IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt,"image_url": image_url,  "model": { "id": 136, "label": "Sora", "purpose": "Video", "type": "Checkpoint", "description": "This video generation model is more physically accurate, realistic, and more controllable than prior systems. It also features synchronized dialogue and sound effects.", "baseModel": "sora", "versionInfo": { "id": 170, "index": None, "name": "2", "description": None, "modelId": 136, "trainedWords": [], "steps": None, "epochs": None, "clipSkip": None, "vaeId": None, "createdAt": "2025-10-06T21:00:59.007Z", "updatedAt": "2025-10-06T21:52:44.257Z", "publishedAt": None, "status": "Published", "trainingStatus": None, "trainingDetails": None, "inaccurate": False, "baseModel": "sora", "baseModelType": None, "meta": {}, "earlyAccessTimeFrame": 0, "requireAuth": False, "settings": None, "availability": "Public", "creditCost": 40, "creditCostConfig": { "4": 40, "8": 80, "12": 120 }, "isActive": True, "modelPath": "fal-ai/sora-2/image-to-video", "baseModelSetType": None, "type": "ImageToVideo", "uploadType": "Created", "isDefault": False, "autoUpscale": False, "files": [] }, "checkpoint": "" }, "width": 1024, "height": 1024, "duration": 12, "mediaId": "cmhdek3if03l6yifsr2b2athb", "sourceMedia": image_url, "motion_bucket_id": 60, "generate_audio": True, "resolution": "720p", "aspect_ratio": "auto" }
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def start_sora_pro_text_to_video_job(prompt):
    print("Starting SORA PRO TEXT-TO-VIDEO generation...")
    payload = {"prompt": prompt,"selectedModel": {"id": 136,"label": "Sora","purpose": "Video","type": "Checkpoint","description": "This video generation model is more physically accurate, realistic, and more controllable than prior systems. It also features synchronized dialogue and sound effects.","baseModel": "sora","versionInfo": {"id": 172,"name": "2 Pro","modelId": 136,"createdAt": "2025-10-08T09:25:37.338Z","updatedAt": "2025-10-08T09:26:39.470Z","status": "Published","baseModel": "sora","creditCost": 80,"creditCostConfig": {"4": 80,"8": 120,"12": 240},"isActive": True,"modelPath": "fal-ai/sora-2/text-to-video/pro","type": "TextToVideo"},"checkpoint": "","version": "2 Pro"},"width": 1280,"height": 720,"duration": 8,"aspect_ratio": "16:9","resolution": "720p","mediaId": "cmhdz8pd7075e1cfldfwugpb1","fps": 24,"advanced": {"videoDuration": 8,"videoAspectRatio": "16:9"}}
    return _start_video_job("https://www.basedlabs.ai/api/generate/text-to-video", payload)

def start_sora_pro_image_to_video_job(prompt, image_url, media_id):
    print("Starting SORA PRO IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt,"image_url": image_url,"model": {"id": 136,"label": "Sora","purpose": "Video","type": "Checkpoint","description": "This video generation model is more physically accurate, realistic, and more controllable than prior systems. It also features synchronized dialogue and sound effects.","baseModel": "sora","versionInfo": {"id": 173,"name": "2 Pro","modelId": 136,"createdAt": "2025-10-08T09:25:51.489Z","updatedAt": "2025-10-08T09:27:00.146Z","status": "Published","baseModel": "sora","creditCost": 80,"creditCostConfig": {"4": 80,"8": 120,"12": 240},"isActive": True,"modelPath": "fal-ai/sora-2/image-to-video/pro","type": "ImageToVideo"},"checkpoint": "","version": "2 Pro"},"width": 1024,"height": 1024,"duration": 12,"mediaId": "cmhdz8pd7075e1cfldfwugpb1","sourceMedia": image_url,"motion_bucket_id": 60,"generate_audio": True,"resolution": "720p","aspect_ratio": "auto"}
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def start_kling_image_to_video_job(prompt, image_url, media_id):
    print("Starting KLING (Turbo) IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt,"image_url": image_url,  "model": { "id": 118, "label": "Kling", "purpose": "Video", "type": "Checkpoint", "description": "Kling model for video generation", "baseModel": "Kling", "versionInfo": { "id": 167, "index": None, "name": "2.5 Turbo", "description": None, "modelId": 118, "trainedWords": [], "steps": None, "epochs": None, "clipSkip": None, "vaeId": None, "createdAt": "2025-09-23T21:57:59.791Z", "updatedAt": "2025-09-23T21:58:40.950Z", "publishedAt": None, "status": "Published", "trainingStatus": None, "trainingDetails": None, "inaccurate": False, "baseModel": "Kling", "baseModelType": None, "meta": {}, "earlyAccessTimeFrame": 0, "requireAuth": False, "settings": None, "availability": "Public", "creditCost": 50, "creditCostConfig": { "5": 50, "10": 100 }, "isActive": True, "modelPath": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video", "baseModelSetType": None, "type": "ImageToVideo", "uploadType": "Created", "isDefault": False, "autoUpscale": False, "files": [] }, "checkpoint": "" }, "width": 447, "height": 447, "duration": 10, "mediaId": "cmh8pnlhu06ne0rfh6sw7zyd9", "sourceMedia": image_url, "motion_bucket_id": 60, "generate_audio": True, "resolution": "720p", "aspect_ratio": "auto" }
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def start_kling_standard_image_to_video_job(prompt, image_url, media_id):
    print("Starting KLING (Standard) IMAGE-TO-VIDEO generation...")
    payload = { "prompt": prompt, "image_url": image_url, "model": { "id": 118, "label": "Kling", "purpose": "Video", "type": "Checkpoint", "description": "Kling model for video generation", "baseModel": "Kling", "versionInfo": { "id": 129, "index": None, "name": "2.1 Standard", "description": None, "modelId": 118, "trainedWords": [], "steps": None, "epochs": None, "clipSkip": None, "vaeId": None, "createdAt": "2025-06-19T01:47:31.721Z", "updatedAt": "2025-07-14T03:25:11.370Z", "publishedAt": None, "status": "Published", "trainingStatus": None, "trainingDetails": None, "inaccurate": False, "baseModel": "Kling", "baseModelType": None, "meta": {}, "earlyAccessTimeFrame": 0, "requireAuth": False, "settings": None, "availability": "Public", "creditCost": 50, "creditCostConfig": { "5": 50, "10": 100 }, "isActive": True, "modelPath": "fal-ai/kling-video/v2.1/standard/image-to-video", "baseModelSetType": None, "type": "ImageToVideo", "uploadType": "Created", "isDefault": False, "autoUpscale": False, "files": [] }, "checkpoint": "" }, "width": 1024, "height": 1024, "duration": 10, "mediaId": "cmhesrtdu05ia03cr84b439l6", "sourceMedia": image_url, "motion_bucket_id": 60, "generate_audio": True, "resolution": "720p", "aspect_ratio": "auto" }
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def poll_for_video_result(request_id, history_id, cancel_event):
    poll_url = f"https://www.basedlabs.ai/api/generate/video/{request_id}"
    poll_payload = {"id": request_id, "historyId": history_id}
    for i in range(120): # Poll for up to 10 minutes
        if cancel_event.is_set(): return "CANCELLED"
        try:
            response = SESSION.post(poll_url, data=json.dumps(poll_payload), headers=BASEDLABS_HEADERS, timeout=15)
            response.raise_for_status()
            data = response.json(); status = data.get("status")
            print(f"Polling attempt {i+1}... Status: {status}")
            if status == "COMPLETED":
                return data.get("output")
            elif status == "FAILED":
                print(f"Polling failed for request {request_id}. Full response: {data}")
                return None
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Polling failed for request {request_id}: {e}"); return None
    print("Polling timed out."); return None
