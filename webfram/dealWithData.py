from socket import *
from select import select
import json
from time import sleep

class DoDAta:
    def __init__(self,host="0.0.0.0",port=9999,dir="./static"):
        self.host = host
        self.port = port
        self.dir = dir
        self.adress = (host,port)
        # 直接创建出套接字
        self.rlist = []
        self.wlist = []
        self.xlist = []
        self.creat_socket()
        self.bind()

    # 创建套接字
    def creat_socket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    # 绑定
    def bind(self):
        self.sockfd.bind(self.adress)

    def clientDoRequest(self, connfd):
        json_data = connfd.recv(1024*1024).decode()
        if not json_data:
            return
        # print(json_data)
        request_dict = json.loads(json_data)
        # print(request_dict)
        if request_dict["method"] == "GET":
            info = request_dict["info"]
            # print("请求内容",info)
            # 根据请求内容进行数据整理
            # 分为两类: 1.请求网页 2.其他
            if info == "/" or info[-5:] == ".html":
                self.get_html(connfd, info)
            else:
                self.get_data(connfd, info)
        else:
            framDict = {"status":"404","data":"ERROR"}
            jsonData = json.dumps(framDict)
            connfd.send(jsonData.encode())

    def get_html(self, connfd, info):
        if info == "/":
            filename = self.dir+"/index.html"
        else:
            filename = self.dir+info
        try:
            fd = open(filename,"rb")
        except Exception:
            response = "<h1>Sorry....</h1>"
            framDict={"status":"404","data":response}
        else:
            response = fd.read()
            framDict={"status":"200","data":response.decode()}
        finally:
            jsonData = json.dumps(framDict)
            connfd.send(jsonData.encode())


    def get_data(self,c,info):
        f = open(self.dir+"/error.html")
        framDict={"status":"404","data":f.read()}
        jsonData = json.dumps(framDict)
        c.send(jsonData.encode())

    # 入口
    def serve_forever(self):
        self.sockfd.listen(5)
        print("Listen the port",self.port)
        self.rlist.append(self.sockfd)
        while True:
            rs, wx, xs = select(self.rlist, self.wlist, self.xlist)
            for r in rs:
                if r is self.sockfd:
                    c,addr = r.accept()
                    print("Connect from",addr)
                    self.rlist.append(c)
                else:
                    self.clientDoRequest(r)

if __name__ == '__main__':
    doData = DoDAta()
    doData.serve_forever()









