from datasets import load_dataset

def load_summarization_data(dataset_name="cnn_dailymail", version="3.0.0", split="train[:1%]"):
    """
    Load a summarization dataset.
    Args:
        dataset_name (str): Name of the dataset to load.
        version (str): Version of the dataset.
        split (str): Split to load (e.g., 'train', 'test', 'validation').
                     Default is 'train[:1%]' for quick testing.
    Returns:
        Dataset: The loaded dataset.
    """
    print(f"Loading {dataset_name} version {version} split {split}...")
    dataset = load_dataset(dataset_name, version, split=split)
    return dataset

def preprocess_function(examples, tokenizer, max_input_length=1024, max_target_length=128):
    """
    Preprocess the data for summarization.
    Args:
        examples (dict): Batch of examples.
        tokenizer (PreTrainedTokenizer): Tokenizer to use.
        max_input_length (int): Max length for input text.
        max_target_length (int): Max length for summary.
    Returns:
        dict: Tokenized inputs and labels.
    """
    inputs = [doc for doc in examples["article"]]
    model_inputs = tokenizer(inputs, max_length=max_input_length, truncation=True)

    # Setup the tokenizer for targets
    labels = tokenizer(text_target=examples["highlights"], max_length=max_target_length, truncation=True)

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs
