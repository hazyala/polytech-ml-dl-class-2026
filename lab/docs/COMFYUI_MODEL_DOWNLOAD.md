# ComfyUI Model Download Note

ComfyUI checkpoint/model files are intentionally not committed to this repository.
The Stable Diffusion checkpoint used in the old local environment was:

```text
v1-5-pruned-emaonly.safetensors
```

It was previously stored at:

```text
D:\ML_DL_Lab\comfyui_data\models\checkpoints\v1-5-pruned-emaonly.safetensors
```

## Download Source

Use the Hugging Face model repository:

```text
https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5
```

Direct file page:

```text
https://huggingface.co/stable-diffusion-v1-5/stable-diffusion-v1-5/blob/main/v1-5-pruned-emaonly.safetensors
```

The file is about 4.27GB, so it should stay outside Git.

## Where To Put It

For this cleaned repository, use:

```text
D:\ML_DL_Class\lab\comfyui_data\models\checkpoints\v1-5-pruned-emaonly.safetensors
```

For a ComfyUI install inside a container or cloned ComfyUI folder, place checkpoint
files under:

```text
ComfyUI\models\checkpoints
```

## Notes

- `*.safetensors`, `*.ckpt`, `*.pt`, and similar model files are ignored by `.gitignore`.
- Hugging Face may require login or license acceptance before downloading some model files.
- ComfyUI Cloud can be used instead of local model downloads when local GPU/model storage is not needed.
