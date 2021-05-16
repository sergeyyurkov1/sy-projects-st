import os

def load_static(file, tags=True) :
    '''Loader for text files to be embedded with Streamlit
    Takes path to a `file` as main argument
    If `tags` is set to True, surrounds the text with script tags, else returns just text
    '''
    ext = file.split('.')[-1]
    
    with open( os.path.join( os.path.dirname(__file__), file ) ) as f :
        static_file = f.read()
    
    if tags == True :
        if ext == "js" :
            return f"<script>{static_file}</script>"
        elif ext == "css" :
            return f"<style>{static_file}</style>"
        elif ext == "html" :
            return static_file
        else :
            return ""
    elif tags == False :
         return static_file
