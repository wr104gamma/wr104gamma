import tkinter as tk
from tkinter import ttk
import subprocess
from tkinter import messagebox
from textblob import TextBlob
import spacy
from langdetect import detect

# Load the spaCy model
nlp = spacy.load("en_core_web_sm")

def analyze_text():
    text = text_entry.get("1.0", tk.END).strip()  # Retrieve text from text entry widget
    polarity_score = analyze_sentiment(text)
    overall_tone = 'positive' if polarity_score > 0 else 'negative' if polarity_score < 0 else 'neutral'
    spacy_analysis = analyze_with_spacy(text)
    grammatical_errors, spelling_errors = check_spelling_and_grammar(text)
    display_analysis_results(text, overall_tone, polarity_score, spacy_analysis, grammatical_errors, spelling_errors)

def analyze_with_spacy(text):
    doc = nlp(text)
    # Extract relevant information from spaCy analysis
    named_entities = [ent.text for ent in doc.ents]
    nouns = [token.text for token in doc if token.pos_ == "NOUN"]
    verbs = [token.text for token in doc if token.pos_ == "VERB"]
    # You can extract more information as needed
    return named_entities, nouns, verbs

def analyze_sentiment(text):
    # Your code to analyze sentiment goes here
    # For demonstration purposes, let's return a dummy value
    return 0.5

def check_spelling_and_grammar(text):
    # Run hunspell to check spelling and grammar
    process = subprocess.Popen(['hunspell', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate(input=text.encode())
    misspelled_words = output.decode().splitlines()
    # Filter out words from the custom dictionary
    custom_words = set()
    with open("custom_dictionary.txt", "r") as f:
        for line in f:
            custom_words.add(line.strip())
    misspelled_words = [word for word in misspelled_words if word not in custom_words]
    # For demonstration purposes, let's assume all misspelled words are grammatical errors
    return [], misspelled_words

def display_analysis_results(text, overall_tone, polarity_score, spacy_analysis, grammatical_errors, spelling_errors):
    analysis_window = tk.Toplevel()  # Create a new top-level window for displaying results
    analysis_window.title("Analysis Results")
    
    # Create a Text widget with word wrapping, scrollbars, and other configurations
    analysis_text = tk.Text(analysis_window, wrap=tk.WORD, height=20, width=60)
    analysis_text.pack(fill=tk.BOTH, expand=True)
    analysis_text.insert(tk.END, f"Overall Tone: {overall_tone.capitalize()}\n")
    analysis_text.insert(tk.END, f"Polarity Score: {polarity_score:.2f}\n\n")
    analysis_text.insert(tk.END, "Named Entities: {}\n".format(", ".join(spacy_analysis[0])))
    analysis_text.insert(tk.END, "Nouns: {}\n".format(", ".join(spacy_analysis[1])))
    analysis_text.insert(tk.END, "Verbs: {}\n".format(", ".join(spacy_analysis[2])))
    analysis_text.insert(tk.END, "Grammatical Errors: {}\n".format(", ".join(grammatical_errors)))
    analysis_text.insert(tk.END, "Spelling Errors: {}\n".format(", ".join(spelling_errors)))
    
    # Make the Text widget read-only
    analysis_text.config(state=tk.DISABLED)

    # Add scrollbars
    scrollbar = tk.Scrollbar(analysis_window, orient=tk.VERTICAL, command=analysis_text.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    analysis_text.config(yscrollcommand=scrollbar.set)

def update_hunspell():
    # Execute the command to update hunspell
    subprocess.call(['sudo', 'apt', 'upgrade', 'hunspell'])

# FUNCTION TO HIGHLIGHT MISSPELLED WORDS AND BAD WORDS
def highlight_spelling(event=None):
    # Clear existing tags
    text_entry.tag_remove("misspelled", "1.0", tk.END)
    text_entry.tag_remove("bad_word", "1.0", tk.END)

    # Retrieve text from the text entry widget
    text = text_entry.get("1.0", tk.END)

    # Run hunspell to check spelling
    process = subprocess.Popen(['hunspell', '-l'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, _ = process.communicate(input=text.encode())
    misspelled_words = output.decode().splitlines()

    # Filter out words from the custom dictionary
    custom_words = set()
    with open("custom_dictionary.txt", "r") as f:
        for line in f:
            custom_words.add(line.strip())

    misspelled_words = [word for word in misspelled_words if word not in custom_words]

    # Highlight misspelled words
    for word in misspelled_words:
        start_index = "1.0"
        while True:
            start_index = text_entry.search(word, start_index, stopindex=tk.END)
            if not start_index:
                break
            end_index = f"{start_index}+{len(word)}c"
            text_entry.tag_add("misspelled", start_index, end_index)
            start_index = end_index

    # Read bad words from the file
    with open("bad_word_dictionary.txt", "r") as f:
        bad_words = [line.strip() for line in f]

    # Highlight bad words
    for bad_word in bad_words:
        start_index = "1.0"
        while True:
            start_index = text_entry.search(bad_word, start_index, stopindex=tk.END, regexp=True)
            if not start_index:
                break
            end_index = f"{start_index}+{len(bad_word)}c"
            text_entry.tag_add("bad_word", start_index, end_index)
            start_index = end_index

# Function to add word to dictionary
def add_to_dictionary(event=None):
    try:
        word = text_entry.get("sel.first", "sel.last")
        with open("custom_dictionary.txt", "a") as f:
            f.write(word + "\n")
        messagebox.showinfo("Success", f"The word '{word}' has been added to the dictionary!")
    except tk.TclError:
        messagebox.showerror("Error", "No text selected!")

# Function to add bad word to dictionary
def add_bad_word(event=None):
    try:
        word = text_entry.get("sel.first", "sel.last")
        with open("bad_word_dictionary.txt", "a") as f:
            f.write(word + "\n")
        messagebox.showinfo("Success", f"The word '{word}' has been added to the bad word dictionary!")
    except tk.TclError:
        messagebox.showerror("Error", "No text selected!")



# Function to handle right-click event
def right_click(event):
    context_menu.tk_popup(event.x_root, event.y_root)
def select_all(event=None):
    text_entry.tag_add(tk.SEL, "1.0", tk.END)
    text_entry.mark_set(tk.INSERT, "1.0")
    text_entry.see(tk.INSERT)
    return 'break'

def cut(event=None):
    text_entry.event_generate("<<Cut>>")
    return 'break'

def copy(event=None):
    text_entry.event_generate("<<Copy>>")
    return 'break'

def paste(event=None):
    text_entry.event_generate("<<Paste>>")
    return 'break'

# Function to handle right-click-release event
def right_click_release(event):
    right_click_menu.tk_popup(event.x_root, event.y_root)



# Function to handle double-click event

def double_click(event):
    word_start = text_entry.index("@%s,%s wordstart" % (event.x, event.y))
    word_end = text_entry.index("%s wordend" % word_start)
    selected_word = text_entry.get(word_start, word_end)
    context_menu.delete(0, tk.END)  # Clear existing menu
    if selected_word.strip():
        context_menu.add_command(label="Add to Dictionary", command=add_to_dictionary)
        context_menu.add_command(label="Add Bad Word", command=add_bad_word)
    else:
        context_menu.add_command(label="Cut", command=cut)
        context_menu.add_command(label="Copy", command=copy)
        context_menu.add_command(label="Paste", command=paste)
    context_menu.tk_popup(event.x_root, event.y_root)

# GUI setup
root = tk.Tk()
root.title("QPI Analytics 1.0B")

label_instruction = tk.Label(root, text="Enter your text below:")
label_instruction.pack()

text_entry = tk.Text(root, wrap=tk.WORD, width=50, height=10)
text_entry.pack()

# Add tag configuration for misspelled words
text_entry.tag_config("misspelled", background="pink")

# Create a single context menu for both right-click and double-click
context_menu = tk.Menu(root, tearoff=0)
context_menu.add_command(label="Cut", command=cut)
context_menu.add_command(label="Copy", command=copy)
context_menu.add_command(label="Paste", command=paste)
context_menu.add_separator()
context_menu.add_command(label="Select All", command=select_all)

# Function to handle right-click event and double-click event
def handle_click(event):
    word_start = text_entry.index("@%s,%s wordstart" % (event.x, event.y))
    word_end = text_entry.index("%s wordend" % word_start)
    selected_word = text_entry.get(word_start, word_end)
    
    # Clear existing menu
    context_menu.delete(0, tk.END)

    # If a word is selected, add options to add to dictionary or bad word, otherwise add cut, copy, paste, select all
    if selected_word.strip():
        context_menu.add_command(label="Add to Dictionary", command=add_to_dictionary)
        context_menu.add_command(label="Add Bad Word", command=add_bad_word)
    else:
        context_menu.add_command(label="Cut", command=cut)
        context_menu.add_command(label="Copy", command=copy)
        context_menu.add_command(label="Paste", command=paste)
        context_menu.add_separator()  # Add a separator between the existing options and the new ones
        context_menu.add_command(label="Select All", command=select_all)

    # Display the context menu at the clicked location
    context_menu.tk_popup(event.x_root, event.y_root)

# Bind right-click event and double-click event to the text entry widget
text_entry.bind("<ButtonRelease-3>", handle_click)
text_entry.bind("<Double-1>", handle_click)


# Advanced analysis checkboxes
frame = ttk.Frame(root)
frame.pack(pady=10)

check_pos_tagging = ttk.Checkbutton(frame, text="Part-of-Speech Tagging")
check_dependency_parsing = ttk.Checkbutton(frame, text="Dependency Parsing")
check_entity_recognition = ttk.Checkbutton(frame, text="Entity Recognition")
check_aspect_based_sentiment = ttk.Checkbutton(frame, text="Aspect-Based Sentiment Analysis")
check_text_classification = ttk.Checkbutton(frame, text="Text Classification")
check_language_detection = ttk.Checkbutton(frame, text="Language Detection")
check_coreference_resolution = ttk.Checkbutton(frame, text="Coreference Resolution")
check_named_entity_disambiguation = ttk.Checkbutton(frame, text="Named Entity Disambiguation")
check_word_embeddings = ttk.Checkbutton(frame, text="Word Embeddings")
check_topic_modeling = ttk.Checkbutton(frame, text="Topic Modeling")

check_pos_tagging.grid(row=0, column=0, sticky="w")
check_dependency_parsing.grid(row=1, column=0, sticky="w")
check_entity_recognition.grid(row=2, column=0, sticky="w")
check_aspect_based_sentiment.grid(row=3, column=0, sticky="w")
check_text_classification.grid(row=4, column=0, sticky="w")
check_language_detection.grid(row=5, column=0, sticky="w")
check_coreference_resolution.grid(row=6, column=0, sticky="w")
check_named_entity_disambiguation.grid(row=7, column=0, sticky="w")
check_word_embeddings.grid(row=8, column=0, sticky="w")
check_topic_modeling.grid(row=9, column=0, sticky="w")

analyze_button = tk.Button(root, text="Analyze Text", command=analyze_text)
analyze_button.pack()

update_button = tk.Button(root, text="Update Spelling", command=update_hunspell)
update_button.pack()

# Bind the highlight_spelling function to the <KeyRelease> event
text_entry.bind("<KeyRelease>", highlight_spelling)

root.protocol("WM_DELETE_WINDOW", root.quit)
root.mainloop()  # This line should be at the end of your code
