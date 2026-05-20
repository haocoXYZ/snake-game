import tarfile
with tarfile.open("C:/Users/ADMIN/OneDrive/Desktop/Snake/build/web/snake.tar.gz", "r:gz") as tar:
    for member in tar.getmembers():
        print(member.name)
