from openai import OpenAI


class GPTWrapper:
    def __init__(self, api_key=None):
        self.__client = OpenAI(api_key='')
        if api_key:
            self.set_api(api_key)

    def set_api(self, api_key):
        self.__api_key = api_key
        self.__client.api_key = api_key

    def get_profile_image(self, sex, ethnicity, age):
        image_data = ''
        try:
            text = f"""
    Photorealistic
    {sex},
    {ethnicity},
    {age} years old,
    Close-up portrait of a person for an ID card, neutral background, professional attire, clear facial features, eye-level shot, soft lighting to highlight details without harsh shadows, high resolution for print quality --ar 1:1
    """
            response = self.__client.images.generate(
                model="dall-e-3",
                prompt=text,
                n=1,
                style="vivid",
                size="1024x1024",
                response_format="b64_json",
            )
            for _ in response.data:
                image_data = _.b64_json
            return image_data
        except Exception as e:
            print(e)
            raise Exception(e)