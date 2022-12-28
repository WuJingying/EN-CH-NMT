# README

机器翻译方法主要有基于实例的机器翻译方法、基于统计的机器翻译方法以及神经机器翻译（Neural Machine Translation，NMT）。NMT通常采用**Encoder-Decoder**结构，实现对变长输入句子的建模。编码器实现对源语言句子的"理解"，形成一个特定维度的浮点数向量，之后解码器根据此向量逐字生成目标语言的翻译结果。

#### 数据

数据集来自 [WMT 2018 Chinese-English track](http://statmt.org/wmt18/translation-task.html) 中的新闻领域中英双语数据集。

##### 分词

本项目使用[sentencepiece](https://link.zhihu.com/?target=https%3A//github.com/google/sentencepiece)[[3\]](https://zhuanlan.zhihu.com/p/347061440#ref_3)实现BPE分词。sentencepiece是一个google开源的自然语言处理工具包，支持bpe、unigram等多种分词方法。其优势在于：bpe、unigram等方法均假设输入文本是已经切分好的，只有这样bpe才能统计词频（通常直接通过空格切分）。但是，汉语、日语等语言的字与字之间并没有空格分隔。

sentencepiece提出，可以将所有字符编码成Unicode码（包括空格），通过训练直接将原始文本（未切分）变为分词后的文本，从而避免了跨语言的问题。

- 工具：[sentencepiece](https://github.com/google/sentencepiece)
- 预处理：`get_corpus.py`抽取train、dev和test中双语语料，分别保存到`./data/corpus.en`和`./data/corpus.ch`中，每行一个句子。
- 训练分词模型：`tokenizer.py`中调用了sentencepiece.SentencePieceTrainer.Train()方法，利用`corpus.en`和`corpus.ch`中的语料训练分词模型，训练完成后会在生成`chn.model`，`chn.vocab`，`eng.model`和`eng.vocab`，其中`.model`和`.vocab`分别为模型文件和对应的词表。

##### 分词结果test

```
input:美国总统特朗普今日抵达夏威夷。
output:['▁美国总统', '特朗普', '今日', '抵达', '夏威夷', '。']
```

注：sentencepiece将每句文本的开头和空格均用 '_' 表示。

##### 数据预处理

- 把原始语料中的中英文句对按照英文句子的长度排序，使得每个batch中的句子长度相近。
- 利用训练好的分词模型分别对中英文句子进行分词，利用词表将其转换为id。
- 在每个 id sequence 的首尾加上起始符和终止符，并将其转换为Tensor。

将上述Tensor输入到transformer-pytorch定义的Batch类中，转换为transformer支持的输入格式（构造decoder的输入输出、attention mask等）。上述代码在data_loader.py文件中。

#### 模型

采用Harvard开源的 [transformer-pytorch]([The Annotated Transformer (harvard.edu)](http://nlp.seas.harvard.edu/2018/04/03/attention.html))。

#### BLEU评测

BLEU即Bilingual Evaluation Understudy，在机器翻译任务中，BLEU非常常见，它主要用于评估模型生成句子（candidate）和实际句子（reference）之间的差异。其具体的计算公式见下式：

<img src="D:\astudy\NLTK\bleu公式.PNG" style="zoom: 50%;" />

其中$p_n$是n-gram修正准确率， $w_n$ 为$\frac 1n$，$c$是机器译文长度，$r$是参考译文长度，$N$通常取为4（和人工评价相关度最高）。

我们的BLEU值计算采用sacrebleu。sacrebleu指出，现有的BLEU计算工具(nltk等)均需要提前进行分词，采取的分词方案不同会导致BLEU计算的结果有较大差异。因此，sacrebleu接收原文本输入，将分词和bleu计算统一进行，提供了更加具有可比性的BLEU分数参考。

分别使用两种optimizer的优化结果评测如下：

| Model | NoamOpt | LabelSmoothing | BLEU-score |
| ----- | ------- | -------------- | ---------- |
| 1     | No      | No             | 24.03      |
| 2     | Yes     | No             | 25.94      |
| 3     | No      | Yes            | 23.84      |

已训练好的当前最优模型在`./experiment/model.pth`中，针对不同的beam_size进行BLEU评测结果如下：

| beam_size  | 2     | 3     | 4     | 5     |
| ---------- | ----- | ----- | ----- | ----- |
| BLEU-score | 26.59 | 26.80 | 26.84 | 26.86 |

#### 单句翻译示例

```
英文句子：
"The near-term policy remedies are clear: raise the minimum wage to a level that will keep a fully employed worker and his or her family out of poverty, and extend the earned-income tax credit to childless workers."

beam_size=3翻译结果：
短期政策方案很清楚:把最低工资提高到充分就业的水平,并扩大向无薪工人发放所得的税收信用。

deepl翻译器翻译结果：
近期的政策补救措施是明确的：将最低工资提高到能够使充分就业的工人及其家庭摆脱贫困的水平，并将收入税收抵免扩大到无子女工人。
```

