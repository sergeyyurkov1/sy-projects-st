conda create -n multiapp python=3.7.9

conda activate multiapp

pip install -r requirements.txt
pip install protobuf==3.20.\*

streamlit run app.py
