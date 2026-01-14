import torch
import torch.serialization
import functools

print("DEBUG: Applying torch.load patch for weights_only=False")

_original_torch_load = torch.load
_original_serialization_load = torch.serialization.load

@functools.wraps(_original_torch_load)
def _patched_load(*args, **kwargs):
    # Force weights_only=False if not specified
    if 'weights_only' not in kwargs:
        kwargs['weights_only'] = False
    return _original_torch_load(*args, **kwargs)

# Patch both locations to cover all bases
torch.load = _patched_load
torch.serialization.load = _patched_load

print("DEBUG: torch.load patched successfully")
