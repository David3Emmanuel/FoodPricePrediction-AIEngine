import json
import pandas as pd
from tqdm import tqdm
from transformers import pipeline
from torch.utils.data import Dataset
from typing import Sequence

class ListDataset(Dataset):
    """Simple dataset wrapper for efficient inference."""
    def __init__(self, original_list: Sequence[str]):
        self.original_list = original_list

    def __len__(self):
        return len(self.original_list)

    def __getitem__(self, i):
        return self.original_list[i]

def analyze_sentiment(texts: list[str], model_name: str = "ProsusAI/finbert") -> list[float]:
    """
    Analyzes sentiment of a list of texts using the specified model.
    Returns a list of scores (positive=score, negative=-score, neutral=0.0).
    """
    print(f"Initializing sentiment pipeline: {model_name}")
    nlp = pipeline("text-classification", model=model_name)
    
    print(f"Scoring {len(texts)} articles...")
    dataset = ListDataset(texts)
    results = list(tqdm(nlp(dataset, truncation=True, max_length=512)))
    
    scores = []
    for s in results:
        score = s['score']
        label = s['label']
        if label == 'positive':
            scores.append(float(score))
        elif label == 'negative':
            scores.append(float(-score))
        else:
            scores.append(0.0)
            
    return scores

def process_news_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Standardizes a news DataFrame, runs sentiment analysis, 
    and aggregates to weekly granularity.
    
    Expected columns: 'date', 'title', 'article' (JSON string with 'body')
    """
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])

    def parse_body_json(json_string):
        try:
            return json.loads(json_string).get('body', '')
        except (json.JSONDecodeError, AttributeError):
            return ""

    print("Parsing text data...")
    df['Body_Text'] = df['article'].apply(parse_body_json)
    df['Combined_Text'] = df['title'] + ". " + df['Body_Text'].str[:300]

    # Run sentiment
    df['Sentiment_Score'] = analyze_sentiment(df['Combined_Text'].tolist())

    print("Aggregating to Weekly Data...")
    df['Year'] = df['date'].dt.year
    df['Week'] = df['date'].dt.strftime('%W').astype(int)

    weekly = df.groupby(['Year', 'Week'])['Sentiment_Score'].mean().reset_index()
    weekly.rename(columns={'Sentiment_Score': 'Weekly_Econ_Sentiment_Score'}, inplace=True)
    
    return weekly
