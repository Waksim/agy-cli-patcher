# agy CLI patcher

Builds an ad-hoc signed copy of one Google-signed Antigravity CLI `1.5.3` build for Apple Silicon. The patch changes two bytes in the protobuf descriptor for `ineligible_tiers` before re-signing. The CLI continues to use its standard proxy settings.

The script checks the input SHA-256 and Google code signature, requires exactly one matching descriptor, and creates a new executable. It refuses to overwrite an existing output.

## Build and test

Use native Python 3 on Apple Silicon macOS. Pass the original Google-signed executable as the input.

```sh
python3 patch_agy.py /path/to/original/agy ./agy-patched
AGY_CLI_DISABLE_AUTO_UPDATE=true ./agy-patched --model gemini-4-argon-high -p 'Reply with exactly OK.'
```

## Install and roll back

Keep the Google-signed binary as a backup. To install, create the patched copy beside the installed `agy` and rename it over that file. To roll back, copy the signed backup to a fresh file in the same directory and rename it over the patched binary. Future CLI updates may replace the patch.

The general binary-patching approach was inspired by [Antigravity Unlocker](https://github.com/confeden/Antigravity/releases/tag/v2.29.0).
