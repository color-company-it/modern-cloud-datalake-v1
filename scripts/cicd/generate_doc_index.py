import glob

HEADER = """
![logo](src/logo.png)

# Welcome to the Modern Cloud Datalake V1!

This particular repository represents a proof of concept (POC) for a polylithic enterprise data lake in AWS, which is a
cloud-based platform that offers a range of tools and services for data storage and analysis. The POC is designed to
demonstrate how a data lake can serve as a platform for startups and enterprises, providing a single source of truth for
data and enabling users to easily access and analyze data from various sources.

The benefits of a modern data lake design include improved data accessibility and flexibility, the ability to easily
integrate data from various sources, and the ability to store and analyze large amounts of data at scale. This can help
organizations gain a better understanding of their data and make more informed decisions, leading to improved efficiency
and effectiveness. Overall, modern data lake designs are an important tool for organizations looking to extract value
from their data and drive business growth.

![Architecture](./src/arhitecture.png)

"""

FOOTER = """

---
<small> 
Please note that the above code and associated documentation are provided as a reference and are not guaranteed to be
error-free. This solution is a work in progress and may be subject to change. It is the responsibility of the user to
thoroughly test and verify the correctness of the code before using it in production environments. 
</small>
"""


def generate_index(directory: str) -> None:
    """
    Yes.. I am this lazy...
    """
    # Create an empty list to store the file names
    file_names = []

    # Iterate through the files in the directory
    for file in glob.glob(directory, recursive=True):
        # Check if the file is a markdown file
        if file.endswith(".md") and not file.endswith("index.md"):
            # Add the file name to the list
            file = file.replace("../../docs\\", "").replace("\\", "/")
            file_names.append(file)

    # Sort the list of file names
    file_names.sort()
    indexed_files = {}

    for file in file_names:
        file_parts = file.split("/")
        folder = "Index" if len(file_parts) < 2 else file_parts[0]

        if folder not in indexed_files:
            indexed_files[folder] = []
        indexed_files[folder].append(file_parts[-1])

    # Open the index file for writing
    with open("./documentation/index.md", "w") as index_file:
        # Write the index title
        index_file.write(HEADER)
        index_file.write("# Index\n\n")

        # Iterate through the file names
        count = 1
        for subheader, filenames in indexed_files.items():
            index_file.write(f"{count}. {subheader}\n")
            for filename in filenames:
                # Write the file name as a markdown link to the file
                index_file.write(
                    f"\t- [{filename.replace('.md', '')}]({subheader}/{filename})\n"
                )
            count += 1


if __name__ == "__main__":
    generate_index("./documentation/**/*")
