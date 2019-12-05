import bypy
import configparser as config
import os


#读取配置文件
cfg = config.ConfigParser()
cfg.read("src/config.ini")
localPath=cfg.get("SET","localPath")
remotePath=cfg.get("SET","remotePath")
syncTime=int(cfg.get("SET","syncTime"))
print("读取配置文件\n本地："+localPath+"\n远程："+remotePath)
print("同步时间：",syncTime)

bp=bypy.ByPy()
bp1=bypy.ByPy()
#bp.info()
#bp.list()
fc=bp.meta("linux/fgv/sdd")
print("fc:",fc)
fc=bp1.meta("linux/fgv/")
print("fc:",fc)

print(os.path.split(localPath))
#bp.syncdown(remotePath,localPath,True)
#bp.syncup(localPath,remotePath,True)
#bp.compare(remotePath,localPath)
