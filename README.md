# photo_arrange

1. 安装Python3后，使用pip install -r requirements.txt安装对应的依赖库
2. 有两种执行方式
  - 多目录执行，可以将所有目录写到一个文件中，然后使用-c参数指定对应点文件：python main.py -c path-file -o output-path
  - 单目录执行，可以直接使用-i指定：python main.py -i input-path -o output-path
  
照片会被收集到output-path目录下，按照YYYY-MM的目录组织，文件会按照YYYYMMDD_hhmmss来重新命名
