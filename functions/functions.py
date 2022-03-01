from constants import ROOT


def load_static(file: str, tags: bool = True) -> str:
    '''Loader for text files to be embedded with Streamlit. Takes path to a `file` as main argument. If `tags` is set to `True`, surrounds the text with script tags (e.g. <style>), else returns just the text.
    '''
    from pathlib import Path

    import constants

    ext = file.split('.')[-1]
    
    with open(list(Path(constants.ROOT).rglob(file))[0]) as f :
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
