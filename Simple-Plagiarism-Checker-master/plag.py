from flask import Flask, request, render_template
import re
import math
import os
import time

app = Flask(__name__)

@app.route("/")
def loadPage():
    return render_template('index.html', query="")

@app.route("/", methods=['POST'])
def cosineSimilarity():
    # Record the start time
    start_time = time.time()

    try:
        universalSetOfUniqueWords = set()
        matchPercentages = {}

        # Input Query Processing
        inputQuery = request.form['query']
        lowercaseQuery = inputQuery.lower()
        queryWordList = re.sub(r"[^\w]", " ", lowercaseQuery).split()

        # Add query words to the universal set
        universalSetOfUniqueWords.update(queryWordList)

        # Read all database files from 'plagdb' folder
        folder_path = "plagdb"
        databaseFiles = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]

        # Process each database file
        for file_path in databaseFiles:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as fd:
                databaseContent = fd.read().lower()

            databaseContent = cleanText(databaseContent)

            databaseWordList = re.sub(r"[^\w]", " ", databaseContent).split()
            universalSetOfUniqueWords.update(databaseWordList)

            # Term Frequency calculation
            queryTF = [queryWordList.count(word) for word in universalSetOfUniqueWords]
            databaseTF = [databaseWordList.count(word) for word in universalSetOfUniqueWords]

            # Cosine Similarity Calculation
            dotProduct = sum(q * d for q, d in zip(queryTF, databaseTF))
            queryVectorMagnitude = math.sqrt(sum(q ** 2 for q in queryTF))
            databaseVectorMagnitude = math.sqrt(sum(d ** 2 for d in databaseTF))

            # Avoid division by zero
            if queryVectorMagnitude == 0 or databaseVectorMagnitude == 0:
                matchPercentage = 0
            else:
                matchPercentage = (dotProduct / (queryVectorMagnitude * databaseVectorMagnitude)) * 100

            # Store results
            matchPercentages[file_path] = matchPercentage

        # Create output summary ordered by match percentage
        output = "\n".join(
            [f"{percent:.2f} % \t\t: {os.path.basename(file)}" for file, percent in sorted(matchPercentages.items(), key=lambda x: x[1], reverse=True)]
        )


        elapsed_time = round((time.time()) - start_time, 3)
        return render_template('index.html', query=inputQuery, output=output, resulttime=elapsed_time)
    except Exception as e:
        output = f"Error: {str(e)}. Please Enter Valid Data."
        elapsed_time = round((time.time()) - start_time, 3)
        return render_template('index.html', query=request.form.get('query', ""), output=output, resulttime=elapsed_time)

def cleanText(text):
    """
    Cleans the input text by:
    - Removing multiple spaces.
    - Removing multiple newlines.
    - Stripping leading and trailing whitespace.
    """
    text = re.sub(r'\s+', ' ', text)  # Remove multiple spaces
    text = re.sub(r'\n+', '\n', text)  # Remove multiple newlines
    text = text.strip()  # Strip leading and trailing whitespace
    return text

if __name__ == "__main__":
    app.run(debug=True)


