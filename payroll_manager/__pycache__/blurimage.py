import streamlit as st
from PIL import Image, ImageFilter, ImageChops
from transformers import pipeline
import torch
import numpy as np
import logging

# ---------------- LOGGING ----------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------- BACKGROUND BLUR CLASS ----------------
class BackgroundBlur:
    def __init__(self):
        self.device = 0 if torch.cuda.is_available() else -1
        self.model = pipeline(
            "image-segmentation",
            model="nvidia/segformer-b0-finetuned-ade-512-512",
            device=self.device
        )
        logger.info("Person segmentation model loaded")

    def extract_person_mask(self, results):
        """
        Extract and combine all 'person' masks using PIL only
        """
        combined_mask = None

        for item in results:
            if item["label"] == "person":
                mask = item["mask"].convert("L")
                combined_mask = (
                    mask if combined_mask is None
                    else ImageChops.lighter(combined_mask, mask)
                )

        if combined_mask is None:
            return None

        # Smooth edges
        combined_mask = combined_mask.filter(ImageFilter.GaussianBlur(2))
        return combined_mask

    def process_image(self, image, blur_level):
        try:
            results = self.model(image)

            person_mask = self.extract_person_mask(results)
            if person_mask is None:
                return None, "No person detected in image"

            # Blur background
            blurred_bg = image.filter(ImageFilter.GaussianBlur(blur_level))

            # Composite: keep person sharp
            final_image = Image.composite(
                image,        # foreground (sharp person)
                blurred_bg,   # background
                person_mask   # person mask
            )

            return final_image, None

        except Exception as e:
            logger.error(f"Processing error: {e}")
            return None, str(e)

# ---------------- STREAMLIT APP ----------------
def main():
    st.set_page_config(page_title="Background Blur App", layout="wide")

    st.title("Prakriti's Background Blur App")
    st.markdown("Blurs the background while keeping the person sharp.")

    @st.cache_resource
    def load_model():
        return BackgroundBlur()

    with st.spinner("Loading AI model..."):
        processor = load_model()

    uploaded = st.file_uploader("Upload an image", type=["jpg", "png", "jpeg"])

    if uploaded:
        image = Image.open(uploaded).convert("RGB")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Original Image")
            st.image(image, use_column_width=True)

        with col2:
            blur = st.slider("Blur Intensity", 0, 30, 15)

            if st.button("Process Image"):
                with st.spinner("Processing..."):
                    result, error = processor.process_image(image, blur)

                    if error:
                        st.error(error)
                    else:
                        st.image(result, use_column_width=True)

                        import io
                        buf = io.BytesIO()
                        result.save(buf, format="PNG")

                        st.download_button(
                            "Download Image",
                            buf.getvalue(),
                            "background_blur.png",
                            "image/png"
                        )

# ---------------- RUN ----------------
if __name__ == "__main__":
    main()




    

                                            
                                   
            
    
        