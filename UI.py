import streamlit as st
from pathlib import Path
from Main import *
import itertools
import os
import time
from streamlit.script_runner import RerunException

@st.cache(show_spinner=False)
def load(search):
    return  init_all(search)

def paginator(label, results, docs_per_page=10):    
    location = location = st.sidebar.empty()
    results = list(results)
    n_pages = len(results)
    n_pages = (len(results) - 1) // docs_per_page + 1
    page_format_func = lambda i: "Page %s" % i
    page_number = location.selectbox(label, range(n_pages), format_func=page_format_func)
    try:
        min_index = page_number * docs_per_page
        max_index = min_index + docs_per_page
    except:
        min_index =0
        max_index=0
    return itertools.islice(enumerate(results), min_index, max_index)

def show_paginator():
    corpus = st.session_state.utils_load[0]
    for i, doc in paginator(str(len(st.session_state.current_results))+' Files found', st.session_state.current_results):
        st.write('%s. **%s**' % (i, corpus[doc][0]))
        st.write(' **%s**  ....' % corpus[doc][1][:300])

def find(search):
    utils_load = st.session_state.utils_load
    results=resolve_query(search,utils_load[2],utils_load[3],len(utils_load[1]),utils_load[4])
    if len(results)>0:
        st.session_state.current_query = search
        st.session_state.current_results = results

def change_path(path):
    if Path.exists(Path(path)):
        st.session_state.current_path = path
        with st.spinner('Loading files, it could take a few minutes'):
            st.session_state.utils_load = load(path)
        st.success('Done')                        
        st.session_state.show_form = False
        st.session_state.current_query = ""
        st.session_state.current_results = []
    else:
        st.error('Path not found or not valid')
        time.sleep(1)
    

def show_form():
    st.session_state.show_form = True



st.title('Information Retrieval System')

if 'current_path' not in st.session_state:
    st.session_state.current_path = os.getcwd().replace(os.sep,'/')+'/Test_Collections/Cranfield'
if 'utils_load' not in st.session_state:
    st.session_state.utils_load = load(st.session_state.current_path)
if 'current_query' not in st.session_state:
    st.session_state.current_query = ""
if 'current_results' not in st.session_state:
    st.session_state.current_results = {}
if 'show_form' not in st.session_state:
    st.session_state.show_form = False
if st.session_state.show_form:
    load_input = st.text_input('Current Folder',value=st.session_state.current_path)
    change_button = st.button('Change')
    if change_button:
        change_path(load_input)
        raise RerunException(st.script_request_queue.RerunData(None))
else:
    search = st.text_input('Input your query',value=st.session_state.current_query)
    if st.button('Search'):
        find(search)
    if st.button('Change Folder'):
        show_form()
        raise RerunException(st.script_request_queue.RerunData(None))
    
    if len(search)>1 : 
        show_paginator()

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


