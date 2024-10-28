# code_plagarism_cheker

# AI Code Similarity Checker

This project implements a code similarity checker that searches for code snippets and discussions about AI-generated code across various platforms, including GitHub, Stack Overflow, GitLab, Bitbucket, and the internet using Google Custom Search API.

## Features

- Searches for code snippets on GitHub, Stack Overflow, GitLab, and Bitbucket.
- Searches for discussions about AI-generated code using Google Custom Search API.
- Computes embeddings for code snippets to find similarities using FAISS.
- Provides a distance metric for evaluating code similarity.

## Requirements

To run this project, you need the following Python packages:

- `openai`
- `requests`
- `numpy`
- `faiss-cpu`
- `beautifulsoup4`

You can install these requirements by running:

```bash
pip install -r requirements.txt
