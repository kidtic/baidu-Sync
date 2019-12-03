import bypy
import configparser as config


#读取配置文件
cfg = config.ConfigParser()
cfg.read("src/config.ini")
localPath=cfg.get("SET","localPath")
remotePath=cfg.get("SET","remotePath")
syncTime=int(cfg.get("SET","syncTime"))
print("读取配置文件\n本地："+localPath+"\n远程："+remotePath)
print("同步时间：",syncTime)

bp=bypy.ByPy()
bp.info()
bp.list()
#bp.syncdown(remotePath,localPath,True)
#bp.syncup(localPath,remotePath,True)
bp.compare(remotePath,localPath)
