from io import BytesIO

from PIL import Image
from rembg import remove
from taipy.gui import Gui, State, notify, download

image = None
original_image = None
cleaned_image = None

fixed = False

path_upload = ""

advanced_properties = {
    "alpha_matting_foreground_threshold": 240,
    "alpha_matting_background_threshold": 10,
    "alpha_matting_erode_size": 10,
}


theme = {
    "color_primary": "#F2AA4C",
    "color_background_dark": "#101820",
    "font_family": "Inter",
}


def image_to_bytes(img: Image) -> bytes:
    """Convert an image instance to bytes.

    Args:
        img (Image): image instance

    Returns:
        bytes: image data in bytes
    """
    buffer = BytesIO()
    img.save(buffer, format="PNG")

    return buffer.getvalue()


def remove_background(state: State, id=None, action=None):
    """Perform background removal from image in state.

    Args:
        state (State): Taipy app global context.
    """
    notify(state, "info", "Removing background...")
    fixed_img = remove(
        state.image,
        alpha_matting=True if action is not None else False,
        alpha_matting_foreground_threshold=int(
            state.advanced_properties["alpha_matting_foreground_threshold"]
        ),
        alpha_matting_background_threshold=int(
            state.advanced_properties["alpha_matting_background_threshold"]
        ),
        alpha_matting_erode_size=int(
            state.advanced_properties["alpha_matting_erode_size"]
        ),
    )
    state.cleaned_image = image_to_bytes(fixed_img)
    state.fixed = True
    notify(state, "success", "Background removed!")


def upload_image(state: State):
    """Callback handler when input image has been uploaded.

    Args:
        state (State): Taipy app global context.
    """
    state.image = Image.open(state.path_upload)
    state.original_image = image_to_bytes(state.image)
    state.fixed = False
    remove_background(state)


def download_image(state: State):
    """Callback handler for image download.

    Args:
        state (State): Taipy app global context.
    """
    download(state, content=state.cleaned_image, name="fixed_img.png")


md_page = """<|layout|columns=280px 1fr|class_name=p2|
<|

### Tai<span class="color-primary">Purge</span>

<|{path_upload}|file_selector|extensions=.png,.jpg|label=Upload your image|on_action=upload_image|class_name=d-block mt4|>

<|More Options|expandable|not expanded|class_name=mt2 mb2|

**Foreground Threshold**

<|{advanced_properties.alpha_matting_foreground_threshold}|slider|max=500|>

**Background threshold**

<|{advanced_properties.alpha_matting_background_threshold}|slider|max=50|>

**Erosion size**
<|{advanced_properties.alpha_matting_erode_size}|slider|max=50|>

<|Run with options|button|on_action=remove_background|class_name=plain fullwidth|active={original_image}|>

|>

<|{None}|file_download|label=Download result|on_action=download_image|active={fixed}|>

|>

<|ml6|

### Background **Remover**{: .color-primary}

<|images|layout|columns=1 1|
<col1|card text-center|part|render={original_image}|
### Original Image
<|{original_image}|image|>
|col1>

<col2|card text-center|part|render={fixed}|
### Cleaned Image
<|{cleaned_image}|image|>
|col2>
|images>

|>
"""

if __name__ == "__main__":
    Gui(page=md_page).run(use_reloader=True, stylekit=theme)
