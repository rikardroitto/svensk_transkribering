#!/usr/bin/env python3
"""
Wrapper script that aggressively patches ALL torch.load variants
BEFORE importing any other modules.
"""

import torch
import torch.serialization
import functools

print("=" * 60)
print("Patching torch.load and ALL internal variants...")
print("=" * 60)

# Get references to the ORIGINAL functions before anyone else can
_orig_load = torch.load
_orig_serialization_load = torch.serialization.load

# Check if _legacy_load exists (older PyTorch)
_orig_legacy_load = getattr(torch.serialization, '_legacy_load', None)

# The key insight: we need to wrap the function and force weights_only=False
def make_patched_load(original_fn, name):
    @functools.wraps(original_fn)
    def patched(*args, **kwargs):
        # Force weights_only=False
        kwargs['weights_only'] = False
        return original_fn(*args, **kwargs)
    print(f"  ✓ Patched: {name}")
    return patched

# Apply patches to ALL known entry points
torch.load = make_patched_load(_orig_load, "torch.load")
torch.serialization.load = make_patched_load(_orig_serialization_load, "torch.serialization.load")

if _orig_legacy_load:
    torch.serialization._legacy_load = make_patched_load(_orig_legacy_load, "torch.serialization._legacy_load")

# Also try to patch the fabric/lightning utility if it exists
try:
    import lightning_fabric.utilities.cloud_io as cloud_io
    if hasattr(cloud_io, '_load'):
        _orig_cloud_load = cloud_io._load
        cloud_io._load = make_patched_load(_orig_cloud_load, "lightning_fabric.utilities.cloud_io._load")
except ImportError:
    pass

print("=" * 60)
print("All patches applied. Starting webapp...")
print("=" * 60)

# Now it's safe to import and run the webapp
if __name__ == "__main__":
    from whisper_diarize.webapp import run
    run(host="127.0.0.1", port=5000)
