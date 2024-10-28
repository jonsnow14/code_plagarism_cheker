import openai
import requests
import numpy as np
import faiss
from bs4 import BeautifulSoup

# Set your OpenAI API key
openai.api_key = 'your-openai-api-key-here'  # Replace with your actual API key

# Set your API tokens and URLs
github_token = 'your-github-token-here'  # Replace with your GitHub token
gitlab_token = 'your-gitlab-token-here'  # Replace with your GitLab token
bitbucket_username = 'your-bitbucket-username'
bitbucket_app_password = 'your-bitbucket-app-password'  # Create an app password for Bitbucket
github_api_url = 'https://api.github.com/search/code'
gitlab_api_url = 'https://gitlab.com/api/v4/projects'
bitbucket_api_url = 'https://api.bitbucket.org/2.0/repositories'

# Google Custom Search API details
google_api_key = 'your-google-api-key-here'  # Replace with your Google API key
google_cse_id = 'your-custom-search-engine-id'  # Replace with your CSE ID
google_search_url = 'https://www.googleapis.com/customsearch/v1'

# Function to generate embeddings for a code snippet
def get_code_embedding(code_snippet):
    response = openai.Embedding.create(
        input=code_snippet,
        model="text-embedding-ada-002"  # Use an appropriate embedding model
    )
    return response['data'][0]['embedding']

# Create a FAISS index for fast similarity search
def create_faiss_index(embeddings):
    dim = len(embeddings[0])  # Dimensionality of the embeddings
    index = faiss.IndexFlatL2(dim)  # L2 distance for similarity
    index.add(np.array(embeddings).astype('float32'))  # Add embeddings to the index
    return index

# Function to search for code on GitHub
def search_github_code(query):
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3.text-match+json',
    }
    params = {'q': query, 'per_page': 10}
    response = requests.get(github_api_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Error fetching data from GitHub:", response.status_code)
        return []

# Function to search for questions on Stack Overflow
def search_stackoverflow_code(query):
    params = {
        'order': 'desc',
        'sort': 'activity',
        'intitle': query,
        'site': 'stackoverflow',
        'pagesize': 10
    }
    response = requests.get('https://api.stackexchange.com/2.3/search', params=params)
    
    if response.status_code == 200:
        return response.json()['items']
    else:
        print("Error fetching data from Stack Overflow:", response.status_code)
        return []

# Function to search for code on GitLab
def search_gitlab_code(query):
    params = {'search': query, 'per_page': 10}
    response = requests.get(f"{gitlab_api_url}/search", headers={'PRIVATE-TOKEN': gitlab_token}, params=params)
    
    if response.status_code == 200:
        return response.json()
    else:
        print("Error fetching data from GitLab:", response.status_code)
        return []

# Function to search for code on Bitbucket
def search_bitbucket_code(query):
    response = requests.get(f"{bitbucket_api_url}?q={query}", auth=(bitbucket_username, bitbucket_app_password))
    
    if response.status_code == 200:
        return response.json()['values']
    else:
        print("Error fetching data from Bitbucket:", response.status_code)
        return []

# Function to search for discussions around generated code on the internet
def search_generated_code_discussions(query):
    params = {
        'key': google_api_key,
        'cx': google_cse_id,
        'q': query,
        'num': 10  # Number of results to return
    }
    response = requests.get(google_search_url, params=params)
    
    if response.status_code == 200:
        return response.json().get('items', [])
    else:
        print("Error fetching data from Google Search:", response.status_code)
        return []

# Function to check for code similarity using FAISS
def check_code_similarity(code_snippet, faiss_index):
    new_embedding = get_code_embedding(code_snippet)
    new_embedding = np.array([new_embedding]).astype('float32')
    
    distances, indices = faiss_index.search(new_embedding, k=3)  # Get top 3 similar snippets
    return distances, indices

# Search for code on multiple platforms
search_query = "def squares"  # Example search query; modify as needed
github_results = search_github_code(search_query)
stackoverflow_results = search_stackoverflow_code(search_query)
gitlab_results = search_gitlab_code(search_query)
bitbucket_results = search_bitbucket_code(search_query)
generated_code_discussions = search_generated_code_discussions(search_query)

# Generate embeddings for results
stored_embeddings = []
stored_code_snippets = []

# Process GitHub results
for item in github_results:
    code_snippet = item['text_matches'][0]['fragment']  # Extract the relevant code snippet
    stored_code_snippets.append(code_snippet)
    stored_embeddings.append(get_code_embedding(code_snippet))

# Process Stack Overflow results
for item in stackoverflow_results:
    code_snippet = item['body']  # Extract the body from the question
    stored_code_snippets.append(code_snippet)
    stored_embeddings.append(get_code_embedding(code_snippet))

# Process GitLab results
for item in gitlab_results:
    if 'content' in item:  # Assuming the content field contains code
        code_snippet = item['content']  
        stored_code_snippets.append(code_snippet)
        stored_embeddings.append(get_code_embedding(code_snippet))

# Process Bitbucket results
for item in bitbucket_results:
    code_snippet = item['name']  # Adjust based on the actual structure
    stored_code_snippets.append(code_snippet)
    stored_embeddings.append(get_code_embedding(code_snippet))

# Process generated code discussions
for item in generated_code_discussions:
    code_snippet = item.get('snippet', '')  # Extract snippet or relevant part
    stored_code_snippets.append(code_snippet)
    stored_embeddings.append(get_code_embedding(code_snippet))

# Create FAISS index
faiss_index = create_faiss_index(stored_embeddings)

# New code snippet to check
new_code = """
def new_example(n):
    return [x * x for x in range(n)]
"""

# Check similarity
distances, indices = check_code_similarity(new_code, faiss_index)

# Display results
for idx, distance in zip(indices[0], distances[0]):
    print(f"Snippet {idx}: {stored_code_snippets[idx]}")
    print(f"Distance: {distance:.4f} (lower is more similar)\n")
