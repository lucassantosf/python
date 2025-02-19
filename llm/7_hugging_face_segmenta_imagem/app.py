import gradio as gd
from transformers import pipeline
from PIL import Image

# Streamlit
def remove_background(img):
    pipeline_model = pipeline("image-segmentation", model="briaai/RMBG-1.4", trust_remote_code=True)
    mask_pillow = pipeline_model(img, return_mask=True)
    image_pillow = pipeline_model(img)
    return image_pillow

# remove_background("img/image2.jpg")

app = gd.Interface(
    title="Remove Background na Imagem",
    description="Faça upload da imagem para remover o background",
    fn=remove_background,
    inputs=gd.components.Image(type="pil"),
    outputs=gd.components.Image(type="pil", format="png")
)

if __name__ == "__main__":
    app.launch(share=True)