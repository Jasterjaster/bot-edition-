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
    'Cookie': "_ga=GA1.1.1481592877.1761543536; _gcl_au=1.1.858473141.1761543536; wooTracker=hmuCqdt5aCnU; __stripe_mid=b2e8127c-4af7-48e7-afa1-5ece90f7ed4bd735a1; __Host-next-auth.csrf-token=8b81582a1bf06b4b9874dfc38bd05bb138555c91a3791fb62b37914a7b9b2f54%7Ce4cedc8303cdd99e503a210b28088483333cd6e1f21b7623ba3750658a46fca4; _clck=ognrxy%5E2%5Eg0m%5E0%5E2126; __Secure-next-auth.callback-url=%2Fauth-complete; __Secure-next-auth.session-token.0=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..ERkyod92dxFJL2q6.yKKp4SDSH2COy9ta9anPE2SlQeZ3qCSCzZpXQz_3PJHonqddvE9Hj-VBQYlMlAyPUjLuoHzk2OlWPMjJOvNzwx3QyGx2ef0QCEczUuLuLZxAT31ol08uVhavI5pQonbdq0_C-ubO5C78WdVCM4zZ-MzsDbj1pjDaYVL1DxRRwdHEGCRy6UIFdQcyBGINRv9ZW63QhKLLYyPeV3aR0fPd7f8MoIUu04NXENbGtvU5RPT-zCbWx-d6bJ0uOuN3CpS1AtVcqYLxZJztC_YZZ4uCE_CV-XgPOyvkonI78DHMQ-DxcoymYDlQoU84plaEK22Nd4bTkB1ODm0HlTLG9FLzHW0J7XDhRjufxsQ2Lm7Go_HNiArVDoj0yJ6AqVJsInk-IGGWwF8VaJIynEcuyXiWH5e4KmPSjkpaPFStbbBMKoRPKCH8-2UZRNnZRvllOuNRFlKoib2J07Bg-pgKjPDJi34vPGrHJ-iZGVd8rIUxYjBztR1rQU4PHPqWOvEQjd9aVMeSgKoduKDnO2kY-zvmZnuTznoybzcXfP8PlT1XSaH0xUC7dS_ykZrCZBUUbONtlDFwrCNyEURyYFV1hiQUUhxLKEgBM6vx123PGiDmuCwW-eDxQ0vMOIwO3LpJ-ZNvNSzYSlRZtN3JvpDPckONJiXupeKvgbFTA1fOKkjB4ZsSCs5Xcrl2KIKfqtepT21QcZSU_1c2lLzjTUboY_OmWmb4wdnpj4YZCjlbp3cueBqV3F4kYRkL0q32Ili_OMrscroUwt5ld8JIbNuXg_CqB5mgcli3cZrbsW1w8erSqmRUjLbkGTOWwW1b-j8PgIVnn1gEOhcNljMLjnkSIhZFVrKSiM49yW8ucZAluVVjIrIoar-hegTC1WKmqaZPRkj5U164Ywc7_pkXO84PmotZQCDKPC6NSfLanDCxgwlrX4khLvTCZlyRte1QkdxXQ0GHiywENa_5A8rvHhRW8BlMcdG0xsfX2Pt5ykUi3SOQXRR2bT8qzvwBlBi-1djS_LsPml2GucYbF8DdvAZZbBh6kz7RWGNkjZcumak72UtLUDkDNo1WGnYHeRVAP-eiQF4_ffYHSzo-O8KOE690ojEDuc4Oo3mJScgx1o1ZPISWrZWmhrs_DPKMGd9Z0RMcmTzmlE8YSmhjuPogFc0wofb-JeXJYXa_52YtkjSRZVPAKqVSOJFYNqk_U3YvgGWhQo6amWhHj2RU5-rZqxSbUdrJVUKy1IW7N6ldkXh4Ls1wjNtUseM4VTDuj-wD0JcqEcA9qwCkzB9TVha7gdqeXnQ8HaejMqkBUHvw54nFfhp38YFGpjMd9hpZScI-yZNL5I8m6-Yo4oGBzaE5SpYkAM4laeMLK752xL2KudckHP1W9YggWiyRoQqKx9hznbpQXef5V8UBE3wzQD-mplv5u_ei6BWNiKoXhl0zTf1eXe4x9RrTVGpRsMscYaRYvPE2_27eAUH4SMASHMrZ2atslXBpozBiVKY8kIGUYYpXwSaph14s1rKyNki3rM9hZBO5QyK_NyOMSIJP5wq-u0fJctw9BN-HV2IJplEkHv-Ob9wqdo4Hm4JfFB5DMM6QFfFH_-I-6SCFEmyTuPUdp3nMYxiQ_5FpVgxamfnhrrTIEqGUBpxL-JZG-2etVG-RZ-kzrzKc0hZ0ZHG_5AicwNGHelOIdMb55YvKK7ZD_T8JeLi3RuQxyUIMm444GUuykx8yxdREXFCWxoAK5Q_lRmstOaYTWEHCtBcskeiat2E0SI3fUWj172SH_eKHI6vzIXYF7fcCz1vVrH_kUplaVuCNgMe4QZhfEw38v_TrSl3BGczfNZ67a8hCeCrlZLQbtz2G7DYh2U0bQNZ-kwkiHD7FrmWktUjRH8Q_t1QK1aTS2CviSeuySECAWmZVmBayx3i8wQuWRXpfN9sdGR6Jw2ck29GTUjW2Fh0J8xCSjcU7sexzoWzbtu1dk4774rxwNqMS1a991dsONH5SUIxaryxXGDiADpsqOW1NwDTTFJHCsS36XHeEmtDzwyLO5p_kApFhcCRhn-_4Pe90HRexOrgDKKpznAPYcQC6qO2z26nW-8IoDdFfvcWBq-A7WeKCSGhuebo5jfbxaZr9jAT9yW8hb3yShUzg0PSLRTsJnh7VLP-dNjEzdQPT7RdrZqwkCFZzE8SzoQSWmdEXnEW3X5m5b89su0W7RjEgrLQrqTAYVMxj49lzTJD0A0sE-fB7jIzCkytIAynJlUw5m-n3Rmj0UM8Lqca0S8Km91KfJPZFtd6_WCw5TIp-YtaPEJRw-YgIv83G4gZf3cZyCYhIPte7HMgB2iiKEjWI9ufBysU_w0yCSiB6XImnSoEjRjO773G574BNQZh5C6kk6_WCuvN-5VLRkcvuCOZKWqPxibY_6NVkqM8NQ2tyR5KESLRA61M5sLX0XuXROLJ16eMKfLqg1hH7fV6TMytvaOTVA1Jzf1tnhObFx6qSG6yNlS6KX78Nx9Gg1nFbTdlCIYwX1kjrzMiiY_t4-An6B5xbzJ7PZEx6XuOP8-dPgTT9bYv28sbhNYqdKy1hchS26M7R4SO6OKBvKr9mw4KUoJC32ad9WRy7trtkfCqPYyHvH0Bg350vsUrvxBn4H63AUNWrUJz7JCPC0Q24QYvlD2erK519uXtnzT4Zt-gtRxSzlJWLPOvSSr1mo5rjPJ0u1t_0P49t-C1kh73F-dwyx_KMP5JzCbIl10LWXrqnk16WC9t8RB-OlF7T9Wurx0oY3SD7icVmZ6nMhjTPmciBUcbcy_t7c9bntrJ1pdFHP_CfI-zzS4o5JJ_aa-DeB2VfDkGetj6J4Jsc57WCQsQOhR3euorz6c1hLymxfbve6GE2VPCPVBSBq4knXEDfYV4LkcL6yKNdD2TFPMk-F8PO2xFOlb4WFwyOZA5T0CGyNykWDZyFU4xS6QqE1gGVRnAiAHStbyx7s835RI83dAjOcGj8WxMgCmPChWGEd0aykx3hfQNxV2ogRJK6RVtT4Z6SOMQdaXmNJVJkImDGf2RG1u70O_V-pF8CB2--IVwzEcDqGt5SRBSxX-2JNID3vTuheLrs825LZgpPKAXgltX5VIEK2puTUlyahml3lgy3llU2lzptodicwwF7TRzPluL6JhHaIeZSJSXAjHYMU2Kk_T4cVtQwsDQOtEni7dcRlpi87I82FqfKJxHwyJAR7pCa_BI93CDNFwSvG0gDmxicqnnlrlrVd9Ytco5U9KmJQ_myb1m4A1kYGNaopOjnuAXwi0OU3YCp6QNq0EcIlLdRY-36W3Zp7aEjLR6KPShASFA4MjqYdmbFxoZiY91oq__A8zg3rKXsKX3OtOtHilVfBCtbe8JwDdn2HEqEuPxLL5nxgEw4JjZJ3RrVRGfuLF2n81lRJu8jo2yKKpREigTP_Y-DGYv_jxAehqPvXg0MDcYdxgSEj1C6bR5uOnv7KnP8ibTSSck3iJ3mYY7lswmSLDJ6pJ4W4kDG4zWoDDleEamcRj_QFMz2pZQkNV4VaCjhEkqGRX5iWgS5Keb8jZUK1aWV-LJtN_9jNqCJmh30rt0zIugvflCAt5C0XTer1VJJyFxoxwFN0F5xceHpcRB-loIRRl3AdCXKKkhjv1foXHXH9UEQB4bQejmp5Ul--H6xwH01n-W2NsdunhwJs1p9VbmVD1EmR4F-EVxNlz5Rm7RpBM7WYjZj_xHgmJRm_ZbGs3eLNcbDREqt0hO-s6D4UF4tBLrljsP7YU9F13tmpGldb3NojLsuwiZHEa35zRsTIDyr19BdZa1L549iOpIDGLm3bkdUkR-CWVkL6UjMseA0PP9dtocP0khTk0ai3iNlRIZXYIy0sD4Ladk4YN4FufvkcqH; __Secure-next-auth.session-token.1=AHdWY7POsT8w_Rf7oliDgBhBAfyjYfv3XNieijC-4wqIAsKdiwZbTCa-dBLAe8QU2zc-hr7yYAjnhXxW_xEz2xIDCA7dcZDTCUSr25hObBXYlQefh_pEUbhO9guKQjqsP5lDk4pSayxxrDqTHBoJiyGeQqKzvqJU1LrXlk_1hd8gkSfNy6BWUVn8d3cVmNDTHgSr8rIMw16ubJzLde2uQCdRXUPRQ93DZL52IIDhcooBtsdQZOsgSfTlrm96J9YSVVk5diICfYM7Esi_DPhde7mmJWnHESh17qnGXw9sjHSs6eca48j-Thn0rR25U1v3WBXEuRH7aVc5QmmONUKE2OT_qnaBoyQ.jwmzYxdZxXAiqiH5z22zhg; _ga_W69KQFDMG6=GS2.1.s1761871667$o8$g1$t1761871993$j60$l0$h0; _clsk=1ycp1ma%5E1761871993758%5E4%5E1%5Ej.clarity.ms%2Fcollect; ph_phc_XWjgbcoHTiX3FlNDwmxBS48kFNh2ecuGsUzkut6aVPX_posthog=%7B%22distinct_id%22%3A%22440855%22%2C%22%24sesid%22%3A%5B1761872134056%2C%22019a37bc-215a-71dc-a41d-a4cff75b04ed%22%2C1761871667546%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22https%3A%2F%2Fwww.basedlabs.ai%2Fgenerate%22%2C%22u%22%3A%22https%3A%2F%2Fwww.basedlabs.ai%2Fgenerate%2Fcmh8pnlhu06ne0rfh6sw7zyd9%22%7D%7D"}

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
