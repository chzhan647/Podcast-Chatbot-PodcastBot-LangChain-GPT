import streamlit as st 
import pandas as pd
import numpy as np
from langchain.utilities import WikipediaAPIWrapper

question_input = st.text_input("Question:")

if question_input:
    keywords = question_input.split()

    wikipedia = WikipediaAPIWrapper()
    context_input = wikipedia.run(' '.join(keywords))

    QA_input = {
        'question': question_input,
        'context': context_input
    }

    res = nlp(QA_input)

    st.text_area("Answer:", res['answer'])
    st.write("Score:", res['score'])