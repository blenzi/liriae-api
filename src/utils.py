import os
import s3fs


def open_file(filename, mode="r"):
    """
    Return a file object, open with open(data/<filename>, <mode>) or fs.open(projet-outil-ae/test/filename, <mode>)
    for s3, depending if environment variable $AWS_S3_ENDPOINT is set
    Args:
        filename (str): file to open
        mode (str): open mode
    Returns:
        File object
    """
    if "AWS_S3_ENDPOINT" in os.environ:
        # Create filesystem object
        S3_ENDPOINT_URL = "https://" + os.environ["AWS_S3_ENDPOINT"]
        fs = s3fs.S3FileSystem(client_kwargs={"endpoint_url": S3_ENDPOINT_URL})
        return fs.open(f"projet-outil-ae/test/{filename}", mode=mode)
    else:
        return open(f"data/{filename}", mode=mode)
