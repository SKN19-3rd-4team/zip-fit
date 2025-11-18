```shell

# 환경 설정
conda create -n zf_back python=3.12

# 필수 설치
pip install fastapi uvicorn "pydantic[email]"
pip install mysql-connector-python aiomysql langchain openai
pip install pydantic-settings

# 실행
uvicorn zip_fit.main:app --reload

```