# photo_classify

依赖库：re, exifread, hachoir

1. 安装Python3后，使用pip install安装对应的依赖库
2. 将需要整理照片的路径写到一个文件中，例如：path-file，每个路径一行
3. python collect.py -c path-file or -i input-path -o output-path

照片按照YYYY-MM的目录组织，文件会按照YYYYMMDD_hhmmss来重新命名
