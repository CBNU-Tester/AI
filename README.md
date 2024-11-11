# AI
데이터 생성 및 전처리 및 모델 학습 코드 최종 업로드

main.py - url, search_term 에 입력된 정보를 바탕으로 데이터를 생성함

data_extractor.py - 학습데이터 생성을 위한 csv 파일 생성 코드

preprocess_html.py - 모델 입력전 html 코드 전처리

model.py - 사용하는 모델

Make_Dataset.ipynb - data_extractor로 생성한 데이터를 직접 라벨링하고 해당 데이터를 전처리해 학습 데이터를 만드는 과정

model_train.ipynb - Make_Dataset으로 생성된 데이터를 모델에 학습시켜 파라미터를 저장하는 코드

사전학습된 모델 및 토크나이저 : https://drive.google.com/file/d/16zEsgrFyIM0fZZ2HEj9URNNqvrr102_H/view?usp=sharing
파인튜닝된 모델 : https://drive.google.com/file/d/1VmOe7rm8aKYJCVn4Visc87okw94fkiYA/view?usp=sharing


만들어진 모델 파라미터
