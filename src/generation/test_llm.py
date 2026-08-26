from src.generation.llm_client import LLMClient


def main():
    client = LLMClient()

    response = client.generate(
        "Erkläre in einem Satz, was ein Masterstudiengang ist."
    )

    print("\n" + "=" * 80)
    print("LLM TEST")
    print("=" * 80)
    print(response)
    print("=" * 80)


if __name__ == "__main__":
    main()