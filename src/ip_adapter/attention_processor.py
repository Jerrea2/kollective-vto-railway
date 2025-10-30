from diffusers.models.attention_processor import AttnProcessor2_0 as _AttnProcessor2_0

class AttnProcessor2_0(_AttnProcessor2_0):
    pass

class IPAttnProcessor2_0(_AttnProcessor2_0):
    def __init__(self, *args, **kwargs):
        super().__init__()
