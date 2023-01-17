import argparse
import os
import shutil

import boto3

S3 = boto3.client("s3")
ABS_PATH = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")


def archive_to_s3(
    directory: str, s3_bucket: str, s3_prefix: str, filename: str
) -> None:
    try:
        os.makedirs("tmp")
    except FileExistsError:
        shutil.rmtree("tmp/")

    # copy directory to create the archive
    shutil.copytree(directory, f"tmp/{filename}")

    # archive file
    archive_file = shutil.make_archive(filename, "zip", directory)

    # send to s3
    S3.upload_file(archive_file, s3_bucket, f"{s3_prefix}/{filename}.zip")

    # clean up
    shutil.rmtree("tmp/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--function", type=str, default=None)
    parser.add_argument("--directory", type=str, default=None)
    parser.add_argument("--s3_bucket", type=str, default=None)
    parser.add_argument("--s3_prefix", type=str, default=None)
    parser.add_argument("--file_name", type=str, default=None)
    args = parser.parse_args()

    if args.function == "archive_to_s3":
        archive_to_s3(
            directory=f"{ABS_PATH}/{args.directory}",
            s3_bucket=args.s3_bucket,
            s3_prefix=args.s3_prefix,
            filename=args.file_name,
        )
