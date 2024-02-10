import os


def replace_in_file(file_path, old_text, new_text):
    # Read the contents of the file
    with open(file_path, 'r', encoding='utf-8') as file:
        file_contents = file.read()

    # Replace the old text with the new text
    new_contents = file_contents.replace(old_text, new_text)

    # Write the updated contents back to the file
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_contents)


def replace_in_directory(directory_path, old_text, new_text):
    # Iterate over all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)
        # Check if the path is a file (not a directory)
        if os.path.isfile(file_path):
            # Replace text in the file
            replace_in_file(file_path, old_text, new_text)


def main():
    # Set the working directory
    working_directory = os.getcwd()

    # Define the old and new texts to replace
    old_text = '"raw_text": ", (nsfw),"'
    new_text = '"raw_text": ", (nsfw),embedding:easynegative.safetensors,"'

    # Replace text in files in the working directory
    replace_in_directory(working_directory, old_text, new_text)


if __name__ == "__main__":
    main()
