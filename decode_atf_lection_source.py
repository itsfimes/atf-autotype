from modules.corrector import autocorrect
corrected_chars = {
    "~": " ",
    "ù": "ů",
    "ø": "ř",
    "ì": "ě",
    "": "š",
    "è": "č",
    "": "ž",
    "ò": "ň"
}

def extract_pipe_separated_strings(file_path, output_file=None):
    """
    Extracts all pipe-separated strings from a file, preserving special characters.

    Args:
        file_path: Path to the input file
        output_file: Optional path to save extracted strings (one per line)

    Returns:
        List of extracted strings
    """
    try:
        # Read file in binary mode first to preserve all bytes
        with open(file_path, 'rb') as f:
            raw_data = f.read()

        # Try to decode with latin-1 which maps all bytes 0-255 directly
        # This preserves characters like č (0xE8) and í (0xED)
        content = raw_data.decode('latin-1')
        print(f"Successfully read file (preserving all byte values)")

        # Split by pipe character
        strings = content.split('|')

        # Clean up the strings but preserve special characters
        # Only strip actual whitespace, not special chars
        cleaned_strings = []
        for s in strings:
            # Strip only common whitespace
            cleaned = s.strip(' \t\n\r\x00')
            for wrong, right in corrected_chars.items():
                cleaned = cleaned.replace(wrong, right)

            if cleaned and not any(x in cleaned for x in ["#", "&", "$"]):
                cleaned_strings.append(cleaned)

        print(f"\nFound {len(cleaned_strings)} pipe-separated strings")

        # Print first 20 strings as preview
        print("\nPreview (first 20 strings):")
        for i, s in enumerate(cleaned_strings[:20], 1):
            # Show both the string and its hex representation for debugging
            hex_repr = ' '.join(f'{ord(c):02x}' for c in s[:20])
            print(f"{i}. {s} (hex: {hex_repr}...)")

        # Save to output file if specified, using latin-1 to preserve all chars
        if output_file:
            with open(output_file, 'w', encoding='latin-1', errors="replace") as f:
                f.write('\n'.join(cleaned_strings))
            print(f"\nAll strings saved to: {output_file}")

            # Also create a UTF-8 version with best-effort conversion
            utf8_output = output_file.replace('.txt', '_utf8.txt')
            with open(utf8_output, 'w', encoding='utf-8', errors='replace') as f:
                f.write('\n'.join(cleaned_strings))
            print(f"UTF-8 version saved to: {utf8_output}")

        return cleaned_strings

    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        return []


if __name__ == "__main__":
    # Usage example
    input_file = "text.txd"  # Change this to your file path
    output_file = "ac_source.txt"  # Optional: where to save results

    strings = extract_pipe_separated_strings(input_file, output_file)

    print(f"\nTotal strings extracted: {len(strings)}")

    # Show some stats about special characters found
    special_chars = set()
    for s in strings:
        for c in s:
            if ord(c) > 127:
                special_chars.add(c)

    if special_chars:
        print(f"\nSpecial characters found: {' '.join(sorted(special_chars))}")
        print(f"Hex values: {' '.join(f'{ord(c):02x}' for c in sorted(special_chars))}")