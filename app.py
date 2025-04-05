from flask import Flask, jsonify
from flask_cors import CORS
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load dataset
file_path = "stackoverflow_questions.csv"
df = pd.read_csv(file_path)

# Convert 'Upload Time' to datetime
df['Upload Time'] = pd.to_datetime(df['Upload Time'], errors='coerce')

# Extract year
df['Year'] = df['Upload Time'].dt.year

# Filter
df_filtered = df[df['Year'].isin([2023, 2024, 2025])]

def get_top_tags(df, top_n=10):
    tag_counts = df['Tag'].value_counts().nlargest(top_n)
    total = tag_counts.sum()
    return (tag_counts / total * 100).to_dict()

@app.route('/')
def home():
    return jsonify({"message": "API is running", "try": "/data"})

@app.route('/data', methods=['GET'])
def get_data():
    yearly_data = {
        year: get_top_tags(df_filtered[df_filtered['Year'] == year])
        for year in [2023, 2024, 2025]
    }
    all_tags = set(tag for year_data in yearly_data.values() for tag in year_data.keys())
    top_tags_overall = sorted(
        all_tags,
        key=lambda tag: sum(yearly_data[year].get(tag, 0) for year in yearly_data),
        reverse=True
    )[:10]
    filtered_data = {
        year: {tag: yearly_data[year].get(tag, 0) for tag in top_tags_overall}
        for year in yearly_data
    }
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
