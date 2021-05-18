지금 14google(1).tsv가 14meta.tsv와 짝지어지고 이는 pretrained model에 대해서만 벡터화를 한것

14googlecustom.tsv 는 pre trained model을 배제하고 우리의 데이터만 이용해 fasttext로 skipgram을 이용해 training한 형태이며,
14googlepttrain.tsv 는 14metacustompttrain이랑 짝지어져 우리의 데이터를 이용하고 pretrained model을이용해 fasttext로 training한 형태이다.
