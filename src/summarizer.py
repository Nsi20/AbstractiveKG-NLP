import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, Seq2SeqTrainingArguments, Seq2SeqTrainer, DataCollatorForSeq2Seq
import evaluate
import numpy as np

class Summarizer:
    def __init__(self, model_checkpoint="facebook/bart-large-cnn"):
        self.model_checkpoint = model_checkpoint
        self.tokenizer = AutoTokenizer.from_pretrained(model_checkpoint)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_checkpoint)
        self.metric = evaluate.load("rouge")

    def compute_metrics(self, eval_pred):
        predictions, labels = eval_pred
        decoded_preds = self.tokenizer.batch_decode(predictions, skip_special_tokens=True)
        labels = np.where(labels != -100, labels, self.tokenizer.pad_token_id)
        decoded_labels = self.tokenizer.batch_decode(labels, skip_special_tokens=True)

        result = self.metric.compute(predictions=decoded_preds, references=decoded_labels, use_stemmer=True)
        prediction_lens = [np.count_nonzero(pred != self.tokenizer.pad_token_id) for pred in predictions]
        result["gen_len"] = np.mean(prediction_lens)
        
        return {k: round(v, 4) for k, v in result.items()}

    def train(self, tokenized_datasets, output_dir="bart-summarization", num_epochs=1, batch_size=2):
        """
        Fine-tune the model.
        """
        data_collator = DataCollatorForSeq2Seq(self.tokenizer, model=self.model)

        args = Seq2SeqTrainingArguments(
            output_dir=output_dir,
            evaluation_strategy="epoch" if "validation" in tokenized_datasets else "no",
            learning_rate=2e-5,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            weight_decay=0.01,
            save_total_limit=2,
            num_train_epochs=num_epochs,
            predict_with_generate=True,
            fp16=torch.cuda.is_available(),
            logging_steps=10,
        )

        trainer = Seq2SeqTrainer(
            model=self.model,
            args=args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["validation"] if "validation" in tokenized_datasets else None,
            tokenizer=self.tokenizer,
            data_collator=data_collator,
            compute_metrics=self.compute_metrics if "validation" in tokenized_datasets else None,
        )

        print("Starting training...")
        trainer.train()
        print(f"Saving model to {output_dir}...")
        trainer.save_model(output_dir)

    def generate_summary(self, text, max_length=128):
        """
        Generate a summary for the given text.
        """
        inputs = self.tokenizer(text, return_tensors="pt", max_length=1024, truncation=True)
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(device)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        summary_ids = self.model.generate(inputs["input_ids"], max_length=max_length, num_beams=4, early_stopping=True)
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
