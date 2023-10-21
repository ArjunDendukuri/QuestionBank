py -m venv env
%~dp0\env\Scripts\activate.bat
py -m pip install PyMuPDF Pillow urllib3
git clone https://github.com/ArjunDendukuri/QuestionBank --branch master --single-branch