
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import glob
import re
import os
import numpy as np
import sys
import PyPDF2 
import chardet

# Download the 'stopwords' dataset
nltk.download('stopwords')

# Inisialisasi stopwords untuk Bahasa Indonesia dan Bahasa Inggris
Stopwords = set(stopwords.words('indonesian')).union(set(stopwords.words('english')))


# Fungsi untuk membaca file
def read_file(file_path):
  with open(file_path, 'rb') as f:
    return f.read()

# Fungsi untuk membaca file PDF
def read_pdf(file_path):
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                text += page.extract_text() or ""
    except Exception as e:
        print(f"Error reading PDF file {file_path}: {e}")
    return text

# Fungsi untuk membaca file teks dengan mendeteksi encoding
def read_text_file(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read()
        result = chardet.detect(raw_data)
        encoding = result['encoding']

    with open(file_path, "r", encoding=encoding, errors="ignore") as file:
        text = file.read()
    return text

# Fungsi untuk menemukan semua kata unik dan frekuensinya
def finding_all_unique_words_and_freq(words):
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1
    return word_freq

# Fungsi untuk menghapus karakter khusus
def remove_special_characters(text):
    regex = re.compile(r'[^a-zA-Z0-9\s]')
    text_returned = re.sub(regex, '', text)
    return text_returned

# Mencari set kata unik dari semua dokumen
all_words = []
dict_global = {}
file_folder = 'data/*'
idx = 1
files_with_index = {}

for file in glob.glob(file_folder):
    print(f"Processing: {file}")
    text = read_file(file)
    text = remove_special_characters(text)
    text = re.sub(r'\d', '', text)  # Menghapus angka
    words = word_tokenize(text)
    words = [word.lower() for word in words if len(word) > 1 and word not in Stopwords]
    dict_global.update(finding_all_unique_words_and_freq(words))
    files_with_index[idx] = os.path.basename(file)
    idx += 1

unique_words_all = set(dict_global.keys())

# Mendefinisikan linked list
class Node:
    def __init__(self, docId, freq=None):
        self.freq = freq
        self.doc = docId
        self.nextval = None

class SlinkedList:
    def __init__(self, head=None):
        self.head = head

# Membuat linked list untuk setiap kata
linked_list_data = {}
for word in unique_words_all:
    linked_list_data[word] = SlinkedList()

idx = 1
for file in glob.glob(file_folder):
    text = read_file(file)
    text = remove_special_characters(text)
    text = re.sub(r'\d', '', text)  # Menghapus angka
    words = word_tokenize(text)
    words = [word.lower() for word in words if len(word) > 1 and word not in Stopwords]
    word_freq_in_doc = finding_all_unique_words_and_freq(words)

    for word in word_freq_in_doc.keys():
        linked_list = linked_list_data[word].head
        new_node = Node(idx, word_freq_in_doc[word])
        if linked_list is None:
            linked_list_data[word].head = new_node
        else:
            while linked_list.nextval:
                linked_list = linked_list.nextval
            linked_list.nextval = new_node
    idx += 1

# Proses query dan output
query = input('Enter your query: ')
query = word_tokenize(query)
connecting_words = []
different_words = []

for word in query:
    if word.lower() not in ["and", "or", "not"]:
        different_words.append(word.lower())
    else:
        connecting_words.append(word.lower())

print("Connecting Words:", connecting_words)

total_files = len(files_with_index)
zeroes_and_ones_of_all_words = []

for word in different_words:
    if word in unique_words_all:
        zeroes_and_ones = [0] * total_files
        linkedlist = linked_list_data[word].head
        while linkedlist:
            zeroes_and_ones[linkedlist.doc - 1] = 1
            linkedlist = linkedlist.nextval
        zeroes_and_ones_of_all_words.append(zeroes_and_ones)
    else:
        print(f"{word} not found, ignoring this word.")
        continue

# Operasi bitwise berdasarkan kata penghubung
for word in connecting_words:
    if len(zeroes_and_ones_of_all_words) < 2:
        break
    word_list1 = zeroes_and_ones_of_all_words.pop(0)
    word_list2 = zeroes_and_ones_of_all_words.pop(0)

    if word == "and":
        bitwise_op = [w1 & w2 for w1, w2 in zip(word_list1, word_list2)]
    elif word == "or":
        bitwise_op = [w1 | w2 for w1, w2 in zip(word_list1, word_list2)]
    elif word == "not":
        bitwise_op = [not w2 for w2 in word_list2]
        bitwise_op = [int(b == True) for b in bitwise_op]
        bitwise_op = [w1 & b for w1, b in zip(word_list1, bitwise_op)]

    zeroes_and_ones_of_all_words.insert(0, bitwise_op)

# Menyusun daftar file berdasarkan hasil query
files = []
if zeroes_and_ones_of_all_words:
    lis = zeroes_and_ones_of_all_words[0]
    cnt = 1
    for index in lis:
        if index == 1:
            files.append(files_with_index[cnt])
        cnt += 1

print("Files Matching Query:", files)

'''
Query = pohon and kenapa or hasil
Dari hasil eksekusi program, dapat disimpulkan bahwa query pencarian yang
diajukan adalah "pohon and kenapa or hasil." Maksud dari query ini adalah untuk
menemukan dokumen yang mengandung kata "pohon" dan "kenapa", atau dokumen yang
mengandung kata "hasil. Namun, program tidak menemukan kata "kenapa" dalam
dokumen yang diproses. Oleh karena itu, program mengabaikan kata tersebut dan
melanjutkan pencarian dengan hanya mempertimbangkan kata "pohon" dan "hasil."
Setelah memproses semua file yang ada, program menemukan bahwa ketiga dokumen
yang dianalisis (DECISION_TREE.pdf, Konsep_Pohon_Keputusan.pdf, dan
Pohon_keputusan_pptx.pdf) mengandung kata "pohon" atau "hasil."
Artinya, semua file tersebut relevan dengan query yang diajukan,
karena setidaknya mengandung salah satu kata yang dicari.
'''