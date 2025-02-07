# RoBERTa 预训练（Masked Language Modeling）
本项目是 RoBERTa 模型在 Paddle 2.0上的开源实现，包含了数据 tokenization 和预训练代码。本项目旨在用简练清晰的代码完成基本预训练任务（仅 Masked Language Modeling）。该代码易于理解，便于修改和定制。
## 简介
本目录下包含:

utils.py: 数据采样函数 DataCollatorMLM

create_data.py: tokenize 数据（使用 HF datasets 导入和预处理 wikipedia 数据）

run_pretrain.py: 预训练代码

## 数据准备
运行 create_data.py，默认使用 wikipedia corpus 数据，自动下载（约34GB）

```
python create_data.py \
--output_dir wiki \
--dataset_name wikipedia \
--dataset_config_name 20200501.en \
--tokenizer_name roberta-base \
--max_seq_length 512 \
--line_by_line False \
--preprocessing_num_workers 20
```

其中参数释义如下：
- `output_dir` 指示数据 tokenize 后保存的目录。
- `dataset_name` 表示数据名称，默认使用 wikipedia。
- `dataset_config_name` 表示数据参数，默认使用 wikipedia 英文数据。
- `tokenizer_name` 表示 tokenizer 名。
- `max_seq_length` 表示最大序列长度。
- `line_by_line` 表示是否将数据 group 到 max_seq_length，True 则不进行 grouping。
- `preprocessing_num_workers` 表示 worker 数量，亦为 multi-processing 数量。

## 预训练

```
python -m paddle.distributed.launch --gpus "0,1" run_pretrain.py \
--model_name_or_path roberta-en-base \
--batch_size 16 \
--learning_rate 1e-4 \
--weight_decay 1e-2 \
--warmup_steps 10000 \
--num_train_epochs 3 \
--input_file wiki \
--output_dir ckp/ \
--logging_steps 100 \
--save_steps 10000 \
--max_steps -1 \
--device gpu \
--max_seq_length 512 \
--amp True
```

其中参数释义如下：
- `model_name_or_path` 指示了某种特定配置的模型，对应有其预训练模型和预训练时使用的 tokenizer。若模型相关内容保存在本地，这里也可以提供相应目录地址。
- `batch_size` 表示每次迭代**每张卡**上的样本数目。
- `learning_rate` 表示基础学习率大小，将于 learning rate scheduler 产生的值相乘作为当前学习率。
- `weight_decay` 表示 AdamW 优化器中使用的 weight_decay 的系数。
- `warmup_steps` 表示动态学习率热启的 step 数。
- `num_train_epochs` 表示训练轮数。
- `input_file` 表示输入数据的目录，由 create_data.py 创建。
- `output_dir` 表示模型的保存目录。
- `logging_steps` 表示日志打印间隔。
- `save_steps` 表示模型保存及评估间隔。
- `max_steps` 表示最大训练步数。若训练`num_train_epochs`轮包含的训练步数大于该值，则达到`max_steps`后就提前结束。
- `device` 表示训练使用的设备, 'gpu'表示使用 GPU, 'xpu'表示使用百度昆仑卡, 'cpu'表示使用 CPU。
- `max_seq_length` 训练数据最大长度。
- `amp` 指示是否启用自动混合精度训练。

注：
paddle.Dataloader 需2.3rc 版本才支持 HF datasets 类，现行版本可以直接在 python paddle 库中的 reader.py 中注释掉：
```
assert isinstance(dataset, Dataset)
```
https://github.com/PaddlePaddle/Paddle/blob/0ee230a7d3177f791d2a5388ab4dffdccc03f4aa/python/paddle/fluid/reader.py#L335

## fine-tune

finetune 代码请参考[benchmark_glue](../../examples/benchmark/glue)

运行如下：

```shell
export CUDA_VISIBLE_DEVICES=0
export TASK_NAME=SST-2

python -u ./run_glue.py \
    --model_type roberta \
    --model_name_or_path ROBERTA_CKP_PATH \
    --tokenizer_name_or_path roberta-en-base \
    --task_name $TASK_NAME \
    --max_seq_length 128 \
    --batch_size 32   \
    --learning_rate 3e-5 \
    --num_train_epochs 3 \
    --logging_steps 1 \
    --save_steps 100 \
    --output_dir ./tmp/$TASK_NAME/ \
    --device gpu

```


总训练 tokens：512(seq_len) * 32(batch_size) * 780000(iteration)，约 RoBERTa 训练量10%，在 GLUE validation set 表现：

| Model GLUE Score  | CoLA | SST-2 | MRPC | STS-B | QQP  | MNLI | QNLI | RTE  |
|-------------------|------|-------|------|-------|------|------|------|------|
| RoBERTa paper     | 68.0 | 96.4  | 90.9 | 92.4  | 92.2 | 90.2 | 94.7 | 86.6 |
| PaddleNLP 6-epoch | 36.9 | 89.5  | 84.3 | 86.2  | 88.6 | 80.5 | 88.4 | 58.1 |
