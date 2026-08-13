import io
import re

import os

BASE = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE, 'ToxicGuard_V5_2_FocalLoss_Colab.ipynb')

with io.open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace missing quotes around em-dash
new_content = content.replace("'Epoch':—", "'Epoch':'—'")

if content != new_content:
    with io.open(file_path, 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Fixed missing quotes for Epoch.")
else:
    print("No changes made.")
