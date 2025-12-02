from src.pipeline import AbstractiveKGPipeline

def main():
    pipeline = AbstractiveKGPipeline()

    # Sample text (e.g., a news snippet)
    text = """
    Elon Musk, the CEO of Tesla and SpaceX, announced a new mission to Mars. 
    The mission aims to establish a permanent human settlement on the Red Planet. 
    SpaceX has been developing the Starship rocket for this purpose. 
    NASA is also collaborating with SpaceX on various lunar missions.
    """

    print(f"Input Text:\n{text.strip()}\n")

    try:
        summary, kg_data = pipeline.process(text)
        
        print("\n--- Final Output ---")
        print("Entities:", [e['text'] for e in kg_data['entities']])
        print("Relations:", [f"{r['head']} -> {r['type']} -> {r['tail']}" for r in kg_data['relations']])
        
    finally:
        pipeline.close()

if __name__ == "__main__":
    main()
