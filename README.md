# LeeBlack

## Usages:
```
python poem_generator.py -v -p poem_1_1458.data -n tonal.txt -m model/rnn-theano.npz -k '採藥' '牧童'
```
### Result:
```
暖日眠芳草
鶱修袋諼綖
嵬堂然戀日
三數後看年
```

## Data file format:
```
8
微 風 驚 暮 坐
臨 牖 思 悠 哉
開 門 復 動 竹
疑 是 故 人 來
時 滴 枝 上 露
稍 沾 階 下 苔
何 當 一 入 幌
爲 拂 綠 琴 埃
4
燕 語 如 傷 舊 國 春
宮 花 一 落 已 成 塵
自 從 一 閉 風 光 後
幾 度 飛 來 不 見 人
...
```

## TODO
1. Code cleanup
2. Implement poem with 7 words in a sentence
3. Import more data
4. Implement aclweb.org/anthology/D/D14/D14-1074.pdf
5. Implement phase-based learning
6. Generate using unknown keywords

## References
Code of rnn_theano and rnn_theano_gru from:
https://github.com/dennybritz/rnn-tutorial-rnnlm
https://github.com/dennybritz/rnn-tutorial-gru-lstm

First sentence generated using:
http://www.fit.vutbr.cz/~imikolov/rnnlm/

Poem data from:
http://fanti.dugushici.com

Poem keywords from:
http://cls.hs.yzu.edu.tw/MakePoem/SSHY.htm (詩學含英)

Tonal data from:
https://zh.wikisource.org/zh-hant/%E5%B9%B3%E6%B0%B4%E9%9F%BB (平水韻)
