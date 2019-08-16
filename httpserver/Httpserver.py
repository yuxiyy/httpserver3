"""
httpserver 3.0

获取http请求
解析http请求
将请求发送给WebFrame
从WebFrame接收反馈数据
将数据组织为Response格式发送给客户端
"""

from socket import *
import sys,json,re
from threading import Thread
from httpserver.config import Config

# httpserver功能
class HTTPserver:
    def __init__(self):
        self.host = Config.HOST
        self.port = Config.PORT
        self.creatSocket()
        self.bind()

    # 创建套接字
    def creatSocket(self):
        self.sockfd = socket()
        self.sockfd.setsockopt(SOL_SOCKET,SO_REUSEADDR,Config.DEBUG)

    # 绑定地址
    def bind(self):
        self.address = (self.host,self.port)
        self.sockfd.bind(self.address)

    # 启动服务
    def serveForever(self):
        self.sockfd.listen(5)
        print("Start the http server:%d"%self.port)
        while True:
            connfd,addr = self.sockfd.accept()
            client = Thread(target=self.handle,args=(connfd,))
            client.setDaemon(True)
            client.start()

    # 具体处理客户端请求
    def handle(self,connfd):
        sockfd = socket()
        try:
            sockfd.connect((Config.frameIp,Config.framePort))
        except Exception as e:
            print(e)
            return
        while True:
            request = connfd.recv(4096).decode()
            if not request:
                break
            pattern = r"(?P<method>[A-Z]+)\s+(?P<info>/\S*)"
            try:
                env = re.match(pattern,request).groupdict()
                # print(env)
            except:
                connfd.close()
                return
            else:
                if not env:
                    env={"method":"GET","info":"/"}
                data = self.connect_frame(env,sockfd)
                if data:
                    self.response(connfd,data)

    def response(self,connfd,data):
        if data["status"] == "200":
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders+= "Content-Type:text/html\r\n"
            responseHeaders+= "\r\n"
            responseBody = data["data"]
        elif data["status"] == "404":
            responseHeaders = "HTTP/1.1 404 Not Found\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = data["data"]
        else:
            responseHeaders = "HTTP/1.1 200 OK\r\n"
            responseHeaders += "Content-Type:text/html\r\n"
            responseHeaders += "\r\n"
            responseBody = "UNKNOWN ERROR"

        # 将数据发送给浏览器
        data = responseHeaders+responseBody
        connfd.send(data.encode())

    # 负责和webframe交互,socket客户端
    def connect_frame(self,env,sockfd):

        # 将env转换为json发送
        json_data = json.dumps(env)
        # print(json_data)
        sockfd.send(json_data.encode())
        # 接收webframe反馈的数据
        data = sockfd.recv(1024*1024*10).decode()
        return json.loads(data)


if __name__ == '__main__':
    httpd = HTTPserver()
    httpd.serveForever()















