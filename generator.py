from itertools import product

# Defining the structure of our data
years = range(2018, 2024)  # From 2018 to 2023
terms = ["May-June", "November"]
papers = ["Paper-1", "Paper-2"]
languages = ["English", "Afrikaans"]
memos = ["Memo-1", "Memo-2"]
memo_language = "English-and-Afrikaans"

# Generate question papers
data = []
for year, term, paper, language in product(years, terms, papers, languages):
    entry = {
        "subject": "Mathematics",
        "type": "Question paper",
        "paper": paper,
        "year": year,
        "term": term,
        "language": language,
        "path": f"{year}/{year}-{term}-Mathematics-{paper}-{language}.pdf"
    }
    data.append(entry)

# Generate memos (in both languages)
for year, term, memo in product(years, terms, memos):
    entry = {
        "subject": "Mathematics",
        "type": "Memorandum",
        "paper": memo,
        "year": year,
        "term": term,
        "language": memo_language,
        "path": f"{year}/{year}-{term}-Mathematics-{memo}-{memo_language}.pdf"
    }
    data.append(entry)

# Displaying sample data to confirm
# data[:10], len(data)  # Show first 10 entries and the total count

print(data)
