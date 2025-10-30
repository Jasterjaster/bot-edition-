import requests
import json
import time
import os
from io import BytesIO
from PIL import Image

# --- الإعدادات ---
API_KEYS = [os.getenv("GOOGLE_API_KEY_1"), os.getenv("GOOGLE_API_KEY_2")]
GEMINI_API_URL_TEMPLATE = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={}"
GENERATION_CONFIG = {"temperature": 1, "top_p": 0.95, "top_k": 64, "max_output_tokens": 8192}
SAFETY_SETTINGS = [{"category": c, "threshold": "BLOCK_NONE"} for c in ["HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH", "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"]]
SESSION = requests.Session()

PROMPT_ENHANCER_INSTRUCTION = {
    "parts": [{"text": "You are a professional prompt engineer for an AI image generator. Your task is to take a user's simple idea and expand it into a detailed, rich, and effective prompt in English. The prompt should include details about the subject, setting, lighting, artistic style, composition, and technical specifications like '8K, photorealistic, sharp focus'. Your output should ONLY be the final English prompt, with no additional text or explanation."}]
}
IMAGE_DESCRIBER_INSTRUCTION = {
    "parts": [{"text": "You are an expert art analyst. Your task is to describe the provided image in comprehensive detail. Cover the main subject, background, setting, color palette, lighting, composition, mood, and potential artistic style. Your description should be clear, objective, and informative. Respond in Arabic."}]
}

BASEDLABS_HEADERS = {
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36",
    'Content-Type': "application/json",
    'origin': "https://www.basedlabs.ai",
    'referer': "https://www.basedlabs.ai/generate",
    'Cookie': "__stripe_mid=98a39d0e-fc3b-4d3f-8440-fb44ed522f89850cb2; wooTracker=qMbCymDSKWsG; _ga=GA1.1.627743185.1759741008; _gcl_au=1.1.1178378055.1759741008; _clck=g8363s%5E2%5Efzx%5E0%5E2105; __Host-next-auth.csrf-token=b0968e1c7f8a1f342798bc3f24d14bfd9b48bace3b6d16b658836f7ec2d3a6cd%7Cecb359cd5c5fb76ec2749506f4644f3d2855d5bbd923eea23d791af531129b70; __Secure-next-auth.callback-url=https%3A%2F%2Fwww.basedlabs.ai; _ga_W69KQFDMG6=GS2.1.s1759788282$o2$g1$t1759789106$j59$l0$h0; __Secure-next-auth.session-token=eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..Jqq0vx-U4vaVMng5.n7xOHmgjdpC5Re1NxwDI84mLsrCK-jqGarMANT6iWmX32BlX3iI-S6irf6-GZ9Vr23ZQC6uqQ0yMwkj7CKtv-GgxRCq-EW7cthwN6cA-YnYZAvAEcsMC02uP6fasrn04tz5bzeSDeHC-vpIPU-D-06V99hT_IIH3q5D8Gv0s4qW3EqDVjsC4HvQhJoDEIB5olmgSJoNAHKuM6X5VhRZVXpNJDIacDOT8xwbKKT2b-lWovS_yhTy8AnfEPK675fKN_PFVCtm8nC1HMOwH8Pkt2qvBrweawn9QNVKjhoPWZPLJEOL30zC38vWD905OELr7F3htZ3dDyTSZ-Lc_RtA59ELsSdXzHw9py2LRxJeb8JSEami0kyUnhPflenJYym3sJuS9CN4sEZIXzSO5b0p45BK1KImlroCagG_Ltv6ZWYuV8mkZbHD4zHl8CNso_Sq2r1A9_-2ShBJDf56XBw8V64vGj90YAhlf6GhVDdJxTqF7y6Oon62SIyhwfgvcGm8Y010On7qN13SJoBksJcJ9GpnUTrScOtxRAK22oGTt5_O0-gcDbzxVwmLXhsLs5A.XoYjqyTU9FbZqiQhrxbeXw; ph_phc_XWjgbcoHTiX3FlNDwmxBS48kFNh2ecuGsUzkut6aVPX_posthog=%7B%22distinct_id%22%3A%22440855%22%2C%22%24sesid%22%3A%5B1759789165252%2C%220199bb8e-35c4-78dd-9005-f89bea23a40e%22%2C1759788283332%5D%2C%22%24epp%22%3Atrue%2C%22%24initial_person_info%22%3A%7B%22r%22%3A%22%24direct%22%2C%22u%22%3A%22https://www.basedlabs.ai/generate%22%7D%7D"
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
                print(f"GEMINI API ERROR: Status {response.status_code} with key ...{api_key[-4:]}.")
        except requests.exceptions.RequestException as e: 
            print(f"NETWORK ERROR to Gemini with key ...{api_key[-4:]}: {e}")
    return "خطأ في الاتصال بالخدمة.", None

def generate_enhanced_prompt(simple_prompt):
    return generate_gemini_response([], simple_prompt, system_instruction=PROMPT_ENHANCER_INSTRUCTION)

def describe_image_with_gemini(image_base64):
    return generate_gemini_response([], "", image_base64=image_base64, system_instruction=IMAGE_DESCRIBER_INSTRUCTION)

# --- خدمات BasedLabs (الصور والفيديو) ---
def generate_image_from_prompt(prompt):
    start_url = "https://www.basedlabs.ai/api/generate/image/v2"
    payload = { "prompt": prompt, "negative_prompt": "", "num_outputs": "1", "width": 1024, "height": 1024, "guidance_scale": 7.5, "num_inference_steps": 50, "selectedModel": {"id": 128, "versionInfo": {"modelPath": "fal-ai/imagen4/preview/ultra"}}, "model": "imagen3"}
    try:
        response_start = SESSION.post(start_url, data=json.dumps(payload), headers=BASEDLABS_HEADERS, timeout=20)
        if response_start.status_code != 200: print(f"Error starting job: {response_start.text}"); return []
        start_data = response_start.json(); request_id = start_data.get("request_id"); history_id = start_data.get("historyId")
        if not request_id or not history_id: print(f"Could not get request_id or history_id: {start_data}"); return []
        poll_url = f"https://www.basedlabs.ai/api/generate/image/v2/{request_id}"; poll_payload = {"historyId": history_id}
        for _ in range(30):
            response_poll = SESSION.post(poll_url, data=json.dumps(poll_payload), headers=BASEDLABS_HEADERS, timeout=20)
            if response_poll.status_code == 200:
                poll_data = response_poll.json(); status = poll_data.get("status")
                if status == "COMPLETED":
                    images_data = poll_data.get('history', {}).get('prediction', {}).get('images', [])
                    if images_data: return [img['url'] for img in images_data if 'url' in img]
            time.sleep(5)
        print("Job timed out."); return []
    except requests.exceptions.RequestException as e: print(f"An error occurred during API call: {e}"); return []

def upload_image_for_editing(image_data, file_name="temp_image.jpg"):
    try:
        url_step1 = "https://www.basedlabs.ai/api/upload/signed-url"
        payload_step1 = {"fileName": file_name, "contentType": "image/jpeg", "fileSize": len(image_data), "uploadTool": "generate2-drag-drop"}
        response_step1 = SESSION.post(url_step1, data=json.dumps(payload_step1), headers=BASEDLABS_HEADERS); response_step1.raise_for_status()
        upload_data = response_step1.json()
        signed_url, cdn_url = upload_data.get("signedUrl"), upload_data.get("cdnUrl")
        if not signed_url: return None
        SESSION.put(signed_url, data=image_data, headers={'Content-Type': "image/jpeg"}).raise_for_status()
        return cdn_url
    except requests.exceptions.RequestException as e: print(f"حدث خطأ أثناء رفع الصورة: {e}"); return None

def start_image_editing_job(uploaded_image_url, prompt):
    url_generate = "https://www.basedlabs.ai/api/generate/image-to-image"
    payload_generate ={ "prompt": prompt, "image_urls": [uploaded_image_url], "strength": 0.95, "num_outputs": 1, "width": 1024, "height": 1024, "guidance_scale": 7.5, "num_inference_steps": 50, "selectedModel": { "id": 133, "versionInfo": { "modelPath": "fal-ai/nano-banana/edit"}}}
    try:
        response = SESSION.post(url_generate, data=json.dumps(payload_generate), headers=BASEDLABS_HEADERS); response.raise_for_status()
        return response.json().get("jobId")
    except requests.exceptions.RequestException as e: print(f"حدث خطأ أثناء بدء مهمة التعديل: {e}"); return None

def poll_for_editing_result(job_id):
    url_poll = f"https://www.basedlabs.ai/api/generate/image-to-image?jobId={job_id}"
    for _ in range(30):
        try:
            response = SESSION.get(url_poll, headers=BASEDLABS_HEADERS); response.raise_for_status()
            data = response.json(); status = data.get("status")
            if status == "COMPLETED":
                final_images = data.get("outputs", [])
                return final_images[0] if final_images else None
            elif status in ["FAILED", "ERROR"]: return None
            time.sleep(5)
        except requests.exceptions.RequestException as e: print(f"حدث خطأ أثناء المتابعة: {e}"); return None
    return None

# --- [مُحسَّن] خدمات الفيديو العامة والخاصة ---
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
        if not all([request_id, history_id]): return None
        return {"request_id": request_id, "history_id": history_id}
    except Exception as e:
        print(f"Video generation start failed: {e}"); return None

# --- دوال خاصة بكل موديل ---

def start_veo_text_to_video_job(prompt):
    print("Starting VEO TEXT-TO-VIDEO generation...")
    # ملاحظة: لا يوجد payload رسمي لـ VEO text-to-video، سنستخدم sora كبديل مؤقت
    payload = { "prompt": prompt,    "selectedModel": {
                "id": 84,
                "label": "Veo3",
                "purpose": "Video",
                "type": "Checkpoint",
                "description": "veo 3 is effectively acting as a camera operator, set designer, and editor that gets your script – following stage directions about characters and camera angles with newfound accuracy.",
                "baseModel": "Veo3",
                "versionInfo": {
                    "id": 97,
                    "index": None,
                    "name": "1.0 Text",
                    "description": None,
                    "modelId": 84,
                    "trainedWords": [],
                    "steps": None,
                    "epochs": None,
                    "clipSkip": None,
                    "vaeId": None,
                    "createdAt": "2025-06-18T06:40:31.421Z",
                    "updatedAt": "2025-09-09T03:16:59.081Z",
                    "publishedAt": None,
                    "status": "Published",
                    "trainingStatus": None,
                    "trainingDetails": None,
                    "inaccurate": False,
                    "baseModel": "Veo3",
                    "baseModelType": None,
                    "meta": {},
                    "earlyAccessTimeFrame": 0,
                    "requireAuth": False,
                    "settings": None,
                    "availability": "Public",
                    "creditCost": 300,
                    "creditCostConfig": {
                        "8": 300
                    },
                    "isActive": True,
                    "modelPath": "fal-ai/veo3",
                    "baseModelSetType": None,
                    "type": "TextToVideo",
                    "uploadType": "Created",
                    "files": []
                },
                "checkpoint": ""
            },
            "width": 1280,
            "height": 720,
            "duration": 5,
            "aspect_ratio": "16:9",
            "mediaId": "cmfu0511e0468ypgv5rab1h67",
            "fps": 24,
            "advanced": {
                "videoDuration": 5,
                "videoAspectRatio": "16:9"
            }
        }
    return _start_video_job("https://www.basedlabs.ai/api/generate/text-to-video", payload)

def start_veo_image_to_video_job(prompt, image_url, media_id):
    print("Starting VEO IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt, "image_url": image_url, "model": {
    "id": 84,
    "label": "Veo3",
    "purpose": "Video",
    "type": "Checkpoint",
    "description": "veo 3 is effectively acting as a camera operator, set designer, and editor that gets your script – following stage directions about characters and camera angles with newfound accuracy.",
    "baseModel": "Veo3",
    "versionInfo": {
      "id": 144,
      "index": None,
      "name": "1.0 Image",
      "description": None,
      "modelId": 84,
      "trainedWords": [],
      "steps": None,
      "epochs": None,
      "clipSkip": None,
      "vaeId": None,
      "createdAt": "2025-08-02T02:10:24.730Z",
      "updatedAt": "2025-09-09T03:15:45.253Z",
      "publishedAt": None,
      "status": "Published",
      "trainingStatus": None,
      "trainingDetails": None,
      "inaccurate": False,
      "baseModel": "Veo3",
      "baseModelType": None,
      "meta": {},
      "earlyAccessTimeFrame": 0,
      "requireAuth": False,
      "settings": None,
      "availability": "Public",
      "creditCost": 300,
      "creditCostConfig": {
        "8": 300
      },
      "isActive": True,
      "modelPath": "fal-ai/veo3/image-to-video",
      "baseModelSetType": None,
      "type": "ImageToVideo",
      "uploadType": "Created",
      "files": []
    },
    "checkpoint": "",
    "version": "1.0 Image"
  },
  "width": 1024,
  "height": 1024,
  "duration": 8,
  "mediaId": "cmgfopat300laz6e9n9h4uxja",
  "sourceMedia": image_url,
  "motion_bucket_id": 60,
  "generate_audio": True,
  "resolution": "1080p",
  "aspect_ratio": "auto"
}
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def start_sora_text_to_video_job(prompt):
    print("Starting SORA TEXT-TO-VIDEO generation...")
    payload = {"prompt": prompt,"selectedModel": {"id": 136,"label": "Sora","purpose": "Video","type": "Checkpoint","description": "This video generation model is more physically accurate, realistic, and more controllable than prior systems. It also features synchronized dialogue and sound effects.","baseModel": "sora","versionInfo": {"id": 169,"name": "2","modelId": 136,"createdAt": "2025-10-06T20:58:42.562Z","updatedAt": "2025-10-06T21:52:35.411Z","status": "Published","baseModel": "sora","creditCost": 40,"creditCostConfig": {"4": 40,"8": 80,"12": 120},"isActive": True,"modelPath": "fal-ai/sora-2/text-to-video","type": "TextToVideo"},"checkpoint": ""},"width": 1280,"height": 720,"duration": 12,"aspect_ratio": "16:9","resolution": "720p","mediaId": "cmh8pnlhu06ne0rfh6sw7zyd9","fps": 24,"advanced": {"videoDuration": 12,"videoAspectRatio": "16:9"}}
    return _start_video_job("https://www.basedlabs.ai/api/generate/text-to-video", payload)

def start_sora_image_to_video_job(prompt, image_url, media_id):
    print("Starting SORA IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt,"image_url": image_url,  "model": {
    "id": 136,
    "label": "Sora",
    "purpose": "Video",
    "type": "Checkpoint",
    "description": "This video generation model is more physically accurate, realistic, and more controllable than prior systems. It also features synchronized dialogue and sound effects.",
    "baseModel": "sora",
    "versionInfo": {
      "id": 170,
      "index": None,
      "name": "2",
      "description": None,
      "modelId": 136,
      "trainedWords": [],
      "steps": None,
      "epochs": None,
      "clipSkip": None,
      "vaeId": None,
      "createdAt": "2025-10-06T21:00:59.007Z",
      "updatedAt": "2025-10-06T21:52:44.257Z",
      "publishedAt": None,
      "status": "Published",
      "trainingStatus": None,
      "trainingDetails": None,
      "inaccurate": False,
      "baseModel": "sora",
      "baseModelType": None,
      "meta": {},
      "earlyAccessTimeFrame": 0,
      "requireAuth": False,
      "settings": None,
      "availability": "Public",
      "creditCost": 40,
      "creditCostConfig": {
        "4": 40,
        "8": 80,
        "12": 120
      },
      "isActive": True,
      "modelPath": "fal-ai/sora-2/image-to-video",
      "baseModelSetType": None,
      "type": "ImageToVideo",
      "uploadType": "Created",
      "isDefault": False,
      "autoUpscale": False,
      "files": []
    },
    "checkpoint": ""
  },
  "width": 1024,
  "height": 1024,
  "duration": 12,
  "mediaId": "cmhdek3if03l6yifsr2b2athb",
  "sourceMedia": image_url,
  "motion_bucket_id": 60,
  "generate_audio": True,
  "resolution": "720p",
  "aspect_ratio": "auto"
}
    return _start_video_job("https://www.basedlabs.ai/api/generate/video", payload)

def start_kling_image_to_video_job(prompt, image_url, media_id):
    print("Starting KLING IMAGE-TO-VIDEO generation...")
    payload = {"prompt": prompt,"image_url": image_url,  "model": {
    "id": 118,
    "label": "Kling",
    "purpose": "Video",
    "type": "Checkpoint",
    "description": "Kling model for video generation",
    "baseModel": "Kling",
    "versionInfo": {
      "id": 167,
      "index": None,
      "name": "2.5 Turbo",
      "description": None,
      "modelId": 118,
      "trainedWords": [],
      "steps": None,
      "epochs": None,
      "clipSkip": None,
      "vaeId": None,
      "createdAt": "2025-09-23T21:57:59.791Z",
      "updatedAt": "2025-09-23T21:58:40.950Z",
      "publishedAt": None,
      "status": "Published",
      "trainingStatus": None,
      "trainingDetails": None,
      "inaccurate": False,
      "baseModel": "Kling",
      "baseModelType": None,
      "meta": {},
      "earlyAccessTimeFrame": 0,
      "requireAuth": False,
      "settings": None,
      "availability": "Public",
      "creditCost": 50,
      "creditCostConfig": {
        "5": 50,
        "10": 100
      },
      "isActive": True,
      "modelPath": "fal-ai/kling-video/v2.5-turbo/pro/image-to-video",
      "baseModelSetType": None,
      "type": "ImageToVideo",
      "uploadType": "Created",
      "isDefault": False,
      "autoUpscale": False,
      "files": []
    },
    "checkpoint": ""
  },
  "width": 447,
  "height": 447,
  "duration": 10,
  "mediaId": "cmh8pnlhu06ne0rfh6sw7zyd9",
  "sourceMedia": image_url,
  "motion_bucket_id": 60,
  "generate_audio": True,
  "resolution": "720p",
  "aspect_ratio": "auto"
}
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
                return None
            time.sleep(5)
        except requests.exceptions.RequestException as e:
            print(f"Polling failed: {e}"); return None
    print("Polling timed out."); return None
