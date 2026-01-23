# nsfwcheck

A high-performance wrapper service for NSFW and malicious content detection. This service coordinates checks across multiple specialized engines to provide a unified safety verdict.

## Features
- **Unified API**: Accepts both images and URLs.
- **QR Code Extraction**: Automatically extracts and scans URLs hidden in images.
- **Multi-Engine Integration**:
    - Coordinates with `imagesafe` (Node.js/nsfwjs) for content analysis.
    - Coordinates with `urlsafe` (Python) for link categorization.

## Credits & Attribution
This project stands on the shoulders of gems. Special thanks to:

- **[infinitered/nsfwjs](https://github.com/infinitered/nsfwjs)**: The core library and AI models used for image classification.
- **[andresribeiro/nsfwjs-docker](https://github.com/andresribeiro/nsfwjs-docker)**: For the inspiration and initial Dockerization patterns of the `nsfwjs` engine.

## Quick Start
```bash
make du
```
Then run tests with:
```bash
make test
```
